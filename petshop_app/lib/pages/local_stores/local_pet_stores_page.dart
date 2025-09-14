import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:pull_to_refresh/pull_to_refresh.dart';
import '../../constants/app_colors.dart';
import '../../services/local_service_service.dart';
import 'local_pet_store_detail_page.dart';

class LocalPetStoresPage extends StatefulWidget {
  const LocalPetStoresPage({super.key});

  @override
  State<LocalPetStoresPage> createState() => _LocalPetStoresPageState();
}

class _LocalPetStoresPageState extends State<LocalPetStoresPage> {
  final ScrollController _scrollController = ScrollController();
  final RefreshController _refreshController =
      RefreshController(initialRefresh: false);

  // 真实宠店数据
  List<Map<String, dynamic>> _stores = [];
  bool _isLoading = false;
  bool _hasMore = true;
  int _currentPage = 1;
  String? _errorMessage;

  // 默认宠店数据（API失败时使用）
  final List<Map<String, dynamic>> _defaultStores = [
    {
      'id': '1',
      'name': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=201',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'products': [
        {
          'image': 'https://picsum.photos/200/200?random=301',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=302',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=303',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=304',
          'price': 432,
        },
      ],
    },
    {
      'id': '2',
      'name': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=202',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'products': [
        {
          'image': 'https://picsum.photos/200/200?random=311',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=312',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=313',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=314',
          'price': 432,
        },
      ],
    },
    {
      'id': '3',
      'name': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=203',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'products': [
        {
          'image': 'https://picsum.photos/200/200?random=321',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=322',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=323',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=324',
          'price': 432,
        },
      ],
    },
    {
      'id': '4',
      'name': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=204',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'products': [
        {
          'image': 'https://picsum.photos/200/200?random=331',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=332',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=333',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=334',
          'price': 432,
        },
      ],
    },
  ];

  @override
  void initState() {
    super.initState();
    _loadStores();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _refreshController.dispose();
    super.dispose();
  }

  // 加载宠店数据
  Future<void> _loadStores({bool isRefresh = false}) async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      if (isRefresh) {
        _currentPage = 1;
        _hasMore = true;
      }

      final result = await LocalServiceService.getServicesByType(
        'local_store',
        page: _currentPage,
        pageSize: 20,
      );

      final List<Map<String, dynamic>> newStores = (result['items'] as List)
          .map((item) => LocalServiceService.formatServiceForUI(item))
          .toList();

      setState(() {
        if (isRefresh) {
          _stores = newStores;
        } else {
          _stores.addAll(newStores);
        }

        _currentPage++;
        _hasMore = newStores.length >= 20;
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
        _errorMessage = e.toString();
        // 如果是第一次加载失败，使用默认数据
        if (_stores.isEmpty) {
          _stores = _defaultStores;
        }
      });

      if (isRefresh) {
        _refreshController.refreshFailed();
      } else {
        _refreshController.loadFailed();
      }

      print('加载宠店失败: $e');
    }
  }

  // 刷新数据
  void _onRefresh() async {
    await _loadStores(isRefresh: true);
  }

  // 加载更多
  void _onLoading() async {
    if (!_hasMore) {
      _refreshController.loadNoData();
      return;
    }
    await _loadStores();
  }

  // 构建空状态
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.store_outlined,
            size: 80.w,
            color: Colors.grey[400],
          ),
          SizedBox(height: 16.h),
          Text(
            '还没有找到宠物店',
            style: TextStyle(
              fontSize: 16.sp,
              color: Colors.grey[500],
              fontWeight: FontWeight.w500,
            ),
          ),
          SizedBox(height: 8.h),
          Text(
            '快来发现附近的好店吧！',
            style: TextStyle(
              fontSize: 14.sp,
              color: Colors.grey[400],
            ),
          ),
        ],
      ),
    );
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
          '本地宠店',
          style: TextStyle(
            color: Colors.black87,
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: SmartRefresher(
        controller: _refreshController,
        onRefresh: _onRefresh,
        onLoading: _onLoading,
        enablePullDown: true,
        enablePullUp: true,
        child: _isLoading && _stores.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : _stores.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    padding: EdgeInsets.all(16.w),
                    itemCount: _stores.length,
                    itemBuilder: (context, index) {
                      final store = _stores[index];
                      return _buildStoreCard(store);
                    },
                  ),
      ),
    );
  }

  Widget _buildStoreCard(Map<String, dynamic> store) {
    final products = store['products'] as List<Map<String, dynamic>>;

    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => LocalPetStoreDetailPage(store: store),
          ),
        );
      },
      child: Container(
        margin: EdgeInsets.only(bottom: 16.h),
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
        child: Padding(
          padding: EdgeInsets.all(16.w),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 店铺头部信息
              Row(
                children: [
                  CircleAvatar(
                    radius: 24.r,
                    backgroundImage: NetworkImage(store['avatar']),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          store['name'],
                          style: TextStyle(
                            fontSize: 16.sp,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                          ),
                        ),
                        SizedBox(height: 4.h),
                        Row(
                          children: [
                            // 星级评分
                            ...List.generate(5, (index) {
                              return Icon(
                                index < store['rating'].floor()
                                    ? Icons.star
                                    : Icons.star_border,
                                color: const Color(0xFFFFB74D),
                                size: 14.sp,
                              );
                            }),
                            SizedBox(width: 8.w),
                            Text(
                              store['followers'],
                              style: TextStyle(
                                fontSize: 12.sp,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding:
                        EdgeInsets.symmetric(horizontal: 16.w, vertical: 6.h),
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(15.r),
                    ),
                    child: Text(
                      '进店',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12.sp,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),

              SizedBox(height: 16.h),

              // 商品网格
              GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 4,
                  crossAxisSpacing: 8.w,
                  mainAxisSpacing: 8.h,
                  childAspectRatio: 0.85,
                ),
                itemCount: products.length,
                itemBuilder: (context, index) {
                  final product = products[index];
                  return _buildProductItem(product);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProductItem(Map<String, dynamic> product) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8.r),
        image: DecorationImage(
          image: NetworkImage(product['image']),
          fit: BoxFit.cover,
        ),
      ),
      child: Stack(
        children: [
          // 价格标签
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 4.w, vertical: 2.h),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.black.withValues(alpha: 0.7),
                  ],
                ),
                borderRadius:
                    BorderRadius.vertical(bottom: Radius.circular(8.r)),
              ),
              child: Text(
                '¥${product['price']}',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 10.sp,
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
