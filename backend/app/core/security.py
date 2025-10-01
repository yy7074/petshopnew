from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from sqlalchemy.orm import Session
from app.core.config import settings

# Password encryption context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
optional_auth = HTTPBearer(auto_error=False)

def _truncate_password(password: str) -> str:
    """
    截断密码到72字节以符合bcrypt限制
    bcrypt只能处理最大72字节的密码
    """
    if not isinstance(password, str):
        return password
    
    password_bytes = password.encode('utf-8')
    if len(password_bytes) <= 72:
        return password
    
    # 截断到72字节，确保不会在多字节字符中间切断
    truncated = password_bytes[:72]
    # 尝试解码，如果失败则逐步减少长度直到成功
    for i in range(72, 68, -1):  # 最多回退4字节（UTF-8最多4字节字符）
        try:
            return truncated[:i].decode('utf-8')
        except UnicodeDecodeError:
            continue
    # 如果还是失败，返回原密码的前部分
    return password[:20]  # 安全回退

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        # 截断密码到bcrypt允许的最大长度
        truncated_password = _truncate_password(plain_password)
        return pwd_context.verify(truncated_password, hashed_password)
    except ValueError as e:
        # bcrypt相关错误
        if "password cannot be longer than 72 bytes" in str(e):
            print(f"⚠️ 密码过长，已自动截断: {len(plain_password.encode('utf-8'))} bytes")
            # 强制使用更短的密码重试
            return pwd_context.verify(plain_password[:20], hashed_password)
        print(f"❌ 密码验证错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知验证错误: {e}")
        return False

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    try:
        # 截断密码到bcrypt允许的最大长度
        truncated_password = _truncate_password(password)
        return pwd_context.hash(truncated_password)
    except Exception as e:
        print(f"❌ 密码哈希生成错误: {e}")
        # 如果失败，使用更短的密码
        return pwd_context.hash(password[:20])

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    from app.core.database import SessionLocal
    from app.models.user import User
    
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    finally:
        db.close()

def get_current_user_optional(token: Optional[str] = Depends(optional_auth)):
    """获取当前用户（可选）"""
    if not token:
        return None
    try:
        return get_current_user(token.credentials)
    except HTTPException:
        return None

def get_admin_user(current_user = Depends(get_current_user)):
    """获取管理员用户"""
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


