from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from .user import UserResponse
import re

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    phone: str
    email: Optional[EmailStr] = None
    password: str
    nickname: Optional[str] = None

# 短信验证码相关模型
class SendSMSRequest(BaseModel):
    phone: str
    
    @validator('phone')
    def validate_phone(cls, v):
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v

class VerifySMSRequest(BaseModel):
    phone: str
    code: str
    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    @validator('code')
    def validate_code(cls, v):
        if not re.match(r'^\d{6}$', v):
            raise ValueError('验证码必须是6位数字')
        return v

class SMSLoginRequest(BaseModel):
    phone: str
    code: str
    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    @validator('code')
    def validate_code(cls, v):
        if not re.match(r'^\d{6}$', v):
            raise ValueError('验证码必须是6位数字')
        return v

class SMSResponse(BaseModel):
    success: bool
    message: str
    code: Optional[str] = None  # 开发环境返回验证码

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None


