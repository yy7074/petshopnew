import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import 'package:provider/provider.dart';

import 'constants/app_theme.dart';
import 'pages/splash/splash_page.dart';
import 'services/api_service.dart';
import 'services/storage_service.dart';
import 'utils/app_routes.dart';
import 'utils/system_ui_helper.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 初始化本地存储
  await StorageService.init();

  // 使用系统UI帮助类设置样式
  SystemUIHelper.resetSystemUI();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ScreenUtilInit(
      designSize: const Size(375, 812),
      minTextAdapt: true,
      splitScreenMode: true,
      builder: (context, child) {
        return MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => ApiService()),
          ],
          child: GetMaterialApp(
            title: '拍宠有道',
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: ThemeMode.light,
            home: const SplashPage(),
            getPages: AppRoutes.routes,
            debugShowCheckedModeBanner: false,
            defaultTransition: Transition.cupertino,
            transitionDuration: const Duration(milliseconds: 300),
          ),
        );
      },
    );
  }
}
