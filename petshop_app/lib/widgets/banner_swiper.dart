import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:card_swiper/card_swiper.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../constants/app_colors.dart';

class BannerSwiper extends StatefulWidget {
  const BannerSwiper({super.key});

  @override
  State<BannerSwiper> createState() => _BannerSwiperState();
}

class _BannerSwiperState extends State<BannerSwiper> {
  final List<String> bannerImages = [
    'https://via.placeholder.com/375x180/FF6B35/FFFFFF?text=Banner+1',
    'https://via.placeholder.com/375x180/4CAF50/FFFFFF?text=Banner+2',
    'https://via.placeholder.com/375x180/2196F3/FFFFFF?text=Banner+3',
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 180.h,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12.r),
        child: Swiper(
          itemBuilder: (BuildContext context, int index) {
            return GestureDetector(
              onTap: () {
                // TODO: 处理轮播图点击
                debugPrint('Banner $index clicked');
              },
              child: CachedNetworkImage(
                imageUrl: bannerImages[index],
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
          itemCount: bannerImages.length,
          pagination: SwiperPagination(
            alignment: Alignment.bottomCenter,
            margin: EdgeInsets.only(bottom: 16.h),
            builder: DotSwiperPaginationBuilder(
              color: Colors.white.withOpacity(0.5),
              activeColor: Colors.white,
              size: 8.w,
              activeSize: 8.w,
            ),
          ),
          control: null, // 隐藏左右箭头
          autoplay: true,
          autoplayDelay: 3000,
          duration: 800,
          curve: Curves.easeInOut,
        ),
      ),
    );
  }
}
