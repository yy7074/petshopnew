import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';
import '../product/product_detail_page.dart';

class LocalPetStoreDetailPage extends StatefulWidget {
  final Map<String, dynamic> store;

  const LocalPetStoreDetailPage({super.key, required this.store});

  @override
  State<LocalPetStoreDetailPage> createState() => _LocalPetStoreDetailPageState();
}

class _LocalPetStoreDetailPageState extends State<LocalPetStoreDetailPage> {
  final ScrollController _scrollController = ScrollController();

  // 扩展商品数据用于详情页展示
  final List<Map<String, dynamic>> _detailProducts = [
    {
      'id': 401,
      'seller_id': 1,
      'image': 'https://picsum.photos/400/400?random=401',
      'images': ['https://picsum.photos/400/400?random=401'],
      'title': '宠物标题宠物标题宠物',
      'price': 923.9,
      'description': '宠物标题宠物标题宠物',
      'location': '本地宠物店',
      'seller_name': '本地宠物店',
    },
    {
      'id': 402,
      'seller_id': 1,
      'image': 'https://picsum.photos/400/400?random=402',
      'images': ['https://picsum.photos/400/400?random=402'],
      'title': '宠物标题宠物标题宠物',
      'price': 923.9,
      'description': '宠物标题宠物标题宠物',
      'location': '本地宠物店',
      'seller_name': '本地宠物店',
    },
    {
      'id': 403,
      'seller_id': 1,
      'image': 'https://picsum.photos/400/400?random=403',
      'images': ['https://picsum.photos/400/400?random=403'],
      'title': '宠物标题宠物标题宠物',
      'price': 923.9,
      'description': '宠物标题宠物标题宠物',
      'location': '本地宠物店',
      'seller_name': '本地宠物店',
    },
    {
      'id': 404,
      'seller_id': 1,
      'image': 'https://picsum.photos/400/400?random=404',
      'images': ['https://picsum.photos/400/400?random=404'],
      'title': '宠物标题宠物标题宠物',
      'price': 923.9,
      'description': '宠物标题宠物标题宠物',
      'location': '本地宠物店',
      'seller_name': '本地宠物店',
    },
  ];

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.black87),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          '店铺详情',
          style: TextStyle(
            color: Colors.black87,
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: SingleChildScrollView(
        controller: _scrollController,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 店铺信息头部
            Container(
              color: Colors.white,
              padding: EdgeInsets.all(16.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 30.r,
                        backgroundImage: NetworkImage(widget.store['avatar']),
                      ),
                      SizedBox(width: 16.w),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              widget.store['name'],
                              style: TextStyle(
                                fontSize: 18.sp,
                                fontWeight: FontWeight.w600,
                                color: Colors.black87,
                              ),
                            ),
                            SizedBox(height: 8.h),
                            Row(
                              children: [
                                // 星级评分
                                ...List.generate(5, (index) {
                                  return Icon(
                                    index < widget.store['rating'].floor()
                                        ? Icons.star
                                        : Icons.star_border,
                                    color: const Color(0xFFFFB74D),
                                    size: 16.sp,
                                  );
                                }),
                                SizedBox(width: 8.w),
                                Text(
                                  widget.store['followers'],
                                  style: TextStyle(
                                    fontSize: 14.sp,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 20.w, vertical: 8.h),
                        decoration: BoxDecoration(
                          color: AppColors.primary,
                          borderRadius: BorderRadius.circular(20.r),
                        ),
                        child: Text(
                          '关注',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 14.sp,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                  
                  SizedBox(height: 16.h),
                  
                  // 店铺地址信息
                  Container(
                    padding: EdgeInsets.all(12.w),
                    decoration: BoxDecoration(
                      color: Colors.grey[50],
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.location_on,
                          size: 16.sp,
                          color: Colors.grey[600],
                        ),
                        SizedBox(width: 8.w),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '历下区经十路与舜文路路口南方向内心b座116室',
                                style: TextStyle(
                                  fontSize: 14.sp,
                                  color: Colors.black87,
                                ),
                              ),
                              SizedBox(height: 4.h),
                              Text(
                                '距您1.2千米',
                                style: TextStyle(
                                  fontSize: 12.sp,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                        Icon(
                          Icons.arrow_forward_ios,
                          size: 14.sp,
                          color: Colors.grey[600],
                        ),
                      ],
                    ),
                  ),
                  
                  SizedBox(height: 16.h),
                  
                  // 店铺简介
                  Text(
                    '店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介店铺简介..',
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: Colors.grey[700],
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
            
            SizedBox(height: 8.h),
            
            // 商品网格
            Container(
              color: Colors.white,
              padding: EdgeInsets.all(16.w),
              child: GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  crossAxisSpacing: 12.w,
                  mainAxisSpacing: 12.h,
                  childAspectRatio: 0.8,
                ),
                itemCount: _detailProducts.length,
                itemBuilder: (context, index) {
                  final product = _detailProducts[index];
                  return _buildDetailProductItem(product);
                },
              ),
            ),
            
            SizedBox(height: 100.h),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailProductItem(Map<String, dynamic> product) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ProductDetailPage(productData: product),
          ),
        );
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 商品图片
            Expanded(
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.vertical(top: Radius.circular(8.r)),
                  image: DecorationImage(
                    image: NetworkImage(product['image']),
                    fit: BoxFit.cover,
                  ),
                ),
              ),
            ),
            
            // 商品信息
            Padding(
              padding: EdgeInsets.all(12.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product['title'],
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: Colors.black87,
                      height: 1.3,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  SizedBox(height: 8.h),
                  Text(
                    '¥${product['price']}',
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w600,
                      color: AppColors.primary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}