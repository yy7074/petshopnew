import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';
import '../../services/store_service.dart';
import 'local_pet_store_detail_page.dart';

class LocalPetStoresPage extends StatefulWidget {
  const LocalPetStoresPage({super.key});

  @override
  State<LocalPetStoresPage> createState() => _LocalPetStoresPageState();
}

class _LocalPetStoresPageState extends State<LocalPetStoresPage> {
  final ScrollController _scrollController = ScrollController();
  final StoreService _storeService = StoreService();

  List<Map<String, dynamic>> _stores = [];
  bool _isLoading = false;
  bool _hasMore = true;
  int _currentPage = 1;
  final int _pageSize = 20;

  @override
  void initState() {
    super.initState();
    _loadStores();
    _scrollController.addListener(_onScroll);
  }

  // 加载店铺列表
  Future<void> _loadStores({bool refresh = false}) async {
    if (_isLoading) return;
    if (!refresh && !_hasMore) return;

    setState(() {
      _isLoading = true;
      if (refresh) {
        _currentPage = 1;
        _stores = [];
        _hasMore = true;
      }
    });

    try {
      final result = await _storeService.getLocalPetStores(
        page: _currentPage,
        pageSize: _pageSize,
      );

      if (result.success && result.data != null) {
        final items = (result.data!['items'] as List?)
                ?.map((e) => e as Map<String, dynamic>)
                .toList() ??
            [];

        setState(() {
          if (refresh) {
            _stores = items;
          } else {
            _stores.addAll(items);
          }

          _hasMore = items.length >= _pageSize;
          _currentPage++;
          _isLoading = false;
        });
      } else {
        setState(() {
          _isLoading = false;
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(result.message ?? '加载失败')),
          );
        }
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载失败: $e')),
        );
      }
    }
  }

  // 滚动监听
  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      _loadStores();
    }
  }

  // 备用的模拟数据（保留用于参考）
  final List<Map<String, dynamic>> _mockStores = [
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
  void dispose() {
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
          '本地宠店',
          style: TextStyle(
            color: Colors.black87,
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: _stores.isEmpty && _isLoading
          ? _buildLoadingView()
          : _stores.isEmpty
              ? _buildEmptyView()
              : RefreshIndicator(
                  onRefresh: () => _loadStores(refresh: true),
                  child: ListView.builder(
                    controller: _scrollController,
                    padding: EdgeInsets.all(16.w),
                    itemCount: _stores.length + (_hasMore ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == _stores.length) {
                        return _buildLoadingMore();
                      }
                      final store = _stores[index];
                      return _buildStoreCard(store);
                    },
                  ),
                ),
    );
  }

  // 加载中视图
  Widget _buildLoadingView() {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }

  // 空数据视图
  Widget _buildEmptyView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.store_outlined,
            size: 64.sp,
            color: Colors.grey[400],
          ),
          SizedBox(height: 16.h),
          Text(
            '暂无店铺数据',
            style: TextStyle(
              fontSize: 16.sp,
              color: Colors.grey[600],
            ),
          ),
          SizedBox(height: 24.h),
          ElevatedButton(
            onPressed: () => _loadStores(refresh: true),
            child: const Text('重新加载'),
          ),
        ],
      ),
    );
  }

  // 加载更多指示器
  Widget _buildLoadingMore() {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 16.h),
      child: const Center(
        child: CircularProgressIndicator(),
      ),
    );
  }

  Widget _buildStoreCard(Map<String, dynamic> store) {
    // 兼容API返回的数据格式
    final storeName = store['name'] ?? store['shop_name'] ?? '未知店铺';
    final storeAvatar = store['avatar'] ??
        store['logo'] ??
        'https://picsum.photos/60/60?random=${store['id']}';
    final rating =
        (store['rating'] ?? store['average_rating'] ?? 4.0).toDouble();
    final followers = store['followers'] ?? store['followers_count'] ?? 0;
    final products =
        (store['products'] as List?)?.cast<Map<String, dynamic>>() ?? [];

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
                    backgroundImage: NetworkImage(storeAvatar),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          storeName,
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
                                index < rating.floor()
                                    ? Icons.star
                                    : Icons.star_border,
                                color: const Color(0xFFFFB74D),
                                size: 14.sp,
                              );
                            }),
                            SizedBox(width: 8.w),
                            Text(
                              followers is int
                                  ? '$followers粉丝'
                                  : followers.toString(),
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

              if (products.isNotEmpty) ...[
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
                  itemCount: products.length > 4 ? 4 : products.length,
                  itemBuilder: (context, index) {
                    final product = products[index];
                    return _buildProductItem(product);
                  },
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProductItem(Map<String, dynamic> product) {
    // 兼容API返回的数据格式
    final imageUrl = product['image'] ??
        (product['images'] is List && (product['images'] as List).isNotEmpty
            ? product['images'][0]
            : 'https://picsum.photos/200/200?random=${product['id']}');
    final price = product['price'] ??
        product['current_price'] ??
        product['starting_price'] ??
        0;

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8.r),
        image: DecorationImage(
          image: NetworkImage(imageUrl.toString()),
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
                '¥$price',
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
