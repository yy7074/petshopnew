import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'order_detail_page.dart';

class OrderListPage extends StatefulWidget {
  const OrderListPage({super.key});

  @override
  State<OrderListPage> createState() => _OrderListPageState();
}

class _OrderListPageState extends State<OrderListPage>
    with TickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();

  List<String> _tabs = ['全部', '待付款', '待发货', '待收货', '退款/售后'];

  List<Map<String, dynamic>> _orders = [
    {
      'id': '20251178012308012',
      'status': '待付款',
      'statusText': '待付款',
      'storeName': '店铺名称',
      'productImage': 'https://picsum.photos/200/200?random=1',
      'productTitle': '产品标题产品标题产品标题标题产品标题产品标题',
      'price': 199.99,
      'quantity': 1,
      'totalAmount': 199.99,
      'orderTime': '2025-11-17 10:12:09',
      'actions': ['取消订单', '继续付款'],
    },
    {
      'id': '20251178012308013',
      'status': '待收货',
      'statusText': '待收货',
      'storeName': '店铺名称',
      'productImage': 'https://picsum.photos/200/200?random=2',
      'productTitle': '产品标题产品标题产品标题标题产品标题产品标题',
      'price': 199.99,
      'quantity': 1,
      'totalAmount': 199.99,
      'orderTime': '2025-11-17 10:12:09',
      'actions': ['查看物流', '确认收货'],
    },
    {
      'id': '20251178012308014',
      'status': '已完成',
      'statusText': '已完成',
      'storeName': '店铺名称',
      'productImage': 'https://picsum.photos/200/200?random=3',
      'productTitle': '产品标题产品标题产品标题标题产品标题产品标题',
      'price': 199.99,
      'quantity': 1,
      'totalAmount': 199.99,
      'orderTime': '2025-11-17 10:12:09',
      'actions': ['申请退款', '再次购买'],
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabs.length, vsync: this);
    _tabController.addListener(() {
      setState(() {
        // Tab index changed
      });
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
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
          SizedBox(width: 52.w), // 占位，保持标题居中
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
      child: ListView.builder(
        physics: const BouncingScrollPhysics(),
        padding: EdgeInsets.symmetric(horizontal: 16.w),
        itemCount: _orders.length,
        itemBuilder: (context, index) {
          final order = _orders[index];
          return _buildOrderCard(order, index);
        },
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
                  order['storeName'],
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: const Color(0xFF333333),
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const Spacer(),
                Text(
                  order['statusText'],
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: const Color(0xFF9C4DFF),
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
                        imageUrl: order['productImage'],
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
                          order['productTitle'],
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
                              '¥${order['price']}',
                              style: TextStyle(
                                fontSize: 16.sp,
                                color: const Color(0xFF333333),
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const Spacer(),
                            Text(
                              'x${order['quantity']}',
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
                  '¥${order['totalAmount']}',
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
    List<String> actions = order['actions'] as List<String>;

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
  void _continuePayment(Map<String, dynamic> order) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('跳转到支付页面')),
    );
  }

  // 查看物流
  void _viewLogistics(Map<String, dynamic> order) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('跳转到物流页面')),
    );
  }

  // 确认收货
  void _confirmReceipt(Map<String, dynamic> order) {
    setState(() {
      order['status'] = '已完成';
      order['statusText'] = '已完成';
      order['actions'] = ['申请退款', '再次购买'];
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('确认收货成功')),
    );
  }

  // 申请退款
  void _applyRefund(Map<String, dynamic> order) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('跳转到退款页面')),
    );
  }

  // 再次购买
  void _buyAgain(Map<String, dynamic> order) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('跳转到商品页面')),
    );
  }
}
