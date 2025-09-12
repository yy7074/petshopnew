import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'publish_type_page.dart';

class PublishPage extends StatefulWidget {
  const PublishPage({super.key});

  @override
  State<PublishPage> createState() => _PublishPageState();
}

class _PublishPageState extends State<PublishPage> {
  final TextEditingController _titleController = TextEditingController();
  String _price = '¥0.00';
  String _shippingMethod = '包邮';

  @override
  void dispose() {
    _titleController.dispose();
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
            SizedBox(height: 20.h),
            _buildImageUpload(),
            SizedBox(height: 20.h),
            _buildProductTitle(),
            SizedBox(height: 20.h),
            _buildPriceSection(),
            SizedBox(height: 20.h),
            _buildShippingSection(),
            const Spacer(),
            _buildPublishButton(),
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
              '发布',
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

  // 构建图片上传
  Widget _buildImageUpload() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '产品图片',
            style: TextStyle(
              fontSize: 16.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w600,
            ),
          ),
          SizedBox(height: 12.h),
          Row(
            children: [
              // 第一张图片
              _buildImageItem('https://picsum.photos/200/200?random=1'),
              SizedBox(width: 12.w),
              // 第二张图片
              _buildImageItem('https://picsum.photos/200/200?random=2'),
              SizedBox(width: 12.w),
              // 添加图片按钮
              _buildAddImageButton(),
            ],
          ),
        ],
      ),
    );
  }

  // 构建图片项目
  Widget _buildImageItem(String imageUrl) {
    return Container(
      width: 80.w,
      height: 80.w,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8.r),
        color: const Color(0xFFF5F5F5),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(8.r),
        child: CachedNetworkImage(
          imageUrl: imageUrl,
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
    );
  }

  // 构建添加图片按钮
  Widget _buildAddImageButton() {
    return GestureDetector(
      onTap: () {
        _showPublishTypeDialog();
      },
      child: Container(
        width: 80.w,
        height: 80.w,
        decoration: BoxDecoration(
          color: const Color(0xFFF5F5F5),
          borderRadius: BorderRadius.circular(8.r),
          border: Border.all(
            color: const Color(0xFFE0E0E0),
            width: 1,
            style: BorderStyle.solid,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.add,
              size: 24.w,
              color: const Color(0xFF999999),
            ),
            SizedBox(height: 4.h),
            Text(
              '添加',
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

  // 构建产品标题
  Widget _buildProductTitle() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '产品标题',
            style: TextStyle(
              fontSize: 16.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w600,
            ),
          ),
          SizedBox(height: 12.h),
          TextField(
            controller: _titleController,
            decoration: InputDecoration(
              hintText: '描述一下产品...',
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
              contentPadding: EdgeInsets.symmetric(
                horizontal: 12.w,
                vertical: 12.h,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 构建价格区域
  Widget _buildPriceSection() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          Text(
            '价格',
            style: TextStyle(
              fontSize: 16.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          GestureDetector(
            onTap: () {
              _showPriceDialog();
            },
            child: Row(
              children: [
                Text(
                  _price,
                  style: TextStyle(
                    fontSize: 16.sp,
                    color: const Color(0xFF333333),
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(width: 4.w),
                Icon(
                  Icons.arrow_forward_ios,
                  size: 14.w,
                  color: const Color(0xFF999999),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 构建发货方式区域
  Widget _buildShippingSection() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          Text(
            '发货方式',
            style: TextStyle(
              fontSize: 16.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          GestureDetector(
            onTap: () {
              _showShippingDialog();
            },
            child: Row(
              children: [
                Text(
                  _shippingMethod,
                  style: TextStyle(
                    fontSize: 16.sp,
                    color: const Color(0xFF333333),
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(width: 4.w),
                Icon(
                  Icons.arrow_forward_ios,
                  size: 14.w,
                  color: const Color(0xFF999999),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 构建发布按钮
  Widget _buildPublishButton() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: GestureDetector(
        onTap: () {
          _publishProduct();
        },
        child: Container(
          width: double.infinity,
          padding: EdgeInsets.symmetric(vertical: 16.h),
          decoration: BoxDecoration(
            color: const Color(0xFF2196F3),
            borderRadius: BorderRadius.circular(12.r),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF2196F3).withOpacity(0.3),
                blurRadius: 8,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Text(
            '发布',
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

  // 显示发布类型对话框
  void _showPublishTypeDialog() {
    showModalBottomSheet(
      context: context,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(20.r),
          topRight: Radius.circular(20.r),
        ),
      ),
      builder: (context) => const PublishTypePage(),
    );
  }

  // 显示价格对话框
  void _showPriceDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16.r),
        ),
        title: Text(
          '设置价格',
          style: TextStyle(
            fontSize: 16.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w600,
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                hintText: '请输入价格',
                prefixText: '¥',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.r),
                ),
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
                _price = '¥199.99';
              });
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

  // 显示发货方式对话框
  void _showShippingDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16.r),
        ),
        title: Text(
          '选择发货方式',
          style: TextStyle(
            fontSize: 16.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w600,
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildShippingOption('包邮', '包邮'),
            _buildShippingOption('到付', '到付'),
            _buildShippingOption('自提', '自提'),
          ],
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
        ],
      ),
    );
  }

  // 构建发货方式选项
  Widget _buildShippingOption(String title, String value) {
    return GestureDetector(
      onTap: () {
        setState(() {
          _shippingMethod = value;
        });
        Navigator.pop(context);
      },
      child: Container(
        width: double.infinity,
        padding: EdgeInsets.symmetric(vertical: 12.h),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: const Color(0xFFF0F0F0),
              width: 1,
            ),
          ),
        ),
        child: Text(
          title,
          style: TextStyle(
            fontSize: 14.sp,
            color: const Color(0xFF333333),
          ),
        ),
      ),
    );
  }

  // 发布产品
  void _publishProduct() {
    if (_titleController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入产品标题')),
      );
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('产品发布成功')),
    );
    Navigator.pop(context);
  }
}
