import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import '../../utils/app_routes.dart';
import '../../services/auth_service.dart';
import 'sms_login_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _authService = AuthService();
  bool _isWechatLoading = false;
  bool _isPhoneLoading = false;
  bool _agreedToTerms = true; // 默认已同意

  @override
  void initState() {
    super.initState();
    // 设置状态栏样式
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
        statusBarBrightness: Brightness.light,
      ),
    );
  }

  // 微信登录
  void _wechatLogin() async {
    if (!_agreedToTerms) {
      Get.snackbar(
        '提示',
        '请先阅读并同意用户协议和隐私政策',
        snackPosition: SnackPosition.TOP,
        backgroundColor: Colors.orange,
        colorText: Colors.white,
      );
      return;
    }

    setState(() {
      _isWechatLoading = true;
    });

    try {
      // TODO: 实现微信登录逻辑
      await Future.delayed(const Duration(seconds: 2)); // 模拟登录过程

      // 登录成功，跳转到主页
      Get.offAllNamed(AppRoutes.main);
      Get.snackbar(
        '登录成功',
        '欢迎使用拍宠有道！',
        snackPosition: SnackPosition.TOP,
        backgroundColor: Colors.green,
        colorText: Colors.white,
      );
    } catch (e) {
      Get.snackbar(
        '登录失败',
        '微信登录失败，请重试',
        snackPosition: SnackPosition.TOP,
        backgroundColor: Colors.red,
        colorText: Colors.white,
      );
    } finally {
      if (mounted) {
        setState(() {
          _isWechatLoading = false;
        });
      }
    }
  }

  // 手机号登录
  void _phoneLogin() {
    if (!_agreedToTerms) {
      Get.snackbar(
        '提示',
        '请先阅读并同意用户协议和隐私政策',
        snackPosition: SnackPosition.TOP,
        backgroundColor: Colors.orange,
        colorText: Colors.white,
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const SMSLoginPage(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Container(
            width: double.infinity,
            padding: EdgeInsets.symmetric(horizontal: 32.w),
            child: Column(
              children: [
                SizedBox(height: 60.h),

                // 顶部标题
                Text(
                  '登录',
                  style: TextStyle(
                    fontSize: 24.sp,
                    fontWeight: FontWeight.w600,
                    color: const Color(0xFF333333),
                  ),
                ),

                SizedBox(height: 80.h),

                // Logo和品牌信息
                Column(
                  children: [
                    // 应用Logo
                    Container(
                      width: 160.w,
                      height: 160.w,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(20.r),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF9C4DFF).withOpacity(0.2),
                            blurRadius: 20,
                            offset: const Offset(0, 8),
                            spreadRadius: 2,
                          ),
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(20.r),
                        child: Image.asset(
                          'assets/images/app_logo.png',
                          width: 160.w,
                          height: 160.w,
                          fit: BoxFit.contain,
                          errorBuilder: (context, error, stackTrace) {
                            // 如果logo加载失败，显示备用图标
                            return Container(
                              width: 160.w,
                              height: 160.w,
                              decoration: BoxDecoration(
                                gradient: const LinearGradient(
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                  colors: [
                                    Color(0xFF9C4DFF),
                                    Color(0xFF7B1FA2),
                                  ],
                                ),
                                borderRadius: BorderRadius.circular(20.r),
                              ),
                              child: Icon(
                                Icons.pets,
                                size: 80.w,
                                color: Colors.white,
                              ),
                            );
                          },
                        ),
                      ),
                    ),

                    SizedBox(height: 32.h),

                    // 品牌名称
                    Text(
                      '拍宠有道',
                      style: TextStyle(
                        fontSize: 32.sp,
                        fontWeight: FontWeight.bold,
                        color: const Color(0xFF333333),
                        letterSpacing: 2.0,
                      ),
                    ),

                    SizedBox(height: 12.h),

                    // 品牌标语
                    Text(
                      '优质服务 更多选择',
                      style: TextStyle(
                        fontSize: 16.sp,
                        color: const Color(0xFF999999),
                        letterSpacing: 1.0,
                      ),
                    ),
                  ],
                ),

                SizedBox(height: 120.h),

                // 登录按钮区域
                Column(
                  children: [
                    // 微信一键登录按钮
                    Container(
                      width: double.infinity,
                      height: 50.h,
                      child: ElevatedButton(
                        onPressed: _isWechatLoading ? null : _wechatLogin,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF9C4DFF),
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shadowColor: Colors.transparent,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(25.r),
                          ),
                        ),
                        child: _isWechatLoading
                            ? SizedBox(
                                width: 20.w,
                                height: 20.w,
                                child: const CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                      Colors.white),
                                ),
                              )
                            : Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.wechat,
                                    size: 20.w,
                                    color: Colors.white,
                                  ),
                                  SizedBox(width: 8.w),
                                  Text(
                                    '微信一键登录',
                                    style: TextStyle(
                                      fontSize: 16.sp,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ],
                              ),
                      ),
                    ),

                    SizedBox(height: 16.h),

                    // 手机号登录按钮
                    Container(
                      width: double.infinity,
                      height: 50.h,
                      child: ElevatedButton(
                        onPressed: _isPhoneLoading ? null : _phoneLogin,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFF5F5F5),
                          foregroundColor: const Color(0xFF333333),
                          elevation: 0,
                          shadowColor: Colors.transparent,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(25.r),
                          ),
                        ),
                        child: _isPhoneLoading
                            ? SizedBox(
                                width: 20.w,
                                height: 20.w,
                                child: const CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                      Color(0xFF333333)),
                                ),
                              )
                            : Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.phone_android,
                                    size: 20.w,
                                    color: const Color(0xFF333333),
                                  ),
                                  SizedBox(width: 8.w),
                                  Text(
                                    '手机号登录',
                                    style: TextStyle(
                                      fontSize: 16.sp,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ],
                              ),
                      ),
                    ),
                  ],
                ),

                SizedBox(height: 80.h),

                // 底部协议勾选
                Row(
                  children: [
                    GestureDetector(
                      onTap: () {
                        setState(() {
                          _agreedToTerms = !_agreedToTerms;
                        });
                      },
                      child: Container(
                        width: 18.w,
                        height: 18.w,
                        decoration: BoxDecoration(
                          color: _agreedToTerms
                              ? const Color(0xFF9C4DFF)
                              : Colors.transparent,
                          border: Border.all(
                            color: _agreedToTerms
                                ? const Color(0xFF9C4DFF)
                                : const Color(0xFFCCCCCC),
                            width: 1.5,
                          ),
                          borderRadius: BorderRadius.circular(3.r),
                        ),
                        child: _agreedToTerms
                            ? Icon(
                                Icons.check,
                                size: 12.w,
                                color: Colors.white,
                              )
                            : null,
                      ),
                    ),
                    SizedBox(width: 8.w),
                    Expanded(
                      child: RichText(
                        text: TextSpan(
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: const Color(0xFF999999),
                          ),
                          children: [
                            const TextSpan(text: '您已阅读并同意 '),
                            TextSpan(
                              text: '《用户协议》',
                              style: TextStyle(
                                color: const Color(0xFF9C4DFF),
                                decoration: TextDecoration.underline,
                              ),
                            ),
                            const TextSpan(text: ' '),
                            TextSpan(
                              text: '《隐私政策》',
                              style: TextStyle(
                                color: const Color(0xFF9C4DFF),
                                decoration: TextDecoration.underline,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),

                SizedBox(height: 60.h),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
