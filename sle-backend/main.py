from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api import routes

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SLE医疗顾问后端API服务",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(routes.router)

# 根路径
@app.get("/")
async def root():
    return {
        "message": "Welcome to SLE Medical Advisor Backend",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
