from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from app.models.user import UserCheckin
from app.schemas.checkin import (
    CheckinStatus, CheckinResult, CheckinInfo, DailyReward, MilestoneInfo,
    CheckinRecord, CheckinHistoryResponse, CheckinStatistics,
    CheckinCalendarData, CheckinCalendarDay
)


class CheckinService:
    def __init__(self, db: Session):
        self.db = db

    def get_checkin_status(self, user_id: int) -> CheckinStatus:
        """获取用户签到状态"""
        today = date.today()
        
        # 检查今天是否已签到
        today_checkin = self.db.query(UserCheckin).filter(
            and_(
                UserCheckin.user_id == user_id,
                UserCheckin.checkin_date == today
            )
        ).first()
        
        is_checked_today = today_checkin is not None
        
        # 获取连续签到天数
        consecutive_days = self._calculate_consecutive_days(user_id)
        
        # 获取总签到天数
        total_checkin_days = self.db.query(UserCheckin).filter(
            UserCheckin.user_id == user_id
        ).count()
        
        # 获取本月签到日期
        month_start = today.replace(day=1)
        month_checkins = self.db.query(UserCheckin.checkin_date).filter(
            and_(
                UserCheckin.user_id == user_id,
                UserCheckin.checkin_date >= month_start,
                UserCheckin.checkin_date <= today
            )
        ).all()
        
        month_checkin_dates = [checkin.checkin_date.day for checkin in month_checkins]
        
        # 今日奖励
        today_reward = DailyReward(
            points=self._get_daily_reward_points(consecutive_days + 1 if not is_checked_today else consecutive_days),
            description="每日签到奖励"
        )
        
        # 下个里程碑
        next_milestone = self._get_next_milestone(consecutive_days)
        
        return CheckinStatus(
            is_checked_today=is_checked_today,
            consecutive_days=consecutive_days,
            total_checkin_days=total_checkin_days,
            month_checkin_dates=month_checkin_dates,
            today_reward=today_reward,
            next_milestone=next_milestone,
            can_checkin=not is_checked_today
        )

    def daily_checkin(self, user_id: int) -> CheckinResult:
        """执行每日签到"""
        today = date.today()
        
        # 检查今天是否已签到
        existing_checkin = self.db.query(UserCheckin).filter(
            and_(
                UserCheckin.user_id == user_id,
                UserCheckin.checkin_date == today
            )
        ).first()
        
        if existing_checkin:
            raise ValueError("今天已经签到过了")
        
        # 计算连续签到天数
        consecutive_days = self._calculate_consecutive_days(user_id) + 1
        
        # 计算奖励
        daily_points = self._get_daily_reward_points(consecutive_days)
        milestone_points = 0
        is_milestone = self._is_milestone_day(consecutive_days)
        
        if is_milestone:
            milestone_points = self._get_milestone_reward(consecutive_days)
        
        total_points = daily_points + milestone_points
        
        # 创建签到记录
        checkin = UserCheckin(
            user_id=user_id,
            checkin_date=today,
            consecutive_days=consecutive_days,
            reward_points=total_points
        )
        
        self.db.add(checkin)
        self.db.commit()
        self.db.refresh(checkin)
        
        # 构建返回结果
        daily_reward = DailyReward(points=daily_points, description="每日签到奖励")
        milestone_reward = None
        if is_milestone:
            milestone_reward = DailyReward(points=milestone_points, description=f"连续签到{consecutive_days}天里程碑奖励")
        
        checkin_info = CheckinInfo(
            consecutive_days=consecutive_days,
            reward_points=total_points,
            daily_reward=daily_reward,
            milestone_reward=milestone_reward,
            is_milestone=is_milestone
        )
        
        return CheckinResult(
            message="签到成功！",
            checkin_info=checkin_info
        )

    def get_checkin_history(self, user_id: int, page: int = 1, page_size: int = 20) -> CheckinHistoryResponse:
        """获取签到历史"""
        offset = (page - 1) * page_size
        
        query = self.db.query(UserCheckin).filter(UserCheckin.user_id == user_id)
        total = query.count()
        
        checkins = query.order_by(desc(UserCheckin.checkin_date)).offset(offset).limit(page_size).all()
        
        items = [
            CheckinRecord(
                id=checkin.id,
                checkin_date=checkin.checkin_date.strftime("%Y-%m-%d"),
                consecutive_days=checkin.consecutive_days,
                reward_points=checkin.reward_points,
                created_at=checkin.created_at
            )
            for checkin in checkins
        ]
        
        total_pages = (total + page_size - 1) // page_size
        
        return CheckinHistoryResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def get_checkin_statistics(self, user_id: int) -> CheckinStatistics:
        """获取签到统计"""
        total_checkin_days = self.db.query(UserCheckin).filter(UserCheckin.user_id == user_id).count()
        
        total_points = self.db.query(func.sum(UserCheckin.reward_points)).filter(
            UserCheckin.user_id == user_id
        ).scalar() or 0
        
        # 计算最大连续签到天数
        max_consecutive_days = self._calculate_max_consecutive_days(user_id)
        
        # 当前连续签到天数
        current_consecutive_days = self._calculate_consecutive_days(user_id)
        
        # 本月签到天数
        today = date.today()
        month_start = today.replace(day=1)
        month_checkin_days = self.db.query(UserCheckin).filter(
            and_(
                UserCheckin.user_id == user_id,
                UserCheckin.checkin_date >= month_start,
                UserCheckin.checkin_date <= today
            )
        ).count()
        
        return CheckinStatistics(
            total_checkin_days=total_checkin_days,
            total_points=int(total_points),
            max_consecutive_days=max_consecutive_days,
            current_consecutive_days=current_consecutive_days,
            month_checkin_days=month_checkin_days
        )

    def get_checkin_calendar(self, user_id: int, year: int, month: int) -> CheckinCalendarData:
        """获取签到日历"""
        # 获取指定月份的签到记录
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
        
        checkins = self.db.query(UserCheckin).filter(
            and_(
                UserCheckin.user_id == user_id,
                UserCheckin.checkin_date >= month_start,
                UserCheckin.checkin_date <= month_end
            )
        ).all()
        
        calendar = {}
        for checkin in checkins:
            day = checkin.checkin_date.day
            calendar[day] = CheckinCalendarDay(
                consecutive_days=checkin.consecutive_days,
                reward_points=checkin.reward_points,
                is_milestone=self._is_milestone_day(checkin.consecutive_days)
            )
        
        return CheckinCalendarData(
            year=year,
            month=month,
            calendar=calendar,
            total_days=len(checkins)
        )

    def _calculate_consecutive_days(self, user_id: int) -> int:
        """计算连续签到天数"""
        today = date.today()
        consecutive_days = 0
        current_date = today
        
        while True:
            checkin = self.db.query(UserCheckin).filter(
                and_(
                    UserCheckin.user_id == user_id,
                    UserCheckin.checkin_date == current_date
                )
            ).first()
            
            if checkin:
                consecutive_days += 1
                current_date -= timedelta(days=1)
            else:
                # 如果当前日期是今天且没有签到记录，检查昨天
                if current_date == today:
                    current_date -= timedelta(days=1)
                    continue
                else:
                    break
        
        return consecutive_days

    def _calculate_max_consecutive_days(self, user_id: int) -> int:
        """计算历史最大连续签到天数"""
        checkins = self.db.query(UserCheckin.checkin_date).filter(
            UserCheckin.user_id == user_id
        ).order_by(UserCheckin.checkin_date).all()
        
        if not checkins:
            return 0
        
        max_consecutive = 1
        current_consecutive = 1
        
        for i in range(1, len(checkins)):
            prev_date = checkins[i-1].checkin_date
            curr_date = checkins[i].checkin_date
            
            if (curr_date - prev_date).days == 1:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1
        
        return max_consecutive

    def _get_daily_reward_points(self, consecutive_days: int) -> int:
        """获取每日奖励钻石数"""
        # 基础奖励10钻石，连续签到有额外奖励
        if consecutive_days <= 7:
            return 10
        elif consecutive_days <= 14:
            return 15
        elif consecutive_days <= 30:
            return 20
        else:
            return 25

    def _is_milestone_day(self, consecutive_days: int) -> bool:
        """判断是否是里程碑天数"""
        milestone_days = [7, 14, 30, 60, 100, 365]
        return consecutive_days in milestone_days

    def _get_milestone_reward(self, consecutive_days: int) -> int:
        """获取里程碑奖励"""
        milestone_rewards = {
            7: 50,      # 连续7天额外50钻石
            14: 100,    # 连续14天额外100钻石
            30: 200,    # 连续30天额外200钻石
            60: 500,    # 连续60天额外500钻石
            100: 1000,  # 连续100天额外1000钻石
            365: 3650   # 连续365天额外3650钻石
        }
        return milestone_rewards.get(consecutive_days, 0)

    def _get_next_milestone(self, consecutive_days: int) -> Optional[MilestoneInfo]:
        """获取下个里程碑信息"""
        milestone_days = [7, 14, 30, 60, 100, 365]
        
        for milestone in milestone_days:
            if consecutive_days < milestone:
                remaining_days = milestone - consecutive_days
                reward_points = self._get_milestone_reward(milestone)
                return MilestoneInfo(
                    days=milestone,
                    remaining_days=remaining_days,
                    reward=DailyReward(
                        points=reward_points,
                        description=f"连续签到{milestone}天里程碑奖励"
                    )
                )
        
        return None