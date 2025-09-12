import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import '../../constants/app_colors.dart';
import '../../utils/app_routes.dart';
import '../../widgets/custom_app_bar.dart';
import '../../widgets/category_grid.dart';
import '../../widgets/product_card.dart';
import '../../widgets/banner_swiper.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage>
    with AutomaticKeepAliveClientMixin {
  final ScrollController _scrollController = ScrollController();

  @override
  bool get wantKeepAlive => true;

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      appBar: CustomAppBar(
        title: '宠物拍卖',
        showSearch: true,
        onSearchTap: () {
          Get.toNamed(AppRoutes.search);
        },
      ),
      body: RefreshIndicator(
        onRefresh: _onRefresh,
        child: CustomScrollView(
          controller: _scrollController,
          slivers: [
            // 轮播图
            SliverToBoxAdapter(
              child: Container(
                margin: EdgeInsets.all(16.w),
                child: const BannerSwiper(),
              ),
            ),
            // 分类网格
            SliverToBoxAdapter(
              child: Container(
                margin: EdgeInsets.symmetric(horizontal: 16.w),
                child: const CategoryGrid(),
              ),
            ),
            // 功能区域
            SliverToBoxAdapter(
              child: _buildFunctionSection(),
            ),
            // 一口价商品
            SliverToBoxAdapter(
              child: _buildSectionHeader('一口价', '更多'),
            ),
            SliverToBoxAdapter(
              child: _buildProductList(),
            ),
            // 专场活动
            SliverToBoxAdapter(
              child: _buildSectionHeader('专场活动', '更多'),
            ),
            SliverToBoxAdapter(
              child: _buildSpecialEvents(),
            ),
            // 同城服务
            SliverToBoxAdapter(
              child: _buildSectionHeader('同城服务', '更多'),
            ),
            SliverToBoxAdapter(
              child: _buildLocalServices(),
            ),
            // 热门拍卖
            SliverToBoxAdapter(
              child: _buildSectionHeader('热门拍卖', '更多'),
            ),
            SliverGrid(
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 0.75,
                crossAxisSpacing: 12.w,
                mainAxisSpacing: 12.w,
              ),
              delegate: SliverChildBuilderDelegate(
                (context, index) {
                  return Container(
                    margin: EdgeInsets.only(
                      left: index % 2 == 0 ? 16.w : 0,
                      right: index % 2 == 1 ? 16.w : 0,
                    ),
                    child: const ProductCard(),
                  );
                },
                childCount: 10,
              ),
            ),
            SliverToBoxAdapter(
              child: SizedBox(height: 20.h),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _onRefresh() async {
    await Future.delayed(const Duration(seconds: 2));
  }

  Widget _buildFunctionSection() {
    return Container(
      margin: EdgeInsets.all(16.w),
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
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildFunctionItem(
            icon: Icons.flash_on,
            title: '闪拍',
            color: AppColors.accent,
          ),
          _buildFunctionItem(
            icon: Icons.local_offer,
            title: '一口价',
            color: AppColors.success,
          ),
          _buildFunctionItem(
            icon: Icons.location_on,
            title: '同城',
            color: AppColors.info,
          ),
          _buildFunctionItem(
            icon: Icons.star,
            title: '精选',
            color: AppColors.warning,
          ),
        ],
      ),
    );
  }

  Widget _buildFunctionItem({
    required IconData icon,
    required String title,
    required Color color,
  }) {
    return GestureDetector(
      onTap: () {
        // TODO: 处理功能点击
      },
      child: Column(
        children: [
          Container(
            width: 48.w,
            height: 48.w,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12.r),
            ),
            child: Icon(
              icon,
              color: color,
              size: 24.w,
            ),
          ),
          SizedBox(height: 8.h),
          Text(
            title,
            style: TextStyle(
              fontSize: 12.sp,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, String action) {
    return Container(
      margin: EdgeInsets.fromLTRB(16.w, 24.h, 16.w, 16.h),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          GestureDetector(
            onTap: () {
              // TODO: 处理更多点击
            },
            child: Row(
              children: [
                Text(
                  action,
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: AppColors.textSecondary,
                  ),
                ),
                Icon(
                  Icons.chevron_right,
                  size: 16.w,
                  color: AppColors.textSecondary,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductList() {
    return SizedBox(
      height: 200.h,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: EdgeInsets.symmetric(horizontal: 16.w),
        itemCount: 5,
        itemBuilder: (context, index) {
          return Container(
            width: 160.w,
            margin: EdgeInsets.only(right: 12.w),
            child: const ProductCard(),
          );
        },
      ),
    );
  }

  Widget _buildSpecialEvents() {
    return SizedBox(
      height: 120.h,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: EdgeInsets.symmetric(horizontal: 16.w),
        itemCount: 3,
        itemBuilder: (context, index) {
          return Container(
            width: 280.w,
            margin: EdgeInsets.only(right: 12.w),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12.r),
              gradient: LinearGradient(
                colors: [
                  AppColors.primary.withOpacity(0.8),
                  AppColors.primaryLight.withOpacity(0.8),
                ],
              ),
            ),
            child: Stack(
              children: [
                Positioned(
                  right: -20.w,
                  top: -20.h,
                  child: Icon(
                    Icons.pets,
                    size: 80.w,
                    color: Colors.white.withOpacity(0.2),
                  ),
                ),
                Padding(
                  padding: EdgeInsets.all(16.w),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '春季宠物专场',
                        style: TextStyle(
                          fontSize: 16.sp,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 4.h),
                      Text(
                        '精选优质宠物，限时特惠',
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: Colors.white.withOpacity(0.9),
                        ),
                      ),
                      SizedBox(height: 8.h),
                      Container(
                        padding: EdgeInsets.symmetric(
                          horizontal: 12.w,
                          vertical: 4.h,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(12.r),
                        ),
                        child: Text(
                          '立即参与',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildLocalServices() {
    return SizedBox(
      height: 100.h,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: EdgeInsets.symmetric(horizontal: 16.w),
        itemCount: 4,
        itemBuilder: (context, index) {
          final services = ['上门服务', '宠物交流', '本地宠店', '鱼缸造景'];
          final icons = [
            Icons.home_repair_service,
            Icons.chat,
            Icons.store,
            Icons.water,
          ];
          final colors = [
            AppColors.primary,
            AppColors.success,
            AppColors.info,
            AppColors.warning,
          ];

          return Container(
            width: 80.w,
            margin: EdgeInsets.only(right: 16.w),
            child: Column(
              children: [
                Container(
                  width: 60.w,
                  height: 60.w,
                  decoration: BoxDecoration(
                    color: colors[index].withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16.r),
                  ),
                  child: Icon(
                    icons[index],
                    color: colors[index],
                    size: 28.w,
                  ),
                ),
                SizedBox(height: 8.h),
                Text(
                  services[index],
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: AppColors.textSecondary,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}


