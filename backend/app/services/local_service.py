from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from ..models.local_service import (
    PetSocialPost, PetSocialComment, PetSocialLike, PetBreedingInfo, LocalPetStore,
    AquariumDesignService, LocalPickupService, DoorService,
    PetValuationService, RecyclingItem, RecyclingOrder, PartnerApplication, 
    NearbyItem, ServiceStatus
)
from ..models.user import User
from ..schemas.local_service import (
    PetSocialPostCreate, PetSocialPostUpdate, PetSocialPostResponse, PetSocialPostListResponse,
    PetSocialCommentCreate, PetSocialCommentResponse,
    PetBreedingInfoCreate, PetBreedingInfoUpdate, PetBreedingInfoResponse, PetBreedingInfoListResponse,
    LocalPetStoreCreate, LocalPetStoreUpdate, LocalPetStoreResponse, LocalPetStoreListResponse,
    AquariumDesignServiceCreate, AquariumDesignServiceUpdate, AquariumDesignServiceResponse, AquariumDesignServiceListResponse,
    DoorServiceCreate, DoorServiceUpdate, DoorServiceResponse, DoorServiceListResponse,
    PetValuationServiceCreate, PetValuationServiceResponse, PetValuationServiceListResponse,
    NearbyItemCreate, NearbyItemUpdate, NearbyItemResponse, NearbyItemListResponse,
    ServiceStatsResponse
)

class LocalService:
    
    # 宠物交流相关方法
    async def create_social_post(self, db: Session, post_data: PetSocialPostCreate, user_id: int) -> PetSocialPostResponse:
        """创建宠物交流帖子"""
        post = PetSocialPost(
            user_id=user_id,
            title=post_data.title,
            content=post_data.content,
            images=json.dumps(post_data.images) if post_data.images else None,
            pet_type=post_data.pet_type,
            location=post_data.location
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        
        return await self._build_social_post_response(db, post)
    
    async def get_social_posts(
        self, 
        db: Session, 
        page: int = 1, 
        page_size: int = 20,
        pet_type: Optional[str] = None,
        location: Optional[str] = None
    ) -> PetSocialPostListResponse:
        """获取宠物交流帖子列表"""
        query = db.query(PetSocialPost).filter(PetSocialPost.status == ServiceStatus.ACTIVE)
        
        if pet_type:
            query = query.filter(PetSocialPost.pet_type == pet_type)
        if location:
            query = query.filter(PetSocialPost.location.contains(location))
        
        # 置顶帖子优先，然后按创建时间倒序
        query = query.order_by(desc(PetSocialPost.is_top), desc(PetSocialPost.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        posts = query.offset(offset).limit(page_size).all()
        
        items = []
        for post in posts:
            items.append(await self._build_social_post_response(db, post))
        
        return PetSocialPostListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def get_social_post_detail(self, db: Session, post_id: int) -> Optional[PetSocialPostResponse]:
        """获取帖子详情并增加浏览量"""
        post = db.query(PetSocialPost).filter(PetSocialPost.id == post_id).first()
        if not post:
            return None
        
        # 增加浏览量
        post.view_count += 1
        db.commit()
        
        return await self._build_social_post_response(db, post)
    
    async def create_social_comment(self, db: Session, post_id: int, comment_data: PetSocialCommentCreate, user_id: int) -> PetSocialCommentResponse:
        """创建评论"""
        # 检查帖子是否存在
        post = db.query(PetSocialPost).filter(PetSocialPost.id == post_id).first()
        if not post:
            raise ValueError("帖子不存在")
        
        comment = PetSocialComment(
            post_id=post_id,
            user_id=user_id,
            content=comment_data.content,
            parent_id=comment_data.parent_id
        )
        db.add(comment)
        
        # 更新帖子评论数
        post.comment_count += 1
        
        db.commit()
        db.refresh(comment)
        
        return await self._build_social_comment_response(db, comment)
    
    async def toggle_post_like(self, db: Session, post_id: int, user_id: int) -> Dict[str, Any]:
        """点赞/取消点赞帖子"""
        # 检查帖子是否存在
        post = db.query(PetSocialPost).filter(PetSocialPost.id == post_id).first()
        if not post:
            raise ValueError("帖子不存在")
        
        # 检查用户是否已点赞
        existing_like = db.query(PetSocialLike).filter(
            and_(PetSocialLike.post_id == post_id, PetSocialLike.user_id == user_id)
        ).first()
        
        if existing_like:
            # 取消点赞
            db.delete(existing_like)
            post.like_count = max(0, post.like_count - 1)
            liked = False
        else:
            # 添加点赞
            like = PetSocialLike(post_id=post_id, user_id=user_id)
            db.add(like)
            post.like_count += 1
            liked = True
        
        db.commit()
        
        return {
            "liked": liked,
            "like_count": post.like_count
        }
    
    async def search_social_posts(
        self, 
        db: Session, 
        query: str,
        page: int = 1, 
        page_size: int = 20,
        pet_type: Optional[str] = None,
        location: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """搜索宠物社交帖子"""
        # 构建查询
        db_query = db.query(PetSocialPost).filter(PetSocialPost.status == ServiceStatus.ACTIVE)
        
        # 搜索条件
        search_filter = or_(
            PetSocialPost.title.contains(query),
            PetSocialPost.content.contains(query)
        )
        db_query = db_query.filter(search_filter)
        
        # 筛选条件
        if pet_type:
            db_query = db_query.filter(PetSocialPost.pet_type == pet_type)
        if location:
            db_query = db_query.filter(PetSocialPost.location.contains(location))
        
        # 排序
        if sort_by == "like_count":
            sort_column = PetSocialPost.like_count
        elif sort_by == "comment_count":
            sort_column = PetSocialPost.comment_count
        elif sort_by == "view_count":
            sort_column = PetSocialPost.view_count
        else:
            sort_column = PetSocialPost.created_at
        
        if sort_order == "asc":
            db_query = db_query.order_by(sort_column.asc())
        else:
            db_query = db_query.order_by(sort_column.desc())
        
        total = db_query.count()
        offset = (page - 1) * page_size
        posts = db_query.offset(offset).limit(page_size).all()
        
        items = []
        for post in posts:
            items.append(await self._build_social_post_response(db, post))
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "query": query,
            "filters": {
                "pet_type": pet_type,
                "location": location,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
    
    async def get_post_likes(self, db: Session, post_id: int, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取帖子点赞列表"""
        # 检查帖子是否存在
        post = db.query(PetSocialPost).filter(PetSocialPost.id == post_id).first()
        if not post:
            raise ValueError("帖子不存在")
        
        # 查询点赞列表
        query = db.query(PetSocialLike).filter(PetSocialLike.post_id == post_id)
        query = query.order_by(desc(PetSocialLike.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        likes = query.offset(offset).limit(page_size).all()
        
        # 获取用户信息
        items = []
        for like in likes:
            user = db.query(User).filter(User.id == like.user_id).first()
            items.append({
                "id": like.id,
                "user_id": like.user_id,
                "user_nickname": user.nickname if user else "未知用户",
                "user_avatar": user.avatar if user else None,
                "created_at": like.created_at
            })
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    # 宠物配种相关方法
    async def create_breeding_info(self, db: Session, breeding_data: PetBreedingInfoCreate, user_id: int) -> PetBreedingInfoResponse:
        """创建宠物配种信息"""
        breeding = PetBreedingInfo(
            user_id=user_id,
            pet_name=breeding_data.pet_name,
            pet_type=breeding_data.pet_type,
            breed=breeding_data.breed,
            gender=breeding_data.gender,
            age=breeding_data.age,
            weight=breeding_data.weight,
            health_status=breeding_data.health_status,
            vaccination_status=breeding_data.vaccination_status,
            images=json.dumps(breeding_data.images) if breeding_data.images else None,
            description=breeding_data.description,
            requirements=breeding_data.requirements,
            location=breeding_data.location,
            contact_phone=breeding_data.contact_phone,
            contact_wechat=breeding_data.contact_wechat,
            price=breeding_data.price
        )
        db.add(breeding)
        db.commit()
        db.refresh(breeding)
        
        return await self._build_breeding_info_response(db, breeding)
    
    async def get_breeding_info_list(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        pet_type: Optional[str] = None,
        breed: Optional[str] = None,
        gender: Optional[str] = None,
        location: Optional[str] = None
    ) -> PetBreedingInfoListResponse:
        """获取宠物配种信息列表"""
        query = db.query(PetBreedingInfo).filter(
            and_(
                PetBreedingInfo.status == ServiceStatus.ACTIVE,
                PetBreedingInfo.is_available == True
            )
        )
        
        if pet_type:
            query = query.filter(PetBreedingInfo.pet_type == pet_type)
        if breed:
            query = query.filter(PetBreedingInfo.breed.contains(breed))
        if gender:
            query = query.filter(PetBreedingInfo.gender == gender)
        if location:
            query = query.filter(PetBreedingInfo.location.contains(location))
        
        query = query.order_by(desc(PetBreedingInfo.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        breeding_infos = query.offset(offset).limit(page_size).all()
        
        items = []
        for breeding in breeding_infos:
            items.append(await self._build_breeding_info_response(db, breeding))
        
        return PetBreedingInfoListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    # 本地宠店相关方法
    async def get_local_pet_stores(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        location: Optional[str] = None,
        service_type: Optional[str] = None
    ) -> LocalPetStoreListResponse:
        """获取本地宠店列表"""
        query = db.query(LocalPetStore).filter(LocalPetStore.status == ServiceStatus.ACTIVE)
        
        if location:
            query = query.filter(LocalPetStore.address.contains(location))
        if service_type:
            query = query.filter(LocalPetStore.services.contains(service_type))
        
        # 认证店铺优先，然后按评分倒序
        query = query.order_by(desc(LocalPetStore.is_verified), desc(LocalPetStore.rating))
        
        total = query.count()
        offset = (page - 1) * page_size
        stores = query.offset(offset).limit(page_size).all()
        
        items = []
        for store in stores:
            items.append(await self._build_pet_store_response(store))
        
        return LocalPetStoreListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    # 鱼缸造景相关方法
    async def create_aquarium_design_service(self, db: Session, design_data: AquariumDesignServiceCreate, user_id: int) -> AquariumDesignServiceResponse:
        """创建鱼缸造景服务"""
        design_service = AquariumDesignService(
            provider_id=user_id,
            title=design_data.title,
            description=design_data.description,
            tank_sizes=json.dumps(design_data.tank_sizes) if design_data.tank_sizes else None,
            design_styles=json.dumps(design_data.design_styles) if design_data.design_styles else None,
            price_range=design_data.price_range,
            portfolio_images=json.dumps(design_data.portfolio_images) if design_data.portfolio_images else None,
            location=design_data.location,
            contact_phone=design_data.contact_phone,
            contact_wechat=design_data.contact_wechat
        )
        db.add(design_service)
        db.commit()
        db.refresh(design_service)
        
        return await self._build_aquarium_design_response(db, design_service)
    
    async def get_aquarium_design_services(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        location: Optional[str] = None,
        style: Optional[str] = None
    ) -> AquariumDesignServiceListResponse:
        """获取鱼缸造景服务列表"""
        query = db.query(AquariumDesignService).filter(
            and_(
                AquariumDesignService.status == ServiceStatus.ACTIVE,
                AquariumDesignService.is_available == True
            )
        )
        
        if location:
            query = query.filter(AquariumDesignService.location.contains(location))
        if style:
            query = query.filter(AquariumDesignService.design_styles.contains(style))
        
        query = query.order_by(desc(AquariumDesignService.rating), desc(AquariumDesignService.order_count))
        
        total = query.count()
        offset = (page - 1) * page_size
        services = query.offset(offset).limit(page_size).all()
        
        items = []
        for service in services:
            items.append(await self._build_aquarium_design_response(db, service))
        
        return AquariumDesignServiceListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    # 上门服务相关方法
    async def create_door_service(self, db: Session, service_data: DoorServiceCreate, user_id: int) -> DoorServiceResponse:
        """创建上门服务"""
        door_service = DoorService(
            provider_id=user_id,
            service_name=service_data.service_name,
            service_type=service_data.service_type,
            description=service_data.description,
            service_area=service_data.service_area,
            price=service_data.price,
            duration=service_data.duration,
            equipment_needed=service_data.equipment_needed,
            images=json.dumps(service_data.images) if service_data.images else None,
            contact_phone=service_data.contact_phone
        )
        db.add(door_service)
        db.commit()
        db.refresh(door_service)
        
        return await self._build_door_service_response(db, door_service)
    
    async def get_door_services(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        service_type: Optional[str] = None,
        location: Optional[str] = None
    ) -> DoorServiceListResponse:
        """获取上门服务列表"""
        query = db.query(DoorService).filter(
            and_(
                DoorService.status == ServiceStatus.ACTIVE,
                DoorService.is_available == True
            )
        )
        
        if service_type:
            query = query.filter(DoorService.service_type == service_type)
        if location:
            query = query.filter(DoorService.service_area.contains(location))
        
        query = query.order_by(desc(DoorService.rating), desc(DoorService.order_count))
        
        total = query.count()
        offset = (page - 1) * page_size
        services = query.offset(offset).limit(page_size).all()
        
        items = []
        for service in services:
            items.append(await self._build_door_service_response(db, service))
        
        return DoorServiceListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    # 宠物估价相关方法
    async def create_pet_valuation(self, db: Session, valuation_data: PetValuationServiceCreate, user_id: int) -> PetValuationServiceResponse:
        """创建宠物估价申请"""
        valuation = PetValuationService(
            user_id=user_id,
            pet_type=valuation_data.pet_type,
            breed=valuation_data.breed,
            age=valuation_data.age,
            gender=valuation_data.gender,
            weight=valuation_data.weight,
            health_status=valuation_data.health_status,
            special_features=valuation_data.special_features,
            images=json.dumps(valuation_data.images)
        )
        db.add(valuation)
        db.commit()
        db.refresh(valuation)
        
        return await self._build_pet_valuation_response(db, valuation)
    
    # 附近发现相关方法
    async def create_nearby_item(self, db: Session, item_data: NearbyItemCreate, user_id: int) -> NearbyItemResponse:
        """创建附近发现项目"""
        nearby_item = NearbyItem(
            user_id=user_id,
            title=item_data.title,
            description=item_data.description,
            category=item_data.category,
            price=item_data.price,
            images=json.dumps(item_data.images) if item_data.images else None,
            location=item_data.location,
            latitude=item_data.latitude,
            longitude=item_data.longitude,
            contact_phone=item_data.contact_phone,
            contact_wechat=item_data.contact_wechat
        )
        db.add(nearby_item)
        db.commit()
        db.refresh(nearby_item)
        
        return await self._build_nearby_item_response(db, nearby_item)
    
    async def get_nearby_items(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[float] = None
    ) -> NearbyItemListResponse:
        """获取附近发现列表"""
        query = db.query(NearbyItem).filter(NearbyItem.status == ServiceStatus.ACTIVE)
        
        if category:
            query = query.filter(NearbyItem.category == category)
        if location:
            query = query.filter(NearbyItem.location.contains(location))
        
        # 如果提供了坐标和半径，进行地理位置筛选
        if latitude and longitude and radius:
            # 简单的距离计算（实际应用中可能需要更精确的地理计算）
            query = query.filter(
                and_(
                    NearbyItem.latitude.isnot(None),
                    NearbyItem.longitude.isnot(None),
                    func.sqrt(
                        func.pow(NearbyItem.latitude - latitude, 2) +
                        func.pow(NearbyItem.longitude - longitude, 2)
                    ) <= radius
                )
            )
        
        # 置顶优先，然后按创建时间倒序
        query = query.order_by(desc(NearbyItem.is_top), desc(NearbyItem.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        
        response_items = []
        for item in items:
            response_items.append(await self._build_nearby_item_response(db, item))
        
        return NearbyItemListResponse(
            items=response_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    # 统计相关方法
    async def get_service_stats(self, db: Session) -> ServiceStatsResponse:
        """获取服务统计数据"""
        total_posts = db.query(PetSocialPost).filter(PetSocialPost.status == ServiceStatus.ACTIVE).count()
        total_breeding = db.query(PetBreedingInfo).filter(PetBreedingInfo.status == ServiceStatus.ACTIVE).count()
        total_stores = db.query(LocalPetStore).filter(LocalPetStore.status == ServiceStatus.ACTIVE).count()
        total_designs = db.query(AquariumDesignService).filter(AquariumDesignService.status == ServiceStatus.ACTIVE).count()
        total_door_services = db.query(DoorService).filter(DoorService.status == ServiceStatus.ACTIVE).count()
        total_valuations = db.query(PetValuationService).count()
        total_nearby_items = db.query(NearbyItem).filter(NearbyItem.status == ServiceStatus.ACTIVE).count()
        
        return ServiceStatsResponse(
            total_posts=total_posts,
            total_breeding=total_breeding,
            total_stores=total_stores,
            total_designs=total_designs,
            total_door_services=total_door_services,
            total_valuations=total_valuations,
            total_nearby_items=total_nearby_items
        )
    
    # 私有辅助方法
    async def _build_social_post_response(self, db: Session, post: PetSocialPost) -> PetSocialPostResponse:
        """构建社交帖子响应"""
        user = db.query(User).filter(User.id == post.user_id).first()
        
        return PetSocialPostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            images=json.loads(post.images) if post.images else None,
            pet_type=post.pet_type,
            location=post.location,
            view_count=post.view_count,
            like_count=post.like_count,
            comment_count=post.comment_count,
            is_top=post.is_top,
            status=post.status,
            user_id=post.user_id,
            user_nickname=user.nickname if user else None,
            user_avatar=user.avatar_url if user else None,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
    
    async def _build_social_comment_response(self, db: Session, comment: PetSocialComment) -> PetSocialCommentResponse:
        """构建社交评论响应"""
        user = db.query(User).filter(User.id == comment.user_id).first()
        
        # 获取回复
        replies = db.query(PetSocialComment).filter(PetSocialComment.parent_id == comment.id).all()
        reply_responses = []
        for reply in replies:
            reply_responses.append(await self._build_social_comment_response(db, reply))
        
        return PetSocialCommentResponse(
            id=comment.id,
            content=comment.content,
            parent_id=comment.parent_id,
            user_id=comment.user_id,
            user_nickname=user.nickname if user else None,
            user_avatar=user.avatar_url if user else None,
            created_at=comment.created_at,
            replies=reply_responses
        )
    
    async def _build_breeding_info_response(self, db: Session, breeding: PetBreedingInfo) -> PetBreedingInfoResponse:
        """构建配种信息响应"""
        user = db.query(User).filter(User.id == breeding.user_id).first()
        
        return PetBreedingInfoResponse(
            id=breeding.id,
            pet_name=breeding.pet_name,
            pet_type=breeding.pet_type,
            breed=breeding.breed,
            gender=breeding.gender,
            age=breeding.age,
            weight=breeding.weight,
            health_status=breeding.health_status,
            vaccination_status=breeding.vaccination_status,
            images=json.loads(breeding.images) if breeding.images else None,
            description=breeding.description,
            requirements=breeding.requirements,
            location=breeding.location,
            contact_phone=breeding.contact_phone,
            contact_wechat=breeding.contact_wechat,
            price=breeding.price,
            is_available=breeding.is_available,
            status=breeding.status,
            user_id=breeding.user_id,
            user_nickname=user.nickname if user else None,
            user_avatar=user.avatar_url if user else None,
            created_at=breeding.created_at,
            updated_at=breeding.updated_at
        )
    
    async def _build_pet_store_response(self, store: LocalPetStore) -> LocalPetStoreResponse:
        """构建宠店响应"""
        return LocalPetStoreResponse(
            id=store.id,
            name=store.name,
            owner_name=store.owner_name,
            phone=store.phone,
            address=store.address,
            latitude=store.latitude,
            longitude=store.longitude,
            business_hours=store.business_hours,
            services=json.loads(store.services) if store.services else None,
            images=json.loads(store.images) if store.images else None,
            description=store.description,
            rating=store.rating,
            review_count=store.review_count,
            is_verified=store.is_verified,
            status=store.status,
            created_at=store.created_at,
            updated_at=store.updated_at
        )
    
    async def _build_aquarium_design_response(self, db: Session, design: AquariumDesignService) -> AquariumDesignServiceResponse:
        """构建鱼缸造景响应"""
        user = db.query(User).filter(User.id == design.provider_id).first()
        
        return AquariumDesignServiceResponse(
            id=design.id,
            title=design.title,
            description=design.description,
            tank_sizes=json.loads(design.tank_sizes) if design.tank_sizes else None,
            design_styles=json.loads(design.design_styles) if design.design_styles else None,
            price_range=design.price_range,
            portfolio_images=json.loads(design.portfolio_images) if design.portfolio_images else None,
            location=design.location,
            contact_phone=design.contact_phone,
            contact_wechat=design.contact_wechat,
            rating=design.rating,
            order_count=design.order_count,
            is_available=design.is_available,
            status=design.status,
            provider_id=design.provider_id,
            provider_nickname=user.nickname if user else None,
            provider_avatar=user.avatar_url if user else None,
            created_at=design.created_at,
            updated_at=design.updated_at
        )
    
    async def _build_door_service_response(self, db: Session, service: DoorService) -> DoorServiceResponse:
        """构建上门服务响应"""
        user = db.query(User).filter(User.id == service.provider_id).first()
        
        return DoorServiceResponse(
            id=service.id,
            service_name=service.service_name,
            service_type=service.service_type,
            description=service.description,
            service_area=service.service_area,
            price=service.price,
            duration=service.duration,
            equipment_needed=service.equipment_needed,
            images=json.loads(service.images) if service.images else None,
            contact_phone=service.contact_phone,
            rating=service.rating,
            order_count=service.order_count,
            is_available=service.is_available,
            status=service.status,
            provider_id=service.provider_id,
            provider_nickname=user.nickname if user else None,
            provider_avatar=user.avatar_url if user else None,
            created_at=service.created_at,
            updated_at=service.updated_at
        )
    
    async def _build_pet_valuation_response(self, db: Session, valuation: PetValuationService) -> PetValuationServiceResponse:
        """构建宠物估价响应"""
        user = db.query(User).filter(User.id == valuation.user_id).first()
        valuator = db.query(User).filter(User.id == valuation.valuator_id).first() if valuation.valuator_id else None
        
        return PetValuationServiceResponse(
            id=valuation.id,
            pet_type=valuation.pet_type,
            breed=valuation.breed,
            age=valuation.age,
            gender=valuation.gender,
            weight=valuation.weight,
            health_status=valuation.health_status,
            special_features=valuation.special_features,
            images=json.loads(valuation.images),
            estimated_value=valuation.estimated_value,
            valuator_id=valuation.valuator_id,
            valuator_nickname=valuator.nickname if valuator else None,
            valuation_notes=valuation.valuation_notes,
            status=valuation.status,
            user_id=valuation.user_id,
            user_nickname=user.nickname if user else None,
            created_at=valuation.created_at,
            updated_at=valuation.updated_at
        )
    
    async def _build_nearby_item_response(self, db: Session, item: NearbyItem) -> NearbyItemResponse:
        """构建附近发现响应"""
        user = db.query(User).filter(User.id == item.user_id).first()
        
        return NearbyItemResponse(
            id=item.id,
            title=item.title,
            description=item.description,
            category=item.category,
            price=item.price,
            images=json.loads(item.images) if item.images else None,
            location=item.location,
            latitude=item.latitude,
            longitude=item.longitude,
            contact_phone=item.contact_phone,
            contact_wechat=item.contact_wechat,
            view_count=item.view_count,
            like_count=item.like_count,
            is_top=item.is_top,
            status=item.status,
            user_id=item.user_id,
            user_nickname=user.nickname if user else None,
            user_avatar=user.avatar_url if user else None,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
    
    # ==================== 回收查询相关方法 ====================
    
    async def create_recycling_item(
        self, 
        db: Session, 
        item_data: Dict[str, Any], 
        user_id: int
    ) -> Dict[str, Any]:
        """创建回收物品"""
        recycling_item = RecyclingItem(
            user_id=user_id,
            name=item_data.get('name'),
            category=item_data.get('category'),
            original_price=item_data.get('original_price'),
            recycling_price=item_data.get('recycling_price'),
            condition=item_data.get('condition'),
            description=item_data.get('description'),
            images=json.dumps(item_data.get('images', [])),
            location=item_data.get('location'),
            contact_phone=item_data.get('contact_phone'),
            contact_wechat=item_data.get('contact_wechat')
        )
        
        db.add(recycling_item)
        db.commit()
        db.refresh(recycling_item)
        
        return await self._build_recycling_item_response(db, recycling_item)
    
    async def get_recycling_items(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """获取回收物品列表"""
        query = db.query(RecyclingItem)
        
        # 筛选条件
        if category and category != "全部":
            query = query.filter(RecyclingItem.category == category)
        if location:
            query = query.filter(RecyclingItem.location.contains(location))
        if status:
            query = query.filter(RecyclingItem.status == status)
        if keyword:
            search_filter = or_(
                RecyclingItem.name.contains(keyword),
                RecyclingItem.description.contains(keyword)
            )
            query = query.filter(search_filter)
        
        # 排序
        if sort_by == "recycling_price":
            sort_column = RecyclingItem.recycling_price
        elif sort_by == "original_price":
            sort_column = RecyclingItem.original_price
        elif sort_by == "view_count":
            sort_column = RecyclingItem.view_count
        else:
            sort_column = RecyclingItem.created_at
        
        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        
        results = []
        for item in items:
            results.append(await self._build_recycling_item_response(db, item))
        
        return {
            "items": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def get_recycling_item_detail(self, db: Session, item_id: int) -> Dict[str, Any]:
        """获取回收物品详情"""
        item = db.query(RecyclingItem).filter(RecyclingItem.id == item_id).first()
        if not item:
            raise ValueError("回收物品不存在")
        
        # 增加浏览次数
        item.view_count += 1
        db.commit()
        
        return await self._build_recycling_item_response(db, item)
    
    async def create_recycling_order(
        self,
        db: Session,
        order_data: Dict[str, Any],
        buyer_id: int
    ) -> Dict[str, Any]:
        """创建回收订单"""
        item_id = order_data.get('item_id')
        
        # 检查物品是否存在且可回收
        item = db.query(RecyclingItem).filter(RecyclingItem.id == item_id).first()
        if not item:
            raise ValueError("回收物品不存在")
        if item.status != "可回收":
            raise ValueError("该物品已不可回收")
        
        # 创建订单
        order = RecyclingOrder(
            item_id=item_id,
            buyer_id=buyer_id,
            seller_id=item.user_id,
            agreed_price=order_data.get('agreed_price'),
            pickup_address=order_data.get('pickup_address'),
            pickup_time=order_data.get('pickup_time'),
            notes=order_data.get('notes')
        )
        
        db.add(order)
        # 更新物品状态
        item.status = "已预订"
        
        db.commit()
        db.refresh(order)
        
        return await self._build_recycling_order_response(db, order)
    
    async def get_recycling_orders(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        order_type: str = "all"  # all, buy, sell
    ) -> Dict[str, Any]:
        """获取用户的回收订单"""
        query = db.query(RecyclingOrder)
        
        # 根据订单类型筛选
        if order_type == "buy":
            query = query.filter(RecyclingOrder.buyer_id == user_id)
        elif order_type == "sell":
            query = query.filter(RecyclingOrder.seller_id == user_id)
        else:
            query = query.filter(
                or_(RecyclingOrder.buyer_id == user_id, RecyclingOrder.seller_id == user_id)
            )
        
        if status:
            query = query.filter(RecyclingOrder.status == status)
        
        query = query.order_by(desc(RecyclingOrder.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        orders = query.offset(offset).limit(page_size).all()
        
        results = []
        for order in orders:
            results.append(await self._build_recycling_order_response(db, order))
        
        return {
            "items": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def _build_recycling_item_response(self, db: Session, item: RecyclingItem) -> Dict[str, Any]:
        """构建回收物品响应数据"""
        user = db.query(User).filter(User.id == item.user_id).first()
        
        return {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "original_price": item.original_price,
            "recycling_price": item.recycling_price,
            "condition": item.condition,
            "description": item.description,
            "images": json.loads(item.images) if item.images else [],
            "location": item.location,
            "contact_phone": item.contact_phone,
            "contact_wechat": item.contact_wechat,
            "status": item.status,
            "view_count": item.view_count,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "user_id": item.user_id,
            "user_nickname": user.nickname if user else "未知用户",
            "user_avatar": user.avatar if user else None
        }
    
    async def _build_recycling_order_response(self, db: Session, order: RecyclingOrder) -> Dict[str, Any]:
        """构建回收订单响应数据"""
        item = db.query(RecyclingItem).filter(RecyclingItem.id == order.item_id).first()
        buyer = db.query(User).filter(User.id == order.buyer_id).first()
        seller = db.query(User).filter(User.id == order.seller_id).first()
        
        return {
            "id": order.id,
            "item_id": order.item_id,
            "item_name": item.name if item else "未知物品",
            "item_images": json.loads(item.images) if item and item.images else [],
            "buyer_id": order.buyer_id,
            "buyer_nickname": buyer.nickname if buyer else "未知用户",
            "seller_id": order.seller_id,
            "seller_nickname": seller.nickname if seller else "未知用户",
            "agreed_price": order.agreed_price,
            "pickup_address": order.pickup_address,
            "pickup_time": order.pickup_time,
            "notes": order.notes,
            "status": order.status,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }
    
    # ==================== 合作方代理相关方法 ====================
    
    async def create_partner_application(
        self,
        db: Session,
        application_data: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """创建合作方代理申请"""
        # 检查用户是否已有待审核的申请
        existing_application = db.query(PartnerApplication).filter(
            and_(
                PartnerApplication.user_id == user_id,
                PartnerApplication.status == "待审核"
            )
        ).first()
        
        if existing_application:
            raise ValueError("您已有待审核的申请，请耐心等待审核结果")
        
        application = PartnerApplication(
            user_id=user_id,
            name=application_data.get('name'),
            phone=application_data.get('phone'),
            company=application_data.get('company'),
            address=application_data.get('address'),
            agent_type=application_data.get('agent_type'),
            remark=application_data.get('remark')
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        return await self._build_partner_application_response(db, application)
    
    async def get_partner_applications(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        agent_type: Optional[str] = None,
        keyword: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取合作方代理申请列表"""
        query = db.query(PartnerApplication)
        
        # 筛选条件
        if user_id:
            query = query.filter(PartnerApplication.user_id == user_id)
        if status:
            query = query.filter(PartnerApplication.status == status)
        if agent_type:
            query = query.filter(PartnerApplication.agent_type == agent_type)
        if keyword:
            search_filter = or_(
                PartnerApplication.name.contains(keyword),
                PartnerApplication.company.contains(keyword),
                PartnerApplication.phone.contains(keyword)
            )
            query = query.filter(search_filter)
        
        query = query.order_by(desc(PartnerApplication.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        applications = query.offset(offset).limit(page_size).all()
        
        results = []
        for app in applications:
            results.append(await self._build_partner_application_response(db, app))
        
        return {
            "items": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def get_partner_application_detail(
        self, 
        db: Session, 
        application_id: int
    ) -> Dict[str, Any]:
        """获取合作方代理申请详情"""
        application = db.query(PartnerApplication).filter(
            PartnerApplication.id == application_id
        ).first()
        
        if not application:
            raise ValueError("申请不存在")
        
        return await self._build_partner_application_response(db, application)
    
    async def review_partner_application(
        self,
        db: Session,
        application_id: int,
        reviewer_id: int,
        status: str,
        admin_remark: Optional[str] = None
    ) -> Dict[str, Any]:
        """审核合作方代理申请"""
        if status not in ["已通过", "已拒绝"]:
            raise ValueError("无效的审核状态")
        
        application = db.query(PartnerApplication).filter(
            PartnerApplication.id == application_id
        ).first()
        
        if not application:
            raise ValueError("申请不存在")
        
        if application.status != "待审核":
            raise ValueError("该申请已被审核")
        
        application.status = status
        application.admin_remark = admin_remark
        application.reviewed_by = reviewer_id
        application.reviewed_at = datetime.utcnow()
        
        db.commit()
        
        return await self._build_partner_application_response(db, application)
    
    async def get_user_partner_applications(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取用户的合作方代理申请"""
        return await self.get_partner_applications(
            db=db,
            page=page,
            page_size=page_size,
            user_id=user_id
        )
    
    async def _build_partner_application_response(
        self, 
        db: Session, 
        application: PartnerApplication
    ) -> Dict[str, Any]:
        """构建合作方代理申请响应数据"""
        user = db.query(User).filter(User.id == application.user_id).first()
        reviewer = None
        if application.reviewed_by:
            reviewer = db.query(User).filter(User.id == application.reviewed_by).first()
        
        return {
            "id": application.id,
            "name": application.name,
            "phone": application.phone,
            "company": application.company,
            "address": application.address,
            "agent_type": application.agent_type,
            "remark": application.remark,
            "status": application.status,
            "admin_remark": application.admin_remark,
            "reviewed_at": application.reviewed_at,
            "created_at": application.created_at,
            "updated_at": application.updated_at,
            "user_id": application.user_id,
            "user_nickname": user.nickname if user else "未知用户",
            "user_avatar": user.avatar if user else None,
            "reviewer_id": application.reviewed_by,
            "reviewer_nickname": reviewer.nickname if reviewer else None
        }

