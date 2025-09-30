import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import '../../services/storage_service.dart';
import '../../services/splash_ad_service.dart';
import '../../utils/app_routes.dart';

class SplashPage extends StatefulWidget {
  const SplashPage({super.key});

  @override
  State<SplashPage> createState() => _SplashPageState();
}

class _SplashPageState extends State<SplashPage> with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  int _currentPageIndex = 0;
  final bool _canSkip = true;
  bool _showSkipButton = false;

  // 广告数据
  Map<String, dynamic>? _adData;
  bool _isLoadingAd = true;

  // 默认启动图片（备用）
  final List<String> _defaultSplashImages = [
    'assets/images/splash_ad.png', // 水质检测剂广告页
    'assets/images/splash_brand.png', // 拍竞有道品牌页
  ];

  @override
  void initState() {
    super.initState();
    _initAnimation();
    // 清除缓存，确保每次都获取最新广告
    SplashAdService.clearCache();
    _loadSplashAd();
  }

  void _initAnimation() {
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeIn,
    ));

    _fadeController.forward();
  }

  /// 加载启动广告
  Future<void> _loadSplashAd() async {
    try {
      print('🚀 开始加载启动广告...');
      final adData = await SplashAdService.getSplashAd();

      if (mounted) {
        setState(() {
          _adData = adData;
          _isLoadingAd = false;
        });

        if (adData != null) {
          print('✅ 成功获取广告数据: ${adData['id']} - ${adData['ad_type']}');
          print('📸 图片URL: ${adData['image_url']}');

          // 记录展示统计
          if (adData['id'] != null) {
            SplashAdService.updateAdStats(adData['id'], 'view');
          }
        } else {
          print('⚠️  未获取到广告数据，将显示默认启动页');
        }

        _startSplashSequence();
      }
    } catch (e) {
      print('❌ 加载启动广告失败: $e');
      if (mounted) {
        setState(() {
          _isLoadingAd = false;
        });
        _startSplashSequence();
      }
    }
  }

  void _startSplashSequence() {
    if (!mounted) return;

    // 根据广告配置或默认值设置显示时长
    final displayDuration = _adData?['display_duration'] ?? 3;
    final skipDelay = _adData?['skip_delay'] ?? 0;
    final skipEnabled = _adData?['skip_enabled'] ?? true;

    // 设置跳过按钮显示
    if (skipEnabled && skipDelay > 0) {
      Future.delayed(Duration(seconds: skipDelay), () {
        if (mounted) {
          setState(() {
            _showSkipButton = true;
          });
        }
      });
    } else if (skipEnabled) {
      setState(() {
        _showSkipButton = true;
      });
    }

    // 第一页（广告页）显示指定时长
    Future.delayed(Duration(seconds: displayDuration), () {
      if (mounted) {
        _fadeController.reverse().then((_) {
          if (mounted) {
            setState(() {
              _currentPageIndex = 1;
              _showSkipButton = true; // 品牌页总是可以跳过
            });
            _fadeController.forward();

            // 第二页显示3秒后跳转
            Future.delayed(const Duration(seconds: 3), () {
              _navigateToNext();
            });
          }
        });
      }
    });
  }

  void _navigateToNext() {
    if (!mounted) return;

    final token = StorageService.getUserToken();
    if (token != null && token.isNotEmpty) {
      Get.offAllNamed(AppRoutes.main);
    } else {
      Get.offAllNamed(AppRoutes.login);
    }
  }

  void _skipSplash() {
    if (_canSkip && _showSkipButton) {
      _navigateToNext();
    }
  }

  void _handleAdClick() {
    if (_adData != null) {
      SplashAdService.handleAdClick(_adData!);
    }
    _navigateToNext();
  }

  /// 构建启动页面内容
  Widget _buildSplashContent() {
    if (_currentPageIndex == 0) {
      // 第一页：显示后台配置的广告或默认广告
      return _buildAdContent();
    } else {
      // 第二页：品牌页面
      return _buildBrandContent();
    }
  }

  /// 构建广告内容
  Widget _buildAdContent() {
    if (_isLoadingAd) {
      // 加载中显示默认背景
      return _buildDefaultBackground();
    }

    if (_adData != null) {
      // 显示后台配置的广告
      final adType = _adData!['ad_type'];

      if (adType == 'image' && _adData!['image_url'] != null) {
        return GestureDetector(
          onTap: _handleAdClick,
          child: Image.network(
            _adData!['image_url'],
            fit: BoxFit.cover,
            errorBuilder: (context, error, stackTrace) {
              print('网络广告图片加载失败: $error');
              return _buildDefaultAdImage();
            },
            loadingBuilder: (context, child, loadingProgress) {
              if (loadingProgress == null) return child;
              return _buildDefaultBackground();
            },
          ),
        );
      } else if (adType == 'video' && _adData!['video_url'] != null) {
        // 视频广告暂时显示占位图
        return GestureDetector(
          onTap: _handleAdClick,
          child: Container(
            color: Colors.black,
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.play_circle_outline,
                    size: 80.w,
                    color: Colors.white,
                  ),
                  SizedBox(height: 16.h),
                  Text(
                    '视频广告',
                    style: TextStyle(
                      fontSize: 18.sp,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }
    }

    // 没有广告数据时显示默认广告图片
    return _buildDefaultAdImage();
  }

  /// 构建品牌内容
  Widget _buildBrandContent() {
    return Image.asset(
      _defaultSplashImages[1], // 品牌页
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        return _buildDefaultBackground();
      },
    );
  }

  /// 构建默认广告图片
  Widget _buildDefaultAdImage() {
    return Image.asset(
      _defaultSplashImages[0], // 默认广告页
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        return _buildDefaultBackground();
      },
    );
  }

  /// 构建默认背景
  Widget _buildDefaultBackground() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0xFF9C4DFF),
            Color(0xFF7B1FA2),
          ],
        ),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(
              width: 100.w,
              height: 100.w,
              child: Icon(
                Icons.pets,
                size: 80.w,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 24.h),
            Text(
              '拍宠有道',
              style: TextStyle(
                fontSize: 28.sp,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 8.h),
            Text(
              '专业宠物拍卖平台',
              style: TextStyle(
                fontSize: 16.sp,
                color: Colors.white70,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: GestureDetector(
        onTap: _skipSplash,
        child: Stack(
          children: [
            // 启动页面图片
            // 启动页面内容
            FadeTransition(
              opacity: _fadeAnimation,
              child: Container(
                width: double.infinity,
                height: double.infinity,
                child: _buildSplashContent(),
              ),
            ),

            // 跳过按钮（根据广告配置显示）
            if (_showSkipButton)
              Positioned(
                top: MediaQuery.of(context).padding.top + 16.h,
                right: 16.w,
                child: GestureDetector(
                  onTap: _skipSplash,
                  child: Container(
                    padding:
                        EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.3),
                      borderRadius: BorderRadius.circular(20.r),
                    ),
                    child: Text(
                      '跳过',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 14.sp,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ),
              ),

            // 页面指示器
            Positioned(
              bottom: 60.h,
              left: 0,
              right: 0,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(
                  2, // 固定2页：广告页 + 品牌页
                  (index) => Container(
                    width: 8.w,
                    height: 8.w,
                    margin: EdgeInsets.symmetric(horizontal: 4.w),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: _currentPageIndex == index
                          ? Colors.white
                          : Colors.white.withValues(alpha: 0.3),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
