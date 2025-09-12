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
      height: 60.h + MediaQuery.of(context).padding.bottom, // 进一步降低整体高度
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
              height: 45.h + MediaQuery.of(context).padding.bottom, // 进一步降低主体高度
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
            top: -10.h, // 调整位置以适应新的高度，减少伸出高度
            child: Center(
              child: GestureDetector(
                onTap: () => onTap(2),
                child: Container(
                  width: 60.w, // 稍微减小尺寸避免边界问题
                  height: 60.w,
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
                        color: Colors.black.withOpacity(0.15), // 减少阴影透明度
                        blurRadius: 10, // 减小模糊半径
                        offset: const Offset(0, 3), // 减小偏移
                      ),
                      BoxShadow(
                        color: const Color(0xFF29B6F6).withOpacity(0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: EdgeInsets.all(8.w), // 减少内边距
                    child: Image.asset(
                      'assets/images/pet_shop_logo.png', // 使用拍宠有道logo
                      fit: BoxFit.contain,
                      errorBuilder: (context, error, stackTrace) {
                        return Icon(
                          Icons.pets,
                          size: 28.w, // 减小图标尺寸
                          color: Colors.white, // 改为白色图标
                        );
                      },
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
          padding: EdgeInsets.symmetric(vertical: 4.h), // 减小垂直内边距
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                isSelected ? selectedIcon : unselectedIcon,
                size: 22.w, // 稍微减小图标尺寸
                color: isSelected ? AppColors.primary : AppColors.textSecondary,
              ),
              SizedBox(height: 2.h), // 减小间距
              Text(
                label,
                style: TextStyle(
                  fontSize: 9.sp, // 稍微减小字体
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
