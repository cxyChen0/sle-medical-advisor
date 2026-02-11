"""
工具注册表
用于管理和调用各种AI Agent工具
"""

from typing import Dict, List, Any, Optional
from app.services.report_parser import parse_report
from app.services.history_service import get_medical_history
from app.services.normalization_service import normalize_medical_terms
from fastapi import UploadFile


class ToolRegistry:
    """
    工具注册表
    用于管理和调用各种工具
    """
    
    def __init__(self):
        """
        初始化工具注册表
        """
        self.tools = {
            "parse_report": {
                "function": self._parse_report,
                "description": "解析医疗检查单",
                "parameters": {
                    "file": "UploadFile",
                    "report_type": "str"
                }
            },
            "get_medical_history": {
                "function": self._get_medical_history,
                "description": "获取患者病史记录",
                "parameters": {
                    "patient_id": "str"
                }
            },
            "normalize_terms": {
                "function": self._normalize_terms,
                "description": "归一化医学术语",
                "parameters": {
                    "terms": "List[str]"
                }
            }
        }
    
    def get_available_tools(self) -> List[Dict]:
        """
        获取可用工具列表
        
        Returns:
            工具列表
        """
        available_tools = []
        for tool_name, tool_info in self.tools.items():
            available_tools.append({
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": tool_info["parameters"]
            })
        return available_tools
    
    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        调用指定工具
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            
        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            raise ValueError(f"工具不存在: {tool_name}")
        
        tool_info = self.tools[tool_name]
        tool_function = tool_info["function"]
        
        # 调用工具函数
        try:
            result = await tool_function(args)
            return result
        except Exception as e:
            raise Exception(f"工具执行失败: {str(e)}")
    
    async def _parse_report(self, args: Dict[str, Any]) -> Dict:
        """
        解析检查单工具
        
        Args:
            args: 工具参数
            
        Returns:
            解析结果
        """
        # 注意：实际使用时，file参数需要是UploadFile对象
        # 这里为了演示，返回模拟数据
        return {
            "patient_id": args.get("patient_id", "1"),
            "report_date": "2026-01-15",
            "report_type": args.get("report_type", "lab"),
            "indicators": [
                {
                    "name": "抗核抗体",
                    "value": "阳性",
                    "unit": "",
                    "reference_range": "阴性",
                    "is_abnormal": True
                },
                {
                    "name": "白细胞计数",
                    "value": "3.8",
                    "unit": "10^9/L",
                    "reference_range": "4.0-10.0 10^9/L",
                    "is_abnormal": True
                }
            ]
        }
    
    async def _get_medical_history(self, args: Dict[str, Any]) -> Dict:
        """
        获取病史记录工具
        
        Args:
            args: 工具参数
            
        Returns:
            病史记录
        """
        patient_id = args.get("patient_id", "1")
        return await get_medical_history(patient_id)
    
    async def _normalize_terms(self, args: Dict[str, Any]) -> List[Dict]:
        """
        归一化医学术语工具
        
        Args:
            args: 工具参数
            
        Returns:
            归一化结果
        """
        terms = args.get("terms", [])
        return await normalize_medical_terms(terms)
