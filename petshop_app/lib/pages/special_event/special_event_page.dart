import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../search/search_page.dart';
import '../product/product_detail_page.dart';
import '../../services/event_service.dart';
import '../../services/auction_service.dart';
import '../../services/favorite_service.dart';
import '../../models/product.dart' as product_models;

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
  final EventService _eventService = EventService();
  final AuctionService _auctionService = AuctionService();
  final FavoriteService _favoriteService = FavoriteService();
  
  // 排序状态管理
  String _selectedSort = '默认排序';
  bool _priceAscending = true;
  bool _timeAscending = true;

  // 标签筛选状态
  String _selectedTag = '全部(500)';

  // 加载状态
  bool _isLoading = true;
  String? _errorMessage;

  // 商品数据
  List<product_models.Product> _products = [];
  List<product_models.Product> _allProducts = []; // 存储所有商品用于筛选

  @override
  void initState() {
    super.initState();
    _loadEventProducts();
  }

  /// 加载专场商品
  Future<void> _loadEventProducts() async {
    if (widget.eventId == null) {
      setState(() {
        _isLoading = false;
        _errorMessage = '专场 ID 不能为空';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await _eventService.getEventProducts(
        eventId: int.parse(widget.eventId!),
        page: 1,
        pageSize: 50,
      );

      if (result.success && result.data != null) {
        final productList = result.data!
            .map((item) => product_models.Product.fromJson(item))
            .toList();
        
        setState(() {
          _allProducts = productList;
          _products = List.from(productList);
          _isLoading = false;
          _selectedTag = '全部(${_products.length})';
        });
      } else {
        setState(() {
          _isLoading = false;
          _errorMessage = result.message ?? '加载商品失败';
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = '加载商品失败: $e';
      });
    }
  }

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
    if (_isLoading) {
      return Container(
        margin: EdgeInsets.symmetric(horizontal: 16.w),
        height: 400.h,
        child: const Center(
          child: CircularProgressIndicator(
            color: Color(0xFF9C4DFF),
          ),
        ),
      );
    }

    if (_errorMessage != null) {
      return Container(
        margin: EdgeInsets.symmetric(horizontal: 16.w),
        height: 400.h,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline,
                size: 64.w,
                color: const Color(0xFF999999),
              ),
              SizedBox(height: 16.h),
              Text(
                _errorMessage!,
                style: TextStyle(
                  fontSize: 14.sp,
                  color: const Color(0xFF999999),
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 16.h),
              ElevatedButton(
                onPressed: _loadEventProducts,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF9C4DFF),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                ),
                child: Text(
                  '重试',
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    }

    if (_products.isEmpty) {
      return Container(
        margin: EdgeInsets.symmetric(horizontal: 16.w),
        height: 400.h,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.pets,
                size: 64.w,
                color: const Color(0xFF999999),
              ),
              SizedBox(height: 16.h),
              Text(
                '暂无商品',
                style: TextStyle(
                  fontSize: 16.sp,
                  color: const Color(0xFF999999),
                ),
              ),
              SizedBox(height: 8.h),
              Text(
                '请稍后再来看看吧',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: const Color(0xFFCCCCCC),
                ),
              ),
            ],
          ),
        ),
      );
    }

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
  Widget _buildProductCard(product_models.Product product) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ProductDetailPage(
              productData: _convertProductToMap(product),
            ),
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
                      imageUrl: product.images.isNotEmpty 
                          ? product.images.first 
                          : 'https://picsum.photos/200/200?random=${product.id}',
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
                        _toggleFavorite(product.id);
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
                          Icons.favorite_border, // 暂时显示未收藏状态
                          size: 16.w,
                          color: const Color(0xFF999999),
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
                      '编号： ${product.id}',
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
                          '${product.auctionInfo?.bidCount ?? 0}次出价',
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
                          '${product.auctionInfo?.bidCount ?? 0}人已看',
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
                      product.title,
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
                          '¥${product.currentPrice.toStringAsFixed(2)}',
                          style: TextStyle(
                            fontSize: 16.sp,
                            color: const Color(0xFFFF5722),
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        GestureDetector(
                          onTap: () {
                            // TODO: 实现出价功能
                            _showBidDialog(product);
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
                          _formatTimeLeft(product.auctionInfo?.endTime),
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
              return a.currentPrice.compareTo(b.currentPrice);
            } else {
              return b.currentPrice.compareTo(a.currentPrice);
            }
          });
          break;
        case '结标时间':
          _products.sort((a, b) {
            final aEndTime = a.auctionInfo?.endTime ?? DateTime.now();
            final bEndTime = b.auctionInfo?.endTime ?? DateTime.now();
            if (_timeAscending) {
              return aEndTime.compareTo(bEndTime);
            } else {
              return bEndTime.compareTo(aEndTime);
            }
          });
          break;
        case '我的关注':
          _products.sort((a, b) {
            // 假设收藏状态暂时为false，后续需要实现收藏功能
            final aFavorite = false; // TODO: 从用户收藏列表获取
            final bFavorite = false; // TODO: 从用户收藏列表获取
            if (aFavorite && !bFavorite) {
              return -1;
            } else if (!aFavorite && bFavorite) {
              return 1;
            } else {
              return 0;
            }
          });
          break;
        case '默认排序':
        default:
          // 恢复原始顺序
          _products = List.from(_allProducts);
          break;
      }
    });
  }

  // 将Product对象转换为Map用于ProductDetailPage
  Map<String, dynamic> _convertProductToMap(product_models.Product product) {
    return {
      'id': product.id,
      'title': product.title,
      'description': product.description,
      'images': product.images,
      'price': product.currentPrice,
      'original_price': product.auctionInfo?.startPrice ?? product.fixedInfo?.price ?? 0,
      'status': product.status,
      'category': product.categoryId.toString(),
      'breed': '', // Product模型中没有breed字段，使用空字符串
      'age': 0, // Product模型中没有age字段，使用默认值
      'gender': '', // Product模型中没有gender字段，使用空字符串
      'location': product.location ?? '',
      'seller_id': product.sellerId,
      'seller_name': product.seller?.name ?? '',
      'auction_type': product.type == product_models.ProductType.auction ? 1 : 2,
      'starting_price': product.auctionInfo?.startPrice ?? 0,
      'current_price': product.currentPrice,
      'bid_increment': product.auctionInfo?.bidIncrement ?? 10.0,
      'auction_info': product.auctionInfo != null ? {
        'start_time': product.auctionInfo!.startTime.toIso8601String(),
        'end_time': product.auctionInfo!.endTime.toIso8601String(),
        'bid_count': product.auctionInfo!.bidCount,
        'current_price': product.auctionInfo!.currentPrice,
        'bid_increment': product.auctionInfo!.bidIncrement,
      } : null,
      'created_at': product.createdAt.toIso8601String(),
      'updated_at': product.updatedAt.toIso8601String(),
    };
  }

  // 格式化剩余时间
  String _formatTimeLeft(DateTime? endTime) {
    if (endTime == null) {
      return '已结束';
    }

    final now = DateTime.now();
    final difference = endTime.difference(now);

    if (difference.isNegative) {
      return '已结束';
    }

    final days = difference.inDays;
    final hours = difference.inHours % 24;
    final minutes = difference.inMinutes % 60;

    if (days > 0) {
      return '${days}天${hours}小时';
    } else if (hours > 0) {
      return '${hours}小时${minutes}分钟';
    } else {
      return '${minutes}分钟';
    }
  }

  // 显示出价对话框
  void _showBidDialog(product_models.Product product) {
    final TextEditingController bidController = TextEditingController();
    final double minBid = product.currentPrice + (product.auctionInfo?.bidIncrement ?? 10.0);
    
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16.r),
          ),
          title: Text(
            '出价竞拍',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF333333),
            ),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                product.title,
                style: TextStyle(
                  fontSize: 14.sp,
                  color: const Color(0xFF666666),
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              SizedBox(height: 16.h),
              Text(
                '当前价格: ¥${product.currentPrice.toStringAsFixed(2)}',
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.w600,
                  color: const Color(0xFFFF5722),
                ),
              ),
              SizedBox(height: 8.h),
              Text(
                '最低出价: ¥${minBid.toStringAsFixed(2)}',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: const Color(0xFF666666),
                ),
              ),
              SizedBox(height: 16.h),
              TextField(
                controller: bidController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: '您的出价',
                  hintText: '请输入出价金额',
                  prefixText: '¥',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.r),
                    borderSide: const BorderSide(
                      color: Color(0xFF9C4DFF),
                      width: 2,
                    ),
                  ),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text(
                '取消',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: const Color(0xFF999999),
                ),
              ),
            ),
            ElevatedButton(
              onPressed: () {
                final bidAmount = double.tryParse(bidController.text);
                if (bidAmount == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('请输入有效的出价金额')),
                  );
                  return;
                }
                
                if (bidAmount < minBid) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('出价不能低于最低出价 ¥${minBid.toStringAsFixed(2)}'),
                    ),
                  );
                  return;
                }
                
                // TODO: 调用出价API
                Navigator.of(context).pop();
                _placeBid(product.id, bidAmount);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF9C4DFF),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8.r),
                ),
              ),
              child: Text(
                '确认出价',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  // 提交出价
  Future<void> _placeBid(int productId, double bidAmount) async {
    try {
      final result = await _auctionService.placeBid(
        productId: productId,
        bidAmount: bidAmount,
      );
      
      if (result.success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('出价成功: ¥${bidAmount.toStringAsFixed(2)}'),
            backgroundColor: Colors.green,
          ),
        );
        
        // 刷新商品数据
        _loadEventProducts();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('出价失败: ${result.message}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('出价失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  // 切换收藏状态
  Future<void> _toggleFavorite(int productId) async {
    try {
      // 首先检查当前收藏状态
      final checkResult = await _favoriteService.isFavorite(productId);
      
      if (checkResult.success) {
        final bool isFavorited = checkResult.data!;
        
        if (isFavorited) {
          // 取消收藏
          final result = await _favoriteService.removeFavorite(productId);
          if (result.success) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('已取消收藏'),
                backgroundColor: Colors.orange,
              ),
            );
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('取消收藏失败: ${result.message}'),
                backgroundColor: Colors.red,
              ),
            );
          }
        } else {
          // 添加收藏
          final result = await _favoriteService.addFavorite(productId);
          if (result.success) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('收藏成功'),
                backgroundColor: Colors.green,
              ),
            );
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('收藏失败: ${result.message}'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('检查收藏状态失败: ${checkResult.message}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('收藏操作失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}