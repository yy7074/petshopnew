from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
import random
import time
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.sms_code import SMSCode
import logging

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.client = self._create_client()
    
    def _create_client(self) -> Dysmsapi20170525Client:
        """创建阿里云短信客户端"""
        config = open_api_models.Config(
            access_key_id=settings.SMS_ACCESS_KEY,
            access_key_secret=settings.SMS_SECRET_KEY,
            endpoint=f"dysmsapi.aliyuncs.com"
        )
        return Dysmsapi20170525Client(config)
    
    async def send_verification_code(self, phone: str, db: Session) -> dict:
        """发送验证码短信"""
        try:
            # 生成6位数字验证码
            code = str(random.randint(100000, 999999))
            
            # 构建请求参数
            send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
                phone_numbers=phone,
                sign_name=settings.SMS_SIGN_NAME,
                template_code=settings.SMS_TEMPLATE_ID,
                template_param=f'{{"code":"{code}"}}'
            )
            
            runtime = util_models.RuntimeOptions()
            
            # 发送短信
            response = await self.client.send_sms_with_options_async(
                send_sms_request, runtime
            )
            
            # 存储验证码到数据库
            await self._store_verification_code(phone, code, db)
            
            return {
                "success": True,
                "message": "验证码发送成功",
                "code": code,  # 开发环境返回验证码，生产环境应该删除
                "biz_id": response.body.biz_id
            }
            
        except Exception as e:
            logger.error(f"发送短信验证码失败: {str(e)}")
            return {
                "success": False,
                "message": f"发送失败: {str(e)}"
            }
    
    async def verify_code(self, phone: str, code: str, db: Session) -> bool:
        """验证验证码"""
        try:
            # 查找有效的验证码
            sms_code = db.query(SMSCode).filter(
                SMSCode.phone == phone,
                SMSCode.code == code,
                SMSCode.is_used == False,
                SMSCode.expires_at > datetime.utcnow()
            ).first()
            
            if not sms_code:
                return False
            
            # 标记为已使用
            sms_code.is_used = True
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"验证短信验证码失败: {str(e)}")
            return False
    
    async def _store_verification_code(self, phone: str, code: str, db: Session):
        """存储验证码到数据库"""
        try:
            # 先删除该手机号的旧验证码
            db.query(SMSCode).filter(SMSCode.phone == phone).delete()
            
            # 创建新的验证码记录
            expires_at = datetime.utcnow() + timedelta(minutes=5)  # 5分钟后过期
            sms_code = SMSCode(
                phone=phone,
                code=code,
                expires_at=expires_at
            )
            
            db.add(sms_code)
            db.commit()
            
        except Exception as e:
            logger.error(f"存储验证码失败: {str(e)}")
            db.rollback()
            raise

# 创建全局实例
sms_service = SMSService()
