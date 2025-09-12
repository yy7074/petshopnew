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
      height: 80.h + MediaQuery.of(context).padding.bottom,
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
        children: [
          // 底部导航栏主体
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              height: 80.h + MediaQuery.of(context).padding.bottom,
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

          // 中间圆形按钮 - 宠物拍卖图标
          Positioned(
            left: 0,
            right: 0,
            top: 0,
            child: Center(
              child: GestureDetector(
                onTap: () => onTap(2),
                child: Container(
                  width: 70.w,
                  height: 70.w,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Color(0xFFFF9800), // 橙色
                        Color(0xFFF57C00),
                        Color(0xFFE65100),
                      ],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.15),
                        blurRadius: 12,
                        offset: const Offset(0, 4),
                      ),
                      BoxShadow(
                        color: const Color(0xFFFF9800).withOpacity(0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Container(
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.white,
                    ),
                    margin: EdgeInsets.all(4.w),
                    child: Stack(
                      children: [
                        // 锦鲤装饰图案
                        Positioned.fill(
                          child: Padding(
                            padding: EdgeInsets.all(8.w),
                            child: CustomPaint(
                              painter: KoiFishPainter(),
                            ),
                          ),
                        ),
                      ],
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

// 锦鲤装饰画笔
class KoiFishPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFFFF6B35) // 橙红色
      ..style = PaintingStyle.fill;

    final outlinePaint = Paint()
      ..color = const Color(0xFFF57C00)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width * 0.35;

    // 绘制简化的锦鲤鱼形状
    final fishPath = Path();

    // 鱼身（椭圆）
    final fishBodyRect = Rect.fromCenter(
        center: center, width: radius * 1.6, height: radius * 0.8);
    fishPath.addOval(fishBodyRect);

    // 鱼尾
    final tailPath = Path();
    tailPath.moveTo(center.dx + radius * 0.8, center.dy);
    tailPath.lineTo(center.dx + radius * 1.2, center.dy - radius * 0.4);
    tailPath.lineTo(center.dx + radius * 1.2, center.dy + radius * 0.4);
    tailPath.close();

    canvas.drawPath(fishPath, paint);
    canvas.drawPath(tailPath, paint);
    canvas.drawPath(fishPath, outlinePaint);
    canvas.drawPath(tailPath, outlinePaint);

    // 鱼眼
    final eyePaint = Paint()..color = Colors.white;
    final eyeCenter =
        Offset(center.dx - radius * 0.3, center.dy - radius * 0.1);
    canvas.drawCircle(eyeCenter, radius * 0.15, eyePaint);

    final pupilPaint = Paint()..color = Colors.black;
    canvas.drawCircle(eyeCenter, radius * 0.08, pupilPaint);

    // 装饰性波纹
    final wavePaint = Paint()
      ..color = const Color(0xFFFF9800).withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    for (int i = 0; i < 3; i++) {
      canvas.drawCircle(center, radius * 0.3 + (i * radius * 0.2), wavePaint);
    }
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
