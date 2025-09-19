from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from ..models.store_application import StoreApplication
from ..models.store import Store
from ..models.user import User
from ..schemas.store_application import (
    StoreApplicationCreate, StoreApplicationUpdate, StoreApplicationResponse,
    StoreApplicationListResponse, StoreApplicationReview, StoreTypeInfo, StoreTypesResponse
)
from ..schemas.store import StoreCreate
from .notification_service import NotificationService
import re
import logging

logger = logging.getLogger(__name__)

class StoreApplicationService:
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    # 店铺类型配置
    STORE_TYPES = {
        '个人店': {
            'deposit': Decimal('600.00'), 
            'description': '根据《电子商务法》相关规定,个人小额交易,可凭身份证开店。年交易额在10万以下,后续可升级为个体工商户或企业。',
            'auto_approve': True,  # 个人店支持自动审批
            'required_docs': ['id_front_image', 'id_back_image']
        },
        '个体商家': {
            'deposit': Decimal('1000.00'), 
            'description': '提供个体工商户营业执照,身份证。',
            'auto_approve': False,
            'required_docs': ['id_front_image', 'id_back_image', 'business_license_image']
        },
        '企业店': {
            'deposit': Decimal('5000.00'), 
            'description': '须提供企业营业执照,法人身份证。',
            'auto_approve': False,
            'required_docs': ['id_front_image', 'id_back_image', 'business_license_image']
        },
        '旗舰店': {
            'deposit': Decimal('10000.00'), 
            'description': '提供个体工商户营业执照,身份证。',
            'auto_approve': False,
            'required_docs': ['id_front_image', 'id_back_image', 'business_license_image']
        }
    }
    
    async def get_store_types(self) -> StoreTypesResponse:
        """获取店铺类型列表"""
        types = []
        for type_name, config in self.STORE_TYPES.items():
            types.append(StoreTypeInfo(
                type_name=type_name,
                deposit_amount=config['deposit'],
                description=config['description']
            ))
        return StoreTypesResponse(types=types)
    
    async def create_application(self, db: Session, application_data: StoreApplicationCreate, user_id: int) -> StoreApplicationResponse:
        """创建店铺申请"""
        # 检查用户是否已有店铺
        existing_store = db.query(Store).filter(Store.owner_id == user_id).first()
        if existing_store:
            raise ValueError("用户已经拥有店铺")
        
        # 检查是否已有待审核的申请
        existing_application = db.query(StoreApplication).filter(
            and_(
                StoreApplication.user_id == user_id,
                StoreApplication.status.in_([0, 1])  # 待审核或已通过
            )
        ).first()
        if existing_application:
            if existing_application.status == 0:
                raise ValueError("您已有待审核的开店申请，请耐心等待")
            elif existing_application.status == 1:
                raise ValueError("您的开店申请已通过，请完成后续流程")
        
        # 验证申请数据
        validation_result = await self._validate_application_data(application_data)
        if not validation_result["is_valid"]:
            raise ValueError(f"申请数据验证失败: {', '.join(validation_result['errors'])}")
        
        # 计算押金
        store_config = self.STORE_TYPES.get(application_data.store_type, {})
        deposit_amount = store_config.get('deposit', Decimal('0.00'))
        
        # 创建申请记录
        application = StoreApplication(
            user_id=user_id,
            store_name=application_data.store_name,
            store_description=application_data.store_description,
            store_type=application_data.store_type,
            consignee_name=application_data.consignee_name,
            consignee_phone=application_data.consignee_phone,
            return_region=application_data.return_region,
            return_address=application_data.return_address,
            real_name=application_data.real_name,
            id_number=application_data.id_number,
            id_start_date=application_data.id_start_date,
            id_end_date=application_data.id_end_date,
            id_front_image=application_data.id_front_image,
            id_back_image=application_data.id_back_image,
            business_license_image=application_data.business_license_image,
            deposit_amount=deposit_amount
        )
        
        db.add(application)
        db.flush()  # 获取ID但不提交
        
        # 检查是否可以自动审批
        auto_approved = False
        if store_config.get('auto_approve', False):
            try:
                auto_approval_result = await self._auto_approve_application(db, application)
                if auto_approval_result["approved"]:
                    application.status = 1  # 自动通过
                    application.reviewed_at = datetime.now()
                    auto_approved = True
                    logger.info(f"申请 {application.id} 自动审批通过")
            except Exception as e:
                logger.error(f"自动审批失败: {e}")
                # 自动审批失败不影响申请创建，保持待审核状态
        
        db.commit()
        db.refresh(application)
        
        # 发送通知
        await self._send_application_notifications(db, application, auto_approved)
        
        return self._to_response(application)
    
    async def get_application_by_user(self, db: Session, user_id: int) -> Optional[StoreApplicationResponse]:
        """获取用户的店铺申请"""
        application = db.query(StoreApplication).filter(
            StoreApplication.user_id == user_id
        ).order_by(desc(StoreApplication.created_at)).first()
        
        if not application:
            return None
        
        return self._to_response(application)
    
    async def get_application_by_id(self, db: Session, application_id: int) -> Optional[StoreApplicationResponse]:
        """通过ID获取店铺申请"""
        application = db.query(StoreApplication).filter(
            StoreApplication.id == application_id
        ).first()
        
        if not application:
            return None
        
        return self._to_response(application)
    
    async def update_application(self, db: Session, application_id: int, application_data: StoreApplicationUpdate, user_id: int) -> StoreApplicationResponse:
        """更新店铺申请"""
        application = db.query(StoreApplication).filter(
            and_(
                StoreApplication.id == application_id,
                StoreApplication.user_id == user_id,
                StoreApplication.status == 0  # 只有待审核状态可以修改
            )
        ).first()
        
        if not application:
            raise ValueError("申请不存在或无法修改")
        
        # 更新字段
        for field, value in application_data.dict(exclude_unset=True).items():
            if hasattr(application, field):
                setattr(application, field, value)
        
        # 如果修改了店铺类型，重新计算押金
        if application_data.store_type:
            deposit_amount = self.STORE_TYPES.get(application_data.store_type, {}).get('deposit', Decimal('0.00'))
            application.deposit_amount = deposit_amount
        
        db.commit()
        db.refresh(application)
        
        return self._to_response(application)
    
    async def get_applications_list(
        self, 
        db: Session, 
        page: int = 1, 
        page_size: int = 20,
        status: Optional[int] = None,
        store_type: Optional[str] = None
    ) -> StoreApplicationListResponse:
        """获取店铺申请列表（管理员用）"""
        query = db.query(StoreApplication)
        
        if status is not None:
            query = query.filter(StoreApplication.status == status)
        if store_type:
            query = query.filter(StoreApplication.store_type == store_type)
        
        query = query.order_by(desc(StoreApplication.created_at))
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        applications = query.offset(offset).limit(page_size).all()
        
        # 转换为响应格式
        items = [self._to_response(app) for app in applications]
        
        return StoreApplicationListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def review_application(self, db: Session, application_id: int, review_data: StoreApplicationReview, reviewer_id: int) -> StoreApplicationResponse:
        """审核店铺申请"""
        application = db.query(StoreApplication).filter(
            and_(
                StoreApplication.id == application_id,
                StoreApplication.status == 0  # 只有待审核状态可以审核
            )
        ).first()
        
        if not application:
            raise ValueError("申请不存在或已处理")
        
        # 更新审核信息
        application.status = review_data.status
        application.reject_reason = review_data.reject_reason
        application.reviewer_id = reviewer_id
        application.reviewed_at = datetime.now()
        
        db.commit()
        db.refresh(application)
        
        return self._to_response(application)
    
    async def create_store_from_application(self, db: Session, application_id: int) -> Dict[str, Any]:
        """从申请创建店铺（支付完成后）"""
        application = db.query(StoreApplication).filter(
            and_(
                StoreApplication.id == application_id,
                StoreApplication.status == 1,  # 审核通过
                StoreApplication.payment_status == 1  # 已支付
            )
        ).first()
        
        if not application:
            raise ValueError("申请不存在、未通过审核或未支付费用")
        
        # 检查是否已创建店铺
        existing_store = db.query(Store).filter(Store.owner_id == application.user_id).first()
        if existing_store:
            raise ValueError("用户已经拥有店铺")
        
        # 创建店铺
        store_data = StoreCreate(
            name=application.store_name,
            description=application.store_description,
            location=application.return_region,
            phone=application.consignee_phone,
            is_open=True
        )
        
        store = Store(
            owner_id=application.user_id,
            name=store_data.name,
            description=store_data.description,
            location=store_data.location,
            phone=store_data.phone,
            is_open=store_data.is_open,
            verified=True  # 通过申请审核的店铺直接认证
        )
        
        db.add(store)
        
        # 更新申请状态为已开店
        application.status = 3
        
        db.commit()
        db.refresh(store)
        
        return {
            "store_id": store.id,
            "message": "店铺创建成功"
        }
    
    async def mark_payment_completed(self, db: Session, application_id: int) -> StoreApplicationResponse:
        """标记支付完成"""
        application = db.query(StoreApplication).filter(
            and_(
                StoreApplication.id == application_id,
                StoreApplication.status == 1,  # 审核通过
                StoreApplication.payment_status == 0  # 未支付
            )
        ).first()
        
        if not application:
            raise ValueError("申请不存在、未通过审核或已支付")
        
        application.payment_status = 1
        application.paid_at = datetime.now()
        
        db.commit()
        db.refresh(application)
        
        return self._to_response(application)
    
    async def _validate_application_data(self, application_data: StoreApplicationCreate) -> Dict[str, Any]:
        """验证申请数据"""
        errors = []
        
        # 验证身份证号格式
        if not self._validate_id_number(application_data.id_number):
            errors.append("身份证号格式不正确")
        
        # 验证手机号格式
        if not self._validate_phone(application_data.consignee_phone):
            errors.append("手机号格式不正确")
        
        # 验证店铺类型
        if application_data.store_type not in self.STORE_TYPES:
            errors.append("不支持的店铺类型")
        
        # 验证必需文档
        store_config = self.STORE_TYPES.get(application_data.store_type, {})
        required_docs = store_config.get('required_docs', [])
        
        for doc_field in required_docs:
            doc_value = getattr(application_data, doc_field, None)
            if not doc_value:
                doc_name = {
                    'id_front_image': '身份证人像面',
                    'id_back_image': '身份证国徽面', 
                    'business_license_image': '营业执照'
                }.get(doc_field, doc_field)
                errors.append(f"缺少{doc_name}照片")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def _validate_id_number(self, id_number: str) -> bool:
        """验证身份证号格式"""
        if not id_number or len(id_number) != 18:
            return False
        
        # 简单的身份证号格式验证
        pattern = r'^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$'
        return bool(re.match(pattern, id_number))
    
    def _validate_phone(self, phone: str) -> bool:
        """验证手机号格式"""
        if not phone:
            return False
        
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    async def _auto_approve_application(self, db: Session, application: StoreApplication) -> Dict[str, Any]:
        """自动审批申请"""
        checks = []
        
        # 检查身份证有效期
        try:
            end_date = datetime.strptime(application.id_end_date, '%Y-%m-%d')
            if end_date > datetime.now():
                checks.append({"check": "id_validity", "passed": True})
            else:
                checks.append({"check": "id_validity", "passed": False, "reason": "身份证已过期"})
        except:
            checks.append({"check": "id_validity", "passed": False, "reason": "身份证有效期格式错误"})
        
        # 检查必需文档是否完整
        store_config = self.STORE_TYPES.get(application.store_type, {})
        required_docs = store_config.get('required_docs', [])
        
        docs_complete = True
        for doc_field in required_docs:
            if not getattr(application, doc_field, None):
                docs_complete = False
                break
        
        checks.append({"check": "documents_complete", "passed": docs_complete})
        
        # 检查用户信誉（简化版）
        user = db.query(User).filter(User.id == application.user_id).first()
        credit_score = 100  # 默认信誉分
        if user and hasattr(user, 'credit_score'):
            credit_score = user.credit_score
        
        checks.append({"check": "credit_score", "passed": credit_score >= 80, "score": credit_score})
        
        # 判断是否自动通过
        all_passed = all(check.get("passed", False) for check in checks)
        
        return {
            "approved": all_passed,
            "checks": checks,
            "message": "自动审批通过" if all_passed else "未通过自动审批条件"
        }
    
    async def _send_application_notifications(self, db: Session, application: StoreApplication, auto_approved: bool):
        """发送申请相关通知"""
        try:
            if auto_approved:
                await self.notification_service.send_store_auto_approved_notification(
                    db=db,
                    user_id=application.user_id,
                    store_name=application.store_name
                )
            else:
                await self.notification_service.send_store_application_submitted_notification(
                    db=db,
                    user_id=application.user_id,
                    store_name=application.store_name
                )
        except Exception as e:
            logger.error(f"发送申请通知失败: {e}")
    
    async def auto_process_applications(self, db: Session) -> Dict[str, Any]:
        """批量自动处理申请（定时任务）"""
        # 查找符合自动审批条件的申请
        pending_applications = db.query(StoreApplication).filter(
            StoreApplication.status == 0  # 待审核
        ).all()
        
        processed_count = 0
        approved_count = 0
        results = []
        
        for application in pending_applications:
            try:
                store_config = self.STORE_TYPES.get(application.store_type, {})
                if store_config.get('auto_approve', False):
                    auto_result = await self._auto_approve_application(db, application)
                    
                    if auto_result["approved"]:
                        application.status = 1
                        application.reviewed_at = datetime.now()
                        approved_count += 1
                        
                        # 发送通知
                        await self.notification_service.send_store_auto_approved_notification(
                            db=db,
                            user_id=application.user_id,
                            store_name=application.store_name
                        )
                    
                    processed_count += 1
                    results.append({
                        "application_id": application.id,
                        "user_id": application.user_id,
                        "store_name": application.store_name,
                        "approved": auto_result["approved"],
                        "checks": auto_result["checks"]
                    })
                    
            except Exception as e:
                logger.error(f"自动处理申请 {application.id} 失败: {e}")
                results.append({
                    "application_id": application.id,
                    "approved": False,
                    "error": str(e)
                })
        
        if processed_count > 0:
            db.commit()
        
        return {
            "success": True,
            "processed_count": processed_count,
            "approved_count": approved_count,
            "results": results
        }
    
    def _to_response(self, application: StoreApplication) -> StoreApplicationResponse:
        """转换为响应格式"""
        return StoreApplicationResponse(
            id=application.id,
            user_id=application.user_id,
            store_name=application.store_name,
            store_description=application.store_description,
            store_type=application.store_type,
            consignee_name=application.consignee_name,
            consignee_phone=application.consignee_phone,
            return_region=application.return_region,
            return_address=application.return_address,
            real_name=application.real_name,
            id_number=application.id_number,
            id_start_date=application.id_start_date,
            id_end_date=application.id_end_date,
            id_front_image=application.id_front_image,
            id_back_image=application.id_back_image,
            business_license_image=application.business_license_image,
            status=application.status,
            reject_reason=application.reject_reason,
            reviewer_id=application.reviewer_id,
            reviewed_at=application.reviewed_at,
            deposit_amount=application.deposit_amount,
            annual_fee=application.annual_fee,
            payment_status=application.payment_status,
            paid_at=application.paid_at,
            created_at=application.created_at,
            updated_at=application.updated_at
        )
