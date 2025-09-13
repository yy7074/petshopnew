class User {
  final int id;
  final String phone;
  final String nickname;
  final String? avatar;
  final String? realName;
  final String? idCard;
  final String status;
  final DateTime createdAt;

  User({
    required this.id,
    required this.phone,
    required this.nickname,
    this.avatar,
    this.realName,
    this.idCard,
    required this.status,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? 0,
      phone: json['phone'] ?? '',
      nickname: json['nickname'] ?? '',
      avatar: json['avatar'],
      realName: json['real_name'],
      idCard: json['id_card'],
      status: json['status'] ?? 'active',
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone': phone,
      'nickname': nickname,
      'avatar': avatar,
      'real_name': realName,
      'id_card': idCard,
      'status': status,
      'created_at': createdAt.toIso8601String(),
    };
  }

  User copyWith({
    int? id,
    String? phone,
    String? nickname,
    String? avatar,
    String? realName,
    String? idCard,
    String? status,
    DateTime? createdAt,
  }) {
    return User(
      id: id ?? this.id,
      phone: phone ?? this.phone,
      nickname: nickname ?? this.nickname,
      avatar: avatar ?? this.avatar,
      realName: realName ?? this.realName,
      idCard: idCard ?? this.idCard,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

class LoginResponse {
  final String accessToken;
  final String refreshToken;
  final User user;

  LoginResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.user,
  });

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    return LoginResponse(
      accessToken: json['access_token'] ?? '',
      refreshToken: json['refresh_token'] ?? '',
      user: User.fromJson(json['user'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'user': user.toJson(),
    };
  }
}