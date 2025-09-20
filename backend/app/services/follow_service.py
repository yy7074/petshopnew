from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, or_
from datetime import datetime, timedelta
from typing import Optional, List
from app.models.user import User
from app.models.follow import UserFollow, BrowseHistory
from app.schemas.follow import (
    FollowUser, FollowResponse, FollowListResponse,
    BrowseHistoryItem, BrowseHistoryResponse, UserDetailResponse
)


class FollowService:
    def __init__(self, db: Session):
        self.db = db

    def follow_user(self, follower_id: int, following_id: int) -> FollowResponse:
        """关注用户"""
        if follower_id == following_id:
            return FollowResponse(success=False, message="不能关注自己", is_following=False)

        # 检查是否已经关注
        existing_follow = self.db.query(UserFollow).filter(
            and_(
                UserFollow.follower_id == follower_id,
                UserFollow.following_id == following_id
            )
        ).first()

        if existing_follow:
            return FollowResponse(success=False, message="已经关注过了", is_following=True)

        # 检查被关注用户是否存在
        target_user = self.db.query(User).filter(User.id == following_id).first()
        if not target_user:
            return FollowResponse(success=False, message="用户不存在", is_following=False)

        # 创建关注关系
        follow = UserFollow(follower_id=follower_id, following_id=following_id)
        self.db.add(follow)
        self.db.commit()

        return FollowResponse(success=True, message="关注成功", is_following=True)

    def unfollow_user(self, follower_id: int, following_id: int) -> FollowResponse:
        """取消关注用户"""
        follow = self.db.query(UserFollow).filter(
            and_(
                UserFollow.follower_id == follower_id,
                UserFollow.following_id == following_id
            )
        ).first()

        if not follow:
            return FollowResponse(success=False, message="未关注该用户", is_following=False)

        self.db.delete(follow)
        self.db.commit()

        return FollowResponse(success=True, message="取消关注成功", is_following=False)

    def get_following_list(self, user_id: int, page: int = 1, page_size: int = 20) -> FollowListResponse:
        """获取关注列表"""
        offset = (page - 1) * page_size

        # 查询关注的用户
        query = self.db.query(UserFollow, User).join(
            User, UserFollow.following_id == User.id
        ).filter(UserFollow.follower_id == user_id)

        total = query.count()
        follows = query.order_by(desc(UserFollow.created_at)).offset(offset).limit(page_size).all()

        items = []
        for follow, user in follows:
            # 获取该用户的粉丝数和关注数
            follower_count = self._get_follower_count(user.id)
            following_count = self._get_following_count(user.id)
            
            # 计算最后活跃时间
            last_active = self._calculate_last_active(user.last_login_at)

            follow_user = FollowUser(
                id=user.id,
                nickname=user.nickname or user.username,
                avatar_url=user.avatar_url,
                description=getattr(user, 'bio', None) or "这个人很懒，什么都没写",
                follower_count=follower_count,
                following_count=following_count,
                is_following=True,
                follow_time=follow.created_at,
                last_active=last_active,
                is_verified=user.is_verified
            )
            items.append(follow_user)

        has_more = total > page * page_size

        return FollowListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more
        )

    def get_followers_list(self, user_id: int, page: int = 1, page_size: int = 20) -> FollowListResponse:
        """获取粉丝列表"""
        offset = (page - 1) * page_size

        # 查询粉丝用户
        query = self.db.query(UserFollow, User).join(
            User, UserFollow.follower_id == User.id
        ).filter(UserFollow.following_id == user_id)

        total = query.count()
        follows = query.order_by(desc(UserFollow.created_at)).offset(offset).limit(page_size).all()

        items = []
        for follow, user in follows:
            # 获取该用户的粉丝数和关注数
            follower_count = self._get_follower_count(user.id)
            following_count = self._get_following_count(user.id)
            
            # 检查是否互相关注
            is_following = self._check_is_following(user_id, user.id)
            
            # 计算最后活跃时间
            last_active = self._calculate_last_active(user.last_login_at)
            
            # 判断是否为新粉丝（3天内关注的）
            is_new_follower = follow.created_at > datetime.now() - timedelta(days=3)

            follow_user = FollowUser(
                id=user.id,
                nickname=user.nickname or user.username,
                avatar_url=user.avatar_url,
                description=getattr(user, 'bio', None) or "这个人很懒，什么都没写",
                follower_count=follower_count,
                following_count=following_count,
                is_following=is_following,
                follow_time=follow.created_at,
                last_active=last_active,
                is_verified=user.is_verified
            )
            items.append(follow_user)

        has_more = total > page * page_size

        return FollowListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more
        )

    def _get_follower_count(self, user_id: int) -> int:
        """获取用户粉丝数"""
        return self.db.query(UserFollow).filter(UserFollow.following_id == user_id).count()

    def _get_following_count(self, user_id: int) -> int:
        """获取用户关注数"""
        return self.db.query(UserFollow).filter(UserFollow.follower_id == user_id).count()

    def _check_is_following(self, follower_id: int, following_id: int) -> bool:
        """检查是否关注"""
        return self.db.query(UserFollow).filter(
            and_(
                UserFollow.follower_id == follower_id,
                UserFollow.following_id == following_id
            )
        ).first() is not None

    def _calculate_last_active(self, last_login_at: Optional[datetime]) -> str:
        """计算最后活跃时间文本"""
        if not last_login_at:
            return "很久未活跃"
        
        now = datetime.now()
        diff = now - last_login_at
        
        if diff.days == 0:
            if diff.seconds < 3600:
                return f"{diff.seconds // 60}分钟前活跃"
            else:
                return f"{diff.seconds // 3600}小时前活跃"
        elif diff.days == 1:
            return "1天前活跃"
        elif diff.days < 7:
            return f"{diff.days}天前活跃"
        else:
            return "1周前活跃"


class BrowseHistoryService:
    def __init__(self, db: Session):
        self.db = db

    def add_browse_history(self, user_id: int, product_id: int, product_data: dict):
        """添加浏览历史"""
        # 检查是否已存在该商品的浏览记录
        existing = self.db.query(BrowseHistory).filter(
            and_(
                BrowseHistory.user_id == user_id,
                BrowseHistory.product_id == product_id
            )
        ).first()

        if existing:
            # 更新浏览时间
            existing.updated_at = datetime.now()
            self.db.commit()
            return

        # 创建新的浏览记录
        history = BrowseHistory(
            user_id=user_id,
            product_id=product_id,
            product_title=product_data.get('title', ''),
            product_image=product_data.get('image', ''),
            product_price=str(product_data.get('price', '0')),
            seller_name=product_data.get('seller_name', ''),
            seller_location=product_data.get('seller_location', ''),
            product_type=product_data.get('type', 'auction'),
            product_status=product_data.get('status', '拍卖中')
        )
        
        self.db.add(history)
        self.db.commit()

    def get_browse_history(self, user_id: int, page: int = 1, page_size: int = 20) -> BrowseHistoryResponse:
        """获取浏览历史"""
        offset = (page - 1) * page_size

        query = self.db.query(BrowseHistory).filter(BrowseHistory.user_id == user_id)
        total = query.count()
        
        histories = query.order_by(desc(BrowseHistory.updated_at)).offset(offset).limit(page_size).all()

        items = []
        for history in histories:
            browse_time_text = self._format_browse_time(history.updated_at)
            
            item = BrowseHistoryItem(
                id=history.id,
                product_id=history.product_id,
                product_title=history.product_title,
                product_image=history.product_image,
                product_price=history.product_price,
                seller_name=history.seller_name,
                seller_location=history.seller_location,
                product_type=history.product_type,
                product_status=history.product_status,
                browse_time=history.updated_at,
                browse_time_text=browse_time_text
            )
            items.append(item)

        return BrowseHistoryResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )

    def get_today_browse_history(self, user_id: int) -> List[BrowseHistoryItem]:
        """获取今天的浏览历史"""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        histories = self.db.query(BrowseHistory).filter(
            and_(
                BrowseHistory.user_id == user_id,
                BrowseHistory.updated_at >= today,
                BrowseHistory.updated_at < tomorrow
            )
        ).order_by(desc(BrowseHistory.updated_at)).all()

        items = []
        for history in histories:
            browse_time_text = f"今天 {history.updated_at.strftime('%H:%M')}"
            
            item = BrowseHistoryItem(
                id=history.id,
                product_id=history.product_id,
                product_title=history.product_title,
                product_image=history.product_image,
                product_price=history.product_price,
                seller_name=history.seller_name,
                seller_location=history.seller_location,
                product_type=history.product_type,
                product_status=history.product_status,
                browse_time=history.updated_at,
                browse_time_text=browse_time_text
            )
            items.append(item)

        return items

    def get_yesterday_browse_history(self, user_id: int) -> List[BrowseHistoryItem]:
        """获取昨天的浏览历史"""
        yesterday = datetime.now().date() - timedelta(days=1)
        today = datetime.now().date()
        
        histories = self.db.query(BrowseHistory).filter(
            and_(
                BrowseHistory.user_id == user_id,
                BrowseHistory.updated_at >= yesterday,
                BrowseHistory.updated_at < today
            )
        ).order_by(desc(BrowseHistory.updated_at)).all()

        items = []
        for history in histories:
            browse_time_text = f"昨天 {history.updated_at.strftime('%H:%M')}"
            
            item = BrowseHistoryItem(
                id=history.id,
                product_id=history.product_id,
                product_title=history.product_title,
                product_image=history.product_image,
                product_price=history.product_price,
                seller_name=history.seller_name,
                seller_location=history.seller_location,
                product_type=history.product_type,
                product_status=history.product_status,
                browse_time=history.updated_at,
                browse_time_text=browse_time_text
            )
            items.append(item)

        return items

    def delete_browse_history(self, user_id: int, history_id: int) -> bool:
        """删除浏览历史"""
        history = self.db.query(BrowseHistory).filter(
            and_(
                BrowseHistory.id == history_id,
                BrowseHistory.user_id == user_id
            )
        ).first()

        if not history:
            return False

        self.db.delete(history)
        self.db.commit()
        return True

    def clear_browse_history(self, user_id: int) -> bool:
        """清空浏览历史"""
        self.db.query(BrowseHistory).filter(BrowseHistory.user_id == user_id).delete()
        self.db.commit()
        return True

    def _format_browse_time(self, browse_time: datetime) -> str:
        """格式化浏览时间"""
        now = datetime.now()
        diff = now - browse_time
        
        if diff.days == 0:
            if diff.seconds < 3600:
                return f"{diff.seconds // 60}分钟前"
            else:
                return f"{diff.seconds // 3600}小时前"
        elif diff.days == 1:
            return "1天前"
        elif diff.days < 7:
            return f"{diff.days}天前"
        else:
            return browse_time.strftime("%m-%d")


class UserInfoService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_detail(self, user_id: int) -> Optional[UserDetailResponse]:
        """获取用户详细信息"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # 获取关注数和粉丝数
        following_count = self.db.query(UserFollow).filter(UserFollow.follower_id == user_id).count()
        follower_count = self.db.query(UserFollow).filter(UserFollow.following_id == user_id).count()

        return UserDetailResponse(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            real_name=user.real_name,
            phone=user.phone,
            email=user.email,
            avatar_url=user.avatar_url,
            gender=user.gender,
            birth_date=user.birth_date.strftime('%Y-%m-%d') if user.birth_date else None,
            location=user.location,
            bio=getattr(user, 'bio', None),
            is_verified=user.is_verified,
            follower_count=follower_count,
            following_count=following_count,
            created_at=user.created_at
        )

    def update_user_info(self, user_id: int, update_data: dict) -> bool:
        """更新用户信息"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        # 更新字段
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                if field == 'birth_date' and isinstance(value, str):
                    # 处理日期字符串
                    try:
                        from datetime import datetime
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    except:
                        continue
                setattr(user, field, value)

        self.db.commit()
        return True