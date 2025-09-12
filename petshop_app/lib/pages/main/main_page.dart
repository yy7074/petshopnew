import 'package:flutter/material.dart';
import '../../widgets/custom_bottom_nav.dart';
import '../home/home_page.dart';
import '../category/category_page.dart';
import '../message/message_page.dart';
import '../profile/profile_page.dart';
import '../publish/publish_page.dart';

class MainPage extends StatefulWidget {
  const MainPage({super.key});

  @override
  State<MainPage> createState() => _MainPageState();
}

class _MainPageState extends State<MainPage> {
  int _currentIndex = 0;
  late PageController _pageController;

  final List<Widget> _pages = [
    const HomePage(), // 0: 首页
    const CategoryPage(), // 1: 分类
    const MessagePage(), // 2: 消息（原来的index 3）
    const ProfilePage(), // 3: 我的（原来的index 4）
  ];

  @override
  void initState() {
    super.initState();
    _pageController = PageController(initialPage: 0);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PageView(
        controller: _pageController,
        physics: const NeverScrollableScrollPhysics(), // 禁用PageView的滑动
        onPageChanged: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        children: _pages,
      ),
      bottomNavigationBar: CustomBottomNav(
        currentIndex: _currentIndex,
        onTap: (index) {
          if (index == 2) {
            // 中间按钮 - 导航到发布页面
            Navigator.of(context).push(
              MaterialPageRoute(builder: (context) => const PublishPage()),
            );
          } else {
            // 其他按钮 - 切换tab
            setState(() {
              // 重新映射索引：消息和我的页面的索引需要调整
              if (index >= 3) {
                _currentIndex = index - 1; // 消息(3->2), 我的(4->3)
              } else {
                _currentIndex = index; // 首页(0), 分类(1)
              }
              _pageController.animateToPage(
                _currentIndex,
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeInOut,
              );
            });
          }
        },
      ),
      extendBody: true,
    );
  }
}
