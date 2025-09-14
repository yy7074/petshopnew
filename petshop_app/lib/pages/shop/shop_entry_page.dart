import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'shop_info_page.dart';

class ShopEntryPage extends StatefulWidget {
  const ShopEntryPage({super.key});

  @override
  State<ShopEntryPage> createState() => _ShopEntryPageState();
}

class _ShopEntryPageState extends State<ShopEntryPage> {
  String _selectedShopType = '个人店';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          child: Column(
            children: [
              SizedBox(height: 16.h),
              _buildHeader(),
              SizedBox(height: 24.h),
              _buildUserProfile(),
              SizedBox(height: 24.h),
              _buildInstructions(),
              SizedBox(height: 24.h),
              _buildGuide(),
              SizedBox(height: 24.h),
              _buildShopTypeSelection(),
              SizedBox(height: 40.h),
              _buildConfirmButton(),
              SizedBox(height: 100.h),
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

  // 构建用户资料
  Widget _buildUserProfile() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Column(
        children: [
          // 头像
          Container(
            width: 80.w,
            height: 80.w,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xFFF0F0F0),
            ),
            child: ClipOval(
              child: Image.asset(
                'assets/images/avatar_placeholder.png',
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => Container(
                  color: const Color(0xFFF0F0F0),
                  child: const Icon(
                    Icons.person,
                    color: Color(0xFF999999),
                    size: 40,
                  ),
                ),
              ),
            ),
          ),
          SizedBox(height: 12.h),
          // 用户名
          Text(
            'Li',
            style: TextStyle(
              fontSize: 16.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  // 构建入驻须知
  Widget _buildInstructions() {
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
            '入驻须知',
            style: TextStyle(
              fontSize: 16.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w600,
            ),
          ),
          SizedBox(height: 12.h),
          Text(
            '入驻的商家分四个等级',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF666666),
            ),
          ),
          SizedBox(height: 8.h),
          _buildInstructionItem('旗舰店 10000元押金'),
          _buildInstructionItem('企业店 5000元押金'),
          _buildInstructionItem('个体商家 1000元押金'),
          _buildInstructionItem('个人店 600元押金'),
          SizedBox(height: 8.h),
          Text(
            '每年店铺运营费用 (188元/年)',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF666666),
            ),
          ),
        ],
      ),
    );
  }

  // 构建须知项目
  Widget _buildInstructionItem(String text) {
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
              fontSize: 14.sp,
              color: const Color(0xFF666666),
            ),
          ),
        ],
      ),
    );
  }

  // 构建入驻指南
  Widget _buildGuide() {
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
      child: Column(
        children: [
          Padding(
            padding: EdgeInsets.all(16.w),
            child: Row(
              children: [
                Text(
                  '入驻指南',
                  style: TextStyle(
                    fontSize: 16.sp,
                    color: const Color(0xFF333333),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          _buildGuideItem('我都可以发布哪些拍品?'),
          _buildGuideItem('在本平台开店做生意都会有哪些费用?'),
          _buildGuideItem('我可以开多少个店铺?'),
        ],
      ),
    );
  }

  // 构建指南项目
  Widget _buildGuideItem(String text) {
    return GestureDetector(
      onTap: () {
        // 处理指南点击
      },
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
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
            Expanded(
              child: Text(
                text,
                style: TextStyle(
                  fontSize: 14.sp,
                  color: const Color(0xFF333333),
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
    );
  }

  // 构建店铺类型选择
  Widget _buildShopTypeSelection() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '选择您的开店身份',
            style: TextStyle(
              fontSize: 16.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w600,
            ),
          ),
          SizedBox(height: 16.h),
          _buildShopTypeCard(
            '个人店',
            '根据《电子商务法》相关规定,个人小额交易,可凭身份证开店。年交易额在10万以下,后续可升级为个体工商户或企业。',
            Icons.person,
            '个人店',
          ),
          SizedBox(height: 12.h),
          _buildShopTypeCard(
            '个体商家',
            '提供个体工商户营业执照,身份证。',
            Icons.store,
            '个体商家',
          ),
          SizedBox(height: 12.h),
          _buildShopTypeCard(
            '企业店',
            '须提供企业营业执照,法人身份证。',
            Icons.business,
            '企业店',
          ),
          SizedBox(height: 12.h),
          _buildShopTypeCard(
            '旗舰店',
            '提供个体工商户营业执照,身份证。',
            Icons.flag,
            '旗舰店',
          ),
        ],
      ),
    );
  }

  // 构建店铺类型卡片
  Widget _buildShopTypeCard(
      String title, String description, IconData icon, String value) {
    bool isSelected = _selectedShopType == value;

    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedShopType = value;
        });
      },
      child: Container(
        padding: EdgeInsets.all(16.w),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12.r),
          border: Border.all(
            color:
                isSelected ? const Color(0xFF9C4DFF) : const Color(0xFFE0E0E0),
            width: isSelected ? 2 : 1,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            // 图标
            Container(
              width: 40.w,
              height: 40.w,
              decoration: BoxDecoration(
                color: isSelected
                    ? const Color(0xFF9C4DFF).withOpacity(0.1)
                    : const Color(0xFFF5F5F5),
                borderRadius: BorderRadius.circular(8.r),
              ),
              child: Icon(
                icon,
                size: 20.w,
                color: isSelected
                    ? const Color(0xFF9C4DFF)
                    : const Color(0xFF999999),
              ),
            ),
            SizedBox(width: 12.w),
            // 内容
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 16.sp,
                      color: const Color(0xFF333333),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  SizedBox(height: 4.h),
                  Text(
                    description,
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: const Color(0xFF666666),
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
            // 选择按钮
            Container(
              width: 20.w,
              height: 20.w,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: isSelected
                      ? const Color(0xFF9C4DFF)
                      : const Color(0xFFE0E0E0),
                  width: 2,
                ),
                color:
                    isSelected ? const Color(0xFF9C4DFF) : Colors.transparent,
              ),
              child: isSelected
                  ? Icon(
                      Icons.check,
                      size: 12.w,
                      color: Colors.white,
                    )
                  : null,
            ),
          ],
        ),
      ),
    );
  }

  // 构建确认按钮
  Widget _buildConfirmButton() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: GestureDetector(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ShopInfoPage(storeType: _selectedShopType),
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
            '确定并填写店铺信息',
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
}
