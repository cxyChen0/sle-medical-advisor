"""
AI语义分类服务
用于对未知医学术语进行智能语义理解和分类
支持阿里云百炼和智谱GLM两种AI服务
"""

from typing import Dict, List, Optional
import httpx
import json
from app.config.settings import settings


class AISemanticClassifier:
    """AI语义分类器基类"""
    
    def __init__(self):
        self.standard_terms = {
            "抗核抗体": "自身抗体",
            "抗双链DNA抗体": "自身抗体",
            "Sm抗体": "自身抗体",
            "RNP抗体": "自身抗体",
            "SSA抗体": "自身抗体",
            "SSB抗体": "自身抗体",
            "白细胞计数": "血常规",
            "红细胞计数": "血常规",
            "血红蛋白": "血常规",
            "血小板计数": "血常规",
            "尿蛋白": "尿常规",
            "尿红细胞": "尿常规",
            "尿白细胞": "尿常规",
            "C3": "免疫功能",
            "C4": "免疫功能",
            "IgG": "免疫功能",
            "IgA": "免疫功能",
            "IgM": "免疫功能"
        }
    
    async def classify_term(self, term: str) -> Dict:
        """
        对单个术语进行语义分类
        
        Args:
            term: 需要分类的术语
            
        Returns:
            分类结果字典，包含：
            - normalized: 归一化后的标准术语
            - category: 术语类别
            - confidence: 置信度
            - explanation: 分类说明
        """
        raise NotImplementedError("子类必须实现此方法")
    
    async def classify_terms_batch(self, terms: List[str]) -> List[Dict]:
        """
        批量分类术语 - 使用单次API调用
        
        Args:
            terms: 需要分类的术语列表
            
        Returns:
            分类结果列表
        """
        if not terms:
            return []
        
        # 构建批量分类提示词
        standard_terms_list = "\n".join([f"- {name} ({category})" for name, category in self.standard_terms.items()])
        
        terms_list = "\n".join([f"{i+1}. {term}" for i, term in enumerate(terms)])
        
        prompt = f"""你是一个专业的医学术语分类助手。请将给定的医学术语分类到最接近的标准术语中。

标准术语列表：
{standard_terms_list}

需要分类的术语：
{terms_list}

请分析每个术语的语义，并返回JSON格式的分类结果，格式如下：
{{
  "results": [
    {{
      "original": "原始术语",
      "normalized": "最匹配的标准术语名称",
      "category": "该术语所属的医学类别",
      "confidence": 匹配置信度（0-1之间的浮点数）,
      "explanation": "简要说明分类理由"
    }}
  ]
}}

如果术语与任何标准术语都不相关，请将normalized设为原术语，category设为"其他"，confidence设为0.3。

只返回JSON，不要包含其他内容。"""
        
        if not self.api_key:
            return [
                {
                    "normalized": term,
                    "category": "其他",
                    "confidence": 0.0,
                    "explanation": "未配置API密钥"
                }
                for term in terms
            ]
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    try:
                        parsed_result = json.loads(content)
                        return parsed_result.get("results", [])
                    except json.JSONDecodeError:
                        return [
                            {
                                "normalized": term,
                                "category": "其他",
                                "confidence": 0.4,
                                "explanation": "AI返回结果解析失败"
                            }
                            for term in terms
                        ]
                else:
                    return [
                        {
                            "normalized": term,
                            "category": "其他",
                            "confidence": 0.0,
                            "explanation": f"API调用失败: {response.status_code}"
                        }
                        for term in terms
                    ]
        except Exception as e:
            return [
                {
                    "normalized": term,
                    "category": "其他",
                    "confidence": 0.0,
                    "explanation": f"分类失败: {str(e)}"
                }
                for term in terms
            ]
    
    async def parse_report_text(self, text: str, report_type: str) -> Dict:
        """
        解析检查单文本
        
        Args:
            text: 检查单文本内容
            report_type: 报告类型 (lab/pathology)
            
        Returns:
            解析结果字典
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def _build_classification_prompt(self, term: str) -> str:
        """
        构建分类提示词
        
        Args:
            term: 需要分类的术语
            
        Returns:
            提示词
        """
        standard_terms_list = "\n".join([f"- {name} ({category})" for name, category in self.standard_terms.items()])
        
        prompt = f"""你是一个专业的医学术语分类助手。请将给定的医学术语分类到最接近的标准术语中。

标准术语列表：
{standard_terms_list}

请分析术语 "{term}" 的语义，并返回JSON格式的分类结果，包含以下字段：
- normalized: 最匹配的标准术语名称
- category: 该术语所属的医学类别（如：自身抗体、血常规、尿常规、免疫功能等）
- confidence: 匹配置信度（0-1之间的浮点数）
- explanation: 简要说明分类理由

如果术语与任何标准术语都不相关，请将normalized设为原术语，category设为"其他"，confidence设为0.3。

只返回JSON，不要包含其他内容。"""
        
        return prompt
    
    def _build_report_parsing_prompt(self, text: str, report_type: str) -> str:
        """
        构建检查单解析提示词
        
        Args:
            text: 检查单文本内容
            report_type: 报告类型 (lab/pathology)
            
        Returns:
            提示词
        """
        standard_terms_list = "\n".join([f"- {name} ({category})" for name, category in self.standard_terms.items()])
        
        prompt = f"""你是一个专业的医学检查单解析助手。请从以下检查单文本中提取所有检查指标及其对应值。

检查单类型：{report_type}

检查单文本：
{text}

请返回JSON格式的解析结果，包含以下字段：
- indicators: 指标列表，每个指标包含：
  - name: 指标名称（请使用标准医学术语）
  - value: 指标值
  - unit: 单位（如果有）
  - reference_range: 参考范围（如果有）
  - is_abnormal: 是否异常（布尔值）
  - normalized_name: 归一化后的标准术语名称
  - normalization_confidence: 归一化置信度（0-1之间）
- patient_info: 患者信息（如果能提取到）
  - patient_id: 患者ID
  - name: 患者姓名
  - gender: 性别
  - age: 年龄
- report_info: 报告信息
  - report_date: 检查日期
  - report_number: 报告编号

特别注意：
1. 对于化验报告(lab)，请提取所有的检查项目、数值、单位、参考范围和异常状态
2. 对于病理报告(pathology)，请提取病理发现、病理诊断、标本类型等信息作为指标
3. 请确保提取所有可能的指标，不要遗漏任何信息
4. 如果无法确定某个字段，请保持为空
5. 指标名称请使用标准医学术语，如：白细胞计数、红细胞计数、血红蛋白、血小板计数、抗核抗体、抗双链DNA抗体、Sm抗体、RNP抗体、SSA抗体、SSB抗体、C3、C4、IgG、IgA、IgM、尿蛋白、尿红细胞、尿白细胞等
6. normalized_name应该是标准术语，如果name已经是标准术语，则normalized_name与name相同
7. normalization_confidence应该是0-1之间的数值，表示归一化的置信度

只返回JSON，不要包含其他内容。"""
        
        return prompt


class AliyunClassifier(AISemanticClassifier):
    """阿里云百炼分类器"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.ALIYUN_API_KEY
        self.model = settings.ALIYUN_MODEL
        self.base_url = settings.ALIYUN_BASE_URL
    
    async def classify_term(self, term: str) -> Dict:
        """
        使用阿里云百炼API进行术语分类
        
        Args:
            term: 需要分类的术语
            
        Returns:
            分类结果字典
        """
        if not self.api_key:
            return {
                "normalized": term,
                "category": "其他",
                "confidence": 0.0,
                "explanation": "未配置阿里云API密钥"
            }
        
        try:
            prompt = self._build_classification_prompt(term)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    try:
                        parsed_result = json.loads(content)
                        return {
                            "normalized": parsed_result.get("normalized", term),
                            "category": parsed_result.get("category", "其他"),
                            "confidence": float(parsed_result.get("confidence", 0.5)),
                            "explanation": parsed_result.get("explanation", "")
                        }
                    except json.JSONDecodeError:
                        return {
                            "normalized": term,
                            "category": "其他",
                            "confidence": 0.4,
                            "explanation": "AI返回结果解析失败"
                        }
                else:
                    return {
                        "normalized": term,
                        "category": "其他",
                        "confidence": 0.0,
                        "explanation": f"API调用失败: {response.status_code}"
                    }
        except Exception as e:
            return {
                "normalized": term,
                "category": "其他",
                "confidence": 0.0,
                "explanation": f"分类失败: {str(e)}"
            }
    
    async def parse_report_text(self, text: str, report_type: str) -> Dict:
        """
        使用阿里云百炼API解析检查单文本
        
        Args:
            text: 检查单文本内容
            report_type: 报告类型 (lab/pathology)
            
        Returns:
            解析结果字典
        """
        if not self.api_key:
            return {
                "indicators": [],
                "patient_info": {},
                "report_info": {}
            }
        
        try:
            prompt = self._build_report_parsing_prompt(text, report_type)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    try:
                        parsed_result = json.loads(content)
                        return {
                            "indicators": parsed_result.get("indicators", []),
                            "patient_info": parsed_result.get("patient_info", {}),
                            "report_info": parsed_result.get("report_info", {})
                        }
                    except json.JSONDecodeError:
                        return {
                            "indicators": [],
                            "patient_info": {},
                            "report_info": {}
                        }
                else:
                    return {
                        "indicators": [],
                        "patient_info": {},
                        "report_info": {}
                    }
        except Exception as e:
            return {
                "indicators": [],
                "patient_info": {},
                "report_info": {}
            }


class ZhipuClassifier(AISemanticClassifier):
    """智谱GLM分类器"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.ZHIPU_API_KEY
        self.model = settings.ZHIPU_MODEL
        self.base_url = settings.ZHIPU_BASE_URL
    
    async def classify_term(self, term: str) -> Dict:
        """
        使用智谱GLM API进行术语分类
        
        Args:
            term: 需要分类的术语
            
        Returns:
            分类结果字典
        """
        if not self.api_key:
            return {
                "normalized": term,
                "category": "其他",
                "confidence": 0.0,
                "explanation": "未配置智谱API密钥"
            }
        
        try:
            prompt = self._build_classification_prompt(term)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    try:
                        parsed_result = json.loads(content)
                        return {
                            "normalized": parsed_result.get("normalized", term),
                            "category": parsed_result.get("category", "其他"),
                            "confidence": float(parsed_result.get("confidence", 0.5)),
                            "explanation": parsed_result.get("explanation", "")
                        }
                    except json.JSONDecodeError:
                        return {
                            "normalized": term,
                            "category": "其他",
                            "confidence": 0.4,
                            "explanation": "AI返回结果解析失败"
                        }
                else:
                    return {
                        "normalized": term,
                        "category": "其他",
                        "confidence": 0.0,
                        "explanation": f"API调用失败: {response.status_code}"
                    }
        except Exception as e:
            return {
                "normalized": term,
                "category": "其他",
                "confidence": 0.0,
                "explanation": f"分类失败: {str(e)}"
            }
    
    async def classify_terms_batch(self, terms: List[str]) -> List[Dict]:
        """
        批量分类术语 - 使用单次API调用
        
        Args:
            terms: 需要分类的术语列表
            
        Returns:
            分类结果列表
        """
        if not terms:
            return []
        
        # 构建批量分类提示词
        standard_terms_list = "\n".join([f"- {name} ({category})" for name, category in self.standard_terms.items()])
        
        terms_list = "\n".join([f"{i+1}. {term}" for i, term in enumerate(terms)])
        
        prompt = f"""你是一个专业的医学术语分类助手。请将给定的医学术语分类到最接近的标准术语中。

标准术语列表：
{standard_terms_list}

需要分类的术语：
{terms_list}

请分析每个术语的语义，并返回JSON格式的分类结果，格式如下：
{{
  "results": [
    {{
      "original": "原始术语",
      "normalized": "最匹配的标准术语名称",
      "category": "该术语所属的医学类别",
      "confidence": 匹配置信度（0-1之间的浮点数）,
      "explanation": "简要说明分类理由"
    }}
  ]
}}

如果术语与任何标准术语都不相关，请将normalized设为原术语，category设为"其他"，confidence设为0.3。

只返回JSON，不要包含其他内容。"""
        
        if not self.api_key:
            return [
                {
                    "normalized": term,
                    "category": "其他",
                    "confidence": 0.0,
                    "explanation": "未配置API密钥"
                }
                for term in terms
            ]
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    try:
                        parsed_result = json.loads(content)
                        return parsed_result.get("results", [])
                    except json.JSONDecodeError:
                        return [
                            {
                                "normalized": term,
                                "category": "其他",
                                "confidence": 0.4,
                                "explanation": "AI返回结果解析失败"
                            }
                            for term in terms
                        ]
                else:
                    return [
                        {
                            "normalized": term,
                            "category": "其他",
                            "confidence": 0.0,
                            "explanation": f"API调用失败: {response.status_code}"
                        }
                        for term in terms
                    ]
        except Exception as e:
            return [
                {
                    "normalized": term,
                    "category": "其他",
                    "confidence": 0.0,
                    "explanation": f"分类失败: {str(e)}"
                }
                for term in terms
            ]


class AISemanticService:
    """AI语义分类服务"""
    
    def __init__(self):
        self.provider = settings.AI_SERVICE_PROVIDER
        self.classifier = self._get_classifier()
    
    def _get_classifier(self) -> AISemanticClassifier:
        """
        根据配置获取分类器实例
        
        Returns:
            分类器实例
        """
        if self.provider == "aliyun":
            return AliyunClassifier()
        elif self.provider == "zhipu":
            return ZhipuClassifier()
        else:
            return AliyunClassifier()
    
    async def classify_term(self, term: str, threshold: float = None) -> Dict:
        """
        对术语进行语义分类
        
        Args:
            term: 需要分类的术语
            threshold: 置信度阈值，低于此值时返回原术语
            
        Returns:
            分类结果字典
        """
        if threshold is None:
            threshold = settings.AI_NORMALIZATION_THRESHOLD
        
        result = await self.classifier.classify_term(term)
        
        if result["confidence"] < threshold:
            result["normalized"] = term
            result["explanation"] = f"置信度低于阈值({threshold})，使用原术语"
        
        return result
    
    async def classify_terms_batch(self, terms: List[str], threshold: float = None) -> List[Dict]:
        """
        批量分类术语
        
        Args:
            terms: 需要分类的术语列表
            threshold: 置信度阈值
            
        Returns:
            分类结果列表
        """
        results = await self.classifier.classify_terms_batch(terms)
        
        if threshold is None:
            threshold = settings.AI_NORMALIZATION_THRESHOLD
        
        for result in results:
            if result["confidence"] < threshold:
                result["normalized"] = result.get("original", "")
                result["explanation"] = f"置信度低于阈值({threshold})，使用原术语"
        
        return results
    
    async def parse_report_text(self, text: str, report_type: str) -> Dict:
        """
        解析检查单文本
        
        Args:
            text: 检查单文本内容
            report_type: 报告类型 (lab/pathology)
            
        Returns:
            解析结果字典
        """
        return await self.classifier.parse_report_text(text, report_type)


# 创建全局服务实例
ai_semantic_service = AISemanticService()


async def classify_term_with_ai(term: str, threshold: float = None) -> Dict:
    """
    使用AI对术语进行语义分类
    
    Args:
        term: 需要分类的术语
        threshold: 置信度阈值
        
    Returns:
        分类结果字典
    """
    return await ai_semantic_service.classify_term(term, threshold)


async def classify_terms_batch_with_ai(terms: List[str], threshold: float = None) -> List[Dict]:
    """
    使用AI批量分类术语
    
    Args:
        terms: 需要分类的术语列表
        threshold: 置信度阈值
        
    Returns:
        分类结果列表
    """
    return await ai_semantic_service.classify_terms_batch(terms, threshold)


async def parse_report_with_ai(text: str, report_type: str) -> Dict:
    """
    使用AI解析检查单文本
    
    Args:
        text: 检查单文本内容
        report_type: 报告类型 (lab/pathology)
        
    Returns:
        解析结果字典
    """
    return await ai_semantic_service.parse_report_text(text, report_type)