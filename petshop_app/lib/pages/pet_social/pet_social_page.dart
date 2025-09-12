import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';
import 'pet_social_detail_page.dart';

class PetSocialPage extends StatefulWidget {
  const PetSocialPage({super.key});

  @override
  State<PetSocialPage> createState() => _PetSocialPageState();
}

class _PetSocialPageState extends State<PetSocialPage> {
  final ScrollController _scrollController = ScrollController();

  // 模拟社交帖子数据
  final List<Map<String, dynamic>> _posts = [
    {
      'id': '1',
      'userAvatar': 'https://picsum.photos/60/60?random=1',
      'username': '萌宠小主',
      'postTime': '2小时前',
      'content': '今天带我家小橘猫去洗澡，结果它居然很乖呢！',
      'images': ['https://picsum.photos/300/400?random=11', 'https://picsum.photos/300/400?random=12'],
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
      'images': ['https://picsum.photos/300/400?random=31', 'https://picsum.photos/300/400?random=32', 'https://picsum.photos/300/400?random=33'],
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
      'images': ['https://picsum.photos/300/400?random=51', 'https://picsum.photos/300/400?random=52'],
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
              // TODO: 实现搜索功能
            },
          ),
        ],
      ),
      body: CustomScrollView(
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
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // TODO: 实现发布新帖子功能
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('发布新帖子功能待实现')),
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
                borderRadius: BorderRadius.vertical(top: Radius.circular(12.r)),
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
                        padding: EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
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
                      padding: EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
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
}