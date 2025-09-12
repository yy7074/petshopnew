import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:image_picker/image_picker.dart';
import '../../constants/app_colors.dart';

class PetSocialPublishPage extends StatefulWidget {
  const PetSocialPublishPage({super.key});

  @override
  State<PetSocialPublishPage> createState() => _PetSocialPublishPageState();
}

class _PetSocialPublishPageState extends State<PetSocialPublishPage> {
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _contentController = TextEditingController();
  final ImagePicker _picker = ImagePicker();
  
  List<String> _selectedImages = [];
  String _selectedLocation = '';
  
  // 模拟已选择的图片（用占位图片）
  final List<String> _demoImages = [
    'https://picsum.photos/300/300?random=501',
    'https://picsum.photos/300/300?random=502',
  ];

  @override
  void initState() {
    super.initState();
    // 使用演示图片
    _selectedImages.addAll(_demoImages);
  }

  @override
  void dispose() {
    _titleController.dispose();
    _contentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.black87),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          '发布',
          style: TextStyle(
            color: Colors.black87,
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 图片选择区域
            _buildImageSelector(),
            
            SizedBox(height: 24.h),
            
            // 标题输入
            _buildTitleInput(),
            
            SizedBox(height: 24.h),
            
            // 正文输入
            _buildContentInput(),
            
            SizedBox(height: 200.h), // 占位空间，确保内容不被底部按钮遮挡
          ],
        ),
      ),
      bottomSheet: _buildBottomSheet(),
    );
  }

  Widget _buildImageSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 图片网格
        Container(
          height: 240.h,
          child: GridView.builder(
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 3,
              crossAxisSpacing: 8.w,
              mainAxisSpacing: 8.h,
              childAspectRatio: 1.0,
            ),
            itemCount: _selectedImages.length + 1, // +1 for add button
            itemBuilder: (context, index) {
              if (index < _selectedImages.length) {
                return _buildImageItem(_selectedImages[index], index);
              } else {
                return _buildAddImageButton();
              }
            },
          ),
        ),
      ],
    );
  }

  Widget _buildImageItem(String imagePath, int index) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12.r),
        image: DecorationImage(
          image: NetworkImage(imagePath), // 使用网络图片作为演示
          fit: BoxFit.cover,
        ),
      ),
      child: Stack(
        children: [
          // 删除按钮
          Positioned(
            top: 4.h,
            right: 4.w,
            child: GestureDetector(
              onTap: () {
                setState(() {
                  _selectedImages.removeAt(index);
                });
              },
              child: Container(
                width: 24.w,
                height: 24.w,
                decoration: const BoxDecoration(
                  color: Colors.black54,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.close,
                  color: Colors.white,
                  size: 16.sp,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAddImageButton() {
    return GestureDetector(
      onTap: _addImage,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(12.r),
          border: Border.all(color: Colors.grey[300]!, width: 1),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.add,
              size: 32.sp,
              color: Colors.grey[500],
            ),
            SizedBox(height: 4.h),
            Text(
              '添加图片',
              style: TextStyle(
                fontSize: 12.sp,
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTitleInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: _titleController,
          decoration: InputDecoration(
            hintText: '添加标题',
            hintStyle: TextStyle(
              color: Colors.grey[500],
              fontSize: 16.sp,
            ),
            border: InputBorder.none,
            contentPadding: EdgeInsets.zero,
          ),
          style: TextStyle(
            fontSize: 16.sp,
            color: Colors.black87,
            fontWeight: FontWeight.w500,
          ),
          maxLines: 2,
        ),
        Container(
          height: 1,
          color: Colors.grey[200],
          margin: EdgeInsets.only(top: 8.h),
        ),
      ],
    );
  }

  Widget _buildContentInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: _contentController,
          decoration: InputDecoration(
            hintText: '添加正文',
            hintStyle: TextStyle(
              color: Colors.grey[500],
              fontSize: 16.sp,
            ),
            border: InputBorder.none,
            contentPadding: EdgeInsets.zero,
          ),
          style: TextStyle(
            fontSize: 16.sp,
            color: Colors.black87,
          ),
          maxLines: 10,
          minLines: 5,
        ),
      ],
    );
  }

  Widget _buildBottomSheet() {
    return Container(
      color: Colors.white,
      padding: EdgeInsets.only(
        left: 16.w,
        right: 16.w,
        top: 16.h,
        bottom: MediaQuery.of(context).padding.bottom + 16.h,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 添加地点选项
          GestureDetector(
            onTap: _selectLocation,
            child: Container(
              padding: EdgeInsets.symmetric(vertical: 16.h),
              child: Row(
                children: [
                  Icon(
                    Icons.location_on_outlined,
                    size: 24.sp,
                    color: Colors.grey[600],
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: Text(
                      _selectedLocation.isEmpty ? '添加地点' : _selectedLocation,
                      style: TextStyle(
                        fontSize: 16.sp,
                        color: _selectedLocation.isEmpty ? Colors.grey[600] : Colors.black87,
                      ),
                    ),
                  ),
                  Icon(
                    Icons.arrow_forward_ios,
                    size: 16.sp,
                    color: Colors.grey[400],
                  ),
                ],
              ),
            ),
          ),
          
          Container(
            height: 1,
            color: Colors.grey[200],
          ),
          
          SizedBox(height: 16.h),
          
          // 发布按钮
          GestureDetector(
            onTap: _publishPost,
            child: Container(
              width: double.infinity,
              height: 50.h,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AppColors.primary,
                    AppColors.primary.withValues(alpha: 0.8),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(25.r),
              ),
              child: Center(
                child: Text(
                  '发布帖子',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _addImage() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        setState(() {
          // 在实际应用中，这里应该是 image.path
          // 为了演示，我们添加一个随机图片
          _selectedImages.add('https://picsum.photos/300/300?random=${DateTime.now().millisecondsSinceEpoch}');
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('选择图片失败: $e')),
      );
    }
  }

  void _selectLocation() {
    // TODO: 实现地点选择功能
    showModalBottomSheet(
      context: context,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20.r)),
      ),
      builder: (context) => Container(
        height: 300.h,
        padding: EdgeInsets.all(20.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '选择地点',
              style: TextStyle(
                fontSize: 18.sp,
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 20.h),
            ListTile(
              leading: const Icon(Icons.location_on),
              title: const Text('当前位置'),
              subtitle: const Text('济南万象城'),
              onTap: () {
                setState(() {
                  _selectedLocation = '济南万象城';
                });
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.search),
              title: const Text('搜索地点'),
              onTap: () {
                Navigator.pop(context);
                // TODO: 实现地点搜索
              },
            ),
          ],
        ),
      ),
    );
  }

  void _publishPost() {
    if (_titleController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请添加标题')),
      );
      return;
    }
    
    if (_contentController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请添加正文内容')),
      );
      return;
    }
    
    if (_selectedImages.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请添加至少一张图片')),
      );
      return;
    }
    
    // TODO: 实现发布逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('发布成功！')),
    );
    
    // 返回到宠物交流页面
    Navigator.pop(context);
  }
}