import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../constants/app_colors.dart';
import '../../widgets/auction_card.dart';
import '../../widgets/banner_swiper.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> with TickerProviderStateMixin {
  late TabController _tabController;
  late PageController _pageController;
  int _currentTabIndex = 0;

  final List<String> tabs = [
    '首页·AI',
    '宠物',
    '水族',
    '一口价',
    '同城',
    '限时拍卖',
    '今日专场',
    '山东鱼宠专场',
    '苏州宠物专场'
  ];

  // 功能网格数据
  final List<Map<String, dynamic>> functionGrid = [
    {
      'name': 'AI识宠',
      'icon': 'assets/icons/ai_pet.png',
      'color': Color(0xFFFF9500)
    },
    {
      'name': '限时拍卖',
      'icon': 'assets/icons/time_auction.png',
      'color': Color(0xFF9C27B0)
    },
    {
      'name': '品牌专区',
      'icon': 'assets/icons/brand_zone.png',
      'color': Color(0xFFF44336)
    },
    {
      'name': '一口价专区',
      'icon': 'assets/icons/fixed_price.png',
      'color': Color(0xFF2196F3)
    },
    {
      'name': '成交查询',
      'icon': 'assets/icons/deal_query.png',
      'color': Color(0xFF9C27B0)
    },
    {
      'name': '同城送达',
      'icon': 'assets/icons/local_delivery.png',
      'color': Color(0xFF4CAF50)
    },
    {
      'name': '回收查询',
      'icon': 'assets/icons/recycle_query.png',
      'color': Color(0xFFFF9800)
    },
    {
      'name': '合作方及代理',
      'icon': 'assets/icons/partnership.png',
      'color': Color(0xFF673AB7)
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
    _tabController = TabController(length: tabs.length, vsync: this);
    _pageController = PageController(initialPage: 0);

    _tabController.addListener(() {
      if (_tabController.indexIsChanging) {
        setState(() {
          _currentTabIndex = _tabController.index;
        });
        _pageController.animateToPage(
          _tabController.index,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // 紫色渐变顶部区域
          Container(
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
                ],
              ),
            ),
          ),

          // 主内容区域
          Expanded(
            child: Container(
              color: const Color(0xFFF5F5F5),
              child: PageView.builder(
                controller: _pageController,
                onPageChanged: (index) {
                  setState(() {
                    _currentTabIndex = index;
                  });
                  _tabController.animateTo(index);
                },
                itemCount: tabs.length,
                itemBuilder: (context, index) {
                  return _buildTabContent(index);
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      height: 36.h,
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(18.r),
        border: Border.all(color: Colors.white.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          SizedBox(width: 12.w),
          Icon(
            Icons.search,
            size: 20.w,
            color: Colors.white,
          ),
          SizedBox(width: 8.w),
          Expanded(
            child: Text(
              '搜拍品',
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.white.withOpacity(0.8),
              ),
            ),
          ),
          Container(
            margin: EdgeInsets.only(right: 8.w),
            padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 4.h),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12.r),
              border: Border.all(color: Colors.white.withOpacity(0.3)),
            ),
            child: Text(
              '搜索',
              style: TextStyle(
                fontSize: 12.sp,
                color: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      height: 40.h,
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: tabs.asMap().entries.map((entry) {
          final index = entry.key;
          final tab = entry.value;
          final isSelected = index == _currentTabIndex;
          final isFirst = index == 0;

          return GestureDetector(
            onTap: () {
              setState(() {
                _currentTabIndex = index;
              });
              _tabController.animateTo(index);
            },
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h),
              decoration: BoxDecoration(
                color: isSelected ? Colors.white : Colors.transparent,
                borderRadius: BorderRadius.circular(20.r),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (isFirst) ...[
                    Container(
                      padding:
                          EdgeInsets.symmetric(horizontal: 4.w, vertical: 1.h),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFEB3B),
                        borderRadius: BorderRadius.circular(8.r),
                      ),
                      child: Text(
                        '推荐',
                        style: TextStyle(
                          fontSize: 10.sp,
                          color: Colors.black,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    SizedBox(width: 4.w),
                  ],
                  Text(
                    tab,
                    style: TextStyle(
                      fontSize: 14.sp,
                      color:
                          isSelected ? const Color(0xFF9C4DFF) : Colors.white,
                      fontWeight:
                          isSelected ? FontWeight.w600 : FontWeight.normal,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildBannerSection() {
    return Container(
      margin:
          EdgeInsets.symmetric(horizontal: 8.w, vertical: 12.h), // 减少边距让轮播图更宽
      child: BannerSwiper(
        images: [
          'https://picsum.photos/400/200?random=1&sig=banner1',
          'https://picsum.photos/400/200?random=2&sig=banner2',
          'https://picsum.photos/400/200?random=3&sig=banner3',
          'https://picsum.photos/400/200?random=4&sig=banner4',
        ],
        onTap: (index) {
          // 轮播图点击事件
          print('Banner clicked: $index');
        },
      ),
    );
  }

  Widget _buildFunctionGrid() {
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
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 4,
          childAspectRatio: 1,
          crossAxisSpacing: 16.w,
          mainAxisSpacing: 16.h,
        ),
        itemCount: functionGrid.length,
        itemBuilder: (context, index) {
          final item = functionGrid[index];
          return GestureDetector(
            onTap: () {
              // 处理功能点击
              print('点击了：${item['name']}');
            },
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 48.w,
                  height: 48.w,
                  decoration: BoxDecoration(
                    color: (item['color'] as Color).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12.r),
                  ),
                  child: Icon(
                    _getIconByName(item['name']),
                    color: item['color'] as Color,
                    size: 24.w,
                  ),
                ),
                SizedBox(height: 8.h),
                Text(
                  item['name'],
                  style: TextStyle(
                    fontSize: 11.sp,
                    color: const Color(0xFF333333),
                    fontWeight: FontWeight.w500,
                  ),
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
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

          // 标签筛选
          Container(
            height: 32.h,
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: [
                _buildFilterTag('全部', true),
                _buildFilterTag('比熊', false),
                _buildFilterTag('标赛', false),
                _buildFilterTag('标赛', false),
                _buildFilterTag('标赛', false),
                _buildFilterTag('新秀', false),
              ],
            ),
          ),
          SizedBox(height: 16.h),

          // 专场卡片
          Row(
            children: [
              Expanded(
                child: _buildSpecialCard(
                  '今日专场',
                  '山东鱼宠专场',
                  '08-10 20:00 结标',
                  '拍卖中：500 件',
                  'https://picsum.photos/200/150?random=20',
                  const Color(0xFF4A90E2),
                ),
              ),
              SizedBox(width: 12.w),
              Expanded(
                child: _buildSpecialCard(
                  '今日专场',
                  '苏州宠物专场',
                  '08-10 20:00 结标',
                  '拍卖中：432 件',
                  'https://picsum.photos/200/150?random=21',
                  const Color(0xFF7B68EE),
                ),
              ),
            ],
          ),
          SizedBox(height: 16.h),

          // 热门拍卖商品
          Text(
            '热门拍卖',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF333333),
            ),
          ),
          SizedBox(height: 12.h),
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: auctionProducts.length,
            itemBuilder: (context, index) {
              final product = auctionProducts[index];
              return Container(
                margin: EdgeInsets.only(bottom: 16.h),
                child: AuctionCard(
                  product: product,
                  onTap: () {
                    Navigator.pushNamed(
                      context,
                      '/product-detail',
                      arguments: product,
                    );
                  },
                  onFavorite: () {
                    setState(() {
                      auctionProducts[index]['isFavorite'] =
                          !(product['isFavorite'] ?? false);
                    });
                  },
                ),
              );
            },
          ),
          SizedBox(height: 80.h), // 底部导航栏高度
        ],
      ),
    );
  }

  Widget _buildFilterTag(String text, bool isSelected) {
    return Container(
      margin: EdgeInsets.only(right: 8.w),
      padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h),
      decoration: BoxDecoration(
        color: isSelected ? AppColors.primary : Colors.white,
        borderRadius: BorderRadius.circular(16.r),
        border: Border.all(
          color: isSelected ? AppColors.primary : AppColors.border,
        ),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 12.sp,
          color: isSelected ? Colors.white : AppColors.textSecondary,
          fontWeight: isSelected ? FontWeight.w500 : FontWeight.normal,
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
    return Container(
      height: 120.h,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12.r),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            accentColor.withOpacity(0.8),
            accentColor,
          ],
        ),
      ),
      child: Stack(
        children: [
          // 背景图片
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
                width: 80.w,
                height: double.infinity,
                fit: BoxFit.cover,
                placeholder: (context, url) => Container(
                  color: Colors.white.withOpacity(0.3),
                ),
              ),
            ),
          ),

          // 文字内容
          Padding(
            padding: EdgeInsets.all(12.w),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.9),
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                  child: Text(
                    tag,
                    style: TextStyle(
                      fontSize: 10.sp,
                      color: accentColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                SizedBox(height: 4.h),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const Spacer(),
                Row(
                  children: [
                    Icon(
                      Icons.access_time,
                      size: 12.w,
                      color: Colors.white,
                    ),
                    SizedBox(width: 2.w),
                    Text(
                      endTime,
                      style: TextStyle(
                        fontSize: 10.sp,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 2.h),
                Text(
                  count,
                  style: TextStyle(
                    fontSize: 12.sp,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 构建标签页内容
  Widget _buildTabContent(int tabIndex) {
    return SingleChildScrollView(
      child: Column(
        children: [
          // 首页内容 (index 0)
          if (tabIndex == 0) ...[
            _buildBannerSection(),
            _buildFunctionGrid(),
            _buildProductList(),
          ]
          // 宠物内容 (index 1)
          else if (tabIndex == 1) ...[
            _buildCategoryContent('宠物', [
              {
                'name': '英短蓝猫',
                'price': 1200,
                'image': 'https://picsum.photos/200/200?random=30'
              },
              {
                'name': '金毛犬',
                'price': 2500,
                'image': 'https://picsum.photos/200/200?random=31'
              },
              {
                'name': '布偶猫',
                'price': 3800,
                'image': 'https://picsum.photos/200/200?random=32'
              },
            ]),
          ]
          // 水族内容 (index 2)
          else if (tabIndex == 2) ...[
            _buildCategoryContent('水族', [
              {
                'name': '红绿灯鱼',
                'price': 25,
                'image': 'https://picsum.photos/200/200?random=33'
              },
              {
                'name': '龙鱼',
                'price': 1500,
                'image': 'https://picsum.photos/200/200?random=34'
              },
              {
                'name': '锦鲤',
                'price': 800,
                'image': 'https://picsum.photos/200/200?random=35'
              },
            ]),
          ]
          // 一口价内容 (index 3)
          else if (tabIndex == 3) ...[
            _buildCategoryContent('一口价专区', [
              {
                'name': '萨摩耶',
                'price': 1800,
                'image': 'https://picsum.photos/200/200?random=36'
              },
              {
                'name': '柯基',
                'price': 1500,
                'image': 'https://picsum.photos/200/200?random=37'
              },
              {
                'name': '比熊',
                'price': 1200,
                'image': 'https://picsum.photos/200/200?random=38'
              },
            ]),
          ]
          // 同城内容 (index 4)
          else if (tabIndex == 4) ...[
            _buildCategoryContent('同城服务', [
              {
                'name': '宠物美容',
                'price': 100,
                'image': 'https://picsum.photos/200/200?random=39'
              },
              {
                'name': '宠物医疗',
                'price': 200,
                'image': 'https://picsum.photos/200/200?random=40'
              },
              {
                'name': '宠物寄养',
                'price': 50,
                'image': 'https://picsum.photos/200/200?random=41'
              },
            ]),
          ]
          // 限时拍卖内容 (index 5)
          else if (tabIndex == 5) ...[
            _buildSpecialAuctionContent(),
          ]
          // 今日专场内容 (index 6)
          else if (tabIndex == 6) ...[
            _buildTodaySpecialContent(),
          ]
          // 山东鱼宠专场内容 (index 7)
          else if (tabIndex == 7) ...[
            _buildShandongFishContent(),
          ]
          // 苏州宠物专场内容 (index 8)
          else if (tabIndex == 8) ...[
            _buildSuzhouPetContent(),
          ]
          // 默认内容
          else ...[
            _buildDefaultContent(tabs[tabIndex]),
          ],
        ],
      ),
    );
  }

  // 构建分类内容
  Widget _buildCategoryContent(String title, List<Map<String, dynamic>> items) {
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
          SizedBox(height: 80.h),
        ],
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
          ...auctionProducts
              .map((product) => Container(
                    margin: EdgeInsets.only(bottom: 16.h),
                    child: AuctionCard(
                      product: product,
                      onTap: () {
                        Navigator.pushNamed(context, '/product-detail',
                            arguments: product);
                      },
                      onFavorite: () {},
                    ),
                  ))
              .toList(),
          SizedBox(height: 80.h),
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
                        Navigator.pushNamed(context, '/product-detail',
                            arguments: product);
                      },
                      onFavorite: () {},
                    ),
                  ))
              .toList(),
          SizedBox(height: 80.h),
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
                        Navigator.pushNamed(context, '/product-detail',
                            arguments: product);
                      },
                      onFavorite: () {},
                    ),
                  ))
              .toList(),
          SizedBox(height: 80.h),
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
}
