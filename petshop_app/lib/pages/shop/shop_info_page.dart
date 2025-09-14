import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:image_picker/image_picker.dart';
import '../../services/store_application_service.dart';
import '../../services/storage_service.dart';
import '../../models/user.dart';

class ShopInfoPage extends StatefulWidget {
  final String storeType;

  const ShopInfoPage({
    super.key,
    required this.storeType,
  });

  @override
  State<ShopInfoPage> createState() => _ShopInfoPageState();
}

class _ShopInfoPageState extends State<ShopInfoPage> {
  final _formKey = GlobalKey<FormState>();
  final _shopNameController = TextEditingController();
  final _shopIntroController = TextEditingController();
  final _consigneeNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();
  final _realNameController = TextEditingController();
  final _idNumberController = TextEditingController();

  String _selectedRegion = '';
  String _idStartDate = '';
  String _idEndDate = '';
  bool _isLongTerm = false;
  bool _agreeTerms = false;
  bool _isSubmitting = false;

  // 图片相关
  String? _idFrontImageUrl;
  String? _idBackImageUrl;
  String? _businessLicenseImageUrl;

  User? _currentUser;

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
  }

  void _loadUserInfo() {
    final user = StorageService.getUser();
    setState(() {
      _currentUser = user;
    });
  }

  @override
  void dispose() {
    _shopNameController.dispose();
    _shopIntroController.dispose();
    _consigneeNameController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
    _realNameController.dispose();
    _idNumberController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              SizedBox(height: 16.h),
              _buildHeader(),
              SizedBox(height: 16.h),
              _buildProgressIndicator(),
              SizedBox(height: 24.h),
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  child: Column(
                    children: [
                      _buildImportantReminder(),
                      SizedBox(height: 24.h),
                      _buildShopInfo(),
                      SizedBox(height: 24.h),
                      _buildReturnAddress(),
                      SizedBox(height: 24.h),
                      _buildRealNameInfo(),
                      SizedBox(height: 24.h),
                      _buildIdPhotos(),
                      SizedBox(height: 24.h),
                      _buildBusinessLicense(),
                      SizedBox(height: 24.h),
                      _buildTermsAndActions(),
                      SizedBox(height: 100.h),
                    ],
                  ),
                ),
              ),
            ],
          ),
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
              '店铺入驻',
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

  // 构建进度指示器
  Widget _buildProgressIndicator() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          _buildProgressStep('店铺信息', 1, true),
          _buildProgressLine(true),
          _buildProgressStep('账户密码', 2, false),
          _buildProgressLine(false),
          _buildProgressStep('支付费用', 3, false),
          _buildProgressLine(false),
          _buildProgressStep('平台审核', 4, false),
          _buildProgressLine(false),
          _buildProgressStep('支付签约', 5, false),
        ],
      ),
    );
  }

  // 构建进度步骤
  Widget _buildProgressStep(String title, int step, bool isCompleted) {
    return Column(
      children: [
        Container(
          width: 24.w,
          height: 24.w,
          decoration: BoxDecoration(
            color:
                isCompleted ? const Color(0xFF9C4DFF) : const Color(0xFFE0E0E0),
            shape: BoxShape.circle,
          ),
          child: isCompleted
              ? Icon(
                  Icons.check,
                  size: 14.w,
                  color: Colors.white,
                )
              : Center(
                  child: Text(
                    '$step',
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
        ),
        SizedBox(height: 4.h),
        Text(
          title,
          style: TextStyle(
            fontSize: 10.sp,
            color:
                isCompleted ? const Color(0xFF9C4DFF) : const Color(0xFF999999),
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  // 构建进度线
  Widget _buildProgressLine(bool isCompleted) {
    return Expanded(
      child: Container(
        height: 2.h,
        margin: EdgeInsets.symmetric(horizontal: 4.w),
        decoration: BoxDecoration(
          color:
              isCompleted ? const Color(0xFF9C4DFF) : const Color(0xFFE0E0E0),
          borderRadius: BorderRadius.circular(1.r),
        ),
      ),
    );
  }

  // 构建重要提醒
  Widget _buildImportantReminder() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FA),
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '重要提醒',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w600,
            ),
          ),
          SizedBox(height: 8.h),
          Text(
            '开店时填写的姓名、身份证号、手机号必须是真实信息,且三者必须属于同一个人!如果信息不一致(例如用他人身份证或手机号)将导致:',
            style: TextStyle(
              fontSize: 12.sp,
              color: const Color(0xFF666666),
              height: 1.4,
            ),
          ),
          SizedBox(height: 8.h),
          _buildReminderItem('可能无法通过开店审核'),
          _buildReminderItem('后续店铺货款可能无法提现到银行卡'),
        ],
      ),
    );
  }

  // 构建提醒项目
  Widget _buildReminderItem(String text) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 2.h),
      child: Row(
        children: [
          Container(
            width: 4.w,
            height: 4.w,
            decoration: const BoxDecoration(
              color: Color(0xFF666666),
              shape: BoxShape.circle,
            ),
          ),
          SizedBox(width: 8.w),
          Text(
            text,
            style: TextStyle(
              fontSize: 12.sp,
              color: const Color(0xFF666666),
            ),
          ),
        ],
      ),
    );
  }

  // 构建店铺信息
  Widget _buildShopInfo() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
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
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '店铺信息',
              style: TextStyle(
                fontSize: 16.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 16.h),
            _buildInputField(
              '店铺名称',
              _shopNameController,
              '不包含他人注册商标或联系方式',
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '请输入店铺名称';
                }
                if (value.trim().length < 2) {
                  return '店铺名称至少2个字符';
                }
                return null;
              },
            ),
            SizedBox(height: 16.h),
            _buildInputField(
              '店铺介绍',
              _shopIntroController,
              '填写店铺介绍,不包含联系方式',
              maxLines: 3,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '请输入店铺介绍';
                }
                return null;
              },
            ),
          ],
        ),
      ),
    );
  }

  // 构建退货地址
  Widget _buildReturnAddress() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
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
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '退货地址 (仅退货时可见)',
              style: TextStyle(
                fontSize: 16.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 16.h),
            _buildInputField(
              '收货人姓名',
              _consigneeNameController,
              '请填写收货人姓名',
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '请输入收货人姓名';
                }
                return null;
              },
            ),
            SizedBox(height: 16.h),
            _buildInputField(
              '手机号码',
              _phoneController,
              '请填写收货人联系方式',
              keyboardType: TextInputType.phone,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '请输入手机号码';
                }
                if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(value.trim())) {
                  return '请输入正确的手机号码';
                }
                return null;
              },
            ),
            SizedBox(height: 16.h),
            _buildRegionField(),
            SizedBox(height: 16.h),
            _buildInputField(
              '详细地址',
              _addressController,
              '如街道、门牌号、小区、单元等',
              maxLines: 2,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '请输入详细地址';
                }
                return null;
              },
            ),
            SizedBox(height: 8.h),
            Text(
              '*因地址填写有误导致退货时造成的问题由卖家承担',
              style: TextStyle(
                fontSize: 10.sp,
                color: const Color(0xFF999999),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建实名信息
  Widget _buildRealNameInfo() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
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
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '实名信息 (用于余额,货款提现)',
              style: TextStyle(
                fontSize: 16.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 16.h),
            _buildInputField(
              '实名信息',
              _realNameController,
              '请填写真实姓名',
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '请输入真实姓名';
                }
                return null;
              },
            ),
            SizedBox(height: 16.h),
            _buildInputField(
              '身份证号',
              _idNumberController,
              '请填写身份证号码',
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '请输入身份证号码';
                }
                if (!RegExp(
                        r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]$')
                    .hasMatch(value.trim())) {
                  return '请输入正确的身份证号码';
                }
                return null;
              },
            ),
            SizedBox(height: 16.h),
            _buildDateField('证件开始日', _idStartDate, '选择证件开始日期'),
            SizedBox(height: 16.h),
            _buildDateField('证件结束日', _idEndDate, '选择证件到期日或长期'),
          ],
        ),
      ),
    );
  }

  // 构建身份证照片
  Widget _buildIdPhotos() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
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
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '身份证照片 (仅审核时使用)',
              style: TextStyle(
                fontSize: 16.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 8.h),
            Text(
              '请用手机横向拍摄以保持图片正常显示',
              style: TextStyle(
                fontSize: 12.sp,
                color: const Color(0xFF666666),
              ),
            ),
            SizedBox(height: 16.h),
            Row(
              children: [
                Expanded(
                  child: _buildPhotoUpload('人像面', Icons.person),
                ),
                SizedBox(width: 12.w),
                Expanded(
                  child: _buildPhotoUpload('国徽面', Icons.flag),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // 构建经营许可证
  Widget _buildBusinessLicense() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
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
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '经营许可证 (选填,仅审核时使用)',
              style: TextStyle(
                fontSize: 16.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 8.h),
            Text(
              '请用手机横向拍摄以保持图片正常显示',
              style: TextStyle(
                fontSize: 12.sp,
                color: const Color(0xFF666666),
              ),
            ),
            SizedBox(height: 16.h),
            _buildPhotoUpload('文物经营许可证', Icons.business),
          ],
        ),
      ),
    );
  }

  // 构建条款和操作按钮
  Widget _buildTermsAndActions() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Column(
        children: [
          // 确认信息
          Text(
            '请确认以上信息准确无误',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w500,
            ),
          ),
          SizedBox(height: 16.h),
          // 操作按钮
          Row(
            children: [
              Expanded(
                child: GestureDetector(
                  onTap: () {
                    Navigator.pop(context);
                  },
                  child: Container(
                    padding: EdgeInsets.symmetric(vertical: 14.h),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      border: Border.all(
                        color: const Color(0xFFE0E0E0),
                        width: 1,
                      ),
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    child: Text(
                      '上一步',
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: const Color(0xFF666666),
                        fontWeight: FontWeight.w500,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              ),
              SizedBox(width: 12.w),
              Expanded(
                child: GestureDetector(
                  onTap: _isSubmitting
                      ? null
                      : () {
                          _submitInfo();
                        },
                  child: Container(
                    padding: EdgeInsets.symmetric(vertical: 14.h),
                    decoration: BoxDecoration(
                      color:
                          _isSubmitting ? Colors.grey : const Color(0xFF9C4DFF),
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    child: _isSubmitting
                        ? Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              SizedBox(
                                width: 16.w,
                                height: 16.w,
                                child: const CircularProgressIndicator(
                                  color: Colors.white,
                                  strokeWidth: 2,
                                ),
                              ),
                              SizedBox(width: 8.w),
                              Text(
                                '提交中...',
                                style: TextStyle(
                                  fontSize: 14.sp,
                                  color: Colors.white,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          )
                        : Text(
                            '提交信息并开户验证',
                            style: TextStyle(
                              fontSize: 14.sp,
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
                            textAlign: TextAlign.center,
                          ),
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: 16.h),
          // 条款
          _buildTermsCheckbox(),
        ],
      ),
    );
  }

  // 构建条款复选框
  Widget _buildTermsCheckbox() {
    return GestureDetector(
      onTap: () {
        setState(() {
          _agreeTerms = !_agreeTerms;
        });
      },
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 16.w,
            height: 16.w,
            decoration: BoxDecoration(
              color: _agreeTerms ? const Color(0xFF9C4DFF) : Colors.transparent,
              border: Border.all(
                color: _agreeTerms
                    ? const Color(0xFF9C4DFF)
                    : const Color(0xFFE0E0E0),
                width: 1,
              ),
              borderRadius: BorderRadius.circular(2.r),
            ),
            child: _agreeTerms
                ? Icon(
                    Icons.check,
                    size: 12.w,
                    color: Colors.white,
                  )
                : null,
          ),
          SizedBox(width: 8.w),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '1. 点击即表示同意《隐私政策》《用户协议》《拍卖规则与服务协议》',
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: const Color(0xFF666666),
                    height: 1.4,
                  ),
                ),
                SizedBox(height: 4.h),
                Text(
                  '2.资料审核不通过可再次提交,店铺认证费用缴纳后,无论是 否审核通过,均不予退还',
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: const Color(0xFF666666),
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 构建输入字段
  Widget _buildInputField(
      String label, TextEditingController controller, String hintText,
      {TextInputType? keyboardType,
      int maxLines = 1,
      String? Function(String?)? validator}) {
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
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8.r),
              borderSide: const BorderSide(
                color: Colors.red,
                width: 1,
              ),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8.r),
              borderSide: const BorderSide(
                color: Colors.red,
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
          '所在地区',
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
                    _selectedRegion.isEmpty ? '选择位置省市区' : _selectedRegion,
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

  // 构建日期选择字段
  Widget _buildDateField(String label, String value, String hintText) {
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
        GestureDetector(
          onTap: () {
            _showDatePicker(label);
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
                    value.isEmpty ? hintText : value,
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: value.isEmpty
                          ? const Color(0xFF999999)
                          : const Color(0xFF333333),
                    ),
                  ),
                ),
                if (label == '证件结束日') ...[
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        _isLongTerm = !_isLongTerm;
                        if (_isLongTerm) {
                          _idEndDate = '长期';
                        }
                      });
                    },
                    child: Row(
                      children: [
                        Container(
                          width: 16.w,
                          height: 16.w,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: _isLongTerm
                                  ? const Color(0xFF9C4DFF)
                                  : const Color(0xFFE0E0E0),
                              width: 1,
                            ),
                            color: _isLongTerm
                                ? const Color(0xFF9C4DFF)
                                : Colors.transparent,
                          ),
                          child: _isLongTerm
                              ? Icon(
                                  Icons.check,
                                  size: 10.w,
                                  color: Colors.white,
                                )
                              : null,
                        ),
                        SizedBox(width: 4.w),
                        Text(
                          '长期',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: const Color(0xFF666666),
                          ),
                        ),
                        SizedBox(width: 8.w),
                      ],
                    ),
                  ),
                ],
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

  // 构建照片上传
  Widget _buildPhotoUpload(String label, IconData icon) {
    String? imageUrl;
    switch (label) {
      case '人像面':
        imageUrl = _idFrontImageUrl;
        break;
      case '国徽面':
        imageUrl = _idBackImageUrl;
        break;
      case '文物经营许可证':
        imageUrl = _businessLicenseImageUrl;
        break;
    }

    return GestureDetector(
      onTap: () {
        _uploadPhoto(label);
      },
      child: Container(
        height: 100.h,
        decoration: BoxDecoration(
          color: const Color(0xFFF5F5F5),
          border: Border.all(
            color: const Color(0xFFE0E0E0),
            width: 1,
            style: BorderStyle.solid,
          ),
          borderRadius: BorderRadius.circular(8.r),
        ),
        child: imageUrl != null && imageUrl.isNotEmpty
            ? Stack(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8.r),
                    child: Image.network(
                      'https://catdog.dachaonet.com$imageUrl',
                      width: double.infinity,
                      height: double.infinity,
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) {
                        return _buildUploadPlaceholder(label, icon);
                      },
                    ),
                  ),
                  Positioned(
                    top: 4.h,
                    right: 4.w,
                    child: GestureDetector(
                      onTap: () {
                        setState(() {
                          switch (label) {
                            case '人像面':
                              _idFrontImageUrl = null;
                              break;
                            case '国徽面':
                              _idBackImageUrl = null;
                              break;
                            case '文物经营许可证':
                              _businessLicenseImageUrl = null;
                              break;
                          }
                        });
                      },
                      child: Container(
                        width: 20.w,
                        height: 20.w,
                        decoration: const BoxDecoration(
                          color: Colors.red,
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          Icons.close,
                          size: 12.w,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ],
              )
            : _buildUploadPlaceholder(label, icon),
      ),
    );
  }

  Widget _buildUploadPlaceholder(String label, IconData icon) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          icon,
          size: 24.w,
          color: const Color(0xFF999999),
        ),
        SizedBox(height: 8.h),
        Container(
          padding: EdgeInsets.symmetric(horizontal: 8.w, vertical: 4.h),
          decoration: BoxDecoration(
            color: const Color(0xFF9C4DFF),
            borderRadius: BorderRadius.circular(4.r),
          ),
          child: Text(
            '+上传$label',
            style: TextStyle(
              fontSize: 10.sp,
              color: Colors.white,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
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
            Text(
              '选择地区',
              style: TextStyle(
                fontSize: 18.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 20.h),
            Expanded(
              child: ListView(
                children: [
                  _buildRegionItem('山东省济南市历下区'),
                  _buildRegionItem('山东省济南市市中区'),
                  _buildRegionItem('山东省济南市槐荫区'),
                  _buildRegionItem('山东省济南市天桥区'),
                  _buildRegionItem('山东省济南市历城区'),
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

  // 显示日期选择器
  void _showDatePicker(String label) {
    showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime(2100),
    ).then((date) {
      if (date != null) {
        setState(() {
          if (label == '证件开始日') {
            _idStartDate =
                '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
          } else if (label == '证件结束日') {
            _idEndDate =
                '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
          }
        });
      }
    });
  }

  // 上传照片
  void _uploadPhoto(String label) {
    showModalBottomSheet(
      context: context,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(20.r),
          topRight: Radius.circular(20.r),
        ),
      ),
      builder: (context) => Container(
        padding: EdgeInsets.all(20.w),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '选择上传方式',
              style: TextStyle(
                fontSize: 18.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 20.h),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                GestureDetector(
                  onTap: () async {
                    Navigator.pop(context);
                    await _pickAndUploadImage(label, ImageSource.camera);
                  },
                  child: Column(
                    children: [
                      Container(
                        width: 60.w,
                        height: 60.w,
                        decoration: BoxDecoration(
                          color: const Color(0xFF9C4DFF),
                          borderRadius: BorderRadius.circular(12.r),
                        ),
                        child: Icon(
                          Icons.camera_alt,
                          size: 30.w,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 8.h),
                      Text(
                        '拍照',
                        style: TextStyle(
                          fontSize: 14.sp,
                          color: const Color(0xFF333333),
                        ),
                      ),
                    ],
                  ),
                ),
                GestureDetector(
                  onTap: () async {
                    Navigator.pop(context);
                    await _pickAndUploadImage(label, ImageSource.gallery);
                  },
                  child: Column(
                    children: [
                      Container(
                        width: 60.w,
                        height: 60.w,
                        decoration: BoxDecoration(
                          color: const Color(0xFF9C4DFF),
                          borderRadius: BorderRadius.circular(12.r),
                        ),
                        child: Icon(
                          Icons.photo_library,
                          size: 30.w,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 8.h),
                      Text(
                        '相册',
                        style: TextStyle(
                          fontSize: 14.sp,
                          color: const Color(0xFF333333),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            SizedBox(height: 20.h),
          ],
        ),
      ),
    );
  }

  // 选择并上传图片
  Future<void> _pickAndUploadImage(String label, ImageSource source) async {
    try {
      XFile? image;
      if (source == ImageSource.camera) {
        image = await StoreApplicationService.pickImageFromCamera();
      } else {
        image = await StoreApplicationService.pickImageFromGallery();
      }

      if (image != null) {
        // 显示上传进度
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => const Center(
            child: CircularProgressIndicator(),
          ),
        );

        try {
          // 先测试认证状态
          await StoreApplicationService.testAuth();

          final result = await StoreApplicationService.uploadImage(image);
          Navigator.pop(context); // 关闭进度对话框

          setState(() {
            switch (label) {
              case '人像面':
                _idFrontImageUrl = result['url'];
                break;
              case '国徽面':
                _idBackImageUrl = result['url'];
                break;
              case '文物经营许可证':
                _businessLicenseImageUrl = result['url'];
                break;
            }
          });

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('$label上传成功')),
          );
        } catch (e) {
          Navigator.pop(context); // 关闭进度对话框
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('上传失败: $e')),
          );
        }
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('选择图片失败: $e')),
      );
    }
  }

  // 提交信息
  void _submitInfo() async {
    if (!_agreeTerms) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请先同意相关条款')),
      );
      return;
    }

    if (!_formKey.currentState!.validate()) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请完善表单信息')),
      );
      return;
    }

    if (_selectedRegion.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请选择所在地区')),
      );
      return;
    }

    if (_idStartDate.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请选择证件开始日期')),
      );
      return;
    }

    if (_idEndDate.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请选择证件结束日期')),
      );
      return;
    }

    if (_idFrontImageUrl == null || _idFrontImageUrl!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请上传身份证人像面照片')),
      );
      return;
    }

    if (_idBackImageUrl == null || _idBackImageUrl!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请上传身份证国徽面照片')),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      // 构建申请数据
      final applicationData = {
        'store_name': _shopNameController.text.trim(),
        'store_description': _shopIntroController.text.trim(),
        'store_type': widget.storeType,
        'consignee_name': _consigneeNameController.text.trim(),
        'consignee_phone': _phoneController.text.trim(),
        'return_region': _selectedRegion,
        'return_address': _addressController.text.trim(),
        'real_name': _realNameController.text.trim(),
        'id_number': _idNumberController.text.trim(),
        'id_start_date': _idStartDate,
        'id_end_date': _idEndDate,
        'id_front_image': _idFrontImageUrl,
        'id_back_image': _idBackImageUrl,
        'business_license_image': _businessLicenseImageUrl,
      };

      // 提交申请
      await StoreApplicationService.createApplication(applicationData);

      setState(() {
        _isSubmitting = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('店铺申请提交成功，请等待审核')),
      );

      // 返回上一页
      Navigator.of(context).pop();
      Navigator.of(context).pop(); // 返回到个人中心页面
    } catch (e) {
      setState(() {
        _isSubmitting = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('提交失败: $e')),
      );
    }
  }
}
