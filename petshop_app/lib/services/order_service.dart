import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants/api_constants.dart';
import 'storage_service.dart';

class OrderService {
  static const String baseUrl = ApiConstants.baseUrl;

  // 获取订单列表
  static Future<Map<String, dynamic>> getOrders({
    int page = 1,
    int pageSize = 20,
    String? status,
    String? orderType = 'buy', // buy: 我买进的, sell: 我卖出的
    String? startDate,
    String? endDate,
  }) async {
    try {
      final token = StorageService.getUserToken();
      if (token == null || token.isEmpty) {
        throw Exception('请先登录');
      }

      // 构建查询参数
      final queryParams = <String, String>{
        'page': page.toString(),
        'page_size': pageSize.toString(),
      };

      if (status != null && status.isNotEmpty) {
        queryParams['status'] = status;
      }
      if (orderType != null && orderType.isNotEmpty) {
        queryParams['order_type'] = orderType;
      }
      if (startDate != null && startDate.isNotEmpty) {
        queryParams['start_date'] = startDate;
      }
      if (endDate != null && endDate.isNotEmpty) {
        queryParams['end_date'] = endDate;
      }

      final uri =
          Uri.parse('$baseUrl/orders').replace(queryParameters: queryParams);

      final response = await http.get(
        uri,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? '获取订单列表失败');
      }
    } catch (e) {
      throw Exception('网络错误: $e');
    }
  }

  // 获取订单详情
  static Future<Map<String, dynamic>> getOrderDetail(int orderId) async {
    try {
      final token = StorageService.getUserToken();
      if (token == null || token.isEmpty) {
        throw Exception('请先登录');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/orders/$orderId'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? '获取订单详情失败');
      }
    } catch (e) {
      throw Exception('网络错误: $e');
    }
  }

  // 取消订单
  static Future<Map<String, dynamic>> cancelOrder(
      int orderId, String reason) async {
    try {
      final token = StorageService.getUserToken();
      if (token == null || token.isEmpty) {
        throw Exception('请先登录');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/orders/$orderId/cancel'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'reason': reason,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? '取消订单失败');
      }
    } catch (e) {
      throw Exception('网络错误: $e');
    }
  }

  // 确认收货
  static Future<Map<String, dynamic>> confirmReceived(int orderId) async {
    try {
      final token = StorageService.getUserToken();
      if (token == null || token.isEmpty) {
        throw Exception('请先登录');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/orders/$orderId/confirm-received'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? '确认收货失败');
      }
    } catch (e) {
      throw Exception('网络错误: $e');
    }
  }

  // 申请退款
  static Future<Map<String, dynamic>> applyRefund(
      int orderId, String reason) async {
    try {
      final token = StorageService.getUserToken();
      if (token == null || token.isEmpty) {
        throw Exception('请先登录');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/orders/$orderId/apply-refund'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'reason': reason,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? '申请退款失败');
      }
    } catch (e) {
      throw Exception('网络错误: $e');
    }
  }

  // 获取物流信息
  static Future<Map<String, dynamic>> getLogistics(int orderId) async {
    try {
      final token = StorageService.getUserToken();
      if (token == null || token.isEmpty) {
        throw Exception('请先登录');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/orders/$orderId/logistics'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? '获取物流信息失败');
      }
    } catch (e) {
      throw Exception('网络错误: $e');
    }
  }

  // 支付订单
  static Future<Map<String, dynamic>> payOrder(
      int orderId, String paymentMethod) async {
    try {
      final token = StorageService.getUserToken();
      if (token == null || token.isEmpty) {
        throw Exception('请先登录');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/orders/$orderId/pay'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'payment_method': paymentMethod,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? '支付失败');
      }
    } catch (e) {
      throw Exception('网络错误: $e');
    }
  }

  // 获取订单状态文本
  static String getStatusText(String status) {
    switch (status) {
      case 'pending':
        return '待付款';
      case 'paid':
        return '待发货';
      case 'shipped':
        return '待收货';
      case 'delivered':
        return '已送达';
      case 'completed':
        return '已完成';
      case 'cancelled':
        return '已取消';
      case 'refunded':
        return '已退款';
      default:
        return '未知状态';
    }
  }

  // 获取订单状态颜色
  static String getStatusColor(String status) {
    switch (status) {
      case 'pending':
        return '#FFA500'; // 橙色
      case 'paid':
        return '#2196F3'; // 蓝色
      case 'shipped':
        return '#9C27B0'; // 紫色
      case 'delivered':
        return '#4CAF50'; // 绿色
      case 'completed':
        return '#4CAF50'; // 绿色
      case 'cancelled':
        return '#757575'; // 灰色
      case 'refunded':
        return '#F44336'; // 红色
      default:
        return '#999999'; // 默认灰色
    }
  }

  // 获取订单可执行的操作
  static List<String> getOrderActions(String status) {
    switch (status) {
      case 'pending':
        return ['取消订单', '继续付款'];
      case 'paid':
        return ['联系卖家', '申请退款'];
      case 'shipped':
        return ['查看物流', '确认收货'];
      case 'delivered':
        return ['确认收货', '申请退款'];
      case 'completed':
        return ['再次购买', '评价'];
      case 'cancelled':
        return ['删除订单'];
      case 'refunded':
        return ['删除订单'];
      default:
        return [];
    }
  }
}
