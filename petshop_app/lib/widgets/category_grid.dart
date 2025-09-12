import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../constants/app_colors.dart';

class CategoryGrid extends StatelessWidget {
  const CategoryGrid({super.key});

  @override
  Widget build(BuildContext context) {
    final categories = [
      {'name': '宠物', 'icon': Icons.pets, 'color': AppColors.primary},
      {'name': '水族', 'icon': Icons.water, 'color': AppColors.info},
      {'name': '用品', 'icon': Icons.shopping_bag, 'color': AppColors.success},
      {'name': '食品', 'icon': Icons.restaurant, 'color': AppColors.warning},
      {'name': '玩具', 'icon': Icons.toys, 'color': AppColors.accent},
      {'name': '医疗', 'icon': Icons.medical_services, 'color': AppColors.error},
      {'name': '美容', 'icon': Icons.content_cut, 'color': AppColors.primary},
      {'name': '更多', 'icon': Icons.more_horiz, 'color': AppColors.textSecondary},
    ];

    return Container(
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 4,
          childAspectRatio: 1,
          crossAxisSpacing: 16.w,
          mainAxisSpacing: 16.h,
        ),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final category = categories[index];
          return GestureDetector(
            onTap: () {
              // TODO: 处理分类点击
              debugPrint('Category ${category['name']} clicked');
            },
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 48.w,
                  height: 48.w,
                  decoration: BoxDecoration(
                    color: (category['color'] as Color).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12.r),
                  ),
                  child: Icon(
                    category['icon'] as IconData,
                    color: category['color'] as Color,
                    size: 24.w,
                  ),
                ),
                SizedBox(height: 8.h),
                Text(
                  category['name'] as String,
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: AppColors.textSecondary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
