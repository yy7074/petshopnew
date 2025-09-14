import 'user.dart';

class Bid {
  final int id;
  final int productId;
  final int userId;
  final double bidAmount;
  final DateTime bidTime;
  final String status;
  final User? user;

  Bid({
    required this.id,
    required this.productId,
    required this.userId,
    required this.bidAmount,
    required this.bidTime,
    required this.status,
    this.user,
  });

  factory Bid.fromJson(Map<String, dynamic> json) {
    return Bid(
      id: json['id'] ?? 0,
      productId: json['product_id'] ?? 0,
      userId: json['user_id'] ?? 0,
      bidAmount: double.tryParse(json['amount']?.toString() ?? json['bid_amount']?.toString() ?? '0') ?? 0,
      bidTime: DateTime.parse(json['created_at'] ?? json['bid_time'] ?? DateTime.now().toIso8601String()),
      status: _convertStatus(json['status']),
      user: json['user_info'] != null ? User.fromJson(json['user_info']) : 
           (json['user'] != null ? User.fromJson(json['user']) : null),
    );
  }

  static String _convertStatus(dynamic status) {
    if (status == null) return 'active';
    
    // 如果已经是字符串，直接返回
    if (status is String) return status;
    
    // 如果是数字，转换为对应的字符串状态
    switch (status) {
      case 1:
        return 'active';   // 进行中
      case 2:
        return 'won';      // 已中标
      case 3:
        return 'lost';     // 已失标
      case 4:
        return 'cancelled'; // 已取消
      default:
        return 'active';
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product_id': productId,
      'user_id': userId,
      'bid_amount': bidAmount,
      'bid_time': bidTime.toIso8601String(),
      'status': status,
      'user': user?.toJson(),
    };
  }
}

class BidRequest {
  final int productId;
  final double bidAmount;

  BidRequest({
    required this.productId,
    required this.bidAmount,
  });

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'bid_amount': bidAmount,
    };
  }
}

class AutoBid {
  final int id;
  final int userId;
  final int productId;
  final double maxAmount;
  final double increment;
  final String status;

  AutoBid({
    required this.id,
    required this.userId,
    required this.productId,
    required this.maxAmount,
    required this.increment,
    required this.status,
  });

  factory AutoBid.fromJson(Map<String, dynamic> json) {
    return AutoBid(
      id: json['id'] ?? 0,
      userId: json['user_id'] ?? 0,
      productId: json['product_id'] ?? 0,
      maxAmount: (json['max_amount'] ?? 0).toDouble(),
      increment: (json['increment'] ?? 0).toDouble(),
      status: json['status'] ?? 'active',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'product_id': productId,
      'max_amount': maxAmount,
      'increment': increment,
      'status': status,
    };
  }
}