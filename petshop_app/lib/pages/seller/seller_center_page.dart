import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../services/user_role_service.dart';
import '../../services/storage_service.dart';
import '../profile/profile_page.dart';

class SellerCenterPage extends StatefulWidget {
  const SellerCenterPage({super.key});

  @override
  State<SellerCenterPage> createState() => _SellerCenterPageState();
}

class _SellerCenterPageState extends State<SellerCenterPage> {
  final UserRoleService _userRoleService = UserRoleService();

  @override
  Widget build(BuildContext context) {
    final user = StorageService.getUser();

    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: CustomScrollView(
        slivers: [
          // 顶部用户信息区域
          SliverAppBar(
            expandedHeight: 200.h,
            floating: false,
            pinned: true,
            backgroundColor: const Color(0xFF9C4DFF),
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Color(0xFF9C4DFF),
                      Color(0xFF7B1FA2),
                    ],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding:
                        EdgeInsets.symmetric(horizontal: 16.w, vertical: 20.h),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            // 用户头像
                            CircleAvatar(
                              radius: 30.r,
                              backgroundColor: Colors.white.withOpacity(0.2),
                              backgroundImage: user?.avatar != null
                                  ? NetworkImage(user!.avatar!)
                                  : null,
                              child: user?.avatar == null
                                  ? Icon(
                                      Icons.person,
                                      size: 30.r,
                                      color: Colors.white,
                                    )
                                  : null,
                            ),
                            SizedBox(width: 16.w),

                            // 用户信息
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    user?.nickname ?? '卖家用户',
                                    style: TextStyle(
                                      fontSize: 20.sp,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                  ),
                                  SizedBox(height: 4.h),
                                  Text(
                                    '卖家中心',
                                    style: TextStyle(
                                      fontSize: 14.sp,
                                      color: Colors.white.withOpacity(0.8),
                                    ),
                                  ),
                                ],
                              ),
                            ),

                            // 切换买家按钮
                            GestureDetector(
                              onTap: _switchToBuyer,
                              child: Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: 16.w,
                                  vertical: 8.h,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(12.r),
                                ),
                                child: Text(
                                  '切换买家',
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
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),

          // 店铺统计数据
          SliverToBoxAdapter(
            child: Container(
              margin: EdgeInsets.all(16.w),
              padding: EdgeInsets.all(16.w),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12.r),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '店铺数据',
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFF333333),
                    ),
                  ),
                  SizedBox(height: 16.h),
                  Row(
                    children: [
                      _buildDataItem('商品数量', '0', Icons.inventory),
                      _buildDataItem('待处理订单', '0', Icons.pending_actions),
                      _buildDataItem('本月销售', '¥0', Icons.trending_up),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // 功能菜单
          SliverToBoxAdapter(
            child: Container(
              margin: EdgeInsets.symmetric(horizontal: 16.w),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12.r),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                children: [
                  _buildMenuItem(
                    icon: Icons.add_business,
                    title: '发布商品',
                    subtitle: '添加新的商品到您的店铺',
                    onTap: () {
                      Navigator.pushNamed(context, '/publish-product');
                    },
                  ),
                  _buildDivider(),
                  _buildMenuItem(
                    icon: Icons.inventory_2,
                    title: '商品管理',
                    subtitle: '管理您的商品库存和信息',
                    onTap: () {
                      Navigator.pushNamed(context, '/seller-products');
                    },
                  ),
                  _buildDivider(),
                  _buildMenuItem(
                    icon: Icons.receipt_long,
                    title: '订单管理',
                    subtitle: '处理买家订单和发货',
                    onTap: () {
                      // TODO: 导航到订单管理页面
                      _showComingSoon('订单管理');
                    },
                  ),
                  _buildDivider(),
                  _buildMenuItem(
                    icon: Icons.store,
                    title: '店铺设置',
                    subtitle: '编辑店铺信息和设置',
                    onTap: () {
                      // TODO: 导航到店铺设置页面
                      _showComingSoon('店铺设置');
                    },
                  ),
                  _buildDivider(),
                  _buildMenuItem(
                    icon: Icons.analytics,
                    title: '数据分析',
                    subtitle: '查看店铺经营数据',
                    onTap: () {
                      // TODO: 导航到数据分析页面
                      _showComingSoon('数据分析');
                    },
                  ),
                ],
              ),
            ),
          ),

          SizedBox(height: 100.h).sliver,
        ],
      ),
    );
  }

  Widget _buildDataItem(String title, String value, IconData icon) {
    return Expanded(
      child: Column(
        children: [
          Icon(
            icon,
            size: 24.w,
            color: const Color(0xFF9C4DFF),
          ),
          SizedBox(height: 8.h),
          Text(
            value,
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF333333),
            ),
          ),
          SizedBox(height: 4.h),
          Text(
            title,
            style: TextStyle(
              fontSize: 12.sp,
              color: const Color(0xFF666666),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      contentPadding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
      leading: Container(
        width: 48.w,
        height: 48.w,
        decoration: BoxDecoration(
          color: const Color(0xFF9C4DFF).withOpacity(0.1),
          borderRadius: BorderRadius.circular(12.r),
        ),
        child: Icon(
          icon,
          size: 24.w,
          color: const Color(0xFF9C4DFF),
        ),
      ),
      title: Text(
        title,
        style: TextStyle(
          fontSize: 16.sp,
          fontWeight: FontWeight.w500,
          color: const Color(0xFF333333),
        ),
      ),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          fontSize: 12.sp,
          color: const Color(0xFF666666),
        ),
      ),
      trailing: Icon(
        Icons.arrow_forward_ios,
        size: 16.w,
        color: const Color(0xFF999999),
      ),
      onTap: onTap,
    );
  }

  Widget _buildDivider() {
    return Divider(
      height: 1.h,
      thickness: 1.h,
      color: const Color(0xFFF0F0F0),
      indent: 16.w,
      endIndent: 16.w,
    );
  }

  /// 切换到买家模式
  Future<void> _switchToBuyer() async {
    final result = await _userRoleService.switchToBuyerMode();

    if (result.success) {
      if (mounted) {
        // 返回到个人中心页面（买家模式）
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (context) => const ProfilePage(),
          ),
        );

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.message),
            backgroundColor: Colors.green,
          ),
        );
      }
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.message),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// 显示即将上线提示
  void _showComingSoon(String feature) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('即将上线'),
        content: Text('$feature功能正在开发中，敬请期待！'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
}

extension SizedBoxSliver on SizedBox {
  Widget get sliver => SliverToBoxAdapter(child: this);
}
