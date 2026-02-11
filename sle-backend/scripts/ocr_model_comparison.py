"""
OCR模型对比测试脚本
测试不同的OCR模型和参数组合，找到最佳配置
"""

import sys
import time
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from cnocr import CnOcr
from PIL import Image, ImageEnhance
import os


def test_ocr_models(image_path: str):
    """测试不同的OCR模型"""
    
    print(f"\n{'='*70}")
    print(f"OCR模型对比测试: {Path(image_path).name}")
    print(f"{'='*70}\n")
    
    model_dir = os.path.join(os.getcwd(), 'cnocr_models')
    os.makedirs(model_dir, exist_ok=True)
    os.environ['CNOCR_HOME'] = model_dir
    
    models_to_test = [
        {
            'name': 'densenet_lite_136',
            'description': '轻量级模型，速度快',
            'config': {
                'model_name': 'densenet_lite_136',
                'model_dir': model_dir,
                'rec_model_fp16': True,
            }
        },
        {
            'name': 'densenet_lite_136_gru',
            'description': '带GRU的轻量级模型',
            'config': {
                'model_name': 'densenet_lite_136-gru',
                'model_dir': model_dir,
                'rec_model_fp16': True,
            }
        },
    ]
    
    results = []
    
    for model_info in models_to_test:
        print(f"\n测试模型: {model_info['name']}")
        print(f"描述: {model_info['description']}")
        print("-" * 70)
        
        try:
            ocr = CnOcr(**model_info['config'])
            
            start_time = time.time()
            result = ocr.ocr(image_path)
            ocr_time = time.time() - start_time
            
            if result and isinstance(result, list):
                text = '\n'.join([item['text'] for item in result if 'text' in item])
                
                print(f"✓ OCR成功")
                print(f"  耗时: {ocr_time:.3f}秒")
                print(f"  识别文本长度: {len(text)} 字符")
                print(f"  识别结果数量: {len(result)}")
                print(f"\n识别文本预览:")
                print(text[:500])
                
                results.append({
                    'model': model_info['name'],
                    'description': model_info['description'],
                    'time': ocr_time,
                    'text_length': len(text),
                    'result_count': len(result),
                    'text': text,
                    'success': True
                })
            else:
                print(f"✗ OCR失败: 结果格式错误")
                results.append({
                    'model': model_info['name'],
                    'description': model_info['description'],
                    'time': ocr_time,
                    'success': False
                })
                
        except Exception as e:
            print(f"✗ OCR失败: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'model': model_info['name'],
                'description': model_info['description'],
                'success': False,
                'error': str(e)
            })
    
    # 对比结果
    print(f"\n{'='*70}")
    print("模型对比总结")
    print(f"{'='*70}\n")
    
    successful_results = [r for r in results if r.get('success')]
    
    if successful_results:
        print(f"{'模型':<30} {'耗时(秒)':<12} {'文本长度':<12} {'识别数量':<12}")
        print("-" * 70)
        
        for result in successful_results:
            print(f"{result['model']:<30} {result['time']:<12.3f} {result['text_length']:<12} {result['result_count']:<12}")
        
        # 找出最佳模型
        fastest = min(successful_results, key=lambda x: x['time'])
        longest_text = max(successful_results, key=lambda x: x['text_length'])
        
        print(f"\n最快模型: {fastest['model']} ({fastest['time']:.3f}秒)")
        print(f"识别文本最多: {longest_text['model']} ({longest_text['text_length']} 字符)")
    
    # 保存结果
    output_dir = Path(__file__).parent.parent / "test_results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{Path(image_path).stem}_ocr_comparison.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 结果已保存: {output_file}")
    
    return results


def test_image_preprocessing(image_path: str):
    """测试不同的图片预处理方法"""
    
    print(f"\n{'='*70}")
    print(f"图片预处理测试: {Path(image_path).name}")
    print(f"{'='*70}\n")
    
    img = Image.open(image_path)
    print(f"原始图片: {img.size[0]}x{img.size[1]}, 模式: {img.mode}")
    
    # 测试1: 原始图片
    print("\n1. 原始图片")
    print("-" * 70)
    model_dir = os.path.join(os.getcwd(), 'cnocr_models')
    os.environ['CNOCR_HOME'] = model_dir
    ocr = CnOcr(model_name='densenet_lite_136', model_dir=model_dir, rec_model_fp16=True)
    
    start_time = time.time()
    result = ocr.ocr(image_path)
    ocr_time = time.time() - start_time
    
    if result and isinstance(result, list):
        text = '\n'.join([item['text'] for item in result if 'text' in item])
        print(f"耗时: {ocr_time:.3f}秒")
        print(f"文本长度: {len(text)} 字符")
        print(f"识别结果数量: {len(result)}")
    
    # 测试2: 灰度图
    print("\n2. 灰度图")
    print("-" * 70)
    gray_img = img.convert('L')
    gray_path = str(Path(image_path).with_suffix('.gray.jpg'))
    gray_img.save(gray_path, 'JPEG', quality=95)
    
    start_time = time.time()
    result = ocr.ocr(gray_path)
    ocr_time = time.time() - start_time
    
    if result and isinstance(result, list):
        text = '\n'.join([item['text'] for item in result if 'text' in item])
        print(f"耗时: {ocr_time:.3f}秒")
        print(f"文本长度: {len(text)} 字符")
        print(f"识别结果数量: {len(result)}")
    
    Path(gray_path).unlink()
    
    # 测试3: 增强对比度
    print("\n3. 增强对比度")
    print("-" * 70)
    contrast_img = ImageEnhance.Contrast(img).enhance(1.5)
    contrast_path = str(Path(image_path).with_suffix('.contrast.jpg'))
    contrast_img.save(contrast_path, 'JPEG', quality=95)
    
    start_time = time.time()
    result = ocr.ocr(contrast_path)
    ocr_time = time.time() - start_time
    
    if result and isinstance(result, list):
        text = '\n'.join([item['text'] for item in result if 'text' in item])
        print(f"耗时: {ocr_time:.3f}秒")
        print(f"文本长度: {len(text)} 字符")
        print(f"识别结果数量: {len(result)}")
    
    Path(contrast_path).unlink()
    
    # 测试4: 增强清晰度
    print("\n4. 增强清晰度")
    print("-" * 70)
    sharp_img = ImageEnhance.Sharpness(img).enhance(1.3)
    sharp_path = str(Path(image_path).with_suffix('.sharp.jpg'))
    sharp_img.save(sharp_path, 'JPEG', quality=95)
    
    start_time = time.time()
    result = ocr.ocr(sharp_path)
    ocr_time = time.time() - start_time
    
    if result and isinstance(result, list):
        text = '\n'.join([item['text'] for item in result if 'text' in item])
        print(f"耗时: {ocr_time:.3f}秒")
        print(f"文本长度: {len(text)} 字符")
        print(f"识别结果数量: {len(result)}")
    
    Path(sharp_path).unlink()
    
    # 测试5: 组合优化
    print("\n5. 组合优化 (灰度+对比度+清晰度)")
    print("-" * 70)
    optimized_img = img.convert('L')
    optimized_img = ImageEnhance.Contrast(optimized_img).enhance(1.5)
    optimized_img = ImageEnhance.Sharpness(optimized_img).enhance(1.3)
    optimized_path = str(Path(image_path).with_suffix('.optimized.jpg'))
    optimized_img.save(optimized_path, 'JPEG', quality=95)
    
    start_time = time.time()
    result = ocr.ocr(optimized_path)
    ocr_time = time.time() - start_time
    
    if result and isinstance(result, list):
        text = '\n'.join([item['text'] for item in result if 'text' in item])
        print(f"耗时: {ocr_time:.3f}秒")
        print(f"文本长度: {len(text)} 字符")
        print(f"识别结果数量: {len(result)}")
        print(f"\n识别文本:")
        print(text)
    
    Path(optimized_path).unlink()


def main():
    if len(sys.argv) < 2:
        print("使用方法: python ocr_model_comparison.py <文件路径>")
        print("\n示例:")
        print("  python ocr_model_comparison.py test_images/medical_report.png")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    
    # 测试不同模型
    test_ocr_models(file_path)
    
    # 测试图片预处理
    test_image_preprocessing(file_path)


if __name__ == "__main__":
    main()
