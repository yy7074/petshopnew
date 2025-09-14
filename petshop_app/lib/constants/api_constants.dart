import 'package:flutter/foundation.dart';

class ApiConstants {
  // 基础配置 - 根据环境动态设置
  static String get baseUrl {
    if (kDebugMode) {
      // Debug模式：本地开发服务器
      return 'http://localhost:3000/api/v1';
    } else {
      // Release模式：生产服务器
      return 'https://catdog.dachaonet.com/api/v1';
    }
  }

  static const String version = '';

  // 超时配置 - Release模式下更短的超时时间
  static int get connectTimeout => kDebugMode ? 30000 : 15000;
  static int get receiveTimeout => kDebugMode ? 30000 : 15000;

  // 认证相关
  static const String login = '$version/auth/login';
  static const String register = '$version/auth/register';
  static const String logout = '$version/auth/logout';
  static const String refreshToken = '$version/auth/refresh';
  static const String userProfile = '$version/auth/profile';

  // 商品相关
  static const String products = '$version/products';
  static const String productDetail = '$version/products';
  static const String categories = '$version/categories';
  static const String banners = '$version/banners';

  // 竞拍相关
  static const String bids = '$version/bids';
  static const String auctionResults = '$version/auctions/results';
  static const String autoBid = '$version/auctions/auto-bid';

  // 订单相关
  static const String orders = '$version/orders';
  static const String payments = '$version/payments';
  static const String logistics = '$version/logistics';

  // 搜索相关
  static const String search = '$version/search';
  static const String searchHistory = '$version/search/history';

  // 用户中心
  static const String userAddresses = '$version/user/addresses';
  static const String userFavorites = '$version/user/favorites';
  static const String userCheckin = '$version/user/checkin';

  // 消息聊天
  static const String messages = '$version/messages';
  static const String chat = '$version/chat';

  // 发布管理
  static const String publishProduct = '$version/products';
  static const String uploadImage = '$version/upload/image';
}
