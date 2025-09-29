import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';
import '../../services/local_service_service.dart';
import 'pet_social_detail_page.dart';
import 'pet_social_publish_page.dart';

class PetSocialPage extends StatefulWidget {
  const PetSocialPage({super.key});

  @override
  State<PetSocialPage> createState() => _PetSocialPageState();
}

class _PetSocialPageState extends State<PetSocialPage> {
  final ScrollController _scrollController = ScrollController();

  // 数据状态
  List<Map<String, dynamic>> _posts = [];
  bool _isLoading = true;
  bool _isLoadingMore = false;
  String? _errorMessage;
  int _currentPage = 1;
  bool _hasMore = true;

  // 筛选条件
  String? _selectedPetType;
  String? _selectedLocation;
  String _currentSearchQuery = '';

  // 宠物类型选项
  final List<String> _petTypes = ['全部', '狗狗', '猫咪', '鸟类', '鱼类', '爬虫', '小宠'];

  @override
  void initState() {
    super.initState();
    _loadPosts();
    _scrollController.addListener(_onScroll);
  }

  // 滚动监听
  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      _loadMorePosts();
    }
  }

  // 加载帖子
  Future<void> _loadPosts({bool refresh = false}) async {
    if (!refresh && _isLoading) return;

    setState(() {
      if (refresh) {
        _isLoading = true;
        _currentPage = 1;
        _hasMore = true;
        _posts.clear();
      } else {
        _isLoading = true;
      }
      _errorMessage = null;
    });

    try {
      final result = _currentSearchQuery.isNotEmpty
          ? await LocalServiceService.searchSocialPosts(
              query: _currentSearchQuery,
              page: _currentPage,
              pageSize: 20,
              petType: _selectedPetType,
              location: _selectedLocation,
            )
          : await LocalServiceService.getSocialPosts(
              page: _currentPage,
              pageSize: 20,
              petType: _selectedPetType,
              location: _selectedLocation,
            );

      final List<Map<String, dynamic>> newPosts =
          List<Map<String, dynamic>>.from(result['items'] ?? []);

      setState(() {
        if (refresh || _currentPage == 1) {
          _posts = newPosts;
        } else {
          _posts.addAll(newPosts);
        }
        _hasMore = newPosts.length >= 20;
        _isLoading = false;
        _isLoadingMore = false;
      });
    } catch (e) {
      // API失败时使用模拟数据
      print('API请求失败，使用模拟数据: $e');
      setState(() {
        if (refresh || _currentPage == 1) {
          _posts = _mockPosts;
        } else {
          _posts.addAll(_mockPosts);
        }
        _hasMore = false;
        _isLoading = false;
        _isLoadingMore = false;
        _errorMessage = null;
      });
    }
  }

  // 加载更多帖子
  Future<void> _loadMorePosts() async {
    if (_isLoadingMore || !_hasMore) return;

    setState(() {
      _isLoadingMore = true;
      _currentPage++;
    });

    await _loadPosts();
  }

  // 点赞功能
  Future<void> _toggleLike(int index, int postId) async {
    try {
      final result = await LocalServiceService.togglePostLike(postId);

      setState(() {
        _posts[index]['liked'] = result['liked'];
        _posts[index]['like_count'] = result['like_count'];
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['liked'] ? '点赞成功' : '取消点赞'),
          duration: const Duration(seconds: 1),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('操作失败: $e')),
      );
    }
  }

  // 原来的模拟数据（作为备用）
  final List<Map<String, dynamic>> _mockPosts = [
    {
      'id': '1',
      'userAvatar': 'https://picsum.photos/60/60?random=1',
      'username': '萌宠小主',
      'postTime': '2小时前',
      'content': '今天带我家小橘猫去洗澡，结果它居然很乖呢！',
      'images': [
        'https://picsum.photos/300/400?random=11',
        'https://picsum.photos/300/400?random=12'
      ],
      'likeCount': 128,
      'commentCount': 36,
      'viewCount': 1253,
    },
    {
      'id': '2',
      'userAvatar': 'https://picsum.photos/60/60?random=2',
      'username': '狗狗专家',
      'postTime': '4小时前',
      'content': '分享一下训练金毛的小技巧～',
      'images': ['https://picsum.photos/300/500?random=21'],
      'likeCount': 89,
      'commentCount': 22,
      'viewCount': 856,
    },
    {
      'id': '3',
      'userAvatar': 'https://picsum.photos/60/60?random=3',
      'username': '鸟儿之家',
      'postTime': '6小时前',
      'content': '我家鹦鹉学会说"你好"啦！',
      'images': [
        'https://picsum.photos/300/400?random=31',
        'https://picsum.photos/300/400?random=32',
        'https://picsum.photos/300/400?random=33'
      ],
      'likeCount': 234,
      'commentCount': 67,
      'viewCount': 2134,
    },
    {
      'id': '4',
      'userAvatar': 'https://picsum.photos/60/60?random=4',
      'username': '水族达人',
      'postTime': '8小时前',
      'content': '新买的热带鱼，颜值超高！',
      'images': ['https://picsum.photos/300/600?random=41'],
      'likeCount': 156,
      'commentCount': 43,
      'viewCount': 1876,
    },
    {
      'id': '5',
      'userAvatar': 'https://picsum.photos/60/60?random=5',
      'username': '仓鼠妈妈',
      'postTime': '12小时前',
      'content': '我家小仓鼠又偷偷藏食物了哈哈',
      'images': [
        'https://picsum.photos/300/400?random=51',
        'https://picsum.photos/300/400?random=52'
      ],
      'likeCount': 92,
      'commentCount': 18,
      'viewCount': 723,
    },
    {
      'id': '6',
      'userAvatar': 'https://picsum.photos/60/60?random=6',
      'username': '爬宠爱好者',
      'postTime': '1天前',
      'content': '蜥蜴宝宝的日常～太可爱了！',
      'images': ['https://picsum.photos/300/500?random=61'],
      'likeCount': 67,
      'commentCount': 12,
      'viewCount': 445,
    },
  ];

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  // 构建页面主体
  Widget _buildBody() {
    if (_isLoading && _posts.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_errorMessage != null && _posts.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64.w,
              color: Colors.grey[400],
            ),
            SizedBox(height: 16.h),
            Text(
              '加载失败',
              style: TextStyle(
                fontSize: 16.sp,
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 8.h),
            Text(
              _errorMessage!,
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.grey[500],
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 16.h),
            ElevatedButton(
              onPressed: () => _loadPosts(refresh: true),
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (_posts.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.pets,
              size: 64.w,
              color: Colors.grey[400],
            ),
            SizedBox(height: 16.h),
            Text(
              '暂无宠物交流内容',
              style: TextStyle(
                fontSize: 16.sp,
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 8.h),
            Text(
              '快来发布第一条宠物动态吧～',
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => _loadPosts(refresh: true),
      child: CustomScrollView(
        controller: _scrollController,
        slivers: [
          SliverPadding(
            padding: EdgeInsets.all(8.w),
            sliver: SliverGrid(
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 0.75,
                crossAxisSpacing: 8.w,
                mainAxisSpacing: 8.w,
              ),
              delegate: SliverChildBuilderDelegate(
                (context, index) {
                  final post = _posts[index % _posts.length];
                  return _buildPostCard(post);
                },
                childCount: _posts.length * 3, // 重复显示数据以演示滚动
              ),
            ),
          ),
          if (_isLoadingMore)
            SliverToBoxAdapter(
              child: Container(
                padding: EdgeInsets.all(16.w),
                alignment: Alignment.center,
                child: const CircularProgressIndicator(),
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
          '宠物交流',
          style: TextStyle(
            color: Colors.black87,
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search, color: Colors.black87),
            onPressed: () {
              _showSearchDialog();
            },
          ),
        ],
      ),
      body: _buildBody(),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
                builder: (context) => const PetSocialPublishPage()),
          );
        },
        backgroundColor: AppColors.primary,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  Widget _buildPostCard(Map<String, dynamic> post) {
    final images = post['images'] as List<String>;
    final mainImage = images.first;

    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => PetSocialDetailPage(post: post),
          ),
        );
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 主图片
            Expanded(
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  borderRadius:
                      BorderRadius.vertical(top: Radius.circular(12.r)),
                  image: DecorationImage(
                    image: NetworkImage(mainImage),
                    fit: BoxFit.cover,
                  ),
                ),
                child: Stack(
                  children: [
                    // 多图标识
                    if (images.length > 1)
                      Positioned(
                        top: 8.h,
                        right: 8.w,
                        child: Container(
                          padding: EdgeInsets.symmetric(
                              horizontal: 6.w, vertical: 2.h),
                          decoration: BoxDecoration(
                            color: Colors.black54,
                            borderRadius: BorderRadius.circular(10.r),
                          ),
                          child: Text(
                            '${images.length}',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 10.sp,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                    // 观看次数
                    Positioned(
                      bottom: 8.h,
                      right: 8.w,
                      child: Container(
                        padding: EdgeInsets.symmetric(
                            horizontal: 6.w, vertical: 2.h),
                        decoration: BoxDecoration(
                          color: Colors.black54,
                          borderRadius: BorderRadius.circular(10.r),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.visibility,
                              size: 10.sp,
                              color: Colors.white,
                            ),
                            SizedBox(width: 2.w),
                            Text(
                              _formatCount(post['viewCount']),
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 10.sp,
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
            ),

            // 用户信息和内容
            Padding(
              padding: EdgeInsets.all(12.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 用户头像和信息
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 12.r,
                        backgroundImage: NetworkImage(post['userAvatar']),
                      ),
                      SizedBox(width: 8.w),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              post['username'],
                              style: TextStyle(
                                fontSize: 12.sp,
                                fontWeight: FontWeight.w600,
                                color: Colors.black87,
                              ),
                            ),
                            Text(
                              post['postTime'],
                              style: TextStyle(
                                fontSize: 10.sp,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),

                  SizedBox(height: 8.h),

                  // 帖子内容
                  Text(
                    post['content'],
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: Colors.black87,
                      height: 1.3,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),

                  SizedBox(height: 8.h),

                  // 互动数据
                  Row(
                    children: [
                      Icon(
                        Icons.favorite_border,
                        size: 14.sp,
                        color: Colors.grey[600],
                      ),
                      SizedBox(width: 4.w),
                      Text(
                        _formatCount(post['likeCount']),
                        style: TextStyle(
                          fontSize: 10.sp,
                          color: Colors.grey[600],
                        ),
                      ),
                      SizedBox(width: 12.w),
                      Icon(
                        Icons.chat_bubble_outline,
                        size: 14.sp,
                        color: Colors.grey[600],
                      ),
                      SizedBox(width: 4.w),
                      Text(
                        _formatCount(post['commentCount']),
                        style: TextStyle(
                          fontSize: 10.sp,
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
      ),
    );
  }

  String _formatCount(int count) {
    if (count >= 1000) {
      return '${(count / 1000).toStringAsFixed(1)}k';
    }
    return count.toString();
  }

  // 显示搜索对话框
  void _showSearchDialog() {
    showDialog(
      context: context,
      builder: (context) {
        final TextEditingController searchController = TextEditingController();
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16.r),
          ),
          title: Text(
            '搜索宠物话题',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.w600,
            ),
          ),
          content: TextField(
            controller: searchController,
            decoration: InputDecoration(
              hintText: '输入关键词搜索',
              prefixIcon: const Icon(Icons.search),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8.r),
              ),
            ),
            autofocus: true,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            ElevatedButton(
              onPressed: () {
                final query = searchController.text.trim();
                if (query.isNotEmpty) {
                  Navigator.pop(context);
                  _performSearch(query);
                }
              },
              child: const Text('搜索'),
            ),
          ],
        );
      },
    );
  }

  // 执行搜索
  void _performSearch(String query) {
    setState(() {
      _currentSearchQuery = query;
    });
    _loadPosts(refresh: true);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('搜索: $query')),
    );
  }

  // 清除搜索
  void _clearSearch() {
    setState(() {
      _currentSearchQuery = '';
    });
    _loadPosts(refresh: true);
  }
}
