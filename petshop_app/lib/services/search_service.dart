import 'package:dio/dio.dart';
import '../models/product.dart';
import 'api_service.dart';
import 'auth_service.dart';

class SearchService {
  final ApiService _apiService = ApiService();

  // 搜索商品
  Future<ApiResult<List<Product>>> searchProducts({
    required String keyword,
    int page = 1,
    int pageSize = 20,
    int? categoryId,
    String? sortBy,
    String? sortOrder,
    double? minPrice,
    double? maxPrice,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'keyword': keyword,
        'page': page,
        'page_size': pageSize,
      };

      if (categoryId != null) queryParams['category_id'] = categoryId;
      if (sortBy != null) queryParams['sort_by'] = sortBy;
      if (sortOrder != null) queryParams['sort_order'] = sortOrder;
      if (minPrice != null) queryParams['min_price'] = minPrice;
      if (maxPrice != null) queryParams['max_price'] = maxPrice;

      final response = await _apiService.get('/search', queryParameters: queryParams);

      if (response.statusCode == 200) {
        final List<dynamic> productsJson = response.data['data']['items'] ?? [];
        final products = productsJson.map((json) => Product.fromJson(json)).toList();
        return ApiResult.success(products);
      } else {
        return ApiResult.error(response.data['message'] ?? '搜索失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取搜索历史
  Future<ApiResult<List<String>>> getSearchHistory() async {
    try {
      final response = await _apiService.get('/search/history');

      if (response.statusCode == 200) {
        final List<dynamic> historyJson = response.data['data'] ?? [];
        final history = historyJson.map((item) => item.toString()).toList();
        return ApiResult.success(history);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取搜索历史失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 保存搜索历史
  Future<ApiResult<void>> saveSearchHistory(String keyword) async {
    try {
      final response = await _apiService.post('/search/history', data: {
        'keyword': keyword,
      });

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '保存搜索历史失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 清除搜索历史
  Future<ApiResult<void>> clearSearchHistory() async {
    try {
      final response = await _apiService.delete('/search/history');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '清除搜索历史失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取热门搜索
  Future<ApiResult<List<String>>> getHotSearchKeywords() async {
    try {
      final response = await _apiService.get('/search/hot');

      if (response.statusCode == 200) {
        final List<dynamic> keywordsJson = response.data['data'] ?? [];
        final keywords = keywordsJson.map((item) => item.toString()).toList();
        return ApiResult.success(keywords);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取热门搜索失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 搜索建议
  Future<ApiResult<List<String>>> getSearchSuggestions(String keyword) async {
    try {
      final response = await _apiService.get('/search/suggestions', queryParameters: {
        'keyword': keyword,
      });

      if (response.statusCode == 200) {
        final List<dynamic> suggestionsJson = response.data['data'] ?? [];
        final suggestions = suggestionsJson.map((item) => item.toString()).toList();
        return ApiResult.success(suggestions);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取搜索建议失败');
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
      return error.response?.data?['message'] ?? '搜索失败';
    }
  }
}