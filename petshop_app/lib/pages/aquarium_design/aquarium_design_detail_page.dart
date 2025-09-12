import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:card_swiper/card_swiper.dart';
import '../../constants/app_colors.dart';

class AquariumDesignDetailPage extends StatefulWidget {
  final Map<String, dynamic> item;
  final bool isReward;

  const AquariumDesignDetailPage({
    super.key,
    required this.item,
    required this.isReward,
  });

  @override
  State<AquariumDesignDetailPage> createState() => _AquariumDesignDetailPageState();
}

class _AquariumDesignDetailPageState extends State<AquariumDesignDetailPage> {
  final TextEditingController _commentController = TextEditingController();
  
  // 模拟图片轮播数据
  final List<String> _images = [
    'https://picsum.photos/400/300?random=901',
    'https://picsum.photos/400/300?random=902',
    'https://picsum.photos/400/300?random=903',
    'https://picsum.photos/400/300?random=904',
    'https://picsum.photos/400/300?random=905',
  ];

  // 模拟评论数据
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
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
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
              backgroundImage: NetworkImage(widget.item['shopAvatar']),
            ),
            SizedBox(width: 8.w),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Li', // 用户名
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
                    height: 300.h,
                    child: Stack(
                      children: [
                        Swiper(
                          itemBuilder: (BuildContext context, int index) {
                            return Container(
                              decoration: BoxDecoration(
                                image: DecorationImage(
                                  image: NetworkImage(_images[index]),
                                  fit: BoxFit.cover,
                                ),
                              ),
                            );
                          },
                          itemCount: _images.length,
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

                  // 内容详情
                  Padding(
                    padding: EdgeInsets.all(16.w),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // 悬赏标题
                        Text(
                          '悬赏标题',
                          style: TextStyle(
                            fontSize: 18.sp,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                            height: 1.4,
                          ),
                        ),
                        SizedBox(height: 12.h),
                        
                        // 正文内容
                        Text(
                          '正文内容正文内容正文内容正文内容正文内容正文内容正文内容正文内容正文内容正文内容正文内容正文内容',
                          style: TextStyle(
                            fontSize: 14.sp,
                            color: Colors.black87,
                            height: 1.5,
                          ),
                        ),
                        SizedBox(height: 12.h),
                        
                        // 时间和地点
                        Text(
                          '2025-07-05  济南万象城',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: Colors.grey[600],
                          ),
                        ),
                        SizedBox(height: 16.h),
                        
                        // 当前悬赏价格
                        Row(
                          children: [
                            Text(
                              widget.isReward ? '当前悬赏' : '商品价格',
                              style: TextStyle(
                                fontSize: 14.sp,
                                color: Colors.grey[600],
                              ),
                            ),
                            SizedBox(width: 8.w),
                            Text(
                              '¥${widget.item['currentPrice']}',
                              style: TextStyle(
                                fontSize: 20.sp,
                                fontWeight: FontWeight.w600,
                                color: AppColors.primary,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  // 互动数据栏
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
                    decoration: BoxDecoration(
                      border: Border(
                        top: BorderSide(color: Colors.grey[200]!, width: 0.5),
                        bottom: BorderSide(color: Colors.grey[200]!, width: 0.5),
                      ),
                    ),
                    child: Row(
                      children: [
                        _buildActionButton(Icons.favorite_border, '128', false),
                        SizedBox(width: 24.w),
                        _buildActionButton(Icons.chat_bubble_outline, '36', false),
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
                        ..._comments.map((comment) => _buildCommentItem(comment)).toList(),
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
        // TODO: 实现对应的交互功能
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
                        padding: EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
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
                  contentPadding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 10.h),
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
}