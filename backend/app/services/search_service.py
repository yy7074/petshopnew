from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from typing import List, Optional
from datetime import datetime, timedelta
import redis
import json

from ..models.product import Product, Category
from ..models.user import User, SearchHistory
from ..schemas.search import SearchResponse, SearchSuggestionResponse, HotSearchResponse
from ..schemas.product import ProductResponse
from ..core.config import settings

class SearchService:
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL) if hasattr(settings, 'REDIS_URL') else None
    
    async def search_products(
        self,
        db: Session,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "relevance",
        sort_order: str = "desc",
        auction_type: Optional[str] = None,
        location: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> SearchResponse:
        """搜索商品"""
        
        # 构建基础查询
        query = db.query(Product).filter(Product.status == "active")
        
        # 关键词搜索
        if keyword:
            search_term = f"%{keyword}%"
            query = query.filter(
                or_(
                    Product.title.like(search_term),
                    Product.description.like(search_term),
                    Product.tags.like(search_term)
                )
            )
            
            # 记录搜索热度
            await self._record_search_popularity(keyword)
        
        # 分类筛选
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        # 价格范围筛选
        if min_price is not None:
            query = query.filter(Product.current_price >= min_price)
        if max_price is not None:
            query = query.filter(Product.current_price <= max_price)
        
        # 拍卖类型筛选
        if auction_type and auction_type != "both":
            query = query.filter(Product.auction_type == auction_type)
        
        # 地理位置筛选（如果有）
        if location:
            query = query.filter(Product.location.like(f"%{location}%"))
        
        # 排序
        if sort_by == "relevance":
            # 相关度排序：标题匹配 > 描述匹配 > 标签匹配
            if keyword:
                query = query.order_by(
                    desc(
                        func.case(
                            (Product.title.like(f"%{keyword}%"), 3),
                            (Product.description.like(f"%{keyword}%"), 2),
                            (Product.tags.like(f"%{keyword}%"), 1),
                            else_=0
                        )
                    ),
                    desc(Product.view_count)
                )
            else:
                query = query.order_by(desc(Product.view_count))
        elif sort_by == "price":
            order_field = Product.current_price
        elif sort_by == "created_at":
            order_field = Product.created_at
        elif sort_by == "end_time":
            order_field = Product.auction_end_time
        elif sort_by == "popularity":
            order_field = Product.view_count
        else:
            order_field = Product.created_at
        
        if sort_by != "relevance":
            if sort_order == "asc":
                query = query.order_by(asc(order_field))
            else:
                query = query.order_by(desc(order_field))
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        # 构建响应
        items = []
        for product in products:
            product_data = ProductResponse(
                id=product.id,
                title=product.title,
                description=product.description,
                category_id=product.category_id,
                starting_price=product.starting_price,
                current_price=product.current_price,
                auction_type=product.auction_type,
                auction_end_time=product.auction_end_time,
                status=product.status,
                seller_id=product.seller_id,
                view_count=product.view_count,
                favorite_count=product.favorite_count,
                created_at=product.created_at,
                updated_at=product.updated_at
            )
            items.append(product_data)
        
        # 获取搜索建议
        suggestions = []
        if keyword and len(keyword) >= 2:
            suggestions = await self.get_search_suggestions(db, keyword, 5)
        
        # 获取筛选选项
        filters = await self.get_search_filters(db, keyword, category_id)
        
        return SearchResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
            keyword=keyword,
            suggestions=[s.keyword for s in suggestions],
            filters=filters
        )
    
    async def get_search_suggestions(
        self, 
        db: Session, 
        keyword: str, 
        limit: int = 10
    ) -> List[SearchSuggestionResponse]:
        """获取搜索建议"""
        suggestions = []
        
        # 从商品标题中获取建议
        products = db.query(Product.title).filter(
            and_(
                Product.title.like(f"%{keyword}%"),
                Product.status == "active"
            )
        ).limit(limit).all()
        
        for product in products:
            suggestions.append(SearchSuggestionResponse(
                keyword=product.title,
                type="product",
                count=1
            ))
        
        # 从搜索历史中获取建议
        if self.redis_client:
            try:
                pattern = f"search_suggestion:{keyword}*"
                keys = self.redis_client.keys(pattern)
                for key in keys[:limit]:
                    keyword_suggestion = key.decode().replace("search_suggestion:", "")
                    count = self.redis_client.get(key)
                    if count:
                        suggestions.append(SearchSuggestionResponse(
                            keyword=keyword_suggestion,
                            type="history",
                            count=int(count)
                        ))
            except:
                pass
        
        # 去重并按热度排序
        unique_suggestions = {}
        for suggestion in suggestions:
            if suggestion.keyword not in unique_suggestions:
                unique_suggestions[suggestion.keyword] = suggestion
            else:
                unique_suggestions[suggestion.keyword].count += suggestion.count
        
        result = list(unique_suggestions.values())
        result.sort(key=lambda x: x.count, reverse=True)
        return result[:limit]
    
    async def get_hot_searches(
        self, 
        db: Session, 
        limit: int = 10
    ) -> List[HotSearchResponse]:
        """获取热门搜索"""
        hot_searches = []
        
        if self.redis_client:
            try:
                # 从Redis获取热门搜索
                hot_keys = self.redis_client.zrevrange("hot_searches", 0, limit - 1, withscores=True)
                for keyword_bytes, score in hot_keys:
                    keyword = keyword_bytes.decode()
                    hot_searches.append(HotSearchResponse(
                        keyword=keyword,
                        count=int(score),
                        trend="up"  # 这里可以根据历史数据计算趋势
                    ))
            except:
                pass
        
        # 如果Redis没有数据，从数据库获取
        if not hot_searches:
            # 从搜索历史表获取热门搜索
            recent_searches = db.query(
                SearchHistory.keyword,
                func.count(SearchHistory.id).label("count")
            ).filter(
                SearchHistory.created_at >= datetime.now() - timedelta(days=7)
            ).group_by(SearchHistory.keyword).order_by(
                desc("count")
            ).limit(limit).all()
            
            for search in recent_searches:
                hot_searches.append(HotSearchResponse(
                    keyword=search.keyword,
                    count=search.count,
                    trend="stable"
                ))
        
        return hot_searches
    
    async def get_user_search_history(
        self, 
        db: Session, 
        user_id: int, 
        limit: int = 20
    ) -> List[str]:
        """获取用户搜索历史"""
        history = db.query(SearchHistory.keyword).filter(
            SearchHistory.user_id == user_id
        ).order_by(desc(SearchHistory.created_at)).limit(limit).all()
        
        return [h.keyword for h in history]
    
    async def save_search_history(
        self, 
        db: Session, 
        user_id: int, 
        keyword: str
    ):
        """保存搜索历史"""
        # 检查是否已存在相同关键词的最近搜索
        existing = db.query(SearchHistory).filter(
            and_(
                SearchHistory.user_id == user_id,
                SearchHistory.keyword == keyword
            )
        ).first()
        
        if existing:
            # 更新时间
            existing.created_at = datetime.now()
        else:
            # 创建新记录
            history = SearchHistory(
                user_id=user_id,
                keyword=keyword
            )
            db.add(history)
        
        db.commit()
        
        # 记录到Redis热门搜索
        await self._record_search_popularity(keyword)
    
    async def clear_search_history(self, db: Session, user_id: int):
        """清除搜索历史"""
        db.query(SearchHistory).filter(SearchHistory.user_id == user_id).delete()
        db.commit()
    
    async def delete_search_history_item(
        self, 
        db: Session, 
        user_id: int, 
        keyword: str
    ):
        """删除单条搜索历史"""
        db.query(SearchHistory).filter(
            and_(
                SearchHistory.user_id == user_id,
                SearchHistory.keyword == keyword
            )
        ).delete()
        db.commit()
    
    async def get_search_filters(
        self, 
        db: Session, 
        keyword: Optional[str] = None, 
        category_id: Optional[int] = None
    ) -> dict:
        """获取搜索筛选选项"""
        filters = {}
        
        # 获取分类筛选
        categories_query = db.query(Category).filter(Category.is_active == True)
        if keyword:
            # 如果有关键词，只显示有相关商品的分类
            categories_query = categories_query.join(Product).filter(
                and_(
                    Product.status == "active",
                    or_(
                        Product.title.like(f"%{keyword}%"),
                        Product.description.like(f"%{keyword}%")
                    )
                )
            ).distinct()
        
        categories = categories_query.all()
        filters["categories"] = [
            {"id": cat.id, "name": cat.name, "count": cat.product_count}
            for cat in categories
        ]
        
        # 获取价格范围
        price_query = db.query(
            func.min(Product.current_price).label("min_price"),
            func.max(Product.current_price).label("max_price")
        ).filter(Product.status == "active")
        
        if keyword:
            price_query = price_query.filter(
                or_(
                    Product.title.like(f"%{keyword}%"),
                    Product.description.like(f"%{keyword}%")
                )
            )
        
        if category_id:
            price_query = price_query.filter(Product.category_id == category_id)
        
        price_range = price_query.first()
        if price_range and price_range.min_price is not None:
            filters["price_range"] = {
                "min": float(price_range.min_price),
                "max": float(price_range.max_price)
            }
        
        # 获取拍卖类型统计
        auction_types = db.query(
            Product.auction_type,
            func.count(Product.id).label("count")
        ).filter(Product.status == "active")
        
        if keyword:
            auction_types = auction_types.filter(
                or_(
                    Product.title.like(f"%{keyword}%"),
                    Product.description.like(f"%{keyword}%")
                )
            )
        
        auction_types = auction_types.group_by(Product.auction_type).all()
        filters["auction_types"] = [
            {"type": at.auction_type, "count": at.count}
            for at in auction_types
        ]
        
        return filters
    
    async def get_trending_keywords(
        self, 
        db: Session, 
        period: str = "day", 
        limit: int = 10
    ) -> List[dict]:
        """获取趋势关键词"""
        # 计算时间范围
        if period == "hour":
            time_delta = timedelta(hours=1)
        elif period == "day":
            time_delta = timedelta(days=1)
        elif period == "week":
            time_delta = timedelta(weeks=1)
        elif period == "month":
            time_delta = timedelta(days=30)
        else:
            time_delta = timedelta(days=1)
        
        start_time = datetime.now() - time_delta
        
        # 从搜索历史获取趋势关键词
        trending = db.query(
            SearchHistory.keyword,
            func.count(SearchHistory.id).label("count")
        ).filter(
            SearchHistory.created_at >= start_time
        ).group_by(SearchHistory.keyword).order_by(
            desc("count")
        ).limit(limit).all()
        
        result = []
        for trend in trending:
            result.append({
                "keyword": trend.keyword,
                "count": trend.count,
                "period": period
            })
        
        return result
    
    async def get_category_suggestions(
        self, 
        db: Session, 
        category_id: int, 
        limit: int = 10
    ) -> List[str]:
        """获取分类相关搜索建议"""
        # 获取该分类下的热门商品标题
        products = db.query(Product.title).filter(
            and_(
                Product.category_id == category_id,
                Product.status == "active"
            )
        ).order_by(desc(Product.view_count)).limit(limit).all()
        
        # 提取关键词
        suggestions = []
        for product in products:
            # 简单的关键词提取，实际应用中可以使用更复杂的NLP算法
            words = product.title.split()
            for word in words:
                if len(word) >= 2 and word not in suggestions:
                    suggestions.append(word)
                    if len(suggestions) >= limit:
                        break
            if len(suggestions) >= limit:
                break
        
        return suggestions
    
    async def autocomplete_search(
        self, 
        db: Session, 
        query: str, 
        search_type: str = "all", 
        limit: int = 10
    ) -> dict:
        """搜索自动完成"""
        results = {"products": [], "categories": [], "brands": [], "users": []}
        
        if search_type in ["all", "products"]:
            # 商品搜索
            products = db.query(Product.title).filter(
                and_(
                    Product.title.like(f"%{query}%"),
                    Product.status == "active"
                )
            ).limit(limit).all()
            results["products"] = [p.title for p in products]
        
        if search_type in ["all", "categories"]:
            # 分类搜索
            categories = db.query(Category.name).filter(
                and_(
                    Category.name.like(f"%{query}%"),
                    Category.is_active == True
                )
            ).limit(limit).all()
            results["categories"] = [c.name for c in categories]
        
        if search_type in ["all", "users"]:
            # 用户搜索
            users = db.query(User.username).filter(
                and_(
                    User.username.like(f"%{query}%"),
                    User.status == 1
                )
            ).limit(limit).all()
            results["users"] = [u.username for u in users]
        
        return results
    
    async def _record_search_popularity(self, keyword: str):
        """记录搜索热度"""
        if self.redis_client:
            try:
                # 增加搜索次数
                self.redis_client.zincrby("hot_searches", 1, keyword)
                
                # 设置过期时间（7天）
                self.redis_client.expire("hot_searches", 7 * 24 * 3600)
                
                # 记录建议关键词
                self.redis_client.incr(f"search_suggestion:{keyword}")
                self.redis_client.expire(f"search_suggestion:{keyword}", 7 * 24 * 3600)
            except:
                pass