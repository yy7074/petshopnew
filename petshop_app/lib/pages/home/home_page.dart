import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:get/get.dart';
import '../../constants/app_colors.dart';
import '../../widgets/auction_card.dart';
import '../../widgets/banner_swiper.dart';
import '../pet_social/pet_social_page.dart';
import '../local_stores/local_pet_stores_page.dart';
import '../aquarium_design/aquarium_design_page.dart';
import '../door_service/door_service_page.dart';
import '../search/search_page.dart';
import '../events/special_event_page.dart';
import '../product/product_detail_page.dart';
import '../../services/product_service.dart' as product_service;
import '../../services/event_service.dart';
import '../../services/home_service.dart' as home_service;
import '../../models/product.dart' as product_models;
import '../../models/category.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late PageController _pageController;
  int _currentTabIndex = 0;
  final product_service.ProductService _productService =
      product_service.ProductService();
  final EventService _eventService = EventService();
  final home_service.HomeService _homeService = home_service.HomeService();

  // 数据状态
  List<product_models.Product> _products = [];
  List<product_models.Product> _hotProducts = [];
  List<product_models.Product> _recentProducts = [];
  List<product_models.Product> _recommendedProducts = [];
  List<home_service.SpecialEvent> _specialEvents = [];
  List<Category> _categories = [];
  List<home_service.Banner> _banners = [];
  home_service.HomeStats? _homeStats;
  bool _isLoading = false;
  String? _errorMessage;

  final List<String> tabs = [
    '首页·AI',
    '宠物',
    '水族',
    '一口价',
    '同城',
  ];

  // 功能网格数据
  final List<Map<String, dynamic>> functionGrid = [
    {
      'name': 'AI识宠',
      'icon': 'assets/icons/ai_pet.png',
      'color': Color(0xFFFFB74D)
    },
    {
      'name': '限时拍卖',
      'icon': 'assets/icons/limited_auction.png',
      'color': Color(0xFF9C4DFF)
    },
    {
      'name': '品牌专区',
      'icon': 'assets/icons/brand_zone.png',
      'color': Color(0xFFFF7043)
    },
    {
      'name': '一口价专区',
      'icon': 'assets/icons/fixed_price.png',
      'color': Color(0xFF42A5F5)
    },
    {
      'name': '成交查询',
      'icon': 'assets/icons/transaction_query.png',
      'color': Color(0xFF9C4DFF)
    },
    {
      'name': '同城送达',
      'icon': 'assets/icons/local_delivery.png',
      'color': Color(0xFF66BB6A)
    },
    {
      'name': '回收查询',
      'icon': 'assets/icons/recycle_query.png',
      'color': Color(0xFFFFCA28)
    },
    {
      'name': '合作方及代理',
      'icon': 'assets/icons/cooperation.png',
      'color': Color(0xFFAB47BC)
    },
    {
      'name': '支付测试',
      'icon': 'assets/icons/transaction_query.png',
      'color': Color(0xFFE91E63)
    },
    {
      'name': '拍卖测试',
      'icon': 'assets/icons/limited_auction.png',
      'color': Color(0xFF2196F3)
    },
  ];

  final List<Map<String, dynamic>> auctionProducts = [
    {
      'id': 1,
      'name': '纯种英短蓝猫',
      'currentPrice': 1200.0,
      'startPrice': 800.0,
      'image': 'https://picsum.photos/200/200?random=10',
      'category': '猫咪',
      'timeLeft': '2天3小时',
      'bidCount': 15,
      'description': '健康活泼的英短蓝猫，疫苗齐全，血统纯正',
      'location': '北京朝阳',
      'seller': {
        'name': '爱宠之家',
        'avatar': 'https://picsum.photos/50/50?random=1',
        'rating': 4.8,
      }
    },
    {
      'id': 2,
      'name': '金毛犬幼崽',
      'currentPrice': 2500.0,
      'startPrice': 1500.0,
      'image': 'https://picsum.photos/200/200?random=11',
      'category': '狗狗',
      'timeLeft': '1天12小时',
      'bidCount': 23,
      'description': '温顺可爱的金毛犬，已训练基本指令',
      'location': '上海浦东',
      'seller': {
        'name': '宠物乐园',
        'avatar': 'https://picsum.photos/50/50?random=2',
        'rating': 4.9,
      }
    },
  ];

  @override
  void initState() {
    super.initState();
    _pageController = PageController(initialPage: 0);
    _loadHomeData();
  }

  /// 加载首页数据
  Future<void> _loadHomeData() async {
    print('===== 开始加载首页数据 =====');
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // 并行加载多个数据
      final results = await Future.wait([
        _homeService.getHomeData(),
        _homeService.getHomeBanners(),
        _homeService.getHomeStats(),
      ]);

      print('API调用完成，开始处理结果...');
      print('results[0].success: ${results[0].success}');
      print('results[1].success: ${results[1].success}');
      print('results[2].success: ${results[2].success}');

      if (mounted) {
        print('组件仍然mounted，开始setState...');
        setState(() {
          _isLoading = false;

          // 处理首页数据
          if (results[0].success) {
            final homeData = results[0].data! as home_service.HomeData;
            print('首页数据类型: ${homeData.runtimeType}');
            print('赋值前专场数量: ${homeData.specialEvents.length}');
            print(
                '专场数据详情: ${homeData.specialEvents.map((e) => '${e.id}-${e.title}').toList()}');

            _hotProducts = homeData.hotProducts;
            _recentProducts = homeData.recentProducts;
            _recommendedProducts = homeData.recommendedProducts;
            _specialEvents = homeData.specialEvents;
            _categories = homeData.categories;

            print('赋值后_specialEvents长度: ${_specialEvents.length}');
            print(
                '赋值后_specialEvents内容: ${_specialEvents.map((e) => '${e.id}-${e.title}').toList()}');
          } else {
            print('首页数据加载失败: ${results[0].message}');
            _errorMessage = results[0].message;
          }

          // 处理轮播图数据
          try {
            if (results[1].success) {
              final bannersData = results[1].data as List<dynamic>;
              print('轮播图原始数据数量: ${bannersData.length}');
              print('轮播图原始数据: ${bannersData}');

              _banners = bannersData
                  .map((item) => home_service.Banner.fromJson(
                      item as Map<String, dynamic>))
                  .toList();

              print('轮播图解析后数量: ${_banners.length}');
              print(
                  '轮播图解析后内容: ${_banners.map((b) => '${b.id}-${b.title}').toList()}');
            } else {
              print('轮播图数据加载失败: ${results[1].message}');
            }
          } catch (e) {
            print('轮播图数据解析错误: $e');
            print('轮播图原始数据: ${results[1].data}');
          }

          // 处理统计数据
          if (results[2].success) {
            _homeStats = results[2].data! as home_service.HomeStats;
          }

          print(
              'setState内部最终检查 - 轮播图: ${_banners.length}, 专场: ${_specialEvents.length}');
        });

        // setState外部再次检查
        print(
            'setState外部最终检查 - 轮播图: ${_banners.length}, 专场: ${_specialEvents.length}');
      } else {
        print('组件已经unmounted，跳过setState');
      }
    } catch (e) {
      print('加载数据异常: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = '加载数据失败: $e';
        });
      }
    }

    print('===== 首页数据加载完成 =====');
  }

  /// 刷新数据
  Future<void> _refreshData() async {
    await _loadHomeData();
  }

  /// 处理轮播图点击
  void _handleBannerTap(home_service.Banner banner) {
    debugPrint('Banner clicked: ${banner.title}');
    // 根据链接类型进行导航
    if (banner.link.startsWith('/events/')) {
      // 跳转到专场页面
      Get.toNamed('/special-event',
          arguments: {'eventId': banner.link.split('/').last});
    } else if (banner.link.startsWith('/products')) {
      // 跳转到商品列表页面
      Get.toNamed('/products', arguments: {'query': banner.link});
    } else {
      // 其他链接处理
      debugPrint('Banner link: ${banner.link}');
    }
  }

  /// 转换Product对象为Map格式（兼容AuctionCard）
  Map<String, dynamic> _convertProductToMap(product_models.Product product) {
    return {
      'id': product.id,
      'seller_id': product.sellerId, // 添加seller_id字段
      'name': product.title,
      'title': product.title, // 添加title字段（ProductDetailPage可能需要）
      'currentPrice': product.auctionInfo?.currentPrice ?? 0.0,
      'current_price': product.auctionInfo?.currentPrice ?? 0.0, // 添加current_price字段
      'startPrice': product.auctionInfo?.startPrice ?? 0.0,
      'starting_price': product.auctionInfo?.startPrice ?? 0.0, // 添加starting_price字段
      'images': product.images, // 添加images字段
      'image': product.images.isNotEmpty
          ? product.images.first
          : 'https://picsum.photos/200/200?random=${product.id}',
      'category': '宠物', // TODO: 从categoryId获取分类名称
      'category_id': product.categoryId, // 添加category_id字段
      'timeLeft': _formatTimeLeft(product.auctionInfo?.endTime),
      'bidCount': product.auctionInfo?.bidCount ?? 0,
      'bid_count': product.auctionInfo?.bidCount ?? 0, // 添加bid_count字段
      'description': product.description,
      'location': product.location ?? '未知',
      'auction_type': product.type == product_models.ProductType.auction ? 1 : 2,
      'auction_end_time': product.auctionInfo?.endTime.toIso8601String(),
      'created_at': product.createdAt.toIso8601String(),
      'updated_at': product.updatedAt.toIso8601String(),
      'seller': {
        'name': '卖家${product.sellerId}',
        'avatar': 'https://picsum.photos/50/50?random=${product.sellerId}',
        'rating': 4.8,
      }
    };
  }

  /// 格式化剩余时间
  String _formatTimeLeft(DateTime? endTime) {
    if (endTime == null) return '未知';

    final now = DateTime.now();
    final difference = endTime.difference(now);

    if (difference.isNegative) {
      return '已结束';
    }

    final days = difference.inDays;
    final hours = difference.inHours % 24;
    final minutes = difference.inMinutes % 60;

    if (days > 0) {
      return '${days}天${hours}小时';
    } else if (hours > 0) {
      return '${hours}小时${minutes}分钟';
    } else {
      return '${minutes}分钟';
    }
  }

  /// 切换收藏状态
  void _toggleFavorite(product_models.Product product) {
    // TODO: 实现收藏功能
    debugPrint('Toggle favorite for product: ${product.id}');
  }

  /// 构建商品卡片骨架屏
  Widget _buildProductCardSkeleton() {
    return Container(
      height: 200.h,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // 图片骨架
          Container(
            height: 120.h,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(12.r),
                topRight: Radius.circular(12.r),
              ),
            ),
          ),
          // 内容骨架
          Expanded(
            child: Padding(
              padding: EdgeInsets.all(12.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    height: 16.h,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(4.r),
                    ),
                  ),
                  SizedBox(height: 8.h),
                  Container(
                    height: 14.h,
                    width: 100.w,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(4.r),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF9C4DFF), // 紫色
              Color(0xFF7B1FA2), // 深紫色
            ],
          ),
        ),
        child: SafeArea(
          bottom: false,
          child: Column(
            children: [
              SizedBox(height: 8.h),
              // 搜索栏
              _buildSearchBar(),
              SizedBox(height: 16.h),
              // Tab标签
              _buildTabBar(),
              SizedBox(height: 16.h),
              // 主内容区域
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFFF5F5F5),
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(20.r),
                      topRight: Radius.circular(20.r),
                    ),
                  ),
                  child: PageView.builder(
                    controller: _pageController,
                    physics:
                        const NeverScrollableScrollPhysics(), // 禁用PageView的手势滑动，但允许内部滚动
                    scrollDirection: Axis.horizontal, // 明确指定水平滚动
                    onPageChanged: (index) {
                      setState(() {
                        _currentTabIndex = index;
                      });
                    },
                    itemCount: 5, // 5个标签页
                    itemBuilder: (context, index) {
                      switch (index) {
                        case 0:
                          return SingleChildScrollView(
                            physics: const BouncingScrollPhysics(), // 使用弹性滚动
                            child: Column(
                              children: [
                                _buildBannerSection(),
                                _buildFunctionGrid(),
                                _buildProductList(),
                                SizedBox(height: 100.h), // 添加底部空间确保可以滚动
                              ],
                            ),
                          );
                        case 1:
                          return _buildPetPageContent();
                        case 2:
                          return _buildAquaticPageContent();
                        case 3:
                          return _buildFixedPricePageContent();
                        case 4:
                          return _buildLocalServicesPageContent();
                        default:
                          return Container();
                      }
                    },
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSearchBar() {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const SearchPage()),
        );
      },
      child: Container(
        margin: EdgeInsets.symmetric(horizontal: 16.w),
        height: 36.h,
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.15),
          borderRadius: BorderRadius.circular(18.r),
        ),
        child: Row(
          children: [
            SizedBox(width: 16.w),
            Icon(
              Icons.search,
              size: 18.w,
              color: Colors.white.withOpacity(0.9),
            ),
            SizedBox(width: 8.w),
            Expanded(
              child: Text(
                '搜拍品',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: Colors.white.withOpacity(0.9),
                  fontWeight: FontWeight.w400,
                ),
              ),
            ),
            Container(
              height: 24.h,
              width: 1.w,
              color: Colors.white.withOpacity(0.3),
              margin: EdgeInsets.symmetric(horizontal: 12.w),
            ),
            Padding(
              padding: EdgeInsets.only(right: 16.w),
              child: Text(
                '搜索',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: Colors.white.withOpacity(0.9),
                  fontWeight: FontWeight.w400,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      height: 38.h, // 减少高度，使tabbar更紧凑
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween, // 固定5个标签平均分布
        children: tabs.asMap().entries.map((entry) {
          final index = entry.key;
          final tab = entry.value;
          final isSelected = index == _currentTabIndex;

          return GestureDetector(
            onTap: () {
              if (_currentTabIndex != index) {
                _pageController.animateToPage(
                  index,
                  duration: const Duration(milliseconds: 200),
                  curve: Curves.easeInOut,
                );
              }
            },
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: EdgeInsets.symmetric(
                      horizontal: 10.w, vertical: 6.h), // 减少内边距
                  decoration: const BoxDecoration(
                    color: Colors.transparent, // 去掉白色背景
                  ),
                  child: Stack(
                    clipBehavior: Clip.none,
                    children: [
                      Text(
                        tab,
                        style: TextStyle(
                          fontSize: 14.sp, // 稍小字体
                          color: Colors.white, // 始终保持白色，不改变
                          fontWeight:
                              isSelected ? FontWeight.w600 : FontWeight.w500,
                        ),
                      ),
                      // 为"宠物"添加右上角"捡漏"图标
                      if (index == 1) // 宠物是第二个标签（索引为1）
                        Positioned(
                          top: -12.h, // 调高位置确保可见
                          right: -6.w,
                          child: Container(
                            padding: EdgeInsets.symmetric(
                                horizontal: 3.w, vertical: 1.h),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFFEB3B),
                              borderRadius: BorderRadius.circular(4.r),
                            ),
                            child: Text(
                              '捡漏',
                              style: TextStyle(
                                fontSize: 7.sp,
                                color: Colors.black87,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
                SizedBox(height: 2.h), // 减少间距
                // 选中时显示底部黄色横条
                Container(
                  width: isSelected ? 24.w : 0,
                  height: 2.h,
                  decoration: BoxDecoration(
                    color: isSelected
                        ? const Color(0xFFFFEB3B)
                        : Colors.transparent, // 黄色横条
                    borderRadius: BorderRadius.circular(1.r),
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  // 轮播图部分 - 与推广横幅同样大小
  Widget _buildBannerSection() {
    print('构建轮播图区域，轮播图数量: ${_banners.length}');

    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
      height: 120.h, // 与推广横幅相同高度
      width: double.infinity, // 宽度更大
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16.r),
        child: _banners.isEmpty
            ? Container(
                height: 120.h,
                color: Colors.grey[200],
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.image_outlined,
                        size: 32.w,
                        color: Colors.grey[400],
                      ),
                      SizedBox(height: 8.h),
                      Text(
                        '暂无轮播图数据 (${_banners.length})',
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              )
            : BannerSwiper(
                images: _banners.map((banner) => banner.image).toList(),
                onTap: (index) {
                  if (index < _banners.length) {
                    final banner = _banners[index];
                    // 处理轮播图点击事件
                    _handleBannerTap(banner);
                  }
                },
              ),
      ),
    );
  }

  /// 构建专场区域
  Widget _buildSpecialEventsSection() {
    print('构建专场区域，专场数量: ${_specialEvents.length}');

    if (_specialEvents.isEmpty) {
      return Container(
        height: 120.h,
        margin: EdgeInsets.symmetric(horizontal: 16.w),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(12.r),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.event_available_outlined,
                size: 32.w,
                color: Colors.grey[400],
              ),
              SizedBox(height: 8.h),
              Text(
                '暂无专场数据 (${_specialEvents.length})',
                style: TextStyle(
                  fontSize: 12.sp,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      );
    }

    return Container(
      height: 120.h,
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _specialEvents.length,
        itemBuilder: (context, index) {
          final event = _specialEvents[index];
          return Container(
            width: 200.w,
            margin: EdgeInsets.only(right: 12.w),
            child: GestureDetector(
              onTap: () {
                // 跳转到专场详情页面，传递专场 ID
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => SpecialEventPage(
                      title: event.title,
                      eventId: event.id.toString(),
                    ),
                  ),
                ).then((_) {
                  // 从专场页面返回时刷新首页数据
                  _loadHomeData();
                });
              },
              child: _buildSpecialCard(
                '专场',
                event.title,
                _formatEventTime(event.endTime ?? DateTime.now()),
                '进行中',
                event.bannerImage ??
                    'https://picsum.photos/200/150?random=event${event.id}',
                const Color(0xFF4A90E2),
              ),
            ),
          );
        },
      ),
    );
  }

  /// 格式化专场时间
  String _formatEventTime(DateTime endTime) {
    final now = DateTime.now();
    final difference = endTime.difference(now);

    if (difference.isNegative) {
      return '已结束';
    } else if (difference.inDays > 0) {
      return '${difference.inDays}天后结束';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}小时后结束';
    } else {
      return '${difference.inMinutes}分钟后结束';
    }
  }

  Widget _buildFunctionGrid() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
      padding:
          EdgeInsets.symmetric(horizontal: 0, vertical: 8.h), // 减少内边距，移除水平内边距
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
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        padding: EdgeInsets.symmetric(horizontal: 8.w), // 只给GridView加水平内边距
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 4,
          childAspectRatio: 1.2, // 调整比例，让高度更紧凑
          crossAxisSpacing: 0, // 移除水平间距
          mainAxisSpacing: 8.h, // 减少主轴间距
        ),
        itemCount: functionGrid.length,
        itemBuilder: (context, index) {
          final item = functionGrid[index];
          return GestureDetector(
            onTap: () {
              // 处理功能点击
              if (item['name'] == '限时拍卖') {
                // 跳转到专场列表页面
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const SpecialEventPage(
                      title: '限时拍卖专场',
                      eventId: '1',
                    ),
                  ),
                );
              } else if (item['name'] == '支付测试') {
                // 跳转到支付测试页面
                Get.toNamed('/test-payment');
              } else if (item['name'] == '拍卖测试') {
                // 跳转到拍卖测试页面
                Get.toNamed('/auction-test');
              } else {
                debugPrint('点击了：${item['name']}');
              }
            },
            child: Container(
              margin: EdgeInsets.symmetric(horizontal: 4.w), // 给每个按钮加小间距
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // 图标容器 - 去掉背景色
                  SizedBox(
                    width: 40.w,
                    height: 40.w,
                    child: Image.asset(
                      item['icon'],
                      width: 40.w,
                      height: 40.w,
                      fit: BoxFit.contain,
                      errorBuilder: (context, error, stackTrace) {
                        return Icon(
                          _getIconByName(item['name']),
                          color: item['color'] as Color,
                          size: 24.w,
                        );
                      },
                    ),
                  ),
                  SizedBox(height: 4.h), // 减少间距
                  // 文字
                  Text(
                    item['name'],
                    style: TextStyle(
                      fontSize: 9.sp, // 减小字体
                      color: const Color(0xFF333333),
                      fontWeight: FontWeight.w500,
                      height: 1.1,
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  IconData _getIconByName(String name) {
    switch (name) {
      case 'AI识宠':
        return Icons.pets;
      case '限时拍卖':
        return Icons.access_time;
      case '品牌专区':
        return Icons.star;
      case '一口价专区':
        return Icons.local_offer;
      case '成交查询':
        return Icons.list_alt;
      case '同城送达':
        return Icons.location_on;
      case '回收查询':
        return Icons.recycling;
      case '合作方及代理':
        return Icons.handshake;
      default:
        return Icons.apps;
    }
  }

  Widget _buildProductList() {
    return Container(
      margin: EdgeInsets.fromLTRB(16.w, 16.h, 16.w, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 限时拍卖专场标题
          Row(
            children: [
              Text(
                '限时拍卖专场',
                style: TextStyle(
                  fontSize: 18.sp,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF333333),
                ),
              ),
              SizedBox(width: 8.w),
              Icon(
                Icons.access_time,
                size: 16.w,
                color: AppColors.primary,
              ),
              SizedBox(width: 4.w),
              Text(
                '限时招募参与',
                style: TextStyle(
                  fontSize: 12.sp,
                  color: AppColors.textHint,
                ),
              ),
            ],
          ),
          SizedBox(height: 12.h),

          // 标签筛选 - 两行布局
          Column(
            children: [
              // 第一行：6个标签
              Wrap(
                spacing: 6.w, // 减少水平间距
                runSpacing: 6.h, // 减少垂直间距
                children: [
                  _buildFilterTag('自定义', true, isPrimary: true),
                  _buildFilterTag('比熊', false),
                  _buildFilterTag('标赛', false),
                  _buildFilterTag('双血统', false),
                  _buildFilterTag('幼犬', false),
                  _buildFilterTag('成犬', false),
                ],
              ),
              SizedBox(height: 6.h), // 减少行间距
              // 第二行：4个标签
              Wrap(
                spacing: 6.w,
                runSpacing: 6.h,
                children: [
                  _buildFilterTag('竞价中', false),
                  _buildFilterTag('即将结束', false),
                  _buildFilterTag('热门推荐', false),
                  _buildFilterTag('新品上架', false),
                ],
              ),
            ],
          ),
          SizedBox(height: 16.h),

          // 专场卡片 - 使用后台数据
          _buildSpecialEventsSection(),
          SizedBox(height: 16.h),

          SizedBox(height: 16.h), // 减少底部空间
        ],
      ),
    );
  }

  Widget _buildFilterTag(String text, bool isSelected,
      {bool isPrimary = false}) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h), // 减少内边距
      decoration: BoxDecoration(
        color: isSelected
            ? (isPrimary ? const Color(0xFF9C4DFF) : Colors.white)
            : Colors.white,
        borderRadius: BorderRadius.circular(16.r), // 减少圆角
        border: Border.all(
          color: isSelected
              ? (isPrimary ? const Color(0xFF9C4DFF) : const Color(0xFF9C4DFF))
              : const Color(0xFF9C4DFF),
          width: 1,
        ),
      ),
      child: Text(
        text,
        textAlign: TextAlign.center,
        style: TextStyle(
          fontSize: 10.sp, // 减小字体大小
          color: isSelected
              ? (isPrimary ? Colors.white : const Color(0xFF9C4DFF))
              : const Color(0xFF9C4DFF),
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildSpecialCard(
    String tag,
    String title,
    String endTime,
    String count,
    String imageUrl,
    Color accentColor,
  ) {
    return GestureDetector(
      onTap: () {
        // 跳转到专场列表页面
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => SpecialEventPage(
              title: title,
              eventId: '1',
            ),
          ),
        );
      },
      child: Container(
        height: 140.h, // Increased height to match design
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(12.r),
          child: Stack(
            children: [
              // Background image covering the entire card
              Positioned.fill(
                child: CachedNetworkImage(
                  imageUrl: imageUrl,
                  fit: BoxFit.cover,
                  placeholder: (context, url) => Container(
                    color: accentColor.withOpacity(0.3),
                  ),
                  errorWidget: (context, url, error) => Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          accentColor.withOpacity(0.8),
                          accentColor,
                        ],
                      ),
                    ),
                  ),
                ),
              ),

              // Gradient overlay
              Positioned.fill(
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.black.withOpacity(0.2),
                        Colors.black.withOpacity(0.6),
                      ],
                    ),
                  ),
                ),
              ),

              // Content
              Padding(
                padding: EdgeInsets.all(12.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding:
                          EdgeInsets.symmetric(horizontal: 8.w, vertical: 3.h),
                      decoration: BoxDecoration(
                        color: accentColor,
                        borderRadius: BorderRadius.circular(10.r),
                      ),
                      child: Text(
                        tag,
                        style: TextStyle(
                          fontSize: 10.sp,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    SizedBox(height: 8.h),
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16.sp,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const Spacer(),
                    Row(
                      children: [
                        Icon(
                          Icons.access_time,
                          size: 14.w,
                          color: Colors.white,
                        ),
                        SizedBox(width: 4.w),
                        Text(
                          endTime,
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 4.h),
                    // 状态信息
                    Text(
                      count,
                      style: TextStyle(
                        fontSize: 12.sp,
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
      ),
    );
  }

  // 构建分类内容
  Widget _buildCategoryContent(String title, List<Map<String, dynamic>> items) {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(), // 使用弹性滚动
      child: Container(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 20.sp,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF333333),
              ),
            ),
            SizedBox(height: 16.h),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12.w,
                mainAxisSpacing: 12.w,
                childAspectRatio: 0.8,
              ),
              itemCount: items.length,
              itemBuilder: (context, index) {
                final item = items[index];
                return Container(
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
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: ClipRRect(
                          borderRadius:
                              BorderRadius.vertical(top: Radius.circular(12.r)),
                          child: CachedNetworkImage(
                            imageUrl: item['image'],
                            width: double.infinity,
                            fit: BoxFit.cover,
                            placeholder: (context, url) => Container(
                              color: AppColors.background,
                              child: Center(
                                child: CircularProgressIndicator(
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                      AppColors.primary),
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                      Padding(
                        padding: EdgeInsets.all(8.w),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item['name'],
                              style: TextStyle(
                                fontSize: 14.sp,
                                fontWeight: FontWeight.w500,
                                color: const Color(0xFF333333),
                              ),
                            ),
                            SizedBox(height: 4.h),
                            Text(
                              '¥${item['price']}',
                              style: TextStyle(
                                fontSize: 16.sp,
                                fontWeight: FontWeight.bold,
                                color: Colors.red,
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
            SizedBox(height: 16.h),
          ],
        ),
      ),
    );
  }

  // 限时拍卖专场内容
  Widget _buildSpecialAuctionContent() {
    return Container(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '限时拍卖专场',
            style: TextStyle(
              fontSize: 20.sp,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF333333),
            ),
          ),
          SizedBox(height: 16.h),
          // 显示加载状态或商品列表
          if (_isLoading)
            ...List.generate(
                3,
                (index) => Container(
                      margin: EdgeInsets.only(bottom: 16.h),
                      child: _buildProductCardSkeleton(),
                    ))
          else if (_hotProducts.isNotEmpty)
            ..._hotProducts
                .map((product) => Container(
                      margin: EdgeInsets.only(bottom: 16.h),
                      child: AuctionCard(
                        product: _convertProductToMap(product),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => ProductDetailPage(
                                  productData: _convertProductToMap(product)),
                            ),
                          );
                        },
                        onFavorite: () {
                          // 处理收藏
                          _toggleFavorite(product);
                        },
                      ),
                    ))
                .toList()
          else
            Container(
              padding: EdgeInsets.all(32.w),
              child: Center(
                child: Column(
                  children: [
                    Icon(
                      Icons.inventory_2_outlined,
                      size: 48.w,
                      color: Colors.grey[400],
                    ),
                    SizedBox(height: 16.h),
                    Text(
                      _errorMessage ?? '暂无商品数据',
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: Colors.grey[600],
                      ),
                    ),
                    SizedBox(height: 16.h),
                    ElevatedButton(
                      onPressed: _refreshData,
                      child: const Text('刷新'),
                    ),
                  ],
                ),
              ),
            ),
          SizedBox(height: 16.h),
        ],
      ),
    );
  }

  // 今日专场内容
  Widget _buildTodaySpecialContent() {
    return Container(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '今日专场',
            style: TextStyle(
              fontSize: 20.sp,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF333333),
            ),
          ),
          SizedBox(height: 16.h),
          _buildSpecialCard(
            '今日专场',
            '精选宠物拍卖',
            '08-10 20:00 结标',
            '拍卖中：156 件',
            'https://picsum.photos/400/200?random=50',
            const Color(0xFF4A90E2),
          ),
          SizedBox(height: 16.h),
          Text(
            '热门商品',
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF333333),
            ),
          ),
          SizedBox(height: 12.h),
          ...auctionProducts
              .take(2)
              .map((product) => Container(
                    margin: EdgeInsets.only(bottom: 16.h),
                    child: AuctionCard(
                      product: product,
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) =>
                                ProductDetailPage(productData: product),
                          ),
                        );
                      },
                      onFavorite: () {},
                    ),
                  ))
              .toList(),
          SizedBox(height: 16.h),
        ],
      ),
    );
  }

  // 山东鱼宠专场内容
  Widget _buildShandongFishContent() {
    return _buildRegionalSpecialContent(
      '山东鱼宠专场',
      '水族专业养殖基地',
      'https://picsum.photos/400/200?random=51',
      const Color(0xFF00BCD4),
    );
  }

  // 苏州宠物专场内容
  Widget _buildSuzhouPetContent() {
    return _buildRegionalSpecialContent(
      '苏州宠物专场',
      '江南宠物精品展示',
      'https://picsum.photos/400/200?random=52',
      const Color(0xFF9C27B0),
    );
  }

  // 地区专场通用内容
  Widget _buildRegionalSpecialContent(
      String title, String subtitle, String imageUrl, Color themeColor) {
    return Container(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 20.sp,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF333333),
            ),
          ),
          SizedBox(height: 8.h),
          Text(
            subtitle,
            style: TextStyle(
              fontSize: 14.sp,
              color: AppColors.textSecondary,
            ),
          ),
          SizedBox(height: 16.h),
          Container(
            height: 120.h,
            width: double.infinity,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12.r),
              gradient: LinearGradient(
                colors: [themeColor.withOpacity(0.8), themeColor],
              ),
            ),
            child: Stack(
              children: [
                Positioned(
                  right: 0,
                  top: 0,
                  bottom: 0,
                  child: ClipRRect(
                    borderRadius: BorderRadius.only(
                      topRight: Radius.circular(12.r),
                      bottomRight: Radius.circular(12.r),
                    ),
                    child: CachedNetworkImage(
                      imageUrl: imageUrl,
                      width: 120.w,
                      height: double.infinity,
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                Padding(
                  padding: EdgeInsets.all(16.w),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: TextStyle(
                          fontSize: 18.sp,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 8.h),
                      Text(
                        '专业养殖，品质保证',
                        style: TextStyle(
                          fontSize: 14.sp,
                          color: Colors.white.withOpacity(0.9),
                        ),
                      ),
                      const Spacer(),
                      Text(
                        '正在进行中...',
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          SizedBox(height: 16.h),
          Text(
            '推荐商品',
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF333333),
            ),
          ),
          SizedBox(height: 12.h),
          ...auctionProducts
              .take(1)
              .map((product) => Container(
                    margin: EdgeInsets.only(bottom: 16.h),
                    child: AuctionCard(
                      product: product,
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) =>
                                ProductDetailPage(productData: product),
                          ),
                        );
                      },
                      onFavorite: () {},
                    ),
                  ))
              .toList(),
          SizedBox(height: 16.h),
        ],
      ),
    );
  }

  // 默认内容
  Widget _buildDefaultContent(String tabName) {
    return Container(
      padding: EdgeInsets.all(16.w),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(height: 100.h),
          Icon(
            Icons.pets,
            size: 64.w,
            color: AppColors.primary,
          ),
          SizedBox(height: 16.h),
          Text(
            '$tabName 内容',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF333333),
            ),
          ),
          SizedBox(height: 8.h),
          Text(
            '更多精彩内容即将上线',
            style: TextStyle(
              fontSize: 14.sp,
              color: AppColors.textSecondary,
            ),
          ),
          SizedBox(height: 200.h),
        ],
      ),
    );
  }

  // 刷新数据
  Future<void> _onRefresh() async {
    await Future.delayed(const Duration(seconds: 2));
    if (mounted) {
      setState(() {
        // 刷新数据
      });
    }
  }

  // 构建宠物页面内容
  Widget _buildPetPageContent() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      child: Column(
        children: [
          SizedBox(height: 16.h),

          // 分类网格
          _buildPetCategoryGrid(),
          SizedBox(height: 16.h),

          // 标签筛选
          _buildPetFilterTags(),
          SizedBox(height: 16.h),

          // 商品列表
          _buildPetProductList(),
          SizedBox(height: 100.h),
        ],
      ),
    );
  }

  // 构建宠物页面搜索栏
  Widget _buildPetSearchBar() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      height: 40.h,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20.r),
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
          SizedBox(width: 16.w),
          Icon(
            Icons.search,
            size: 20.w,
            color: const Color(0xFF9C4DFF),
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: TextField(
              decoration: const InputDecoration(
                hintText: '搜拍品',
                hintStyle: TextStyle(
                  color: Color(0xFF999999),
                ),
                border: InputBorder.none,
              ),
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF333333),
              ),
            ),
          ),
          Container(
            width: 1.w,
            height: 20.h,
            color: const Color(0xFFE0E0E0),
          ),
          SizedBox(width: 12.w),
          Text(
            '搜索',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF9C4DFF),
              fontWeight: FontWeight.w500,
            ),
          ),
          SizedBox(width: 16.w),
        ],
      ),
    );
  }

  // 构建宠物分类网格
  Widget _buildPetCategoryGrid() {
    // 第一行：宠物分期 - 单独背景卡
    final topRowCategories = [
      {'name': '宠物分期', 'icon': Icons.percent, 'color': const Color(0xFFFFB74D)},
      {'name': '宠粮', 'icon': Icons.food_bank, 'color': const Color(0xFF9C77FF)},
      {
        'name': '宠药',
        'icon': Icons.medical_services,
        'color': const Color(0xFFFF6B6B)
      },
      {'name': '宠物店', 'icon': Icons.store, 'color': const Color(0xFFFFEB3B)},
      {
        'name': '店铺排行',
        'icon': Icons.emoji_events,
        'color': const Color(0xFF4ECDC4)
      },
    ];

    // 下面10个分类
    final bottomCategories = [
      {'name': '猫咪', 'icon': Icons.pets, 'color': const Color(0xFF6FA8DC)},
      {'name': '狗狗', 'icon': Icons.pets, 'color': const Color(0xFFFFB347)},
      {'name': '爬宠', 'icon': Icons.pets, 'color': const Color(0xFF90EE90)},
      {'name': '小宠', 'icon': Icons.pets, 'color': const Color(0xFFDDA0DD)},
      {'name': '鹦鹉', 'icon': Icons.pets, 'color': const Color(0xFFFF6347)},
      {'name': '鸟类', 'icon': Icons.pets, 'color': const Color(0xFF87CEEB)},
      {
        'name': '昆虫',
        'icon': Icons.bug_report,
        'color': const Color(0xFF8FBC8F)
      },
      {'name': '大型宠物', 'icon': Icons.pets, 'color': const Color(0xFFFFB6C1)},
      {'name': '变异宠物', 'icon': Icons.star, 'color': const Color(0xFFFFE5B4)},
      {
        'name': '宠物批发',
        'icon': Icons.business,
        'color': const Color(0xFF87CEFA)
      },
    ];

    return Column(
      children: [
        // 顶部5个分类 - 单独背景卡
        Container(
          margin: EdgeInsets.symmetric(horizontal: 16.w, vertical: 4.h),
          padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 12.h),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12.r),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: SizedBox(
            height: 65.h, // 进一步减少高度
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: topRowCategories.map((category) {
                return Expanded(
                  child: _buildCategoryItem(category),
                );
              }).toList(),
            ),
          ),
        ),

        SizedBox(height: 8.h),

        // 下面10个分类 - 单独背景卡
        Container(
          margin: EdgeInsets.symmetric(horizontal: 16.w, vertical: 4.h),
          padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 12.h),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12.r),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: SizedBox(
            height: 130.h, // 进一步减少高度
            child: GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 5,
                crossAxisSpacing: 6.w,
                mainAxisSpacing: 6.h,
                childAspectRatio: 1.1,
              ),
              itemCount: bottomCategories.length,
              itemBuilder: (context, index) {
                final category = bottomCategories[index];
                return _buildCategoryItem(category);
              },
            ),
          ),
        ),
      ],
    );
  }

  // 构建分类项目
  Widget _buildCategoryItem(Map<String, dynamic> category) {
    return GestureDetector(
      onTap: () {
        print('点击了${category['name']}');
      },
      child: Container(
        constraints: BoxConstraints(maxHeight: 55.h), // 进一步减少最大高度
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 34.w, // 减小图标容器
              height: 34.w,
              decoration: BoxDecoration(
                color: category['color'] as Color,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: (category['color'] as Color).withOpacity(0.2),
                    blurRadius: 2,
                    offset: const Offset(0, 1),
                  ),
                ],
              ),
              child: Icon(
                category['icon'] as IconData,
                size: 18.w, // 减小图标大小
                color: Colors.white,
              ),
            ),
            SizedBox(height: 3.h), // 减小间距
            Flexible(
              child: Text(
                category['name'] as String,
                style: TextStyle(
                  fontSize: 8.sp, // 减小字体
                  color: const Color(0xFF333333),
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建宠物页面标签筛选
  Widget _buildPetFilterTags() {
    final tags = ['标签', '标签', '标签', '标签', '标签', '标签', '标签'];

    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: tags.map((tag) {
          final isSelected = false; // 从设计图看都没有选中状态
          return GestureDetector(
            onTap: () {
              print('点击了标签: $tag');
            },
            child: Container(
              width: 40.w,
              height: 20.h,
              decoration: BoxDecoration(
                color: const Color(0xFF9C4DFF),
                borderRadius: BorderRadius.circular(10.r),
              ),
              child: Center(
                child: Text(
                  tag,
                  style: TextStyle(
                    fontSize: 10.sp,
                    color: Colors.white,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // 构建宠物商品列表
  Widget _buildPetProductList() {
    final products = [
      {
        'id': 1, // 添加真实ID
        'title': '宠物标题宠物标题宠物标题宠物标题宠物标题',
        'name': '宠物标题宠物标题宠物标题宠物标题宠物标题',
        'price': 432,
        'starting_price': 432,
        'image': 'https://picsum.photos/200/200?random=40',
        'images': ['https://picsum.photos/200/200?random=40'],
        'isFavorite': false,
        'isBoutique': true,
        'timeLeft': '今天20:05截拍',
      },
      {
        'id': 2, // 添加真实ID
        'title': '宠物标题宠物标题宠物标题宠物标题宠物',
        'name': '宠物标题宠物标题宠物标题宠物标题宠物',
        'price': 432,
        'starting_price': 432,
        'image': 'https://picsum.photos/200/200?random=41',
        'images': ['https://picsum.photos/200/200?random=41'],
        'isFavorite': true,
        'isBoutique': true,
        'timeLeft': '今天20:05截拍',
      },
    ];

    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          Expanded(
            child: _buildPetProductCard(products[0]),
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: _buildPetProductCard(products[1]),
          ),
        ],
      ),
    );
  }

  // 构建宠物商品卡片
  Widget _buildPetProductCard(Map<String, dynamic> product) {
    return GestureDetector(
      onTap: () {
        print('点击了商品: ${product['name']}');
      },
      child: Container(
        height: 200.h, // 减少总高度
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 商品图片
            SizedBox(
              height: 120.h, // 固定图片高度
              width: double.infinity,
              child: Stack(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(8.r),
                      topRight: Radius.circular(8.r),
                    ),
                    child: CachedNetworkImage(
                      imageUrl: product['image'],
                      fit: BoxFit.cover,
                      width: double.infinity,
                      height: double.infinity,
                      placeholder: (context, url) => Container(
                        color: const Color(0xFFF5F5F5),
                        child: const Center(
                          child: CircularProgressIndicator(),
                        ),
                      ),
                      errorWidget: (context, url, error) => Container(
                        color: const Color(0xFFF5F5F5),
                        child: const Icon(Icons.error),
                      ),
                    ),
                  ),
                  // 精品标签
                  if (product['isBoutique'])
                    Positioned(
                      top: 4.h,
                      left: 4.w,
                      child: Container(
                        padding: EdgeInsets.symmetric(
                            horizontal: 4.w, vertical: 1.h),
                        decoration: BoxDecoration(
                          color: const Color(0xFF9C4DFF),
                          borderRadius: BorderRadius.circular(2.r),
                        ),
                        child: Text(
                          '精品',
                          style: TextStyle(
                            fontSize: 7.sp,
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  // 右下角收藏图标
                  Positioned(
                    bottom: 4.h,
                    right: 4.w,
                    child: Icon(
                      Icons.favorite_border,
                      size: 14.w,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
            // 商品信息
            Expanded(
              child: Padding(
                padding: EdgeInsets.all(6.w), // 减少内边距
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Flexible(
                      child: Text(
                        product['name'],
                        style: TextStyle(
                          fontSize: 10.sp, // 减小字体
                          color: const Color(0xFF333333),
                          fontWeight: FontWeight.w500,
                          height: 1.2,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    SizedBox(height: 2.h),
                    Text(
                      '¥${product['price']}',
                      style: TextStyle(
                        fontSize: 14.sp, // 减小字体
                        color: const Color(0xFFFF5722),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    SizedBox(height: 1.h),
                    Text(
                      '无理由',
                      style: TextStyle(
                        fontSize: 8.sp,
                        color: const Color(0xFF999999),
                      ),
                    ),
                    SizedBox(height: 1.h),
                    Text(
                      '①${product['timeLeft']}',
                      style: TextStyle(
                        fontSize: 8.sp,
                        color: const Color(0xFF9C4DFF),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建水族页面内容
  Widget _buildAquaticPageContent() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      child: Column(
        children: [
          SizedBox(height: 16.h),

          // 顶部3个分类卡片
          _buildAquaticTopCards(),
          SizedBox(height: 16.h),

          // 12个分类网格
          _buildAquaticCategoryGrid(),
          SizedBox(height: 16.h),

          // 标签筛选
          _buildAquaticFilterTags(),
          SizedBox(height: 16.h),

          // 商品列表
          _buildAquaticProductList(),
          SizedBox(height: 100.h),
        ],
      ),
    );
  }

  // 构建水族顶部3个分类卡片
  Widget _buildAquaticTopCards() {
    final topCards = [
      {
        'name': '粮类',
        'icon': Icons.pets,
        'color': const Color(0xFFFF8A65),
        'hasRedDot': true
      },
      {
        'name': '药品',
        'icon': Icons.medical_services,
        'color': const Color(0xFFFFD54F),
        'hasRedDot': false
      },
      {
        'name': '鱼缸',
        'icon': Icons.water,
        'color': const Color(0xFF81C784),
        'hasRedDot': true
      },
    ];

    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w, vertical: 4.h),
      padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 12.h),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: SizedBox(
        height: 65.h,
        child: Row(
          children: [
            Expanded(
              child: _buildAquaticTopCardItem(topCards[0]),
            ),
            Expanded(
              child: _buildAquaticTopCardItem(topCards[1]),
            ),
            Expanded(
              child: _buildAquaticTopCardItem(topCards[2]),
            ),
          ],
        ),
      ),
    );
  }

  // 构建水族顶部卡片项目
  Widget _buildAquaticTopCardItem(Map<String, dynamic> card) {
    return GestureDetector(
      onTap: () {
        print('点击了${card['name']}');
      },
      child: Container(
        constraints: BoxConstraints(maxHeight: 55.h),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Stack(
              clipBehavior: Clip.none,
              children: [
                Container(
                  width: 34.w,
                  height: 34.w,
                  decoration: BoxDecoration(
                    color: card['color'] as Color,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: (card['color'] as Color).withOpacity(0.2),
                        blurRadius: 2,
                        offset: const Offset(0, 1),
                      ),
                    ],
                  ),
                  child: Icon(
                    card['icon'] as IconData,
                    size: 18.w,
                    color: Colors.white,
                  ),
                ),
                // 红点提示 - 相对于圆形图标定位
                if (card['hasRedDot'] == true)
                  Positioned(
                    top: -2.h, // 稍微突出圆形顶部
                    right: -2.w, // 稍微突出圆形右侧
                    child: Container(
                      width: 8.w,
                      height: 8.w,
                      decoration: const BoxDecoration(
                        color: Colors.red,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
              ],
            ),
            SizedBox(height: 3.h),
            Text(
              card['name'] as String,
              style: TextStyle(
                fontSize: 8.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  // 构建水族分类网格
  Widget _buildAquaticCategoryGrid() {
    final categories = [
      {'name': '鱼类', 'icon': Icons.pets, 'color': const Color(0xFFFF8A65)},
      {'name': '两栖类', 'icon': Icons.pets, 'color': const Color(0xFF81C784)},
      {'name': '哺乳类', 'icon': Icons.pets, 'color': const Color(0xFF4FC3F7)},
      {'name': '两栖爬行', 'icon': Icons.pets, 'color': const Color(0xFFFFD54F)},
      {'name': '海洋生物', 'icon': Icons.waves, 'color': const Color(0xFFFF7043)},
      {'name': '水族用品', 'icon': Icons.build, 'color': const Color(0xFF9575CD)},
      {
        'name': '鱼缸造景',
        'icon': Icons.landscape,
        'color': const Color(0xFF64B5F6)
      },
      {'name': '水草', 'icon': Icons.grass, 'color': const Color(0xFF81C784)},
    ];

    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w, vertical: 4.h),
      padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 12.h),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: SizedBox(
        height: 170.h, // 继续增加高度
        child: GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 4,
            crossAxisSpacing: 6.w, // 稍微减少水平间距
            mainAxisSpacing: 2.h, // 大幅减少行间距
            childAspectRatio: 0.75, // 进一步调整比例给文字更多空间
          ),
          itemCount: categories.length,
          itemBuilder: (context, index) {
            final category = categories[index];
            return _buildAquaticCategoryItem(category);
          },
        ),
      ),
    );
  }

  // 构建水族分类项目
  Widget _buildAquaticCategoryItem(Map<String, dynamic> category) {
    return GestureDetector(
      onTap: () {
        print('点击了${category['name']}');
      },
      child: Container(
        constraints: BoxConstraints(maxHeight: 80.h), // 继续增加最大高度
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.start, // 改为顶部对齐
          children: [
            Container(
              width: 28.w, // 继续减小图标尺寸
              height: 28.w,
              decoration: BoxDecoration(
                color: category['color'] as Color,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: (category['color'] as Color).withOpacity(0.2),
                    blurRadius: 2,
                    offset: const Offset(0, 1),
                  ),
                ],
              ),
              child: Icon(
                category['icon'] as IconData,
                size: 14.w, // 继续减小图标大小
                color: Colors.white,
              ),
            ),
            SizedBox(height: 6.h), // 增加间距
            Expanded(
              child: Container(
                alignment: Alignment.topCenter,
                child: Text(
                  category['name'] as String,
                  style: TextStyle(
                    fontSize: 8.sp, // 稍微减小字体确保显示
                    color: const Color(0xFF333333),
                    fontWeight: FontWeight.w500,
                    height: 1.0,
                  ),
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建水族标签筛选
  Widget _buildAquaticFilterTags() {
    final tags = ['标签', '标签', '标签', '标签', '标签', '标签', '标签'];

    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: tags.map((tag) {
          return GestureDetector(
            onTap: () {
              print('点击了标签: $tag');
            },
            child: Container(
              width: 40.w,
              height: 20.h,
              decoration: BoxDecoration(
                color: const Color(0xFF9C4DFF),
                borderRadius: BorderRadius.circular(10.r),
              ),
              child: Center(
                child: Text(
                  tag,
                  style: TextStyle(
                    fontSize: 10.sp,
                    color: Colors.white,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // 构建水族商品列表
  Widget _buildAquaticProductList() {
    final products = [
      {
        'name': '宠物标题宠物标题宠物标题宠物标题宠物标题',
        'price': 432,
        'image': 'https://picsum.photos/200/200?random=50',
        'isFavorite': false,
        'isBoutique': true,
        'timeLeft': '今天20:05截拍',
      },
      {
        'name': '宠物标题宠物标题宠物标题宠物标题宠物',
        'price': 432,
        'image': 'https://picsum.photos/200/200?random=51',
        'isFavorite': true,
        'isBoutique': true,
        'timeLeft': '今天20:05截拍',
      },
    ];

    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          Expanded(
            child: _buildAquaticProductCard(products[0]),
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: _buildAquaticProductCard(products[1]),
          ),
        ],
      ),
    );
  }

  // 构建水族商品卡片
  Widget _buildAquaticProductCard(Map<String, dynamic> product) {
    return GestureDetector(
      onTap: () {
        print('点击了商品: ${product['name']}');
      },
      child: Container(
        height: 200.h,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 商品图片
            SizedBox(
              height: 120.h,
              width: double.infinity,
              child: Stack(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(8.r),
                      topRight: Radius.circular(8.r),
                    ),
                    child: CachedNetworkImage(
                      imageUrl: product['image'],
                      fit: BoxFit.cover,
                      width: double.infinity,
                      height: double.infinity,
                      placeholder: (context, url) => Container(
                        color: const Color(0xFFF5F5F5),
                        child: const Center(
                          child: CircularProgressIndicator(),
                        ),
                      ),
                      errorWidget: (context, url, error) => Container(
                        color: const Color(0xFFF5F5F5),
                        child: const Icon(Icons.error),
                      ),
                    ),
                  ),
                  // 精品标签
                  if (product['isBoutique'])
                    Positioned(
                      top: 4.h,
                      left: 4.w,
                      child: Container(
                        padding: EdgeInsets.symmetric(
                            horizontal: 4.w, vertical: 1.h),
                        decoration: BoxDecoration(
                          color: const Color(0xFF9C4DFF),
                          borderRadius: BorderRadius.circular(2.r),
                        ),
                        child: Text(
                          '精品',
                          style: TextStyle(
                            fontSize: 7.sp,
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  // 右下角收藏图标
                  Positioned(
                    bottom: 4.h,
                    right: 4.w,
                    child: Icon(
                      product['isFavorite']
                          ? Icons.favorite
                          : Icons.favorite_border,
                      size: 14.w,
                      color: product['isFavorite']
                          ? const Color(0xFFFFEB3B)
                          : Colors.white,
                    ),
                  ),
                ],
              ),
            ),
            // 商品信息
            Expanded(
              child: Padding(
                padding: EdgeInsets.all(6.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Flexible(
                      child: Text(
                        product['name'],
                        style: TextStyle(
                          fontSize: 10.sp,
                          color: const Color(0xFF333333),
                          fontWeight: FontWeight.w500,
                          height: 1.2,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    SizedBox(height: 2.h),
                    Text(
                      '¥${product['price']}',
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: const Color(0xFFFF5722),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    SizedBox(height: 1.h),
                    Text(
                      '无理由',
                      style: TextStyle(
                        fontSize: 8.sp,
                        color: const Color(0xFF999999),
                      ),
                    ),
                    SizedBox(height: 1.h),
                    Text(
                      '①${product['timeLeft']}',
                      style: TextStyle(
                        fontSize: 8.sp,
                        color: const Color(0xFF9C4DFF),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建一口价页面内容
  Widget _buildFixedPricePageContent() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      child: Column(
        children: [
          SizedBox(height: 16.h),

          // 上新和热门商品行
          _buildFixedPriceTopSections(),
          SizedBox(height: 16.h),

          // 宠物分类横向滚动列表
          _buildFixedPriceCategorySection(),
          SizedBox(height: 16.h),

          // 底部商品网格列表
          _buildFixedPriceProductGrid(),
          SizedBox(height: 100.h),
        ],
      ),
    );
  }

  // 构建一口价页面顶部上新和热门商品行
  Widget _buildFixedPriceTopSections() {
    return Column(
      children: [
        // 上新商品行
        _buildFixedPriceProductRow('上新', [
          {
            'name': '刚刚上新',
            'price': 432,
            'image': 'https://picsum.photos/200/200?random=60',
            'tag': '刚刚上新',
          },
          {
            'name': '刚刚上新',
            'price': 432,
            'image': 'https://picsum.photos/200/200?random=61',
            'tag': '刚刚上新',
          },
        ]),
        SizedBox(height: 16.h),
        // 热门商品行
        _buildFixedPriceProductRow('热门', [
          {
            'name': '标题标题标...',
            'price': 432,
            'image': 'https://picsum.photos/200/200?random=62',
            'tag': '',
          },
          {
            'name': '标题标题标...',
            'price': 432,
            'image': 'https://picsum.photos/200/200?random=63',
            'tag': '',
          },
        ]),
      ],
    );
  }

  // 构建一口价商品行
  Widget _buildFixedPriceProductRow(
      String title, List<Map<String, dynamic>> products) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.w600,
                  color: const Color(0xFF333333),
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                size: 14.w,
                color: const Color(0xFF999999),
              ),
            ],
          ),
          SizedBox(height: 12.h),
          Row(
            children: products.map((product) {
              return Expanded(
                child: Container(
                  margin: EdgeInsets.only(
                      right: products.indexOf(product) == products.length - 1
                          ? 0
                          : 12.w),
                  child: _buildFixedPriceProductCard(product),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  // 构建一口价商品卡片
  Widget _buildFixedPriceProductCard(Map<String, dynamic> product) {
    return GestureDetector(
      onTap: () {
        print('点击了商品: ${product['name']}');
      },
      child: Container(
        height: 180.h,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 商品图片
            Expanded(
              flex: 3,
              child: Stack(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(8.r),
                      topRight: Radius.circular(8.r),
                    ),
                    child: CachedNetworkImage(
                      imageUrl: product['image'],
                      fit: BoxFit.cover,
                      width: double.infinity,
                      height: double.infinity,
                      placeholder: (context, url) => Container(
                        color: const Color(0xFFF5F5F5),
                        child: const Center(
                          child: CircularProgressIndicator(),
                        ),
                      ),
                      errorWidget: (context, url, error) => Container(
                        color: const Color(0xFFF5F5F5),
                        child: const Icon(Icons.error),
                      ),
                    ),
                  ),
                  // 标签
                  if (product['tag'] != null &&
                      product['tag'].toString().isNotEmpty)
                    Positioned(
                      top: 6.h,
                      left: 6.w,
                      child: Container(
                        padding: EdgeInsets.symmetric(
                            horizontal: 6.w, vertical: 2.h),
                        decoration: BoxDecoration(
                          color: const Color(0xFF4CAF50),
                          borderRadius: BorderRadius.circular(2.r),
                        ),
                        child: Text(
                          product['tag'],
                          style: TextStyle(
                            fontSize: 8.sp,
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
            // 商品信息
            Expanded(
              flex: 2,
              child: Padding(
                padding: EdgeInsets.all(8.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      product['name'],
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: const Color(0xFF333333),
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    Text(
                      '¥${product['price']}',
                      style: TextStyle(
                        fontSize: 16.sp,
                        color: const Color(0xFFFF5722),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建宠物分类横向滚动区域
  Widget _buildFixedPriceCategorySection() {
    final categories = [
      {'name': '猫咪', 'icon': Icons.pets, 'color': const Color(0xFFFFB347)},
      {'name': '狗狗', 'icon': Icons.pets, 'color': const Color(0xFFFF8A65)},
      {'name': '爬宠', 'icon': Icons.pets, 'color': const Color(0xFF81C784)},
      {'name': '小宠', 'icon': Icons.pets, 'color': const Color(0xFFDDA0DD)},
      {'name': '鹦鹉', 'icon': Icons.pets, 'color': const Color(0xFFFF6347)},
      {'name': '鸟类', 'icon': Icons.pets, 'color': const Color(0xFF87CEEB)},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          margin: EdgeInsets.symmetric(horizontal: 16.w),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '宠物分类',
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.w600,
                  color: const Color(0xFF333333),
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                size: 14.w,
                color: const Color(0xFF999999),
              ),
            ],
          ),
        ),
        SizedBox(height: 12.h),
        Container(
          height: 80.h,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: EdgeInsets.symmetric(horizontal: 16.w),
            itemCount: categories.length,
            itemBuilder: (context, index) {
              final category = categories[index];
              return Container(
                width: 70.w,
                margin: EdgeInsets.only(right: 16.w),
                child: _buildFixedPriceCategoryItem(category),
              );
            },
          ),
        ),
      ],
    );
  }

  // 构建一口价分类项目
  Widget _buildFixedPriceCategoryItem(Map<String, dynamic> category) {
    return GestureDetector(
      onTap: () {
        print('点击了分类: ${category['name']}');
      },
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 50.w,
            height: 50.w,
            decoration: BoxDecoration(
              color: category['color'] as Color,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: (category['color'] as Color).withOpacity(0.3),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Icon(
              category['icon'] as IconData,
              size: 28.w,
              color: Colors.white,
            ),
          ),
          SizedBox(height: 6.h),
          Text(
            category['name'] as String,
            style: TextStyle(
              fontSize: 12.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  // 构建底部商品网格列表
  Widget _buildFixedPriceProductGrid() {
    final products = [
      {
        'name': '宠物标题宠物标题宠物',
        'price': 432,
        'image': 'https://picsum.photos/200/200?random=70',
        'shop': '水族馆',
      },
      {
        'name': '宠物标题宠物标题宠物',
        'price': 432,
        'image': 'https://picsum.photos/200/200?random=71',
        'shop': '水族馆',
      },
      {
        'name': '宠物标题宠物标题宠物',
        'price': 432,
        'image': 'https://picsum.photos/200/200?random=72',
        'shop': '水族馆',
      },
      {
        'name': '宠物标题宠物标题宠物',
        'price': 432,
        'image': 'https://picsum.photos/200/200?random=73',
        'shop': '水族馆',
      },
    ];

    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 12.w,
          mainAxisSpacing: 12.h,
          childAspectRatio: 0.8,
        ),
        itemCount: products.length,
        itemBuilder: (context, index) {
          final product = products[index];
          return _buildFixedPriceGridCard(product);
        },
      ),
    );
  }

  // 构建网格商品卡片
  Widget _buildFixedPriceGridCard(Map<String, dynamic> product) {
    return GestureDetector(
      onTap: () {
        print('点击了商品: ${product['name']}');
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 商品图片
            Expanded(
              flex: 3,
              child: ClipRRect(
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(8.r),
                  topRight: Radius.circular(8.r),
                ),
                child: CachedNetworkImage(
                  imageUrl: product['image'],
                  fit: BoxFit.cover,
                  width: double.infinity,
                  height: double.infinity,
                  placeholder: (context, url) => Container(
                    color: const Color(0xFFF5F5F5),
                    child: const Center(
                      child: CircularProgressIndicator(),
                    ),
                  ),
                  errorWidget: (context, url, error) => Container(
                    color: const Color(0xFFF5F5F5),
                    child: const Icon(Icons.error),
                  ),
                ),
              ),
            ),
            // 商品信息
            Expanded(
              flex: 2,
              child: Padding(
                padding: EdgeInsets.all(8.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      product['name'],
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: const Color(0xFF333333),
                        fontWeight: FontWeight.w500,
                        height: 1.2,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '¥${product['price']}',
                          style: TextStyle(
                            fontSize: 16.sp,
                            color: const Color(0xFFFF5722),
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        SizedBox(height: 4.h),
                        Row(
                          children: [
                            Container(
                              width: 16.w,
                              height: 16.w,
                              decoration: const BoxDecoration(
                                color: Color(0xFF666666),
                                shape: BoxShape.circle,
                              ),
                              child: Icon(
                                Icons.store,
                                size: 10.w,
                                color: Colors.white,
                              ),
                            ),
                            SizedBox(width: 4.w),
                            Text(
                              product['shop'],
                              style: TextStyle(
                                fontSize: 10.sp,
                                color: const Color(0xFF666666),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建同城服务页面内容
  Widget _buildLocalServicesPageContent() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      child: Container(
        padding: EdgeInsets.all(16.w),
        child: Column(
          children: [
            SizedBox(height: 8.h),
            _buildLocalServicesGrid(),
            SizedBox(height: 100.h),
          ],
        ),
      ),
    );
  }

  // 构建同城服务网格
  Widget _buildLocalServicesGrid() {
    final services = [
      {
        'title': '宠物交流',
        'subtitle': '分享宠物心得',
        'icon': Icons.chat,
        'color': const Color(0xFFFFF59D), // 黄色
      },
      {
        'title': '宠物配种',
        'subtitle': '寻找理想伴侣',
        'icon': Icons.favorite,
        'color': const Color(0xFFD1C4E9), // 紫色
      },
      {
        'title': '本地宠店',
        'subtitle': '发现附近好店',
        'icon': Icons.store,
        'color': const Color(0xFFFFCDD2), // 粉色
      },
      {
        'title': '鱼缸造景',
        'subtitle': '定制水族景观',
        'icon': Icons.water,
        'color': const Color(0xFFFFF59D), // 黄色
      },
      {
        'title': '同城快取',
        'subtitle': '快速自取服务',
        'icon': Icons.local_shipping,
        'color': const Color(0xFFD1C4E9), // 紫色
      },
      {
        'title': '上门服务',
        'subtitle': '专业到家服务',
        'icon': Icons.home,
        'color': const Color(0xFFFFCDD2), // 粉色
      },
      {
        'title': '宠物估价',
        'subtitle': '专业估价服务',
        'icon': Icons.assessment,
        'color': const Color(0xFFFFF59D), // 黄色
      },
      {
        'title': '附近',
        'subtitle': '发现身边好物',
        'icon': Icons.location_on,
        'color': const Color(0xFFD1C4E9), // 紫色
      },
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16.w,
        mainAxisSpacing: 16.h,
        childAspectRatio: 1.0,
      ),
      itemCount: services.length,
      itemBuilder: (context, index) {
        final service = services[index];
        return _buildLocalServiceCard(service);
      },
    );
  }

  // 构建同城服务卡片
  Widget _buildLocalServiceCard(Map<String, dynamic> service) {
    return GestureDetector(
      onTap: () {
        if (service['title'] == '宠物交流') {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const PetSocialPage()),
          );
        } else if (service['title'] == '本地宠店') {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const LocalPetStoresPage()),
          );
        } else if (service['title'] == '鱼缸造景') {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AquariumDesignPage()),
          );
        } else if (service['title'] == '上门服务') {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const DoorServicePage()),
          );
        } else {
          print('点击了服务: ${service['title']}');
        }
      },
      child: Container(
        decoration: BoxDecoration(
          color: service['color'] as Color,
          borderRadius: BorderRadius.circular(16.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Stack(
          children: [
            // 背景装饰图案
            Positioned(
              top: -20.h,
              right: -20.w,
              child: Container(
                width: 80.w,
                height: 80.w,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
              ),
            ),
            Positioned(
              bottom: -30.h,
              left: -30.w,
              child: Container(
                width: 100.w,
                height: 100.w,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.05),
                  shape: BoxShape.circle,
                ),
              ),
            ),
            // 内容
            Padding(
              padding: EdgeInsets.all(20.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 图标
                  Container(
                    width: 48.w,
                    height: 48.w,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.9),
                      borderRadius: BorderRadius.circular(12.r),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Icon(
                      service['icon'] as IconData,
                      size: 24.w,
                      color: service['color'] as Color,
                    ),
                  ),
                  const Spacer(),
                  // 标题
                  Text(
                    service['title'] as String,
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.bold,
                      color: Colors.red,
                    ),
                  ),
                  SizedBox(height: 4.h),
                  // 副标题
                  Text(
                    service['subtitle'] as String,
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: Colors.black87,
                      fontWeight: FontWeight.w500,
                    ),
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
