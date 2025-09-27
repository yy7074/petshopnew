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

      final response =
          await _apiService.get('/search/', queryParameters: queryParams);

      if (response.statusCode == 200) {
        // 后台搜索API返回格式：SearchResponse
        final responseData = response.data;

        if (responseData['items'] != null) {
          final List<dynamic> productsJson = responseData['items'];
          final products =
              productsJson.map((json) => Product.fromJson(json)).toList();
          return ApiResult.success(products);
        } else {
          return ApiResult.error('搜索结果格式错误');
        }
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
        // 后台API直接返回字符串数组
        final List<dynamic> historyJson = response.data ?? [];
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
        // 后台API返回 List<HotSearchResponse>
        final List<dynamic> keywordsJson = response.data ?? [];
        final keywords = keywordsJson
            .map((item) => item is Map
                ? item['keyword']?.toString() ?? ''
                : item.toString())
            .toList();
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
      final response =
          await _apiService.get('/search/suggestions', queryParameters: {
        'keyword': keyword,
      });

      if (response.statusCode == 200) {
        // 后台API返回 List<SearchSuggestionResponse>
        final List<dynamic> suggestionsJson = response.data ?? [];
        final suggestions = suggestionsJson
            .map((item) => item is Map
                ? item['keyword']?.toString() ?? ''
                : item.toString())
            .toList();
        return ApiResult.success(suggestions);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取搜索建议失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 错误处理
  // 保存搜索历史到服务器
  Future<ApiResult<void>> saveSearchKeyword(String keyword) async {
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

  // 删除单条搜索历史
  Future<ApiResult<void>> deleteSearchHistoryItem(String keyword) async {
    try {
      final response = await _apiService.delete('/search/history/$keyword');

      if (response.statusCode == 200) {
        return ApiResult.success(null);
      } else {
        return ApiResult.error(response.data['message'] ?? '删除搜索历史失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取搜索筛选选项
  Future<ApiResult<Map<String, dynamic>>> getSearchFilters({
    String? keyword,
    int? categoryId,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (keyword != null) queryParams['keyword'] = keyword;
      if (categoryId != null) queryParams['category_id'] = categoryId;

      final response = await _apiService.get('/search/filters',
          queryParameters: queryParams);

      if (response.statusCode == 200) {
        return ApiResult.success(response.data ?? {});
      } else {
        return ApiResult.error(response.data['message'] ?? '获取筛选选项失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 获取趋势关键词
  Future<ApiResult<List<String>>> getTrendingKeywords({
    String period = 'day',
    int limit = 10,
  }) async {
    try {
      final response =
          await _apiService.get('/search/trending', queryParameters: {
        'period': period,
        'limit': limit,
      });

      if (response.statusCode == 200) {
        final List<dynamic> keywordsJson = response.data ?? [];
        final keywords = keywordsJson
            .map((item) => item is Map
                ? item['keyword']?.toString() ?? ''
                : item.toString())
            .toList();
        return ApiResult.success(keywords);
      } else {
        return ApiResult.error(response.data['message'] ?? '获取趋势关键词失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

  // 自动完成搜索
  Future<ApiResult<List<String>>> autocompleteSearch({
    required String query,
    String type = 'all',
    int limit = 10,
  }) async {
    try {
      final response =
          await _apiService.get('/search/autocomplete', queryParameters: {
        'q': query,
        'type': type,
        'limit': limit,
      });

      if (response.statusCode == 200) {
        final List<dynamic> suggestionsJson = response.data ?? [];
        final suggestions = suggestionsJson
            .map((item) =>
                item is Map ? item['text']?.toString() ?? '' : item.toString())
            .toList();
        return ApiResult.success(suggestions);
      } else {
        return ApiResult.error(response.data['message'] ?? '自动完成失败');
      }
    } on DioException catch (e) {
      return ApiResult.error(_handleError(e));
    }
  }

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
