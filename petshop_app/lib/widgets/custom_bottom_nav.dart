import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../constants/app_colors.dart';

class CustomBottomNav extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const CustomBottomNav({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 80.h + MediaQuery.of(context).padding.bottom, // 增加高度以容纳突出按钮
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Stack(
        clipBehavior: Clip.none, // 允许子组件超出边界
        children: [
          // 底部导航栏主体
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              height: 60.h + MediaQuery.of(context).padding.bottom,
              padding: EdgeInsets.only(
                  bottom: MediaQuery.of(context).padding.bottom),
              child: Row(
                children: [
                  // 首页
                  _buildNavItem(0, Icons.home_outlined, Icons.home, '首页'),
                  // 分类
                  _buildNavItem(
                      1, Icons.grid_view_outlined, Icons.grid_view, '分类'),
                  // 中间空白区域
                  Expanded(child: Container()),
                  // 消息
                  _buildNavItem(
                      3, Icons.chat_bubble_outline, Icons.chat_bubble, '消息'),
                  // 我的
                  _buildNavItem(4, Icons.person_outline, Icons.person, '我的'),
                ],
              ),
            ),
          ),

          // 中间圆形按钮 - 使用app logo
          Positioned(
            left: 0,
            right: 0,
            top: -20.h, // 向上突出更多
            child: Center(
              child: GestureDetector(
                onTap: () => onTap(2),
                child: Container(
                  width: 70.w, // 恢复原始尺寸
                  height: 70.w,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Color(0xFF66D9FF), // 蓝色渐变
                        Color(0xFF4FC3F7),
                        Color(0xFF29B6F6),
                      ],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.2),
                        blurRadius: 15,
                        offset: const Offset(0, 5),
                      ),
                      BoxShadow(
                        color: const Color(0xFF29B6F6).withOpacity(0.4),
                        blurRadius: 10,
                        offset: const Offset(0, 3),
                      ),
                    ],
                  ),
                  child: Container(
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.white,
                    ),
                    margin: EdgeInsets.all(4.w),
                    child: Padding(
                      padding: EdgeInsets.all(12.w),
                      child: Image.asset(
                        'assets/images/app_logo.png',
                        fit: BoxFit.contain,
                        errorBuilder: (context, error, stackTrace) {
                          return Icon(
                            Icons.pets,
                            size: 32.w,
                            color: const Color(0xFF29B6F6),
                          );
                        },
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem(
      int index, IconData unselectedIcon, IconData selectedIcon, String label) {
    final isSelected = currentIndex == index;

    return Expanded(
      child: GestureDetector(
        onTap: () => onTap(index),
        behavior: HitTestBehavior.opaque,
        child: Container(
          padding: EdgeInsets.symmetric(vertical: 8.h),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                isSelected ? selectedIcon : unselectedIcon,
                size: 24.w,
                color: isSelected ? AppColors.primary : AppColors.textSecondary,
              ),
              SizedBox(height: 4.h),
              Text(
                label,
                style: TextStyle(
                  fontSize: 10.sp,
                  color:
                      isSelected ? AppColors.primary : AppColors.textSecondary,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
