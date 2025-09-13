"""
环境变量配置文件
用于管理敏感信息和配置参数
"""
import os
from typing import List
from pathlib import Path

# 加载.env.local文件（如果存在）
def load_env_file():
    """加载环境变量文件"""
    env_files = ['.env.local', '.env']
    for env_file in env_files:
        env_path = Path(__file__).parent.parent.parent / env_file
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
            break

# 加载环境变量
load_env_file()

class EnvConfig:
    """环境变量配置类"""
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/petshop_auction")
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))
    
    # 阿里云短信配置
    SMS_ACCESS_KEY: str = os.getenv("SMS_ACCESS_KEY", "")
    SMS_SECRET_KEY: str = os.getenv("SMS_SECRET_KEY", "")
    SMS_SIGN_NAME: str = os.getenv("SMS_SIGN_NAME", "")
    SMS_TEMPLATE_ID: str = os.getenv("SMS_TEMPLATE_ID", "")
    SMS_REGION: str = os.getenv("SMS_REGION", "cn-hangzhou")
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # 应用配置
    APP_NAME: str = os.getenv("APP_NAME", "宠物拍卖API")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    VERSION: str = os.getenv("VERSION", "1.0.0")
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "*").split(",")
    
    # 文件上传配置
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "static/uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))
    ALLOWED_EXTENSIONS: List[str] = os.getenv("ALLOWED_EXTENSIONS", ".jpg,.jpeg,.png,.gif,.webp").split(",")
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))
    
    # 支付配置
    ALIPAY_APP_ID: str = os.getenv("ALIPAY_APP_ID", "")
    ALIPAY_PRIVATE_KEY: str = os.getenv("ALIPAY_PRIVATE_KEY", "")
    ALIPAY_PUBLIC_KEY: str = os.getenv("ALIPAY_PUBLIC_KEY", "")
    
    WECHAT_APP_ID: str = os.getenv("WECHAT_APP_ID", "")
    WECHAT_MCH_ID: str = os.getenv("WECHAT_MCH_ID", "")
    WECHAT_API_KEY: str = os.getenv("WECHAT_API_KEY", "")
    
    # 推送配置
    JPUSH_APP_KEY: str = os.getenv("JPUSH_APP_KEY", "")
    JPUSH_MASTER_SECRET: str = os.getenv("JPUSH_MASTER_SECRET", "")
    
    @classmethod
    def validate_required_configs(cls) -> List[str]:
        """验证必需的配置项"""
        missing_configs = []
        
        if not cls.SMS_ACCESS_KEY:
            missing_configs.append("SMS_ACCESS_KEY")
        if not cls.SMS_SECRET_KEY:
            missing_configs.append("SMS_SECRET_KEY")
        if not cls.SMS_SIGN_NAME:
            missing_configs.append("SMS_SIGN_NAME")
        if not cls.SMS_TEMPLATE_ID:
            missing_configs.append("SMS_TEMPLATE_ID")
            
        return missing_configs

# 创建全局配置实例
env_config = EnvConfig()
