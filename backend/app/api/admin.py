from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import Optional, List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import verify_token, get_current_user, verify_password, create_access_token
from app.models.user import User
from app.models.product import Product, Category, SpecialEvent, EventProduct
from app.models.order import Order
from app.models.store import Store
from app.models.message import Message
from app.schemas.admin import *

router = APIRouter()
security = HTTPBearer()

# 管理员认证依赖
async def get_admin_user(current_user: User = Depends(get_current_user)):
    """验证管理员权限"""
    if not current_user or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="管理员权限不足")
    return current_user

# 管理员登录
@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(credentials: AdminLoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    # 查找管理员用户
    admin = db.query(User).filter(
        and_(
            User.username == credentials.username,
            User.is_admin == True  # 假设有is_admin字段
        )
    ).first()
    
    if not admin or not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 生成token
    access_token = create_access_token(data={"sub": str(admin.id)})
    
    return AdminLoginResponse(
        access_token=access_token,
        token_type="bearer",
        admin_info=AdminInfo(
            id=admin.id,
            username=admin.username,
            email=admin.email
        )
    )

# 验证token
@router.get("/verify", response_model=TokenVerifyResponse)
async def verify_admin_token(admin: User = Depends(get_admin_user)):
    """验证管理员token"""
    return TokenVerifyResponse(
        valid=True,
        admin_info=AdminInfo(
            id=admin.id,
            username=admin.username,
            email=admin.email
        )
    )

# 仪表盘统计
@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """获取仪表盘统计数据"""
    today = datetime.now().date()
    
    # 用户总数
    total_users = db.query(func.count(User.id)).scalar()
    
    # 商品总数
    total_products = db.query(func.count(Product.id)).scalar()
    
    # 今日订单数
    today_orders = db.query(func.count(Order.id)).filter(
        func.date(Order.created_at) == today
    ).scalar()
    
    # 今日收入
    today_revenue = db.query(func.sum(Order.total_amount)).filter(
        and_(
            func.date(Order.created_at) == today,
            Order.payment_status == 2  # 已支付
        )
    ).scalar() or 0
    
    # 本月统计
    month_start = today.replace(day=1)
    month_users = db.query(func.count(User.id)).filter(
        User.created_at >= month_start
    ).scalar()
    
    month_revenue = db.query(func.sum(Order.total_amount)).filter(
        and_(
            Order.created_at >= month_start,
            Order.payment_status == 2
        )
    ).scalar() or 0
    
    return DashboardStats(
        total_users=total_users or 0,
        total_products=total_products or 0,
        today_orders=today_orders or 0,
        today_revenue=float(today_revenue),
        month_new_users=month_users or 0,
        month_revenue=float(month_revenue)
    )

# 用户管理
@router.get("/users", response_model=UserListResponse)
async def get_users(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None),
    search: Optional[str] = Query(None)
):
    """获取用户列表"""
    query = db.query(User)
    
    # 状态筛选
    if status is not None:
        query = query.filter(User.status == status)
    
    # 搜索筛选
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    # 分页
    total = query.count()
    users = query.offset((page - 1) * size).limit(size).all()
    
    return UserListResponse(
        users=[UserInfo.from_orm(user) for user in users],
        total=total,
        page=page,
        size=size
    )

# 商品管理
@router.get("/products", response_model=ProductListResponse)
async def get_products(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None)
):
    """获取商品列表"""
    query = db.query(Product)
    
    # 状态筛选
    if status is not None:
        query = query.filter(Product.status == status)
    
    # 分类筛选
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # 分页
    total = query.count()
    products = query.offset((page - 1) * size).limit(size).all()
    
    product_list = []
    for product in products:
        product_info = ProductInfo.from_orm(product)
        # 获取卖家信息
        seller = db.query(User).filter(User.id == product.seller_id).first()
        product_info.seller_name = seller.username if seller else "未知"
        # 获取分类信息
        category = db.query(Category).filter(Category.id == product.category_id).first()
        product_info.category_name = category.name if category else "未知"
        product_list.append(product_info)
    
    return ProductListResponse(
        products=product_list,
        total=total,
        page=page,
        size=size
    )

# 分类管理
@router.get("/categories", response_model=CategoryListResponse)
async def get_categories(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    categories = db.query(Category).all()
    
    category_list = []
    for category in categories:
        # 获取商品数量
        product_count = db.query(func.count(Product.id)).filter(
            Product.category_id == category.id
        ).scalar()
        
        # 获取父分类名称
        parent_name = None
        if category.parent_id and category.parent_id > 0:
            parent = db.query(Category).filter(Category.id == category.parent_id).first()
            if parent:
                parent_name = parent.name
        
        category_info = CategoryInfo.from_orm(category)
        category_info.product_count = product_count or 0
        category_info.parent_name = parent_name
        category_list.append(category_info)
    
    return CategoryListResponse(categories=category_list)

# 订单管理
@router.get("/orders", response_model=OrderListResponse)
async def get_orders(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None),
    search: Optional[str] = Query(None)
):
    """获取订单列表"""
    query = db.query(Order)
    
    # 状态筛选
    if status is not None:
        query = query.filter(Order.order_status == status)
    
    # 搜索筛选
    if search:
        # 只搜索订单号，用户名和商品标题需要在后端过滤
        query = query.filter(Order.order_no.ilike(f"%{search}%"))
    
    # 分页
    total = query.count()
    orders = query.order_by(desc(Order.created_at)).offset((page - 1) * size).limit(size).all()
    
    order_list = []
    for order in orders:
        order_info = OrderInfo.from_orm(order)
        # 获取买家信息
        buyer = db.query(User).filter(User.id == order.buyer_id).first()
        order_info.buyer_name = buyer.username if buyer else "未知"
        # 获取商品信息
        product = db.query(Product).filter(Product.id == order.product_id).first()
        order_info.product_title = product.title if product else "未知"
        order_list.append(order_info)
    
    return OrderListResponse(
        orders=order_list,
        total=total,
        page=page,
        size=size
    )

# 店铺管理
@router.get("/shops", response_model=ShopListResponse)
async def get_shops(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None)
):
    """获取店铺列表"""
    query = db.query(Store).join(User, Store.owner_id == User.id)
    
    # 状态筛选
    if status is not None:
        query = query.filter(Store.is_open == (status == 1))
    
    # 分页
    total = query.count()
    shops = query.offset((page - 1) * size).limit(size).all()
    
    shop_list = []
    for shop in shops:
        shop_info = ShopInfo.model_validate(shop)
        # 获取店主信息
        owner = db.query(User).filter(User.id == shop.owner_id).first()
        shop_info.owner_name = owner.username if owner else None
        shop_list.append(shop_info)
    
    return ShopListResponse(
        shops=shop_list,
        total=total,
        page=page,
        size=size
    )

# 专场活动管理
@router.get("/events", response_model=EventListResponse)
async def get_events(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None)
):
    """获取专场活动列表"""
    query = db.query(SpecialEvent)
    
    # 状态筛选
    if is_active is not None:
        query = query.filter(SpecialEvent.is_active == is_active)
    
    # 分页
    total = query.count()
    events = query.order_by(desc(SpecialEvent.created_at)).offset((page - 1) * size).limit(size).all()
    
    event_list = []
    for event in events:
        # 获取关联商品数量
        product_count = db.query(func.count(EventProduct.id)).filter(
            EventProduct.event_id == event.id
        ).scalar()
        
        event_info = EventInfo.from_orm(event)
        event_info.product_count = product_count or 0
        event_list.append(event_info)
    
    return EventListResponse(
        events=event_list,
        total=total,
        page=page,
        size=size
    )

@router.get("/events/{event_id}")
async def get_event_by_id(
    event_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取单个专场活动详情"""
    try:
        # 查询专场活动
        event = db.query(SpecialEvent).filter(SpecialEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="专场活动不存在")
        
        # 获取商品数量
        product_count = db.query(EventProduct).filter(
            EventProduct.event_id == event_id
        ).count()
        
        # 转换为响应格式
        event_info = EventInfo.from_orm(event)
        event_info.product_count = product_count
        
        return event_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取专场活动失败: {str(e)}")

@router.post("/events")
async def create_event(
    event_data: dict,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """创建专场活动"""
    try:
        from datetime import datetime
        
        # 创建专场活动
        event = SpecialEvent(
            title=event_data.get("title"),
            description=event_data.get("description"),
            banner_image=event_data.get("banner_image"),
            start_time=datetime.fromisoformat(event_data.get("start_time")) if event_data.get("start_time") else None,
            end_time=datetime.fromisoformat(event_data.get("end_time")) if event_data.get("end_time") else None,
            is_active=event_data.get("is_active", True)
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        return {
            "success": True,
            "message": "专场活动创建成功",
            "data": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat() if event.start_time else None,
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "is_active": event.is_active
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建专场活动失败: {str(e)}")

@router.put("/events/{event_id}")
async def update_event(
    event_id: int,
    event_data: dict,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """更新专场活动"""
    try:
        from datetime import datetime
        
        # 查找专场活动
        event = db.query(SpecialEvent).filter(SpecialEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="专场活动不存在")
        
        # 更新字段
        if 'title' in event_data:
            event.title = event_data['title']
        if 'description' in event_data:
            event.description = event_data['description']
        if 'start_time' in event_data:
            event.start_time = datetime.fromisoformat(event_data['start_time'].replace('T', ' '))
        if 'end_time' in event_data:
            event.end_time = datetime.fromisoformat(event_data['end_time'].replace('T', ' '))
        if 'is_active' in event_data:
            event.is_active = event_data['is_active']
        if 'sort_order' in event_data:
            event.sort_order = event_data['sort_order']
        
        db.commit()
        
        return {
            "success": True,
            "message": "专场活动更新成功",
            "data": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat() if event.start_time else None,
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "is_active": event.is_active,
                "sort_order": event.sort_order
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新专场活动失败: {str(e)}")

@router.post("/events/{event_id}/products")
async def add_products_to_event(
    event_id: int,
    product_data: dict,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """添加商品到专场活动"""
    try:
        # 验证专场活动是否存在
        event = db.query(SpecialEvent).filter(SpecialEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="专场活动不存在")
        
        product_ids = product_data.get("product_ids", [])
        if not product_ids:
            raise HTTPException(status_code=400, detail="请选择要添加的商品")
        
        added_count = 0
        for product_id in product_ids:
            # 验证商品是否存在
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                continue
            
            # 检查商品是否已经在专场中
            existing = db.query(EventProduct).filter(
                EventProduct.event_id == event_id,
                EventProduct.product_id == product_id
            ).first()
            
            if existing:
                continue
            
            # 添加商品到专场
            event_product = EventProduct(
                event_id=event_id,
                product_id=product_id,
                sort_order=product_data.get("sort_order", 0)
            )
            
            db.add(event_product)
            added_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"成功添加 {added_count} 个商品到专场",
            "data": {
                "added_count": added_count,
                "event_id": event_id,
                "event_title": event.title
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"添加商品到专场失败: {str(e)}")

@router.delete("/events/{event_id}/products/{product_id}")
async def remove_product_from_event(
    event_id: int,
    product_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """从专场活动中移除商品"""
    try:
        # 查找专场商品关联
        event_product = db.query(EventProduct).filter(
            EventProduct.event_id == event_id,
            EventProduct.product_id == product_id
        ).first()
        
        if not event_product:
            raise HTTPException(status_code=404, detail="商品不在该专场中")
        
        db.delete(event_product)
        db.commit()
        
        return {
            "success": True,
            "message": "商品已从专场中移除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"移除商品失败: {str(e)}")

@router.get("/events/{event_id}/products")
async def get_event_products_admin(
    event_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取专场活动中的商品(管理端)"""
    try:
        # 验证专场活动是否存在
        event = db.query(SpecialEvent).filter(SpecialEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="专场活动不存在")
        
        # 查询专场中的商品
        query = db.query(Product).join(
            EventProduct, Product.id == EventProduct.product_id
        ).filter(EventProduct.event_id == event_id)
        
        total = query.count()
        products = query.order_by(EventProduct.sort_order, Product.created_at.desc()).offset((page - 1) * size).limit(size).all()
        
        # 转换为响应格式
        product_list = []
        for product in products:
            # 获取分类名称
            category = db.query(Category).filter(Category.id == product.category_id).first()
            category_name = category.name if category else "未分类"
            
            # 获取卖家名称
            seller = db.query(User).filter(User.id == product.seller_id).first()
            seller_name = seller.username if seller else "未知卖家"
            
            product_info = ProductInfo(
                id=product.id,
                title=product.title,
                description=product.description,
                starting_price=float(product.starting_price),
                current_price=float(product.current_price),
                buy_now_price=float(product.buy_now_price) if product.buy_now_price else None,
                auction_type=product.auction_type,
                auction_start_time=product.auction_start_time,
                auction_end_time=product.auction_end_time,
                location=product.location,
                shipping_fee=float(product.shipping_fee),
                is_free_shipping=product.is_free_shipping,
                condition_type=product.condition_type,
                view_count=product.view_count,
                bid_count=product.bid_count,
                favorite_count=product.favorite_count,
                status=product.status,
                is_featured=product.is_featured,
                created_at=product.created_at,
                seller_name=seller_name,
                category_name=category_name
            )
            product_list.append(product_info)
        
        return ProductListResponse(
            products=product_list,
            total=total,
            page=page,
            size=size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取专场商品失败: {str(e)}")

@router.get("/products/available-for-event")
async def get_available_products_for_event(
    event_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取可添加到专场的商品列表"""
    try:
        # 查询拍卖商品
        query = db.query(Product).filter(
            Product.auction_type == 1,  # 只有拍卖商品
            Product.status.in_([1, 2])  # 待审核或拍卖中
        )
        
        # 如果指定了专场ID，排除已在该专场中的商品
        if event_id:
            existing_product_ids = db.query(EventProduct.product_id).filter(
                EventProduct.event_id == event_id
            ).subquery()
            query = query.filter(~Product.id.in_(existing_product_ids))
        
        # 搜索过滤
        if keyword:
            query = query.filter(Product.title.contains(keyword))
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        total = query.count()
        products = query.order_by(desc(Product.created_at)).offset((page - 1) * size).limit(size).all()
        
        # 转换为响应格式
        product_list = []
        for product in products:
            # 获取分类名称
            category = db.query(Category).filter(Category.id == product.category_id).first()
            category_name = category.name if category else "未分类"
            
            # 获取卖家名称
            seller = db.query(User).filter(User.id == product.seller_id).first()
            seller_name = seller.username if seller else "未知卖家"
            
            product_info = ProductInfo(
                id=product.id,
                title=product.title,
                description=product.description,
                starting_price=float(product.starting_price),
                current_price=float(product.current_price),
                buy_now_price=float(product.buy_now_price) if product.buy_now_price else None,
                auction_type=product.auction_type,
                auction_start_time=product.auction_start_time,
                auction_end_time=product.auction_end_time,
                location=product.location,
                shipping_fee=float(product.shipping_fee),
                is_free_shipping=product.is_free_shipping,
                condition_type=product.condition_type,
                view_count=product.view_count,
                bid_count=product.bid_count,
                favorite_count=product.favorite_count,
                status=product.status,
                is_featured=product.is_featured,
                created_at=product.created_at,
                seller_name=seller_name,
                category_name=category_name
            )
            product_list.append(product_info)
        
        return ProductListResponse(
            products=product_list,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取可选商品失败: {str(e)}")

# 消息管理
@router.get("/messages", response_model=MessageListResponse)
async def get_messages(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    message_type: Optional[str] = Query(None),
    is_read: Optional[bool] = Query(None)
):
    """获取消息列表"""
    query = db.query(Message)
    
    # 类型筛选
    if message_type is not None:
        query = query.filter(Message.message_type == message_type)
    
    # 状态筛选
    if is_read is not None:
        query = query.filter(Message.is_read == is_read)
    
    # 分页
    total = query.count()
    messages = query.order_by(desc(Message.created_at)).offset((page - 1) * size).limit(size).all()
    
    message_list = []
    for message in messages:
        message_info = MessageInfo.from_orm(message)
        # 获取接收者信息
        receiver = db.query(User).filter(User.id == message.receiver_id).first()
        message_info.receiver_name = receiver.username if receiver else "未知"
        # 获取发送者信息
        if message.sender_id:
            sender = db.query(User).filter(User.id == message.sender_id).first()
            message_info.sender_name = sender.username if sender else "未知"
        else:
            message_info.sender_name = "系统"
        message_list.append(message_info)
    
    return MessageListResponse(
        messages=message_list,
        total=total,
        page=page,
        size=size
    )

# 发送系统消息
@router.post("/messages/system", response_model=dict)
async def send_system_message(
    message_data: SystemMessageRequest,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """发送系统消息"""
    # 根据接收者类型发送消息
    if message_data.receiver_type == "all":
        # 发送给所有用户
        users = db.query(User).filter(User.status == 1).all()
        for user in users:
            message = Message(
                sender_id=None,  # 系统消息
                receiver_id=user.id,
                message_type="system",  # 系统消息
                title=message_data.title,
                content=message_data.content
            )
            db.add(message)
    elif message_data.receiver_type == "user":
        # 发送给指定用户
        for user_id in message_data.receiver_ids:
            message = Message(
                sender_id=None,
                receiver_id=user_id,
                message_type="system",
                title=message_data.title,
                content=message_data.content
            )
            db.add(message)
    
    db.commit()
    
    return {"message": "系统消息发送成功"}

# 统计数据接口
@router.get("/statistics/overview", response_model=StatisticsOverview)
async def get_statistics_overview(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """获取统计概览"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # 每日新增用户
    daily_users = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        func.date(User.created_at).between(start_date, end_date)
    ).group_by(func.date(User.created_at)).all()
    
    # 每日订单数
    daily_orders = db.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('count')
    ).filter(
        func.date(Order.created_at).between(start_date, end_date)
    ).group_by(func.date(Order.created_at)).all()
    
    # 每日收入
    daily_revenue = db.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('amount')
    ).filter(
        and_(
            func.date(Order.created_at).between(start_date, end_date),
            Order.payment_status == 2
        )
    ).group_by(func.date(Order.created_at)).all()
    
    return StatisticsOverview(
        daily_users=[{"date": str(item.date), "count": item.count} for item in daily_users],
        daily_orders=[{"date": str(item.date), "count": item.count} for item in daily_orders],
        daily_revenue=[{"date": str(item.date), "amount": float(item.amount or 0)} for item in daily_revenue]
    )

# 导出数据
@router.get("/export/{data_type}")
async def export_data(
    data_type: str,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """导出数据"""
    # 这里应该实现具体的数据导出逻辑
    # 返回CSV或Excel文件
    if data_type not in ["users", "products", "orders", "shops"]:
        raise HTTPException(status_code=400, detail="不支持的数据类型")
    
    return {"message": f"{data_type}数据导出功能开发中..."}