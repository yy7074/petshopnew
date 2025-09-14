import 'package:dio/dio.dart';
import '../models/chat.dart';
import 'api_service.dart';
import 'auth_service.dart';

class ChatService {
  final ApiService _apiService = ApiService();

  // 发送商品咨询
  Future<ApiResult<ConsultationResponse>> sendProductConsultation({
    required int productId,
    required int sellerId,
    required String message,
  }) async {
    try {
      final response = await _apiService.post('/chat/consult', data: {
        'product_id': productId,
        'seller_id': sellerId,
        'message': message,
      });
      
      if (response.statusCode == 200) {
        final result = ConsultationResponse.fromJson(response.data);
        return ApiResult.success(result);
      } else {
        return ApiResult.error(response.data['detail'] ?? '咨询发送失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取对话列表
  Future<ApiResult<ConversationListResponse>> getConversations({
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final response = await _apiService.get('/chat/conversations', queryParameters: {
        'page': page,
        'page_size': pageSize,
      });
      
      if (response.statusCode == 200) {
        final result = ConversationListResponse.fromJson(response.data);
        return ApiResult.success(result);
      } else {
        return ApiResult.error(response.data['detail'] ?? '获取对话列表失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取对话详情
  Future<ApiResult<ConversationDetail>> getConversation(int conversationId) async {
    try {
      final response = await _apiService.get('/chat/conversations/$conversationId');
      
      if (response.statusCode == 200) {
        final result = ConversationDetail.fromJson(response.data);
        return ApiResult.success(result);
      } else {
        return ApiResult.error(response.data['detail'] ?? '获取对话详情失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取对话消息列表
  Future<ApiResult<MessageListResponse>> getConversationMessages({
    required int conversationId,
    int page = 1,
    int pageSize = 50,
  }) async {
    try {
      final response = await _apiService.get(
        '/chat/conversations/$conversationId/messages',
        queryParameters: {
          'page': page,
          'page_size': pageSize,
        },
      );
      
      if (response.statusCode == 200) {
        final result = MessageListResponse.fromJson(response.data);
        return ApiResult.success(result);
      } else {
        return ApiResult.error(response.data['detail'] ?? '获取消息列表失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 发送消息
  Future<ApiResult<ChatMessage>> sendMessage({
    required int conversationId,
    required String content,
    String messageType = 'text',
  }) async {
    try {
      final response = await _apiService.post('/chat/conversations/$conversationId/messages', data: {
        'content': content,
        'message_type': messageType,
      });
      
      if (response.statusCode == 200) {
        final result = ChatMessage.fromJson(response.data);
        return ApiResult.success(result);
      } else {
        return ApiResult.error(response.data['detail'] ?? '消息发送失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 直接发送消息（创建对话）
  Future<ApiResult<ChatMessage>> sendDirectMessage({
    required int receiverId,
    required String content,
    String messageType = 'text',
  }) async {
    try {
      final response = await _apiService.post('/chat/messages', data: {
        'receiver_id': receiverId,
        'content': content,
        'message_type': messageType,
      });
      
      if (response.statusCode == 200) {
        final result = ChatMessage.fromJson(response.data);
        return ApiResult.success(result);
      } else {
        return ApiResult.error(response.data['detail'] ?? '消息发送失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 标记对话消息为已读
  Future<ApiResult<String>> markConversationAsRead(int conversationId) async {
    try {
      final response = await _apiService.put('/chat/conversations/$conversationId/read');
      
      if (response.statusCode == 200) {
        return ApiResult.success(response.data['message'] ?? '标记成功');
      } else {
        return ApiResult.error(response.data['detail'] ?? '标记失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取未读消息数量
  Future<ApiResult<int>> getUnreadCount() async {
    try {
      final response = await _apiService.get('/chat/unread-count');
      
      if (response.statusCode == 200) {
        return ApiResult.success(response.data['count'] ?? 0);
      } else {
        return ApiResult.error(response.data['detail'] ?? '获取未读数量失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 删除对话
  Future<ApiResult<String>> deleteConversation(int conversationId) async {
    try {
      final response = await _apiService.delete('/chat/conversations/$conversationId');
      
      if (response.statusCode == 200) {
        return ApiResult.success(response.data['message'] ?? '删除成功');
      } else {
        return ApiResult.error(response.data['detail'] ?? '删除失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 搜索消息
  Future<ApiResult<MessageListResponse>> searchMessages({
    required String keyword,
    int? conversationId,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'keyword': keyword,
        'page': page,
        'page_size': pageSize,
      };
      
      if (conversationId != null) {
        queryParams['conversation_id'] = conversationId;
      }

      final response = await _apiService.get('/chat/search', queryParameters: queryParams);
      
      if (response.statusCode == 200) {
        final result = MessageListResponse.fromJson(response.data);
        return ApiResult.success(result);
      } else {
        return ApiResult.error(response.data['detail'] ?? '搜索失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 错误处理
  String _handleError(DioException error) {
    if (error.response?.data != null) {
      final data = error.response!.data;
      if (data is Map<String, dynamic>) {
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

    if (error.response?.statusCode == 404) {
      return '资源不存在';
    } else if (error.response?.statusCode == 403) {
      return '无权限访问';
    } else if (error.response?.statusCode == 401) {
      return '请先登录';
    } else if (error.type == DioExceptionType.connectionTimeout ||
               error.type == DioExceptionType.receiveTimeout) {
      return '网络连接超时，请检查网络';
    } else if (error.type == DioExceptionType.unknown) {
      return '网络连接失败，请检查网络';
    } else {
      return '请求失败，请稍后重试';
    }
  }
}