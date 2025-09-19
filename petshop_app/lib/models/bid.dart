import 'user.dart';

class Bid {
  final int id;
  final int productId;
  final int userId;
  final double bidAmount;
  final DateTime bidTime;
  final String status;
  final User? user;
  final BidProductInfo? product;

  Bid({
    required this.id,
    required this.productId,
    required this.userId,
    required this.bidAmount,
    required this.bidTime,
    required this.status,
    this.user,
    this.product,
  });

  factory Bid.fromJson(Map<String, dynamic> json) {
    print('Bid.fromJson - 原始数据: ${json.toString()}');
    print('  product_info: ${json['product_info']}');

    final productInfo = json['product_info'] != null
        ? BidProductInfo.fromJson(json['product_info'])
        : null;

    print(
        '  解析后的productInfo: title=${productInfo?.title}, status=${productInfo?.status}');

    return Bid(
      id: json['id'] ?? 0,
      productId: json['product_id'] ?? 0,
      userId: json['user_id'] ?? 0,
      bidAmount: double.tryParse(json['amount']?.toString() ??
              json['bid_amount']?.toString() ??
              '0') ??
          0,
      bidTime: DateTime.parse(json['created_at'] ??
          json['bid_time'] ??
          DateTime.now().toIso8601String()),
      status: _convertStatus(json['status']),
      user: json['user_info'] != null
          ? User.fromJson(json['user_info'])
          : (json['user'] != null ? User.fromJson(json['user']) : null),
      product: productInfo,
    );
  }

  static String _convertStatus(dynamic status) {
    if (status == null) return 'active';

    // 如果已经是字符串，直接返回
    if (status is String) return status;

    // 如果是数字，转换为对应的字符串状态
    // 根据后端数据库实际含义：1:有效/领先, 2:被超越, 3:撤销
    switch (status) {
      case 1:
        return 'active'; // 有效/领先
      case 2:
        return 'lost'; // 被超越
      case 3:
        return 'cancelled'; // 撤销
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
      'product': product?.toJson(),
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

class BidProductInfo {
  final String title;
  final String? image;
  final int? status; // 商品状态: 1:活跃 2:拍卖中 3:已结束

  BidProductInfo({
    required this.title,
    this.image,
    this.status,
  });

  factory BidProductInfo.fromJson(Map<String, dynamic> json) {
    return BidProductInfo(
      title: json['title'] ?? '未知商品',
      image: json['image'],
      status: json['status'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'image': image,
      'status': status,
    };
  }
}
