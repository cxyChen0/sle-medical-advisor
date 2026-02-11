"""
OCR性能验证脚本
分析所有测试图片的OCR性能和识别准确性
"""

import json
from pathlib import Path
from difflib import SequenceMatcher
from typing import Dict, List, Any


def load_test_results() -> List[Dict[str, Any]]:
    """加载测试结果"""
    results_file = Path("ocr_performance_results.json")
    if results_file.exists():
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度"""
    return SequenceMatcher(None, text1, text2).ratio()


def analyze_performance_data(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析性能数据"""
    if not results:
        return {}
    
    # 检查数据格式
    if 'strategy_name' in results[0]:
        # 策略测试格式
        total_strategies = len(results)
        avg_original_size = sum(r['original_size_mb'] for r in results) / total_strategies
        avg_optimized_size = sum(r['optimized_size_mb'] for r in results) / total_strategies
        avg_compression_ratio = sum(r['compression_ratio'] for r in results) / total_strategies
        
        avg_original_ocr_time = sum(r['original_ocr_time'] for r in results) / total_strategies
        avg_optimized_ocr_time = sum(r['optimized_ocr_time'] for r in results) / total_strategies
        avg_optimization_time = sum(r['opt_time'] for r in results) / total_strategies
        
        avg_text_similarity = sum(r['text_similarity'] for r in results) / total_strategies
        
        avg_ocr_time_saving = sum(r['ocr_time_improvement'] for r in results) / total_strategies
        avg_total_time_saving = sum(r['total_time_improvement'] for r in results) / total_strategies
        
        return {
            'test_type': 'strategy_comparison',
            'total_strategies_tested': total_strategies,
            'file_size': {
                'avg_original_mb': round(avg_original_size, 3),
                'avg_optimized_mb': round(avg_optimized_size, 3),
                'avg_compression_ratio': round(avg_compression_ratio, 2)
            },
            'processing_time': {
                'avg_original_ocr_time': round(avg_original_ocr_time, 3),
                'avg_optimized_ocr_time': round(avg_optimized_ocr_time, 3),
                'avg_optimization_time': round(avg_optimization_time, 3),
                'avg_total_time': round(avg_optimized_ocr_time + avg_optimization_time, 3)
            },
            'performance_improvement': {
                'avg_ocr_time_saving_pct': round(avg_ocr_time_saving, 2),
                'avg_total_time_saving_pct': round(avg_total_time_saving, 2)
            },
            'accuracy': {
                'avg_text_similarity': round(avg_text_similarity * 100, 2)
            }
        }
    else:
        # 单图片测试格式
        total_images = len(results)
        avg_original_size = sum(r['original']['size_mb'] for r in results) / total_images
        avg_optimized_size = sum(r['optimized']['size_mb'] for r in results) / total_images
        avg_compression_ratio = sum(r['optimized']['compression_ratio'] for r in results) / total_images
        
        avg_original_ocr_time = sum(r['original']['ocr_time'] for r in results) / total_images
        avg_optimized_ocr_time = sum(r['optimized']['ocr_time'] for r in results) / total_images
        avg_optimization_time = sum(r['optimized']['opt_time'] for r in results) / total_images
        
        avg_text_similarity = sum(r['performance']['text_similarity'] for r in results) / total_images
        
        avg_ocr_time_saving = sum(r['performance']['ocr_time_improvement'] for r in results) / total_images
        avg_total_time_saving = sum(r['performance']['total_time_improvement'] for r in results) / total_images
        
        return {
            'test_type': 'single_image',
            'total_images_tested': total_images,
            'file_size': {
                'avg_original_mb': round(avg_original_size, 3),
                'avg_optimized_mb': round(avg_optimized_size, 3),
                'avg_compression_ratio': round(avg_compression_ratio, 2)
            },
            'processing_time': {
                'avg_original_ocr_time': round(avg_original_ocr_time, 3),
                'avg_optimized_ocr_time': round(avg_optimized_ocr_time, 3),
                'avg_optimization_time': round(avg_optimization_time, 3),
                'avg_total_time': round(avg_optimized_ocr_time + avg_optimization_time, 3)
            },
            'performance_improvement': {
                'avg_ocr_time_saving_pct': round(avg_ocr_time_saving, 2),
                'avg_total_time_saving_pct': round(avg_total_time_saving, 2)
            },
            'accuracy': {
                'avg_text_similarity': round(avg_text_similarity * 100, 2)
            }
        }


def generate_performance_report(results: List[Dict[str, Any]]) -> str:
    """生成性能报告"""
    analysis = analyze_performance_data(results)
    
    report = []
    report.append("=" * 80)
    report.append("OCR性能验证报告")
    report.append("=" * 80)
    report.append("")
    
    if not analysis:
        report.append("未找到测试结果数据")
        return "\n".join(report)
    
    test_type = analysis.get('test_type', 'unknown')
    
    if test_type == 'strategy_comparison':
        # 策略对比测试报告
        report.append("【测试类型】策略对比测试")
        report.append(f"测试策略数量: {analysis['total_strategies_tested']}")
        report.append("")
        
        # 文件大小分析
        report.append("【文件大小分析】")
        report.append(f"平均原始文件大小: {analysis['file_size']['avg_original_mb']} MB")
        report.append(f"平均优化后文件大小: {analysis['file_size']['avg_optimized_mb']} MB")
        report.append(f"平均压缩率: {analysis['file_size']['avg_compression_ratio']}%")
        report.append("")
        
        # 处理时间分析
        report.append("【处理时间分析】")
        report.append(f"平均原始OCR时间: {analysis['processing_time']['avg_original_ocr_time']} 秒")
        report.append(f"平均优化后OCR时间: {analysis['processing_time']['avg_optimized_ocr_time']} 秒")
        report.append(f"平均图片优化时间: {analysis['processing_time']['avg_optimization_time']} 秒")
        report.append(f"平均总处理时间: {analysis['processing_time']['avg_total_time']} 秒")
        report.append("")
        
        # 性能提升
        report.append("【性能提升】")
        report.append(f"平均OCR时间节省: {analysis['performance_improvement']['avg_ocr_time_saving_pct']}%")
        report.append(f"平均总时间节省: {analysis['performance_improvement']['avg_total_time_saving_pct']}%")
        report.append("")
        
        # 识别准确性
        report.append("【识别准确性】")
        report.append(f"平均文本相似度: {analysis['accuracy']['avg_text_similarity']}%")
        report.append("")
        
        # 详细结果
        report.append("=" * 80)
        report.append("【策略对比详细结果】")
        report.append("=" * 80)
        report.append("")
        
        report.append(f"{'策略名称':<50} {'压缩率':<10} {'OCR时间':<10} {'总时间':<10} {'相似度':<10}")
        report.append("-" * 90)
        
        for result in results:
            report.append(f"{result['strategy_name']:<50} "
                          f"{result['compression_ratio']:<10.1f}% "
                          f"{result['optimized_ocr_time']:<10.3f}s "
                          f"{result['total_time']:<10.3f}s "
                          f"{result['text_similarity']:<10.2%}")
        
        report.append("")
        
        # 最佳策略推荐
        best_similarity = max(results, key=lambda x: x['text_similarity'])
        best_time = min(results, key=lambda x: x['total_time'])
        
        report.append("=" * 80)
        report.append("【最佳策略推荐】")
        report.append("=" * 80)
        report.append(f"最高识别准确率: {best_similarity['strategy_name']} (相似度: {best_similarity['text_similarity']:.2%})")
        report.append(f"最快处理速度: {best_time['strategy_name']} (总时间: {best_time['total_time']:.3f}s)")
        report.append("")
        
    else:
        # 单图片测试报告
        report.append("【总体统计】")
        report.append(f"测试图片数量: {analysis['total_images_tested']}")
        report.append("")
        
        # 文件大小分析
        report.append("【文件大小分析】")
        report.append(f"平均原始文件大小: {analysis['file_size']['avg_original_mb']} MB")
        report.append(f"平均优化后文件大小: {analysis['file_size']['avg_optimized_mb']} MB")
        report.append(f"平均压缩率: {analysis['file_size']['avg_compression_ratio']}%")
        report.append("")
        
        # 处理时间分析
        report.append("【处理时间分析】")
        report.append(f"平均原始OCR时间: {analysis['processing_time']['avg_original_ocr_time']} 秒")
        report.append(f"平均优化后OCR时间: {analysis['processing_time']['avg_optimized_ocr_time']} 秒")
        report.append(f"平均图片优化时间: {analysis['processing_time']['avg_optimization_time']} 秒")
        report.append(f"平均总处理时间: {analysis['processing_time']['avg_total_time']} 秒")
        report.append("")
        
        # 性能提升
        report.append("【性能提升】")
        report.append(f"平均OCR时间节省: {analysis['performance_improvement']['avg_ocr_time_saving_pct']}%")
        report.append(f"平均总时间节省: {analysis['performance_improvement']['avg_total_time_saving_pct']}%")
        report.append("")
        
        # 识别准确性
        report.append("【识别准确性】")
        report.append(f"平均文本相似度: {analysis['accuracy']['avg_text_similarity']}%")
        report.append("")
        
        # 详细结果
        report.append("=" * 80)
        report.append("【详细测试结果】")
        report.append("=" * 80)
        report.append("")
        
        for i, result in enumerate(results, 1):
            report.append(f"测试 {i}: {result.get('image_name', 'unknown')}")
            report.append("-" * 80)
            
            report.append(f"  原始文件大小: {result['original']['size_mb']:.3f} MB")
            report.append(f"  优化后文件大小: {result['optimized']['size_mb']:.3f} MB")
            report.append(f"  压缩率: {result['optimized']['compression_ratio']:.2f}%")
            
            report.append(f"  原始OCR时间: {result['original']['ocr_time']:.3f} 秒")
            report.append(f"  优化后OCR时间: {result['optimized']['ocr_time']:.3f} 秒")
            report.append(f"  优化时间: {result['optimized']['opt_time']:.3f} 秒")
            report.append(f"  总时间: {result['optimized']['total_time']:.3f} 秒")
            
            report.append(f"  OCR时间节省: {result['performance']['ocr_time_improvement']:.2f}%")
            report.append(f"  总时间节省: {result['performance']['total_time_improvement']:.2f}%")
            
            report.append(f"  文本相似度: {result['performance']['text_similarity'] * 100:.2f}%")
            report.append(f"  原始文本长度: {result['original']['text_length']} 字符")
            report.append(f"  优化后文本长度: {result['optimized']['text_length']} 字符")
            
            report.append("")
    
    # 结论
    report.append("=" * 80)
    report.append("【结论】")
    report.append("=" * 80)
    
    avg_similarity = analysis['accuracy']['avg_text_similarity']
    avg_time_saving = analysis['performance_improvement']['avg_total_time_saving_pct']
    
    if avg_similarity > 90:
        report.append("✓ OCR识别准确性良好，文本相似度超过90%")
    elif avg_similarity > 80:
        report.append("○ OCR识别准确性一般，文本相似度在80-90%之间")
    else:
        report.append("✗ OCR识别准确性较差，需要进一步优化")
    
    if avg_time_saving > 0:
        report.append(f"✓ 图片优化有效，平均节省{avg_time_saving:.2f}%的处理时间")
    else:
        report.append(f"✗ 图片优化未带来时间节省，反而增加了{abs(avg_time_saving):.2f}%的时间")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """主函数"""
    print("加载OCR性能测试结果...")
    results = load_test_results()
    
    if not results:
        print("未找到测试结果，请先运行OCR性能测试")
        return
    
    print(f"找到 {len(results)} 个测试结果")
    print("")
    
    print("生成性能报告...")
    report = generate_performance_report(results)
    
    print(report)
    
    # 保存报告
    report_file = Path("ocr_performance_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存到: {report_file}")


if __name__ == "__main__":
    main()