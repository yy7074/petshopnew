import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class MessagePage extends StatefulWidget {
  const MessagePage({super.key});

  @override
  State<MessagePage> createState() => _MessagePageState();
}

class _MessagePageState extends State<MessagePage>
    with AutomaticKeepAliveClientMixin {
  bool showNotificationBanner = true;

  @override
  bool get wantKeepAlive => true;

  // 模拟消息数据
  final List<Map<String, dynamic>> messages = [
    {
      'type': 'platform',
      'title': '平台通知',
      'tag': '系统',
      'content': '[标题标题标题标题标题标题标...]您围观的拍品...',
      'time': '星期三 21:25',
      'icon': Icons.notifications,
      'iconColor': const Color(0xFF9C4DFF),
      'unreadCount': 0,
    },
    {
      'type': 'auction',
      'title': '新品开拍',
      'tag': '系统',
      'content': '为你推荐新品好物',
      'time': '星期二 14:30',
      'icon': Icons.gavel,
      'iconColor': Colors.red,
      'unreadCount': 0,
    },
    {
      'type': 'chat',
      'title': '水族馆',
      'content': '这个是性价比最高的款式了',
      'time': '星期一 16:45',
      'avatar': 'https://picsum.photos/50/50?random=1',
      'unreadCount': 3,
      'thumbnail': 'https://picsum.photos/60/60?random=2',
    },
    {
      'type': 'chat',
      'title': '水族馆',
      'content': '好的，我考虑一下',
      'time': '星期一 15:20',
      'avatar': 'https://picsum.photos/50/50?random=3',
      'unreadCount': 0,
      'thumbnail': 'https://picsum.photos/60/60?random=4',
    },
  ];

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text(
          '消息',
          style: TextStyle(
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
            color: const Color(0xFF333333),
          ),
        ),
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        automaticallyImplyLeading: false,
      ),
      body: Column(
        children: [
          // 通知横幅
          if (showNotificationBanner) _buildNotificationBanner(),

          // 消息列表
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.zero,
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final message = messages[index];
                return _buildMessageItem(message);
              },
            ),
          ),
        ],
      ),
      floatingActionButton: _buildFloatingActionButton(),
    );
  }

  // 构建通知横幅
  Widget _buildNotificationBanner() {
    return Container(
      margin: EdgeInsets.all(16.w),
      padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
      decoration: BoxDecoration(
        color: const Color(0xFF9C4DFF),
        borderRadius: BorderRadius.circular(8.r),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              '点击开启消息通知,不再错过拍品信息',
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.white,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          SizedBox(width: 12.w),
          GestureDetector(
            onTap: () {
              // 开启通知
              print('开启消息通知');
            },
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(4.r),
              ),
              child: Text(
                '开启 >',
                style: TextStyle(
                  fontSize: 12.sp,
                  color: const Color(0xFF9C4DFF),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
          SizedBox(width: 8.w),
          GestureDetector(
            onTap: () {
              setState(() {
                showNotificationBanner = false;
              });
            },
            child: Icon(
              Icons.close,
              size: 16.w,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  // 构建消息项
  Widget _buildMessageItem(Map<String, dynamic> message) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: Color(0xFFF0F0F0),
            width: 1,
          ),
        ),
      ),
      child: Row(
        children: [
          // 左侧图标或头像
          _buildMessageIcon(message),
          SizedBox(width: 12.w),

          // 中间内容
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 标题和标签
                Row(
                  children: [
                    Text(
                      message['title'],
                      style: TextStyle(
                        fontSize: 16.sp,
                        fontWeight: FontWeight.w600,
                        color: const Color(0xFF333333),
                      ),
                    ),
                    if (message['tag'] != null) ...[
                      SizedBox(width: 8.w),
                      Container(
                        padding: EdgeInsets.symmetric(
                            horizontal: 6.w, vertical: 2.h),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE8D5FF),
                          borderRadius: BorderRadius.circular(4.r),
                        ),
                        child: Text(
                          message['tag'],
                          style: TextStyle(
                            fontSize: 10.sp,
                            color: const Color(0xFF9C4DFF),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                SizedBox(height: 4.h),

                // 内容
                Text(
                  message['content'],
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: const Color(0xFF666666),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                SizedBox(height: 4.h),

                // 时间
                Text(
                  message['time'],
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: const Color(0xFF999999),
                  ),
                ),
              ],
            ),
          ),

          // 右侧内容
          Row(
            children: [
              // 缩略图
              if (message['thumbnail'] != null) ...[
                Container(
                  width: 40.w,
                  height: 40.w,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(4.r),
                    image: DecorationImage(
                      image: NetworkImage(message['thumbnail']),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                SizedBox(width: 8.w),
              ],

              // 未读数量
              if (message['unreadCount'] > 0)
                Container(
                  width: 18.w,
                  height: 18.w,
                  decoration: const BoxDecoration(
                    color: Colors.red,
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      message['unreadCount'].toString(),
                      style: TextStyle(
                        fontSize: 10.sp,
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }

  // 构建消息图标
  Widget _buildMessageIcon(Map<String, dynamic> message) {
    if (message['avatar'] != null) {
      // 聊天消息使用头像
      return Stack(
        children: [
          Container(
            width: 50.w,
            height: 50.w,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              image: DecorationImage(
                image: NetworkImage(message['avatar']),
                fit: BoxFit.cover,
              ),
            ),
          ),
          if (message['unreadCount'] > 0)
            Positioned(
              top: 0,
              right: 0,
              child: Container(
                width: 16.w,
                height: 16.w,
                decoration: const BoxDecoration(
                  color: Colors.red,
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: Text(
                    message['unreadCount'].toString(),
                    style: TextStyle(
                      fontSize: 8.sp,
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            ),
        ],
      );
    } else {
      // 系统消息使用图标
      return Container(
        width: 50.w,
        height: 50.w,
        decoration: BoxDecoration(
          color: message['iconColor'],
          shape: BoxShape.circle,
        ),
        child: Icon(
          message['icon'],
          size: 24.w,
          color: Colors.white,
        ),
      );
    }
  }

  // 构建浮动操作按钮
  Widget _buildFloatingActionButton() {
    return Container(
      width: 80.w,
      height: 80.w,
      decoration: BoxDecoration(
        color: const Color(0xFF9C4DFF),
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF9C4DFF).withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.gavel,
            size: 24.w,
            color: Colors.white,
          ),
          SizedBox(height: 2.h),
          Text(
            '参与',
            style: TextStyle(
              fontSize: 12.sp,
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
