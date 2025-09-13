import 'package:flutter/material.dart';

class AppColors {
  // 主色调
  static const Color primary = Color(0xFFFF6B35);
  static const Color primaryLight = Color(0xFFFF8A65);
  static const Color primaryDark = Color(0xFFE64A19);
  
  // 辅助色
  static const Color secondary = Color(0xFF4CAF50);
  static const Color accent = Color(0xFFFFC107);
  
  // 背景色
  static const Color background = Color(0xFFF5F5F5);
  static const Color backgroundGrey = Color(0xFFF5F5F5);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color cardBackground = Color(0xFFFFFFFF);
  static const Color lightGrey = Color(0xFFE0E0E0);
  
  // 文字颜色
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF757575);
  static const Color textHint = Color(0xFFBDBDBD);
  static const Color textWhite = Color(0xFFFFFFFF);
  
  // 分割线
  static const Color divider = Color(0xFFE0E0E0);
  static const Color border = Color(0xFFE0E0E0);
  
  // 状态色
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFF9800);
  static const Color error = Color(0xFFF44336);
  static const Color info = Color(0xFF2196F3);
  
  // 特殊色
  static const Color price = Color(0xFFFF5722);
  static const Color discount = Color(0xFFE91E63);
  static const Color vip = Color(0xFFFFD700);
  
  // 渐变色
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, primaryLight],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient cardGradient = LinearGradient(
    colors: [Color(0xFFFFFFFF), Color(0xFFF8F8F8)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}



