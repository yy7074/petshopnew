import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../constants/app_colors.dart';

class AuctionCard extends StatelessWidget {
  final Map<String, dynamic> product;
  final VoidCallback? onTap;
  final VoidCallback? onFavorite;

  const AuctionCard({
    super.key,
    required this.product,
    this.onTap,
    this.onFavorite,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 商品图片
            Stack(
              children: [
                ClipRRect(
                  borderRadius:
                      BorderRadius.vertical(top: Radius.circular(12.r)),
                  child: CachedNetworkImage(
                    imageUrl: product['image'] ?? '',
                    width: double.infinity,
                    height: 200.h,
                    fit: BoxFit.cover,
                    placeholder: (context, url) => Container(
                      color: AppColors.background,
                      child: Center(
                        child: CircularProgressIndicator(
                          valueColor:
                              AlwaysStoppedAnimation<Color>(AppColors.primary),
                        ),
                      ),
                    ),
                    errorWidget: (context, url, error) => Container(
                      color: AppColors.background,
                      child: Icon(
                        Icons.pets,
                        size: 50.w,
                        color: AppColors.primary,
                      ),
                    ),
                  ),
                ),

                // 倒计时标签
                Positioned(
                  top: 12.h,
                  right: 12.w,
                  child: Container(
                    padding:
                        EdgeInsets.symmetric(horizontal: 8.w, vertical: 4.h),
                    decoration: BoxDecoration(
                      color: Colors.red,
                      borderRadius: BorderRadius.circular(12.r),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.access_time,
                          size: 10.w,
                          color: Colors.white,
                        ),
                        SizedBox(width: 2.w),
                        Text(
                          product['timeLeft'] ?? '',
                          style: TextStyle(
                            fontSize: 10.sp,
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                // 收藏按钮
                Positioned(
                  top: 12.h,
                  left: 12.w,
                  child: GestureDetector(
                    onTap: onFavorite,
                    child: Container(
                      width: 28.w,
                      height: 28.w,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.9),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        product['isFavorite'] == true
                            ? Icons.favorite
                            : Icons.favorite_border,
                        size: 16.w,
                        color: product['isFavorite'] == true
                            ? Colors.red
                            : AppColors.textSecondary,
                      ),
                    ),
                  ),
                ),
              ],
            ),

            // 商品信息
            Padding(
              padding: EdgeInsets.all(12.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 商品标题
                  Text(
                    product['name'] ?? '',
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  SizedBox(height: 8.h),

                  // 价格信息
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '当前价',
                            style: TextStyle(
                              fontSize: 12.sp,
                              color: AppColors.textSecondary,
                            ),
                          ),
                          Text(
                            '¥${product['currentPrice'] ?? 0}',
                            style: TextStyle(
                              fontSize: 20.sp,
                              fontWeight: FontWeight.bold,
                              color: Colors.red,
                            ),
                          ),
                        ],
                      ),
                      SizedBox(width: 12.w),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '起拍价：¥${product['startPrice'] ?? 0}',
                              style: TextStyle(
                                fontSize: 11.sp,
                                color: AppColors.textHint,
                                decoration: TextDecoration.lineThrough,
                              ),
                            ),
                            SizedBox(height: 2.h),
                            if (product['bidCount'] != null &&
                                product['bidCount'] > 0)
                              Container(
                                padding: EdgeInsets.symmetric(
                                    horizontal: 6.w, vertical: 2.h),
                                decoration: BoxDecoration(
                                  color: AppColors.primary.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(8.r),
                                ),
                                child: Text(
                                  '${product['bidCount']}人出价',
                                  style: TextStyle(
                                    fontSize: 10.sp,
                                    color: AppColors.primary,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 12.h),

                  // 卖家信息和位置
                  Row(
                    children: [
                      // 卖家头像
                      ClipRRect(
                        borderRadius: BorderRadius.circular(12.r),
                        child: CachedNetworkImage(
                          imageUrl: product['seller']?['avatar'] ?? '',
                          width: 24.w,
                          height: 24.w,
                          fit: BoxFit.cover,
                          placeholder: (context, url) => Container(
                            color: AppColors.background,
                            child: Icon(
                              Icons.person,
                              size: 12.w,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ),
                      ),
                      SizedBox(width: 6.w),

                      // 卖家名称
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              product['seller']?['name'] ?? '',
                              style: TextStyle(
                                fontSize: 11.sp,
                                color: AppColors.textSecondary,
                                fontWeight: FontWeight.w500,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            if (product['seller']?['rating'] != null)
                              Row(
                                children: [
                                  Icon(
                                    Icons.star,
                                    size: 10.w,
                                    color: Colors.orange,
                                  ),
                                  SizedBox(width: 2.w),
                                  Text(
                                    '${product['seller']['rating']}',
                                    style: TextStyle(
                                      fontSize: 10.sp,
                                      color: AppColors.textHint,
                                    ),
                                  ),
                                ],
                              ),
                          ],
                        ),
                      ),

                      // 位置信息
                      if (product['location'] != null)
                        Row(
                          children: [
                            Icon(
                              Icons.location_on,
                              size: 12.w,
                              color: AppColors.textHint,
                            ),
                            SizedBox(width: 2.w),
                            Text(
                              product['location'],
                              style: TextStyle(
                                fontSize: 10.sp,
                                color: AppColors.textHint,
                              ),
                            ),
                          ],
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
