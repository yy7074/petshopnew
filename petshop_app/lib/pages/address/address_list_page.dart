import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'add_address_page.dart';

class AddressListPage extends StatefulWidget {
  const AddressListPage({super.key});

  @override
  State<AddressListPage> createState() => _AddressListPageState();
}

class _AddressListPageState extends State<AddressListPage> {
  List<Map<String, dynamic>> _addresses = [
    {
      'id': '1',
      'name': '厉雪梅',
      'phone': '15210010866',
      'address': '山东省济南市历下区浪潮科技园S06楼',
      'isDefault': true,
    },
    {
      'id': '2',
      'name': '厉雪梅',
      'phone': '15210010866',
      'address': '山东省济南市历下区浪潮科技园S06楼',
      'isDefault': false,
    },
    {
      'id': '3',
      'name': '厉雪梅',
      'phone': '15210010866',
      'address': '山东省济南市历下区浪潮科技园S06楼',
      'isDefault': false,
    },
  ];

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
            _buildAddressList(),
            SizedBox(height: 24.h),
            _buildAddButton(),
            SizedBox(height: 100.h),
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
              '收货地址',
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

  // 构建地址列表
  Widget _buildAddressList() {
    return Expanded(
      child: ListView.builder(
        physics: const BouncingScrollPhysics(),
        padding: EdgeInsets.symmetric(horizontal: 16.w),
        itemCount: _addresses.length,
        itemBuilder: (context, index) {
          final address = _addresses[index];
          return _buildAddressCard(address, index);
        },
      ),
    );
  }

  // 构建地址卡片
  Widget _buildAddressCard(Map<String, dynamic> address, int index) {
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
      child: Stack(
        children: [
          Padding(
            padding: EdgeInsets.all(16.w),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 收货人信息
                Text(
                  '${address['name']} ${address['phone']}',
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: const Color(0xFF333333),
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(height: 8.h),
                // 地址详情
                Text(
                  address['address'],
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: const Color(0xFF333333),
                    height: 1.4,
                  ),
                ),
                SizedBox(height: 12.h),
                // 默认状态
                Row(
                  children: [
                    GestureDetector(
                      onTap: () {
                        _setDefaultAddress(address['id']);
                      },
                      child: Container(
                        width: 16.w,
                        height: 16.w,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: address['isDefault'] 
                                ? const Color(0xFF9C4DFF)
                                : const Color(0xFFE0E0E0),
                            width: 2,
                          ),
                          color: address['isDefault'] 
                              ? const Color(0xFF9C4DFF)
                              : Colors.transparent,
                        ),
                        child: address['isDefault']
                            ? Icon(
                                Icons.check,
                                size: 10.w,
                                color: Colors.white,
                              )
                            : null,
                      ),
                    ),
                    SizedBox(width: 6.w),
                    Text(
                      address['isDefault'] ? '已设为默认' : '默认',
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: address['isDefault'] 
                            ? const Color(0xFF9C4DFF)
                            : const Color(0xFF999999),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // 操作按钮
          Positioned(
            right: 16.w,
            top: 16.h,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                // 复制按钮
                GestureDetector(
                  onTap: () {
                    _copyAddress(address);
                  },
                  child: Container(
                    padding: EdgeInsets.symmetric(horizontal: 8.w, vertical: 4.h),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.copy,
                          size: 14.w,
                          color: const Color(0xFF9C4DFF),
                        ),
                        SizedBox(width: 4.w),
                        Text(
                          '复制',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: const Color(0xFF9C4DFF),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                SizedBox(width: 12.w),
                // 修改按钮
                GestureDetector(
                  onTap: () {
                    _editAddress(address);
                  },
                  child: Container(
                    padding: EdgeInsets.symmetric(horizontal: 8.w, vertical: 4.h),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.edit,
                          size: 14.w,
                          color: const Color(0xFF9C4DFF),
                        ),
                        SizedBox(width: 4.w),
                        Text(
                          '修改',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: const Color(0xFF9C4DFF),
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
          // 删除按钮
          Positioned(
            top: 8.h,
            right: 8.w,
            child: GestureDetector(
              onTap: () {
                _deleteAddress(address);
              },
              child: Container(
                width: 20.w,
                height: 20.w,
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.close,
                  size: 12.w,
                  color: const Color(0xFF666666),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 构建添加按钮
  Widget _buildAddButton() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: GestureDetector(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const AddAddressPage(),
            ),
          );
        },
        child: Container(
          width: double.infinity,
          padding: EdgeInsets.symmetric(vertical: 16.h),
          decoration: BoxDecoration(
            color: const Color(0xFF9C4DFF),
            borderRadius: BorderRadius.circular(12.r),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF9C4DFF).withOpacity(0.3),
                blurRadius: 8,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Text(
            '添加收货地址',
            style: TextStyle(
              fontSize: 16.sp,
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      ),
    );
  }

  // 设置默认地址
  void _setDefaultAddress(String addressId) {
    setState(() {
      for (var address in _addresses) {
        address['isDefault'] = address['id'] == addressId;
      }
    });
  }

  // 复制地址
  void _copyAddress(Map<String, dynamic> address) {
    // 这里可以添加复制到剪贴板的逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('地址已复制到剪贴板')),
    );
  }

  // 编辑地址
  void _editAddress(Map<String, dynamic> address) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AddAddressPage(
          address: address,
          isEdit: true,
        ),
      ),
    );
  }

  // 删除地址
  void _deleteAddress(Map<String, dynamic> address) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16.r),
        ),
        title: Text(
          '删除地址',
          style: TextStyle(
            fontSize: 16.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w600,
          ),
        ),
        content: Text(
          '确定要删除这个收货地址吗？',
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
                _addresses.removeWhere((item) => item['id'] == address['id']);
              });
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('地址已删除')),
              );
            },
            child: Text(
              '删除',
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
