"""
AI Agent核心类
用于整合和执行各种技能模块
"""

from typing import List, Dict, Any, Optional
from app.agent.tools import ToolRegistry


class AIAgent:
    """
    AI Agent核心类
    用于规划和执行任务，整合各种技能模块
    """
    
    def __init__(self):
        """
        初始化AI Agent
        """
        self.tool_registry = ToolRegistry()
    
    async def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行AI Agent完成任务
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            任务执行结果
        """
        # 1. 分析任务，确定需要使用的工具
        plan = await self._plan_task(task, context)
        
        # 2. 执行任务计划
        result = await self._execute_plan(plan, context)
        
        # 3. 总结执行结果
        summary = await self._summarize_result(result, task)
        
        return {
            "plan": plan,
            "result": result,
            "summary": summary
        }
    
    async def _plan_task(self, task: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        规划任务执行步骤
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            任务执行计划
        """
        # 获取可用工具列表
        tools = self.tool_registry.get_available_tools()
        
        # 基于任务和工具列表生成执行计划
        # 这里使用简单的规则来生成计划，实际项目中可以使用AI模型来生成更智能的计划
        plan = []
        
        # 检查任务类型并生成相应的计划
        task_lower = task.lower()
        
        if "解析" in task_lower or "检查单" in task_lower:
            plan.append({
                "tool": "parse_report",
                "args": {
                    "report_type": "lab"
                },
                "description": "解析检查单内容"
            })
        
        if "历史" in task_lower or "病史" in task_lower:
            plan.append({
                "tool": "get_medical_history",
                "args": {},
                "description": "获取患者病史记录"
            })
        
        if "归一化" in task_lower or "标准化" in task_lower:
            plan.append({
                "tool": "normalize_terms",
                "args": {},
                "description": "归一化医学术语"
            })
        
        # 如果没有匹配的工具，返回空计划
        if not plan:
            plan.append({
                "tool": "none",
                "args": {},
                "description": "无法确定执行步骤"
            })
        
        return plan
    
    async def _execute_plan(self, plan: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行任务计划
        
        Args:
            plan: 任务执行计划
            context: 上下文信息
            
        Returns:
            执行结果
        """
        results = {}
        
        for step in plan:
            tool_name = step.get("tool")
            tool_args = step.get("args", {})
            
            if not tool_name or tool_name == "none":
                continue
            
            # 调用工具执行步骤
            try:
                # 合并上下文信息到工具参数
                if context:
                    tool_args = {**tool_args, **context}
                
                tool_result = await self.tool_registry.call_tool(
                    tool_name=tool_name,
                    args=tool_args
                )
                results[tool_name] = tool_result
            except Exception as e:
                results[tool_name] = {"error": str(e)}
        
        return results
    
    async def _summarize_result(self, result: Dict[str, Any], task: str) -> str:
        """
        总结执行结果
        
        Args:
            result: 执行结果
            task: 任务描述
            
        Returns:
            总结文本
        """
        # 生成简单的总结
        summary = f"任务 '{task}' 执行完成\n"
        
        for tool_name, tool_result in result.items():
            if "error" in tool_result:
                summary += f"- {tool_name}: 执行失败 - {tool_result['error']}\n"
            else:
                summary += f"- {tool_name}: 执行成功\n"
        
        return summary
