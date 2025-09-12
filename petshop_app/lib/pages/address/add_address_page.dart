import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class AddAddressPage extends StatefulWidget {
  final Map<String, dynamic>? address;
  final bool isEdit;

  const AddAddressPage({
    super.key,
    this.address,
    this.isEdit = false,
  });

  @override
  State<AddAddressPage> createState() => _AddAddressPageState();
}

class _AddAddressPageState extends State<AddAddressPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();
  String _selectedRegion = '';

  @override
  void initState() {
    super.initState();
    if (widget.isEdit && widget.address != null) {
      _nameController.text = widget.address!['name'] ?? '';
      _phoneController.text = widget.address!['phone'] ?? '';
      _addressController.text = widget.address!['address'] ?? '';
      _selectedRegion = '山东省济南市历下区';
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
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
            SizedBox(height: 24.h),
            _buildForm(),
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

  // 构建表单
  Widget _buildForm() {
    return Expanded(
      child: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: Column(
          children: [
            // 表单卡片
            Container(
              margin: EdgeInsets.symmetric(horizontal: 16.w),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16.r),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Form(
                key: _formKey,
                child: Padding(
                  padding: EdgeInsets.all(24.w),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 标题
                      Text(
                        widget.isEdit ? '修改收货地址' : '添加收货地址',
                        style: TextStyle(
                          fontSize: 20.sp,
                          color: const Color(0xFF333333),
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      SizedBox(height: 24.h),
                      
                      // 收货人
                      _buildInputField(
                        label: '收货人',
                        controller: _nameController,
                        hintText: '请输入收货人姓名',
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return '请输入收货人姓名';
                          }
                          return null;
                        },
                      ),
                      SizedBox(height: 20.h),
                      
                      // 手机号
                      _buildInputField(
                        label: '手机号',
                        controller: _phoneController,
                        hintText: '请输入收货人手机号',
                        keyboardType: TextInputType.phone,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return '请输入手机号';
                          }
                          if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(value)) {
                            return '请输入正确的手机号';
                          }
                          return null;
                        },
                      ),
                      SizedBox(height: 20.h),
                      
                      // 地区
                      _buildRegionField(),
                      SizedBox(height: 20.h),
                      
                      // 详细地址
                      _buildInputField(
                        label: '详细地址',
                        controller: _addressController,
                        hintText: '街道、门牌号、小区等',
                        maxLines: 3,
                        suffixIcon: Icon(
                          Icons.location_on,
                          size: 20.w,
                          color: const Color(0xFF9C4DFF),
                        ),
                      ),
                      SizedBox(height: 32.h),
                      
                      // 保存按钮
                      _buildSaveButton(),
                    ],
                  ),
                ),
              ),
            ),
            SizedBox(height: 100.h),
          ],
        ),
      ),
    );
  }

  // 构建输入字段
  Widget _buildInputField({
    required String label,
    required TextEditingController controller,
    required String hintText,
    TextInputType? keyboardType,
    int maxLines = 1,
    Widget? suffixIcon,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 14.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w500,
          ),
        ),
        SizedBox(height: 8.h),
        TextFormField(
          controller: controller,
          keyboardType: keyboardType,
          maxLines: maxLines,
          validator: validator,
          decoration: InputDecoration(
            hintText: hintText,
            hintStyle: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF999999),
            ),
            suffixIcon: suffixIcon,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8.r),
              borderSide: const BorderSide(
                color: Color(0xFFE0E0E0),
                width: 1,
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8.r),
              borderSide: const BorderSide(
                color: Color(0xFFE0E0E0),
                width: 1,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8.r),
              borderSide: const BorderSide(
                color: Color(0xFF9C4DFF),
                width: 2,
              ),
            ),
            contentPadding: EdgeInsets.symmetric(
              horizontal: 12.w,
              vertical: 12.h,
            ),
          ),
        ),
      ],
    );
  }

  // 构建地区选择字段
  Widget _buildRegionField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '地区',
          style: TextStyle(
            fontSize: 14.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w500,
          ),
        ),
        SizedBox(height: 8.h),
        GestureDetector(
          onTap: () {
            _showRegionPicker();
          },
          child: Container(
            width: double.infinity,
            padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 12.h),
            decoration: BoxDecoration(
              border: Border.all(
                color: const Color(0xFFE0E0E0),
                width: 1,
              ),
              borderRadius: BorderRadius.circular(8.r),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    _selectedRegion.isEmpty ? '点击选择' : _selectedRegion,
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: _selectedRegion.isEmpty 
                          ? const Color(0xFF999999)
                          : const Color(0xFF333333),
                    ),
                  ),
                ),
                Icon(
                  Icons.arrow_forward_ios,
                  size: 14.w,
                  color: const Color(0xFF999999),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // 构建保存按钮
  Widget _buildSaveButton() {
    return GestureDetector(
      onTap: () {
        if (_formKey.currentState!.validate()) {
          _saveAddress();
        }
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
          '保存',
          style: TextStyle(
            fontSize: 16.sp,
            color: Colors.white,
            fontWeight: FontWeight.w600,
          ),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }

  // 显示地区选择器
  void _showRegionPicker() {
    showModalBottomSheet(
      context: context,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(20.r),
          topRight: Radius.circular(20.r),
        ),
      ),
      builder: (context) => Container(
        height: 400.h,
        padding: EdgeInsets.all(20.w),
        child: Column(
          children: [
            // 标题
            Text(
              '选择地区',
              style: TextStyle(
                fontSize: 18.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 20.h),
            // 地区列表
            Expanded(
              child: ListView(
                children: [
                  _buildRegionItem('山东省济南市历下区'),
                  _buildRegionItem('山东省济南市市中区'),
                  _buildRegionItem('山东省济南市槐荫区'),
                  _buildRegionItem('山东省济南市天桥区'),
                  _buildRegionItem('山东省济南市历城区'),
                  _buildRegionItem('山东省青岛市市南区'),
                  _buildRegionItem('山东省青岛市市北区'),
                  _buildRegionItem('山东省青岛市李沧区'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建地区选项
  Widget _buildRegionItem(String region) {
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedRegion = region;
        });
        Navigator.pop(context);
      },
      child: Container(
        padding: EdgeInsets.symmetric(vertical: 16.h),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: const Color(0xFFF0F0F0),
              width: 1,
            ),
          ),
        ),
        child: Text(
          region,
          style: TextStyle(
            fontSize: 14.sp,
            color: const Color(0xFF333333),
          ),
        ),
      ),
    );
  }

  // 保存地址
  void _saveAddress() {
    // 这里可以添加保存地址的逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(widget.isEdit ? '地址修改成功' : '地址添加成功'),
      ),
    );
    Navigator.pop(context);
  }
}
