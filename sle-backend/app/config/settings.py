from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    # 应用配置
    APP_NAME: str = "SLE Medical Advisor Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://admin:password@localhost:3306/example_db"
    
    # API配置
    API_V1_STR: str = "/api/v1"
    
    # AI语义分类配置
    # 阿里云百炼配置
    ALIYUN_API_KEY: Optional[str] = None
    ALIYUN_MODEL: str = "qwen-turbo"
    ALIYUN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 智谱GLM配置
    ZHIPU_API_KEY: Optional[str] = None
    ZHIPU_MODEL: str = "glm-4-flash"
    ZHIPU_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    
    # AI服务选择: "aliyun" 或 "zhipu"
    AI_SERVICE_PROVIDER: str = "zhipu"
    
    # AI归一化阈值：当传统归一化置信度低于此值时启用AI
    # 设置为0.5表示启用AI归一化
    AI_NORMALIZATION_THRESHOLD: float = 0.5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()
