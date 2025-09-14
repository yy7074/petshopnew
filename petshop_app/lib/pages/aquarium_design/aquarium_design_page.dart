import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:pull_to_refresh/pull_to_refresh.dart';
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
  final RefreshController _refreshController =
      RefreshController(initialRefresh: false);

  // 真实数据
  List<Map<String, dynamic>> _services = [];
  List<Map<String, dynamic>> _rewardItems = [];
  bool _isLoading = false;
  bool _hasMore = true;
  int _currentPage = 1;

  // 悬赏数据（默认数据）
  final List<Map<String, dynamic>> _defaultRewardItems = [
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
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _rewardItems = List.from(_defaultRewardItems);
    _loadServices();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _scrollController.dispose();
    _refreshController.dispose();
    super.dispose();
  }

  // 加载造景服务数据
  Future<void> _loadServices({bool isRefresh = false}) async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
    });

    try {
      if (isRefresh) {
        _currentPage = 1;
        _hasMore = true;
      }

      final result = await LocalServiceService.getServicesByType(
        'aquarium_design',
        page: _currentPage,
        pageSize: 20,
      );

      final List<Map<String, dynamic>> newServices = (result['items'] as List)
          .map((item) => LocalServiceService.formatServiceForUI(item))
          .toList();

      setState(() {
        if (isRefresh) {
          _services = newServices;
        } else {
          _services.addAll(newServices);
        }

        _currentPage++;
        _hasMore = newServices.length >= 20;
        _isLoading = false;
      });

      if (isRefresh) {
        _refreshController.refreshCompleted();
      } else {
        _refreshController.loadComplete();
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        // 如果是第一次加载失败，使用默认数据
        if (_services.isEmpty) {
          _services = _defaultRewardItems;
        }
      });

      if (isRefresh) {
        _refreshController.refreshFailed();
      } else {
        _refreshController.loadFailed();
      }

      print('加载造景服务失败: $e');
    }
  }

  // 刷新数据
  void _onRefresh() async {
    await _loadServices(isRefresh: true);
  }

  // 加载更多
  void _onLoading() async {
    if (!_hasMore) {
      _refreshController.loadNoData();
      return;
    }
    await _loadServices();
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
    return GridView.builder(
      controller: _scrollController,
      padding: EdgeInsets.all(12.w),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12.w,
        mainAxisSpacing: 12.h,
        childAspectRatio: 0.75,
      ),
      itemCount: _rewardItems.length,
      itemBuilder: (context, index) {
        final item = _rewardItems[index];
        return _buildAquariumItem(item, true);
      },
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
                  image: DecorationImage(
                    image: NetworkImage(item['image']),
                    fit: BoxFit.cover,
                  ),
                ),
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
                      item['title'],
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
                          isReward ? '当前悬赏' : '',
                          style: TextStyle(
                            fontSize: 10.sp,
                            color: Colors.grey[500],
                          ),
                        ),
                        if (isReward) SizedBox(width: 4.w),
                        Text(
                          '¥${item['currentPrice']}',
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
                          backgroundImage: NetworkImage(item['shopAvatar']),
                        ),
                        SizedBox(width: 6.w),
                        Expanded(
                          child: Text(
                            item['shopName'],
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
