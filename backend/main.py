from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth

# 导入所有模型以确保数据库表被创建
from app.models import user, product, order, wallet, deposit, store, store_application, message, local_service, lottery, follow

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

# 后台管理静态文件服务
import os
admin_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin")
if os.path.exists(admin_path):
    app.mount("/admin", StaticFiles(directory=admin_path, html=True), name="admin")

# 注册路由
from app.api import auth, products, bids, orders, auctions, events, home, wallet, deposit, stores, store_applications, chat, messages, users, admin, local_services, ai_recognition, lottery, checkin, follow  # search

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(products.router, prefix="/api/v1/products", tags=["商品"])
app.include_router(bids.router, prefix="/api/v1/bids", tags=["竞拍"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["订单"])
app.include_router(auctions.router, prefix="/api/v1/auctions", tags=["拍卖"])
app.include_router(events.router, prefix="/api/v1/events", tags=["专场活动"])
app.include_router(home.router, prefix="/api/v1/home", tags=["首页"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["钱包"])
app.include_router(deposit.router, prefix="/api/v1/deposits", tags=["保证金"])
app.include_router(stores.router, prefix="/api/v1/stores", tags=["店铺"])
app.include_router(store_applications.router, prefix="/api/v1/store-applications", tags=["店铺申请"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["聊天"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["消息"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
# 兼容性路由：为Flutter应用提供 /api/v1/user 路径
app.include_router(users.router, prefix="/api/v1/user", tags=["用户-兼容"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["后台管理"])
app.include_router(local_services.router, prefix="/api/v1/local-services", tags=["同城服务"])
app.include_router(ai_recognition.router, prefix="/api/v1", tags=["AI识别"])
app.include_router(lottery.router, prefix="/api/v1", tags=["抽奖"])
app.include_router(checkin.router, prefix="/api/v1/checkin", tags=["签到"])
app.include_router(follow.router, prefix="/api/v1", tags=["关注粉丝"])
# app.include_router(search.router, prefix="/api/v1/search", tags=["搜索"])

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
