from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import random
import logging

from ..models.lottery import LotteryPrize, LotteryRecord, LotteryConfig
from ..models.user import User

logger = logging.getLogger(__name__)

class LotteryService:
    
    async def get_lottery_config(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取抽奖配置信息"""
        try:
            # 获取配置
            config = db.query(LotteryConfig).first()
            if not config:
                # 创建默认配置
                config = LotteryConfig(
                    max_daily_draws=3,
                    cost_per_draw=0,
                    is_active=True,
                    description="钻石抽奖，每日免费3次机会！"
                )
                db.add(config)
                db.commit()
                db.refresh(config)
            
            # 检查今日已抽奖次数
            today = datetime.now().date()
            today_draws = db.query(func.count(LotteryRecord.id)).filter(
                and_(
                    LotteryRecord.user_id == user_id,
                    func.date(LotteryRecord.created_at) == today
                )
            ).scalar() or 0
            
            # 获取奖品列表
            prizes = db.query(LotteryPrize).filter(
                LotteryPrize.is_active == True
            ).order_by(LotteryPrize.sort_order).all()
            
            remaining_draws = max(0, config.max_daily_draws - today_draws)
            
            return {
                "max_daily_draws": config.max_daily_draws,
                "cost_per_draw": config.cost_per_draw,
                "is_active": config.is_active,
                "remaining_draws": remaining_draws,
                "today_draws": today_draws,
                "prizes": prizes,
                "description": config.description
            }
            
        except Exception as e:
            logger.error(f"获取抽奖配置失败: {e}")
            raise
    
    async def draw_lottery(self, db: Session, user_id: int, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """执行抽奖"""
        try:
            # 检查活动是否开启
            config = db.query(LotteryConfig).first()
            if not config or not config.is_active:
                return {
                    "success": False,
                    "message": "抽奖活动暂未开启",
                    "prize": None,
                    "remaining_draws": 0,
                    "total_draws_today": 0
                }
            
            # 检查今日抽奖次数
            today = datetime.now().date()
            today_draws = db.query(func.count(LotteryRecord.id)).filter(
                and_(
                    LotteryRecord.user_id == user_id,
                    func.date(LotteryRecord.created_at) == today
                )
            ).scalar() or 0
            
            if today_draws >= config.max_daily_draws:
                return {
                    "success": False,
                    "message": f"今日抽奖次数已用完（{config.max_daily_draws}次）",
                    "prize": None,
                    "remaining_draws": 0,
                    "total_draws_today": today_draws
                }
            
            # 获取可用奖品
            prizes = db.query(LotteryPrize).filter(
                and_(
                    LotteryPrize.is_active == True,
                    LotteryPrize.stock != 0  # 库存不为0
                )
            ).all()
            
            if not prizes:
                return {
                    "success": False,
                    "message": "暂无可抽取的奖品",
                    "prize": None,
                    "remaining_draws": config.max_daily_draws - today_draws - 1,
                    "total_draws_today": today_draws + 1
                }
            
            # 执行抽奖逻辑
            selected_prize = self._select_prize_by_probability(prizes)
            
            if not selected_prize:
                return {
                    "success": False,
                    "message": "抽奖失败，请重试",
                    "prize": None,
                    "remaining_draws": config.max_daily_draws - today_draws,
                    "total_draws_today": today_draws
                }
            
            # 扣减库存（如果不是无限库存）
            if selected_prize.stock > 0:
                selected_prize.stock -= 1
                db.commit()
            
            # 记录抽奖结果
            lottery_record = LotteryRecord(
                user_id=user_id,
                prize_id=selected_prize.id,
                prize_name=selected_prize.name,
                prize_type=selected_prize.type,
                prize_value=selected_prize.value,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(lottery_record)
            db.commit()
            db.refresh(lottery_record)
            
            remaining_draws = config.max_daily_draws - today_draws - 1
            
            return {
                "success": True,
                "message": f"恭喜您抽中：{selected_prize.name}！",
                "prize": selected_prize,
                "remaining_draws": remaining_draws,
                "total_draws_today": today_draws + 1,
                "record_id": lottery_record.id
            }
            
        except Exception as e:
            logger.error(f"抽奖失败: {e}")
            db.rollback()
            raise
    
    def _select_prize_by_probability(self, prizes: List[LotteryPrize]) -> Optional[LotteryPrize]:
        """根据概率选择奖品"""
        try:
            # 计算总概率
            total_probability = sum(prize.probability for prize in prizes)
            
            if total_probability <= 0:
                return None
            
            # 生成随机数
            random_value = random.random() * total_probability
            
            # 根据概率选择奖品
            cumulative_probability = 0
            for prize in prizes:
                cumulative_probability += prize.probability
                if random_value <= cumulative_probability:
                    return prize
            
            # 如果没有选中，返回最后一个奖品
            return prizes[-1] if prizes else None
            
        except Exception as e:
            logger.error(f"选择奖品失败: {e}")
            return None
    
    async def get_lottery_history(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取用户抽奖历史"""
        try:
            query = db.query(LotteryRecord).filter(
                LotteryRecord.user_id == user_id
            ).order_by(LotteryRecord.created_at.desc())
            
            total = query.count()
            records = query.offset((page - 1) * page_size).limit(page_size).all()
            
            return {
                "items": records,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"获取抽奖历史失败: {e}")
            raise
    
    async def claim_prize(self, db: Session, user_id: int, record_id: int) -> Dict[str, Any]:
        """领取奖品"""
        try:
            # 查找抽奖记录
            record = db.query(LotteryRecord).filter(
                and_(
                    LotteryRecord.id == record_id,
                    LotteryRecord.user_id == user_id
                )
            ).first()
            
            if not record:
                return {
                    "success": False,
                    "message": "抽奖记录不存在"
                }
            
            if record.is_claimed:
                return {
                    "success": False,
                    "message": "奖品已经领取过了"
                }
            
            # 标记为已领取
            record.is_claimed = True
            record.claimed_at = datetime.now()
            
            # 根据奖品类型处理
            if record.prize_type in ["voucher", "coupon"]:
                # 这里可以发放优惠券到用户账户
                # 暂时只更新记录状态
                pass
            elif record.prize_type == "pet":
                # 宠物类奖品可能需要线下处理
                pass
            
            db.commit()
            
            return {
                "success": True,
                "message": f"成功领取：{record.prize_name}"
            }
            
        except Exception as e:
            logger.error(f"领取奖品失败: {e}")
            db.rollback()
            raise
    
    async def get_lottery_statistics(self, db: Session, days: int = 7) -> Dict[str, Any]:
        """获取抽奖统计信息（管理员用）"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 总抽奖次数
            total_draws = db.query(func.count(LotteryRecord.id)).filter(
                LotteryRecord.created_at >= start_date
            ).scalar() or 0
            
            # 不同奖品的中奖统计
            prize_stats = db.query(
                LotteryRecord.prize_name,
                func.count(LotteryRecord.id).label('count')
            ).filter(
                LotteryRecord.created_at >= start_date
            ).group_by(LotteryRecord.prize_name).all()
            
            # 每日抽奖统计
            daily_stats = db.query(
                func.date(LotteryRecord.created_at).label('date'),
                func.count(LotteryRecord.id).label('count')
            ).filter(
                LotteryRecord.created_at >= start_date
            ).group_by(func.date(LotteryRecord.created_at)).all()
            
            return {
                "total_draws": total_draws,
                "prize_distribution": [
                    {"prize_name": stat.prize_name, "count": stat.count}
                    for stat in prize_stats
                ],
                "daily_draws": [
                    {"date": str(stat.date), "count": stat.count}
                    for stat in daily_stats
                ],
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"获取抽奖统计失败: {e}")
            raise
    
    async def init_default_prizes(self, db: Session) -> bool:
        """初始化默认奖品"""
        try:
            # 检查是否已有奖品
            existing_count = db.query(func.count(LotteryPrize.id)).scalar()
            if existing_count > 0:
                return True
            
            # 创建默认奖品
            default_prizes = [
                {"name": "1元抵用券", "type": "voucher", "value": 1.0, "color": "#FFE4E1", "probability": 0.25, "sort_order": 1},
                {"name": "2元抵用券", "type": "voucher", "value": 2.0, "color": "#FFB6C1", "probability": 0.20, "sort_order": 2},
                {"name": "3元抵用券", "type": "voucher", "value": 3.0, "color": "#FFA07A", "probability": 0.15, "sort_order": 3},
                {"name": "9.9元抵用券", "type": "voucher", "value": 9.9, "color": "#FF7F50", "probability": 0.12, "sort_order": 4},
                {"name": "12元抵用券", "type": "voucher", "value": 12.0, "color": "#FF6347", "probability": 0.10, "sort_order": 5},
                {"name": "15元抵用券", "type": "voucher", "value": 15.0, "color": "#FF4500", "probability": 0.08, "sort_order": 6},
                {"name": "90元优惠券", "type": "coupon", "value": 90.0, "color": "#DC143C", "probability": 0.05, "sort_order": 7},
                {"name": "128元优惠券", "type": "coupon", "value": 128.0, "color": "#B22222", "probability": 0.03, "sort_order": 8},
                {"name": "鹦鹉一只", "type": "pet", "value": 300.0, "color": "#228B22", "probability": 0.015, "sort_order": 9, "stock": 10},
                {"name": "仓鼠一只", "type": "pet", "value": 80.0, "color": "#32CD32", "probability": 0.005, "sort_order": 10, "stock": 5},
            ]
            
            for prize_data in default_prizes:
                prize = LotteryPrize(**prize_data)
                db.add(prize)
            
            db.commit()
            logger.info("默认抽奖奖品初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化默认奖品失败: {e}")
            db.rollback()
            return False
