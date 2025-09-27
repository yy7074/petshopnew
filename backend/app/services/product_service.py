from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any, Union, Set
from datetime import datetime, timedelta
import os

from ..models.product import Product, ProductImage, Category, ProductFavorite
from ..models.user import User
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse, ProductDetailResponse
from ..core.config import settings

class ProductService:
    
    async def get_products(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[int] = None,
        keyword: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        status: Optional[Union[str, int]] = None,
        auction_type: Optional[Union[str, int]] = None
    ) -> ProductListResponse:
        """获取商品列表"""
        query = db.query(Product)

        status_value = self._normalize_status(status)
        if status_value:
            query = query.filter(Product.status.in_(status_value))
        
        # 分类筛选
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        # 关键词搜索
        if keyword:
            search_term = f"%{keyword}%"
            query = query.filter(
                or_(
                    Product.title.like(search_term),
                    Product.description.like(search_term)
                )
            )
        
        # 价格范围筛选
        if min_price:
            query = query.filter(Product.current_price >= min_price)
        if max_price:
            query = query.filter(Product.current_price <= max_price)
        
        # 拍卖类型筛选
        auction_value = self._normalize_auction_type(auction_type)
        if auction_value:
            query = query.filter(Product.auction_type.in_(auction_value))
        
        # 排序
        if sort_by:
            order_field = self._resolve_sort_field(sort_by)

            if sort_order and sort_order.lower() == "asc":
                query = query.order_by(asc(order_field))
            else:
                query = query.order_by(desc(order_field))
        else:
            query = query.order_by(desc(Product.created_at))
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        return ProductListResponse(
            items=[self._to_product_response(product, db) for product in products],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )

    def _normalize_status(self, status: Optional[Union[str, int]]) -> Optional[Set[Union[int, str]]]:
        if status is None:
            return None

        values: Set[Union[int, str]] = set()

        if isinstance(status, int):
            values.update({status, str(status)})
        else:
            status_str = str(status).strip().lower()
            if not status_str or status_str == "all":
                return None

            if status_str.isdigit():
                values.update({int(status_str), status_str})
            else:
                status_map: Dict[str, Set[Union[int, str]]] = {
                    "draft": {1, "1", "draft"},
                    "pending": {1, "1", "pending", "review"},
                    "review": {1, "1", "pending", "review"},
                    "active": {2, 3, "2", "3", "active", "selling", "on_sale"},
                    "selling": {2, 3, "2", "3", "active", "selling"},
                    "on_sale": {2, 3, "2", "3", "active", "on_sale"},
                    "auction": {3, "3", "auction", "ongoing"},
                    "ongoing": {3, "3", "auction", "ongoing"},
                    "ended": {3, "3", "ended", "finished"},
                    "finished": {3, "3", "ended", "finished"},
                    "sold": {4, "4", "sold", "completed"},
                    "completed": {4, "4", "sold", "completed"},
                    "offline": {0, "0", "offline", "disabled"},
                    "disabled": {0, "0", "offline", "disabled"},
                }
                mapped = status_map.get(status_str)
                if mapped:
                    values.update(mapped)

        return values or None

    def _normalize_auction_type(self, auction_type: Optional[Union[str, int]]) -> Optional[Set[Union[int, str]]]:
        if auction_type is None:
            return None

        values: Set[Union[int, str]] = set()

        if isinstance(auction_type, int):
            values.update({auction_type, str(auction_type)})
        else:
            auction_str = str(auction_type).strip().lower()
            if not auction_str or auction_str in {"both", "all"}:
                return None

            if auction_str.isdigit():
                values.update({int(auction_str), auction_str})
            else:
                auction_map: Dict[str, Set[Union[int, str]]] = {
                    "auction": {1, "1", 3, "3", "auction"},
                    "fixed_price": {2, "2", 3, "3", "fixed", "fixed_price"},
                    "fixed": {2, "2", 3, "3", "fixed", "fixed_price"},
                    "mixed": {3, "3", "mixed", "hybrid"},
                    "hybrid": {3, "3", "mixed", "hybrid"},
                }
                mapped = auction_map.get(auction_str)
                if mapped:
                    values.update(mapped)

        return values or None

    def _resolve_sort_field(self, sort_by: str):
        sort_key = (sort_by or "").strip().lower()
        mapping = {
            "price": Product.current_price,
            "current_price": Product.current_price,
            "created_at": Product.created_at,
            "updated_at": Product.updated_at,
            "end_time": Product.auction_end_time,
            "auction_end_time": Product.auction_end_time,
            "popularity": Product.view_count,
            "view_count": Product.view_count,
            "bid_count": Product.bid_count,
            "favorite_count": Product.favorite_count,
        }

        return mapping.get(sort_key, Product.created_at)
    
    async def get_product_detail(
        self, 
        db: Session, 
        product_id: int, 
        user_id: Optional[int] = None
    ) -> Optional[ProductDetailResponse]:
        """获取商品详情"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        # 增加浏览量
        product.view_count += 1
        db.commit()
        
        # 检查是否收藏
        is_favorited = False
        if user_id:
            favorite = db.query(ProductFavorite).filter(
                and_(
                    ProductFavorite.product_id == product_id,
                    ProductFavorite.user_id == user_id
                )
            ).first()
            is_favorited = favorite is not None
        
        # 获取商品图片
        images = db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).order_by(ProductImage.sort_order).all()
        
        # 获取卖家信息
        seller = db.query(User).filter(User.id == product.seller_id).first()
        
        # 构建商品字典，排除images字段
        product_dict = {k: v for k, v in product.__dict__.items() if k != 'images'}
        
        return ProductDetailResponse(
            **product_dict,
            images=[img.image_url for img in images],
            is_favorited=is_favorited,
            seller_info={
                "id": seller.id,
                "username": seller.username,
                "avatar": seller.avatar_url
            } if seller else None
        )
    
    async def create_product(
        self, 
        db: Session, 
        product_data: ProductCreate, 
        seller_id: int
    ) -> ProductResponse:
        """创建商品"""
        # 创建商品
        product = Product(
            **product_data.dict(exclude={"images"}),
            seller_id=seller_id,
            current_price=product_data.starting_price,
            status="active"
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # 添加商品图片
        if product_data.images:
            for i, image_url in enumerate(product_data.images):
                image = ProductImage(
                    product_id=product.id,
                    image_url=image_url,
                    sort_order=i
                )
                db.add(image)
        
        db.commit()
        return self._to_product_response(product, db)
    
    async def update_product(
        self, 
        db: Session, 
        product_id: int, 
        product_data: ProductUpdate, 
        user_id: int
    ) -> Optional[ProductResponse]:
        """更新商品"""
        product = db.query(Product).filter(
            and_(Product.id == product_id, Product.seller_id == user_id)
        ).first()
        
        if not product:
            return None
        
        # 更新商品信息
        update_data = product_data.dict(exclude_unset=True, exclude={"images"})
        for field, value in update_data.items():
            setattr(product, field, value)
        
        product.updated_at = datetime.now()
        db.commit()
        
        return self._to_product_response(product, db)
    
    async def delete_product(self, db: Session, product_id: int, user_id: int) -> bool:
        """删除商品"""
        product = db.query(Product).filter(
            and_(Product.id == product_id, Product.seller_id == user_id)
        ).first()
        
        if not product:
            return False
        
        # 删除相关图片文件
        images = db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
        for image in images:
            try:
                if image.image_url.startswith("/static/"):
                    file_path = image.image_url.replace("/static/", "static/")
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except:
                pass
        
        # 删除数据库记录
        db.delete(product)
        db.commit()
        return True
    
    async def add_product_image(
        self, 
        db: Session, 
        product_id: int, 
        image_url: str, 
        user_id: int
    ) -> ProductImage:
        """添加商品图片"""
        # 检查权限
        product = db.query(Product).filter(
            and_(Product.id == product_id, Product.seller_id == user_id)
        ).first()
        
        if not product:
            raise ValueError("商品不存在或无权限")
        
        # 获取当前最大排序号
        max_order = db.query(func.max(ProductImage.sort_order)).filter(
            ProductImage.product_id == product_id
        ).scalar() or 0
        
        image = ProductImage(
            product_id=product_id,
            image_url=image_url,
            sort_order=max_order + 1
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        
        return image
    
    async def delete_product_image(
        self, 
        db: Session, 
        product_id: int, 
        image_id: int, 
        user_id: int
    ) -> bool:
        """删除商品图片"""
        # 检查权限
        product = db.query(Product).filter(
            and_(Product.id == product_id, Product.seller_id == user_id)
        ).first()
        
        if not product:
            return False
        
        image = db.query(ProductImage).filter(
            and_(ProductImage.id == image_id, ProductImage.product_id == product_id)
        ).first()
        
        if not image:
            return False
        
        # 删除文件
        try:
            if image.image_url.startswith("/static/"):
                file_path = image.image_url.replace("/static/", "static/")
                if os.path.exists(file_path):
                    os.remove(file_path)
        except:
            pass
        
        db.delete(image)
        db.commit()
        return True
    
    async def toggle_favorite(
        self, 
        db: Session, 
        product_id: int, 
        user_id: int
    ) -> Dict[str, Any]:
        """收藏/取消收藏商品"""
        existing_favorite = db.query(ProductFavorite).filter(
            and_(
                ProductFavorite.product_id == product_id,
                ProductFavorite.user_id == user_id
            )
        ).first()
        
        if existing_favorite:
            # 取消收藏
            db.delete(existing_favorite)
            db.commit()
            return {"is_favorited": False}
        else:
            # 添加收藏
            favorite = ProductFavorite(
                product_id=product_id,
                user_id=user_id
            )
            db.add(favorite)
            db.commit()
            return {"is_favorited": True}
    
    async def get_categories(self, db: Session) -> List[Category]:
        """获取商品分类"""
        return db.query(Category).filter(Category.is_active == True).order_by(Category.sort_order).all()
    
    async def get_user_products(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20,
        status: Optional[str] = None
    ) -> ProductListResponse:
        """获取用户发布的商品"""
        query = db.query(Product).filter(Product.seller_id == user_id)
        
        if status and status != "all":
            query = query.filter(Product.status == status)
        
        query = query.order_by(desc(Product.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        return ProductListResponse(
            items=[self._to_product_response(product, db) for product in products],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def get_user_favorites(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> ProductListResponse:
        """获取用户收藏的商品"""
        query = db.query(Product).join(ProductFavorite).filter(
            ProductFavorite.user_id == user_id
        ).order_by(desc(ProductFavorite.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        return ProductListResponse(
            items=[self._to_product_response(product, db) for product in products],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def get_trending_products(
        self, 
        db: Session, 
        page: int = 1, 
        page_size: int = 20
    ) -> ProductListResponse:
        """获取热门商品"""
        # 基于浏览量和收藏量的热门算法
        query = db.query(Product).filter(
            Product.status == "active"
        ).order_by(
            desc(Product.view_count + Product.favorite_count * 5)
        )
        
        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        return ProductListResponse(
            items=[self._to_product_response(product, db) for product in products],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def get_recent_products(
        self, 
        db: Session, 
        page: int = 1, 
        page_size: int = 20
    ) -> ProductListResponse:
        """获取最新商品"""
        query = db.query(Product).filter(
            Product.status == "active"
        ).order_by(desc(Product.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        return ProductListResponse(
            items=[self._to_product_response(product, db) for product in products],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    def _to_product_response(self, product: Product, db: Session) -> ProductResponse:
        """转换为响应格式"""
        # 获取商品图片
        images = db.query(ProductImage).filter(
            ProductImage.product_id == product.id
        ).order_by(ProductImage.sort_order).all()

        return ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            category_id=product.category_id,
            starting_price=product.starting_price,
            current_price=product.current_price,
            buy_now_price=product.buy_now_price,
            auction_type=product.auction_type,
            auction_start_time=product.auction_start_time,
            auction_end_time=product.auction_end_time,
            location=product.location,
            shipping_fee=product.shipping_fee,
            is_free_shipping=product.is_free_shipping,
            condition_type=product.condition_type,
            stock_quantity=product.stock_quantity,
            status=product.status,
            seller_id=product.seller_id,
            view_count=product.view_count,
            bid_count=product.bid_count,
            favorite_count=product.favorite_count,
            is_featured=product.is_featured,
            created_at=product.created_at,
            updated_at=product.updated_at,
            images=[img.image_url for img in images]
        )
