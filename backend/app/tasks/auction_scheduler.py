import asyncio
import logging
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session
from ..core.database import SessionLocal, get_db
from ..services.auction_service import AuctionService

logger = logging.getLogger(__name__)

class AuctionScheduler:
    """拍卖定时任务调度器"""
    
    def __init__(self):
        self.auction_service = AuctionService()
        self.is_running = False
    
    async def start_scheduler(self, interval_minutes: int = 5):
        """启动定时任务，每隔指定分钟检查一次过期拍卖"""
        self.is_running = True
        logger.info(f"拍卖定时任务启动，检查间隔: {interval_minutes} 分钟")
        
        while self.is_running:
            try:
                await self._check_expired_auctions()
                await asyncio.sleep(interval_minutes * 60)  # 转换为秒
            except Exception as e:
                logger.error(f"定时任务执行失败: {e}")
                await asyncio.sleep(60)  # 出错时等待1分钟后重试
    
    async def stop_scheduler(self):
        """停止定时任务"""
        self.is_running = False
        logger.info("拍卖定时任务已停止")
    
    async def _check_expired_auctions(self):
        """检查并处理过期拍卖"""
        db = SessionLocal()
        try:
            results = await self.auction_service.check_and_end_auctions(db)
            
            if results:
                success_count = sum(1 for r in results if r.get("success"))
                failed_count = len(results) - success_count
                
                logger.info(
                    f"拍卖检查完成: 处理 {len(results)} 个拍卖, "
                    f"成功 {success_count} 个, 失败 {failed_count} 个"
                )
                
                # 记录失败的详细信息
                for result in results:
                    if not result.get("success"):
                        logger.error(
                            f"处理拍卖失败 - 商品ID: {result.get('product_id')}, "
                            f"错误: {result.get('error')}"
                        )
            else:
                logger.debug("当前没有需要处理的过期拍卖")
                
        except Exception as e:
            logger.error(f"检查过期拍卖时发生错误: {e}")
        finally:
            db.close()
    
    async def manual_check(self) -> List[dict]:
        """手动触发一次拍卖检查"""
        db = SessionLocal()
        try:
            results = await self.auction_service.check_and_end_auctions(db)
            logger.info(f"手动检查完成，处理了 {len(results)} 个拍卖")
            return results
        finally:
            db.close()

# 全局调度器实例
auction_scheduler = AuctionScheduler()

async def start_auction_scheduler():
    """启动拍卖定时任务"""
    await auction_scheduler.start_scheduler(interval_minutes=5)

async def stop_auction_scheduler():
    """停止拍卖定时任务"""
    await auction_scheduler.stop_scheduler()

async def manual_check_auctions():
    """手动检查拍卖"""
    return await auction_scheduler.manual_check()