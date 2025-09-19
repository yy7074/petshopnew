from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from ..models.local_service import (
    PetSocialPost, PetSocialComment, PetBreedingInfo, LocalPetStore,
    AquariumDesignService, LocalPickupService, DoorService,
    PetValuationService, NearbyItem, ServiceStatus
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

