import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';
import 'storage_service.dart';
import '../constants/api_constants.dart';

class ApiService extends ChangeNotifier {
  late Dio _dio;

  // 使用统一的API配置
  static String get baseUrl => ApiConstants.baseUrl;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: Duration(milliseconds: ApiConstants.connectTimeout),
      receiveTimeout: Duration(milliseconds: ApiConstants.receiveTimeout),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // 添加拦截器
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          // 添加认证token
          final token = StorageService.getUserToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onResponse: (response, handler) {
          handler.next(response);
        },
        onError: (error, handler) {
          _handleError(error);
          handler.next(error);
        },
      ),
    );

    // 开发环境添加日志拦截器
    if (kDebugMode) {
      _dio.interceptors.add(PrettyDioLogger(
        requestHeader: true,
        requestBody: true,
        responseBody: true,
        responseHeader: false,
        error: true,
        compact: true,
      ));
    }
  }

  void _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        debugPrint('网络超时');
        break;
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        if (statusCode == 401) {
          // Token过期，清除用户数据
          StorageService.clearUserData();
          debugPrint('登录已过期');
        }
        break;
      case DioExceptionType.cancel:
        debugPrint('请求已取消');
        break;
      case DioExceptionType.unknown:
        debugPrint('网络错误');
        break;
      default:
        debugPrint('未知错误: ${error.message}');
    }
  }

  // GET请求
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    return await _dio.get<T>(
      path,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken,
    );
  }

  // POST请求
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    return await _dio.post<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken,
    );
  }

  // PUT请求
  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    return await _dio.put<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken,
    );
  }

  // DELETE请求
  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    return await _dio.delete<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken,
    );
  }

  // 文件上传
  Future<Response<T>> upload<T>(
    String path,
    FormData formData, {
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
  }) async {
    return await _dio.post<T>(
      path,
      data: formData,
      options: options,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
    );
  }

  // 文件下载
  Future<Response> download(
    String urlPath,
    String savePath, {
    ProgressCallback? onReceiveProgress,
    Map<String, dynamic>? queryParameters,
    CancelToken? cancelToken,
    bool deleteOnError = true,
    String lengthHeader = Headers.contentLengthHeader,
    Options? options,
  }) async {
    return await _dio.download(
      urlPath,
      savePath,
      onReceiveProgress: onReceiveProgress,
      queryParameters: queryParameters,
      cancelToken: cancelToken,
      deleteOnError: deleteOnError,
      lengthHeader: lengthHeader,
      options: options,
    );
  }

  // 上传商品图片
  Future<List<String>> uploadProductImages(List<dynamic> files) async {
    try {
      final formData = FormData();

      // 添加多个文件
      for (var file in files) {
        if (file is MultipartFile) {
          formData.files.add(MapEntry('files', file));
        } else {
          // 假设是文件路径
          formData.files.add(
            MapEntry(
              'files',
              await MultipartFile.fromFile(
                file.toString(),
                filename: file.toString().split('/').last,
              ),
            ),
          );
        }
      }

      final response = await upload('/products/upload-images', formData);

      if (response.statusCode == 200 && response.data['success'] == true) {
        return List<String>.from(response.data['images'] ?? []);
      } else {
        throw Exception(response.data['message'] ?? '图片上传失败');
      }
    } catch (e) {
      throw Exception('图片上传失败: $e');
    }
  }

  // 上传单张图片（通用）
  Future<String> uploadSingleImage(dynamic file,
      {String endpoint = '/products/upload-images'}) async {
    try {
      final formData = FormData();

      if (file is MultipartFile) {
        formData.files.add(MapEntry('files', file));
      } else {
        formData.files.add(
          MapEntry(
            'files',
            await MultipartFile.fromFile(
              file.toString(),
              filename: file.toString().split('/').last,
            ),
          ),
        );
      }

      final response = await upload(endpoint, formData);

      if (response.statusCode == 200 && response.data['success'] == true) {
        final images = response.data['images'] as List?;
        if (images != null && images.isNotEmpty) {
          return images[0].toString();
        }
        throw Exception('未返回图片URL');
      } else {
        throw Exception(response.data['message'] ?? '图片上传失败');
      }
    } catch (e) {
      throw Exception('图片上传失败: $e');
    }
  }
}
