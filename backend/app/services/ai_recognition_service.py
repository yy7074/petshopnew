from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import base64
import logging
from decimal import Decimal
import urllib3
import urllib.parse
import json
import ssl

from ..models.user import User
from ..core.config import settings

logger = logging.getLogger(__name__)

class AIRecognitionService:
    
    # 阿里云API配置
    ALIYUN_API_CONFIG = {
        "host": "https://pettype01.market.alicloudapi.com",
        "path": "/s/api/open/petType",
        "app_key": "204937064",
        "app_secret": "vFWCt9PWMxrgZZeJ3IT62ooO0M6FFYoL",
        "app_code": "ef0f5028b5ac46b6891b75d068725440",
        "method": "POST"
    }
    
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
        image_data: str = None,
        image_format: str = None,
        image_url: str = None
    ) -> Dict[str, Any]:
        """识别宠物图片"""
        
        # 检查参数
        if not image_data and not image_url:
            raise ValueError("必须提供图片数据或图片URL")
        
        # 检查用户识别次数限制
        daily_check = await self._check_daily_limit(db, user_id)
        if not daily_check["allowed"]:
            raise ValueError(daily_check["message"])
        
        # 验证图片格式和大小（仅当提供image_data时）
        if image_data:
            validation_result = await self._validate_image(image_data, image_format)
            if not validation_result["valid"]:
                # 对于小图片，只输出警告而不阻止识别
                if "过小" in validation_result["message"]:
                    logger.warning(f"图片质量警告: {validation_result['message']}")
                else:
                    raise ValueError(validation_result["message"])
        
        try:
            # 调用阿里云AI识别接口
            recognition_result = await self._perform_ai_recognition(image_data, image_url)
            
            # 检查是否是真实API结果
            api_source = recognition_result.get("api_source", "unknown")
            if api_source in ["fallback_simulation", "fallback", "aliyun_error", "aliyun_http_error", "aliyun_exception", "aliyun_parse_error"]:
                error_message = recognition_result.get("error", "API调用失败")
                return {
                    "success": False,
                    "message": f"识别失败: {error_message}",
                    "data": None,
                    "error_details": f"API源: {api_source}",
                    "api_source": api_source
                }
            
            # 只有真实API结果才进行增强处理
            enhanced_result = await self._enhance_recognition_result(recognition_result)
            
            # 记录识别历史
            await self._save_recognition_record(db, user_id, enhanced_result, image_format or 'url')
            
            return {
                "success": True,
                "data": enhanced_result,
                "message": "识别成功",
                "api_source": recognition_result.get("api_source", "unknown")
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
    
    async def _perform_ai_recognition(self, image_data: str, image_url: str = None) -> Dict[str, Any]:
        """执行阿里云AI宠物识别"""
        
        # 首先记录调用信息
        logger.info(f"开始AI识别 - 使用图片URL: {bool(image_url)}, 使用图片数据: {bool(image_data)}")
        
        try:
            # 准备API请求
            url = self.ALIYUN_API_CONFIG["host"] + self.ALIYUN_API_CONFIG["path"]
            
            # 请求头 - 使用APPCODE认证
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Authorization': 'APPCODE ' + self.ALIYUN_API_CONFIG["app_code"]
            }
            
            # 请求体 - 根据阿里云API官方文档格式
            body_data = {}
            
            # 图片参数（按照官方示例格式）
            if image_url:
                body_data['imageUrl'] = image_url
                # 如果使用URL，清空base64参数
                body_data['imageBase64'] = ''
            elif image_data:
                body_data['imageBase64'] = image_data
                # 如果使用base64，清空URL参数
                body_data['imageUrl'] = ''
            else:
                raise ValueError("必须提供imageUrl或imageBase64参数")
            
            # petType是必填参数：0为狗，1为猫，按照官方示例格式
            body_data['petType'] = '0'  # 先尝试识别狗（字符串格式）
            
            # 编码请求体
            post_data = urllib.parse.urlencode(body_data).encode('utf-8')
            
            # 创建HTTP连接池
            http = urllib3.PoolManager()
            
            logger.info(f"发送请求到: {url}")
            logger.info(f"请求参数: petType={body_data.get('petType')}, 有图片数据: {bool(image_data)}, 有图片URL: {bool(image_url)}")
            
            # 发送请求
            response = http.request('POST', url, body=post_data, headers=headers)
            
            # 解析响应
            content = response.data.decode('utf-8')
            logger.info(f"阿里云API响应状态: {response.status}")
            logger.info(f"阿里云API响应内容: {content}")
            
            if response.status == 200:
                try:
                    # 解析JSON响应
                    result = json.loads(content)
                    
                    # 检查API响应状态
                    if self._is_aliyun_success(result):
                        logger.info("阿里云API识别成功")
                        return self._parse_aliyun_response(result)
                    else:
                        # 如果狗类识别失败，尝试猫类识别
                        if body_data.get('petType') == '0':
                            logger.info("狗类识别失败，尝试猫类识别")
                            body_data['petType'] = '1'  # 字符串格式
                            post_data = urllib.parse.urlencode(body_data).encode('utf-8')
                            
                            response = http.request('POST', url, body=post_data, headers=headers)
                            content = response.data.decode('utf-8')
                            logger.info(f"阿里云API响应(猫类状态): {response.status}")
                            logger.info(f"阿里云API响应(猫类内容): {content}")
                            
                            if response.status == 200:
                                try:
                                    result = json.loads(content)
                                    if self._is_aliyun_success(result):
                                        logger.info("阿里云API猫类识别成功")
                                        return self._parse_aliyun_response(result)
                                except json.JSONDecodeError as e:
                                    logger.error(f"猫类识别响应JSON解析失败: {e}")
                        
                        logger.error(f"阿里云API返回错误: {result}")
                        return {
                            "pet_type": "unknown",
                            "breed": "识别失败", 
                            "confidence": 0.0,
                            "raw_predictions": [],
                            "api_source": "aliyun_error",
                            "error": result.get("message", "API返回错误")
                        }
                        
                except json.JSONDecodeError as e:
                    logger.error(f"阿里云API响应JSON解析失败: {e}")
                    logger.error(f"原始响应内容: {content}")
                    return {
                        "pet_type": "unknown",
                        "breed": "响应解析失败", 
                        "confidence": 0.0,
                        "raw_predictions": [],
                        "api_source": "aliyun_parse_error",
                        "error": f"JSON解析失败: {str(e)}"
                    }
            else:
                logger.error(f"阿里云API请求失败，状态码: {response.status}, 响应: {content}")
                return {
                    "pet_type": "unknown",
                    "breed": "API请求失败", 
                    "confidence": 0.0,
                    "raw_predictions": [],
                    "api_source": "aliyun_http_error",
                    "error": f"HTTP状态码: {response.status}"
                }
                
        except Exception as e:
            logger.error(f"调用阿里云API异常: {e}", exc_info=True)
            return {
                "pet_type": "unknown",
                "breed": "API调用异常", 
                "confidence": 0.0,
                "raw_predictions": [],
                "api_source": "aliyun_exception",
                "error": str(e)
            }
    
    def _is_aliyun_success(self, result: Dict[str, Any]) -> bool:
        """检查阿里云API调用是否成功"""
        # 根据API文档，成功的条件是：
        # code: 0 表示成功，status: 200 表示HTTP成功，且有data字段
        return (
            result.get('code') == 0 and
            result.get('status') == 200 and
            'data' in result and
            result['data'] is not None
        )
    
    def _parse_aliyun_response(self, api_result: Dict[str, Any]) -> Dict[str, Any]:
        """解析阿里云API响应"""
        try:
            # 根据API文档的响应格式解析
            # 成功响应格式: {"code": 0, "data": {"pet": [{"identification": [...]}], "petType": "dog"}, "status": 200}
            
            data = api_result.get('data', {})
            pet_list = data.get('pet', [])
            
            logger.info(f"解析API响应 - 完整响应: {api_result}")
            
            if not pet_list:
                logger.warning("API响应中没有宠物识别结果")
                return {
                    "pet_type": "unknown",
                    "breed": "未检测到宠物", 
                    "confidence": 0.0,
                    "raw_predictions": [],
                    "api_source": "aliyun_no_results",
                    "original_response": api_result
                }
            
            # 获取第一个宠物的识别结果
            first_pet = pet_list[0]
            identifications = first_pet.get('identification', [])
            
            logger.info(f"解析详情 - 宠物数量: {len(pet_list)}, 识别结果数量: {len(identifications)}")
            logger.info(f"识别结果: {identifications}")
            
            if not identifications:
                logger.warning("API响应中没有品种识别结果")
                return {
                    "pet_type": "unknown",
                    "breed": "无法识别品种", 
                    "confidence": 0.0,
                    "raw_predictions": [],
                    "api_source": "aliyun_no_identification",
                    "original_response": api_result
                }
            
            # 获取置信度最高的结果（第一个就是最高的）
            best_result = identifications[0]
            
            # 提取宠物类型
            pet_type_code = data.get('petType', 'unknown')
            pet_type_map = {
                'cat': '猫',
                'dog': '狗',
                'bird': '鸟',
                'fish': '鱼'
            }
            pet_type = pet_type_map.get(pet_type_code, pet_type_code)
            
            # 提取品种信息（优先中文名）
            breed_chinese = best_result.get('chinese_name', '')
            breed_english = best_result.get('english_name', '')
            breed = breed_chinese if breed_chinese else breed_english
            if not breed:
                breed = '未知品种'
            
            # 提取置信度
            confidence = best_result.get('confidence', 0.0)
            if isinstance(confidence, str):
                try:
                    confidence = float(confidence)
                except:
                    confidence = 0.0
            
            # 构建所有预测结果列表
            predictions = []
            for identification in identifications:
                chinese_name = identification.get('chinese_name', '')
                english_name = identification.get('english_name', '')
                pred_confidence = identification.get('confidence', 0.0)
                
                predictions.append({
                    'breed': chinese_name if chinese_name else english_name,
                    'chinese_name': chinese_name,
                    'english_name': english_name,
                    'confidence': pred_confidence
                })
            
            logger.info(f"解析成功 - 宠物类型: {pet_type}, 品种: {breed}, 置信度: {confidence}")
            
            return {
                "pet_type": pet_type,
                "breed": breed,
                "confidence": float(confidence),
                "raw_predictions": predictions,
                "api_source": "aliyun",
                "original_response": api_result
            }
            
        except Exception as e:
            logger.error(f"解析阿里云API响应失败: {e}")
            logger.error(f"原始响应: {api_result}")
            # 解析失败时返回错误结果
            return {
                "pet_type": "unknown",
                "breed": "解析失败", 
                "confidence": 0.0,
                "raw_predictions": [],
                "api_source": "aliyun_parse_error",
                "error": str(e),
                "original_response": api_result
            }
    
    async def _fallback_recognition(self) -> Dict[str, Any]:
        """回退到模拟识别（当API调用失败时）"""
        import asyncio
        import random
        
        logger.warning("使用回退识别机制 - 阿里云API不可用")
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # 模拟识别结果
        pet_types = list(self.PET_DATABASE.keys())
        selected_type = random.choice(pet_types)
        
        breeds = list(self.PET_DATABASE[selected_type]["breeds"].keys())
        selected_breed = random.choice(breeds)
        
        # 生成置信度 (降低置信度以表明这是模拟结果)
        confidence = random.uniform(0.3, 0.7)
        
        return {
            "pet_type": selected_type,
            "breed": selected_breed,
            "confidence": confidence,
            "raw_predictions": [
                {"breed": selected_breed, "confidence": confidence},
                {"breed": random.choice(breeds), "confidence": confidence - 0.1},
                {"breed": random.choice(breeds), "confidence": confidence - 0.2}
            ],
            "api_source": "fallback_simulation",
            "warning": "此结果为模拟数据，真实API暂不可用"
        }
    
    async def _enhance_recognition_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """增强识别结果，添加详细信息"""
        
        pet_type = raw_result["pet_type"]
        breed_name = raw_result["breed"]
        confidence = raw_result["confidence"]
        
        # 直接返回API识别的品种名，不再依赖本地数据库匹配
        # 因为API返回的品种信息已经很准确了
        return {
            "pet_type": self._translate_pet_type(pet_type),
            "breed": breed_name,  # 直接使用API返回的品种名
            "confidence": confidence,
            "characteristics": self._get_generic_characteristics(pet_type),
            "care_advice": self._get_generic_care_advice(pet_type),
            "health_tips": self._get_generic_health_tips(pet_type),
            "feeding_guide": self._get_generic_feeding_guide(pet_type),
            "estimated_value": self._get_generic_estimated_value(pet_type, breed_name),
            "raw_predictions": raw_result.get("raw_predictions", [])
        }
    
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
    
    def _get_generic_characteristics(self, pet_type: str) -> List[str]:
        """获取通用特征"""
        characteristics_map = {
            "猫": ["独立", "优雅", "敏捷", "聪明"],
            "狗": ["忠诚", "友善", "活泼", "聪明"],
            "鸟": ["活泼", "聪明", "善于模仿", "社交性强"],
            "鱼": ["安静", "观赏性强", "易养护", "色彩丰富"]
        }
        return characteristics_map.get(pet_type, ["温驯", "可爱"])
    
    def _get_generic_care_advice(self, pet_type: str) -> List[str]:
        """获取通用饲养建议"""
        care_map = {
            "猫": ["提供猫砂盆", "定期梳毛", "注意口腔健康", "提供抓板"],
            "狗": ["每天需要运动", "定期梳毛", "注意饮食营养", "定期疫苗接种"],
            "鸟": ["提供宽敞鸟笼", "多样化饮食", "定期清洁", "适当社交"],
            "鱼": ["保持水质清洁", "适宜水温", "充足氧气", "定期换水"]
        }
        return care_map.get(pet_type, ["定期护理", "注意卫生"])
    
    def _get_generic_health_tips(self, pet_type: str) -> List[str]:
        """获取通用健康建议"""
        health_map = {
            "猫": ["预防泌尿系统疾病", "定期驱虫", "关注眼部健康", "预防肥胖"],
            "狗": ["关注关节健康", "预防皮肤病", "定期体检", "注意体重控制"],
            "鸟": ["注意呼吸道健康", "预防羽毛病", "定期检查爪子", "避免温差过大"],
            "鱼": ["预防白点病", "注意水质变化", "避免过度喂食", "观察游泳状态"]
        }
        return health_map.get(pet_type, ["定期健康检查", "注意环境卫生"])
    
    def _get_generic_feeding_guide(self, pet_type: str) -> List[str]:
        """获取通用喂养指南"""
        feeding_map = {
            "猫": ["高蛋白猫粮", "适量湿粮", "避免牛奶", "控制零食量"],
            "狗": ["优质狗粮为主", "适量肉类", "避免巧克力等有害食物", "充足饮水"],
            "鸟": ["专用鸟粮", "新鲜蔬果", "适量种子", "清洁饮水"],
            "鱼": ["专用鱼食", "控制喂食量", "多样化饮食", "定时定量"]
        }
        return feeding_map.get(pet_type, ["营养均衡", "定时喂养"])
    
    def _get_generic_estimated_value(self, pet_type: str, breed_name: str) -> Dict[str, Any]:
        """获取通用估价信息"""
        base_values = {
            "猫": {"min": 500, "max": 5000},
            "狗": {"min": 800, "max": 8000},
            "鸟": {"min": 200, "max": 1500},
            "鱼": {"min": 50, "max": 800}
        }
        
        base = base_values.get(pet_type, {"min": 100, "max": 1000})
        
        return {
            "min_price": base["min"],
            "max_price": base["max"],
            "currency": "CNY",
            "factors": [
                "年龄和健康状况",
                "血统和证书",
                "外观和品相",
                "训练程度",
                "地区市场差异"
            ],
            "note": f"价格仅供参考，{breed_name}的实际价格受多种因素影响"
        }
    
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