import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';
import '../../services/local_service_service.dart';

class DoorServicePage extends StatefulWidget {
  const DoorServicePage({super.key});

  @override
  State<DoorServicePage> createState() => _DoorServicePageState();
}

class _DoorServicePageState extends State<DoorServicePage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ScrollController _scrollController = ScrollController();

  // 当前选中的服务类型
  String _currentServiceType = 'pet_grooming';
  List<Map<String, dynamic>> _services = [];
  bool _isLoading = false;
  bool _hasMore = true;
  int _currentPage = 1;
  final int _pageSize = 20;

  // 服务类型映射
  final Map<int, Map<String, String>> _serviceTypes = {
    0: {'type': 'pet_grooming', 'name': '宠物洗澡'},
    1: {'type': 'aquarium_design', 'name': '鱼缸造景'},
    2: {'type': 'aquarium_repair', 'name': '鱼缸维修'},
  };

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(_onTabChanged);
    _loadServices();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // Tab切换监听
  void _onTabChanged() {
    if (_tabController.indexIsChanging) {
      final newType = _serviceTypes[_tabController.index]!['type']!;
      if (newType != _currentServiceType) {
        setState(() {
          _currentServiceType = newType;
          _currentPage = 1;
          _services = [];
          _hasMore = true;
        });
        _loadServices(refresh: true);
      }
    }
  }

  // 加载服务列表
  Future<void> _loadServices({bool refresh = false}) async {
    if (_isLoading) return;
    if (!refresh && !_hasMore) return;

    setState(() {
      _isLoading = true;
      if (refresh) {
        _currentPage = 1;
        _services = [];
        _hasMore = true;
      }
    });

    try {
      final result = await LocalServiceService.getDoorServices(
        page: _currentPage,
        pageSize: _pageSize,
        serviceType: _currentServiceType,
      );

      if (result['success'] == true || result['items'] != null) {
        final items = (result['items'] as List?)
                ?.map((e) => e as Map<String, dynamic>)
                .toList() ??
            [];

        setState(() {
          if (refresh) {
            _services = items;
          } else {
            _services.addAll(items);
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
            SnackBar(content: Text(result['message'] ?? '加载失败')),
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
      _loadServices();
    }
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
          '上门服务',
          style: TextStyle(
            color: Colors.black87,
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
          ),
        ),
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppColors.primary,
          unselectedLabelColor: Colors.grey[600],
          indicatorColor: AppColors.primary,
          indicatorWeight: 3,
          labelStyle: TextStyle(
            fontSize: 15.sp,
            fontWeight: FontWeight.w600,
          ),
          tabs: const [
            Tab(text: '宠物洗澡'),
            Tab(text: '鱼缸造景'),
            Tab(text: '鱼缸维修'),
          ],
        ),
      ),
      body: _services.isEmpty && _isLoading
          ? _buildLoadingView()
          : _services.isEmpty
              ? _buildEmptyView()
              : RefreshIndicator(
                  onRefresh: () => _loadServices(refresh: true),
                  child: ListView.builder(
                    controller: _scrollController,
                    padding: EdgeInsets.all(16.w),
                    itemCount: _services.length + (_hasMore ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == _services.length) {
                        return _buildLoadingMore();
                      }
                      final service = _services[index];
                      return _buildServiceCard(service);
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
            Icons.room_service_outlined,
            size: 64.sp,
            color: Colors.grey[400],
          ),
          SizedBox(height: 16.h),
          Text(
            '暂无服务数据',
            style: TextStyle(
              fontSize: 16.sp,
              color: Colors.grey[600],
            ),
          ),
          SizedBox(height: 24.h),
          ElevatedButton(
            onPressed: () => _loadServices(refresh: true),
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

  Widget _buildServiceCard(Map<String, dynamic> service) {
    // 兼容API返回的数据格式
    final shopName = service['shop_name'] ?? service['title'] ?? '服务商家';
    final avatar = service['avatar'] ??
        service['logo'] ??
        'https://picsum.photos/60/60?random=${service['id']}';
    final rating =
        (service['rating'] ?? service['average_rating'] ?? 4.0).toDouble();
    final followers =
        service['followers'] ?? service['followers_count'] ?? '0粉丝';
    final address = service['address'] ?? service['location'] ?? '地址待完善';
    final distance = service['distance'] ?? '';
    final servicesList =
        (service['services'] as List?)?.cast<Map<String, dynamic>>() ?? [];

    return Container(
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
            // 商家信息
            Row(
              children: [
                CircleAvatar(
                  radius: 24.r,
                  backgroundImage: NetworkImage(avatar.toString()),
                ),
                SizedBox(width: 12.w),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        shopName,
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
              ],
            ),

            SizedBox(height: 12.h),

            // 地址信息
            Row(
              children: [
                Icon(Icons.location_on, size: 16.sp, color: Colors.grey[600]),
                SizedBox(width: 4.w),
                Expanded(
                  child: Text(
                    address,
                    style: TextStyle(
                      fontSize: 13.sp,
                      color: Colors.grey[700],
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (distance.isNotEmpty) ...[
                  SizedBox(width: 8.w),
                  Text(
                    distance.toString(),
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: AppColors.primary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ],
            ),

            if (servicesList.isNotEmpty) ...[
              SizedBox(height: 12.h),
              const Divider(height: 1),
              SizedBox(height: 12.h),

              // 服务列表
              ...servicesList.map((srv) => _buildServiceItem(srv)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildServiceItem(Map<String, dynamic> service) {
    final name = service['name'] ?? service['title'] ?? '服务项目';
    final price = service['price'] ?? 0;

    return Padding(
      padding: EdgeInsets.only(bottom: 8.h),
      child: Row(
        children: [
          Expanded(
            child: Text(
              name,
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.black87,
              ),
            ),
          ),
          Text(
            '¥$price',
            style: TextStyle(
              fontSize: 15.sp,
              color: AppColors.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
