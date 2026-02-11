"""
OCR文字归一化性能测试脚本
测试OCR、归一化、AI语义分类等各个模块的用时
"""

import sys
import time
from pathlib import Path
from typing import Dict, List
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.report_parser import extract_text_from_file, parse_indicators
from app.services.normalization_service import normalize_medical_terms
from app.services.ai_semantic_service import classify_term_with_ai


class NormalizationPerformanceTester:
    """归一化性能测试器"""

    def __init__(self):
        self.results = []

    def test_full_pipeline(self, file_path: str, report_type: str = "lab") -> dict:
        """
        测试完整流程：OCR -> 解析指标 -> 归一化
        
        Args:
            file_path: 文件路径
            report_type: 报告类型
            
        Returns:
            测试结果字典
        """
        print(f"\n{'='*70}")
        print(f"测试文件: {Path(file_path).name}")
        print(f"{'='*70}\n")
        
        result = {
            'file_name': Path(file_path).name,
            'file_size_mb': Path(file_path).stat().st_size / (1024 * 1024),
            'report_type': report_type,
            'timings': {},
            'metrics': {}
        }
        
        # 1. OCR测试
        print("步骤1: OCR文字识别")
        print("-" * 70)
        ocr_start = time.time()
        text = extract_text_from_file(file_path)
        ocr_time = time.time() - ocr_start
        
        result['timings']['ocr'] = ocr_time
        result['metrics']['text_length'] = len(text)
        result['metrics']['text_preview'] = text[:100] if text else ''
        
        print(f"OCR时间: {ocr_time:.3f}秒")
        print(f"识别文本长度: {len(text)} 字符")
        print(f"文本预览: {text[:100]}...\n")
        
        # 2. 解析指标测试
        print("步骤2: 解析指标 (AI语义分析)")
        print("-" * 70)
        parse_start = time.time()
        indicators = self._run_async(parse_indicators(text, report_type))
        parse_time = time.time() - parse_start
        
        result['timings']['parse_indicators'] = parse_time
        result['metrics']['indicator_count'] = len(indicators)
        
        print(f"解析时间: {parse_time:.3f}秒")
        print(f"解析指标数: {len(indicators)}")
        print(f"指标列表:")
        for ind in indicators[:5]:
            print(f"  - {ind.get('name', '')}: {ind.get('value', '')} {ind.get('unit', '')}")
        if len(indicators) > 5:
            print(f"  ... 还有 {len(indicators) - 5} 个指标")
        print()
        
        # 3. 归一化测试
        if indicators:
            print("步骤3: 医学术语归一化")
            print("-" * 70)
            
            # 提取指标名称
            indicator_names = [ind.get('name', '') for ind in indicators]
            
            norm_start = time.time()
            normalized_results = self._run_async(normalize_medical_terms(indicator_names))
            norm_time = time.time() - norm_start
            
            result['timings']['normalization'] = norm_time
            result['metrics']['normalized_count'] = len([r for r in normalized_results if r.get('normalized') != r.get('original')])
            
            print(f"归一化时间: {norm_time:.3f}秒")
            print(f"归一化结果数: {len(normalized_results)}")
            print(f"实际归一化数: {result['metrics']['normalized_count']}")
            print(f"归一化详情:")
            for res in normalized_results[:5]:
                print(f"  - {res.get('original', '')} -> {res.get('normalized', '')} (置信度: {res.get('confidence', 0):.2f})")
            if len(normalized_results) > 5:
                print(f"  ... 还有 {len(normalized_results) - 5} 个结果")
            print()
            
            # 4. AI分类测试（针对未知术语）
            unknown_terms = [res.get('original', '') for res in normalized_results if res.get('confidence', 0) < 0.6]
            if unknown_terms:
                print("步骤4: AI语义分类 (未知术语)")
                print("-" * 70)
                
                ai_results = []
                ai_times = []
                for term in unknown_terms[:3]:
                    ai_start = time.time()
                    ai_result = self._run_async(classify_term_with_ai(term))
                    ai_time = time.time() - ai_start
                    ai_times.append(ai_time)
                    ai_results.append({
                        'term': term,
                        'normalized': ai_result.get('normalized', ''),
                        'category': ai_result.get('category', ''),
                        'confidence': ai_result.get('confidence', 0),
                        'time': ai_time
                    })
                    print(f"  {term} -> {ai_result.get('normalized', '')} (置信度: {ai_result.get('confidence', 0):.2f}, 时间: {ai_time:.3f}s)")
                
                result['timings']['ai_classification'] = sum(ai_times)
                result['metrics']['ai_classified_count'] = len(ai_results)
                result['metrics']['ai_classification_details'] = ai_results
                print()
            else:
                print("步骤4: AI语义分类 (无需处理)")
                print("-" * 70)
                print("所有术语都已通过传统方法归一化，无需AI分类\n")
                result['timings']['ai_classification'] = 0
                result['metrics']['ai_classified_count'] = 0
        
        # 5. 总体统计
        total_time = sum(result['timings'].values())
        result['timings']['total'] = total_time
        
        print(f"{'='*70}")
        print("性能总结")
        print(f"{'='*70}")
        print(f"{'步骤':<25} {'时间':<15} {'占比':<10}")
        print("-" * 50)
        for step, step_time in result['timings'].items():
            if step != 'total':
                percentage = (step_time / total_time * 100) if total_time > 0 else 0
                print(f"{step:<25} {step_time:<15.3f}s {percentage:<10.1f}%")
        print("-" * 50)
        print(f"{'总计':<25} {total_time:<15.3f}s 100.0%")
        print()
        
        self.results.append(result)
        return result

    def _run_async(self, coro):
        """运行异步函数"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    def test_multiple_files(self, file_paths: List[str], report_type: str = "lab"):
        """测试多个文件"""
        for file_path in file_paths:
            if Path(file_path).exists():
                self.test_full_pipeline(file_path, report_type)
            else:
                print(f"警告: 文件不存在: {file_path}")

    def generate_summary(self):
        """生成测试总结"""
        if not self.results:
            print("没有测试结果")
            return
        
        print(f"\n{'='*70}")
        print("整体测试总结")
        print(f"{'='*70}\n")
        
        total_files = len(self.results)
        avg_timings = {}
        
        for result in self.results:
            for step, step_time in result['timings'].items():
                if step not in avg_timings:
                    avg_timings[step] = []
                avg_timings[step].append(step_time)
        
        print(f"测试文件数: {total_files}")
        print(f"\n平均时间:")
        print(f"{'步骤':<25} {'平均时间':<15} {'最大时间':<15} {'最小时间':<15}")
        print("-" * 70)
        for step in sorted(avg_timings.keys()):
            times = avg_timings[step]
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            print(f"{step:<25} {avg_time:<15.3f}s {max_time:<15.3f}s {min_time:<15.3f}s")
        
        print()
        
        avg_total = avg_timings.get('total', [0])[0]
        avg_ocr = avg_timings.get('ocr', [0])[0]
        avg_parse = avg_timings.get('parse_indicators', [0])[0]
        avg_norm = avg_timings.get('normalization', [0])[0]
        avg_ai = avg_timings.get('ai_classification', [0])[0]
        
        print("时间占比分析:")
        if avg_total > 0:
            print(f"  OCR识别: {avg_ocr / avg_total * 100:.1f}%")
            print(f"  指标解析: {avg_parse / avg_total * 100:.1f}%")
            print(f"  术语归一化: {avg_norm / avg_total * 100:.1f}%")
            print(f"  AI分类: {avg_ai / avg_total * 100:.1f}%")
        
        print()

    def save_results(self, output_file: str = "normalization_performance_results.json"):
        """保存测试结果到JSON文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"测试结果已保存到: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("使用方法: python normalization_performance_test.py <文件路径> [报告类型]")
        print("\n报告类型 (可选):")
        print("  - lab: 化验报告 (默认)")
        print("  - pathology: 病理报告")
        print("\n示例:")
        print("  python normalization_performance_test.py test_images/medical_report.png")
        print("  python normalization_performance_test.py test_images/medical_report.png lab")
        print("  python normalization_performance_test.py test_images/*.png lab")
        sys.exit(1)
    
    file_path = sys.argv[1]
    report_type = sys.argv[2] if len(sys.argv) > 2 else 'lab'
    
    tester = NormalizationPerformanceTester()
    
    if '*' in file_path:
        from glob import glob
        file_paths = glob(file_path)
        tester.test_multiple_files(file_paths, report_type)
    else:
        if Path(file_path).exists():
            tester.test_full_pipeline(file_path, report_type)
        else:
            print(f"错误: 文件不存在: {file_path}")
            sys.exit(1)
    
    tester.generate_summary()
    tester.save_results()


if __name__ == "__main__":
    main()
