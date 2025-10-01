import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import '../../utils/app_routes.dart';
import '../../services/auth_service.dart';
import 'sms_login_page.dart';
import 'terms_of_service_page.dart';
import 'privacy_policy_page.dart';
import '../../widgets/privacy_consent_dialog.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _authService = AuthService();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isTestAccountMode = false;
  bool _isPhoneLoading = false;
  bool _isPasswordLoading = false;
  bool _agreedToTerms = false; // 默认未同意，需要用户主动同意
  bool _passwordVisible = false;

  @override
  void initState() {
    super.initState();
    _checkAndShowPrivacyConsent();
    // 设置状态栏样式
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
        statusBarBrightness: Brightness.light,
      ),
    );

    // 自动填入测试账号信息
    _fillTestAccount();
  }

  // 自动填入测试账号
  void _fillTestAccount() {
    _phoneController.text = "18888888888";
    _passwordController.text = "111111";
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  // 测试账号密码登录
  void _passwordLogin() async {
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

    final phone = _phoneController.text.trim();
    final password = _passwordController.text.trim();

    if (phone.isEmpty || password.isEmpty) {
      Get.snackbar(
        '提示',
        '请输入手机号和密码',
        snackPosition: SnackPosition.TOP,
        backgroundColor: Colors.orange,
        colorText: Colors.white,
      );
      return;
    }

    setState(() {
      _isPasswordLoading = true;
    });

    try {
      final result = await _authService.login(phone: phone, password: password);

      if (result.success) {
        // 登录成功，跳转到主页
        Get.offAllNamed(AppRoutes.main);
        Get.snackbar(
          '登录成功',
          '欢迎使用拍宠有道！',
          snackPosition: SnackPosition.TOP,
          backgroundColor: Colors.green,
          colorText: Colors.white,
        );
      } else {
        Get.snackbar(
          '登录失败',
          result.message,
          snackPosition: SnackPosition.TOP,
          backgroundColor: Colors.red,
          colorText: Colors.white,
        );
      }
    } catch (e) {
      Get.snackbar(
        '登录失败',
        '登录过程中发生错误，请重试',
        snackPosition: SnackPosition.TOP,
        backgroundColor: Colors.red,
        colorText: Colors.white,
      );
    } finally {
      if (mounted) {
        setState(() {
          _isPasswordLoading = false;
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
                        color: Colors.transparent, // 透明背景，移除白边
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

                // 登录方式选择
                Row(
                  children: [
                    Expanded(
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _isTestAccountMode = false;
                          });
                        },
                        child: Container(
                          padding: EdgeInsets.symmetric(vertical: 12.h),
                          decoration: BoxDecoration(
                            border: Border(
                              bottom: BorderSide(
                                color: !_isTestAccountMode
                                    ? const Color(0xFF9C4DFF)
                                    : Colors.transparent,
                                width: 2,
                              ),
                            ),
                          ),
                          child: Text(
                            '手机验证码登录',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 16.sp,
                              color: !_isTestAccountMode
                                  ? const Color(0xFF9C4DFF)
                                  : const Color(0xFF999999),
                              fontWeight: !_isTestAccountMode
                                  ? FontWeight.w600
                                  : FontWeight.normal,
                            ),
                          ),
                        ),
                      ),
                    ),
                    Expanded(
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _isTestAccountMode = true;
                          });
                        },
                        child: Container(
                          padding: EdgeInsets.symmetric(vertical: 12.h),
                          decoration: BoxDecoration(
                            border: Border(
                              bottom: BorderSide(
                                color: _isTestAccountMode
                                    ? const Color(0xFF9C4DFF)
                                    : Colors.transparent,
                                width: 2,
                              ),
                            ),
                          ),
                          child: Text(
                            '测试账号登录',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 16.sp,
                              color: _isTestAccountMode
                                  ? const Color(0xFF9C4DFF)
                                  : const Color(0xFF999999),
                              fontWeight: _isTestAccountMode
                                  ? FontWeight.w600
                                  : FontWeight.normal,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),

                SizedBox(height: 32.h),

                // 登录表单
                if (_isTestAccountMode) ...[
                  // 测试账号登录表单
                  Column(
                    children: [
                      // 手机号输入框
                      Container(
                        decoration: BoxDecoration(
                          color: const Color(0xFFF8F8F8),
                          borderRadius: BorderRadius.circular(12.r),
                        ),
                        child: TextField(
                          controller: _phoneController,
                          keyboardType: TextInputType.phone,
                          decoration: InputDecoration(
                            hintText: '请输入手机号（测试：18888888888）',
                            hintStyle: TextStyle(
                              color: const Color(0xFF999999),
                              fontSize: 14.sp,
                            ),
                            border: InputBorder.none,
                            contentPadding: EdgeInsets.symmetric(
                              horizontal: 16.w,
                              vertical: 16.h,
                            ),
                            prefixIcon: Icon(
                              Icons.phone_android,
                              color: const Color(0xFF666666),
                              size: 20.w,
                            ),
                          ),
                        ),
                      ),

                      SizedBox(height: 16.h),

                      // 密码输入框
                      Container(
                        decoration: BoxDecoration(
                          color: const Color(0xFFF8F8F8),
                          borderRadius: BorderRadius.circular(12.r),
                        ),
                        child: TextField(
                          controller: _passwordController,
                          obscureText: !_passwordVisible,
                          decoration: InputDecoration(
                            hintText: '请输入密码（测试：111111）',
                            hintStyle: TextStyle(
                              color: const Color(0xFF999999),
                              fontSize: 14.sp,
                            ),
                            border: InputBorder.none,
                            contentPadding: EdgeInsets.symmetric(
                              horizontal: 16.w,
                              vertical: 16.h,
                            ),
                            prefixIcon: Icon(
                              Icons.lock_outline,
                              color: const Color(0xFF666666),
                              size: 20.w,
                            ),
                            suffixIcon: GestureDetector(
                              onTap: () {
                                setState(() {
                                  _passwordVisible = !_passwordVisible;
                                });
                              },
                              child: Icon(
                                _passwordVisible
                                    ? Icons.visibility
                                    : Icons.visibility_off,
                                color: const Color(0xFF666666),
                                size: 20.w,
                              ),
                            ),
                          ),
                        ),
                      ),

                      SizedBox(height: 24.h),

                      // 登录按钮
                      Container(
                        width: double.infinity,
                        height: 50.h,
                        child: ElevatedButton(
                          onPressed: (_isPasswordLoading || !_agreedToTerms)
                              ? null
                              : _passwordLogin,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _agreedToTerms
                                ? const Color(0xFF9C4DFF)
                                : const Color(0xFFCCCCCC),
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shadowColor: Colors.transparent,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(25.r),
                            ),
                          ),
                          child: _isPasswordLoading
                              ? SizedBox(
                                  width: 20.w,
                                  height: 20.w,
                                  child: const CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                        Colors.white),
                                  ),
                                )
                              : Text(
                                  '登录',
                                  style: TextStyle(
                                    fontSize: 16.sp,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                        ),
                      ),
                    ],
                  ),
                ] else ...[
                  // 手机号登录按钮
                  Container(
                    width: double.infinity,
                    height: 50.h,
                    child: ElevatedButton(
                      onPressed: (_isPhoneLoading || !_agreedToTerms)
                          ? null
                          : _phoneLogin,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _agreedToTerms
                            ? const Color(0xFF9C4DFF)
                            : const Color(0xFFCCCCCC),
                        foregroundColor: Colors.white,
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
                                valueColor:
                                    AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.phone_android,
                                  size: 20.w,
                                  color: Colors.white,
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

                SizedBox(height: 80.h),

                // 底部协议勾选
                Row(
                  children: [
                    GestureDetector(
                      onTap: () {
                        if (_agreedToTerms) {
                          // 如果已经同意，点击取消同意
                          setState(() {
                            _agreedToTerms = false;
                          });
                        } else {
                          // 如果未同意，显示隐私政策同意弹窗
                          _showPrivacyConsentDialog();
                        }
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
                      child: Wrap(
                        children: [
                          Text(
                            '我已阅读并同意 ',
                            style: TextStyle(
                              fontSize: 12.sp,
                              color: const Color(0xFF999999),
                            ),
                          ),
                          GestureDetector(
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) =>
                                      const TermsOfServicePage(
                                    showButtons: true,
                                    onAccept: null,
                                    onReject: null,
                                  ),
                                ),
                              );
                            },
                            child: Text(
                              '《用户协议》',
                              style: TextStyle(
                                fontSize: 12.sp,
                                color: const Color(0xFF9C4DFF),
                                decoration: TextDecoration.underline,
                              ),
                            ),
                          ),
                          Text(
                            ' ',
                            style: TextStyle(
                              fontSize: 12.sp,
                              color: const Color(0xFF999999),
                            ),
                          ),
                          GestureDetector(
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => const PrivacyPolicyPage(
                                    showButtons: true,
                                    onAccept: null,
                                    onReject: null,
                                  ),
                                ),
                              );
                            },
                            child: Text(
                              '《隐私政策》',
                              style: TextStyle(
                                fontSize: 12.sp,
                                color: const Color(0xFF9C4DFF),
                                decoration: TextDecoration.underline,
                              ),
                            ),
                          ),
                        ],
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

  // 检查并显示隐私政策同意弹窗
  Future<void> _checkAndShowPrivacyConsent() async {
    final prefs = await SharedPreferences.getInstance();
    final hasAgreedToPrivacy = prefs.getBool('has_agreed_to_privacy') ?? false;

    if (!hasAgreedToPrivacy && mounted) {
      // 延迟一下再显示弹窗，确保页面已经完全加载
      await Future.delayed(const Duration(milliseconds: 500));

      if (mounted) {
        showPrivacyConsentDialog(
          context,
          onAccept: () async {
            // 用户同意
            await prefs.setBool('has_agreed_to_privacy', true);
            setState(() {
              _agreedToTerms = true;
            });
          },
          onReject: () {
            // 用户拒绝，退出应用
            SystemNavigator.pop();
          },
        );
      }
    }
    // 确保每次打开应用都需要用户重新勾选，符合合规要求
    // 注释掉自动设置为true的逻辑
    // else {
    //   // 用户之前已经同意过
    //   setState(() {
    //     _agreedToTerms = true;
    //   });
    // }
  }

  // 显示隐私政策同意弹窗（用于勾选框点击）
  Future<void> _showPrivacyConsentDialog() async {
    showPrivacyConsentDialog(
      context,
      onAccept: () async {
        // 用户同意
        final prefs = await SharedPreferences.getInstance();
        await prefs.setBool('has_agreed_to_privacy', true);
        setState(() {
          _agreedToTerms = true;
        });
      },
      onReject: () {
        // 用户拒绝，勾选框保持未选中状态
        setState(() {
          _agreedToTerms = false;
        });
      },
    );
  }
}
