from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import base64
import logging
from decimal import Decimal

from ..models.user import User
from ..core.config import settings

logger = logging.getLogger(__name__)

class AIRecognitionService:
    
    # AI识别配置
    RECOGNITION_CONFIG = {
        "max_image_size": 10 * 1024 * 1024,  # 10MB
        "min_image_size": 10 * 1024,         # 10KB
        "supported_formats": ["jpg", "jpeg", "png", "webp"],
        "max_daily_recognitions": 50,        # 每日最大识别次数
        "confidence_threshold": 0.7,         # 置信度阈值
        "cache_duration_hours": 24,          # 缓存时长
    }
    
    # 宠物品种数据库
    PET_DATABASE = {
        "dog": {
            "breeds": {
                "golden_retriever": {
                    "name": "金毛寻回犬",
                    "characteristics": ["温顺", "聪明", "友善", "忠诚"],
                    "care_tips": ["需要大量运动", "定期梳毛", "注意饮食控制", "社交训练"],
                    "health_tips": ["预防髋关节发育不良", "定期心脏检查", "控制体重"],
                    "feeding_guide": ["高质量狗粮", "分餐喂养", "避免过度喂食"],
                    "price_range": {"min": 1500, "max": 8000},
                    "popularity": 0.9
                },
                "labrador": {
                    "name": "拉布拉多",
                    "characteristics": ["活泼", "友好", "易训练", "温和"],
                    "care_tips": ["充足运动", "游泳训练", "定期护理", "早期社交"],
                    "health_tips": ["预防肥胖", "关注眼部健康", "定期疫苗"],
                    "feeding_guide": ["控制食量", "优质蛋白", "定时喂养"],
                    "price_range": {"min": 1200, "max": 6000},
                    "popularity": 0.95
                },
                "husky": {
                    "name": "哈士奇",
                    "characteristics": ["独立", "活跃", "聪明", "顽皮"],
                    "care_tips": ["大量运动", "耐寒训练", "坚持训练", "安全围栏"],
                    "health_tips": ["预防白内障", "关注关节健康", "定期体检"],
                    "feeding_guide": ["高能量食物", "分餐制", "充足水分"],
                    "price_range": {"min": 2000, "max": 10000},
                    "popularity": 0.8
                }
            }
        },
        "cat": {
            "breeds": {
                "british_shorthair": {
                    "name": "英国短毛猫",
                    "characteristics": ["温和", "独立", "安静", "友善"],
                    "care_tips": ["定期梳毛", "清洁耳朵", "指甲修剪", "环境丰富"],
                    "health_tips": ["预防肥厚性心肌病", "定期口腔护理", "控制体重"],
                    "feeding_guide": ["高蛋白猫粮", "定时定量", "新鲜水源"],
                    "price_range": {"min": 2000, "max": 8000},
                    "popularity": 0.85
                },
                "ragdoll": {
                    "name": "布偶猫",
                    "characteristics": ["温顺", "粘人", "美丽", "安静"],
                    "care_tips": ["每日梳毛", "室内饲养", "温柔对待", "定期洗澡"],
                    "health_tips": ["预防多囊肾", "心脏健康检查", "关注尿路健康"],
                    "feeding_guide": ["优质猫粮", "避免过量", "营养均衡"],
                    "price_range": {"min": 3000, "max": 15000},
                    "popularity": 0.9
                }
            }
        },
        "bird": {
            "breeds": {
                "budgerigar": {
                    "name": "虎皮鹦鹉",
                    "characteristics": ["活泼", "聪明", "善模仿", "社交"],
                    "care_tips": ["宽敞鸟笼", "定期清洁", "社交互动", "飞行空间"],
                    "health_tips": ["预防呼吸道疾病", "注意营养平衡", "定期体检"],
                    "feeding_guide": ["专用鸟粮", "新鲜蔬果", "清洁饮水"],
                    "price_range": {"min": 50, "max": 200},
                    "popularity": 0.7
                }
            }
        }
    }
    
    async def recognize_pet_image(
        self,
        db: Session,
        user_id: int,
        image_data: str,
        image_format: str
    ) -> Dict[str, Any]:
        """识别宠物图片"""
        
        # 检查用户识别次数限制
        daily_check = await self._check_daily_limit(db, user_id)
        if not daily_check["allowed"]:
            raise ValueError(daily_check["message"])
        
        # 验证图片格式和大小
        validation_result = await self._validate_image(image_data, image_format)
        if not validation_result["valid"]:
            raise ValueError(validation_result["message"])
        
        try:
            # 调用AI识别接口（这里模拟）
            recognition_result = await self._perform_ai_recognition(image_data)
            
            # 增强识别结果
            enhanced_result = await self._enhance_recognition_result(recognition_result)
            
            # 记录识别历史
            await self._save_recognition_record(db, user_id, enhanced_result, image_format)
            
            return {
                "success": True,
                "data": enhanced_result,
                "message": "识别成功"
            }
            
        except Exception as e:
            logger.error(f"AI识别失败: {e}")
            return {
                "success": False,
                "message": f"识别失败: {str(e)}",
                "data": None
            }
    
    async def _check_daily_limit(self, db: Session, user_id: int) -> Dict[str, Any]:
        """检查每日识别次数限制"""
        from ..models.ai_recognition import AIRecognitionRecord
        
        today = datetime.now().date()
        daily_count = db.query(func.count(AIRecognitionRecord.id)).filter(
            and_(
                AIRecognitionRecord.user_id == user_id,
                func.date(AIRecognitionRecord.created_at) == today
            )
        ).scalar() or 0
        
        max_daily = self.RECOGNITION_CONFIG["max_daily_recognitions"]
        
        if daily_count >= max_daily:
            return {
                "allowed": False,
                "message": f"今日识别次数已达上限({max_daily}次)，请明天再试",
                "current_count": daily_count
            }
        
        return {
            "allowed": True,
            "message": "识别次数检查通过",
            "current_count": daily_count,
            "remaining": max_daily - daily_count
        }
    
    async def _validate_image(self, image_data: str, image_format: str) -> Dict[str, Any]:
        """验证图片格式和大小"""
        
        # 检查格式
        if image_format.lower() not in self.RECOGNITION_CONFIG["supported_formats"]:
            return {
                "valid": False,
                "message": f"不支持的图片格式，支持格式: {', '.join(self.RECOGNITION_CONFIG['supported_formats'])}"
            }
        
        try:
            # 解码base64检查大小
            image_bytes = base64.b64decode(image_data)
            file_size = len(image_bytes)
            
            if file_size < self.RECOGNITION_CONFIG["min_image_size"]:
                return {
                    "valid": False,
                    "message": "图片文件过小，可能影响识别准确度"
                }
            
            if file_size > self.RECOGNITION_CONFIG["max_image_size"]:
                return {
                    "valid": False,
                    "message": "图片文件过大，请压缩后重试"
                }
            
            return {
                "valid": True,
                "message": "图片验证通过",
                "file_size": file_size
            }
            
        except Exception as e:
            return {
                "valid": False,
                "message": f"图片数据格式错误: {str(e)}"
            }
    
    async def _perform_ai_recognition(self, image_data: str) -> Dict[str, Any]:
        """执行AI识别（模拟实现）"""
        
        # 模拟AI识别延迟
        import asyncio
        import random
        await asyncio.sleep(random.uniform(1.0, 3.0))
        
        # 模拟识别结果
        pet_types = list(self.PET_DATABASE.keys())
        selected_type = random.choice(pet_types)
        
        breeds = list(self.PET_DATABASE[selected_type]["breeds"].keys())
        selected_breed = random.choice(breeds)
        
        # 生成置信度
        confidence = random.uniform(0.6, 0.98)
        
        return {
            "pet_type": selected_type,
            "breed": selected_breed,
            "confidence": confidence,
            "raw_predictions": [
                {"breed": selected_breed, "confidence": confidence},
                {"breed": random.choice(breeds), "confidence": confidence - 0.1},
                {"breed": random.choice(breeds), "confidence": confidence - 0.2}
            ]
        }
    
    async def _enhance_recognition_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """增强识别结果，添加详细信息"""
        
        pet_type = raw_result["pet_type"]
        breed_key = raw_result["breed"]
        confidence = raw_result["confidence"]
        
        # 获取品种详细信息
        breed_info = self.PET_DATABASE.get(pet_type, {}).get("breeds", {}).get(breed_key, {})
        
        if not breed_info:
            # 如果没有找到品种信息，返回基础结果
            return {
                "pet_type": self._translate_pet_type(pet_type),
                "breed": "未知品种",
                "confidence": confidence,
                "characteristics": [],
                "care_advice": [],
                "health_tips": [],
                "feeding_guide": [],
                "estimated_value": None
            }
        
        # 构建完整结果
        result = {
            "pet_type": self._translate_pet_type(pet_type),
            "breed": breed_info["name"],
            "confidence": confidence,
            "characteristics": breed_info.get("characteristics", []),
            "care_advice": breed_info.get("care_tips", []),
            "health_tips": breed_info.get("health_tips", []),
            "feeding_guide": breed_info.get("feeding_guide", []),
            "estimated_value": self._calculate_estimated_value(breed_info),
            "popularity_score": breed_info.get("popularity", 0.0),
            "alternative_breeds": self._get_alternative_breeds(pet_type, breed_key)
        }
        
        return result
    
    def _translate_pet_type(self, pet_type: str) -> str:
        """翻译宠物类型"""
        translations = {
            "dog": "狗",
            "cat": "猫", 
            "bird": "鸟",
            "fish": "鱼",
            "rabbit": "兔子",
            "hamster": "仓鼠"
        }
        return translations.get(pet_type, pet_type)
    
    def _calculate_estimated_value(self, breed_info: Dict[str, Any]) -> Dict[str, Any]:
        """计算估价"""
        price_range = breed_info.get("price_range", {"min": 100, "max": 1000})
        
        return {
            "min_price": price_range["min"],
            "max_price": price_range["max"],
            "currency": "CNY",
            "factors": [
                "年龄和健康状况",
                "血统和证书",
                "外观和品相",
                "训练程度",
                "地区市场差异"
            ],
            "note": "价格仅供参考，实际价格受多种因素影响"
        }
    
    def _get_alternative_breeds(self, pet_type: str, current_breed: str) -> List[Dict[str, Any]]:
        """获取相似品种"""
        breeds = self.PET_DATABASE.get(pet_type, {}).get("breeds", {})
        alternatives = []
        
        for breed_key, breed_info in breeds.items():
            if breed_key != current_breed:
                alternatives.append({
                    "breed": breed_info["name"],
                    "similarity": 0.8,  # 模拟相似度
                    "characteristics": breed_info.get("characteristics", [])[:2]
                })
        
        return alternatives[:3]  # 返回最多3个相似品种
    
    async def _save_recognition_record(
        self,
        db: Session,
        user_id: int,
        result: Dict[str, Any],
        image_format: str
    ):
        """保存识别记录"""
        from ..models.ai_recognition import AIRecognitionRecord
        
        try:
            record = AIRecognitionRecord(
                user_id=user_id,
                pet_type=result["pet_type"],
                breed=result["breed"],
                confidence=result["confidence"],
                result_data=result,
                image_format=image_format,
                status="completed"
            )
            
            db.add(record)
            db.commit()
            
        except Exception as e:
            logger.error(f"保存识别记录失败: {e}")
    
    async def get_recognition_history(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取识别历史"""
        from ..models.ai_recognition import AIRecognitionRecord
        
        query = db.query(AIRecognitionRecord).filter(
            AIRecognitionRecord.user_id == user_id
        ).order_by(AIRecognitionRecord.created_at.desc())
        
        total = query.count()
        records = query.offset((page - 1) * page_size).limit(page_size).all()
        
        history_items = []
        for record in records:
            history_items.append({
                "id": record.id,
                "pet_type": record.pet_type,
                "breed": record.breed,
                "confidence": record.confidence,
                "created_at": record.created_at.isoformat(),
                "result_summary": {
                    "characteristics": record.result_data.get("characteristics", [])[:3],
                    "estimated_value": record.result_data.get("estimated_value")
                }
            })
        
        return {
            "items": history_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def get_recognition_statistics(self, db: Session) -> Dict[str, Any]:
        """获取识别统计信息"""
        from ..models.ai_recognition import AIRecognitionRecord
        
        # 总体统计
        total_stats = db.query(
            func.count(AIRecognitionRecord.id).label('total_recognitions'),
            func.count(func.distinct(AIRecognitionRecord.user_id)).label('unique_users'),
            func.avg(AIRecognitionRecord.confidence).label('avg_confidence')
        ).first()
        
        # 按宠物类型统计
        type_stats = db.query(
            AIRecognitionRecord.pet_type,
            func.count(AIRecognitionRecord.id).label('count'),
            func.avg(AIRecognitionRecord.confidence).label('avg_confidence')
        ).group_by(AIRecognitionRecord.pet_type).all()
        
        # 最受欢迎的品种
        breed_stats = db.query(
            AIRecognitionRecord.breed,
            func.count(AIRecognitionRecord.id).label('count')
        ).group_by(AIRecognitionRecord.breed).order_by(
            func.count(AIRecognitionRecord.id).desc()
        ).limit(10).all()
        
        # 最近7天统计
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_stats = db.query(
            func.count(AIRecognitionRecord.id).label('recent_count'),
            func.avg(AIRecognitionRecord.confidence).label('recent_avg_confidence')
        ).filter(AIRecognitionRecord.created_at >= seven_days_ago).first()
        
        return {
            "total": {
                "recognitions": total_stats.total_recognitions or 0,
                "unique_users": total_stats.unique_users or 0,
                "avg_confidence": round(float(total_stats.avg_confidence or 0), 3)
            },
            "by_pet_type": [
                {
                    "pet_type": stat.pet_type,
                    "count": stat.count,
                    "avg_confidence": round(float(stat.avg_confidence), 3)
                }
                for stat in type_stats
            ],
            "popular_breeds": [
                {
                    "breed": stat.breed,
                    "count": stat.count
                }
                for stat in breed_stats
            ],
            "recent_7_days": {
                "count": recent_stats.recent_count or 0,
                "avg_confidence": round(float(recent_stats.recent_avg_confidence or 0), 3)
            }
        }
    
    async def get_breed_encyclopedia(self, pet_type: Optional[str] = None) -> Dict[str, Any]:
        """获取品种百科"""
        
        if pet_type:
            # 返回特定类型的品种信息
            breeds_data = self.PET_DATABASE.get(pet_type, {}).get("breeds", {})
            translated_type = self._translate_pet_type(pet_type)
            
            breeds = []
            for breed_key, breed_info in breeds_data.items():
                breeds.append({
                    "key": breed_key,
                    "name": breed_info["name"],
                    "characteristics": breed_info.get("characteristics", []),
                    "care_tips": breed_info.get("care_tips", [])[:3],
                    "popularity": breed_info.get("popularity", 0.0),
                    "price_range": breed_info.get("price_range", {})
                })
            
            return {
                "pet_type": translated_type,
                "breeds": breeds,
                "total_breeds": len(breeds)
            }
        
        else:
            # 返回所有类型的概览
            overview = {}
            for type_key, type_data in self.PET_DATABASE.items():
                translated_type = self._translate_pet_type(type_key)
                breeds_count = len(type_data.get("breeds", {}))
                
                overview[translated_type] = {
                    "breeds_count": breeds_count,
                    "popular_breeds": list(type_data.get("breeds", {}).values())[:3]
                }
            
            return {
                "overview": overview,
                "total_types": len(overview)
            }