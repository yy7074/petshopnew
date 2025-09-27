from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user, get_current_user_optional
from ..models.user import User
from ..models.product import Product, ProductImage, Category, ProductFavorite
from ..schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    CategoryResponse, ProductDetailResponse
)
from ..services.product_service import ProductService
from ..core.config import settings

router = APIRouter()
product_service = ProductService()

@router.get("/", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(None, regex="^(price|created_at|end_time|popularity)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    status: Optional[str] = Query("active", regex="^(active|sold|ended|all)$"),
    auction_type: Optional[str] = Query(None, regex="^(auction|fixed_price|both)$"),
    db: Session = Depends(get_db)
):
    """获取商品列表"""
    return await product_service.get_products(
        db=db,
        page=page,
        page_size=page_size,
        category_id=category_id,
        keyword=keyword,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
        status=status,
        auction_type=auction_type
    )

@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取商品详情"""
    product = await product_service.get_product_detail(db, product_id, current_user.id if current_user else None)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建商品"""
    return await product_service.create_product(db, product_data, current_user.id)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新商品"""
    product = await product_service.update_product(db, product_id, product_data, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在或无权限修改")
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除商品"""
    success = await product_service.delete_product(db, product_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="商品不存在或无权限删除")
    return {"message": "商品删除成功"}

@router.post("/upload-images")
async def upload_product_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传商品图片（发布商品时使用）"""
    if len(files) > 9:
        raise HTTPException(status_code=400, detail="最多只能上传9张图片")
    
    uploaded_images = []
    for file in files:
        # 验证文件类型
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file.filename}，支持的格式: {', '.join(allowed_extensions)}")
        
        # 验证文件大小 (5MB限制)
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"文件 {file.filename} 太大，最大支持5MB")
        
        # 重置文件指针
        await file.seek(0)
        
        # 生成唯一文件名
        timestamp = int(datetime.now().timestamp())
        unique_filename = f"product_{current_user.id}_{timestamp}_{file.filename}"
        
        # 创建上传目录
        upload_dir = os.path.join("backend", "static", "uploads", "products")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 压缩图片（如果需要）
        try:
            from PIL import Image
            import io
            
            # 打开图片
            with Image.open(file_path) as img:
                # 转换为RGB模式（去除透明通道）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 如果图片太大则压缩
                max_width, max_height = 1200, 1200
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    img.save(file_path, 'JPEG', quality=85, optimize=True)
                
        except ImportError:
            # 如果没有PIL库，跳过压缩
            pass
        except Exception as e:
            print(f"图片压缩失败: {e}")
        
        # 生成访问URL
        image_url = f"/static/uploads/products/{unique_filename}"
        uploaded_images.append(image_url)
    
    return {
        "success": True,
        "message": "图片上传成功",
        "images": uploaded_images
    }

@router.post("/{product_id}/images")
async def add_product_images(
    product_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """为已存在的商品添加图片"""
    # 验证商品权限
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.seller_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在或无权限操作")
    
    if len(files) > 9:
        raise HTTPException(status_code=400, detail="最多只能上传9张图片")
    
    uploaded_images = []
    for file in files:
        # 验证文件类型
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file.filename}")
        
        # 验证文件大小
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"文件 {file.filename} 太大，最大支持5MB")
        
        await file.seek(0)
        
        # 生成文件名
        timestamp = int(datetime.now().timestamp())
        filename = f"product_{product_id}_{timestamp}_{file.filename}"
        
        # 创建目录
        upload_dir = os.path.join("backend", "static", "uploads", "products")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 图片压缩处理
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                max_width, max_height = 1200, 1200
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    img.save(file_path, 'JPEG', quality=85, optimize=True)
        except:
            pass
        
        # 添加到商品图片列表
        image_url = f"/static/uploads/products/{filename}"
        current_images = product.images or []
        current_images.append(image_url)
        product.images = current_images
        
        uploaded_images.append(image_url)
    
    db.commit()
    
    return {
        "success": True,
        "message": "图片添加成功",
        "images": uploaded_images
    }

@router.delete("/{product_id}/images/{image_id}")
async def delete_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除商品图片"""
    success = await product_service.delete_product_image(db, product_id, image_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="图片不存在或无权限删除")
    return {"message": "图片删除成功"}

@router.post("/{product_id}/favorite")
async def toggle_product_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """收藏/取消收藏商品"""
    result = await product_service.toggle_favorite(db, product_id, current_user.id)
    return {"message": "收藏成功" if result["is_favorited"] else "取消收藏成功", "is_favorited": result["is_favorited"]}

@router.get("/categories/", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """获取商品分类"""
    return await product_service.get_categories(db)

@router.get("/user/{user_id}", response_model=ProductListResponse)
async def get_user_products(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(active|sold|ended|all)$"),
    db: Session = Depends(get_db)
):
    """获取用户发布的商品"""
    return await product_service.get_user_products(db, user_id, page, page_size, status)

@router.get("/favorites/my", response_model=ProductListResponse)
async def get_my_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的收藏商品"""
    return await product_service.get_user_favorites(db, current_user.id, page, page_size)

@router.get("/trending/", response_model=ProductListResponse)
async def get_trending_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取热门商品"""
    return await product_service.get_trending_products(db, page, page_size)

@router.get("/recent/", response_model=ProductListResponse)
async def get_recent_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取最新商品"""
    return await product_service.get_recent_products(db, page, page_size)

# 兼容性端点：为Flutter应用提供拍卖状态接口
@router.get("/{product_id}/auction/status")
async def get_product_auction_status(
    product_id: int,
    db: Session = Depends(get_db)
):
    """获取商品拍卖状态（兼容性端点）"""
    try:
        from ..services.auction_service import AuctionService
        auction_service = AuctionService()
        return await auction_service.get_auction_status(db, product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取拍卖状态失败")