import 'user.dart';
import 'product.dart';

class Order {
  final int id;
  final int buyerId;
  final int sellerId;
  final double totalAmount;
  final String status;
  final String paymentStatus;
  final DateTime createdAt;
  final DateTime updatedAt;
  final User? buyer;
  final User? seller;
  final List<OrderItem> items;
  final Payment? payment;
  final Logistics? logistics;

  Order({
    required this.id,
    required this.buyerId,
    required this.sellerId,
    required this.totalAmount,
    required this.status,
    required this.paymentStatus,
    required this.createdAt,
    required this.updatedAt,
    this.buyer,
    this.seller,
    required this.items,
    this.payment,
    this.logistics,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'] ?? 0,
      buyerId: json['buyer_id'] ?? 0,
      sellerId: json['seller_id'] ?? 0,
      totalAmount: (json['total_amount'] ?? 0).toDouble(),
      status: json['status'] ?? 'pending',
      paymentStatus: json['payment_status'] ?? 'unpaid',
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
      buyer: json['buyer'] != null ? User.fromJson(json['buyer']) : null,
      seller: json['seller'] != null ? User.fromJson(json['seller']) : null,
      items: (json['items'] as List<dynamic>? ?? [])
          .map((item) => OrderItem.fromJson(item))
          .toList(),
      payment: json['payment'] != null ? Payment.fromJson(json['payment']) : null,
      logistics: json['logistics'] != null ? Logistics.fromJson(json['logistics']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'buyer_id': buyerId,
      'seller_id': sellerId,
      'total_amount': totalAmount,
      'status': status,
      'payment_status': paymentStatus,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'buyer': buyer?.toJson(),
      'seller': seller?.toJson(),
      'items': items.map((item) => item.toJson()).toList(),
      'payment': payment?.toJson(),
      'logistics': logistics?.toJson(),
    };
  }
}

class OrderItem {
  final int id;
  final int orderId;
  final int productId;
  final int quantity;
  final double price;
  final Map<String, dynamic> snapshot;
  final Product? product;

  OrderItem({
    required this.id,
    required this.orderId,
    required this.productId,
    required this.quantity,
    required this.price,
    required this.snapshot,
    this.product,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      id: json['id'] ?? 0,
      orderId: json['order_id'] ?? 0,
      productId: json['product_id'] ?? 0,
      quantity: json['quantity'] ?? 1,
      price: (json['price'] ?? 0).toDouble(),
      snapshot: Map<String, dynamic>.from(json['snapshot'] ?? {}),
      product: json['product'] != null ? Product.fromJson(json['product']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'order_id': orderId,
      'product_id': productId,
      'quantity': quantity,
      'price': price,
      'snapshot': snapshot,
      'product': product?.toJson(),
    };
  }

  double get totalPrice => price * quantity;
}

class Payment {
  final int id;
  final int orderId;
  final String paymentMethod;
  final double amount;
  final String? transactionId;
  final String status;
  final DateTime? paidAt;
  final DateTime createdAt;

  Payment({
    required this.id,
    required this.orderId,
    required this.paymentMethod,
    required this.amount,
    this.transactionId,
    required this.status,
    this.paidAt,
    required this.createdAt,
  });

  factory Payment.fromJson(Map<String, dynamic> json) {
    return Payment(
      id: json['id'] ?? 0,
      orderId: json['order_id'] ?? 0,
      paymentMethod: json['payment_method'] ?? '',
      amount: (json['amount'] ?? 0).toDouble(),
      transactionId: json['transaction_id'],
      status: json['status'] ?? 'pending',
      paidAt: json['paid_at'] != null ? DateTime.parse(json['paid_at']) : null,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'order_id': orderId,
      'payment_method': paymentMethod,
      'amount': amount,
      'transaction_id': transactionId,
      'status': status,
      'paid_at': paidAt?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class Logistics {
  final int id;
  final int orderId;
  final String expressCompany;
  final String trackingNumber;
  final String status;
  final DateTime updatedAt;

  Logistics({
    required this.id,
    required this.orderId,
    required this.expressCompany,
    required this.trackingNumber,
    required this.status,
    required this.updatedAt,
  });

  factory Logistics.fromJson(Map<String, dynamic> json) {
    return Logistics(
      id: json['id'] ?? 0,
      orderId: json['order_id'] ?? 0,
      expressCompany: json['express_company'] ?? '',
      trackingNumber: json['tracking_number'] ?? '',
      status: json['status'] ?? 'pending',
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'order_id': orderId,
      'express_company': expressCompany,
      'tracking_number': trackingNumber,
      'status': status,
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}

class CreateOrderRequest {
  final int productId;
  final int quantity;
  final String paymentMethod;

  CreateOrderRequest({
    required this.productId,
    required this.quantity,
    required this.paymentMethod,
  });

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'quantity': quantity,
      'payment_method': paymentMethod,
    };
  }
}