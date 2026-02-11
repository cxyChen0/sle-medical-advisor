"""
OCR性能测试脚本
对比图片优化前后的OCR性能差异
"""

import os
import sys
from pathlib import Path
import time
from typing import Dict, List, Tuple
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.report_parser import get_ocr_instance
from scripts.image_optimizer import ImageOptimizer


class OCRPerformanceTester:
    """OCR性能测试器"""

    def __init__(self):
        self.ocr = get_ocr_instance()
        self.optimizer = ImageOptimizer()

    def get_file_info(self, file_path: str) -> dict:
        """获取文件信息"""
        path = Path(file_path)
        file_size = os.path.getsize(file_path)
        
        return {
            'path': file_path,
            'name': path.name,
            'size': file_size,
            'size_mb': file_size / (1024 * 1024)
        }

    def ocr_image(self, image_path: str) -> Tuple[str, float, dict]:
        """
        对图片进行OCR识别
        
        Returns:
            (识别文本, OCR时间, OCR结果详情)
        """
        start_time = time.time()
        
        try:
            result = self.ocr.ocr(image_path)
            
            ocr_time = time.time() - start_time
            
            if result and isinstance(result, list):
                text = '\n'.join([item['text'] for item in result if 'text' in item])
                text_length = len(text)
                text_lines = len([item for item in result if 'text' in item])
            else:
                text = ''
                text_length = 0
                text_lines = 0
            
            return text, ocr_time, {
                'result_count': len(result) if result else 0,
                'text_length': text_length,
                'text_lines': text_lines
            }
        except Exception as e:
            ocr_time = time.time() - start_time
            return '', ocr_time, {
                'error': str(e),
                'result_count': 0,
                'text_length': 0,
                'text_lines': 0
            }

    def test_single_image(self, image_path: str, optimization_params: dict) -> dict:
        """
        测试单个图片的OCR性能
        
        Args:
            image_path: 图片路径
            optimization_params: 优化参数
            
        Returns:
            测试结果字典
        """
        print(f"\n测试图片: {Path(image_path).name}")
        print("=" * 60)
        
        original_info = self.get_file_info(image_path)
        
        print(f"原始图片: {original_info['size_mb']:.2f} MB")
        
        original_text, original_ocr_time, original_details = self.ocr_image(image_path)
        print(f"原始OCR时间: {original_ocr_time:.3f}秒")
        print(f"识别文本长度: {original_details['text_length']} 字符")
        print(f"识别文本行数: {original_details['text_lines']} 行")
        
        opt_result, opt_time = self.optimizer.optimize_image(
            image_path,
            output_name=None,
            **optimization_params
        )
        
        optimized_path = opt_result['output_path']
        optimized_info = self.get_file_info(optimized_path)
        
        print(f"\n优化后图片: {optimized_info['size_mb']:.2f} MB")
        print(f"压缩率: {(1 - optimized_info['size_mb'] / original_info['size_mb']) * 100:.1f}%")
        print(f"图片优化时间: {opt_time:.3f}秒")
        
        optimized_text, optimized_ocr_time, optimized_details = self.ocr_image(optimized_path)
        print(f"优化后OCR时间: {optimized_ocr_time:.3f}秒")
        print(f"识别文本长度: {optimized_details['text_length']} 字符")
        print(f"识别文本行数: {optimized_details['text_lines']} 行")
        
        total_optimized_time = opt_time + optimized_ocr_time
        time_improvement = (original_ocr_time - optimized_ocr_time) / original_ocr_time * 100
        total_time_improvement = (original_ocr_time - total_optimized_time) / original_ocr_time * 100
        
        print(f"\n性能对比:")
        print(f"  OCR时间节省: {time_improvement:+.1f}%")
        print(f"  总时间(含优化): {total_optimized_time:.3f}秒")
        print(f"  总时间变化: {total_time_improvement:+.1f}%")
        
        text_similarity = self.calculate_text_similarity(original_text, optimized_text)
        print(f"  文本相似度: {text_similarity:.2%}")
        
        return {
            'image_name': Path(image_path).name,
            'original': {
                'size_mb': original_info['size_mb'],
                'ocr_time': original_ocr_time,
                'text_length': original_details['text_length'],
                'text_lines': original_details['text_lines'],
                'text': original_text
            },
            'optimized': {
                'size_mb': optimized_info['size_mb'],
                'compression_ratio': (1 - optimized_info['size_mb'] / original_info['size_mb']) * 100,
                'opt_time': opt_time,
                'ocr_time': optimized_ocr_time,
                'total_time': total_optimized_time,
                'text_length': optimized_details['text_length'],
                'text_lines': optimized_details['text_lines'],
                'text': optimized_text
            },
            'performance': {
                'ocr_time_improvement': time_improvement,
                'total_time_improvement': total_time_improvement,
                'text_similarity': text_similarity
            },
            'optimization_params': optimization_params
        }

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简单的字符匹配）"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        set1 = set(text1)
        set2 = set(text2)
        
        intersection = set1 & set2
        union = set1 | set2
        
        return len(intersection) / len(union) if union else 0.0

    def test_multiple_strategies(self, image_path: str) -> List[dict]:
        """测试多种优化策略"""
        strategies = [
            {
                'name': '策略1: 仅调整大小',
                'params': {
                    'resize': True,
                    'max_width': 2000,
                    'max_height': 2000,
                    'grayscale': False,
                    'enhance_contrast': False,
                    'enhance_sharpness': False,
                    'binarize': False,
                    'denoise': False,
                    'quality': 85
                }
            },
            {
                'name': '策略2: 调整大小 + 灰度',
                'params': {
                    'resize': True,
                    'max_width': 2000,
                    'max_height': 2000,
                    'grayscale': True,
                    'enhance_contrast': False,
                    'enhance_sharpness': False,
                    'binarize': False,
                    'denoise': False,
                    'quality': 85
                }
            },
            {
                'name': '策略3: 调整大小 + 灰度 + 对比度增强',
                'params': {
                    'resize': True,
                    'max_width': 2000,
                    'max_height': 2000,
                    'grayscale': True,
                    'enhance_contrast': True,
                    'enhance_sharpness': False,
                    'binarize': False,
                    'denoise': False,
                    'quality': 85
                }
            },
            {
                'name': '策略4: 调整大小 + 灰度 + 对比度增强 + 清晰度增强',
                'params': {
                    'resize': True,
                    'max_width': 2000,
                    'max_height': 2000,
                    'grayscale': True,
                    'enhance_contrast': True,
                    'enhance_sharpness': True,
                    'binarize': False,
                    'denoise': False,
                    'quality': 85
                }
            },
            {
                'name': '策略5: 激进压缩 (1500px, 质量60)',
                'params': {
                    'resize': True,
                    'max_width': 1500,
                    'max_height': 1500,
                    'grayscale': True,
                    'enhance_contrast': True,
                    'enhance_sharpness': True,
                    'binarize': False,
                    'denoise': False,
                    'quality': 60
                }
            }
        ]
        
        results = []
        
        print(f"\n{'='*70}")
        print(f"测试图片: {Path(image_path).name}")
        print(f"{'='*70}")
        
        original_info = self.get_file_info(image_path)
        print(f"原始图片: {original_info['size_mb']:.2f} MB")
        
        original_text, original_ocr_time, original_details = self.ocr_image(image_path)
        print(f"原始OCR时间: {original_ocr_time:.3f}秒")
        print(f"识别文本长度: {original_details['text_length']} 字符")
        
        for strategy in strategies:
            print(f"\n{strategy['name']}")
            print("-" * 70)
            
            opt_result, opt_time = self.optimizer.optimize_image(
                image_path,
                output_name=f"strategy_{len(results)}.jpg",
                **strategy['params']
            )
            
            optimized_path = opt_result['output_path']
            optimized_info = self.get_file_info(optimized_path)
            
            print(f"  优化后大小: {optimized_info['size_mb']:.2f} MB (压缩率: {(1 - optimized_info['size_mb'] / original_info['size_mb']) * 100:.1f}%)")
            print(f"  优化时间: {opt_time:.3f}秒")
            
            optimized_text, optimized_ocr_time, optimized_details = self.ocr_image(optimized_path)
            
            print(f"  OCR时间: {optimized_ocr_time:.3f}秒")
            print(f"  识别文本长度: {optimized_details['text_length']} 字符")
            
            total_time = opt_time + optimized_ocr_time
            ocr_improvement = (original_ocr_time - optimized_ocr_time) / original_ocr_time * 100
            total_improvement = (original_ocr_time - total_time) / original_ocr_time * 100
            similarity = self.calculate_text_similarity(original_text, optimized_text)
            
            print(f"  OCR时间节省: {ocr_improvement:+.1f}%")
            print(f"  总时间变化: {total_improvement:+.1f}%")
            print(f"  文本相似度: {similarity:.2%}")
            
            results.append({
                'strategy_name': strategy['name'],
                'original_size_mb': original_info['size_mb'],
                'optimized_size_mb': optimized_info['size_mb'],
                'compression_ratio': (1 - optimized_info['size_mb'] / original_info['size_mb']) * 100,
                'opt_time': opt_time,
                'original_ocr_time': original_ocr_time,
                'optimized_ocr_time': optimized_ocr_time,
                'total_time': total_time,
                'ocr_time_improvement': ocr_improvement,
                'total_time_improvement': total_improvement,
                'text_similarity': similarity,
                'original_text_length': original_details['text_length'],
                'optimized_text_length': optimized_details['text_length']
            })
        
        print(f"\n{'='*70}")
        print("策略对比总结")
        print(f"{'='*70}")
        print(f"{'策略':<40} {'压缩率':<10} {'OCR时间':<10} {'总时间':<10} {'相似度':<10}")
        print("-" * 80)
        for r in results:
            print(f"{r['strategy_name']:<40} {r['compression_ratio']:<10.1f}% "
                  f"{r['optimized_ocr_time']:<10.3f}s {r['total_time']:<10.3f}s {r['text_similarity']:<10.2%}")
        
        return results

    def save_results(self, results: List[dict], output_file: str = "ocr_performance_results.json"):
        """保存测试结果到JSON文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n测试结果已保存到: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("使用方法: python ocr_performance_test.py <图片路径> [策略名称]")
        print("\n策略名称（可选）:")
        print("  - default: 调整大小 + 灰度 + 对比度增强 + 清晰度增强")
        print("  - all: 测试所有策略")
        print("\n示例:")
        print("  python ocr_performance_test.py test_image.jpg")
        print("  python ocr_performance_test.py test_image.jpg all")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"错误: 图片文件不存在: {image_path}")
        sys.exit(1)
    
    tester = OCRPerformanceTester()
    
    strategy = sys.argv[2] if len(sys.argv) > 2 else 'default'
    
    if strategy == 'all':
        results = tester.test_multiple_strategies(image_path)
        tester.save_results(results)
    else:
        default_params = {
            'resize': True,
            'max_width': 2000,
            'max_height': 2000,
            'grayscale': True,
            'enhance_contrast': True,
            'enhance_sharpness': True,
            'binarize': False,
            'denoise': False,
            'quality': 85
        }
        result = tester.test_single_image(image_path, default_params)
        tester.save_results([result])


if __name__ == "__main__":
    main()
