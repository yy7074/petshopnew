"""
简化的配置文件
避免pydantic复杂的环境变量解析问题
"""
import os
from typing import List
from .env_config import env_config

class SimpleSettings:
    # 应用配置
    APP_NAME: str = env_config.APP_NAME
    DEBUG: bool = env_config.DEBUG
    VERSION: str = env_config.VERSION
    
    # 数据库配置
    DATABASE_URL: str = env_config.DATABASE_URL
    
    # Redis配置
    REDIS_URL: str = env_config.REDIS_URL
    
    # JWT配置
    SECRET_KEY: str = env_config.SECRET_KEY
    ALGORITHM: str = env_config.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = env_config.ACCESS_TOKEN_EXPIRE_MINUTES
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 文件上传配置
    UPLOAD_DIR: str = env_config.UPLOAD_DIR
    MAX_FILE_SIZE: int = env_config.MAX_FILE_SIZE
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = env_config.DEFAULT_PAGE_SIZE
    MAX_PAGE_SIZE: int = env_config.MAX_PAGE_SIZE
    
    # 支付配置
    ALIPAY_APP_ID: str = env_config.ALIPAY_APP_ID
    ALIPAY_PRIVATE_KEY: str = env_config.ALIPAY_PRIVATE_KEY
    ALIPAY_PUBLIC_KEY: str = env_config.ALIPAY_PUBLIC_KEY
    
    WECHAT_APP_ID: str = env_config.WECHAT_APP_ID
    WECHAT_MCH_ID: str = env_config.WECHAT_MCH_ID
    WECHAT_API_KEY: str = env_config.WECHAT_API_KEY
    
    # 短信配置
    SMS_ACCESS_KEY: str = env_config.SMS_ACCESS_KEY
    SMS_SECRET_KEY: str = env_config.SMS_SECRET_KEY
    SMS_SIGN_NAME: str = env_config.SMS_SIGN_NAME
    SMS_TEMPLATE_ID: str = env_config.SMS_TEMPLATE_ID
    SMS_REGION: str = env_config.SMS_REGION
    
    # 推送配置
    JPUSH_APP_KEY: str = env_config.JPUSH_APP_KEY
    JPUSH_MASTER_SECRET: str = env_config.JPUSH_MASTER_SECRET

settings = SimpleSettings()