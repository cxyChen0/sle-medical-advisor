from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str


class NormalizeRequest(BaseModel):
    """表单名称归一化请求模型"""
    terms: List[str] = Field(..., description="需要归一化的医学术语列表")


class NormalizedTerm(BaseModel):
    """归一化术语模型"""
    original: str = Field(..., description="原始术语")
    normalized: str = Field(..., description="归一化后的术语")
    confidence: float = Field(..., description="归一化的置信度")


class NormalizeResponse(BaseModel):
    """表单名称归一化响应模型"""
    normalized_terms: List[NormalizedTerm]


class Indicator(BaseModel):
    """检查指标模型"""
    name: str = Field(..., description="指标名称")
    value: str = Field(..., description="检测值")
    unit: Optional[str] = Field(None, description="单位")
    reference_range: Optional[str] = Field(None, description="参考范围")
    is_abnormal: Optional[bool] = Field(None, description="是否异常")
    normalized_name: Optional[str] = Field(None, description="归一化后的指标名称")
    normalization_confidence: Optional[float] = Field(None, description="归一化的置信度")


class ParseReportRequest(BaseModel):
    """检查单解析请求模型"""
    report_type: str = Field(..., description="报告类型 (pathology/lab)")


class ParseReportResponse(BaseModel):
    """检查单解析响应模型"""
    patient_id: Optional[str] = Field(None, description="患者ID")
    report_date: Optional[str] = Field(None, description="检查日期")
    report_type: str = Field(..., description="报告类型")
    indicators: List[Indicator] = Field(..., description="指标列表")
    normalization_results: Optional[List[NormalizedTerm]] = Field(None, description="归一化结果列表")


class MedicalHistoryItem(BaseModel):
    """病史记录项模型"""
    date: str = Field(..., description="日期")
    diagnosis: Optional[str] = Field(None, description="诊断")
    symptoms: Optional[List[str]] = Field(None, description="症状列表")
    lab_results: Optional[Dict[str, Any]] = Field(None, description="实验室结果")
    medications: Optional[List[str]] = Field(None, description="用药列表")


class MedicalHistoryResponse(BaseModel):
    """患者病史响应模型"""
    patient_id: str = Field(..., description="患者ID")
    medical_history: List[MedicalHistoryItem] = Field(..., description="病史记录列表")
