import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:card_swiper/card_swiper.dart';
import '../../constants/app_colors.dart';
import '../../services/bid_service.dart';
import '../../services/auction_service.dart';
import '../../models/bid.dart';
import '../../utils/app_routes.dart';
import 'package:get/get.dart';

class ProductDetailPage extends StatefulWidget {
  final Map<String, dynamic>? productData;

  const ProductDetailPage({super.key, this.productData});

  @override
  State<ProductDetailPage> createState() => _ProductDetailPageState();
}

class _ProductDetailPageState extends State<ProductDetailPage> {
  int currentImageIndex = 0;
  final TextEditingController _bidController = TextEditingController();
  final TextEditingController _messageController = TextEditingController();
  final BidService _bidService = BidService();
  final AuctionService _auctionService = AuctionService();
  List<Bid> _bidHistory = [];
  bool _isLoadingBids = false;

  // 拍卖相关状态
  Map<String, dynamic>? _auctionStatus;
  bool _isLoadingAuctionStatus = false;
  bool _isWinner = false;

  List<String> productImages = [];

  final List<Map<String, dynamic>> bidHistory = [
    {'user': '用户A', 'price': 450, 'time': '23:45'},
    {'user': '用户B', 'price': 440, 'time': '23:40'},
    {'user': '用户C', 'price': 435, 'time': '23:35'},
  ];

  @override
  void initState() {
    super.initState();
    _initializeProductImages();
    _loadAuctionStatus();
    _loadBidHistory();
  }

  void _initializeProductImages() {
    final images = widget.productData?['images'] as List?;
    if (images != null && images.isNotEmpty) {
      productImages = images.cast<String>();
    } else {
      // 如果没有图片，使用默认图片
      productImages = ['https://picsum.photos/400/400?random=product'];
    }
  }

  Future<void> _loadAuctionStatus() async {
    // 这里应该从路由参数或widget.productData中获取productId
    final productIdRaw = widget.productData?['id'] ?? 1;
    final productId = productIdRaw is String
        ? int.tryParse(productIdRaw) ?? 1
        : productIdRaw as int;

    setState(() => _isLoadingAuctionStatus = true);

    try {
      final result = await _auctionService.getAuctionStatus(productId);
      setState(() {
        if (result.success && result.data != null) {
          _auctionStatus = result.data;
        } else {
          // API不存在时使用商品基本数据构造拍卖状态
          _auctionStatus = {
            'current_price': widget.productData?['current_price'] ?? '800',
            'is_ended': false,
            'status': 2,
            'bid_count': widget.productData?['bid_count'] ?? 0,
            'end_time': widget.productData?['auction_end_time'],
            'min_increment': '10.0'
          };
        }
        // 检查是否已结束且用户是否中标
        _checkIfWinner(productId);
      });
    } catch (e) {
      print('加载拍卖状态失败: $e');
      // 发生错误时也使用基本数据
      setState(() {
        _auctionStatus = {
          'current_price': widget.productData?['current_price'] ?? '800',
          'is_ended': false,
          'status': 2,
          'bid_count': widget.productData?['bid_count'] ?? 0,
          'end_time': widget.productData?['auction_end_time'],
          'min_increment': '10.0'
        };
      });
    } finally {
      setState(() => _isLoadingAuctionStatus = false);
    }
  }

  Future<void> _loadBidHistory() async {
    final productIdRaw = widget.productData?['id'] ?? 1;
    final productId = productIdRaw is String
        ? int.tryParse(productIdRaw) ?? 1
        : productIdRaw as int;

    setState(() => _isLoadingBids = true);

    try {
      final result = await _bidService.getProductBids(productId: productId, page: 1, pageSize: 10);
      if (result.success && result.data != null) {
        setState(() {
          _bidHistory = result.data!;
        });
      }
    } catch (e) {
      print('加载竞拍记录失败: $e');
    } finally {
      setState(() => _isLoadingBids = false);
    }
  }

  String _getCurrentPrice() {
    // 优先使用竞拍记录中的最高价格
    if (_bidHistory.isNotEmpty) {
      final highestBid = _bidHistory.first; // 竞拍记录已按时间倒序排列，第一个就是最新最高的
      return highestBid.bidAmount.toStringAsFixed(0);
    }
    
    // 其次使用拍卖状态中的价格
    if (_auctionStatus?['current_price'] != null) {
      final priceStr = _auctionStatus!['current_price'].toString();
      final price = double.tryParse(priceStr);
      return price?.toStringAsFixed(0) ?? priceStr;
    }
    
    // 最后使用商品基础数据中的价格
    final basePrice = widget.productData?['current_price'];
    if (basePrice != null) {
      final price = double.tryParse(basePrice.toString());
      return price?.toStringAsFixed(0) ?? basePrice.toString();
    }
    
    // 默认值
    return '0';
  }

  Future<void> _checkIfWinner(int productId) async {
    try {
      final result = await _auctionService.getMyWinningAuctions();
      if (result.success && result.data != null) {
        final items = result.data!;

        if (items.isNotEmpty) {
          final hasWon = items.any((item) {
            final itemProductId = item['product_id'];
            // 确保类型匹配，支持String或int类型的product_id
            if (itemProductId is String) {
              return int.tryParse(itemProductId) == productId;
            } else if (itemProductId is int) {
              return itemProductId == productId;
            }
            return false;
          });
          setState(() => _isWinner = hasWon);
        }
      }
    } catch (e) {
      print('检查中标状态失败: $e');
      // API不可用时默认为未中标状态
      setState(() => _isWinner = false);
    }
  }

  Future<void> _placeBid(double bidAmount) async {
    final productIdRaw = widget.productData?['id'] ?? 1;
    final productId = productIdRaw is String
        ? int.tryParse(productIdRaw) ?? 1
        : productIdRaw as int;

    setState(() => _isLoadingBids = true);

    try {
      final result = await _bidService.placeBid(
        productId: productId,
        bidAmount: bidAmount,
      );

      if (result.success) {
        // 出价成功，刷新拍卖状态和竞拍记录
        await _loadAuctionStatus();
        await _loadBidHistory();

        if (mounted) {
          Navigator.pop(context);
        }
        Get.snackbar(
          '出价成功',
          '恭喜！您已成功出价 ¥${bidAmount.toStringAsFixed(0)}，当前领先',
          backgroundColor: AppColors.success,
          colorText: Colors.white,
        );
      } else {
        // 检查是否是商品不存在的错误，提供友好提示
        String errorMessage = result.message;
        if (errorMessage.contains('商品不存在') ||
            errorMessage.contains('Not Found')) {
          errorMessage = '这是演示商品，请在真实环境中测试出价功能';
        }

        Get.snackbar(
          '出价失败',
          errorMessage,
          backgroundColor: AppColors.error,
          colorText: Colors.white,
        );
      }
    } catch (e) {
      Get.snackbar(
        '出价失败',
        '网络错误，请稍后重试',
        backgroundColor: AppColors.error,
        colorText: Colors.white,
      );
    } finally {
      setState(() => _isLoadingBids = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: Colors.black, size: 20.w),
          onPressed: () => Navigator.pop(context),
        ),
        title: Row(
          children: [
            CircleAvatar(
              radius: 16.w,
              backgroundImage: const AssetImage('assets/images/avatar1.jpg'),
            ),
            SizedBox(width: 8.w),
            Text(
              '招财猫旺财狗',
              style: TextStyle(
                color: Colors.black,
                fontSize: 16.sp,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              print('===== 进店按钮点击 =====');
              print('完整的productData: ${widget.productData}');
              
              // 获取商品的卖家ID，导航到店铺页面
              final sellerId = widget.productData?['seller_id'];
              print('直接获取的seller_id: $sellerId (类型: ${sellerId.runtimeType})');
              
              if (sellerId != null) {
                final finalSellerId = sellerId is String ? int.tryParse(sellerId) : sellerId;
                print('转换后的seller_id: $finalSellerId');
                print('导航到店铺页面，seller_id: $finalSellerId');
                
                Get.toNamed(
                  AppRoutes.store,
                  arguments: {
                    'seller_id': finalSellerId,
                  },
                );
              } else {
                print('seller_id为空，尝试从其他字段获取...');
                
                // 尝试从其他可能的字段获取
                final sellerIdAlt = widget.productData?['seller_info']?['id'] ?? 
                                   widget.productData?['owner_id'];
                print('备用seller_id: $sellerIdAlt');
                
                if (sellerIdAlt != null) {
                  final finalSellerIdAlt = sellerIdAlt is String ? int.tryParse(sellerIdAlt) : sellerIdAlt;
                  print('使用备用seller_id导航: $finalSellerIdAlt');
                  
                  Get.toNamed(
                    AppRoutes.store,
                    arguments: {
                      'seller_id': finalSellerIdAlt,
                    },
                  );
                } else {
                  print('所有seller_id字段都为空，显示错误提示');
                  print('productData的所有键: ${widget.productData?.keys.toList()}');
                  
                  Get.snackbar(
                    '提示',
                    '店铺信息不完整 - 无法找到seller_id',
                    backgroundColor: AppColors.error,
                    colorText: Colors.white,
                  );
                }
              }
              print('===== 进店按钮处理完成 =====');
            },
            child: Text(
              '进店',
              style: TextStyle(
                color: Colors.blue,
                fontSize: 14.sp,
              ),
            ),
          ),
          SizedBox(width: 16.w),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Product Image Swiper
                  Container(
                    height: 300.h,
                    child: Stack(
                      children: [
                        Swiper(
                          itemCount: productImages.length,
                          itemBuilder: (context, index) {
                            return Container(
                              margin: EdgeInsets.symmetric(horizontal: 16.w),
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(8.w),
                              ),
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(8.w),
                                child: Image.network(
                                  productImages[index],
                                  fit: BoxFit.cover,
                                  errorBuilder: (context, error, stackTrace) {
                                    return Container(
                                      color: Colors.grey[200],
                                      child: const Icon(
                                        Icons.image_not_supported,
                                        color: Colors.grey,
                                        size: 50,
                                      ),
                                    );
                                  },
                                  loadingBuilder: (context, child, loadingProgress) {
                                    if (loadingProgress == null) return child;
                                    return Container(
                                      color: Colors.grey[200],
                                      child: const Center(
                                        child: CircularProgressIndicator(),
                                      ),
                                    );
                                  },
                                ),
                              ),
                            );
                          },
                          pagination: SwiperPagination(
                            builder: DotSwiperPaginationBuilder(
                              color: Colors.white.withOpacity(0.5),
                              activeColor: Colors.white,
                              size: 6.w,
                              activeSize: 6.w,
                            ),
                          ),
                          onIndexChanged: (index) {
                            setState(() {
                              currentImageIndex = index;
                            });
                          },
                        ),
                      ],
                    ),
                  ),

                  // Service Guarantee Banner
                  Container(
                    margin: EdgeInsets.all(16.w),
                    padding:
                        EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
                    decoration: BoxDecoration(
                      color: Colors.purple.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8.w),
                      border: Border.all(color: Colors.purple.withOpacity(0.3)),
                    ),
                    child: GestureDetector(
                      onTap: () => _showServiceGuarantee(),
                      child: Row(
                        children: [
                          Icon(
                            Icons.verified_user,
                            color: Colors.purple,
                            size: 16.w,
                          ),
                          SizedBox(width: 8.w),
                          Expanded(
                            child: Text(
                              '服务保障 · 无理由退货免税 · 包邮 · 商品审核 · ...',
                              style: TextStyle(
                                color: Colors.purple,
                                fontSize: 12.sp,
                              ),
                            ),
                          ),
                          Icon(
                            Icons.arrow_forward_ios,
                            color: Colors.purple,
                            size: 12.w,
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Product Info
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16.w),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.productData?['title'] ?? '可爱宠物等你带回家',
                          style: TextStyle(
                            fontSize: 16.sp,
                            fontWeight: FontWeight.w600,
                            height: 1.4,
                          ),
                        ),
                        SizedBox(height: 8.h),
                        Row(
                          children: [
                            Container(
                              padding: EdgeInsets.symmetric(
                                  horizontal: 6.w, vertical: 2.h),
                              decoration: BoxDecoration(
                                color: Colors.orange,
                                borderRadius: BorderRadius.circular(2.w),
                              ),
                              child: Text(
                                '包邮',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 10.sp,
                                ),
                              ),
                            ),
                          ],
                        ),
                        SizedBox(height: 12.h),
                        Row(
                          children: [
                            Text(
                              '当前竞价:',
                              style: TextStyle(
                                fontSize: 14.sp,
                                color: Colors.grey[600],
                              ),
                            ),
                            SizedBox(width: 8.w),
                            Text(
                              '¥${_getCurrentPrice()}',
                              style: TextStyle(
                                fontSize: 24.sp,
                                color: Colors.red,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Spacer(),
                            GestureDetector(
                              onTap: () => _showBidHistory(),
                              child: Text(
                                '查看详情',
                                style: TextStyle(
                                  fontSize: 14.sp,
                                  color: Colors.blue,
                                ),
                              ),
                            ),
                          ],
                        ),
                        SizedBox(height: 8.h),
                        Text(
                          '加价幅度不低于: ¥8',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: Colors.grey[600],
                          ),
                        ),
                        SizedBox(height: 16.h),
                        _buildAuctionStatusRow(),
                      ],
                    ),
                  ),

                  SizedBox(height: 24.h),

                  // Bid History
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16.w),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '竞拍记录',
                          style: TextStyle(
                            fontSize: 16.sp,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        SizedBox(height: 12.h),
                        if (_isLoadingBids)
                          Center(child: CircularProgressIndicator())
                        else if (_bidHistory.isEmpty)
                          Text(
                            '暂无竞拍记录',
                            style: TextStyle(
                              fontSize: 14.sp,
                              color: Colors.grey[500],
                            ),
                          )
                        else
                          ..._bidHistory.take(3)
                            .map((bid) => Container(
                                  padding: EdgeInsets.symmetric(vertical: 8.h),
                                  child: Row(
                                    children: [
                                      CircleAvatar(
                                        radius: 16.w,
                                        child: Text(
                                          bid.user?.nickname?.substring(0, 1) ?? '?',
                                          style: TextStyle(fontSize: 12.sp),
                                        ),
                                      ),
                                      SizedBox(width: 12.w),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              bid.user?.nickname ?? '匿名用户',
                                              style: TextStyle(
                                                fontSize: 14.sp,
                                                fontWeight: FontWeight.w500,
                                              ),
                                            ),
                                            Text(
                                              '出价 ¥${bid.bidAmount.toStringAsFixed(0)}',
                                              style: TextStyle(
                                                fontSize: 12.sp,
                                                color: Colors.grey[600],
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                      Text(
                                        '${bid.bidTime.hour.toString().padLeft(2, '0')}:${bid.bidTime.minute.toString().padLeft(2, '0')}',
                                        style: TextStyle(
                                          fontSize: 12.sp,
                                          color: Colors.grey[500],
                                        ),
                                      ),
                                    ],
                                  ),
                                ))
                            .toList(),
                      ],
                    ),
                  ),

                  SizedBox(height: 100.h),
                ],
              ),
            ),
          ),

          // Bottom Action Bar
          Container(
            padding: EdgeInsets.all(16.w),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: SafeArea(
              child: Row(
                children: [
                  GestureDetector(
                    onTap: () => _showChatDialog(),
                    child: Container(
                      padding: EdgeInsets.symmetric(
                          horizontal: 24.w, vertical: 12.h),
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.purple),
                        borderRadius: BorderRadius.circular(20.w),
                      ),
                      child: Text(
                        '咨询',
                        style: TextStyle(
                          color: Colors.purple,
                          fontSize: 14.sp,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: _buildActionButton(),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton() {
    if (_isLoadingAuctionStatus) {
      return Container(
        padding: EdgeInsets.symmetric(vertical: 16.h),
        decoration: BoxDecoration(
          color: Colors.grey,
          borderRadius: BorderRadius.circular(25.w),
        ),
        child: Center(
          child: SizedBox(
            width: 20.w,
            height: 20.h,
            child: const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              strokeWidth: 2,
            ),
          ),
        ),
      );
    }

    // 检查拍卖状态
    final isEnded = _auctionStatus?['is_ended'] ?? false;
    final status = _auctionStatus?['status'] ?? 2;

    if (isEnded && _isWinner) {
      // 拍卖已结束且用户中标，显示创建订单按钮
      return GestureDetector(
        onTap: _goToWinnerOrder,
        child: Container(
          padding: EdgeInsets.symmetric(vertical: 16.h),
          decoration: BoxDecoration(
            color: AppColors.success,
            borderRadius: BorderRadius.circular(25.w),
          ),
          child: Center(
            child: Text(
              '恭喜中标！立即下单',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16.sp,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
      );
    } else if (isEnded) {
      // 拍卖已结束但用户未中标
      return Container(
        padding: EdgeInsets.symmetric(vertical: 16.h),
        decoration: BoxDecoration(
          color: Colors.grey,
          borderRadius: BorderRadius.circular(25.w),
        ),
        child: Center(
          child: Text(
            '拍卖已结束',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16.sp,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      );
    } else if (status == 2) {
      // 拍卖进行中，显示出价按钮
      return GestureDetector(
        onTap: () => _showBiddingDialog(),
        child: Container(
          padding: EdgeInsets.symmetric(vertical: 16.h),
          decoration: BoxDecoration(
            color: Colors.purple,
            borderRadius: BorderRadius.circular(25.w),
          ),
          child: Center(
            child: Text(
              '我要出价',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16.sp,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
      );
    } else {
      // 其他状态（待审核、已下架等）
      return Container(
        padding: EdgeInsets.symmetric(vertical: 16.h),
        decoration: BoxDecoration(
          color: Colors.grey,
          borderRadius: BorderRadius.circular(25.w),
        ),
        child: Center(
          child: Text(
            '暂不可出价',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16.sp,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      );
    }
  }

  Widget _buildAuctionStatusRow() {
    if (_auctionStatus == null) {
      return Row(
        children: [
          const Icon(
            Icons.star,
            color: Colors.orange,
            size: 16,
          ),
          SizedBox(width: 4.w),
          Text(
            '竞拍火热，加价谨慎',
            style: TextStyle(
              fontSize: 12.sp,
              color: Colors.grey[600],
            ),
          ),
        ],
      );
    }

    final isEnded = _auctionStatus!['is_ended'] ?? false;
    final endTime = _auctionStatus!['end_time'] as String?;
    final bidCount = _auctionStatus!['bid_count'] ?? 0;

    if (isEnded) {
      return Row(
        children: [
          const Icon(
            Icons.gavel,
            color: Colors.red,
            size: 16,
          ),
          SizedBox(width: 4.w),
          Text(
            _isWinner ? '恭喜中标！' : '拍卖已结束',
            style: TextStyle(
              fontSize: 12.sp,
              color: _isWinner ? AppColors.success : Colors.grey[600],
              fontWeight: _isWinner ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          SizedBox(width: 8.w),
          Text(
            '共 $bidCount 次出价',
            style: TextStyle(
              fontSize: 12.sp,
              color: Colors.grey[500],
            ),
          ),
        ],
      );
    } else if (endTime != null) {
      final timeRemaining =
          _auctionService.calculateTimeRemaining(DateTime.parse(endTime));
      final timeText = _auctionService.formatTimeRemaining(timeRemaining);

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.access_time,
                color: Colors.orange,
                size: 16,
              ),
              SizedBox(width: 4.w),
              Text(
                '剩余时间: $timeText',
                style: TextStyle(
                  fontSize: 12.sp,
                  color: Colors.orange,
                  fontWeight: FontWeight.w500,
                ),
              ),
              SizedBox(width: 8.w),
              Text(
                '共 $bidCount 次出价',
                style: TextStyle(
                  fontSize: 12.sp,
                  color: Colors.grey[500],
                ),
              ),
            ],
          ),
          if (_isWinner) ...[
            SizedBox(height: 4.h),
            Text(
              '您当前领先',
              style: TextStyle(
                fontSize: 12.sp,
                color: AppColors.success,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ],
      );
    } else {
      return Row(
        children: [
          const Icon(
            Icons.star,
            color: Colors.orange,
            size: 16,
          ),
          SizedBox(width: 4.w),
          Text(
            '竞拍火热，加价谨慎',
            style: TextStyle(
              fontSize: 12.sp,
              color: Colors.grey[600],
            ),
          ),
        ],
      );
    }
  }

  void _goToWinnerOrder() {
    final productIdRaw = widget.productData?['id'] ?? 1;
    final productId = productIdRaw is String
        ? int.tryParse(productIdRaw) ?? 1
        : productIdRaw as int;
    final productTitle = widget.productData?['title'] ?? '商品';
    final winningAmount = _auctionStatus?['current_price'] ?? '0';
    final productImages = widget.productData?['images'] as List?;

    Get.toNamed(
      AppRoutes.auctionWinnerOrder,
      arguments: {
        'product_id': productId,
        'product_title': productTitle,
        'winning_amount': winningAmount,
        'product_image':
            productImages?.isNotEmpty == true ? productImages![0] : null,
      },
    );
  }

  void _showServiceGuarantee() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.8,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20.w),
            topRight: Radius.circular(20.w),
          ),
        ),
        child: Column(
          children: [
            Container(
              padding: EdgeInsets.all(20.w),
              decoration: BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: Colors.grey.shade200),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.security,
                    color: Colors.purple,
                    size: 24.w,
                  ),
                  SizedBox(width: 8.w),
                  Text(
                    '平台保障',
                    style: TextStyle(
                      fontSize: 18.sp,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Spacer(),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: Icon(Icons.close),
                  ),
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.all(20.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '放心参拍，售后无忧，宠物通义为您保驾护航',
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: Colors.grey[600],
                      ),
                    ),
                    SizedBox(height: 24.h),
                    _buildGuaranteeItem(
                      icon: Icons.assignment_return,
                      title: '无理由退货退款',
                      subtitle: '在符合无理由退货标准的情况下可申请无理由退货',
                      description: '特别注意：无实际责任的门费不支持退货退款。',
                    ),
                    _buildGuaranteeItem(
                      icon: Icons.local_shipping,
                      title: '包邮',
                      subtitle: '全平台所有商品，非偏远地区包邮发货发货家(新疆、西藏地区',
                      description: '需要补运费35-50元费用)',
                    ),
                    _buildGuaranteeItem(
                      icon: Icons.search,
                      title: '商品审核',
                      subtitle: '平台审核部审核动品，售后售后且均受到放心心保障',
                      description: '',
                    ),
                    _buildGuaranteeItem(
                      icon: Icons.verified,
                      title: '拍宠有道官方认定',
                      subtitle: '本商品已被拍宠有道官方认定，已购买保险，请放心心拍',
                      description: '',
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

  Widget _buildGuaranteeItem({
    required IconData icon,
    required String title,
    required String subtitle,
    required String description,
  }) {
    return Container(
      margin: EdgeInsets.only(bottom: 24.h),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(8.w),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: Colors.grey[600], size: 20.w),
              SizedBox(width: 12.w),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                color: Colors.grey[400],
                size: 12.w,
              ),
            ],
          ),
          if (subtitle.isNotEmpty) ...[
            SizedBox(height: 8.h),
            Text(
              subtitle,
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.grey[700],
              ),
            ),
          ],
          if (description.isNotEmpty) ...[
            SizedBox(height: 4.h),
            Text(
              description,
              style: TextStyle(
                fontSize: 12.sp,
                color: Colors.grey[500],
              ),
            ),
          ],
        ],
      ),
    );
  }

  void _showBiddingDialog() {
    final currentPrice = double.tryParse(_getCurrentPrice()) ?? 0;
    final minIncrement =
        double.tryParse(_auctionStatus?['min_increment']?.toString() ?? '10') ??
            10;
    final productTitle = widget.productData?['title'] ?? '商品';
    final productImages = widget.productData?['images'] as List?;
    final productImage =
        productImages?.isNotEmpty == true ? productImages!.first : null;

    // 建议出价金额
    final suggestedBid1 = currentPrice + minIncrement;
    final suggestedBid2 = currentPrice + (minIncrement * 2);
    final suggestedBid3 = currentPrice + (minIncrement * 3);

    String selectedBidAmount = '';

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => Container(
          height: MediaQuery.of(context).size.height * 0.7,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(20.w),
              topRight: Radius.circular(20.w),
            ),
          ),
          child: Column(
            children: [
              // 头部 - 商品信息
              Container(
                padding: EdgeInsets.all(20.w),
                decoration: BoxDecoration(
                  border: Border(
                    bottom: BorderSide(color: Colors.grey.shade200),
                  ),
                ),
                child: Row(
                  children: [
                    // 商品图片
                    Container(
                      width: 60.w,
                      height: 60.w,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8.w),
                        color: Colors.grey[200],
                      ),
                      child: productImage != null
                          ? ClipRRect(
                              borderRadius: BorderRadius.circular(8.w),
                              child: Image.network(
                                productImage,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) =>
                                    Icon(Icons.pets, color: Colors.grey),
                              ),
                            )
                          : Icon(Icons.pets, color: Colors.grey),
                    ),
                    SizedBox(width: 12.w),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            productTitle,
                            style: TextStyle(
                              fontSize: 14.sp,
                              fontWeight: FontWeight.w500,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          SizedBox(height: 4.h),
                          Container(
                            padding: EdgeInsets.symmetric(
                                horizontal: 6.w, vertical: 2.h),
                            decoration: BoxDecoration(
                              color: Colors.orange,
                              borderRadius: BorderRadius.circular(2.w),
                            ),
                            child: Text(
                              '包邮',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 10.sp,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: Icon(Icons.close),
                    ),
                  ],
                ),
              ),

              // 中间 - 出价区域
              Expanded(
                child: Padding(
                  padding: EdgeInsets.all(20.w),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 当前竞价
                      Row(
                        children: [
                          Text(
                            '当前竞价:',
                            style: TextStyle(
                              fontSize: 16.sp,
                              color: Colors.grey[600],
                            ),
                          ),
                          SizedBox(width: 8.w),
                          Text(
                            '¥${currentPrice.toStringAsFixed(0)}',
                            style: TextStyle(
                              fontSize: 24.sp,
                              color: Colors.red,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 8.h),
                      Text(
                        '最低加价幅度 ¥${minIncrement.toStringAsFixed(0)}',
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: Colors.grey[600],
                        ),
                      ),
                      SizedBox(height: 24.h),

                      // 警告信息
                      Row(
                        children: [
                          Icon(
                            Icons.warning,
                            color: Colors.orange,
                            size: 16.w,
                          ),
                          SizedBox(width: 8.w),
                          Text(
                            '竞拍火热，请谨慎出价',
                            style: TextStyle(
                              fontSize: 12.sp,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),

                      SizedBox(height: 24.h),

                      // 建议出价按钮
                      Row(
                        children: [
                          Expanded(
                            child: GestureDetector(
                              onTap: () => setModalState(() =>
                                  selectedBidAmount =
                                      suggestedBid1.toStringAsFixed(0)),
                              child: Container(
                                padding: EdgeInsets.symmetric(vertical: 12.h),
                                decoration: BoxDecoration(
                                  border: Border.all(
                                    color: selectedBidAmount ==
                                            suggestedBid1.toStringAsFixed(0)
                                        ? Colors.red
                                        : Colors.grey.shade300,
                                  ),
                                  borderRadius: BorderRadius.circular(6.w),
                                ),
                                child: Center(
                                  child: Text(
                                    '¥${suggestedBid1.toStringAsFixed(0)}',
                                    style: TextStyle(
                                      color: selectedBidAmount ==
                                              suggestedBid1.toStringAsFixed(0)
                                          ? Colors.red
                                          : Colors.black,
                                      fontSize: 14.sp,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                          SizedBox(width: 12.w),
                          Expanded(
                            child: GestureDetector(
                              onTap: () => setModalState(() =>
                                  selectedBidAmount =
                                      suggestedBid2.toStringAsFixed(0)),
                              child: Container(
                                padding: EdgeInsets.symmetric(vertical: 12.h),
                                decoration: BoxDecoration(
                                  border: Border.all(
                                    color: selectedBidAmount ==
                                            suggestedBid2.toStringAsFixed(0)
                                        ? Colors.red
                                        : Colors.grey.shade300,
                                  ),
                                  borderRadius: BorderRadius.circular(6.w),
                                ),
                                child: Center(
                                  child: Text(
                                    '¥${suggestedBid2.toStringAsFixed(0)}',
                                    style: TextStyle(
                                      color: selectedBidAmount ==
                                              suggestedBid2.toStringAsFixed(0)
                                          ? Colors.red
                                          : Colors.black,
                                      fontSize: 14.sp,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                          SizedBox(width: 12.w),
                          Expanded(
                            child: GestureDetector(
                              onTap: () => setModalState(() =>
                                  selectedBidAmount =
                                      suggestedBid3.toStringAsFixed(0)),
                              child: Container(
                                padding: EdgeInsets.symmetric(vertical: 12.h),
                                decoration: BoxDecoration(
                                  border: Border.all(
                                    color: selectedBidAmount ==
                                            suggestedBid3.toStringAsFixed(0)
                                        ? Colors.red
                                        : Colors.grey.shade300,
                                  ),
                                  borderRadius: BorderRadius.circular(6.w),
                                ),
                                child: Center(
                                  child: Text(
                                    '¥${suggestedBid3.toStringAsFixed(0)}',
                                    style: TextStyle(
                                      color: selectedBidAmount ==
                                              suggestedBid3.toStringAsFixed(0)
                                          ? Colors.red
                                          : Colors.black,
                                      fontSize: 14.sp,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),

                      SizedBox(height: 16.h),

                      // 自定义出价输入框
                      TextField(
                        controller: _bidController,
                        keyboardType: TextInputType.number,
                        onChanged: (value) =>
                            setModalState(() => selectedBidAmount = value),
                        decoration: InputDecoration(
                          labelText: '自定义出价',
                          hintText: '请输入出价金额',
                          prefixText: '¥',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(6.w),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // 底部 - 确认按钮
              Container(
                padding: EdgeInsets.all(20.w),
                child: Column(
                  children: [
                    GestureDetector(
                      onTap: _isLoadingBids
                          ? null
                          : () async {
                              final bidAmountStr = selectedBidAmount.isNotEmpty
                                  ? selectedBidAmount
                                  : _bidController.text.trim();
                              final bidAmount = double.tryParse(bidAmountStr);

                              if (bidAmount == null ||
                                  bidAmount <= currentPrice) {
                                Get.snackbar(
                                  '出价无效',
                                  '出价必须高于当前竞价 ¥${currentPrice.toStringAsFixed(0)}',
                                  backgroundColor: AppColors.error,
                                  colorText: Colors.white,
                                );
                                return;
                              }

                              if (bidAmount < currentPrice + minIncrement) {
                                Get.snackbar(
                                  '出价无效',
                                  '出价必须至少高出 ¥${minIncrement.toStringAsFixed(0)}',
                                  backgroundColor: AppColors.error,
                                  colorText: Colors.white,
                                );
                                return;
                              }

                              await _placeBid(bidAmount);
                            },
                      child: Container(
                        width: double.infinity,
                        padding: EdgeInsets.symmetric(vertical: 16.h),
                        decoration: BoxDecoration(
                          color: _isLoadingBids ? Colors.grey : Colors.purple,
                          borderRadius: BorderRadius.circular(25.w),
                        ),
                        child: Center(
                          child: _isLoadingBids
                              ? SizedBox(
                                  width: 20.w,
                                  height: 20.w,
                                  child: CircularProgressIndicator(
                                      color: Colors.white, strokeWidth: 2),
                                )
                              : Text(
                                  '确定出价',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 16.sp,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                        ),
                      ),
                    ),
                    SizedBox(height: 12.h),
                    Row(
                      children: [
                        Icon(
                          Icons.check_circle,
                          color: Colors.purple,
                          size: 16.w,
                        ),
                        SizedBox(width: 8.w),
                        Text(
                          '出价后不可撤销，请谨慎操作',
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
            ],
          ),
        ),
      ),
    );
  }

  void _showChatDialog() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatPage(),
      ),
    );
  }

  void _showBidHistory() {
    // 刷新竞拍记录
    _loadBidHistory();
    
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.6,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20.w),
            topRight: Radius.circular(20.w),
          ),
        ),
        child: Column(
          children: [
            Container(
              padding: EdgeInsets.all(20.w),
              decoration: BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: Colors.grey.shade200),
                ),
              ),
              child: Row(
                children: [
                  Text(
                    '出价记录',
                    style: TextStyle(
                      fontSize: 18.sp,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Spacer(),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: Icon(Icons.close),
                  ),
                ],
              ),
            ),
            Expanded(
              child: _isLoadingBids 
                ? Center(child: CircularProgressIndicator())
                : _bidHistory.isEmpty
                ? Center(
                    child: Text(
                      '暂无竞拍记录',
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: Colors.grey[500],
                      ),
                    ),
                  )
                : ListView.builder(
                    padding: EdgeInsets.all(16.w),
                    itemCount: _bidHistory.length,
                    itemBuilder: (context, index) {
                      final bid = _bidHistory[index];
                      return Container(
                        padding: EdgeInsets.symmetric(vertical: 12.h),
                        decoration: BoxDecoration(
                          border: Border(
                            bottom: BorderSide(color: Colors.grey.shade200),
                          ),
                        ),
                        child: Row(
                          children: [
                            CircleAvatar(
                              radius: 20.w,
                              child: Text(
                                bid.user?.nickname?.substring(0, 1) ?? '?',
                                style: TextStyle(fontSize: 14.sp),
                              ),
                            ),
                            SizedBox(width: 12.w),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    bid.user?.nickname ?? '匿名用户',
                                    style: TextStyle(
                                      fontSize: 16.sp,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                  SizedBox(height: 4.h),
                                  Text(
                                    '出价时间: ${bid.bidTime.month}月${bid.bidTime.day}日 ${bid.bidTime.hour.toString().padLeft(2, '0')}:${bid.bidTime.minute.toString().padLeft(2, '0')}',
                                    style: TextStyle(
                                      fontSize: 12.sp,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Text(
                              '¥${bid.bidAmount.toStringAsFixed(0)}',
                              style: TextStyle(
                                fontSize: 18.sp,
                                color: Colors.red,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class ChatPage extends StatefulWidget {
  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> messages = [
    {
      'isUser': false,
      'message': '发什么快递呀',
      'time': '23:44',
      'status': '已读',
    },
    {
      'isUser': true,
      'message': '都可以的亲',
      'time': '23:45',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: Colors.black, size: 20.w),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          '招财猫旺财狗',
          style: TextStyle(
            color: Colors.black,
            fontSize: 16.sp,
            fontWeight: FontWeight.w500,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {},
            child: Text(
              '进店',
              style: TextStyle(
                color: Colors.blue,
                fontSize: 14.sp,
              ),
            ),
          ),
          SizedBox(width: 16.w),
        ],
      ),
      body: Column(
        children: [
          // Product Info Header
          Container(
            padding: EdgeInsets.all(16.w),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              border: Border(
                bottom: BorderSide(color: Colors.grey.shade200),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 60.w,
                  height: 60.w,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8.w),
                    image: const DecorationImage(
                      image: AssetImage('assets/images/aquarium1.jpg'),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                SizedBox(width: 12.w),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '宠物标题宠物标题宠物标题宠物标...',
                        style: TextStyle(
                          fontSize: 14.sp,
                          fontWeight: FontWeight.w500,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      SizedBox(height: 4.h),
                      Container(
                        padding: EdgeInsets.symmetric(
                            horizontal: 6.w, vertical: 2.h),
                        decoration: BoxDecoration(
                          color: Colors.orange,
                          borderRadius: BorderRadius.circular(2.w),
                        ),
                        child: Text(
                          '包邮',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 10.sp,
                          ),
                        ),
                      ),
                      SizedBox(height: 4.h),
                      Text(
                        '¥432',
                        style: TextStyle(
                          fontSize: 16.sp,
                          color: Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                TextButton(
                  onPressed: () {},
                  child: Text(
                    '查看详情',
                    style: TextStyle(
                      color: Colors.blue,
                      fontSize: 12.sp,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Messages
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.all(16.w),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final message = messages[index];
                final isUser = message['isUser'] as bool;

                return Container(
                  margin: EdgeInsets.only(bottom: 16.h),
                  child: Column(
                    children: [
                      Text(
                        message['time'],
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: Colors.grey[500],
                        ),
                      ),
                      SizedBox(height: 8.h),
                      Row(
                        mainAxisAlignment: isUser
                            ? MainAxisAlignment.end
                            : MainAxisAlignment.start,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (!isUser) ...[
                            CircleAvatar(
                              radius: 16.w,
                              backgroundImage:
                                  const AssetImage('assets/images/avatar1.jpg'),
                            ),
                            SizedBox(width: 8.w),
                          ],
                          Flexible(
                            child: Container(
                              padding: EdgeInsets.symmetric(
                                  horizontal: 12.w, vertical: 8.h),
                              decoration: BoxDecoration(
                                color:
                                    isUser ? Colors.purple : Colors.grey[200],
                                borderRadius: BorderRadius.circular(8.w),
                              ),
                              child: Text(
                                message['message'],
                                style: TextStyle(
                                  fontSize: 14.sp,
                                  color: isUser ? Colors.white : Colors.black,
                                ),
                              ),
                            ),
                          ),
                          if (isUser) ...[
                            SizedBox(width: 8.w),
                            CircleAvatar(
                              radius: 16.w,
                              backgroundImage:
                                  const AssetImage('assets/images/avatar2.jpg'),
                            ),
                          ],
                        ],
                      ),
                      if (message['status'] != null) ...[
                        SizedBox(height: 4.h),
                        Text(
                          message['status'],
                          style: TextStyle(
                            fontSize: 10.sp,
                            color: Colors.grey[500],
                          ),
                        ),
                      ],
                    ],
                  ),
                );
              },
            ),
          ),

          // Message Input
          Container(
            padding: EdgeInsets.all(16.w),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border(
                top: BorderSide(color: Colors.grey.shade200),
              ),
            ),
            child: SafeArea(
              child: Row(
                children: [
                  IconButton(
                    onPressed: () {},
                    icon: Icon(
                      Icons.keyboard_voice,
                      size: 24.w,
                    ),
                  ),
                  Expanded(
                    child: Container(
                      padding: EdgeInsets.symmetric(horizontal: 12.w),
                      decoration: BoxDecoration(
                        color: Colors.grey[100],
                        borderRadius: BorderRadius.circular(20.w),
                      ),
                      child: TextField(
                        controller: _messageController,
                        decoration: const InputDecoration(
                          border: InputBorder.none,
                          hintText: '请输入消息...',
                        ),
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () {},
                    icon: Icon(
                      Icons.sentiment_satisfied_alt,
                      size: 24.w,
                    ),
                  ),
                  IconButton(
                    onPressed: () {},
                    icon: Icon(
                      Icons.add,
                      size: 24.w,
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
}
