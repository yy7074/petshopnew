import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class PublishTypePage extends StatefulWidget {
  const PublishTypePage({super.key});

  @override
  State<PublishTypePage> createState() => _PublishTypePageState();
}

class _PublishTypePageState extends State<PublishTypePage> {
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 300.h,
      padding: EdgeInsets.all(20.w),
      child: Column(
        children: [
          // 标题
          Text(
            '选择发布类型',
            style: TextStyle(
              fontSize: 18.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w600,
            ),
          ),
          SizedBox(height: 20.h),

          // 拍卖选项
          _buildPublishOption(
            '拍卖',
            '产品精品、普品拍卖,品相够好也可视为甄选',
            Icons.gavel,
            const Color(0xFFFF9800),
            () {
              Navigator.pop(context);
              // 跳转到拍卖发布页面
            },
          ),

          SizedBox(height: 16.h),

          // 一口价选项
          _buildPublishOption(
            '一口价',
            '快速发布,价格实在更快速出手',
            Icons.shopping_bag,
            const Color(0xFFE91E63),
            () {
              Navigator.pop(context);
              // 跳转到一口价发布页面
            },
          ),

          SizedBox(height: 20.h),

          // 关闭按钮
          GestureDetector(
            onTap: () {
              Navigator.pop(context);
            },
            child: Container(
              width: 40.w,
              height: 40.w,
              decoration: BoxDecoration(
                color: const Color(0xFFF5F5F5),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.close,
                size: 20.w,
                color: const Color(0xFF666666),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 构建发布选项
  Widget _buildPublishOption(
    String title,
    String description,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: EdgeInsets.all(16.w),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12.r),
          border: Border.all(
            color: color.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: Row(
          children: [
            // 图标
            Container(
              width: 40.w,
              height: 40.w,
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(8.r),
              ),
              child: Icon(
                icon,
                size: 20.w,
                color: Colors.white,
              ),
            ),
            SizedBox(width: 12.w),
            // 内容
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 16.sp,
                      color: const Color(0xFF333333),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  SizedBox(height: 4.h),
                  Text(
                    description,
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: const Color(0xFF666666),
                      height: 1.3,
                    ),
                  ),
                ],
              ),
            ),
            // 箭头
            Icon(
              Icons.arrow_forward_ios,
              size: 14.w,
              color: const Color(0xFF999999),
            ),
          ],
        ),
      ),
    );
  }
}
