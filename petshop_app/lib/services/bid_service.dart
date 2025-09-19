import 'package:dio/dio.dart';
import '../models/bid.dart';
import '../models/product.dart';
import '../models/user.dart';
import 'api_service.dart';
import 'auth_service.dart';

class BidService {
  final ApiService _apiService = ApiService();

  // 竞拍出价
  Future<ApiResult<Bid>> placeBid({
    required int productId,
    required double bidAmount,
  }) async {
    try {
      final response = await _apiService.post('/bids/', data: {
        'product_id': productId,
        'amount': bidAmount,
      });

      if (response.statusCode == 200) {
        final bid = Bid.fromJson(response.data);
        return ApiResult.success(bid);
      } else {
        return ApiResult.error(response.data['detail'] ?? '出价失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取商品竞拍记录
  Future<ApiResult<List<Bid>>> getProductBids({
    required int productId,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final response =
          await _apiService.get('/bids/product/$productId', queryParameters: {
        'page': page,
        'page_size': pageSize,
      });

      if (response.statusCode == 200) {
        final List<dynamic> bidsJson = response.data['items'] ?? [];
        final bids = bidsJson.map((json) => Bid.fromJson(json)).toList();
        return ApiResult.success(bids);
      } else {
        return ApiResult.error(response.data['detail'] ?? '获取竞拍记录失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取我的竞拍记录
  Future<ApiResult<List<Bid>>> getMyBids({
    int page = 1,
    int pageSize = 20,
    String? status,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };

      if (status != null) queryParams['status'] = status;

      final response =
          await _apiService.get('/bids/my', queryParameters: queryParams);

      if (response.statusCode == 200) {
        final List<dynamic> bidsJson = response.data['items'] ?? [];

        // 调试：打印原始API响应
        print('BidService API响应数据:');
        for (int i = 0; i < bidsJson.length && i < 3; i++) {
          final json = bidsJson[i];
          print(
              '  出价${i + 1}: ID=${json['id']}, status=${json['status']}, product_info=${json['product_info']}');
        }

        final bids = bidsJson.map((json) => Bid.fromJson(json)).toList();

        // 调试：打印解析后的数据
        print('解析后的Bid数据:');
        for (int i = 0; i < bids.length && i < 3; i++) {
          final bid = bids[i];
          print(
              '  出价${i + 1}: ID=${bid.id}, status=${bid.status}, product.status=${bid.product?.status}');
        }

        return ApiResult.success(bids);
      } else {
        return ApiResult.error(response.data['detail'] ?? '获取我的竞拍记录失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取用户竞拍记录
  Future<ApiResult<List<Bid>>> getUserBids({
    int page = 1,
    int pageSize = 20,
    String? status,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };

      if (status != null) queryParams['status'] = status;

      final response =
          await _apiService.get('/bids/user', queryParameters: queryParams);

      if (response.statusCode == 200) {
        final List<dynamic> bidsJson = response.data['items'] ?? [];
        final bids = bidsJson.map((json) => Bid.fromJson(json)).toList();
        return ApiResult.success(bids);
      } else {
        return ApiResult.error(response.data['detail'] ?? '获取竞拍记录失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取正在领先的竞拍
  Future<ApiResult<List<Bid>>> getWinningBids({
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final response = await _apiService.get('/bids/winning', queryParameters: {
        'page': page,
        'page_size': pageSize,
      });

      if (response.statusCode == 200) {
        final List<dynamic> bidsJson = response.data['items'] ?? [];
        final bids = bidsJson.map((json) => Bid.fromJson(json)).toList();
        return ApiResult.success(bids);
      } else {
        return ApiResult.error(response.data['detail'] ?? '获取领先竞拍失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取已中标的竞拍
  Future<ApiResult<List<Bid>>> getWonBids({
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final response = await _apiService.get('/bids/won', queryParameters: {
        'page': page,
        'page_size': pageSize,
      });

      if (response.statusCode == 200) {
        final List<dynamic> bidsJson = response.data['items'] ?? [];
        final bids = bidsJson.map((json) => Bid.fromJson(json)).toList();
        return ApiResult.success(bids);
      } else {
        return ApiResult.error(response.data['detail'] ?? '获取已中标订单失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取我的自动出价设置
  Future<ApiResult<List<AutoBid>>> getMyAutoBids({
    int page = 1,
    int pageSize = 20,
    String status = 'active',
  }) async {
    try {
      final response = await _apiService.get('/bids/auto/my', queryParameters: {
        'page': page,
        'page_size': pageSize,
        'status': status,
      });

      if (response.statusCode == 200) {
        final List<dynamic> autoBidsJson = response.data['items'] ?? [];
        final autoBids =
            autoBidsJson.map((json) => AutoBid.fromJson(json)).toList();
        return ApiResult.success(autoBids);
      } else {
        return ApiResult.error(response.data['detail'] ?? '获取自动出价失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 暂停自动出价
  Future<ApiResult<void>> pauseAutoBid(int autoBidId) async {
    try {
      final response = await _apiService.put('/bids/auto/$autoBidId/pause');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['detail'] ?? '暂停自动出价失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 恢复自动出价
  Future<ApiResult<void>> resumeAutoBid(int autoBidId) async {
    try {
      final response = await _apiService.put('/bids/auto/$autoBidId/resume');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['detail'] ?? '恢复自动出价失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 取消自动出价
  Future<ApiResult<void>> cancelAutoBid(int autoBidId) async {
    try {
      final response = await _apiService.delete('/bids/auto/$autoBidId');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['detail'] ?? '取消自动出价失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 撤销竞拍
  Future<ApiResult<void>> cancelBid(int bidId) async {
    try {
      final response = await _apiService.delete('/bids/$bidId');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '撤销竞拍失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取进行中的拍卖
  Future<ApiResult<List<Product>>> getActiveAuctions({
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final response =
          await _apiService.get('/auctions/active', queryParameters: {
        'page': page,
        'page_size': pageSize,
      });

      if (response.statusCode == 200) {
        final List<dynamic> productsJson = response.data['data']['items'] ?? [];
        final products =
            productsJson.map((json) => Product.fromJson(json)).toList();
        return ApiResult.success(products);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取拍卖列表失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取即将结束的拍卖
  Future<ApiResult<List<Product>>> getEndingAuctions({
    int limit = 10,
  }) async {
    try {
      final response =
          await _apiService.get('/auctions/ending', queryParameters: {
        'limit': limit,
      });

      if (response.statusCode == 200) {
        final List<dynamic> productsJson = response.data['data'] ?? [];
        final products =
            productsJson.map((json) => Product.fromJson(json)).toList();
        return ApiResult.success(products);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取即将结束的拍卖失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取拍卖结果
  Future<ApiResult<List<AuctionResult>>> getAuctionResults({
    int page = 1,
    int pageSize = 20,
    int? userId,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };

      if (userId != null) queryParams['user_id'] = userId;

      final response = await _apiService.get('/auctions/results',
          queryParameters: queryParams);

      if (response.statusCode == 200) {
        final List<dynamic> resultsJson = response.data['data']['items'] ?? [];
        final results =
            resultsJson.map((json) => AuctionResult.fromJson(json)).toList();
        return ApiResult.success(results);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取拍卖结果失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 设置自动竞拍
  Future<ApiResult<AutoBid>> setAutoBid({
    required int productId,
    required double maxAmount,
    required double increment,
  }) async {
    try {
      final response = await _apiService.post('/auctions/auto-bid', data: {
        'product_id': productId,
        'max_amount': maxAmount,
        'increment': increment,
      });

      if (response.statusCode == 200) {
        final autoBid = AutoBid.fromJson(response.data['data']);
        return ApiResult.success(autoBid);
      } else {
        return ApiResult.error(response.data['message'] ?? '设置自动竞拍失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 错误处理
  String _handleError(DioException error) {
    // 先尝试从响应中获取具体错误信息
    if (error.response?.data != null) {
      final data = error.response!.data;
      if (data is Map<String, dynamic>) {
        // 检查详细错误信息字段
        final detail = data['detail']?.toString();
        if (detail != null && detail.isNotEmpty) {
          return detail;
        }
        final message = data['message']?.toString();
        if (message != null && message.isNotEmpty) {
          return message;
        }
      }
    }

    // 根据状态码返回默认错误信息
    if (error.response?.statusCode == 400) {
      return '竞拍金额不符合要求';
    } else if (error.response?.statusCode == 403) {
      return '您不能竞拍自己发布的商品';
    } else if (error.response?.statusCode == 409) {
      return '竞拍已结束或商品不可竞拍';
    } else if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return '网络连接超时，请检查网络';
    } else if (error.type == DioExceptionType.unknown) {
      return '网络连接失败，请检查网络';
    } else {
      return '出价失败，请稍后重试';
    }
  }
}

// 拍卖结果模型
class AuctionResult {
  final int id;
  final int productId;
  final int? winnerId;
  final double finalPrice;
  final DateTime endTime;
  final String status;
  final Product? product;
  final User? winner;

  AuctionResult({
    required this.id,
    required this.productId,
    this.winnerId,
    required this.finalPrice,
    required this.endTime,
    required this.status,
    this.product,
    this.winner,
  });

  factory AuctionResult.fromJson(Map<String, dynamic> json) {
    return AuctionResult(
      id: json['id'] ?? 0,
      productId: json['product_id'] ?? 0,
      winnerId: json['winner_id'],
      finalPrice: (json['final_price'] ?? 0).toDouble(),
      endTime:
          DateTime.parse(json['end_time'] ?? DateTime.now().toIso8601String()),
      status: json['status'] ?? 'ended',
      product:
          json['product'] != null ? Product.fromJson(json['product']) : null,
      winner: json['winner'] != null ? User.fromJson(json['winner']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product_id': productId,
      'winner_id': winnerId,
      'final_price': finalPrice,
      'end_time': endTime.toIso8601String(),
      'status': status,
      'product': product?.toJson(),
      'winner': winner?.toJson(),
    };
  }
}
