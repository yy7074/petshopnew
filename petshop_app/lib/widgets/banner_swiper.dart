import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:card_swiper/card_swiper.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../constants/app_colors.dart';

class BannerSwiper extends StatefulWidget {
  final List<String> images;
  final Function(int)? onTap;

  const BannerSwiper({
    super.key,
    required this.images,
    this.onTap,
  });

  @override
  State<BannerSwiper> createState() => _BannerSwiperState();
}

class _BannerSwiperState extends State<BannerSwiper> {
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity, // 宽度占满父容器
      height: double.infinity, // 高度也占满父容器
      child: Swiper(
          itemBuilder: (BuildContext context, int index) {
            return GestureDetector(
              onTap: () {
                widget.onTap?.call(index);
              },
              child: CachedNetworkImage(
                imageUrl: widget.images[index],
                fit: BoxFit.cover,
                placeholder: (context, url) => Container(
                  color: AppColors.background,
                  child: Center(
                    child: CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(
                        AppColors.primary,
                      ),
                    ),
                  ),
                ),
                errorWidget: (context, url, error) => Container(
                  color: AppColors.background,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.pets,
                        size: 48.w,
                        color: AppColors.primary,
                      ),
                      SizedBox(height: 8.h),
                      Text(
                        '宠物拍卖',
                        style: TextStyle(
                          fontSize: 16.sp,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
          itemCount: widget.images.length,
          pagination: SwiperPagination(
            alignment: Alignment.bottomCenter,
            margin: EdgeInsets.only(bottom: 8.h), // 减小底部边距
            builder: DotSwiperPaginationBuilder(
              color: Colors.white.withOpacity(0.5),
              activeColor: Colors.white,
              size: 6.w, // 减小指示点
              activeSize: 6.w,
            ),
          ),
          control: null, // 隐藏左右箭头
          autoplay: true, // 开启自动播放
          autoplayDelay: 4000, // 4秒切换一次
          autoplayDisableOnInteraction: false, // 用户交互后继续自动播放
          duration: 600, // 切换动画时长
          curve: Curves.easeInOutCubic, // 更流畅的动画曲线
          viewportFraction: 1.0, // 确保轮播图占满宽度
          scale: 1.0, // 不缩放
        ),
    );
  }
}
