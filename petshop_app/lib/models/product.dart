class Product {
  final int id;
  final int sellerId;
  final String title;
  final String description;
  final int categoryId;
  final List<String> images;
  final String status;
  final ProductType type;
  final AuctionInfo? auctionInfo;
  final FixedInfo? fixedInfo;
  final String? location;
  final Seller? seller;
  final DateTime createdAt;
  final DateTime updatedAt;

  Product({
    required this.id,
    required this.sellerId,
    required this.title,
    required this.description,
    required this.categoryId,
    required this.images,
    required this.status,
    required this.type,
    this.auctionInfo,
    this.fixedInfo,
    this.location,
    this.seller,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    // 基于实际API响应格式解析
    final int auctionType = json['auction_type'] ?? 1;
    final ProductType productType =
        auctionType == 1 ? ProductType.auction : ProductType.fixed;

    // 构建AuctionInfo（如果是拍卖类型）
    AuctionInfo? auctionInfo;
    if (productType == ProductType.auction) {
      auctionInfo = AuctionInfo(
        startPrice:
            double.tryParse(json['starting_price']?.toString() ?? '0') ?? 0.0,
        currentPrice:
            double.tryParse(json['current_price']?.toString() ?? '0') ?? 0.0,
        bidIncrement: 10.0, // 默认值，API中没有这个字段
        startTime: json['auction_start_time'] != null
            ? DateTime.parse(json['auction_start_time'])
            : DateTime.now(),
        endTime: json['auction_end_time'] != null
            ? DateTime.parse(json['auction_end_time'])
            : DateTime.now().add(Duration(days: 7)),
        bidCount: json['bid_count'] ?? 0,
      );
    }

    // 构建FixedInfo（如果是一口价类型）
    FixedInfo? fixedInfo;
    if (productType == ProductType.fixed) {
      fixedInfo = FixedInfo(
        price: double.tryParse(json['buy_now_price']?.toString() ?? '0') ?? 0.0,
        stock: json['stock_quantity'] ?? 0,
        salesCount: 0, // API中没有这个字段
      );
    }

    return Product(
      id: json['id'] ?? 0,
      sellerId: json['seller_id'] is int
          ? json['seller_id']
          : (int.tryParse(json['seller_id']?.toString() ?? '0') ?? 0),
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      categoryId: json['category_id'] ?? 0,
      images: List<String>.from(json['images'] ?? []),
      status: (json['status'] ?? 1).toString(),
      type: productType,
      auctionInfo: auctionInfo,
      fixedInfo: fixedInfo,
      location: json['location'],
      seller: null, // seller信息需要单独接口获取
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'seller_id': sellerId,
      'title': title,
      'description': description,
      'category_id': categoryId,
      'images': images,
      'status': status,
      'type': type.toString(),
      'auction_info': auctionInfo?.toJson(),
      'fixed_info': fixedInfo?.toJson(),
      'location': location,
      'seller': seller?.toJson(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  // 获取当前价格
  double get currentPrice {
    if (type == ProductType.auction) {
      return auctionInfo?.currentPrice ?? 0;
    } else {
      return fixedInfo?.price ?? 0;
    }
  }

  // 获取主图
  String get mainImage {
    return images.isNotEmpty ? images.first : '';
  }

  // 是否正在拍卖中
  bool get isAuctionActive {
    if (type != ProductType.auction || auctionInfo == null) return false;
    final now = DateTime.now();
    return now.isAfter(auctionInfo!.startTime) &&
        now.isBefore(auctionInfo!.endTime);
  }

  // 获取剩余时间
  Duration? get timeLeft {
    if (type != ProductType.auction || auctionInfo == null) return null;
    final now = DateTime.now();
    if (now.isAfter(auctionInfo!.endTime)) return null;
    return auctionInfo!.endTime.difference(now);
  }
}

enum ProductType {
  auction,
  fixed;

  static ProductType fromString(String value) {
    switch (value.toLowerCase()) {
      case 'auction':
        return ProductType.auction;
      case 'fixed':
        return ProductType.fixed;
      default:
        return ProductType.auction;
    }
  }

  @override
  String toString() {
    switch (this) {
      case ProductType.auction:
        return 'auction';
      case ProductType.fixed:
        return 'fixed';
    }
  }
}

class AuctionInfo {
  final double startPrice;
  final double currentPrice;
  final double bidIncrement;
  final DateTime startTime;
  final DateTime endTime;
  final int bidCount;

  AuctionInfo({
    required this.startPrice,
    required this.currentPrice,
    required this.bidIncrement,
    required this.startTime,
    required this.endTime,
    required this.bidCount,
  });

  factory AuctionInfo.fromJson(Map<String, dynamic> json) {
    return AuctionInfo(
      startPrice: (json['start_price'] ?? 0).toDouble(),
      currentPrice: (json['current_price'] ?? 0).toDouble(),
      bidIncrement: (json['bid_increment'] ?? 0).toDouble(),
      startTime: DateTime.parse(
          json['start_time'] ?? DateTime.now().toIso8601String()),
      endTime:
          DateTime.parse(json['end_time'] ?? DateTime.now().toIso8601String()),
      bidCount: json['bid_count'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'start_price': startPrice,
      'current_price': currentPrice,
      'bid_increment': bidIncrement,
      'start_time': startTime.toIso8601String(),
      'end_time': endTime.toIso8601String(),
      'bid_count': bidCount,
    };
  }
}

class FixedInfo {
  final double price;
  final int stock;
  final int salesCount;

  FixedInfo({
    required this.price,
    required this.stock,
    required this.salesCount,
  });

  factory FixedInfo.fromJson(Map<String, dynamic> json) {
    return FixedInfo(
      price: (json['price'] ?? 0).toDouble(),
      stock: json['stock'] ?? 0,
      salesCount: json['sales_count'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'price': price,
      'stock': stock,
      'sales_count': salesCount,
    };
  }
}

class Seller {
  final int id;
  final String name;
  final String? avatar;
  final double rating;
  final int followerCount;

  Seller({
    required this.id,
    required this.name,
    this.avatar,
    required this.rating,
    required this.followerCount,
  });

  factory Seller.fromJson(Map<String, dynamic> json) {
    return Seller(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      avatar: json['avatar'],
      rating: (json['rating'] ?? 0).toDouble(),
      followerCount: json['follower_count'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'avatar': avatar,
      'rating': rating,
      'follower_count': followerCount,
    };
  }
}

class Category {
  final int id;
  final String name;
  final int? parentId;
  final int sortOrder;
  final String? icon;
  final String status;

  Category({
    required this.id,
    required this.name,
    this.parentId,
    required this.sortOrder,
    this.icon,
    required this.status,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      parentId: json['parent_id'],
      sortOrder: json['sort_order'] ?? 0,
      icon: json['icon'],
      status: json['status'] ?? 'active',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'parent_id': parentId,
      'sort_order': sortOrder,
      'icon': icon,
      'status': status,
    };
  }
}
