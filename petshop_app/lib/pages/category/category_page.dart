import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';
import '../../widgets/auction_card.dart';

class CategoryPage extends StatefulWidget {
  const CategoryPage({super.key});

  @override
  State<CategoryPage> createState() => _CategoryPageState();
}

class _CategoryPageState extends State<CategoryPage> {
  List<Map<String, dynamic>> products = [];
  String searchQuery = '';
  String selectedCategory = '全部';
  String sortBy = '默认';

  final List<String> categories = ['全部', '猫咪', '狗狗', '鸟类', '水族', '小动物'];
  final List<String> sortOptions = ['默认', '价格低到高', '价格高到低', '最新发布'];

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  void _loadProducts() {
    // 模拟商品数据
    products = [
      {
        'id': 1,
        'name': '纯种英短蓝猫',
        'currentPrice': 1200.0,
        'startPrice': 800.0,
        'image': 'https://picsum.photos/200/200?random=10',
        'category': '猫咪',
        'timeLeft': '2天3小时',
        'bidCount': 15,
        'description': '健康活泼的英短蓝猫，疫苗齐全，血统纯正',
        'location': '北京朝阳',
        'seller': {
          'name': '爱宠之家',
          'avatar': 'https://picsum.photos/50/50?random=1',
          'rating': 4.8,
        }
      },
      {
        'id': 2,
        'name': '金毛犬幼崽',
        'currentPrice': 2500.0,
        'startPrice': 1500.0,
        'image': 'https://picsum.photos/200/200?random=11',
        'category': '狗狗',
        'timeLeft': '1天12小时',
        'bidCount': 23,
        'description': '温顺可爱的金毛犬，已训练基本指令',
        'location': '上海浦东',
        'seller': {
          'name': '宠物乐园',
          'avatar': 'https://picsum.photos/50/50?random=2',
          'rating': 4.9,
        }
      },
      {
        'id': 3,
        'name': '虎皮鹦鹉',
        'currentPrice': 150.0,
        'startPrice': 80.0,
        'image': 'https://picsum.photos/200/200?random=14',
        'category': '鸟类',
        'timeLeft': '5天1小时',
        'bidCount': 6,
        'description': '活泼可爱的虎皮鹦鹉，会说话',
        'location': '深圳南山',
        'seller': {
          'name': '鸟语花香',
          'avatar': 'https://picsum.photos/50/50?random=4',
          'rating': 4.6,
        }
      },
      {
        'id': 4,
        'name': '红绿灯鱼',
        'currentPrice': 25.0,
        'startPrice': 15.0,
        'image': 'https://picsum.photos/200/200?random=15',
        'category': '水族',
        'timeLeft': '3天8小时',
        'bidCount': 12,
        'description': '群游观赏鱼，颜色艳丽',
        'location': '杭州西湖',
        'seller': {
          'name': '水族世界',
          'avatar': 'https://picsum.photos/50/50?random=5',
          'rating': 4.7,
        }
      },
      {
        'id': 5,
        'name': '荷兰猪',
        'currentPrice': 80.0,
        'startPrice': 50.0,
        'image': 'https://picsum.photos/200/200?random=16',
        'category': '小动物',
        'timeLeft': '4天2小时',
        'bidCount': 8,
        'description': '可爱的荷兰猪，性格温顺',
        'location': '成都武侯',
        'seller': {
          'name': '小动物天地',
          'avatar': 'https://picsum.photos/50/50?random=6',
          'rating': 4.5,
        }
      },
    ];
    setState(() {});
  }

  List<Map<String, dynamic>> get filteredProducts {
    var filtered = products.where((product) {
      final matchesCategory =
          selectedCategory == '全部' || product['category'] == selectedCategory;
      final matchesSearch = product['name']
          .toString()
          .toLowerCase()
          .contains(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    }).toList();

    // 排序
    switch (sortBy) {
      case '价格低到高':
        filtered.sort((a, b) => (a['currentPrice'] as double)
            .compareTo(b['currentPrice'] as double));
        break;
      case '价格高到低':
        filtered.sort((a, b) => (b['currentPrice'] as double)
            .compareTo(a['currentPrice'] as double));
        break;
      case '最新发布':
        // 这里可以根据发布时间排序，暂时保持原顺序
        break;
      default:
        // 默认排序
        break;
    }

    return filtered;
  }

  @override
  Widget build(BuildContext context) {
    final category =
        ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;
    final categoryName = category?['name'] ?? '分类';

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          categoryName,
          style: TextStyle(
            color: AppColors.textPrimary,
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
          ),
        ),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: IconThemeData(color: AppColors.textPrimary),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              Navigator.pushNamed(context, '/search');
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // 分类选择器
          Container(
            height: 50.h,
            color: Colors.white,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: EdgeInsets.symmetric(horizontal: 16.w),
              itemCount: categories.length,
              itemBuilder: (context, index) {
                final category = categories[index];
                final isSelected = category == selectedCategory;
                return GestureDetector(
                  onTap: () {
                    setState(() {
                      selectedCategory = category;
                    });
                  },
                  child: Container(
                    margin: EdgeInsets.only(right: 16.w, top: 8.h, bottom: 8.h),
                    padding: EdgeInsets.symmetric(horizontal: 16.w),
                    decoration: BoxDecoration(
                      color:
                          isSelected ? AppColors.primary : Colors.transparent,
                      borderRadius: BorderRadius.circular(20.r),
                      border: Border.all(
                        color:
                            isSelected ? AppColors.primary : AppColors.border,
                      ),
                    ),
                    alignment: Alignment.center,
                    child: Text(
                      category,
                      style: TextStyle(
                        fontSize: 14.sp,
                        color:
                            isSelected ? Colors.white : AppColors.textSecondary,
                        fontWeight:
                            isSelected ? FontWeight.w500 : FontWeight.normal,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          // 排序选择器
          Container(
            height: 44.h,
            color: Colors.white,
            padding: EdgeInsets.symmetric(horizontal: 16.w),
            child: Row(
              children: [
                Text(
                  '共${filteredProducts.length}个商品',
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: AppColors.textSecondary,
                  ),
                ),
                const Spacer(),
                GestureDetector(
                  onTap: () {
                    _showSortOptions();
                  },
                  child: Row(
                    children: [
                      Text(
                        sortBy,
                        style: TextStyle(
                          fontSize: 14.sp,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      SizedBox(width: 4.w),
                      Icon(
                        Icons.keyboard_arrow_down,
                        size: 16.w,
                        color: AppColors.textSecondary,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // 商品列表
          Expanded(
            child: filteredProducts.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.pets,
                          size: 64.w,
                          color: AppColors.textHint,
                        ),
                        SizedBox(height: 16.h),
                        Text(
                          '暂无商品',
                          style: TextStyle(
                            fontSize: 16.sp,
                            color: AppColors.textHint,
                          ),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: EdgeInsets.all(16.w),
                    itemCount: filteredProducts.length,
                    itemBuilder: (context, index) {
                      final product = filteredProducts[index];
                      return Container(
                        margin: EdgeInsets.only(bottom: 16.h),
                        child: AuctionCard(
                          product: product,
                          onTap: () {
                            Navigator.pushNamed(
                              context,
                              '/product-detail',
                              arguments: product,
                            );
                          },
                          onFavorite: () {
                            setState(() {
                              int originalIndex = products
                                  .indexWhere((p) => p['id'] == product['id']);
                              if (originalIndex != -1) {
                                products[originalIndex]['isFavorite'] =
                                    !(product['isFavorite'] ?? false);
                              }
                            });
                          },
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  void _showSortOptions() {
    showModalBottomSheet(
      context: context,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20.r)),
      ),
      builder: (context) {
        return Container(
          padding: EdgeInsets.all(20.w),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40.w,
                height: 4.h,
                decoration: BoxDecoration(
                  color: AppColors.divider,
                  borderRadius: BorderRadius.circular(2.r),
                ),
              ),
              SizedBox(height: 20.h),
              Text(
                '排序方式',
                style: TextStyle(
                  fontSize: 18.sp,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              SizedBox(height: 20.h),
              ...sortOptions.map((option) {
                return ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(
                    option,
                    style: TextStyle(
                      fontSize: 16.sp,
                      color: sortBy == option
                          ? AppColors.primary
                          : AppColors.textPrimary,
                    ),
                  ),
                  trailing: sortBy == option
                      ? Icon(Icons.check, color: AppColors.primary)
                      : null,
                  onTap: () {
                    setState(() {
                      sortBy = option;
                    });
                    Navigator.pop(context);
                  },
                );
              }).toList(),
              SizedBox(height: 20.h),
            ],
          ),
        );
      },
    );
  }
}
