import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';
import 'local_pet_store_detail_page.dart';

class LocalPetStoresPage extends StatefulWidget {
  const LocalPetStoresPage({super.key});

  @override
  State<LocalPetStoresPage> createState() => _LocalPetStoresPageState();
}

class _LocalPetStoresPageState extends State<LocalPetStoresPage> {
  final ScrollController _scrollController = ScrollController();

  // 模拟本地宠店数据
  final List<Map<String, dynamic>> _stores = [
    {
      'id': '1',
      'name': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=201',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'products': [
        {
          'image': 'https://picsum.photos/200/200?random=301',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=302',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=303',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=304',
          'price': 432,
        },
      ],
    },
    {
      'id': '2',
      'name': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=202',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'products': [
        {
          'image': 'https://picsum.photos/200/200?random=311',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=312',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=313',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=314',
          'price': 432,
        },
      ],
    },
    {
      'id': '3',
      'name': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=203',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'products': [
        {
          'image': 'https://picsum.photos/200/200?random=321',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=322',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=323',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=324',
          'price': 432,
        },
      ],
    },
    {
      'id': '4',
      'name': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=204',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'products': [
        {
          'image': 'https://picsum.photos/200/200?random=331',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=332',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=333',
          'price': 432,
        },
        {
          'image': 'https://picsum.photos/200/200?random=334',
          'price': 432,
        },
      ],
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
          '本地宠店',
          style: TextStyle(
            color: Colors.black87,
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: ListView.builder(
        controller: _scrollController,
        padding: EdgeInsets.all(16.w),
        itemCount: _stores.length,
        itemBuilder: (context, index) {
          final store = _stores[index];
          return _buildStoreCard(store);
        },
      ),
    );
  }

  Widget _buildStoreCard(Map<String, dynamic> store) {
    final products = store['products'] as List<Map<String, dynamic>>;

    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => LocalPetStoreDetailPage(store: store),
          ),
        );
      },
      child: Container(
        margin: EdgeInsets.only(bottom: 16.h),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.08),
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
              // 店铺头部信息
              Row(
                children: [
                  CircleAvatar(
                    radius: 24.r,
                    backgroundImage: NetworkImage(store['avatar']),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          store['name'],
                          style: TextStyle(
                            fontSize: 16.sp,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                          ),
                        ),
                        SizedBox(height: 4.h),
                        Row(
                          children: [
                            // 星级评分
                            ...List.generate(5, (index) {
                              return Icon(
                                index < store['rating'].floor()
                                    ? Icons.star
                                    : Icons.star_border,
                                color: const Color(0xFFFFB74D),
                                size: 14.sp,
                              );
                            }),
                            SizedBox(width: 8.w),
                            Text(
                              store['followers'],
                              style: TextStyle(
                                fontSize: 12.sp,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 6.h),
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(15.r),
                    ),
                    child: Text(
                      '进店',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12.sp,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
              
              SizedBox(height: 16.h),
              
              // 商品网格
              GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 4,
                  crossAxisSpacing: 8.w,
                  mainAxisSpacing: 8.h,
                  childAspectRatio: 0.85,
                ),
                itemCount: products.length,
                itemBuilder: (context, index) {
                  final product = products[index];
                  return _buildProductItem(product);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProductItem(Map<String, dynamic> product) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8.r),
        image: DecorationImage(
          image: NetworkImage(product['image']),
          fit: BoxFit.cover,
        ),
      ),
      child: Stack(
        children: [
          // 价格标签
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 4.w, vertical: 2.h),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.black.withValues(alpha: 0.7),
                  ],
                ),
                borderRadius: BorderRadius.vertical(bottom: Radius.circular(8.r)),
              ),
              child: Text(
                '¥${product['price']}',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 10.sp,
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ],
      ),
    );
  }
}