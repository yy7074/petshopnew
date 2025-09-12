import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';

class ShopDataPage extends StatefulWidget {
  const ShopDataPage({super.key});

  @override
  State<ShopDataPage> createState() => _ShopDataPageState();
}

class _ShopDataPageState extends State<ShopDataPage> {
  String _selectedTimeframe = '本月';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: SafeArea(
        child: Column(
          children: [
            SizedBox(height: 16.h),
            _buildHeader(),
            SizedBox(height: 20.h),
            _buildShopInfo(),
            SizedBox(height: 20.h),
            _buildShopMetrics(),
            SizedBox(height: 20.h),
            _buildSalesReport(),
            SizedBox(height: 100.h),
          ],
        ),
      ),
    );
  }

  // 构建头部
  Widget _buildHeader() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          // 返回按钮
          GestureDetector(
            onTap: () {
              Navigator.pop(context);
            },
            child: Container(
              width: 36.w,
              height: 36.w,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(18.r),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.08),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Icon(
                Icons.arrow_back_ios_new,
                size: 18.w,
                color: const Color(0xFF333333),
              ),
            ),
          ),
          SizedBox(width: 16.w),
          // 标题
          Expanded(
            child: Text(
              '店铺数据',
              style: TextStyle(
                fontSize: 18.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          SizedBox(width: 52.w), // 占位，保持标题居中
        ],
      ),
    );
  }

  // 构建店铺信息
  Widget _buildShopInfo() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      padding: EdgeInsets.all(16.w),
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
      child: Row(
        children: [
          // 店铺头像
          Container(
            width: 50.w,
            height: 50.w,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xFFF0F0F0),
            ),
            child: ClipOval(
              child: CachedNetworkImage(
                imageUrl: 'https://picsum.photos/100/100?random=shop',
                fit: BoxFit.cover,
                placeholder: (context, url) => Container(
                  color: const Color(0xFFF0F0F0),
                  child: const Icon(
                    Icons.store,
                    color: Color(0xFF999999),
                  ),
                ),
                errorWidget: (context, url, error) => Container(
                  color: const Color(0xFFF0F0F0),
                  child: const Icon(
                    Icons.store,
                    color: Color(0xFF999999),
                  ),
                ),
              ),
            ),
          ),
          SizedBox(width: 12.w),
          // 店铺信息
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '招财猫旺财狗',
                  style: TextStyle(
                    fontSize: 16.sp,
                    color: const Color(0xFF333333),
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(height: 4.h),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8.w, vertical: 2.h),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2196F3),
                    borderRadius: BorderRadius.circular(10.r),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.check,
                        size: 12.w,
                        color: Colors.white,
                      ),
                      SizedBox(width: 4.w),
                      Text(
                        '精品宠物专卖店',
                        style: TextStyle(
                          fontSize: 10.sp,
                          color: Colors.white,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 构建店铺指标
  Widget _buildShopMetrics() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
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
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '店铺指标',
                  style: TextStyle(
                    fontSize: 16.sp,
                    color: const Color(0xFF333333),
                    fontWeight: FontWeight.w600,
                  ),
                ),
                _buildTimeframeTabs(),
              ],
            ),
            SizedBox(height: 20.h),
            _buildMetricsGrid(),
          ],
        ),
      ),
    );
  }

  // 构建时间范围标签
  Widget _buildTimeframeTabs() {
    return Row(
      children: [
        _buildTimeframeTab('本月', '本月'),
        SizedBox(width: 8.w),
        _buildTimeframeTab('上月', '上月'),
        SizedBox(width: 8.w),
        _buildTimeframeTab('前3个月', '前3个月'),
      ],
    );
  }

  // 构建时间范围标签项
  Widget _buildTimeframeTab(String label, String value) {
    bool isSelected = _selectedTimeframe == value;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedTimeframe = value;
        });
      },
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 8.w, vertical: 4.h),
        decoration: BoxDecoration(
          color: isSelected
              ? const Color(0xFF2196F3).withOpacity(0.1)
              : Colors.transparent,
          border: Border.all(
            color:
                isSelected ? const Color(0xFF2196F3) : const Color(0xFFE0E0E0),
            width: 1,
          ),
          borderRadius: BorderRadius.circular(4.r),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12.sp,
            color:
                isSelected ? const Color(0xFF2196F3) : const Color(0xFF666666),
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }

  // 构建指标网格
  Widget _buildMetricsGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 12.w,
      mainAxisSpacing: 12.h,
      childAspectRatio: 1.5,
      children: [
        _buildMetricItem('成交率排行', '10%', Icons.trending_up),
        _buildMetricItem('售后纠纷率', '10%', Icons.warning),
        _buildMetricItem('0元流拍率', '10%', Icons.cancel),
        _buildMetricItem('瑕疵退款率', '10%', Icons.undo),
        _buildMetricItem('精品率', '10%', Icons.star),
        _buildMetricItem('发拍驳回率', '10%', Icons.block),
      ],
    );
  }

  // 构建指标项目
  Widget _buildMetricItem(String title, String value, IconData icon) {
    return Container(
      padding: EdgeInsets.all(12.w),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FA),
        borderRadius: BorderRadius.circular(8.r),
        border: Border.all(
          color: const Color(0xFFE0E0E0),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 12.sp,
                  color: const Color(0xFF666666),
                  fontWeight: FontWeight.w500,
                ),
              ),
              SizedBox(width: 4.w),
              Icon(
                Icons.help_outline,
                size: 12.w,
                color: const Color(0xFF999999),
              ),
            ],
          ),
          SizedBox(height: 8.h),
          Row(
            children: [
              Icon(
                icon,
                size: 16.w,
                color: const Color(0xFF9C4DFF),
              ),
              SizedBox(width: 8.w),
              Text(
                value,
                style: TextStyle(
                  fontSize: 18.sp,
                  color: const Color(0xFF333333),
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // 构建销售报表
  Widget _buildSalesReport() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
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
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '店铺销售报表',
                    style: TextStyle(
                      fontSize: 16.sp,
                      color: const Color(0xFF333333),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  SizedBox(height: 4.h),
                  Text(
                    '查看详细数据统计',
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: const Color(0xFF666666),
                    ),
                  ),
                ],
              ),
            ),
            GestureDetector(
              onTap: () {
                // 跳转到详细报表页面
              },
              child: Row(
                children: [
                  Text(
                    '查看详情',
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: const Color(0xFF9C4DFF),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  SizedBox(width: 4.w),
                  Icon(
                    Icons.arrow_forward_ios,
                    size: 12.w,
                    color: const Color(0xFF9C4DFF),
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
