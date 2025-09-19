import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:pull_to_refresh/pull_to_refresh.dart';
import 'order_detail_page.dart';
import 'logistics_tracking_page.dart';
import '../payment/payment_page.dart';
import '../../services/order_service.dart';

class OrderListPage extends StatefulWidget {
  final int initialTabIndex;

  const OrderListPage({super.key, this.initialTabIndex = 0});

  @override
  State<OrderListPage> createState() => _OrderListPageState();
}

class _OrderListPageState extends State<OrderListPage>
    with TickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  final RefreshController _refreshController =
      RefreshController(initialRefresh: false);

  List<String> _tabs = ['全部', '待付款', '待发货', '待收货', '退款/售后'];
  List<String> _statusKeys = ['', 'pending', 'paid', 'shipped', 'refunded'];

  List<Map<String, dynamic>> _orders = [];
  bool _isLoading = false;
  bool _hasMore = true;
  int _currentPage = 1;

  // 移除假数据，只显示真实API数据

  @override
  void initState() {
    super.initState();
    _tabController = TabController(
      length: _tabs.length,
      vsync: this,
      initialIndex: widget.initialTabIndex,
    );
    _tabController.addListener(_onTabChanged);
    _loadOrders();
  }

  void _onTabChanged() {
    if (!_tabController.indexIsChanging) {
      _refreshOrders();
    }
  }

  // 加载订单数据
  Future<void> _loadOrders({bool isRefresh = false}) async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
      if (isRefresh) {
        _currentPage = 1;
        _hasMore = true;
      }
    });

    try {
      final currentStatus = _statusKeys[_tabController.index];
      final result = await OrderService.getOrders(
        page: _currentPage,
        pageSize: 20,
        status: currentStatus.isEmpty ? null : currentStatus,
        orderType: 'buy', // 我买进的订单
      );

      final List<dynamic> newOrders = result['items'] ?? [];

      setState(() {
        if (isRefresh) {
          _orders = newOrders.cast<Map<String, dynamic>>();
        } else {
          _orders.addAll(newOrders.cast<Map<String, dynamic>>());
        }

        _hasMore = newOrders.length >= 20;
        _currentPage++;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        // 不再使用假数据，显示空列表和错误信息
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载订单失败: $e')),
        );
      }
    }
  }

  // 刷新订单列表
  Future<void> _refreshOrders() async {
    await _loadOrders(isRefresh: true);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    _refreshController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: SafeArea(
        child: Column(
          children: [
            SizedBox(height: 16.h),
            _buildHeader(),
            SizedBox(height: 16.h),
            _buildSearchBar(),
            SizedBox(height: 16.h),
            _buildTabBar(),
            SizedBox(height: 16.h),
            _buildOrderList(),
          ],
        ),
      ),
    );
  }

  // 构建头部
  Widget _buildHeader() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          // 返回按钮
          GestureDetector(
            onTap: () {
              Navigator.pop(context);
            },
            child: Container(
              width: 36.w,
              height: 36.w,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(18.r),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.08),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Icon(
                Icons.arrow_back_ios_new,
                size: 18.w,
                color: const Color(0xFF333333),
              ),
            ),
          ),
          SizedBox(width: 16.w),
          // 标题
          Expanded(
            child: Text(
              '我买进的',
              style: TextStyle(
                fontSize: 18.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
          ),

          // 测试按钮
          GestureDetector(
            onTap: _createTestOrders,
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 8.w, vertical: 4.h),
              decoration: BoxDecoration(
                color: const Color(0xFF9C4DFF),
                borderRadius: BorderRadius.circular(4.r),
              ),
              child: Text(
                '测试数据',
                style: TextStyle(
                  fontSize: 10.sp,
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 构建搜索栏
  Widget _buildSearchBar() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Container(
        height: 40.h,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: TextField(
          controller: _searchController,
          decoration: InputDecoration(
            hintText: '搜订单产品名称/订单编号/物流编号',
            hintStyle: TextStyle(
              fontSize: 12.sp,
              color: const Color(0xFF999999),
            ),
            prefixIcon: Icon(
              Icons.search,
              size: 18.w,
              color: const Color(0xFF999999),
            ),
            border: InputBorder.none,
            contentPadding: EdgeInsets.symmetric(
              horizontal: 16.w,
              vertical: 12.h,
            ),
          ),
        ),
      ),
    );
  }

  // 构建标签栏
  Widget _buildTabBar() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: TabBar(
        controller: _tabController,
        isScrollable: true,
        indicatorColor: const Color(0xFF9C4DFF),
        indicatorWeight: 2,
        labelColor: const Color(0xFF9C4DFF),
        unselectedLabelColor: const Color(0xFF999999),
        labelStyle: TextStyle(
          fontSize: 14.sp,
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: TextStyle(
          fontSize: 14.sp,
          fontWeight: FontWeight.w500,
        ),
        tabs: _tabs.map((tab) => Tab(text: tab)).toList(),
      ),
    );
  }

  // 构建订单列表
  Widget _buildOrderList() {
    return Expanded(
      child: SmartRefresher(
        controller: _refreshController,
        enablePullDown: true,
        enablePullUp: _hasMore,
        onRefresh: () async {
          await _refreshOrders();
          _refreshController.refreshCompleted();
        },
        onLoading: () async {
          await _loadOrders();
          if (_hasMore) {
            _refreshController.loadComplete();
          } else {
            _refreshController.loadNoData();
          }
        },
        child: _isLoading && _orders.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : _orders.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.shopping_cart_outlined,
                          size: 64.w,
                          color: const Color(0xFF999999),
                        ),
                        SizedBox(height: 16.h),
                        Text(
                          '暂无订单',
                          style: TextStyle(
                            fontSize: 16.sp,
                            color: const Color(0xFF999999),
                          ),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    physics: const BouncingScrollPhysics(),
                    padding: EdgeInsets.symmetric(horizontal: 16.w),
                    itemCount: _orders.length,
                    itemBuilder: (context, index) {
                      final order = _orders[index];
                      return _buildOrderCard(order, index);
                    },
                  ),
      ),
    );
  }

  // 构建订单卡片
  Widget _buildOrderCard(Map<String, dynamic> order, int index) {
    return Container(
      margin: EdgeInsets.only(bottom: 12.h),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // 店铺信息和状态
          Padding(
            padding: EdgeInsets.all(16.w),
            child: Row(
              children: [
                Icon(
                  Icons.store,
                  size: 16.w,
                  color: const Color(0xFF999999),
                ),
                SizedBox(width: 6.w),
                Text(
                  order['seller_info']?['nickname'] ??
                      order['storeName'] ??
                      '未知店铺',
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: const Color(0xFF333333),
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const Spacer(),
                Text(
                  OrderService.getStatusText(
                      order['order_status'] ?? order['statusText'] ?? ''),
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: Color(int.parse(
                            OrderService.getStatusColor(
                                    order['order_status'] ?? '')
                                .substring(1),
                            radix: 16) +
                        0xFF000000),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          // 商品信息
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => OrderDetailPage(order: order),
                ),
              );
            },
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: 16.w),
              child: Row(
                children: [
                  // 商品图片
                  Container(
                    width: 80.w,
                    height: 80.w,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8.r),
                      color: const Color(0xFFF5F5F5),
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8.r),
                      child: CachedNetworkImage(
                        imageUrl: order['product_info']?['images']?[0] ??
                            order['productImage'] ??
                            '',
                        fit: BoxFit.cover,
                        placeholder: (context, url) => Container(
                          color: const Color(0xFFF5F5F5),
                          child: const Center(
                            child: CircularProgressIndicator(),
                          ),
                        ),
                        errorWidget: (context, url, error) => Container(
                          color: const Color(0xFFF5F5F5),
                          child: const Icon(Icons.error),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 12.w),
                  // 商品详情
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // 商品标题
                        Text(
                          order['product_info']?['title'] ??
                              order['productTitle'] ??
                              '商品标题',
                          style: TextStyle(
                            fontSize: 14.sp,
                            color: const Color(0xFF333333),
                            fontWeight: FontWeight.w500,
                            height: 1.3,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        SizedBox(height: 8.h),
                        // 价格和数量
                        Row(
                          children: [
                            Text(
                              '¥${order['final_price'] ?? order['price'] ?? '0.00'}',
                              style: TextStyle(
                                fontSize: 16.sp,
                                color: const Color(0xFF333333),
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const Spacer(),
                            Text(
                              'x${order['items']?.length ?? order['quantity'] ?? 1}',
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
                ],
              ),
            ),
          ),
          // 实付金额
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Text(
                  '实付:',
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: const Color(0xFF333333),
                  ),
                ),
                SizedBox(width: 4.w),
                Text(
                  '¥${order['total_amount'] ?? order['totalAmount'] ?? '0.00'}',
                  style: TextStyle(
                    fontSize: 16.sp,
                    color: const Color(0xFFFF5722),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          // 操作按钮
          Container(
            padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
            decoration: BoxDecoration(
              border: Border(
                top: BorderSide(
                  color: const Color(0xFFF0F0F0),
                  width: 1,
                ),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: _buildActionButtons(order),
            ),
          ),
        ],
      ),
    );
  }

  // 构建操作按钮
  List<Widget> _buildActionButtons(Map<String, dynamic> order) {
    List<Widget> buttons = [];
    List<String> actions = OrderService.getOrderActions(
        order['order_status'] ?? order['status'] ?? '');

    for (int i = 0; i < actions.length; i++) {
      String action = actions[i];
      bool isPrimary = i == actions.length - 1; // 最后一个按钮是主要操作

      buttons.add(
        GestureDetector(
          onTap: () {
            _handleAction(action, order);
          },
          child: Container(
            padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
            decoration: BoxDecoration(
              color: isPrimary ? const Color(0xFF9C4DFF) : Colors.transparent,
              border: isPrimary
                  ? null
                  : Border.all(
                      color: const Color(0xFFE0E0E0),
                      width: 1,
                    ),
              borderRadius: BorderRadius.circular(6.r),
            ),
            child: Text(
              action,
              style: TextStyle(
                fontSize: 12.sp,
                color: isPrimary ? Colors.white : const Color(0xFF666666),
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ),
      );

      if (i < actions.length - 1) {
        buttons.add(SizedBox(width: 12.w));
      }
    }

    return buttons;
  }

  // 处理操作
  void _handleAction(String action, Map<String, dynamic> order) {
    switch (action) {
      case '取消订单':
        _showCancelOrderDialog(order);
        break;
      case '继续付款':
        _continuePayment(order);
        break;
      case '查看物流':
        _viewLogistics(order);
        break;
      case '确认收货':
        _confirmReceipt(order);
        break;
      case '申请退款':
        _applyRefund(order);
        break;
      case '再次购买':
        _buyAgain(order);
        break;
    }
  }

  // 取消订单对话框
  void _showCancelOrderDialog(Map<String, dynamic> order) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16.r),
        ),
        title: Text(
          '取消订单',
          style: TextStyle(
            fontSize: 16.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w600,
          ),
        ),
        content: Text(
          '确定要取消这个订单吗？',
          style: TextStyle(
            fontSize: 14.sp,
            color: const Color(0xFF666666),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
            },
            child: Text(
              '取消',
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF999999),
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                _orders.removeWhere((item) => item['id'] == order['id']);
              });
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('订单已取消')),
              );
            },
            child: Text(
              '确定',
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFFFF5722),
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 继续付款
  void _continuePayment(Map<String, dynamic> order) async {
    try {
      // 跳转到支付页面
      final result = await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => PaymentPage(
            orderId: order['id'],
            totalAmount: double.parse(order['total_amount'].toString()),
            orderNo: order['order_no'] ?? '',
          ),
        ),
      );

      // 如果支付成功，刷新订单列表
      if (result == true) {
        _refreshOrders();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('支付成功')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('跳转支付页面失败: $e')),
      );
    }
  }

  // 查看物流
  void _viewLogistics(Map<String, dynamic> order) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LogisticsTrackingPage(
          orderId: order['id'],
          orderNo: order['order_no'] ?? '',
        ),
      ),
    );
  }

  // 确认收货
  void _confirmReceipt(Map<String, dynamic> order) async {
    try {
      await OrderService.confirmReceived(order['id']);
      setState(() {
        order['order_status'] = 4; // 已收货
        order['status'] = '已完成';
        order['statusText'] = '已完成';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('确认收货成功')),
      );
      // 刷新订单列表
      _refreshOrders();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('确认收货失败: $e')),
      );
    }
  }

  // 申请退款
  void _applyRefund(Map<String, dynamic> order) async {
    try {
      await OrderService.applyRefund(order['id'], '用户申请退款');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('退款申请已提交，请等待处理')),
      );
      // 刷新订单列表
      _refreshOrders();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('申请退款失败: $e')),
      );
    }
  }

  // 再次购买
  void _buyAgain(Map<String, dynamic> order) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('跳转到商品页面')),
    );
  }

  // 创建测试订单数据
  void _createTestOrders() async {
    try {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('正在创建测试订单...')),
      );

      final result = await OrderService.createTestOrders();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['message'] ?? '测试订单创建成功')),
      );

      // 刷新订单列表
      _refreshOrders();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('创建测试订单失败: $e')),
      );
    }
  }
}
