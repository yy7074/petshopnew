import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';
import '../../widgets/auction_card.dart';

class SearchPage extends StatefulWidget {
  const SearchPage({super.key});

  @override
  State<SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage> {
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _searchFocus = FocusNode();

  List<Map<String, dynamic>> searchResults = [];
  List<String> searchHistory = [];
  List<String> hotSearches = ['英短蓝猫', '金毛犬', '布偶猫', '柯基', '萨摩耶', '虎皮鹦鹉'];
  bool isSearching = false;
  bool showResults = false;

  // 模拟全部商品数据
  final List<Map<String, dynamic>> allProducts = [
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
      'name': '布偶猫种公',
      'currentPrice': 3800.0,
      'startPrice': 2000.0,
      'image': 'https://picsum.photos/200/200?random=12',
      'category': '猫咪',
      'timeLeft': '3天8小时',
      'bidCount': 8,
      'description': '品相极佳的布偶猫种公，可用于繁殖',
      'location': '广州天河',
      'seller': {
        'name': '名猫馆',
        'avatar': 'https://picsum.photos/50/50?random=3',
        'rating': 4.7,
      }
    },
    {
      'id': 4,
      'name': '柯基犬',
      'currentPrice': 1800.0,
      'startPrice': 1200.0,
      'image': 'https://picsum.photos/200/200?random=17',
      'category': '狗狗',
      'timeLeft': '2天15小时',
      'bidCount': 19,
      'description': '短腿可爱的柯基犬，性格活泼',
      'location': '南京鼓楼',
      'seller': {
        'name': '萌宠基地',
        'avatar': 'https://picsum.photos/50/50?random=7',
        'rating': 4.6,
      }
    },
    {
      'id': 5,
      'name': '萨摩耶幼犬',
      'currentPrice': 2200.0,
      'startPrice': 1800.0,
      'image': 'https://picsum.photos/200/200?random=18',
      'category': '狗狗',
      'timeLeft': '4天6小时',
      'bidCount': 12,
      'description': '微笑天使萨摩耶，毛量丰厚',
      'location': '天津河西',
      'seller': {
        'name': '白雪公主',
        'avatar': 'https://picsum.photos/50/50?random=8',
        'rating': 4.8,
      }
    },
  ];

  @override
  void initState() {
    super.initState();
    _loadSearchHistory();
    _searchFocus.requestFocus();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _searchFocus.dispose();
    super.dispose();
  }

  void _loadSearchHistory() {
    // 模拟加载搜索历史
    searchHistory = ['英短蓝猫', '金毛犬'];
  }

  void _performSearch(String query) {
    if (query.trim().isEmpty) {
      setState(() {
        showResults = false;
        searchResults = [];
      });
      return;
    }

    setState(() {
      isSearching = true;
    });

    // 模拟搜索延迟
    Future.delayed(const Duration(milliseconds: 500), () {
      final results = allProducts.where((product) {
        return product['name']
                .toString()
                .toLowerCase()
                .contains(query.toLowerCase()) ||
            product['description']
                .toString()
                .toLowerCase()
                .contains(query.toLowerCase());
      }).toList();

      setState(() {
        searchResults = results;
        showResults = true;
        isSearching = false;
      });

      // 添加到搜索历史
      _addToSearchHistory(query);
    });
  }

  void _addToSearchHistory(String query) {
    if (!searchHistory.contains(query)) {
      setState(() {
        searchHistory.insert(0, query);
        if (searchHistory.length > 10) {
          searchHistory = searchHistory.sublist(0, 10);
        }
      });
    }
  }

  void _clearSearchHistory() {
    setState(() {
      searchHistory.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: _buildSearchBar(),
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: showResults ? _buildSearchResults() : _buildSearchSuggestions(),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      height: 36.h,
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(18.r),
      ),
      child: TextField(
        controller: _searchController,
        focusNode: _searchFocus,
        decoration: InputDecoration(
          hintText: '搜索宠物、水族用品...',
          hintStyle: TextStyle(
            fontSize: 14.sp,
            color: AppColors.textSecondary,
          ),
          prefixIcon: Icon(
            Icons.search,
            size: 20.w,
            color: AppColors.textSecondary,
          ),
          suffixIcon: _searchController.text.isNotEmpty
              ? IconButton(
                  icon: Icon(
                    Icons.clear,
                    size: 18.w,
                    color: AppColors.textSecondary,
                  ),
                  onPressed: () {
                    _searchController.clear();
                    setState(() {
                      showResults = false;
                      searchResults = [];
                    });
                  },
                )
              : null,
          border: InputBorder.none,
          contentPadding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
        ),
        style: TextStyle(
          fontSize: 14.sp,
          color: AppColors.textPrimary,
        ),
        onChanged: (value) {
          setState(() {});
          if (value.trim().isNotEmpty) {
            _performSearch(value);
          } else {
            setState(() {
              showResults = false;
              searchResults = [];
            });
          }
        },
        onSubmitted: (value) {
          _performSearch(value);
        },
      ),
    );
  }

  Widget _buildSearchSuggestions() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 搜索历史
          if (searchHistory.isNotEmpty) ...[
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '搜索历史',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                GestureDetector(
                  onTap: _clearSearchHistory,
                  child: Text(
                    '清空',
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 12.h),
            Wrap(
              spacing: 8.w,
              runSpacing: 8.h,
              children: searchHistory.map((item) {
                return GestureDetector(
                  onTap: () {
                    _searchController.text = item;
                    _performSearch(item);
                  },
                  child: Container(
                    padding:
                        EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16.r),
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.history,
                          size: 14.w,
                          color: AppColors.textSecondary,
                        ),
                        SizedBox(width: 4.w),
                        Text(
                          item,
                          style: TextStyle(
                            fontSize: 14.sp,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
            SizedBox(height: 24.h),
          ],

          // 热门搜索
          Text(
            '热门搜索',
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          SizedBox(height: 12.h),
          Wrap(
            spacing: 8.w,
            runSpacing: 8.h,
            children: hotSearches.asMap().entries.map((entry) {
              final index = entry.key;
              final item = entry.value;
              final isHot = index < 3;

              return GestureDetector(
                onTap: () {
                  _searchController.text = item;
                  _performSearch(item);
                },
                child: Container(
                  padding:
                      EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h),
                  decoration: BoxDecoration(
                    color: isHot
                        ? AppColors.primary.withOpacity(0.1)
                        : Colors.white,
                    borderRadius: BorderRadius.circular(16.r),
                    border: Border.all(
                      color: isHot ? AppColors.primary : AppColors.border,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (isHot) ...[
                        Icon(
                          Icons.local_fire_department,
                          size: 14.w,
                          color: AppColors.primary,
                        ),
                        SizedBox(width: 4.w),
                      ],
                      Text(
                        item,
                        style: TextStyle(
                          fontSize: 14.sp,
                          color: isHot
                              ? AppColors.primary
                              : AppColors.textSecondary,
                          fontWeight:
                              isHot ? FontWeight.w500 : FontWeight.normal,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchResults() {
    if (isSearching) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
            ),
            SizedBox(height: 16.h),
            Text(
              '搜索中...',
              style: TextStyle(
                fontSize: 14.sp,
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      );
    }

    if (searchResults.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off,
              size: 64.w,
              color: AppColors.textHint,
            ),
            SizedBox(height: 16.h),
            Text(
              '没有找到相关商品',
              style: TextStyle(
                fontSize: 16.sp,
                color: AppColors.textHint,
              ),
            ),
            SizedBox(height: 8.h),
            Text(
              '试试其他关键词吧',
              style: TextStyle(
                fontSize: 14.sp,
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        // 搜索结果头部
        Container(
          padding: EdgeInsets.all(16.w),
          color: Colors.white,
          child: Row(
            children: [
              Text(
                '共找到${searchResults.length}个商品',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),

        // 搜索结果列表
        Expanded(
          child: ListView.builder(
            padding: EdgeInsets.all(16.w),
            itemCount: searchResults.length,
            itemBuilder: (context, index) {
              final product = searchResults[index];
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
                      searchResults[index]['isFavorite'] =
                          !(product['isFavorite'] ?? false);
                    });
                  },
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
