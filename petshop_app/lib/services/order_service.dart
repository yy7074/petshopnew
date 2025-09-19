import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants/api_constants.dart';
import 'storage_service.dart';

class OrderService {
  static String get baseUrl => ApiConstants.baseUrl;

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

      final uri = Uri.parse('$baseUrl${ApiConstants.orders}')
          .replace(queryParameters: queryParams);

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
        Uri.parse('$baseUrl${ApiConstants.orders}/$orderId'),
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
        Uri.parse('$baseUrl${ApiConstants.orders}/$orderId/cancel'),
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
        Uri.parse('$baseUrl${ApiConstants.orders}/$orderId/confirm-received'),
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
        Uri.parse('$baseUrl${ApiConstants.orders}/$orderId/apply-refund'),
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
        Uri.parse('$baseUrl${ApiConstants.orders}/$orderId/logistics'),
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
        Uri.parse('$baseUrl${ApiConstants.orders}/$orderId/pay'),
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

  // 获取订单状态文本 - 支持数字状态
  static String getStatusText(dynamic status) {
    // 处理数字状态
    if (status is int) {
      switch (status) {
        case 1:
          return '待付款';
        case 2:
          return '待发货';
        case 3:
          return '已发货';
        case 4:
          return '已收货';
        case 5:
          return '已完成';
        case 6:
          return '已取消';
        default:
          return '未知状态';
      }
    }

    // 处理字符串状态
    String statusStr = status.toString().toLowerCase();
    switch (statusStr) {
      case 'pending':
      case '1':
        return '待付款';
      case 'paid':
      case '2':
        return '待发货';
      case 'shipped':
      case '3':
        return '已发货';
      case 'delivered':
      case '4':
        return '已收货';
      case 'completed':
      case '5':
        return '已完成';
      case 'cancelled':
      case '6':
        return '已取消';
      case 'refunded':
        return '已退款';
      default:
        return '未知状态';
    }
  }

  // 获取订单状态颜色 - 支持数字状态
  static String getStatusColor(dynamic status) {
    // 处理数字状态
    if (status is int) {
      switch (status) {
        case 1:
          return '#FFA500'; // 橙色 - 待付款
        case 2:
          return '#2196F3'; // 蓝色 - 待发货
        case 3:
          return '#9C27B0'; // 紫色 - 已发货
        case 4:
          return '#4CAF50'; // 绿色 - 已收货
        case 5:
          return '#4CAF50'; // 绿色 - 已完成
        case 6:
          return '#757575'; // 灰色 - 已取消
        default:
          return '#999999'; // 默认灰色
      }
    }

    // 处理字符串状态
    String statusStr = status.toString().toLowerCase();
    switch (statusStr) {
      case 'pending':
      case '1':
        return '#FFA500'; // 橙色
      case 'paid':
      case '2':
        return '#2196F3'; // 蓝色
      case 'shipped':
      case '3':
        return '#9C27B0'; // 紫色
      case 'delivered':
      case '4':
        return '#4CAF50'; // 绿色
      case 'completed':
      case '5':
        return '#4CAF50'; // 绿色
      case 'cancelled':
      case '6':
        return '#757575'; // 灰色
      case 'refunded':
        return '#F44336'; // 红色
      default:
        return '#999999'; // 默认灰色
    }
  }

  // 获取订单可执行的操作 - 支持数字状态
  static List<String> getOrderActions(dynamic status) {
    // 处理数字状态
    if (status is int) {
      switch (status) {
        case 1: // 待付款
          return ['取消订单', '继续付款'];
        case 2: // 待发货
          return ['联系卖家', '申请退款'];
        case 3: // 已发货
          return ['查看物流', '确认收货'];
        case 4: // 已收货
          return ['确认收货', '申请退款'];
        case 5: // 已完成
          return ['再次购买', '评价'];
        case 6: // 已取消
          return ['删除订单'];
        default:
          return [];
      }
    }

    // 处理字符串状态
    String statusStr = status.toString().toLowerCase();
    switch (statusStr) {
      case 'pending':
      case '1':
        return ['取消订单', '继续付款'];
      case 'paid':
      case '2':
        return ['联系卖家', '申请退款'];
      case 'shipped':
      case '3':
        return ['查看物流', '确认收货'];
      case 'delivered':
      case '4':
        return ['确认收货', '申请退款'];
      case 'completed':
      case '5':
        return ['再次购买', '评价'];
      case 'cancelled':
      case '6':
        return ['删除订单'];
      case 'refunded':
        return ['删除订单'];
      default:
        return [];
    }
  }

  // 创建测试订单数据
  static Future<Map<String, dynamic>> createTestOrders() async {
    try {
      final token = StorageService.getUserToken();
      if (token == null || token.isEmpty) {
        throw Exception('请先登录');
      }

      final response = await http.post(
        Uri.parse('$baseUrl${ApiConstants.orders}/test/create-multiple'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? '创建测试订单失败');
      }
    } catch (e) {
      print('创建测试订单错误: $e');
      throw Exception('网络错误: $e');
    }
  }
}
