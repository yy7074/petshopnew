import 'package:dio/dio.dart';
import '../models/user.dart';
import 'api_service.dart';
import 'storage_service.dart';

class AuthService {
  final ApiService _apiService = ApiService();

  // 登录
  Future<ApiResult<LoginResponse>> login({
    required String phone,
    required String password,
  }) async {
    try {
      // 使用FormData发送表单数据，匹配后端OAuth2PasswordRequestForm的期望
      final formData = FormData.fromMap({
        'username': phone, // 后端使用username字段，但可以接受手机号
        'password': password,
      });

      final response = await _apiService.post('/auth/login', data: formData);

      if (response.statusCode == 200) {
        final loginResponse = LoginResponse.fromJson(response.data);

        // 保存用户信息和token
        await StorageService.saveUser(loginResponse.user);
        await StorageService.saveUserToken(loginResponse.accessToken);
        await StorageService.setString(
            'refresh_token', loginResponse.refreshToken ?? '');

        return ApiResult.success(loginResponse);
      } else {
        return ApiResult.error(response.data['detail'] ?? '登录失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 注册
  Future<ApiResult<LoginResponse>> register({
    required String phone,
    required String password,
    required String nickname,
    String? verificationCode,
  }) async {
    try {
      final response = await _apiService.post('/auth/register', data: {
        'phone': phone,
        'password': password,
        'nickname': nickname,
        'verification_code': verificationCode,
      });

      if (response.statusCode == 200) {
        final loginResponse = LoginResponse.fromJson(response.data['data']);

        // 保存用户信息和token
        await StorageService.saveUser(loginResponse.user);
        await StorageService.saveUserToken(loginResponse.accessToken);
        await StorageService.setString(
            'refresh_token', loginResponse.refreshToken);

        return ApiResult.success(loginResponse);
      } else {
        return ApiResult.error(response.data['message'] ?? '注册失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 发送短信验证码
  Future<ApiResult<Map<String, dynamic>>> sendSMS(String phone) async {
    try {
      final response = await _apiService.post('/auth/send-sms', data: {
        'phone': phone,
      });

      if (response.statusCode == 200) {
        return ApiResult.success(response.data);
      } else {
        return ApiResult.error(response.data['message'] ?? '发送验证码失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 验证短信验证码
  Future<ApiResult<Map<String, dynamic>>> verifySMS(String phone, String code) async {
    try {
      final response = await _apiService.post('/auth/verify-sms', data: {
        'phone': phone,
        'code': code,
      });

      if (response.statusCode == 200) {
        return ApiResult.success(response.data);
      } else {
        return ApiResult.error(response.data['message'] ?? '验证码验证失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 短信验证码登录
  Future<ApiResult<LoginResponse>> smsLogin({
    required String phone,
    required String code,
  }) async {
    try {
      final response = await _apiService.post('/auth/sms-login', data: {
        'phone': phone,
        'code': code,
      });

      if (response.statusCode == 200) {
        final loginResponse = LoginResponse.fromJson(response.data);

        // 保存用户信息和token
        await StorageService.saveUser(loginResponse.user);
        await StorageService.saveUserToken(loginResponse.accessToken);
        await StorageService.setString(
            'refresh_token', loginResponse.refreshToken ?? '');

        return ApiResult.success(loginResponse);
      } else {
        return ApiResult.error(response.data['detail'] ?? '登录失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 发送验证码（兼容旧接口）
  Future<ApiResult<void>> sendVerificationCode(String phone) async {
    try {
      final response = await _apiService.post('/auth/send-code', data: {
        'phone': phone,
      });

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '发送验证码失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 退出登录
  Future<ApiResult<void>> logout() async {
    try {
      await _apiService.post('/auth/logout');

      // 清除本地存储
      await StorageService.clearUserData();

      return ApiResult.success(null);
    } on DioException {
      // 即使接口调用失败，也要清除本地数据
      await StorageService.clearUserData();
      return ApiResult.success(null);
    }
  }

  // 刷新token
  Future<ApiResult<String>> refreshToken() async {
    try {
      final refreshToken = StorageService.getString('refresh_token');
      if (refreshToken == null || refreshToken.isEmpty) {
        return ApiResult.error('刷新令牌不存在');
      }

      final response = await _apiService.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      if (response.statusCode == 200) {
        final newToken = response.data['data']['access_token'];
        await StorageService.saveUserToken(newToken);
        return ApiResult.success(newToken);
      } else {
        return ApiResult.error(response.data['message'] ?? '刷新令牌失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取用户信息
  Future<ApiResult<User>> getUserProfile() async {
    try {
      final response = await _apiService.get('/auth/profile');

      if (response.statusCode == 200) {
        final user = User.fromJson(response.data['data']);
        await StorageService.saveUser(user);
        return ApiResult.success(user);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取用户信息失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 更新用户信息
  Future<ApiResult<User>> updateProfile({
    String? nickname,
    String? avatar,
    String? realName,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (nickname != null) data['nickname'] = nickname;
      if (avatar != null) data['avatar'] = avatar;
      if (realName != null) data['real_name'] = realName;

      final response = await _apiService.put('/auth/profile', data: data);

      if (response.statusCode == 200) {
        final user = User.fromJson(response.data['data']);
        await StorageService.saveUser(user);
        return ApiResult.success(user);
      } else {
        return ApiResult.error(response.data['message'] ?? '更新用户信息失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 检查是否已登录
  Future<bool> isLoggedIn() async {
    final token = StorageService.getUserToken();
    return token != null && token.isNotEmpty;
  }

  // 获取当前用户
  User? getCurrentUser() {
    return StorageService.getUser();
  }

  // 错误处理
  String _handleError(DioException error) {
    if (error.response?.statusCode == 401) {
      return '用户名或密码错误';
    } else if (error.response?.statusCode == 422) {
      return '输入信息格式不正确';
    } else if (error.response?.statusCode == 429) {
      return '请求过于频繁，请稍后再试';
    } else if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return '网络连接超时，请检查网络';
    } else if (error.type == DioExceptionType.unknown) {
      return '网络连接失败，请检查网络';
    } else {
      return error.response?.data?['message'] ?? '未知错误';
    }
  }
}

// API结果封装类
class ApiResult<T> {
  final bool success;
  final T? data;
  final String message;

  ApiResult({
    required this.success,
    this.data,
    required this.message,
  });

  factory ApiResult.success(T data) {
    return ApiResult<T>(
      success: true,
      data: data,
      message: 'success',
    );
  }

  factory ApiResult.error(String message) {
    return ApiResult<T>(
      success: false,
      data: null,
      message: message,
    );
  }
}
