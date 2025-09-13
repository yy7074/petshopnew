import 'user.dart';

class ChatMessage {
  final int id;
  final int senderId;
  final int receiverId;
  final String content;
  final String type;
  final bool isRead;
  final DateTime createdAt;
  final User? sender;

  ChatMessage({
    required this.id,
    required this.senderId,
    required this.receiverId,
    required this.content,
    required this.type,
    required this.isRead,
    required this.createdAt,
    this.sender,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? 0,
      senderId: json['sender_id'] ?? 0,
      receiverId: json['receiver_id'] ?? 0,
      content: json['content'] ?? '',
      type: json['type'] ?? 'text',
      isRead: json['is_read'] ?? false,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      sender: json['sender'] != null ? User.fromJson(json['sender']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sender_id': senderId,
      'receiver_id': receiverId,
      'content': content,
      'type': type,
      'is_read': isRead,
      'created_at': createdAt.toIso8601String(),
      'sender': sender?.toJson(),
    };
  }
}

class Conversation {
  final int id;
  final int userId1;
  final int userId2;
  final ChatMessage? lastMessage;
  final int unreadCount;
  final DateTime updatedAt;
  final User? otherUser;

  Conversation({
    required this.id,
    required this.userId1,
    required this.userId2,
    this.lastMessage,
    required this.unreadCount,
    required this.updatedAt,
    this.otherUser,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'] ?? 0,
      userId1: json['user_id1'] ?? 0,
      userId2: json['user_id2'] ?? 0,
      lastMessage: json['last_message'] != null 
          ? ChatMessage.fromJson(json['last_message']) 
          : null,
      unreadCount: json['unread_count'] ?? 0,
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
      otherUser: json['other_user'] != null ? User.fromJson(json['other_user']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id1': userId1,
      'user_id2': userId2,
      'last_message': lastMessage?.toJson(),
      'unread_count': unreadCount,
      'updated_at': updatedAt.toIso8601String(),
      'other_user': otherUser?.toJson(),
    };
  }
}

class SendMessageRequest {
  final int receiverId;
  final String content;
  final String type;

  SendMessageRequest({
    required this.receiverId,
    required this.content,
    this.type = 'text',
  });

  Map<String, dynamic> toJson() {
    return {
      'receiver_id': receiverId,
      'content': content,
      'type': type,
    };
  }
}