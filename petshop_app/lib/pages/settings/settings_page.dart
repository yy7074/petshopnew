import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../address/address_list_page.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  bool _messagePushEnabled = false;
  String _cacheSize = '246.2M';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: SafeArea(
        child: Column(
          children: [
            SizedBox(height: 16.h),
            _buildHeader(),
            SizedBox(height: 24.h),
            _buildContent(),
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
              '设置',
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

  // 构建内容
  Widget _buildContent() {
    return Expanded(
      child: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: Column(
          children: [
            // 账号信息
            _buildSection(
              '账号信息',
              [
                _buildAccountItem(
                  '头像',
                  null,
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 40.w,
                        height: 40.w,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: const Color(0xFFF0F0F0),
                        ),
                        child: ClipOval(
                          child: CachedNetworkImage(
                            imageUrl:
                                'https://picsum.photos/100/100?random=avatar',
                            fit: BoxFit.cover,
                            placeholder: (context, url) => Container(
                              color: const Color(0xFFF0F0F0),
                              child: const Icon(
                                Icons.person,
                                color: Color(0xFF999999),
                              ),
                            ),
                            errorWidget: (context, url, error) => Container(
                              color: const Color(0xFFF0F0F0),
                              child: const Icon(
                                Icons.person,
                                color: Color(0xFF999999),
                              ),
                            ),
                          ),
                        ),
                      ),
                      SizedBox(width: 8.w),
                      Icon(
                        Icons.arrow_forward_ios,
                        size: 14.w,
                        color: const Color(0xFF999999),
                      ),
                    ],
                  ),
                ),
                _buildAccountItem(
                  '昵称',
                  'Li',
                  hasArrow: true,
                ),
                _buildAccountItem(
                  '手机号',
                  '199****1022',
                ),
                _buildAccountItem(
                  '绑定微信',
                  '已绑定',
                ),
                _buildAccountItem(
                  '收货地址',
                  null,
                  hasArrow: true,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const AddressListPage(),
                      ),
                    );
                  },
                ),
              ],
            ),
            SizedBox(height: 24.h),

            // 辅助功能
            _buildSection(
              '辅助功能',
              [
                _buildAccountItem(
                  '清除缓存',
                  _cacheSize,
                  hasArrow: true,
                  onTap: () {
                    _showClearCacheDialog();
                  },
                ),
                _buildAccountItem(
                  '接收消息推送',
                  null,
                  trailing: Switch(
                    value: _messagePushEnabled,
                    onChanged: (value) {
                      setState(() {
                        _messagePushEnabled = value;
                      });
                    },
                    activeColor: const Color(0xFF9C4DFF),
                  ),
                ),
                _buildAccountItem(
                  '关于我们',
                  null,
                  hasArrow: true,
                  onTap: () {
                    _showAboutDialog();
                  },
                ),
              ],
            ),
            SizedBox(height: 24.h),

            // 账号管理
            _buildSection(
              '账号管理',
              [
                _buildAccountItem(
                  '退出登录',
                  null,
                  onTap: () {
                    _showLogoutDialog();
                  },
                ),
                _buildAccountItem(
                  '注销账号',
                  null,
                  hasArrow: true,
                  onTap: () {
                    _showDeactivateDialog();
                  },
                ),
              ],
            ),
            SizedBox(height: 100.h),
          ],
        ),
      ),
    );
  }

  // 构建分组
  Widget _buildSection(String title, List<Widget> children) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 分组标题
          Padding(
            padding: EdgeInsets.only(left: 16.w, bottom: 12.h),
            child: Text(
              title,
              style: TextStyle(
                fontSize: 16.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          // 分组内容
          Container(
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
              children: children,
            ),
          ),
        ],
      ),
    );
  }

  // 构建账号项目
  Widget _buildAccountItem(
    String title,
    String? value, {
    bool hasArrow = false,
    Widget? trailing,
    VoidCallback? onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 16.h),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: const Color(0xFFF0F0F0),
              width: 1,
            ),
          ),
        ),
        child: Row(
          children: [
            // 标题
            Text(
              title,
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w500,
              ),
            ),
            const Spacer(),
            // 值或自定义尾部
            if (trailing != null)
              trailing
            else if (value != null)
              Text(
                value,
                style: TextStyle(
                  fontSize: 14.sp,
                  color: const Color(0xFF666666),
                ),
              ),
            // 箭头
            if (hasArrow && trailing == null) ...[
              SizedBox(width: 8.w),
              Icon(
                Icons.arrow_forward_ios,
                size: 14.w,
                color: const Color(0xFF999999),
              ),
            ],
          ],
        ),
      ),
    );
  }

  // 显示清除缓存对话框
  void _showClearCacheDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16.r),
        ),
        title: Text(
          '清除缓存',
          style: TextStyle(
            fontSize: 16.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w600,
          ),
        ),
        content: Text(
          '确定要清除所有缓存吗？这将删除应用中的临时文件。',
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
              setState(() {
                _cacheSize = '0.0M';
              });
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('缓存已清除')),
              );
            },
            child: Text(
              '确定',
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF9C4DFF),
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 显示关于我们对话框
  void _showAboutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16.r),
        ),
        title: Text(
          '关于我们',
          style: TextStyle(
            fontSize: 16.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w600,
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '拍宠有道',
              style: TextStyle(
                fontSize: 18.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w700,
              ),
            ),
            SizedBox(height: 8.h),
            Text(
              '版本 1.0.0',
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF666666),
              ),
            ),
            SizedBox(height: 16.h),
            Text(
              '专业的宠物拍卖平台，为您提供优质的宠物交易服务。',
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF666666),
                height: 1.5,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
            },
            child: Text(
              '确定',
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF9C4DFF),
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 显示退出登录对话框
  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16.r),
        ),
        title: Text(
          '退出登录',
          style: TextStyle(
            fontSize: 16.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w600,
          ),
        ),
        content: Text(
          '确定要退出当前账号吗？',
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
              // 这里可以添加退出登录的逻辑
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('已退出登录')),
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

  // 显示注销账号对话框
  void _showDeactivateDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16.r),
        ),
        title: Text(
          '注销账号',
          style: TextStyle(
            fontSize: 16.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w600,
          ),
        ),
        content: Text(
          '注销账号后将无法恢复，确定要继续吗？',
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
              // 这里可以添加注销账号的逻辑
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('账号注销申请已提交')),
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
}
