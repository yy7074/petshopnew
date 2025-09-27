import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';
import '../../services/local_service_service.dart';
import 'aquarium_design_detail_page.dart';

class AquariumDesignPage extends StatefulWidget {
  const AquariumDesignPage({super.key});

  @override
  State<AquariumDesignPage> createState() => _AquariumDesignPageState();
}

class _AquariumDesignPageState extends State<AquariumDesignPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ScrollController _scrollController = ScrollController();

  // 数据状态
  List<Map<String, dynamic>> _designServices = [];
  bool _isLoading = true;
  String? _errorMessage;
  int _currentPage = 1;
  bool _hasMore = true;
  bool _isLoadingMore = false;

  // 筛选条件
  String? _selectedLocation;
  String? _selectedStyle;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadDesignServices();
    _scrollController.addListener(_onScroll);
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      _loadMoreServices();
    }
  }

  Future<void> _loadDesignServices({bool refresh = false}) async {
    setState(() {
      if (refresh) {
        _isLoading = true;
        _currentPage = 1;
        _hasMore = true;
        _designServices.clear();
      } else {
        _isLoading = true;
      }
      _errorMessage = null;
    });

    try {
      final result = await LocalServiceService.getAquariumDesignServices(
        page: _currentPage,
        pageSize: 20,
        location: _selectedLocation,
        style: _selectedStyle,
      );

      final List<Map<String, dynamic>> newServices =
          List<Map<String, dynamic>>.from(result['items'] ?? []);

      setState(() {
        if (refresh || _currentPage == 1) {
          _designServices = newServices;
        } else {
          _designServices.addAll(newServices);
        }
        _hasMore = newServices.length >= 20;
        _isLoading = false;
        _isLoadingMore = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '加载失败: $e';
        _isLoading = false;
        _isLoadingMore = false;
      });
    }
  }

  Future<void> _loadMoreServices() async {
    if (_isLoadingMore || !_hasMore) return;

    setState(() {
      _isLoadingMore = true;
      _currentPage++;
    });

    await _loadDesignServices();
  }

  List<Map<String, dynamic>> get _displayRewardItems =>
      _designServices.isNotEmpty ? _designServices : _mockRewardItems;

  String? _resolveImage(Map<String, dynamic> item) {
    final dynamic directImage = item['image'] ?? item['coverImage'] ?? item['cover_image'];
    if (directImage is String && directImage.isNotEmpty) return directImage;

    final dynamic images = item['images'] ?? item['portfolio_images'];
    if (images is List && images.isNotEmpty) {
      final first = images.first;
      if (first is String && first.isNotEmpty) return first;
      if (first is Map) {
        final dynamic url = first['url'] ?? first['image_url'];
        if (url is String && url.isNotEmpty) return url;
      }
    }

    return null;
  }

  String _resolveTitle(Map<String, dynamic> item) {
    final dynamic title =
        item['title'] ?? item['name'] ?? item['serviceTitle'] ?? item['service_title'];
    return title?.toString() ?? '鱼缸造景服务';
  }

  String _resolveShopName(Map<String, dynamic> item) {
    final dynamic shop =
        item['shopName'] ?? item['provider_name'] ?? item['designer_name'];
    return shop?.toString() ?? '优质服务商';
  }

  String? _resolveShopAvatar(Map<String, dynamic> item) {
    final dynamic avatar =
        item['shopAvatar'] ?? item['provider_avatar'] ?? item['designer_avatar'];
    if (avatar is String && avatar.isNotEmpty) return avatar;
    return null;
  }

  num? _parseNum(dynamic value) {
    if (value == null) return null;
    if (value is num) return value;
    if (value is String && value.isNotEmpty) {
      return num.tryParse(value.replaceAll(RegExp(r'[^0-9\.-]'), ''));
    }
    return null;
  }

  String _formatPrice(Map<String, dynamic> item) {
    final num? price = _parseNum(
      item['currentPrice'] ??
          item['current_price'] ??
          item['price'] ??
          item['reward_amount'] ??
          item['budget_min'],
    );

    if (price != null) {
      return '¥${price.toStringAsFixed(0)}';
    }

    final dynamic priceRange = item['price_range'] ?? item['budget_range'];
    if (priceRange is String && priceRange.isNotEmpty) {
      return priceRange;
    }

    return '价格面议';
  }

  // 原来的模拟数据（作为备用）
  final List<Map<String, dynamic>> _mockRewardItems = [
    {
      'id': '1',
      'image': 'https://picsum.photos/400/300?random=701',
      'title': '产品标题产品标题产品',
      'currentPrice': 924.9,
      'originalPrice': 1200.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=801',
    },
    {
      'id': '2',
      'image': 'https://picsum.photos/400/300?random=702',
      'title': '产品标题产品标题产品',
      'currentPrice': 924.9,
      'originalPrice': 1200.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=802',
    },
    {
      'id': '3',
      'image': 'https://picsum.photos/400/300?random=703',
      'title': '产品标题产品标题产品',
      'currentPrice': 924.9,
      'originalPrice': 1200.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=803',
    },
    {
      'id': '4',
      'image': 'https://picsum.photos/400/300?random=704',
      'title': '产品标题产品标题产品',
      'currentPrice': 924.9,
      'originalPrice': 1200.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=804',
    },
    {
      'id': '5',
      'image': 'https://picsum.photos/400/300?random=705',
      'title': '产品标题产品标题产品',
      'currentPrice': 924.9,
      'originalPrice': 1200.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=805',
    },
    {
      'id': '6',
      'image': 'https://picsum.photos/400/300?random=706',
      'title': '产品标题产品标题产品',
      'currentPrice': 924.9,
      'originalPrice': 1200.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=806',
    },
  ];

  // 购买数据
  final List<Map<String, dynamic>> _buyItems = [
    {
      'id': '1',
      'image': 'https://picsum.photos/400/300?random=711',
      'title': '产品标题产品标题产品',
      'currentPrice': 924.9,
      'originalPrice': 1200.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=811',
    },
    {
      'id': '2',
      'image': 'https://picsum.photos/400/300?random=712',
      'title': '产品标题产品标题产品',
      'currentPrice': 980.9,
      'originalPrice': 1300.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=812',
    },
    {
      'id': '3',
      'image': 'https://picsum.photos/400/300?random=713',
      'title': '产品标题产品标题产品',
      'currentPrice': 980.9,
      'originalPrice': 1300.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=813',
    },
    {
      'id': '4',
      'image': 'https://picsum.photos/400/300?random=714',
      'title': '产品标题产品标题产品',
      'currentPrice': 980.9,
      'originalPrice': 1300.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=814',
    },
    {
      'id': '5',
      'image': 'https://picsum.photos/400/300?random=715',
      'title': '产品标题产品标题产品',
      'currentPrice': 980.9,
      'originalPrice': 1300.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=815',
    },
    {
      'id': '6',
      'image': 'https://picsum.photos/400/300?random=716',
      'title': '产品标题产品标题产品',
      'currentPrice': 980.9,
      'originalPrice': 1300.0,
      'shopName': '水族馆',
      'shopAvatar': 'https://picsum.photos/40/40?random=816',
    },
  ];
  @override
  void dispose() {
    _tabController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.black87),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          '鱼缸造景',
          style: TextStyle(
            color: Colors.black87,
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
          ),
        ),
        bottom: PreferredSize(
          preferredSize: Size.fromHeight(50.h),
          child: Container(
            color: Colors.white,
            child: TabBar(
              controller: _tabController,
              indicatorColor: AppColors.primary,
              indicatorWeight: 2.0,
              indicatorSize: TabBarIndicatorSize.label,
              labelColor: AppColors.primary,
              unselectedLabelColor: Colors.grey[600],
              labelStyle: TextStyle(
                fontSize: 16.sp,
                fontWeight: FontWeight.w600,
              ),
              unselectedLabelStyle: TextStyle(
                fontSize: 16.sp,
                fontWeight: FontWeight.normal,
              ),
              tabs: const [
                Tab(text: '悬赏'),
                Tab(text: '购买'),
              ],
            ),
          ),
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildRewardTab(),
          _buildBuyTab(),
        ],
      ),
    );
  }

  Widget _buildRewardTab() {
    if (_isLoading && _designServices.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_errorMessage != null && _designServices.isEmpty) {
      return Center(
        child: Padding(
          padding: EdgeInsets.all(24.w),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, color: Colors.redAccent, size: 48),
              SizedBox(height: 12.h),
              Text(
                _errorMessage!,
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 14.sp, color: Colors.redAccent),
              ),
              SizedBox(height: 12.h),
              ElevatedButton(
                onPressed: () => _loadDesignServices(refresh: true),
                child: const Text('重新加载'),
              ),
            ],
          ),
        ),
      );
    }

    final items = _displayRewardItems;

    if (items.isEmpty) {
      return Center(
        child: Text(
          '暂无造景悬赏，稍后再来看看吧～',
          style: TextStyle(fontSize: 14.sp, color: Colors.grey[600]),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => _loadDesignServices(refresh: true),
      child: GridView.builder(
        controller: _scrollController,
        padding: EdgeInsets.all(12.w),
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 12.w,
          mainAxisSpacing: 12.h,
          childAspectRatio: 0.75,
        ),
        itemCount: items.length,
        itemBuilder: (context, index) {
          final item = items[index];
          return _buildAquariumItem(item, true);
        },
      ),
    );
  }

  Widget _buildBuyTab() {
    return GridView.builder(
      controller: _scrollController,
      padding: EdgeInsets.all(12.w),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12.w,
        mainAxisSpacing: 12.h,
        childAspectRatio: 0.75,
      ),
      itemCount: _buyItems.length,
      itemBuilder: (context, index) {
        final item = _buyItems[index];
        return _buildAquariumItem(item, false);
      },
    );
  }

  Widget _buildAquariumItem(Map<String, dynamic> item, bool isReward) {
    final imageUrl = _resolveImage(item);
    final title = _resolveTitle(item);
    final shopName = _resolveShopName(item);
    final shopAvatar = _resolveShopAvatar(item);
    final priceText = _formatPrice(item);

    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => AquariumDesignDetailPage(
              item: item,
              isReward: isReward,
            ),
          ),
        );
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.08),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 产品图片
            Expanded(
              flex: 3,
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  borderRadius:
                      BorderRadius.vertical(top: Radius.circular(12.r)),
                  image: imageUrl != null
                      ? DecorationImage(
                          image: NetworkImage(imageUrl),
                          fit: BoxFit.cover,
                        )
                      : null,
                  color: Colors.grey[200],
                ),
                child: imageUrl == null
                    ? Icon(
                        Icons.image_outlined,
                        color: Colors.grey[400],
                        size: 36.w,
                      )
                    : null,
              ),
            ),

            // 产品信息
            Expanded(
              flex: 2,
              child: Padding(
                padding: EdgeInsets.all(12.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 产品标题
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: Colors.black87,
                        height: 1.3,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),

                    SizedBox(height: 8.h),

                    // 价格行
                    Row(
                      children: [
                        Text(
                          isReward ? '当前悬赏' : '服务价格',
                          style: TextStyle(
                            fontSize: 10.sp,
                            color: Colors.grey[500],
                          ),
                        ),
                        SizedBox(width: 4.w),
                        Text(
                          priceText,
                          style: TextStyle(
                            fontSize: 14.sp,
                            fontWeight: FontWeight.w600,
                            color: AppColors.primary,
                          ),
                        ),
                      ],
                    ),

                    SizedBox(height: 8.h),

                    // 店铺信息
                    Row(
                      children: [
                        CircleAvatar(
                          radius: 10.r,
                          backgroundColor: Colors.grey[300],
                          backgroundImage: shopAvatar != null
                              ? NetworkImage(shopAvatar)
                              : null,
                          child: shopAvatar == null
                              ? Icon(
                                  Icons.storefront,
                                  size: 12.sp,
                                  color: Colors.white,
                                )
                              : null,
                        ),
                        SizedBox(width: 6.w),
                        Expanded(
                          child: Text(
                            shopName,
                            style: TextStyle(
                              fontSize: 12.sp,
                              color: Colors.grey[600],
                            ),
                          ),
                        ),
                        Container(
                          width: 16.w,
                          height: 16.w,
                          decoration: BoxDecoration(
                            color: Colors.grey[300],
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.favorite_border,
                            size: 10.sp,
                            color: Colors.grey[600],
                          ),
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
}
