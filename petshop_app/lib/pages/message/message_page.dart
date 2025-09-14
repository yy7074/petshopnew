import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:pull_to_refresh/pull_to_refresh.dart';
import '../../services/message_service.dart';
import 'chat_page.dart';

class MessagePage extends StatefulWidget {
  const MessagePage({super.key});

  @override
  State<MessagePage> createState() => _MessagePageState();
}

class _MessagePageState extends State<MessagePage>
    with AutomaticKeepAliveClientMixin, TickerProviderStateMixin {
  bool showNotificationBanner = true;
  late TabController _tabController;

  // 对话列表数据
  List<Map<String, dynamic>> _conversations = [];
  bool _isConversationsLoading = true;
  int _conversationsPage = 1;
  bool _hasMoreConversations = true;

  // 通知列表数据
  List<Map<String, dynamic>> _notifications = [];
  bool _isNotificationsLoading = true;
  int _notificationsPage = 1;
  bool _hasMoreNotifications = true;

  // 消息统计
  Map<String, dynamic>? _messageStats;

  // 刷新控制器
  final RefreshController _conversationsRefreshController = RefreshController();
  final RefreshController _notificationsRefreshController = RefreshController();

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadInitialData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _conversationsRefreshController.dispose();
    _notificationsRefreshController.dispose();
    super.dispose();
  }

  // 加载初始数据
  Future<void> _loadInitialData() async {
    await Future.wait([
      _loadConversations(refresh: true),
      _loadNotifications(refresh: true),
      _loadMessageStats(),
    ]);
  }

  // 加载对话列表
  Future<void> _loadConversations({bool refresh = false}) async {
    if (refresh) {
      _conversationsPage = 1;
      _hasMoreConversations = true;
    }

    if (!_hasMoreConversations) return;

    try {
      setState(() {
        if (refresh) {
          _isConversationsLoading = true;
          _conversations.clear();
        }
      });

      final result = await MessageService.getConversations(
        page: _conversationsPage,
        pageSize: 20,
      );

      final List<dynamic> items = result['items'] ?? [];
      final List<Map<String, dynamic>> newConversations = items
          .map((item) => MessageService.formatConversationForUI(item))
          .toList();

      setState(() {
        if (refresh) {
          _conversations = newConversations;
        } else {
          _conversations.addAll(newConversations);
        }
        _hasMoreConversations = newConversations.length >= 20;
        _conversationsPage++;
        _isConversationsLoading = false;
      });

      if (refresh) {
        _conversationsRefreshController.refreshCompleted();
      } else {
        _conversationsRefreshController.loadComplete();
      }
    } catch (e) {
      print('加载对话列表失败: $e');
      setState(() {
        _isConversationsLoading = false;
      });

      if (refresh) {
        _conversationsRefreshController.refreshFailed();
      } else {
        _conversationsRefreshController.loadFailed();
      }
    }
  }

  // 加载通知列表
  Future<void> _loadNotifications({bool refresh = false}) async {
    if (refresh) {
      _notificationsPage = 1;
      _hasMoreNotifications = true;
    }

    if (!_hasMoreNotifications) return;

    try {
      setState(() {
        if (refresh) {
          _isNotificationsLoading = true;
          _notifications.clear();
        }
      });

      final result = await MessageService.getNotifications(
        page: _notificationsPage,
        pageSize: 20,
      );

      final List<dynamic> items = result['items'] ?? [];
      final List<Map<String, dynamic>> newNotifications = items
          .map((item) => MessageService.formatNotificationForUI(item))
          .toList();

      setState(() {
        if (refresh) {
          _notifications = newNotifications;
        } else {
          _notifications.addAll(newNotifications);
        }
        _hasMoreNotifications = newNotifications.length >= 20;
        _notificationsPage++;
        _isNotificationsLoading = false;
      });

      if (refresh) {
        _notificationsRefreshController.refreshCompleted();
      } else {
        _notificationsRefreshController.loadComplete();
      }
    } catch (e) {
      print('加载通知列表失败: $e');
      setState(() {
        _isNotificationsLoading = false;
      });

      if (refresh) {
        _notificationsRefreshController.refreshFailed();
      } else {
        _notificationsRefreshController.loadFailed();
      }
    }
  }

  // 加载消息统计
  Future<void> _loadMessageStats() async {
    try {
      final stats = await MessageService.getMessageStats();
      setState(() {
        _messageStats = stats;
      });
    } catch (e) {
      print('加载消息统计失败: $e');
    }
  }

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
        bottom: TabBar(
          controller: _tabController,
          labelColor: const Color(0xFF9C4DFF),
          unselectedLabelColor: const Color(0xFF666666),
          indicatorColor: const Color(0xFF9C4DFF),
          indicatorWeight: 3,
          labelStyle: TextStyle(
            fontSize: 16.sp,
            fontWeight: FontWeight.w600,
          ),
          unselectedLabelStyle: TextStyle(
            fontSize: 16.sp,
            fontWeight: FontWeight.w400,
          ),
          tabs: [
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('聊天'),
                  if (_messageStats != null &&
                      _messageStats!['total_unread_messages'] > 0) ...[
                    SizedBox(width: 8.w),
                    Container(
                      padding:
                          EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
                      decoration: const BoxDecoration(
                        color: Colors.red,
                        shape: BoxShape.circle,
                      ),
                      child: Text(
                        _messageStats!['total_unread_messages'].toString(),
                        style: TextStyle(
                          fontSize: 10.sp,
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('通知'),
                  if (_messageStats != null &&
                      _messageStats!['unread_notifications'] > 0) ...[
                    SizedBox(width: 8.w),
                    Container(
                      padding:
                          EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
                      decoration: const BoxDecoration(
                        color: Colors.red,
                        shape: BoxShape.circle,
                      ),
                      child: Text(
                        _messageStats!['unread_notifications'].toString(),
                        style: TextStyle(
                          fontSize: 10.sp,
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          // 通知横幅
          if (showNotificationBanner) _buildNotificationBanner(),

          // Tab内容
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildConversationsList(),
                _buildNotificationsList(),
              ],
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

  // 构建对话列表
  Widget _buildConversationsList() {
    if (_isConversationsLoading && _conversations.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_conversations.isEmpty) {
      return _buildEmptyState('暂无聊天记录', Icons.chat_bubble_outline);
    }

    return SmartRefresher(
      controller: _conversationsRefreshController,
      enablePullDown: true,
      enablePullUp: _hasMoreConversations,
      onRefresh: () => _loadConversations(refresh: true),
      onLoading: () => _loadConversations(refresh: false),
      child: ListView.builder(
        padding: EdgeInsets.zero,
        itemCount: _conversations.length,
        itemBuilder: (context, index) {
          final conversation = _conversations[index];
          return _buildConversationItem(conversation);
        },
      ),
    );
  }

  // 构建通知列表
  Widget _buildNotificationsList() {
    if (_isNotificationsLoading && _notifications.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_notifications.isEmpty) {
      return _buildEmptyState('暂无系统通知', Icons.notifications_outlined);
    }

    return SmartRefresher(
      controller: _notificationsRefreshController,
      enablePullDown: true,
      enablePullUp: _hasMoreNotifications,
      onRefresh: () => _loadNotifications(refresh: true),
      onLoading: () => _loadNotifications(refresh: false),
      child: ListView.builder(
        padding: EdgeInsets.zero,
        itemCount: _notifications.length,
        itemBuilder: (context, index) {
          final notification = _notifications[index];
          return _buildNotificationItem(notification);
        },
      ),
    );
  }

  // 构建空状态
  Widget _buildEmptyState(String message, IconData icon) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            icon,
            size: 64.w,
            color: const Color(0xFFCCCCCC),
          ),
          SizedBox(height: 16.h),
          Text(
            message,
            style: TextStyle(
              fontSize: 16.sp,
              color: const Color(0xFF999999),
            ),
          ),
        ],
      ),
    );
  }

  // 构建对话项
  Widget _buildConversationItem(Map<String, dynamic> conversation) {
    final otherUserInfo = conversation['other_user_info'] ?? {};
    final String nickname = otherUserInfo['nickname'] ?? '未知用户';
    final String? avatar = otherUserInfo['avatar'];
    final String lastMessage = conversation['last_message_content'] ?? '';
    final String? lastMessageTime = conversation['last_message_time'];
    final int unreadCount = conversation['unread_count'] ?? 0;

    return GestureDetector(
      onTap: () {
        // 导航到聊天页面
        _openChatPage(conversation);
      },
      child: Container(
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
            // 用户头像
            Stack(
              children: [
                Container(
                  width: 50.w,
                  height: 50.w,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: const Color(0xFFF0F0F0),
                    image: avatar != null && avatar.isNotEmpty
                        ? DecorationImage(
                            image: NetworkImage(avatar.startsWith('http')
                                ? avatar
                                : 'https://catdog.dachaonet.com$avatar'),
                            fit: BoxFit.cover,
                          )
                        : null,
                  ),
                  child: avatar == null || avatar.isEmpty
                      ? Icon(
                          Icons.person,
                          size: 30.w,
                          color: const Color(0xFF999999),
                        )
                      : null,
                ),
                if (unreadCount > 0)
                  Positioned(
                    top: 0,
                    right: 0,
                    child: Container(
                      width: 16.w,
                      height: 16.w,
                      padding: EdgeInsets.symmetric(horizontal: 4.w),
                      decoration: const BoxDecoration(
                        color: Colors.red,
                        shape: BoxShape.circle,
                      ),
                      child: Center(
                        child: Text(
                          unreadCount > 99 ? '99+' : unreadCount.toString(),
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
            ),
            SizedBox(width: 12.w),

            // 中间内容
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 用户名
                  Text(
                    nickname,
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w600,
                      color: const Color(0xFF333333),
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  SizedBox(height: 4.h),

                  // 最后一条消息
                  Text(
                    lastMessage.isEmpty ? '暂无消息' : lastMessage,
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: const Color(0xFF666666),
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),

            // 时间
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  MessageService.formatMessageTime(lastMessageTime),
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: const Color(0xFF999999),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // 构建通知项
  Widget _buildNotificationItem(Map<String, dynamic> notification) {
    final String title = notification['title'] ?? '';
    final String content = notification['content'] ?? '';
    final String notificationType =
        notification['notification_type'] ?? 'system';
    final String? createdAt = notification['created_at'];
    final bool isRead = notification['is_read'] ?? false;

    return GestureDetector(
      onTap: () {
        _handleNotificationTap(notification);
      },
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
        decoration: BoxDecoration(
          color: isRead ? Colors.white : const Color(0xFFF8F8F8),
          border: const Border(
            bottom: BorderSide(
              color: Color(0xFFF0F0F0),
              width: 1,
            ),
          ),
        ),
        child: Row(
          children: [
            // 通知图标
            Container(
              width: 50.w,
              height: 50.w,
              decoration: BoxDecoration(
                color: _getNotificationIconColor(notificationType),
                shape: BoxShape.circle,
              ),
              child: Icon(
                _getNotificationIcon(notificationType),
                size: 24.w,
                color: Colors.white,
              ),
            ),
            SizedBox(width: 12.w),

            // 中间内容
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 标题和标签
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          title,
                          style: TextStyle(
                            fontSize: 16.sp,
                            fontWeight:
                                isRead ? FontWeight.w400 : FontWeight.w600,
                            color: const Color(0xFF333333),
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Container(
                        padding: EdgeInsets.symmetric(
                            horizontal: 6.w, vertical: 2.h),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE8D5FF),
                          borderRadius: BorderRadius.circular(4.r),
                        ),
                        child: Text(
                          _getNotificationTypeText(notificationType),
                          style: TextStyle(
                            fontSize: 10.sp,
                            color: const Color(0xFF9C4DFF),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 4.h),

                  // 内容
                  Text(
                    content,
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: const Color(0xFF666666),
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  SizedBox(height: 4.h),

                  // 时间
                  Text(
                    MessageService.formatMessageTime(createdAt),
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: const Color(0xFF999999),
                    ),
                  ),
                ],
              ),
            ),

            // 未读标识
            if (!isRead)
              Container(
                width: 8.w,
                height: 8.w,
                decoration: const BoxDecoration(
                  color: Colors.red,
                  shape: BoxShape.circle,
                ),
              ),
          ],
        ),
      ),
    );
  }

  // 打开聊天页面
  void _openChatPage(Map<String, dynamic> conversation) {
    final otherUserInfo = conversation['other_user_info'] ?? {};
    final int? otherUserId = otherUserInfo['id'];
    final int conversationId = conversation['id'];

    if (otherUserId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('用户信息错误')),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatPage(
          conversationId: conversationId,
          otherUserInfo: otherUserInfo,
        ),
      ),
    ).then((_) {
      // 返回后刷新对话列表和统计
      _loadConversations(refresh: true);
      _loadMessageStats();
    });
  }

  // 处理通知点击
  void _handleNotificationTap(Map<String, dynamic> notification) async {
    final int notificationId = notification['id'];
    final bool isRead = notification['is_read'] ?? false;

    // 如果未读，标记为已读
    if (!isRead) {
      try {
        await MessageService.markNotificationRead(notificationId);

        // 更新本地状态
        setState(() {
          final index =
              _notifications.indexWhere((n) => n['id'] == notificationId);
          if (index != -1) {
            _notifications[index]['is_read'] = true;
          }
        });

        // 刷新统计
        _loadMessageStats();
      } catch (e) {
        print('标记通知已读失败: $e');
      }
    }

    // TODO: 根据通知类型处理跳转
    final String? relatedType = notification['related_type'];
    final int? relatedId = notification['related_id'];

    print('处理通知: type=$relatedType, id=$relatedId');
  }

  // 获取通知图标
  IconData _getNotificationIcon(String notificationType) {
    switch (notificationType) {
      case 'auction':
        return Icons.gavel;
      case 'order':
        return Icons.shopping_bag;
      case 'payment':
        return Icons.payment;
      default:
        return Icons.notifications;
    }
  }

  // 获取通知图标颜色
  Color _getNotificationIconColor(String notificationType) {
    switch (notificationType) {
      case 'auction':
        return Colors.red;
      case 'order':
        return Colors.green;
      case 'payment':
        return Colors.orange;
      default:
        return const Color(0xFF9C4DFF);
    }
  }

  // 获取通知类型文本
  String _getNotificationTypeText(String notificationType) {
    switch (notificationType) {
      case 'auction':
        return '拍卖';
      case 'order':
        return '订单';
      case 'payment':
        return '支付';
      default:
        return '系统';
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
