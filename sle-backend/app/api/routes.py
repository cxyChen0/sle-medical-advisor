from fastapi import APIRouter, HTTPException, UploadFile, File
from app.api.schemas import (
    HealthCheckResponse,
    NormalizeRequest,
    NormalizeResponse,
    ParseReportRequest,
    ParseReportResponse,
    MedicalHistoryResponse
)
from app.services.normalization_service import normalize_medical_terms
from app.services.report_parser import parse_report
from app.services.history_service import get_medical_history

# 创建路由实例
router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """健康检查接口"""
    return HealthCheckResponse(status="healthy")


@router.post("/normalize", response_model=NormalizeResponse)
async def normalize_terms(request: NormalizeRequest):
    """表单名称归一化接口"""
    try:
        normalized_terms = await normalize_medical_terms(request.terms)
        return NormalizeResponse(normalized_terms=normalized_terms)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse-report", response_model=ParseReportResponse)
async def parse_medical_report(
    file: UploadFile = File(...),
    report_type: str = "lab"
):
    """检查单解析接口"""
    try:
        print(f"Received file: {file.filename}, type: {report_type}")
        result = await parse_report(file, report_type)
        print(f"Parse result: {result}")
        return ParseReportResponse(**result)
    except Exception as e:
        print(f"Error parsing report: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/medical-history/{patient_id}", response_model=MedicalHistoryResponse)
async def get_patient_history(patient_id: str):
    """获取患者病史接口"""
    try:
        history = await get_medical_history(patient_id)
        return MedicalHistoryResponse(**history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
