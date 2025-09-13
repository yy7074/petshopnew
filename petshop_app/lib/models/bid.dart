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
      bidAmount: (json['bid_amount'] ?? 0).toDouble(),
      bidTime: DateTime.parse(json['bid_time'] ?? DateTime.now().toIso8601String()),
      status: json['status'] ?? 'active',
      user: json['user'] != null ? User.fromJson(json['user']) : null,
    );
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