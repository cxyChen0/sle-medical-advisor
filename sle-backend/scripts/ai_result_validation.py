"""
AI结果准确性验证脚本
检查AI返回结果的准确度和完整性
"""

import sys
import json
from pathlib import Path
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ai_semantic_service import parse_report_with_ai
from app.services.report_parser import extract_text_from_file


async def validate_ai_result(file_path: str, report_type: str = "lab"):
    """验证AI返回结果的准确度和完整性"""
    
    print(f"\n{'='*70}")
    print(f"AI结果准确性验证: {Path(file_path).name}")
    print(f"{'='*70}\n")
    
    # 1. OCR提取文本
    print("步骤1: OCR提取原始文本")
    print("-" * 70)
    text = extract_text_from_file(file_path)
    print(f"原始文本:\n{text}\n")
    
    # 2. AI解析
    print("步骤2: AI解析")
    print("-" * 70)
    result = await parse_report_with_ai(text, report_type)
    
    print(f"AI返回的JSON结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()
    
    # 3. 验证结果完整性
    print("步骤3: 验证结果完整性")
    print("-" * 70)
    
    # 3.1 检查indicators字段
    indicators = result.get('indicators', [])
    print(f"✓ 指标数量: {len(indicators)}")
    
    if indicators:
        print(f"\n指标详情:")
        for idx, indicator in enumerate(indicators):
            print(f"\n  指标 {idx+1}:")
            print(f"    - name: {indicator.get('name', '缺失')}")
            print(f"    - value: {indicator.get('value', '缺失')}")
            print(f"    - unit: {indicator.get('unit', '缺失')}")
            print(f"    - reference_range: {indicator.get('reference_range', '缺失')}")
            print(f"    - is_abnormal: {indicator.get('is_abnormal', '缺失')}")
            print(f"    - normalized_name: {indicator.get('normalized_name', '缺失')}")
            print(f"    - normalization_confidence: {indicator.get('normalization_confidence', '缺失')}")
    
    # 3.2 检查patient_info字段
    patient_info = result.get('patient_info', {})
    print(f"\n✓ 患者信息:")
    print(f"    - patient_id: {patient_info.get('patient_id', '缺失')}")
    print(f"    - name: {patient_info.get('name', '缺失')}")
    print(f"    - gender: {patient_info.get('gender', '缺失')}")
    print(f"    - age: {patient_info.get('age', '缺失')}")
    
    # 3.3 检查report_info字段
    report_info = result.get('report_info', {})
    print(f"\n✓ 报告信息:")
    print(f"    - report_date: {report_info.get('report_date', '缺失')}")
    print(f"    - report_number: {report_info.get('report_number', '缺失')}")
    
    # 4. 验证准确性
    print(f"\n步骤4: 验证准确性")
    print("-" * 70)
    
    # 4.1 对比原始文本和AI提取的指标
    print("\n原始文本中的指标:")
    lines = text.split('\n')
    for line in lines:
        if ':' in line and any(keyword in line for keyword in ['计数', '蛋白', '抗体', 'C3', 'C4', 'IgG', 'IgA', 'IgM']):
            print(f"  - {line}")
    
    print("\nAI提取的指标:")
    for indicator in indicators:
        print(f"  - {indicator.get('name', '')}: {indicator.get('value', '')} {indicator.get('unit', '')}")
    
    # 5. 检查JSON格式
    print(f"\n步骤5: 检查JSON格式")
    print("-" * 70)
    
    try:
        json_str = json.dumps(result, ensure_ascii=False)
        json_obj = json.loads(json_str)
        print("✓ JSON格式正确")
        print(f"✓ JSON大小: {len(json_str)} 字符")
    except Exception as e:
        print(f"✗ JSON格式错误: {e}")
    
    # 6. 保存JSON文件
    print(f"\n步骤6: 保存JSON文件")
    print("-" * 70)
    
    output_dir = Path(__file__).parent.parent / "test_results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{Path(file_path).stem}_ai_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ JSON文件已保存: {output_file}")
    
    # 7. 总结
    print(f"\n步骤7: 总结")
    print("-" * 70)
    
    missing_fields = []
    for idx, indicator in enumerate(indicators):
        if not indicator.get('name'):
            missing_fields.append(f"指标{idx+1}缺少name")
        if not indicator.get('value'):
            missing_fields.append(f"指标{idx+1}缺少value")
        if not indicator.get('normalized_name'):
            missing_fields.append(f"指标{idx+1}缺少normalized_name")
    
    if missing_fields:
        print(f"✗ 发现缺失字段:")
        for field in missing_fields:
            print(f"  - {field}")
    else:
        print("✓ 所有指标字段完整")
    
    if len(indicators) > 0:
        print(f"✓ AI成功提取了 {len(indicators)} 个指标")
    else:
        print("✗ AI未提取到任何指标")
    
    return result


def main():
    if len(sys.argv) < 2:
        print("使用方法: python ai_result_validation.py <文件路径> [报告类型]")
        print("\n报告类型 (可选):")
        print("  - lab: 化验报告 (默认)")
        print("  - pathology: 病理报告")
        print("\n示例:")
        print("  python ai_result_validation.py test_images/medical_report.png")
        print("  python ai_result_validation.py test_images/medical_report.png lab")
        sys.exit(1)
    
    file_path = sys.argv[1]
    report_type = sys.argv[2] if len(sys.argv) > 2 else 'lab'
    
    if not Path(file_path).exists():
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    
    asyncio.run(validate_ai_result(file_path, report_type))


if __name__ == "__main__":
    main()
