from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
from app.api import auth, products, bids, orders, auctions, events, home  # search, chat

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(products.router, prefix="/api/v1/products", tags=["商品"])
app.include_router(bids.router, prefix="/api/v1/bids", tags=["竞拍"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["订单"])
app.include_router(auctions.router, prefix="/api/v1/auctions", tags=["拍卖"])
app.include_router(events.router, prefix="/api/v1/events", tags=["专场活动"])
app.include_router(home.router, prefix="/api/v1/home", tags=["首页"])
# app.include_router(search.router, prefix="/api/v1/search", tags=["搜索"])
# app.include_router(chat.router, prefix="/api/v1/chat", tags=["聊天"])

# 根路径
@app.get("/")
async def root():
    return {"message": "宠物拍卖API服务", "version": settings.VERSION}

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务运行正常"}

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=settings.DEBUG,
        log_level="info"
    )
