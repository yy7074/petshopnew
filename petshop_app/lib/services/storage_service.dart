import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static SharedPreferences? _prefs;

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // 用户相关
  static const String _keyUserId = 'user_id';
  static const String _keyUserToken = 'user_token';
  static const String _keyUserInfo = 'user_info';
  static const String _keyIsFirstLaunch = 'is_first_launch';

  // 获取用户ID
  static int? getUserId() {
    return _prefs?.getInt(_keyUserId);
  }

  // 设置用户ID
  static Future<bool> setUserId(int userId) async {
    return await _prefs?.setInt(_keyUserId, userId) ?? false;
  }

  // 获取用户Token
  static String? getUserToken() {
    return _prefs?.getString(_keyUserToken);
  }

  // 设置用户Token
  static Future<bool> setUserToken(String token) async {
    return await _prefs?.setString(_keyUserToken, token) ?? false;
  }

  // 获取用户信息
  static String? getUserInfo() {
    return _prefs?.getString(_keyUserInfo);
  }

  // 设置用户信息
  static Future<bool> setUserInfo(String userInfo) async {
    return await _prefs?.setString(_keyUserInfo, userInfo) ?? false;
  }

  // 是否首次启动
  static bool isFirstLaunch() {
    return _prefs?.getBool(_keyIsFirstLaunch) ?? true;
  }

  // 设置首次启动标记
  static Future<bool> setFirstLaunch(bool isFirst) async {
    return await _prefs?.setBool(_keyIsFirstLaunch, isFirst) ?? false;
  }

  // 清除用户数据
  static Future<void> clearUserData() async {
    await _prefs?.remove(_keyUserId);
    await _prefs?.remove(_keyUserToken);
    await _prefs?.remove(_keyUserInfo);
  }

  // 清除所有数据
  static Future<void> clearAll() async {
    await _prefs?.clear();
  }

  // 通用方法
  static Future<bool> setString(String key, String value) async {
    return await _prefs?.setString(key, value) ?? false;
  }

  static String? getString(String key) {
    return _prefs?.getString(key);
  }

  static Future<bool> setInt(String key, int value) async {
    return await _prefs?.setInt(key, value) ?? false;
  }

  static int? getInt(String key) {
    return _prefs?.getInt(key);
  }

  static Future<bool> setBool(String key, bool value) async {
    return await _prefs?.setBool(key, value) ?? false;
  }

  static bool? getBool(String key) {
    return _prefs?.getBool(key);
  }

  static Future<bool> setDouble(String key, double value) async {
    return await _prefs?.setDouble(key, value) ?? false;
  }

  static double? getDouble(String key) {
    return _prefs?.getDouble(key);
  }

  static Future<bool> setStringList(String key, List<String> value) async {
    return await _prefs?.setStringList(key, value) ?? false;
  }

  static List<String>? getStringList(String key) {
    return _prefs?.getStringList(key);
  }

  static Future<bool> remove(String key) async {
    return await _prefs?.remove(key) ?? false;
  }

  static bool containsKey(String key) {
    return _prefs?.containsKey(key) ?? false;
  }
}



