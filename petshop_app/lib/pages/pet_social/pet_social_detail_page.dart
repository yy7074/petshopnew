import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:card_swiper/card_swiper.dart';
import '../../constants/app_colors.dart';

class PetSocialDetailPage extends StatefulWidget {
  final Map<String, dynamic> post;

  const PetSocialDetailPage({super.key, required this.post});

  @override
  State<PetSocialDetailPage> createState() => _PetSocialDetailPageState();
}

class _PetSocialDetailPageState extends State<PetSocialDetailPage> {
  final TextEditingController _commentController = TextEditingController();
  final FocusNode _commentFocusNode = FocusNode();
  final List<Map<String, dynamic>> _comments = [
    {
      'id': '1',
      'userAvatar': 'https://picsum.photos/40/40?random=101',
      'username': '用户昵称',
      'content': '评论评论评论评论评论评论评论评论评论评论评论评论评论评论评论评论评论..',
      'time': '2025-07-05',
      'isReply': false,
    },
    {
      'id': '2',
      'userAvatar': 'https://picsum.photos/40/40?random=102',
      'username': 'Li',
      'content': '评论评论评论评论评论评论评论评论评论评论评论评论评论评论评论评论评论..',
      'time': '2025-07-05 23:42:23',
      'isReply': true,
      'label': '作者',
    },
    {
      'id': '3',
      'userAvatar': 'https://picsum.photos/40/40?random=103',
      'username': '用户昵称',
      'content': '评论评论评论评论评论评论评论评论评论评论评论评论评论评论评论评论评论..',
      'time': '2025-07-05',
      'isReply': false,
    },
  ];

  @override
  void dispose() {
    _commentController.dispose();
    _commentFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final images = widget.post['images'] as List<String>;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.black87),
          onPressed: () => Navigator.pop(context),
        ),
        title: Row(
          children: [
            CircleAvatar(
              radius: 18.r,
              backgroundImage: NetworkImage(widget.post['userAvatar']),
            ),
            SizedBox(width: 8.w),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.post['username'],
                  style: TextStyle(
                    color: Colors.black87,
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const Spacer(),
            Container(
              padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h),
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(15.r),
              ),
              child: Text(
                '关注',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12.sp,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
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
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 图片轮播
                  Container(
                    height: 400.h,
                    child: Stack(
                      children: [
                        Swiper(
                          itemBuilder: (BuildContext context, int index) {
                            return Container(
                              decoration: BoxDecoration(
                                image: DecorationImage(
                                  image: NetworkImage(images[index]),
                                  fit: BoxFit.cover,
                                ),
                              ),
                            );
                          },
                          itemCount: images.length,
                          pagination: SwiperPagination(
                            alignment: Alignment.bottomCenter,
                            margin: EdgeInsets.only(bottom: 20.h),
                            builder: DotSwiperPaginationBuilder(
                              color: Colors.white.withValues(alpha: 0.5),
                              activeColor: Colors.white,
                              size: 8.0,
                              activeSize: 8.0,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  // 帖子内容
                  Padding(
                    padding: EdgeInsets.all(16.w),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '求助：两个月比熊一顿喂食量该多少呀？',
                          style: TextStyle(
                            fontSize: 18.sp,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                            height: 1.4,
                          ),
                        ),
                        SizedBox(height: 12.h),
                        Text(
                          '刚到家几天的小比熊，自己2个月2天，第一次养狗，有没有人知道该喂多少呀？',
                          style: TextStyle(
                            fontSize: 14.sp,
                            color: Colors.black87,
                            height: 1.5,
                          ),
                        ),
                        SizedBox(height: 12.h),
                        Text(
                          '2025-07-05  济南万象城',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),

                  // 互动数据栏
                  Container(
                    padding:
                        EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
                    decoration: BoxDecoration(
                      border: Border(
                        top: BorderSide(color: Colors.grey[200]!, width: 0.5),
                        bottom:
                            BorderSide(color: Colors.grey[200]!, width: 0.5),
                      ),
                    ),
                    child: Row(
                      children: [
                        _buildActionButton(Icons.favorite_border,
                            '${widget.post['likeCount']}', false),
                        SizedBox(width: 24.w),
                        _buildActionButton(Icons.chat_bubble_outline,
                            '${widget.post['commentCount']}', false),
                        SizedBox(width: 24.w),
                        _buildActionButton(Icons.share, '分享', false),
                        const Spacer(),
                        _buildActionButton(Icons.bookmark_border, '收藏', false),
                      ],
                    ),
                  ),

                  // 全部评论
                  Container(
                    padding: EdgeInsets.all(16.w),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '全部评论',
                          style: TextStyle(
                            fontSize: 16.sp,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                          ),
                        ),
                        SizedBox(height: 16.h),

                        // 评论列表
                        ..._comments
                            .map((comment) => _buildCommentItem(comment))
                            .toList(),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // 底部评论输入区
          _buildCommentInputBar(),
        ],
      ),
    );
  }

  Widget _buildActionButton(IconData icon, String label, bool isActive) {
    return GestureDetector(
      onTap: () {
        _handleActionTap(label, isActive);
      },
      child: Row(
        children: [
          Icon(
            icon,
            size: 20.sp,
            color: isActive ? AppColors.primary : Colors.grey[600],
          ),
          SizedBox(width: 4.w),
          Text(
            label,
            style: TextStyle(
              fontSize: 14.sp,
              color: isActive ? AppColors.primary : Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCommentItem(Map<String, dynamic> comment) {
    return Container(
      margin: EdgeInsets.only(bottom: 16.h),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 20.r,
            backgroundImage: NetworkImage(comment['userAvatar']),
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      comment['username'],
                      style: TextStyle(
                        fontSize: 14.sp,
                        fontWeight: FontWeight.w600,
                        color: Colors.black87,
                      ),
                    ),
                    if (comment['isReply'] == true && comment['label'] != null)
                      Container(
                        margin: EdgeInsets.only(left: 8.w),
                        padding: EdgeInsets.symmetric(
                            horizontal: 6.w, vertical: 2.h),
                        decoration: BoxDecoration(
                          color: AppColors.primary,
                          borderRadius: BorderRadius.circular(8.r),
                        ),
                        child: Text(
                          comment['label'],
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 10.sp,
                          ),
                        ),
                      ),
                  ],
                ),
                SizedBox(height: 4.h),
                Text(
                  comment['content'],
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: Colors.black87,
                    height: 1.4,
                  ),
                ),
                SizedBox(height: 8.h),
                Row(
                  children: [
                    Text(
                      comment['time'],
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: Colors.grey[600],
                      ),
                    ),
                    const Spacer(),
                    GestureDetector(
                      onTap: () {
                        // TODO: 实现回复功能
                      },
                      child: Text(
                        '回复',
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: Colors.grey[600],
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCommentInputBar() {
    return Container(
      padding: EdgeInsets.only(
        left: 16.w,
        right: 16.w,
        top: 12.h,
        bottom: MediaQuery.of(context).padding.bottom + 12.h,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(
          top: BorderSide(color: Colors.grey[200]!, width: 0.5),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Container(
              height: 40.h,
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(20.r),
              ),
              child: TextField(
                controller: _commentController,
                decoration: InputDecoration(
                  hintText: '留下您的评论...',
                  hintStyle: TextStyle(
                    color: Colors.grey[500],
                    fontSize: 14.sp,
                  ),
                  border: InputBorder.none,
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 16.w, vertical: 10.h),
                ),
                style: TextStyle(fontSize: 14.sp),
              ),
            ),
          ),
          SizedBox(width: 12.w),
          GestureDetector(
            onTap: () {
              // TODO: 实现发送评论功能
              if (_commentController.text.trim().isNotEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('评论发送成功')),
                );
                _commentController.clear();
              }
            },
            child: Container(
              width: 40.w,
              height: 40.h,
              decoration: BoxDecoration(
                color: AppColors.primary,
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.send,
                color: Colors.white,
                size: 18.sp,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 处理动作按钮点击
  void _handleActionTap(String label, bool isActive) {
    switch (label) {
      case '点赞':
        _toggleLike(isActive);
        break;
      case '评论':
        _focusCommentInput();
        break;
      case '分享':
        _sharePost();
        break;
      default:
        break;
    }
  }

  // 切换点赞状态
  void _toggleLike(bool isCurrentlyLiked) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(isCurrentlyLiked ? '已取消点赞' : '已点赞'),
        duration: const Duration(seconds: 1),
      ),
    );
    // TODO: 实现实际的点赞API调用
  }

  // 聚焦评论输入框
  void _focusCommentInput() {
    _commentFocusNode.requestFocus();
  }

  // 分享帖子
  void _sharePost() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('分享功能开发中'),
        duration: Duration(seconds: 1),
      ),
    );
    // TODO: 实现实际的分享功能
  }
}
