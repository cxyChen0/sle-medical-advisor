"""
医学术语归一化服务
用于将不同医院检查单上的相同项目名称归一化为标准术语
"""

from typing import List, Dict
import json
import os
import re
from app.services.ai_semantic_service import classify_term_with_ai, classify_terms_batch_with_ai
from app.config.settings import settings

# 标准医学术语映射库
STANDARD_TERMS = {
    # 自身抗体
    "抗核抗体": ["ANA", "抗核抗体测定", "抗核抗体检测", "ANA抗体"],
    "抗双链DNA抗体": ["dsDNA", "抗dsDNA抗体", "双链DNA抗体", "ds-DNA"],
    "Sm抗体": ["抗Sm抗体", "Sm蛋白抗体"],
    "RNP抗体": ["抗RNP抗体", "核糖核蛋白抗体"],
    "SSA抗体": ["抗SSA抗体", "Ro抗体", "抗Ro抗体"],
    "SSB抗体": ["抗SSB抗体", "La抗体", "抗La抗体"],
    
    # 血常规
    "白细胞计数": ["白细胞", "WBC", "白血球计数", "白细胞数"],
    "红细胞计数": ["红细胞", "RBC", "红血球计数", "红细胞数"],
    "血红蛋白": ["Hb", "血色素", "血红蛋白浓度"],
    "血小板计数": ["血小板", "PLT", "血小板数"],
    
    # 尿常规
    "尿蛋白": ["蛋白", "PRO", "尿液蛋白", "尿中蛋白"],
    "尿红细胞": ["红细胞", "ERY", "尿潜血", "隐血"],
    "尿白细胞": ["白细胞", "LEU", "尿中白细胞"],
    
    # 免疫功能
    "C3": ["补体C3", "C3补体", "补体成分3"],
    "C4": ["补体C4", "C4补体", "补体成分4"],
    "IgG": ["免疫球蛋白G", "IgG抗体", "免疫球蛋白G测定"],
    "IgA": ["免疫球蛋白A", "IgA抗体", "免疫球蛋白A测定"],
    "IgM": ["免疫球蛋白M", "IgM抗体", "免疫球蛋白M测定"]
}

# 反向映射：从变体到标准术语
VARIANT_TO_STANDARD = {}
for standard, variants in STANDARD_TERMS.items():
    for variant in variants:
        # 添加原始变体
        VARIANT_TO_STANDARD[variant] = standard
        # 添加小写变体
        VARIANT_TO_STANDARD[variant.lower()] = standard
    # 标准术语本身也映射到自己
    VARIANT_TO_STANDARD[standard] = standard
    # 添加标准术语的小写形式
    VARIANT_TO_STANDARD[standard.lower()] = standard


async def normalize_medical_terms(terms: List[str]) -> List[Dict]:
    """
    归一化医学术语列表
    
    Args:
        terms: 需要归一化的术语列表
        
    Returns:
        归一化后的术语列表，每个元素包含原始术语、归一化术语和置信度
    """
    normalized_terms = []
    
    for term in terms:
        normalized, confidence = _normalize_term_sync(term)
        normalized_terms.append({
            "original": term,
            "normalized": normalized,
            "confidence": confidence
        })
    
    return normalized_terms


def _normalize_term_sync(term: str) -> tuple:
    """
    归一化单个医学术语（同步版本，不使用AI）
    
    Args:
        term: 需要归一化的术语
        
    Returns:
        (归一化术语, 置信度)
    """
    term_clean = _clean_term(term)
    
    # 1. 精确匹配 - 考虑大小写
    if term_clean in VARIANT_TO_STANDARD:
        return VARIANT_TO_STANDARD[term_clean], 1.0
    
    # 检查原始术语的精确匹配
    if term in VARIANT_TO_STANDARD:
        return VARIANT_TO_STANDARD[term], 1.0
    
    # 2. 部分匹配
    for variant, standard in VARIANT_TO_STANDARD.items():
        variant_clean = _clean_term(variant)
        if variant_clean in term_clean or term_clean in variant_clean:
            return standard, 0.8
    
    # 3. 关键词匹配
    for standard, variants in STANDARD_TERMS.items():
        all_terms = [standard] + variants
        for t in all_terms:
            t_clean = _clean_term(t)
            if _has_keyword_match(term_clean, t_clean):
                return standard, 0.6
    
    # 4. 对于非医学术语，检查是否为常见字段名
    common_fields = {
        '名称': '名称',
        '手机号': '手机号',
        '联系电话': '联系电话',
        '手机': '手机',
        '客户姓名': '客户姓名',
        '姓名': '姓名',
        '收货人姓名': '收货人姓名',
        '地址': '地址',
        '收货地址': '收货地址',
        '邮编': '邮编',
        '身份证号': '身份证号',
        '出生日期': '出生日期',
        '性别': '性别',
        '年龄': '年龄',
        '民族': '民族',
        '职业': '职业',
        '婚姻状况': '婚姻状况',
        '籍贯': '籍贯',
        '工作单位': '工作单位',
        '紧急联系人': '紧急联系人',
        '邮箱': '邮箱',
        'QQ': 'QQ',
        '微信': '微信',
        '备注': '备注'
    }
    
    # 检查精确匹配
    if term in common_fields:
        return term, 0.9
    
    # 检查部分匹配
    term_lower = term.lower()
    for field_name in common_fields.keys():
        field_lower = field_name.lower()
        if field_lower in term_lower or term_lower in field_lower:
            return field_name, 0.8
    
    # 5. 无法匹配，返回原术语
    return term, 0.5


async def normalize_medical_terms_with_ai(terms: List[str], threshold: float = None) -> List[Dict]:
    """
    使用AI批量归一化医学术语列表
    
    Args:
        terms: 需要归一化的术语列表
        threshold: 置信度阈值
        
    Returns:
        归一化后的术语列表，每个元素包含原始术语、归一化术语和置信度
    """
    if threshold is None:
        threshold = settings.AI_NORMALIZATION_THRESHOLD
    
    # 先用传统方法归一化
    normalized_terms = []
    unknown_terms = []
    unknown_indices = []
    
    for idx, term in enumerate(terms):
        normalized, confidence = _normalize_term_sync(term)
        
        # 如果置信度低于阈值，收集未知术语用于AI处理
        if confidence < threshold:
            unknown_terms.append(term)
            unknown_indices.append(idx)
        
        normalized_terms.append({
            "original": term,
            "normalized": normalized,
            "confidence": confidence
        })
    
    # 对未知术语使用AI批量分类
    if unknown_terms:
        try:
            ai_results = await classify_terms_batch_with_ai(unknown_terms, threshold)
            for idx, ai_result in enumerate(ai_results):
                original_idx = unknown_indices[idx]
                normalized_terms[original_idx] = {
                    "original": unknown_terms[idx],
                    "normalized": ai_result["normalized"],
                    "confidence": ai_result["confidence"]
                }
        except Exception as e:
            print(f"AI批量分类失败，使用传统方法结果: {e}")
    
    return normalized_terms


def _clean_term(term: str) -> str:
    """
    清理术语，去除多余字符和空格
    
    Args:
        term: 原始术语
        
    Returns:
        清理后的术语
    """
    # 去除多余空格
    term = re.sub(r'\s+', ' ', term).strip()
    # 去除括号内容
    term = re.sub(r'\([^)]*\)', '', term).strip()
    # 去除特殊字符
    term = re.sub(r'[^\w\s]', '', term).strip()
    # 转换为小写
    term = term.lower()
    return term


def _has_keyword_match(term1: str, term2: str) -> bool:
    """
    检查两个术语是否有关键词匹配
    
    Args:
        term1: 术语1
        term2: 术语2
        
    Returns:
        是否有关键词匹配
    """
    # 分割术语为关键词
    keywords1 = set(term1.split())
    keywords2 = set(term2.split())
    
    # 计算共同关键词比例
    if not keywords1 or not keywords2:
        return False
    
    common_keywords = keywords1.intersection(keywords2)
    return len(common_keywords) / min(len(keywords1), len(keywords2)) >= 0.5


def update_standard_terms(new_terms: Dict[str, List[str]]):
    """
    更新标准术语库
    
    Args:
        new_terms: 新的术语映射
    """
    global STANDARD_TERMS, VARIANT_TO_STANDARD
    
    # 更新标准术语
    for standard, variants in new_terms.items():
        if standard in STANDARD_TERMS:
            STANDARD_TERMS[standard].extend(variants)
        else:
            STANDARD_TERMS[standard] = variants
    
    # 重新构建反向映射
    VARIANT_TO_STANDARD = {}
    for standard, variants in STANDARD_TERMS.items():
        for variant in variants:
            VARIANT_TO_STANDARD[variant] = standard
        VARIANT_TO_STANDARD[standard] = standard


if __name__ == "__main__":
    # 测试代码
    test_terms = [
        "ANA",
        "白细胞",
        "尿蛋白",
        "补体C3",
        "抗dsDNA抗体",
        "血红蛋白浓度",
        "血小板数",
        "免疫球蛋白G"
    ]
    
    import asyncio
    result = asyncio.run(normalize_medical_terms(test_terms))
    
    print("测试结果:")
    for item in result:
        print(f"{item['original']} → {item['normalized']} (置信度: {item['confidence']:.2f})")
