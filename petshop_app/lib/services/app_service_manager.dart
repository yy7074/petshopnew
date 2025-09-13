import 'api_service.dart';
import 'auth_service.dart';
import 'product_service.dart';
import 'bid_service.dart';
import 'storage_service.dart';

/// 应用服务管理器 - 统一管理所有服务实例
class AppServiceManager {
  static final AppServiceManager _instance = AppServiceManager._internal();
  factory AppServiceManager() => _instance;
  AppServiceManager._internal();

  // 服务实例
  late final ApiService _apiService;
  late final AuthService _authService;
  late final ProductService _productService;
  late final BidService _bidService;

  // 初始化所有服务
  Future<void> init() async {
    // 初始化存储服务
    await StorageService.init();
    
    // 初始化API服务
    _apiService = ApiService();
    
    // 初始化其他服务
    _authService = AuthService();
    _productService = ProductService();
    _bidService = BidService();
  }

  // 获取服务实例
  ApiService get apiService => _apiService;
  AuthService get authService => _authService;
  ProductService get productService => _productService;
  BidService get bidService => _bidService;

  // 便捷方法
  
  /// 检查用户是否已登录
  Future<bool> isUserLoggedIn() async {
    return await _authService.isLoggedIn();
  }

  /// 获取当前用户
  dynamic getCurrentUser() {
    return _authService.getCurrentUser();
  }

  /// 清除所有数据（用于退出登录）
  Future<void> clearAllData() async {
    await StorageService.clearUserData();
  }
}

/// 全局服务管理器实例
final serviceManager = AppServiceManager();