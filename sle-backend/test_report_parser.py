"""
测试检查单解析服务
"""

import asyncio
from fastapi import UploadFile
from io import BytesIO
from app.services.report_parser import parse_report


async def test_lab_report_parsing():
    """测试化验报告解析"""
    print("=== 测试化验报告解析 ===\n")
    
    # 创建一个模拟的化验报告文件
    test_content = """检查单
患者ID: 001
姓名: 张三
性别: 男
年龄: 30
检查日期: 2026-02-11

检查项目: 血常规、生化、免疫

白细胞计数: 5.8 10^9/L
红细胞计数: 4.5 10^12/L
血红蛋白: 145 g/L
血小板计数: 250 10^9/L

抗核抗体: 阳性
抗双链DNA抗体: 120 IU/mL
Sm抗体: 阴性
RNP抗体: 阴性
SSA抗体: 阳性
SSB抗体: 阴性

C3: 0.9 g/L
C4: 0.2 g/L
IgG: 12.0 g/L
IgA: 2.0 g/L
IgM: 1.0 g/L

尿蛋白: 1+
尿红细胞: 阴性
尿白细胞: 阴性
"""
    
    # 创建模拟文件
    file = UploadFile(
        filename="lab_report.txt",
        file=BytesIO(test_content.encode('utf-8'))
    )
    
    try:
        # 解析报告
        result = await parse_report(file, "lab")
        
        print(f"患者ID: {result.get('patient_id')}")
        print(f"报告日期: {result.get('report_date')}")
        print(f"报告类型: {result.get('report_type')}")
        print(f"解析指标数: {len(result.get('indicators', []))}")
        print(f"归一化结果数: {len(result.get('normalization_results', []))}")
        print()
        
        print("解析的指标:")
        for indicator in result.get('indicators', []):
            print(f"- {indicator.get('name')}: {indicator.get('value')} {indicator.get('unit')}")
            print(f"  参考范围: {indicator.get('reference_range')}")
            print(f"  是否异常: {indicator.get('is_abnormal')}")
        
        print()
        print("归一化结果:")
        for item in result.get('normalization_results', []):
            print(f"- {item.get('original')} → {item.get('normalized')} (置信度: {item.get('confidence', 0):.2f})")
        
        print("\n✅ 化验报告解析测试完成！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await file.close()


async def test_pathology_report_parsing():
    """测试病理报告解析"""
    print("\n=== 测试病理报告解析 ===\n")
    
    # 创建一个模拟的病理报告文件
    test_content = """病理检查报告
患者ID: 001
姓名: 张三
性别: 男
年龄: 30
检查日期: 2026-02-10

标本类型: 皮肤组织
检查项目: 活组织检查

病理发现:
表皮角化过度，真皮浅层血管周围可见淋巴细胞浸润，胶原纤维轻度变性。

病理诊断:
符合系统性红斑狼疮皮肤病变。

备注:
建议结合临床症状和其他检查结果综合判断。
"""
    
    # 创建模拟文件
    file = UploadFile(
        filename="pathology_report.txt",
        file=BytesIO(test_content.encode('utf-8'))
    )
    
    try:
        # 解析报告
        result = await parse_report(file, "pathology")
        
        print(f"患者ID: {result.get('patient_id')}")
        print(f"报告日期: {result.get('report_date')}")
        print(f"报告类型: {result.get('report_type')}")
        print(f"解析指标数: {len(result.get('indicators', []))}")
        print(f"归一化结果数: {len(result.get('normalization_results', []))}")
        print()
        
        print("解析的指标:")
        for indicator in result.get('indicators', []):
            print(f"- {indicator.get('name')}: {indicator.get('value')}")
        
        print()
        print("归一化结果:")
        for item in result.get('normalization_results', []):
            print(f"- {item.get('original')} → {item.get('normalized')} (置信度: {item.get('confidence', 0):.2f})")
        
        print("\n✅ 病理报告解析测试完成！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await file.close()


async def main():
    """主测试函数"""
    print("开始测试检查单解析服务...\n")
    
    try:
        await test_lab_report_parsing()
        await test_pathology_report_parsing()
        
        print("\n✅ 所有测试完成！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
