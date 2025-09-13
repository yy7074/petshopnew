import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../search/search_page.dart';
import '../product/product_detail_page.dart';

class SpecialEventPage extends StatefulWidget {
  final String? title;
  final String? eventId;

  const SpecialEventPage({
    super.key,
    this.title,
    this.eventId,
  });

  @override
  State<SpecialEventPage> createState() => _SpecialEventPageState();
}

class _SpecialEventPageState extends State<SpecialEventPage> {
  // 排序状态管理
  String _selectedSort = '默认排序';
  bool _priceAscending = true;
  bool _timeAscending = true;

  // 标签筛选状态
  String _selectedTag = '全部(500)';

  // 商品数据
  List<Map<String, dynamic>> _products = [
    {
      'id': '1869863017137013',
      'name': '精品金毛幼犬 纯种血统',
      'price': 924.9,
      'image': 'https://picsum.photos/200/200?random=80',
      'bids': 39,
      'views': 394,
      'timeLeft': '00时34分23秒',
      'isFavorite': false,
      'endTime': DateTime.now()
          .add(const Duration(hours: 2, minutes: 34, seconds: 23)),
    },
    {
      'id': '1869863017137014',
      'name': '英短蓝猫 健康活泼',
      'price': 1200.5,
      'image': 'https://picsum.photos/200/200?random=81',
      'bids': 25,
      'views': 156,
      'timeLeft': '01时15分45秒',
      'isFavorite': true,
      'endTime': DateTime.now()
          .add(const Duration(hours: 3, minutes: 15, seconds: 45)),
    },
    {
      'id': '1869863017137015',
      'name': '布偶猫 温顺可爱',
      'price': 650.0,
      'image': 'https://picsum.photos/200/200?random=82',
      'bids': 67,
      'views': 289,
      'timeLeft': '02时08分12秒',
      'isFavorite': false,
      'endTime':
          DateTime.now().add(const Duration(hours: 4, minutes: 8, seconds: 12)),
    },
    {
      'id': '1869863017137016',
      'name': '萨摩耶 雪白毛色',
      'price': 1800.0,
      'image': 'https://picsum.photos/200/200?random=83',
      'bids': 12,
      'views': 78,
      'timeLeft': '03时22分56秒',
      'isFavorite': true,
      'endTime': DateTime.now()
          .add(const Duration(hours: 5, minutes: 22, seconds: 56)),
    },
    {
      'id': '1869863017137017',
      'name': '柯基犬 短腿萌宠',
      'price': 450.0,
      'image': 'https://picsum.photos/200/200?random=84',
      'bids': 89,
      'views': 445,
      'timeLeft': '00时45分30秒',
      'isFavorite': false,
      'endTime': DateTime.now()
          .add(const Duration(hours: 1, minutes: 45, seconds: 30)),
    },
    {
      'id': '1869863017137018',
      'name': '比熊犬 卷毛可爱',
      'price': 2100.0,
      'image': 'https://picsum.photos/200/200?random=85',
      'bids': 5,
      'views': 23,
      'timeLeft': '04时15分18秒',
      'isFavorite': false,
      'endTime': DateTime.now()
          .add(const Duration(hours: 6, minutes: 15, seconds: 18)),
    },
  ];

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

              // 顶部导航栏
              _buildHeader(),
              SizedBox(height: 16.h),

              // 排序筛选栏
              _buildSortBar(),
              SizedBox(height: 12.h),

              // 标签筛选
              _buildFilterTags(),
              SizedBox(height: 16.h),

              // 商品网格列表
              _buildProductGrid(),
              SizedBox(height: 100.h),
            ],
          ),
        ),
      ),
    );
  }

  // 构建顶部导航栏
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
          SizedBox(width: 12.w),

          // 标题
          Expanded(
            child: Text(
              widget.title ?? '山东鱼宠专场',
              style: TextStyle(
                fontSize: 18.sp,
                fontWeight: FontWeight.w600,
                color: const Color(0xFF333333),
              ),
              textAlign: TextAlign.center,
            ),
          ),

          // 搜索按钮
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SearchPage()),
              );
            },
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 8.h),
              decoration: BoxDecoration(
                color: const Color(0xFFF5F5F5),
                borderRadius: BorderRadius.circular(18.r),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.search,
                    size: 16.w,
                    color: const Color(0xFF999999),
                  ),
                  SizedBox(width: 4.w),
                  Text(
                    '搜索',
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: const Color(0xFF999999),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 构建排序筛选栏
  Widget _buildSortBar() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          // 默认排序
          _buildSortItem('默认排序', _selectedSort == '默认排序'),
          SizedBox(width: 24.w),

          // 价格排序
          _buildSortItem('价格', _selectedSort == '价格',
              hasArrow: true, isAscending: _priceAscending),
          SizedBox(width: 24.w),

          // 结标时间排序
          _buildSortItem('结标时间', _selectedSort == '结标时间',
              hasArrow: true, isAscending: _timeAscending),
          SizedBox(width: 24.w),

          // 我的关注
          _buildSortItem('我的关注', _selectedSort == '我的关注'),
        ],
      ),
    );
  }

  // 构建排序项目
  Widget _buildSortItem(String title, bool isSelected,
      {bool hasArrow = false, bool? isAscending}) {
    return GestureDetector(
      onTap: () {
        setState(() {
          if (title == '价格') {
            if (_selectedSort == '价格') {
              _priceAscending = !_priceAscending;
            } else {
              _selectedSort = '价格';
              _priceAscending = true;
            }
          } else if (title == '结标时间') {
            if (_selectedSort == '结标时间') {
              _timeAscending = !_timeAscending;
            } else {
              _selectedSort = '结标时间';
              _timeAscending = true;
            }
          } else {
            _selectedSort = title;
          }
        });
        _sortProducts();
      },
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 14.sp,
              color: isSelected
                  ? const Color(0xFF333333)
                  : const Color(0xFF999999),
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
          if (hasArrow) ...[
            SizedBox(width: 4.w),
            Icon(
              isAscending == true
                  ? Icons.keyboard_arrow_up
                  : Icons.keyboard_arrow_down,
              size: 16.w,
              color: isSelected
                  ? const Color(0xFF333333)
                  : const Color(0xFF999999),
            ),
          ],
        ],
      ),
    );
  }

  // 构建标签筛选
  Widget _buildFilterTags() {
    final tags = [
      {'name': '全部(500)', 'isSelected': _selectedTag == '全部(500)'},
      {'name': '竞价中', 'isSelected': _selectedTag == '竞价中'},
      {'name': '即将结束', 'isSelected': _selectedTag == '即将结束'},
      {'name': '热门推荐', 'isSelected': _selectedTag == '热门推荐'},
      {'name': '新品上架', 'isSelected': _selectedTag == '新品上架'},
      {'name': '犬类', 'isSelected': _selectedTag == '犬类'},
      {'name': '猫类', 'isSelected': _selectedTag == '猫类'},
      {'name': '鱼类', 'isSelected': _selectedTag == '鱼类'},
      {'name': '爬宠', 'isSelected': _selectedTag == '爬宠'},
    ];

    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Wrap(
        spacing: 8.w,
        runSpacing: 8.h,
        children: tags.map((tag) {
          return GestureDetector(
            onTap: () {
              setState(() {
                _selectedTag = tag['name'] as String;
              });
            },
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h),
              decoration: BoxDecoration(
                color: (tag['isSelected'] as bool)
                    ? const Color(0xFF9C4DFF)
                    : Colors.white,
                borderRadius: BorderRadius.circular(16.r),
                border: Border.all(
                  color: (tag['isSelected'] as bool)
                      ? const Color(0xFF9C4DFF)
                      : const Color(0xFFE0E0E0),
                  width: 1,
                ),
              ),
              child: Text(
                tag['name'] as String,
                style: TextStyle(
                  fontSize: 12.sp,
                  color: (tag['isSelected'] as bool)
                      ? Colors.white
                      : const Color(0xFF666666),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // 构建商品网格
  Widget _buildProductGrid() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 8.w,
          mainAxisSpacing: 12.h,
          childAspectRatio: 0.72, // 调整比例以匹配设计
        ),
        itemCount: _products.length,
        itemBuilder: (context, index) {
          final product = _products[index];
          return _buildProductCard(product);
        },
      ),
    );
  }

  // 构建商品卡片
  Widget _buildProductCard(Map<String, dynamic> product) {
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
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 商品图片
            Expanded(
              flex: 5, // 增加图片区域比例
              child: Stack(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(12.r),
                      topRight: Radius.circular(12.r),
                    ),
                    child: CachedNetworkImage(
                      imageUrl: product['image'],
                      fit: BoxFit.cover,
                      width: double.infinity,
                      height: double.infinity,
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
                  // 收藏按钮 - 位置调整为右上角
                  Positioned(
                    top: 8.h,
                    right: 8.w,
                    child: GestureDetector(
                      onTap: () {
                        setState(() {
                          product['isFavorite'] = !product['isFavorite'];
                        });
                      },
                      child: Container(
                        width: 28.w,
                        height: 28.w,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.9),
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 4,
                              offset: const Offset(0, 1),
                            ),
                          ],
                        ),
                        child: Icon(
                          product['isFavorite']
                              ? Icons.favorite
                              : Icons.favorite_border,
                          size: 16.w,
                          color: product['isFavorite']
                              ? const Color(0xFFFFEB3B) // 黄色心形
                              : const Color(0xFF999999),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // 商品信息区域
            Expanded(
              flex: 4, // 调整信息区域比例
              child: Padding(
                padding: EdgeInsets.all(8.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // 编号
                    Text(
                      '编号： ${product['id']}',
                      style: TextStyle(
                        fontSize: 10.sp,
                        color: const Color(0xFF9C4DFF),
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),

                    SizedBox(height: 2.h),

                    // 出价和观看数 - 优化布局
                    Row(
                      children: [
                        Icon(
                          Icons.person,
                          size: 12.w,
                          color: const Color(0xFF999999),
                        ),
                        SizedBox(width: 3.w),
                        Text(
                          '${product['bids']}次出价',
                          style: TextStyle(
                            fontSize: 11.sp,
                            color: const Color(0xFF999999),
                            fontWeight: FontWeight.w400,
                          ),
                        ),
                        SizedBox(width: 10.w),
                        Icon(
                          Icons.visibility,
                          size: 12.w,
                          color: const Color(0xFF999999),
                        ),
                        SizedBox(width: 3.w),
                        Text(
                          '${product['views']}人已看',
                          style: TextStyle(
                            fontSize: 11.sp,
                            color: const Color(0xFF999999),
                            fontWeight: FontWeight.w400,
                          ),
                        ),
                      ],
                    ),

                    SizedBox(height: 4.h),

                    // 商品标题 - 优化显示
                    Text(
                      product['name'],
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: const Color(0xFF333333),
                        fontWeight: FontWeight.w600,
                        height: 1.2,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),

                    SizedBox(height: 6.h),

                    // 价格和出价按钮 - 优化布局
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Text(
                          '¥${product['price']}',
                          style: TextStyle(
                            fontSize: 16.sp,
                            color: const Color(0xFFFF5722),
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        GestureDetector(
                          onTap: () {
                            print('点击出价');
                          },
                          child: Container(
                            padding: EdgeInsets.symmetric(
                                horizontal: 12.w, vertical: 6.h),
                            decoration: BoxDecoration(
                              color: const Color(0xFF9C4DFF),
                              borderRadius: BorderRadius.circular(15.r),
                            ),
                            child: Text(
                              '出价',
                              style: TextStyle(
                                fontSize: 11.sp,
                                color: Colors.white,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),

                    SizedBox(height: 4.h),

                    // 倒计时 - 优化显示
                    Row(
                      children: [
                        Icon(
                          Icons.access_time,
                          size: 12.w,
                          color: const Color(0xFF999999),
                        ),
                        SizedBox(width: 4.w),
                        Text(
                          product['timeLeft'],
                          style: TextStyle(
                            fontSize: 11.sp,
                            color: const Color(0xFF999999),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 排序商品
  void _sortProducts() {
    setState(() {
      switch (_selectedSort) {
        case '价格':
          _products.sort((a, b) {
            if (_priceAscending) {
              return (a['price'] as double).compareTo(b['price'] as double);
            } else {
              return (b['price'] as double).compareTo(a['price'] as double);
            }
          });
          break;
        case '结标时间':
          _products.sort((a, b) {
            if (_timeAscending) {
              return (a['endTime'] as DateTime)
                  .compareTo(b['endTime'] as DateTime);
            } else {
              return (b['endTime'] as DateTime)
                  .compareTo(a['endTime'] as DateTime);
            }
          });
          break;
        case '我的关注':
          _products.sort((a, b) {
            if ((a['isFavorite'] as bool) && !(b['isFavorite'] as bool)) {
              return -1;
            } else if (!(a['isFavorite'] as bool) &&
                (b['isFavorite'] as bool)) {
              return 1;
            } else {
              return 0;
            }
          });
          break;
        case '默认排序':
        default:
          // 按原始顺序排序
          break;
      }
    });
  }
}
