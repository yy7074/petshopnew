import 'package:dio/dio.dart';
import '../models/order.dart';
import 'api_service.dart';
import 'auth_service.dart';

class OrderService {
  final ApiService _apiService = ApiService();

  // 创建订单
  Future<ApiResult<Order>> createOrder({
    required int productId,
    required int quantity,
    required String paymentMethod,
  }) async {
    try {
      final response = await _apiService.post('/orders', data: {
        'product_id': productId,
        'quantity': quantity,
        'payment_method': paymentMethod,
      });

      if (response.statusCode == 200) {
        final order = Order.fromJson(response.data['data']);
        return ApiResult.success(order);
      } else {
        return ApiResult.error(response.data['message'] ?? '创建订单失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取订单列表
  Future<ApiResult<List<Order>>> getOrders({
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

      final response = await _apiService.get('/orders', queryParameters: queryParams);

      if (response.statusCode == 200) {
        final List<dynamic> ordersJson = response.data['data']['items'] ?? [];
        final orders = ordersJson.map((json) => Order.fromJson(json)).toList();
        return ApiResult.success(orders);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取订单列表失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取订单详情
  Future<ApiResult<Order>> getOrderDetail(int orderId) async {
    try {
      final response = await _apiService.get('/orders/$orderId');

      if (response.statusCode == 200) {
        final order = Order.fromJson(response.data['data']);
        return ApiResult.success(order);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取订单详情失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 取消订单
  Future<ApiResult<void>> cancelOrder(int orderId) async {
    try {
      final response = await _apiService.put('/orders/$orderId/status', data: {
        'status': 'cancelled',
      });

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '取消订单失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 确认收货
  Future<ApiResult<void>> confirmOrder(int orderId) async {
    try {
      final response = await _apiService.put('/orders/$orderId/status', data: {
        'status': 'completed',
      });

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '确认收货失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 创建支付
  Future<ApiResult<Payment>> createPayment({
    required int orderId,
    required String paymentMethod,
  }) async {
    try {
      final response = await _apiService.post('/payments', data: {
        'order_id': orderId,
        'payment_method': paymentMethod,
      });

      if (response.statusCode == 200) {
        final payment = Payment.fromJson(response.data['data']);
        return ApiResult.success(payment);
      } else {
        return ApiResult.error(response.data['message'] ?? '创建支付失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 查询支付状态
  Future<ApiResult<Payment>> getPaymentStatus(int paymentId) async {
    try {
      final response = await _apiService.get('/payments/$paymentId');

      if (response.statusCode == 200) {
        final payment = Payment.fromJson(response.data['data']);
        return ApiResult.success(payment);
      } else {
        return ApiResult.error(response.data['message'] ?? '查询支付状态失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 查询物流信息
  Future<ApiResult<Logistics>> getLogistics(int orderId) async {
    try {
      final response = await _apiService.get('/logistics/$orderId');

      if (response.statusCode == 200) {
        final logistics = Logistics.fromJson(response.data['data']);
        return ApiResult.success(logistics);
      } else {
        return ApiResult.error(response.data['message'] ?? '查询物流信息失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 错误处理
  String _handleError(DioException error) {
    if (error.response?.statusCode == 400) {
      return '订单信息不正确';
    } else if (error.response?.statusCode == 409) {
      return '订单状态不允许此操作';
    } else if (error.type == DioExceptionType.connectionTimeout ||
               error.type == DioExceptionType.receiveTimeout) {
      return '网络连接超时，请检查网络';
    } else if (error.type == DioExceptionType.unknown) {
      return '网络连接失败，请检查网络';
    } else {
      return error.response?.data?['message'] ?? '操作失败';
    }
  }
}