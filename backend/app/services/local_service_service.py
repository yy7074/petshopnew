from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
import os
import uuid
from fastapi import UploadFile, HTTPException

from ..models.local_service import (
    LocalServicePost, LocalServiceComment, LocalServiceLike, LocalServiceFavorite,
    PetSocialPost, PetSocialComment
)
from ..models.user import User
from ..schemas.local_service import (
    LocalServiceCreate, LocalServiceUpdate, LocalServiceResponse,
    LocalServiceCommentCreate, LocalServiceCommentResponse,
    PetSocialPostCreate, PetSocialPostUpdate, PetSocialPostResponse,
    PetSocialCommentCreate, PetSocialCommentResponse,
    ServiceTypesResponse, ServiceType
)


class LocalServiceService:
    
    def __init__(self):
        self.upload_dir = "static/uploads/local_services"
        os.makedirs(self.upload_dir, exist_ok=True)

    # 同城服务相关方法
    async def create_local_service(
        self, 
        db: Session, 
        service_data: LocalServiceCreate, 
        user_id: int
    ) -> LocalServiceResponse:
        """创建同城服务"""
        db_service = LocalServicePost(
            user_id=user_id,
            **service_data.dict()
        )
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        
        return await self._format_local_service_response(db, db_service, user_id)

    async def get_local_services(
        self,
        db: Session,
        service_type: Optional[str] = None,
        city: Optional[str] = None,
        district: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取同城服务列表"""
        query = db.query(LocalServicePost).filter(LocalServicePost.status == 1)
        
        if service_type:
            query = query.filter(LocalServicePost.service_type == service_type)
        if city:
            query = query.filter(LocalServicePost.city == city)
        if district:
            query = query.filter(LocalServicePost.district == district)
        if keyword:
            query = query.filter(
                or_(
                    LocalServicePost.title.contains(keyword),
                    LocalServicePost.description.contains(keyword)
                )
            )
        
        # 总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        services = query.order_by(desc(LocalServicePost.created_at)).offset(offset).limit(page_size).all()
        
        # 格式化响应
        items = []
        for service in services:
            formatted_service = await self._format_local_service_response(db, service, user_id)
            items.append(formatted_service)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_local_service_by_id(
        self, 
        db: Session, 
        service_id: int, 
        user_id: Optional[int] = None
    ) -> Optional[LocalServiceResponse]:
        """获取单个同城服务详情"""
        service = db.query(LocalServicePost).filter(
            LocalServicePost.id == service_id,
            LocalServicePost.status == 1
        ).first()
        
        if not service:
            return None
        
        # 增加浏览次数
        service.view_count += 1
        db.commit()
        
        return await self._format_local_service_response(db, service, user_id)

    async def update_local_service(
        self,
        db: Session,
        service_id: int,
        service_data: LocalServiceUpdate,
        user_id: int
    ) -> Optional[LocalServiceResponse]:
        """更新同城服务"""
        service = db.query(LocalService).filter(
            LocalService.id == service_id,
            LocalService.user_id == user_id
        ).first()
        
        if not service:
            return None
        
        update_data = service_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service, field, value)
        
        db.commit()
        db.refresh(service)
        
        return await self._format_local_service_response(db, service, user_id)

    async def delete_local_service(self, db: Session, service_id: int, user_id: int) -> bool:
        """删除同城服务"""
        service = db.query(LocalService).filter(
            LocalService.id == service_id,
            LocalService.user_id == user_id
        ).first()
        
        if not service:
            return False
        
        service.status = 3  # 标记为删除
        db.commit()
        return True

    # 宠物交流相关方法
    async def create_pet_social_post(
        self,
        db: Session,
        post_data: PetSocialPostCreate,
        user_id: int
    ) -> PetSocialPostResponse:
        """创建宠物交流帖子"""
        db_post = PetSocialPost(
            user_id=user_id,
            **post_data.dict()
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        return await self._format_pet_social_post_response(db, db_post, user_id)

    async def get_pet_social_posts(
        self,
        db: Session,
        category: Optional[str] = None,
        city: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取宠物交流帖子列表"""
        query = db.query(PetSocialPost).filter(PetSocialPost.status == 1)
        
        if category:
            query = query.filter(PetSocialPost.category == category)
        if city:
            query = query.filter(PetSocialPost.city == city)
        if keyword:
            query = query.filter(
                or_(
                    PetSocialPost.title.contains(keyword),
                    PetSocialPost.content.contains(keyword)
                )
            )
        
        # 总数
        total = query.count()
        
        # 分页，置顶帖子优先
        offset = (page - 1) * page_size
        posts = query.order_by(
            desc(PetSocialPost.is_top),
            desc(PetSocialPost.created_at)
        ).offset(offset).limit(page_size).all()
        
        # 格式化响应
        items = []
        for post in posts:
            formatted_post = await self._format_pet_social_post_response(db, post, user_id)
            items.append(formatted_post)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_pet_social_post_by_id(
        self,
        db: Session,
        post_id: int,
        user_id: Optional[int] = None
    ) -> Optional[PetSocialPostResponse]:
        """获取单个宠物交流帖子详情"""
        post = db.query(PetSocialPost).filter(
            PetSocialPost.id == post_id,
            PetSocialPost.status == 1
        ).first()
        
        if not post:
            return None
        
        # 增加浏览次数
        post.view_count += 1
        db.commit()
        
        return await self._format_pet_social_post_response(db, post, user_id)

    # 评论相关方法
    async def create_local_service_comment(
        self,
        db: Session,
        service_id: int,
        comment_data: LocalServiceCommentCreate,
        user_id: int
    ) -> LocalServiceCommentResponse:
        """创建同城服务评论"""
        # 检查服务是否存在
        service = db.query(LocalService).filter(LocalService.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="服务不存在")
        
        db_comment = LocalServiceComment(
            service_id=service_id,
            user_id=user_id,
            **comment_data.dict()
        )
        db.add(db_comment)
        
        # 更新服务评论数
        service.comment_count += 1
        
        db.commit()
        db.refresh(db_comment)
        
        return await self._format_local_service_comment_response(db, db_comment)

    async def get_local_service_comments(
        self,
        db: Session,
        service_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取同城服务评论列表"""
        query = db.query(LocalServiceComment).filter(
            LocalServiceComment.service_id == service_id,
            LocalServiceComment.status == 1,
            LocalServiceComment.parent_id.is_(None)  # 只获取顶级评论
        )
        
        total = query.count()
        offset = (page - 1) * page_size
        comments = query.order_by(desc(LocalServiceComment.created_at)).offset(offset).limit(page_size).all()
        
        # 格式化响应，包含回复
        items = []
        for comment in comments:
            formatted_comment = await self._format_local_service_comment_response(db, comment, include_replies=True)
            items.append(formatted_comment)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    # 点赞相关方法
    async def toggle_local_service_like(self, db: Session, service_id: int, user_id: int) -> Dict[str, Any]:
        """切换同城服务点赞状态"""
        service = db.query(LocalService).filter(LocalService.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="服务不存在")
        
        existing_like = db.query(LocalServiceLike).filter(
            LocalServiceLike.service_id == service_id,
            LocalServiceLike.user_id == user_id
        ).first()
        
        if existing_like:
            # 取消点赞
            db.delete(existing_like)
            service.like_count = max(0, service.like_count - 1)
            is_liked = False
        else:
            # 添加点赞
            new_like = LocalServiceLike(service_id=service_id, user_id=user_id)
            db.add(new_like)
            service.like_count += 1
            is_liked = True
        
        db.commit()
        
        return {
            "is_liked": is_liked,
            "like_count": service.like_count
        }

    # 图片上传
    async def upload_image(self, file: UploadFile, user_id: int) -> Dict[str, Any]:
        """上传图片"""
        # 检查文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="只支持JPG、PNG、WEBP格式的图片")
        
        # 检查文件大小（5MB）
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="图片大小不能超过5MB")
        
        # 生成文件名
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(self.upload_dir, filename)
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(content)
        
        file_url = f"/static/uploads/local_services/{filename}"
        
        return {
            "url": file_url,
            "filename": filename,
            "size": len(content)
        }

    # 获取服务类型列表
    async def get_service_types(self) -> ServiceTypesResponse:
        """获取服务类型列表"""
        service_types = [
            ServiceType(
                key="pet_social",
                name="宠物交流",
                description="分享宠物心得，交流养宠经验"
            ),
            ServiceType(
                key="local_store",
                name="本地宠店",
                description="发现附近优质宠物店"
            ),
            ServiceType(
                key="aquarium_design",
                name="鱼缸造景",
                description="专业水族造景设计服务"
            ),
            ServiceType(
                key="door_service",
                name="上门服务",
                description="专业宠物上门服务"
            ),
            ServiceType(
                key="breeding",
                name="宠物配种",
                description="寻找理想的宠物伴侣"
            ),
            ServiceType(
                key="pickup",
                name="同城快取",
                description="快速自取服务"
            ),
            ServiceType(
                key="valuation",
                name="宠物估价",
                description="专业宠物估价服务"
            ),
            ServiceType(
                key="nearby",
                name="附近",
                description="发现身边好物"
            )
        ]
        
        return ServiceTypesResponse(items=service_types)

    # 私有方法：格式化响应
    async def _format_local_service_response(
        self, 
        db: Session, 
        service: LocalService, 
        user_id: Optional[int] = None
    ) -> LocalServiceResponse:
        """格式化同城服务响应"""
        # 获取用户信息
        user_info = None
        if service.user:
            user_info = {
                "id": service.user.id,
                "nickname": service.user.nickname or service.user.username,
                "avatar": service.user.avatar,
                "phone": service.user.phone
            }
        
        # 检查是否已点赞/收藏（需要登录用户）
        is_liked = None
        is_favorited = None
        if user_id:
            is_liked = db.query(LocalServiceLike).filter(
                LocalServiceLike.service_id == service.id,
                LocalServiceLike.user_id == user_id
            ).first() is not None
            
            is_favorited = db.query(LocalServiceFavorite).filter(
                LocalServiceFavorite.service_id == service.id,
                LocalServiceFavorite.user_id == user_id
            ).first() is not None
        
        return LocalServiceResponse(
            id=service.id,
            user_id=service.user_id,
            service_type=service.service_type,
            title=service.title,
            description=service.description,
            content=service.content,
            province=service.province,
            city=service.city,
            district=service.district,
            address=service.address,
            latitude=service.latitude,
            longitude=service.longitude,
            price=service.price,
            price_unit=service.price_unit,
            contact_name=service.contact_name,
            contact_phone=service.contact_phone,
            contact_wechat=service.contact_wechat,
            extra_data=service.extra_data,
            images=service.images,
            tags=service.tags,
            status=service.status,
            is_featured=service.is_featured,
            view_count=service.view_count,
            like_count=service.like_count,
            comment_count=service.comment_count,
            created_at=service.created_at,
            updated_at=service.updated_at,
            user_info=user_info,
            is_liked=is_liked,
            is_favorited=is_favorited
        )

    async def _format_pet_social_post_response(
        self,
        db: Session,
        post: PetSocialPost,
        user_id: Optional[int] = None
    ) -> PetSocialPostResponse:
        """格式化宠物交流帖子响应"""
        # 获取用户信息
        user_info = None
        if post.user:
            user_info = {
                "id": post.user.id,
                "nickname": post.user.nickname or post.user.username,
                "avatar": post.user.avatar
            }
        
        # 检查是否已点赞
        is_liked = None
        if user_id:
            # 这里需要创建对应的点赞表，暂时返回False
            is_liked = False
        
        return PetSocialPostResponse(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            images=post.images,
            pet_type=post.pet_type,
            pet_breed=post.pet_breed,
            pet_age=post.pet_age,
            pet_gender=post.pet_gender,
            city=post.city,
            district=post.district,
            category=post.category,
            tags=post.tags,
            view_count=post.view_count,
            like_count=post.like_count,
            comment_count=post.comment_count,
            share_count=post.share_count,
            status=post.status,
            is_top=post.is_top,
            is_featured=post.is_featured,
            created_at=post.created_at,
            updated_at=post.updated_at,
            user_info=user_info,
            is_liked=is_liked
        )

    async def _format_local_service_comment_response(
        self,
        db: Session,
        comment: LocalServiceComment,
        include_replies: bool = False
    ) -> LocalServiceCommentResponse:
        """格式化同城服务评论响应"""
        # 获取用户信息
        user_info = None
        if comment.user:
            user_info = {
                "id": comment.user.id,
                "nickname": comment.user.nickname or comment.user.username,
                "avatar": comment.user.avatar
            }
        
        # 获取回复
        replies = None
        if include_replies:
            reply_comments = db.query(LocalServiceComment).filter(
                LocalServiceComment.parent_id == comment.id,
                LocalServiceComment.status == 1
            ).order_by(LocalServiceComment.created_at).all()
            
            replies = []
            for reply in reply_comments:
                reply_formatted = await self._format_local_service_comment_response(db, reply, False)
                replies.append(reply_formatted)
        
        return LocalServiceCommentResponse(
            id=comment.id,
            service_id=comment.service_id,
            user_id=comment.user_id,
            parent_id=comment.parent_id,
            content=comment.content,
            images=comment.images,
            status=comment.status,
            like_count=comment.like_count,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            user_info=user_info,
            replies=replies
        )
