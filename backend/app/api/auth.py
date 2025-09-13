from datetime import timedelta
import time
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, verify_token, get_current_user
from app.models.user import User
from app.schemas.auth import (
    Token, UserLogin, UserRegister, 
    SendSMSRequest, VerifySMSRequest, SMSLoginRequest, SMSResponse
)
from app.schemas.user import UserResponse
from app.services.sms_service import sms_service

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查手机号是否已存在
    if db.query(User).filter(User.phone == user_data.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已注册"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        phone=user_data.phone,
        email=user_data.email,
        password_hash=hashed_password,
        nickname=user_data.nickname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    # 支持用户名或手机号登录
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.phone == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户已被禁用",
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # 更新最后登录时间
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.post("/logout")
async def logout():
    """用户登出"""
    # 在实际应用中，可以将token加入黑名单
    return {"message": "登出成功"}

# 短信验证码相关接口
@router.post("/send-sms", response_model=SMSResponse)
async def send_sms(request: SendSMSRequest, db: Session = Depends(get_db)):
    """发送短信验证码"""
    try:
        result = await sms_service.send_verification_code(request.phone, db)
        return SMSResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送短信失败: {str(e)}"
        )

@router.post("/verify-sms", response_model=SMSResponse)
async def verify_sms(request: VerifySMSRequest, db: Session = Depends(get_db)):
    """验证短信验证码"""
    try:
        is_valid = await sms_service.verify_code(request.phone, request.code, db)
        if is_valid:
            return SMSResponse(success=True, message="验证码正确")
        else:
            return SMSResponse(success=False, message="验证码错误或已过期")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证短信失败: {str(e)}"
        )

@router.post("/sms-login", response_model=Token)
async def sms_login(request: SMSLoginRequest, db: Session = Depends(get_db)):
    """短信验证码登录"""
    # 验证短信验证码
    is_valid = await sms_service.verify_code(request.phone, request.code, db)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # 查找用户，如果不存在则自动注册
    user = db.query(User).filter(User.phone == request.phone).first()
    
    if not user:
        # 自动注册新用户
        # 为短信登录用户生成一个随机密码（用户不会用到）
        random_password = f"sms_{request.phone}_{int(time.time())}"
        hashed_password = get_password_hash(random_password)
        
        user = User(
            username=request.phone,  # 使用手机号作为用户名
            phone=request.phone,
            password_hash=hashed_password,  # 设置密码哈希
            nickname=f"用户{request.phone[-4:]}",  # 使用手机号后4位作为昵称
            status=1
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户已被禁用"
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # 更新最后登录时间
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

