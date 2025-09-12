import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';
import '../../widgets/custom_app_bar.dart';
import '../../widgets/banner_swiper.dart';
import '../../widgets/category_grid.dart';
import '../../widgets/product_card.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final List<String> bannerImages = [
    'https://picsum.photos/400/200?random=1',
    'https://picsum.photos/400/200?random=2',
    'https://picsum.photos/400/200?random=3',
  ];

  final List<Map<String, dynamic>> categories = [
    {'name': '猫咪', 'icon': Icons.pets, 'color': AppColors.primary},
    {'name': '狗狗', 'icon': Icons.pets, 'color': AppColors.secondary},
    {'name': '鸟类', 'icon': Icons.pets, 'color': AppColors.accent},
    {'name': '其他', 'icon': Icons.pets, 'color': AppColors.primary},
  ];

  final List<Map<String, dynamic>> products = [
    {
      'id': 1,
      'name': '英短蓝猫',
      'price': 1500.0,
      'image': 'https://picsum.photos/200/200?random=10',
      'category': '猫咪',
      'description': '健康活泼的英短蓝猫，疫苗齐全',
    },
    {
      'id': 2,
      'name': '金毛犬',
      'price': 2000.0,
      'image': 'https://picsum.photos/200/200?random=11',
      'category': '狗狗',
      'description': '温顺可爱的金毛犬，已训练',
    },
    {
      'id': 3,
      'name': '蓝猫幼崽',
      'price': 800.0,
      'image': 'https://picsum.photos/200/200?random=12',
      'category': '猫咪',
      'description': '2个月大的蓝猫幼崽，健康可爱',
    },
    {
      'id': 4,
      'name': '拉布拉多',
      'price': 1800.0,
      'image': 'https://picsum.photos/200/200?random=13',
      'category': '狗狗',
      'description': '聪明忠诚的拉布拉多，适合家庭',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(
        title: '宠物商店',
        showSearch: true,
      ),
      body: RefreshIndicator(
        onRefresh: _onRefresh,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            children: [
              // 轮播图
              Container(
                height: 200.h,
                margin: EdgeInsets.all(16.w),
                child: BannerSwiper(
                  images: bannerImages,
                  onTap: (index) {
                    // 处理轮播图点击
                  },
                ),
              ),

              // 分类网格
              Container(
                margin: EdgeInsets.symmetric(horizontal: 16.w),
                child: CategoryGrid(
                  categories: categories,
                  onCategoryTap: (category) {
                    // 跳转到分类页面
                    Navigator.pushNamed(context, '/category',
                        arguments: category);
                  },
                ),
              ),

              // 推荐商品标题
              Container(
                width: double.infinity,
                margin: EdgeInsets.all(16.w),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '推荐商品',
                      style: TextStyle(
                        fontSize: 18.sp,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    GestureDetector(
                      onTap: () {
                        // 跳转到更多商品页面
                      },
                      child: Text(
                        '查看更多',
                        style: TextStyle(
                          fontSize: 14.sp,
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // 商品列表
              Container(
                margin: EdgeInsets.symmetric(horizontal: 16.w),
                child: GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 12.w,
                    mainAxisSpacing: 12.w,
                    childAspectRatio: 0.75,
                  ),
                  itemCount: products.length,
                  itemBuilder: (context, index) {
                    final product = products[index];
                    return ProductCard(
                      product: product,
                      onTap: () {
                        Navigator.pushNamed(
                          context,
                          '/product-detail',
                          arguments: product,
                        );
                      },
                    );
                  },
                ),
              ),

              SizedBox(height: 20.h),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _onRefresh() async {
    // 模拟刷新数据
    await Future.delayed(const Duration(seconds: 2));
    if (mounted) {
      setState(() {
        // 刷新数据
      });
    }
  }
}
