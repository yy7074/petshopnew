import 'package:dio/dio.dart';
import '../models/product.dart';
import 'api_service.dart';
import 'auth_service.dart';

class ProductService {
  final ApiService _apiService = ApiService();

  // 获取商品列表
  Future<ApiResult<List<Product>>> getProducts({
    int page = 1,
    int pageSize = 20,
    int? categoryId,
    String? keyword,
    ProductType? type,
    String? sortBy,
    String? sortOrder,
    int? auctionType, // 添加auctionType参数
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };

      if (categoryId != null) queryParams['category_id'] = categoryId;
      if (keyword != null && keyword.isNotEmpty)
        queryParams['keyword'] = keyword;
      if (type != null) queryParams['type'] = type.toString();
      if (sortBy != null) queryParams['sort_by'] = sortBy;
      if (sortOrder != null) queryParams['sort_order'] = sortOrder;
      if (auctionType != null) queryParams['auction_type'] = auctionType;

      final response =
          await _apiService.get('/products', queryParameters: queryParams);

      if (response.statusCode == 200) {
        final List<dynamic> productsJson = response.data['data']['items'] ?? [];
        final products =
            productsJson.map((json) => Product.fromJson(json)).toList();
        return ApiResult.success(products);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取商品列表失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取商品详情
  Future<ApiResult<Product>> getProductDetail(int productId) async {
    try {
      final response = await _apiService.get('/products/$productId');

      if (response.statusCode == 200) {
        final product = Product.fromJson(response.data['data']);
        return ApiResult.success(product);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取商品详情失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取热门商品
  Future<ApiResult<List<Product>>> getHotProducts({int limit = 10}) async {
    try {
      final response = await _apiService.get('/products/hot', queryParameters: {
        'limit': limit,
      });

      if (response.statusCode == 200) {
        final List<dynamic> productsJson = response.data['data'] ?? [];
        final products =
            productsJson.map((json) => Product.fromJson(json)).toList();
        return ApiResult.success(products);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取热门商品失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取推荐商品
  Future<ApiResult<List<Product>>> getRecommendedProducts(
      {int limit = 10}) async {
    try {
      final response =
          await _apiService.get('/products/recommended', queryParameters: {
        'limit': limit,
      });

      if (response.statusCode == 200) {
        final List<dynamic> productsJson = response.data['data'] ?? [];
        final products =
            productsJson.map((json) => Product.fromJson(json)).toList();
        return ApiResult.success(products);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取推荐商品失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取分类列表
  Future<ApiResult<List<Category>>> getCategories() async {
    try {
      final response = await _apiService.get('/categories');

      if (response.statusCode == 200) {
        final List<dynamic> categoriesJson = response.data['data'] ?? [];
        final categories =
            categoriesJson.map((json) => Category.fromJson(json)).toList();
        return ApiResult.success(categories);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取分类列表失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取轮播图
  Future<ApiResult<List<Banner>>> getBanners() async {
    try {
      final response = await _apiService.get('/banners');

      if (response.statusCode == 200) {
        final List<dynamic> bannersJson = response.data['data'] ?? [];
        final banners =
            bannersJson.map((json) => Banner.fromJson(json)).toList();
        return ApiResult.success(banners);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取轮播图失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 添加收藏
  Future<ApiResult<void>> addFavorite(int productId) async {
    try {
      final response = await _apiService.post('/user/favorites', data: {
        'product_id': productId,
      });

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '收藏失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 取消收藏
  Future<ApiResult<void>> removeFavorite(int productId) async {
    try {
      final response = await _apiService.delete('/user/favorites/$productId');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '取消收藏失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取用户收藏列表
  Future<ApiResult<List<Product>>> getUserFavorites({
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final response =
          await _apiService.get('/user/favorites', queryParameters: {
        'page': page,
        'page_size': pageSize,
      });

      if (response.statusCode == 200) {
        final List<dynamic> productsJson = response.data['data']['items'] ?? [];
        final products = productsJson
            .map((json) => Product.fromJson(json['product']))
            .toList();
        return ApiResult.success(products);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取收藏列表失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 错误处理
  String _handleError(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return '网络连接超时，请检查网络';
    } else if (error.type == DioExceptionType.unknown) {
      return '网络连接失败，请检查网络';
    } else {
      return error.response?.data?['message'] ?? '未知错误';
    }
  }
}

// 轮播图模型
class Banner {
  final int id;
  final String title;
  final String imageUrl;
  final String? linkUrl;
  final int sortOrder;
  final bool isActive;

  Banner({
    required this.id,
    required this.title,
    required this.imageUrl,
    this.linkUrl,
    required this.sortOrder,
    required this.isActive,
  });

  factory Banner.fromJson(Map<String, dynamic> json) {
    return Banner(
      id: json['id'] ?? 0,
      title: json['title'] ?? '',
      imageUrl: json['image_url'] ?? '',
      linkUrl: json['link_url'],
      sortOrder: json['sort_order'] ?? 0,
      isActive: json['is_active'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'image_url': imageUrl,
      'link_url': linkUrl,
      'sort_order': sortOrder,
      'is_active': isActive,
    };
  }
}
