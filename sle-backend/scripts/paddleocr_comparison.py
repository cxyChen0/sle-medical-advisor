"""
PaddleOCR vs CnOCR 对比测试
对比两个OCR库的准确度和性能
"""

import sys
import time
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from cnocr import CnOcr
from paddleocr import PaddleOCR
import os


def test_paddleocr(image_path: str):
    """测试PaddleOCR"""
    
    print(f"\n{'='*70}")
    print(f"PaddleOCR测试: {Path(image_path).name}")
    print(f"{'='*70}\n")
    
    try:
        ocr = PaddleOCR(use_textline_orientation=True, lang='ch')
        
        start_time = time.time()
        result = ocr.ocr(image_path, cls=True)
        ocr_time = time.time() - start_time
        
        if result and result[0]:
            text_lines = [line[1][0] for line in result[0]]
            text = '\n'.join(text_lines)
            
            print(f"✓ OCR成功")
            print(f"  耗时: {ocr_time:.3f}秒")
            print(f"  识别文本长度: {len(text)} 字符")
            print(f"  识别结果数量: {len(result[0])}")
            print(f"\n识别文本:")
            print(text)
            
            return {
                'success': True,
                'time': ocr_time,
                'text_length': len(text),
                'result_count': len(result[0]),
                'text': text,
                'details': result[0]
            }
        else:
            print(f"✗ OCR失败: 未识别到文本")
            return {
                'success': False,
                'time': ocr_time,
                'error': '未识别到文本'
            }
            
    except Exception as e:
        print(f"✗ OCR失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def test_cnocr(image_path: str):
    """测试CnOCR"""
    
    print(f"\n{'='*70}")
    print(f"CnOCR测试: {Path(image_path).name}")
    print(f"{'='*70}\n")
    
    try:
        model_dir = os.path.join(os.getcwd(), 'cnocr_models')
        os.makedirs(model_dir, exist_ok=True)
        os.environ['CNOCR_HOME'] = model_dir
        
        ocr = CnOcr(model_name='densenet_lite_136', model_dir=model_dir, rec_model_fp16=True)
        
        start_time = time.time()
        result = ocr.ocr(image_path)
        ocr_time = time.time() - start_time
        
        if result and isinstance(result, list):
            text = '\n'.join([item['text'] for item in result if 'text' in item])
            
            print(f"✓ OCR成功")
            print(f"  耗时: {ocr_time:.3f}秒")
            print(f"  识别文本长度: {len(text)} 字符")
            print(f"  识别结果数量: {len(result)}")
            print(f"\n识别文本:")
            print(text)
            
            return {
                'success': True,
                'time': ocr_time,
                'text_length': len(text),
                'result_count': len(result),
                'text': text,
                'details': result
            }
        else:
            print(f"✗ OCR失败: 结果格式错误")
            return {
                'success': False,
                'time': ocr_time,
                'error': '结果格式错误'
            }
            
    except Exception as e:
        print(f"✗ OCR失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def compare_ocr_engines(image_path: str):
    """对比两个OCR引擎"""
    
    print(f"\n{'='*70}")
    print(f"OCR引擎对比测试: {Path(image_path).name}")
    print(f"{'='*70}\n")
    
    # 测试PaddleOCR
    paddle_result = test_paddleocr(image_path)
    
    # 测试CnOCR
    cnocr_result = test_cnocr(image_path)
    
    # 对比结果
    print(f"\n{'='*70}")
    print("对比总结")
    print(f"{'='*70}\n")
    
    if paddle_result.get('success') and cnocr_result.get('success'):
        print(f"{'引擎':<15} {'耗时(秒)':<12} {'文本长度':<12} {'识别数量':<12}")
        print("-" * 70)
        print(f"{'PaddleOCR':<15} {paddle_result['time']:<12.3f} {paddle_result['text_length']:<12} {paddle_result['result_count']:<12}")
        print(f"{'CnOCR':<15} {cnocr_result['time']:<12.3f} {cnocr_result['text_length']:<12} {cnocr_result['result_count']:<12}")
        
        # 文本对比
        print(f"\n文本对比:")
        print("-" * 70)
        print(f"PaddleOCR识别的文本:")
        print(paddle_result['text'])
        print(f"\nCnOCR识别的文本:")
        print(cnocr_result['text'])
        
        # 准确度分析
        print(f"\n准确度分析:")
        print("-" * 70)
        
        # 检查关键指标
        key_indicators = ['白细胞', '红细胞', '血红蛋白', '血小板', '抗体', 'C3', 'C4', 'IgG', 'IgA', 'IgM']
        
        paddle_found = sum(1 for indicator in key_indicators if indicator in paddle_result['text'])
        cnocr_found = sum(1 for indicator in key_indicators if indicator in cnocr_result['text'])
        
        print(f"PaddleOCR找到的关键指标: {paddle_found}/{len(key_indicators)}")
        print(f"CnOCR找到的关键指标: {cnocr_found}/{len(key_indicators)}")
        
        # 检查数值识别
        print(f"\n数值识别对比:")
        print("-" * 70)
        
        import re
        paddle_numbers = re.findall(r'\d+\.?\d*', paddle_result['text'])
        cnocr_numbers = re.findall(r'\d+\.?\d*', cnocr_result['text'])
        
        print(f"PaddleOCR识别的数值: {len(paddle_numbers)}个 - {paddle_numbers[:10]}")
        print(f"CnOCR识别的数值: {len(cnocr_numbers)}个 - {cnocr_numbers[:10]}")
        
        # 保存结果
        output_dir = Path(__file__).parent.parent / "test_results"
        output_dir.mkdir(exist_ok=True)
        
        comparison_result = {
            'file': Path(image_path).name,
            'paddleocr': paddle_result,
            'cnocr': cnocr_result,
            'comparison': {
                'paddle_key_indicators': paddle_found,
                'cnocr_key_indicators': cnocr_found,
                'paddle_numbers': len(paddle_numbers),
                'cnocr_numbers': len(cnocr_numbers)
            }
        }
        
        output_file = output_dir / f"{Path(image_path).stem}_ocr_comparison.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 对比结果已保存: {output_file}")
        
        return comparison_result
    else:
        print("无法对比，至少有一个OCR引擎失败")
        return None


def main():
    if len(sys.argv) < 2:
        print("使用方法: python paddleocr_comparison.py <文件路径>")
        print("\n示例:")
        print("  python paddleocr_comparison.py test_images/medical_report.png")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    
    compare_ocr_engines(file_path)


if __name__ == "__main__":
    main()
