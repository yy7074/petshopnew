import 'package:dio/dio.dart';
import '../models/message.dart';
import 'api_service.dart';
import 'auth_service.dart';

class ChatService {
  final ApiService _apiService = ApiService();

  // 获取对话列表
  Future<ApiResult<List<Conversation>>> getConversations({
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final response = await _apiService.get('/messages', queryParameters: {
        'page': page,
        'page_size': pageSize,
      });

      if (response.statusCode == 200) {
        final List<dynamic> conversationsJson = response.data['data']['items'] ?? [];
        final conversations = conversationsJson
            .map((json) => Conversation.fromJson(json))
            .toList();
        return ApiResult.success(conversations);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取对话列表失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取聊天记录
  Future<ApiResult<List<ChatMessage>>> getChatMessages({
    required int conversationId,
    int page = 1,
    int pageSize = 50,
  }) async {
    try {
      final response = await _apiService.get('/chat/$conversationId', queryParameters: {
        'page': page,
        'page_size': pageSize,
      });

      if (response.statusCode == 200) {
        final List<dynamic> messagesJson = response.data['data']['items'] ?? [];
        final messages = messagesJson
            .map((json) => ChatMessage.fromJson(json))
            .toList();
        return ApiResult.success(messages);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取聊天记录失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 发送消息
  Future<ApiResult<ChatMessage>> sendMessage({
    required int receiverId,
    required String content,
    String type = 'text',
  }) async {
    try {
      final response = await _apiService.post('/messages', data: {
        'receiver_id': receiverId,
        'content': content,
        'type': type,
      });

      if (response.statusCode == 200) {
        final message = ChatMessage.fromJson(response.data['data']);
        return ApiResult.success(message);
      } else {
        return ApiResult.error(response.data['message'] ?? '发送消息失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 发送聊天消息（在对话中）
  Future<ApiResult<ChatMessage>> sendChatMessage({
    required int conversationId,
    required String content,
    String type = 'text',
  }) async {
    try {
      final response = await _apiService.post('/chat/$conversationId', data: {
        'content': content,
        'type': type,
      });

      if (response.statusCode == 200) {
        final message = ChatMessage.fromJson(response.data['data']);
        return ApiResult.success(message);
      } else {
        return ApiResult.error(response.data['message'] ?? '发送消息失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 标记消息已读
  Future<ApiResult<void>> markMessageAsRead(int messageId) async {
    try {
      final response = await _apiService.put('/messages/$messageId/read');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '标记已读失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 标记对话已读
  Future<ApiResult<void>> markConversationAsRead(int conversationId) async {
    try {
      final response = await _apiService.put('/chat/$conversationId/read');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '标记已读失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 删除消息
  Future<ApiResult<void>> deleteMessage(int messageId) async {
    try {
      final response = await _apiService.delete('/messages/$messageId');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '删除消息失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 删除对话
  Future<ApiResult<void>> deleteConversation(int conversationId) async {
    try {
      final response = await _apiService.delete('/chat/$conversationId');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '删除对话失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取未读消息数量
  Future<ApiResult<int>> getUnreadCount() async {
    try {
      final response = await _apiService.get('/messages/unread-count');

      if (response.statusCode == 200) {
        final count = response.data['data']['count'] ?? 0;
        return ApiResult.success(count);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取未读消息数失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 错误处理
  String _handleError(DioException error) {
    if (error.response?.statusCode == 403) {
      return '您没有权限进行此操作';
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