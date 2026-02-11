"""
解析SLE相关检查单
支持病理报告和化验报告的解析
支持多张检查单的拼接处理
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import os
from datetime import datetime

# 检查单解析规则
PARSING_RULES = {
    'lab': {
        # 常见SLE化验指标的正则表达式
        'antibodies': {
            'ANA': r'抗核抗体.*?[:：]\s*([+-]|\d+:\d+|阳性|阴性)',
            'dsDNA': r'抗双链DNA抗体.*?[:：]\s*([+-]|\d+\.?\d*|阳性|阴性)',
            'Sm抗体': r'Sm抗体.*?[:：]\s*([+-]|\d+\.?\d*|阳性|阴性)',
            'RNP抗体': r'RNP抗体.*?[:：]\s*([+-]|\d+\.?\d*|阳性|阴性)',
            'SSA抗体': r'SSA抗体.*?[:：]\s*([+-]|\d+\.?\d*|阳性|阴性)',
            'SSB抗体': r'SSB抗体.*?[:：]\s*([+-]|\d+\.?\d*|阳性|阴性)',
        },
        'blood_counts': {
            '白细胞计数': r'白细胞.*?[:：]\s*([\d\.]+)',
            '红细胞计数': r'红细胞.*?[:：]\s*([\d\.]+)',
            '血红蛋白': r'血红蛋白.*?[:：]\s*([\d\.]+)',
            '血小板计数': r'血小板.*?[:：]\s*([\d\.]+)',
        },
        'urine': {
            '蛋白': r'尿蛋白.*?[:：]\s*([\+\-]|\d+\.?\d*|阳性|阴性)',
            '红细胞': r'尿红细胞.*?[:：]\s*([\+\-]|\d+\.?\d*|阳性|阴性)',
            '白细胞': r'尿白细胞.*?[:：]\s*([\+\-]|\d+\.?\d*|阳性|阴性)',
        },
        'immune': {
            'C3': r'C3.*?[:：]\s*([\d\.]+)',
            'C4': r'C4.*?[:：]\s*([\d\.]+)',
            'IgG': r'IgG.*?[:：]\s*([\d\.]+)',
            'IgA': r'IgA.*?[:：]\s*([\d\.]+)',
            'IgM': r'IgM.*?[:：]\s*([\d\.]+)',
        }
    },
    'pathology': {
        'biopsy': r'活组织检查.*?[:：]\s*(.+?)(?=\n|$)',
        'findings': r'病理发现.*?[:：]\s*(.+?)(?=\n|$)',
        'diagnosis': r'病理诊断.*?[:：]\s*(.+?)(?=\n|$)',
        'notes': r'备注.*?[:：]\s*(.+?)(?=\n|$)'
    }
}

# 参考范围字典
REFERENCE_RANGES = {
    '白细胞计数': {'min': 4.0, 'max': 10.0, 'unit': '10^9/L'},
    '红细胞计数': {'min': 3.5, 'max': 5.5, 'unit': '10^12/L'},
    '血红蛋白': {'min': 110, 'max': 160, 'unit': 'g/L'},
    '血小板计数': {'min': 100, 'max': 300, 'unit': '10^9/L'},
    'C3': {'min': 0.8, 'max': 1.6, 'unit': 'g/L'},
    'C4': {'min': 0.1, 'max': 0.4, 'unit': 'g/L'},
    'IgG': {'min': 7.0, 'max': 16.0, 'unit': 'g/L'},
    'IgA': {'min': 0.7, 'max': 4.0, 'unit': 'g/L'},
    'IgM': {'min': 0.4, 'max': 2.3, 'unit': 'g/L'},
}


def extract_text_from_file(file_path: str) -> str:
    """
    从文件中提取文本内容

    Args:
        file_path: 文件路径

    Returns:
        文件文本内容
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 根据文件扩展名选择不同的处理方式
    if file_path.suffix.lower() in ['.txt', '.md']:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_path.suffix.lower() == '.pdf':
        # 需要安装 PyPDF2
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            print("警告: 需要安装 PyPDF2 库来解析PDF文件")
            print("运行: pip install PyPDF2")
            return ""
    elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
        # 需要安装 pytesseract
        try:
            import pytesseract
            from PIL import Image
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            return text
        except ImportError:
            print("警告: 需要安装 pytesseract 和 Pillow 库来解析图片文件")
            print("运行: pip install pytesseract Pillow")
            print("还需要安装 Tesseract OCR 引擎")
            return ""
    else:
        print(f"警告: 不支持的文件类型: {file_path.suffix}")
        return ""


def parse_indicators(text: str, report_type: str) -> List[Dict]:
    """
    从文本中解析检查指标

    Args:
        text: 检查单文本内容
        report_type: 报告类型 (lab/pathology)

    Returns:
        指标列表
    """
    indicators = []

    if report_type == 'lab':
        rules = PARSING_RULES['lab']

        # 解析各类指标
        for category in rules.values():
            for name, pattern in category.items():
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    unit = REFERENCE_RANGES.get(name, {}).get('unit', '')
                    ref_range = REFERENCE_RANGES.get(name, {})

                    # 判断是否异常
                    is_abnormal = False
                    if name in REFERENCE_RANGES and value.replace('.', '').isdigit():
                        num_value = float(value)
                        if num_value < ref_range['min'] or num_value > ref_range['max']:
                            is_abnormal = True
                    elif value in ['阳性', '+', '++', '+++']:
                        is_abnormal = True

                    indicators.append({
                        'name': name,
                        'value': value,
                        'unit': unit,
                        'reference_range': f"{ref_range.get('min', '')}-{ref_range.get('max', '')} {unit}" if ref_range else '',
                        'is_abnormal': is_abnormal,
                        'notes': ''
                    })

    elif report_type == 'pathology':
        rules = PARSING_RULES['pathology']
        for name, pattern in rules.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                indicators.append({
                    'name': name,
                    'value': match.group(1).strip(),
                    'unit': '',
                    'reference_range': '',
                    'is_abnormal': False,
                    'notes': ''
                })

    return indicators


def parse_report(file_path: str, report_type: str) -> Dict:
    """
    解析单个检查单

    Args:
        file_path: 检查单文件路径
        report_type: 报告类型 (lab/pathology)

    Returns:
        解析结果字典
    """
    # 提取文本
    text = extract_text_from_file(file_path)

    # 解析指标
    indicators = parse_indicators(text, report_type)

    # 尝试提取检查日期
    date_match = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)', text)
    report_date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')

    # 尝试提取医院名称
    hospital_match = re.search(r'(医院|医疗中心|诊所).*?(?=\s|$)', text)
    hospital_name = hospital_match.group(0).strip() if hospital_match else ''

    return {
        'file_path': file_path,
        'report_type': report_type,
        'report_date': report_date,
        'hospital_name': hospital_name,
        'indicators': indicators
    }


def parse_multiple_reports(file_paths: List[str], report_type: str) -> Dict:
    """
    解析多个检查单并拼接结果

    Args:
        file_paths: 检查单文件路径列表
        report_type: 报告类型 (lab/pathology)

    Returns:
        合并后的解析结果
    """
    all_reports = []
    all_indicators = {}
    latest_date = None
    hospital_names = set()

    for file_path in file_paths:
        try:
            report = parse_report(file_path, report_type)
            all_reports.append(report)

            # 收集所有指标
            for indicator in report['indicators']:
                name = indicator['name']
                if name not in all_indicators:
                    all_indicators[name] = []
                all_indicators[name].append(indicator)

            # 更新最新日期
            if report['report_date']:
                if latest_date is None or report['report_date'] > latest_date:
                    latest_date = report['report_date']

            # 收集医院名称
            if report['hospital_name']:
                hospital_names.add(report['hospital_name'])

        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {e}")

    # 合并重复指标(如果有多个检查单,保留最新的或标记趋势)
    merged_indicators = []
    for name, values in all_indicators.items():
        if len(values) == 1:
            merged_indicators.append(values[0])
        else:
            # 多个检查单有同一指标,显示趋势
            latest_value = values[0]  # 假设按顺序处理,最后一个是最新的
            merged_indicators.append({
                'name': name,
                'value': latest_value['value'],
                'unit': latest_value['unit'],
                'reference_range': latest_value['reference_range'],
                'is_abnormal': latest_value['is_abnormal'],
                'notes': f"多次检查,共{len(values)}次",
                'trend': values  # 保存所有值用于趋势分析
            })

    return {
        'report_type': report_type,
        'report_count': len(all_reports),
        'report_date': latest_date,
        'hospital_name': ', '.join(list(hospital_names)),
        'indicators': merged_indicators,
        'reports': all_reports
    }


def save_parsed_result(result: Dict, output_path: Optional[str] = None):
    """
    保存解析结果到JSON文件

    Args:
        result: 解析结果
        output_path: 输出文件路径,如果不指定则自动生成
    """
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"parsed_report_{timestamp}.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"解析结果已保存到: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description='解析SLE相关检查单')
    parser.add_argument('--file', type=str, help='检查单文件路径')
    parser.add_argument('--files', type=str, nargs='+', help='多个检查单文件路径')
    parser.add_argument('--type', type=str, choices=['lab', 'pathology'],
                       required=True, help='报告类型: lab(化验) 或 pathology(病理)')
    parser.add_argument('--output', type=str, help='输出JSON文件路径')

    args = parser.parse_args()

    if args.files:
        # 处理多个文件
        result = parse_multiple_reports(args.files, args.type)
        print(f"成功解析 {len(args.files)} 个检查单")
    elif args.file:
        # 处理单个文件
        result = parse_report(args.file, args.type)
        print(f"成功解析检查单: {args.file}")
    else:
        print("错误: 必须指定 --file 或 --files 参数")
        return

    # 打印摘要
    print(f"\n解析摘要:")
    print(f"- 报告类型: {result['report_type']}")
    print(f"- 检查日期: {result.get('report_date', '未知')}")
    print(f"- 指标数量: {len(result['indicators'])}")
    print(f"- 异常指标: {sum(1 for i in result['indicators'] if i['is_abnormal'])}")

    # 打印异常指标
    abnormal = [i for i in result['indicators'] if i['is_abnormal']]
    if abnormal:
        print(f"\n异常指标:")
        for ind in abnormal:
            print(f"  - {ind['name']}: {ind['value']} {ind['unit']}")

    # 保存结果
    save_parsed_result(result, args.output)


if __name__ == '__main__':
    main()
