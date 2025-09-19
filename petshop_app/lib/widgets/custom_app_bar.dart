import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../constants/app_colors.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final bool showSearch;
  final bool showBack;
  final VoidCallback? onSearchTap;
  final VoidCallback? onBackTap;
  final List<Widget>? actions;

  const CustomAppBar({
    super.key,
    required this.title,
    this.showSearch = false,
    this.showBack = false,
    this.onSearchTap,
    this.onBackTap,
    this.actions,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(
        title,
        style: TextStyle(
          fontSize: 18.sp,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
      ),
      backgroundColor: AppColors.surface,
      elevation: 0,
      centerTitle: true,
      leading: showBack
          ? IconButton(
              icon: Icon(
                Icons.arrow_back_ios,
                color: AppColors.textPrimary,
                size: 20.w,
              ),
              onPressed: onBackTap ?? () => Navigator.of(context).pop(),
            )
          : null,
      actions: [
        if (showSearch)
          IconButton(
            icon: Icon(
              Icons.search,
              color: AppColors.textPrimary,
              size: 24.w,
            ),
            onPressed: onSearchTap,
          ),
        ...?actions,
        SizedBox(width: 8.w),
      ],
      bottom: PreferredSize(
        preferredSize: Size.fromHeight(1.h),
        child: Container(
          height: 1.h,
          color: AppColors.divider,
        ),
      ),
    );
  }

  @override
  Size get preferredSize => Size.fromHeight(kToolbarHeight + 1.h);
}












