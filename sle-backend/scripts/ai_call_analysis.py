"""
AI调用详细分析脚本
分析AI指标解析的各个环节耗时
"""

import sys
import time
from pathlib import Path
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ai_semantic_service import parse_report_with_ai
from app.services.report_parser import extract_text_from_file


async def analyze_ai_call(file_path: str, report_type: str = "lab"):
    """详细分析AI调用的各个环节"""
    
    print(f"\n{'='*70}")
    print(f"AI调用详细分析: {Path(file_path).name}")
    print(f"{'='*70}\n")
    
    # 1. OCR提取文本
    print("步骤1: OCR提取文本")
    print("-" * 70)
    ocr_start = time.time()
    text = extract_text_from_file(file_path)
    ocr_time = time.time() - ocr_start
    print(f"OCR时间: {ocr_time:.3f}秒")
    print(f"文本长度: {len(text)} 字符")
    print(f"文本预览: {text[:200]}...\n")
    
    # 2. 构建提示词
    print("步骤2: 构建AI提示词")
    print("-" * 70)
    from app.services.ai_semantic_service import ai_semantic_service
    prompt_start = time.time()
    prompt = ai_semantic_service.classifier._build_report_parsing_prompt(text, report_type)
    prompt_time = time.time() - prompt_start
    print(f"提示词构建时间: {prompt_time:.3f}秒")
    print(f"提示词长度: {len(prompt)} 字符")
    print(f"提示词预览: {prompt[:500]}...\n")
    
    # 3. HTTP请求准备
    print("步骤3: HTTP请求准备")
    print("-" * 70)
    from app.config.settings import settings
    print(f"AI服务提供商: {settings.AI_SERVICE_PROVIDER}")
    print(f"AI模型: {settings.ZHIPU_MODEL if settings.AI_SERVICE_PROVIDER == 'zhipu' else settings.ALIYUN_MODEL}")
    print(f"API地址: {settings.ZHIPU_BASE_URL if settings.AI_SERVICE_PROVIDER == 'zhipu' else settings.ALIYUN_BASE_URL}")
    print(f"超时设置: 60.0秒\n")
    
    # 4. AI调用
    print("步骤4: AI API调用")
    print("-" * 70)
    ai_call_start = time.time()
    
    try:
        result = await parse_report_with_ai(text, report_type)
        
        ai_call_time = time.time() - ai_call_start
        print(f"AI调用总时间: {ai_call_time:.3f}秒")
        print(f"解析指标数: {len(result.get('indicators', []))}")
        print(f"患者信息: {result.get('patient_info', {})}")
        print(f"报告信息: {result.get('report_info', {})}")
        
        print("\n解析的指标:")
        for idx, indicator in enumerate(result.get('indicators', [])[:5]):
            print(f"  {idx+1}. {indicator.get('name', '')}: {indicator.get('value', '')} {indicator.get('unit', '')}")
        if len(result.get('indicators', [])) > 5:
            print(f"  ... 还有 {len(result.get('indicators', [])) - 5} 个指标")
        
        # 5. 时间分解
        print(f"\n步骤5: 时间分解")
        print("-" * 70)
        print(f"OCR时间: {ocr_time:.3f}秒 ({ocr_time/ai_call_time*100:.1f}%)")
        print(f"提示词构建: {prompt_time:.3f}秒 ({prompt_time/ai_call_time*100:.1f}%)")
        print(f"AI API调用: {ai_call_time:.3f}秒 ({ai_call_time/ai_call_time*100:.1f}%)")
        print(f"总时间: {ocr_time + prompt_time + ai_call_time:.3f}秒")
        
        return {
            'ocr_time': ocr_time,
            'prompt_time': prompt_time,
            'ai_call_time': ai_call_time,
            'total_time': ocr_time + prompt_time + ai_call_time,
            'result': result
        }
        
    except Exception as e:
        ai_call_time = time.time() - ai_call_start
        print(f"AI调用失败，耗时: {ai_call_time:.3f}秒")
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return {
            'ocr_time': ocr_time,
            'prompt_time': prompt_time,
            'ai_call_time': ai_call_time,
            'error': str(e)
        }


async def test_multiple_times(file_path: str, report_type: str = "lab", times: int = 3):
    """多次测试AI调用，观察时间稳定性"""
    print(f"\n{'='*70}")
    print(f"多次AI调用测试: {times}次")
    print(f"{'='*70}\n")
    
    results = []
    for i in range(times):
        print(f"\n--- 第{i+1}次测试 ---")
        result = await analyze_ai_call(file_path, report_type)
        results.append(result)
        if i < times - 1:
            await asyncio.sleep(2)
    
    # 统计分析
    print(f"\n{'='*70}")
    print("统计总结")
    print(f"{'='*70}\n")
    
    ai_call_times = [r['ai_call_time'] for r in results if 'ai_call_time' in r]
    if ai_call_times:
        print(f"AI调用时间统计:")
        print(f"  最小值: {min(ai_call_times):.3f}秒")
        print(f"  最大值: {max(ai_call_times):.3f}秒")
        print(f"  平均值: {sum(ai_call_times)/len(ai_call_times):.3f}秒")
        print(f"  标准差: {(sum((x - sum(ai_call_times)/len(ai_call_times))**2 for x in ai_call_times)/len(ai_call_times))**0.5:.3f}秒")


def main():
    if len(sys.argv) < 2:
        print("使用方法: python ai_call_analysis.py <文件路径> [报告类型] [测试次数]")
        print("\n报告类型 (可选):")
        print("  - lab: 化验报告 (默认)")
        print("  - pathology: 病理报告")
        print("\n测试次数 (可选):")
        print("  - 默认1次，可以指定多次测试")
        print("\n示例:")
        print("  python ai_call_analysis.py test_images/medical_report.png")
        print("  python ai_call_analysis.py test_images/medical_report.png lab 3")
        sys.exit(1)
    
    file_path = sys.argv[1]
    report_type = sys.argv[2] if len(sys.argv) > 2 else 'lab'
    times = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    if not Path(file_path).exists():
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    
    if times == 1:
        asyncio.run(analyze_ai_call(file_path, report_type))
    else:
        asyncio.run(test_multiple_times(file_path, report_type, times))


if __name__ == "__main__":
    main()
