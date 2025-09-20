import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import '../checkin/checkin_page.dart';
import '../settings/settings_page.dart';
import '../orders/order_list_page.dart';
import '../seller/seller_center_page.dart';
import '../shop/shop_entry_page.dart';
import '../shop/shop_application_status_page.dart';
import '../../services/store_application_service.dart';
import '../../services/storage_service.dart';
import '../../services/user_role_service.dart';
import '../../services/order_service.dart';
import '../../services/user_info_service.dart';
import '../../services/deposit_service.dart';
import '../../models/user.dart';
import '../../models/deposit.dart';
import '../auth/login_page.dart';
import '../wallet/wallet_page.dart';
import '../deposit/deposit_page.dart';
import '../../utils/app_routes.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  User? _currentUser;
  bool _isLoggedIn = false;
  final UserRoleService _userRoleService = UserRoleService();
  final UserInfoService _userInfoService = UserInfoService();
  final DepositService _depositService = DepositService();

  // 订单数量统计
  Map<String, int> _orderCounts = {
    'pending': 0, // 待付款
    'paid': 0, // 待发货
    'shipped': 0, // 待收货
    'refunded': 0, // 退款售后
  };

  // 用户统计信息
  Map<String, int> _userStats = {
    'following_count': 0,
    'follower_count': 0,
    'browse_history_count': 0,
  };

  // 保证金信息
  DepositInfo? _depositInfo;

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
    // 清除可能存在的overlay
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Navigator.popUntil(context, (route) => route.isFirst);
    });
  }

  void _loadUserInfo() {
    final user = StorageService.getUser();
    final token = StorageService.getUserToken();

    setState(() {
      _currentUser = user;
      _isLoggedIn = token != null && token.isNotEmpty;
    });

    // 如果已登录，加载各种统计信息
    if (_isLoggedIn) {
      _loadOrderCounts();
      _loadUserStats();
      _loadDepositInfo();
    }
  }

  // 加载订单数量统计
  void _loadOrderCounts() async {
    try {
      final counts = await OrderService.getOrderStatusCounts();
      if (mounted) {
        setState(() {
          _orderCounts = counts;
        });
      }
    } catch (e) {
      print('加载订单统计失败: $e');
    }
  }

  // 加载用户统计信息
  void _loadUserStats() async {
    try {
      final result = await _userInfoService.getUserStats();
      if (result.success && result.data != null && mounted) {
        setState(() {
          _userStats = result.data!;
        });
      } else {
        print('获取用户统计失败: ${result.message}');
      }
    } catch (e) {
      print('加载用户统计失败: $e');
    }
  }

  // 加载保证金信息
  void _loadDepositInfo() async {
    try {
      final result = await _depositService.getDepositSummary();
      if (result.success && result.data != null && mounted) {
        setState(() {
          _depositInfo = result.data!;
        });
      } else {
        print('获取保证金信息失败: ${result.message}');
      }
    } catch (e) {
      print('加载保证金信息失败: $e');
    }
  }

  // 导航到订单列表页面
  void _navigateToOrderList(String status) {
    if (!_isLoggedIn) {
      // 未登录，跳转到登录页面
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => const LoginPage()),
      );
      return;
    }

    // 根据状态确定tab索引
    int initialTabIndex = 0;
    switch (status) {
      case 'pending':
        initialTabIndex = 1; // 待付款
        break;
      case 'paid':
        initialTabIndex = 2; // 待发货
        break;
      case 'shipped':
        initialTabIndex = 3; // 待收货
        break;
      case 'refunded':
        initialTabIndex = 4; // 退款/售后
        break;
      default:
        initialTabIndex = 0; // 全部
        break;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => OrderListPage(initialTabIndex: initialTabIndex),
      ),
    ).then((_) {
      // 从订单页面返回后刷新统计数据
      _loadOrderCounts();
      _loadUserStats();
      _loadDepositInfo();
    });
  }

  void _logout() async {
    showDialog(
      context: context,
      barrierDismissible: true, // 允许点击外部关闭
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('确认退出'),
          content: const Text('确定要退出登录吗？'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('取消'),
            ),
            TextButton(
              onPressed: () async {
                Navigator.of(context).pop();
                await StorageService.clearUserData();
                setState(() {
                  _currentUser = null;
                  _isLoggedIn = false;
                });
                // 跳转到登录页面
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (context) => const LoginPage()),
                  (route) => false,
                );
              },
              child: const Text('确定'),
            ),
          ],
        );
      },
    );
  }

  void _handleShopEntry() async {
    if (!_isLoggedIn) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => const LoginPage(),
        ),
      );
      return;
    }

    try {
      // 检查是否已有申请
      final application = await StoreApplicationService.getMyApplication();

      if (application != null) {
        // 已有申请，跳转到状态页面
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const ShopApplicationStatusPage(),
          ),
        );
      } else {
        // 没有申请，跳转到申请页面
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const ShopEntryPage(),
          ),
        );
      }
    } catch (e) {
      // 出错时默认跳转到申请页面
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => const ShopEntryPage(),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: Stack(
        children: [
          // 背景渐变
          Container(
            width: double.infinity,
            height: MediaQuery.of(context).size.height * 0.65, // 渐变覆盖约65%的屏幕高度
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Color(0xFF9C4DFF),
                  Color(0xFF7B1FA2),
                  Color(0xFFF5F5F5), // 渐变到背景色
                ],
                stops: [0.0, 0.7, 1.0], // 控制渐变停止点
              ),
            ),
          ),

          // 主要内容
          SingleChildScrollView(
            child: Column(
              children: [
                _buildHeaderSection(),
                _buildOrderSection(), // 普通的订单卡片
                _buildShopPromoBanner(),
                _buildFunctionRows(),
                _buildDepositSection(),
                _buildLuckyDrawSection(),
                SizedBox(height: 100.h), // 给底部导航栏留出空间
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: _buildFloatingActionButton(),
    );
  }

  Widget _buildHeaderSection() {
    return Container(
      height: 340.h,
      color: Colors.transparent,
      child: Stack(
        children: [
          // 背景装饰爱心图案
          Positioned(
            top: 50.h,
            left: 30.w,
            child: Opacity(
              opacity: 0.1,
              child: Icon(
                Icons.favorite,
                size: 80.w,
                color: Colors.white,
              ),
            ),
          ),
          Positioned(
            top: 80.h,
            right: 50.w,
            child: Opacity(
              opacity: 0.08,
              child: Icon(
                Icons.favorite,
                size: 120.w,
                color: Colors.white,
              ),
            ),
          ),
          Positioned(
            top: 180.h,
            left: 60.w,
            child: Opacity(
              opacity: 0.06,
              child: Icon(
                Icons.favorite,
                size: 60.w,
                color: Colors.white,
              ),
            ),
          ),
          Positioned(
            top: 200.h,
            right: 80.w,
            child: Opacity(
              opacity: 0.05,
              child: Icon(
                Icons.favorite,
                size: 90.w,
                color: Colors.white,
              ),
            ),
          ),

          // 主要内容
          Column(
            children: [
              // 状态栏区域
              Container(
                height: MediaQuery.of(context).padding.top + 44.h,
                padding: EdgeInsets.only(
                  top: MediaQuery.of(context).padding.top,
                  left: 16.w,
                  right: 16.w,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      _currentUser?.isSeller == true ? '卖家中心' : '买家中心',
                      style: TextStyle(
                        fontSize: 18.sp,
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    SizedBox(width: 8.w),
                    GestureDetector(
                      onTap: _handleRoleSwitch,
                      child: Container(
                        padding: EdgeInsets.symmetric(
                            horizontal: 8.w, vertical: 4.h),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(12.r),
                        ),
                        child: Text(
                          _currentUser?.isSeller == true ? '切换买家' : '切换卖家',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: Colors.white,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // 设置区域
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.w),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    // 退出登录按钮（如果已登录）
                    if (_isLoggedIn)
                      GestureDetector(
                        onTap: _logout,
                        child: Container(
                          padding: EdgeInsets.symmetric(
                              horizontal: 8.w, vertical: 4.h),
                          margin: EdgeInsets.only(right: 12.w),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(12.r),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.logout,
                                size: 16.w,
                                color: Colors.white,
                              ),
                              SizedBox(width: 4.w),
                              Text(
                                '退出',
                                style: TextStyle(
                                  fontSize: 12.sp,
                                  color: Colors.white,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    // 设置按钮
                    GestureDetector(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const SettingsPage(),
                          ),
                        );
                      },
                      child: Icon(
                        Icons.settings,
                        size: 22.w,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 20.h),

              // 用户信息区域
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.w),
                child: Row(
                  children: [
                    // 头像
                    Container(
                      width: 60.w,
                      height: 60.w,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                        image: _currentUser?.avatar != null &&
                                _currentUser!.avatar!.isNotEmpty
                            ? DecorationImage(
                                image: NetworkImage(_currentUser!.avatar!),
                                fit: BoxFit.cover,
                              )
                            : const DecorationImage(
                                image: NetworkImage(
                                    'https://picsum.photos/60/60?random=1'),
                                fit: BoxFit.cover,
                              ),
                      ),
                    ),
                    SizedBox(width: 16.w),
                    // 用户名和手机号
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                _currentUser?.nickname ?? '未登录',
                                style: TextStyle(
                                  fontSize: 24.sp,
                                  color: Colors.white,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              SizedBox(width: 8.w),
                              if (_isLoggedIn)
                                GestureDetector(
                                  onTap: () =>
                                      Get.toNamed(AppRoutes.personalInfo),
                                  child: Icon(
                                    Icons.edit,
                                    size: 18.w,
                                    color: Colors.white.withOpacity(0.8),
                                  ),
                                ),
                            ],
                          ),
                          if (_currentUser?.phone != null)
                            Text(
                              _currentUser!.phone,
                              style: TextStyle(
                                fontSize: 14.sp,
                                color: Colors.white.withOpacity(0.8),
                                fontWeight: FontWeight.w400,
                              ),
                            ),
                        ],
                      ),
                    ),
                    // 登录/签到按钮
                    if (_isLoggedIn)
                      GestureDetector(
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const CheckinPage(),
                            ),
                          );
                        },
                        child: Container(
                          padding: EdgeInsets.symmetric(
                              horizontal: 20.w, vertical: 8.h),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.9),
                            borderRadius: BorderRadius.circular(20.r),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                '签到',
                                style: TextStyle(
                                  fontSize: 13.sp,
                                  color: const Color(0xFF9C4DFF),
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              SizedBox(width: 4.w),
                              Container(
                                width: 6.w,
                                height: 6.w,
                                decoration: const BoxDecoration(
                                  color: Colors.red,
                                  shape: BoxShape.circle,
                                ),
                              ),
                            ],
                          ),
                        ),
                      )
                    else
                      GestureDetector(
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const LoginPage(),
                            ),
                          );
                        },
                        child: Container(
                          padding: EdgeInsets.symmetric(
                              horizontal: 20.w, vertical: 8.h),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.9),
                            borderRadius: BorderRadius.circular(20.r),
                          ),
                          child: Text(
                            '登录',
                            style: TextStyle(
                              fontSize: 13.sp,
                              color: const Color(0xFF9C4DFF),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),

              SizedBox(height: 24.h),

              // 统计数据区域
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.w),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    GestureDetector(
                      onTap: () => Get.toNamed(AppRoutes.following),
                      child: _buildStatColumn(
                          '${_userStats['following_count'] ?? 0}', '关注'),
                    ),
                    GestureDetector(
                      onTap: () => Get.toNamed(AppRoutes.followers),
                      child: _buildStatColumn(
                          '${_userStats['follower_count'] ?? 0}', '粉丝'),
                    ),
                    GestureDetector(
                      onTap: () => Get.toNamed(AppRoutes.browseHistory),
                      child: _buildStatColumn(
                          '${_userStats['browse_history_count'] ?? 0}', '历史浏览'),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 30.h),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatColumn(String number, String label) {
    return Column(
      children: [
        Text(
          number,
          style: TextStyle(
            fontSize: 24.sp,
            color: Colors.white,
            fontWeight: FontWeight.w600,
          ),
        ),
        SizedBox(height: 4.h),
        Text(
          label,
          style: TextStyle(
            fontSize: 14.sp,
            color: Colors.white,
            fontWeight: FontWeight.w400,
          ),
        ),
      ],
    );
  }

  Widget _buildOrderSection() {
    return Container(
      margin: EdgeInsets.fromLTRB(16.w, 0, 16.w, 16.h),
      padding: EdgeInsets.all(20.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // 标题行
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '我买进的',
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.w600,
                  color: const Color(0xFF333333),
                ),
              ),
              GestureDetector(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const OrderListPage(),
                    ),
                  );
                },
                child: Row(
                  children: [
                    Text(
                      '全部',
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: const Color(0xFF999999),
                      ),
                    ),
                    SizedBox(width: 4.w),
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 12.w,
                      color: const Color(0xFF999999),
                    ),
                  ],
                ),
              ),
            ],
          ),

          SizedBox(height: 20.h),

          // 订单状态图标行
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildOrderStatusItem(
                icon: Icons.credit_card,
                label: '待付款',
                badgeCount: _orderCounts['pending'] ?? 0,
                status: 'pending',
              ),
              _buildOrderStatusItem(
                icon: Icons.card_giftcard,
                label: '待发货',
                badgeCount: _orderCounts['paid'] ?? 0,
                status: 'paid',
              ),
              _buildOrderStatusItem(
                icon: Icons.local_shipping,
                label: '待收货',
                badgeCount: _orderCounts['shipped'] ?? 0,
                status: 'shipped',
              ),
              _buildOrderStatusItem(
                icon: Icons.account_balance_wallet,
                label: '退款售后',
                badgeCount: _orderCounts['refunded'] ?? 0,
                status: 'refunded',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOrderStatusItem({
    required IconData icon,
    required String label,
    required int badgeCount,
    required String status,
  }) {
    return GestureDetector(
      onTap: () => _navigateToOrderList(status),
      child: Column(
        children: [
          Stack(
            children: [
              Container(
                width: 44.w,
                height: 44.w,
                decoration: BoxDecoration(
                  color: const Color(0xFFF8F8F8),
                  borderRadius: BorderRadius.circular(22.r),
                ),
                child: Icon(
                  icon,
                  size: 22.w,
                  color: const Color(0xFF666666),
                ),
              ),
              if (badgeCount > 0)
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
                        badgeCount.toString(),
                        style: TextStyle(
                          fontSize: 10.sp,
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          ),
          SizedBox(height: 8.h),
          Text(
            label,
            style: TextStyle(
              fontSize: 12.sp,
              color: const Color(0xFF666666),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildShopPromoBanner() {
    return Container(
      margin: EdgeInsets.fromLTRB(16.w, 0, 16.w, 16.h),
      padding: EdgeInsets.symmetric(horizontal: 20.w, vertical: 16.h),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
          colors: [
            Color(0xFFFFB347),
            Color(0xFFFFCC5C),
          ],
        ),
        borderRadius: BorderRadius.circular(16.r),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              '即刻开店 | 首次发拍立享30天流量扶持',
              style: TextStyle(
                fontSize: 12.sp,
                color: Colors.white,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          SizedBox(width: 12.w),
          GestureDetector(
            onTap: () {
              _handleShopEntry();
            },
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 20.w, vertical: 8.h),
              decoration: BoxDecoration(
                color: const Color(0xFF9C4DFF),
                borderRadius: BorderRadius.circular(20.r),
              ),
              child: Text(
                '去开店',
                style: TextStyle(
                  fontSize: 12.sp,
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFunctionRows() {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 16.w),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: _buildFunctionCard(
                  '钱包',
                  '余额、红包等',
                  Icons.account_balance_wallet,
                ),
              ),
              SizedBox(width: 12.w),
              Expanded(
                child: _buildFunctionCard(
                  '保证金',
                  '拍卖保证金',
                  Icons.security,
                ),
              ),
            ],
          ),
          SizedBox(height: 12.h),
          Row(
            children: [
              Expanded(
                child: _buildFunctionCard(
                  '出价/围观',
                  '参与拍品 24',
                  Icons.visibility,
                ),
              ),
              SizedBox(width: 12.w),
              Expanded(
                child: Container(
                  height: 80.h, // 占位，保持对称
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFunctionCard(String title, String subtitle, IconData icon) {
    return GestureDetector(
      onTap: () {
        if (title == '钱包') {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const WalletPage(),
            ),
          );
        } else if (title == '保证金') {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const DepositPage(),
            ),
          );
        } else if (title == '出价/围观') {
          Get.toNamed(AppRoutes.bidRecords);
        }
      },
      child: Container(
        padding: EdgeInsets.all(16.w),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Icon(
              icon,
              size: 20.w,
              color: const Color(0xFF333333),
            ),
            SizedBox(width: 12.w),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 15.sp,
                      fontWeight: FontWeight.w600,
                      color: const Color(0xFF333333),
                    ),
                  ),
                  SizedBox(height: 4.h),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: const Color(0xFF999999),
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              size: 14.w,
              color: const Color(0xFFCCCCCC),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDepositSection() {
    return Container(
      margin: EdgeInsets.fromLTRB(16.w, 16.h, 16.w, 0),
      padding: EdgeInsets.all(20.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '我的保证金',
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF333333),
            ),
          ),
          SizedBox(height: 20.h),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${_depositInfo?.totalDeposit.toStringAsFixed(0) ?? 0}元',
                      style: TextStyle(
                        fontSize: 22.sp,
                        fontWeight: FontWeight.w600,
                        color: const Color(0xFF333333),
                      ),
                    ),
                    SizedBox(height: 4.h),
                    Text(
                      '参拍保证金',
                      style: TextStyle(
                        fontSize: 13.sp,
                        color: const Color(0xFF999999),
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${(_depositInfo?.availableForRefund ?? 0).toStringAsFixed(0)}元',
                      style: TextStyle(
                        fontSize: 22.sp,
                        fontWeight: FontWeight.w600,
                        color: const Color(0xFF333333),
                      ),
                    ),
                    SizedBox(height: 4.h),
                    Text(
                      '未占用',
                      style: TextStyle(
                        fontSize: 13.sp,
                        color: const Color(0xFF999999),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLuckyDrawSection() {
    return Container(
      margin: EdgeInsets.all(16.w),
      height: 140.h,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
          colors: [
            Color(0xFFFF6B6B),
            Color(0xFFFF8E8E),
          ],
        ),
        borderRadius: BorderRadius.circular(16.r),
      ),
      child: Stack(
        children: [
          // 背景装饰元素
          Positioned(
            right: 20.w,
            top: 20.h,
            child: Container(
              width: 60.w,
              height: 60.w,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
            ),
          ),
          Positioned(
            right: 60.w,
            top: 60.h,
            child: Container(
              width: 40.w,
              height: 40.w,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.08),
                shape: BoxShape.circle,
              ),
            ),
          ),

          // 内容
          Padding(
            padding: EdgeInsets.all(20.w),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '钻石抽奖',
                        style: TextStyle(
                          fontSize: 20.sp,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 16.h),
                      GestureDetector(
                        onTap: () {
                          Get.toNamed(AppRoutes.lottery);
                        },
                        child: Container(
                          padding: EdgeInsets.symmetric(
                            horizontal: 24.w,
                            vertical: 10.h,
                          ),
                          decoration: BoxDecoration(
                            color: const Color(0xFF9C4DFF),
                            borderRadius: BorderRadius.circular(20.r),
                          ),
                          child: Text(
                            '立即参与',
                            style: TextStyle(
                              fontSize: 13.sp,
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                // 右侧装饰图案 - 转盘等
                Container(
                  width: 80.w,
                  height: 80.w,
                  child: Stack(
                    children: [
                      // 转盘外圈
                      Container(
                        width: 80.w,
                        height: 80.w,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: Colors.white.withOpacity(0.3),
                            width: 2,
                          ),
                        ),
                      ),
                      // 内圈
                      Center(
                        child: Container(
                          width: 50.w,
                          height: 50.w,
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.3),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.stars,
                            size: 24.w,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFloatingActionButton() {
    return Positioned(
      bottom: 120.h,
      right: 20.w,
      child: GestureDetector(
        onTap: () {},
        child: Container(
          width: 60.w,
          height: 60.w,
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
                size: 20.w,
                color: Colors.white,
              ),
              SizedBox(height: 2.h),
              Text(
                '参与',
                style: TextStyle(
                  fontSize: 10.sp,
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 处理角色切换
  Future<void> _handleRoleSwitch() async {
    if (!_isLoggedIn) {
      // 未登录，跳转到登录页面
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => const LoginPage()),
      );
      return;
    }

    final currentUser = _currentUser;
    if (currentUser == null) return;

    try {
      if (currentUser.isSeller) {
        // 当前是卖家，切换到买家模式
        final result = await _userRoleService.switchToBuyerMode();
        if (result.success) {
          setState(() {
            _loadUserInfo(); // 重新加载用户信息
          });
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result.message),
              backgroundColor: Colors.green,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result.message),
              backgroundColor: Colors.red,
            ),
          );
        }
      } else {
        // 当前是买家，尝试切换到卖家模式
        final result = await _userRoleService.switchToSellerMode();
        if (result.success) {
          // 切换成功，导航到卖家中心
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const SellerCenterPage(),
            ),
          );
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result.message),
              backgroundColor: Colors.green,
            ),
          );
        } else {
          // 切换失败，显示错误信息和选项
          _showSwitchToSellerDialog(result.message);
        }
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('切换失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  /// 显示切换到卖家模式的对话框
  void _showSwitchToSellerDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('无法切换到卖家模式'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(message),
            SizedBox(height: 16.h),
            const Text('您可以：'),
            SizedBox(height: 8.h),
            const Text('• 查看开店申请状态'),
            const Text('• 申请开店（如果还没有申请）'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              // 导航到开店申请状态页面
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ShopApplicationStatusPage(),
                ),
              );
            },
            child: const Text('查看申请状态'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              // 导航到开店申请页面
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ShopEntryPage(),
                ),
              );
            },
            child: const Text('去开店'),
          ),
        ],
      ),
    );
  }
}
