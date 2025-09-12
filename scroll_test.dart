import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: ScrollTestPage(),
    );
  }
}

class ScrollTestPage extends StatefulWidget {
  @override
  _ScrollTestPageState createState() => _ScrollTestPageState();
}

class _ScrollTestPageState extends State<ScrollTestPage> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('滚动测试')),
      body: Column(
        children: [
          // Tab按钮
          Row(
            children: [
              ElevatedButton(
                onPressed: () => setState(() => _currentIndex = 0),
                child: Text('首页'),
              ),
              ElevatedButton(
                onPressed: () => setState(() => _currentIndex = 1),
                child: Text('其他'),
              ),
            ],
          ),
          
          // 内容区域
          Expanded(
            child: IndexedStack(
              index: _currentIndex,
              children: [
                // 首页 - 应该可以滚动
                Scrollbar(
                  child: SingleChildScrollView(
                    physics: AlwaysScrollableScrollPhysics(),
                    child: Column(
                      children: [
                        Container(height: 200, color: Colors.red, child: Center(child: Text('轮播图区域'))),
                        Container(height: 200, color: Colors.green, child: Center(child: Text('功能网格区域'))),
                        Container(height: 300, color: Colors.blue, child: Center(child: Text('限时拍卖区域'))),
                        Container(height: 200, color: Colors.yellow, child: Center(child: Text('更多内容'))),
                        Container(height: 100, color: Colors.grey, child: Center(child: Text('底部内容'))),
                      ],
                    ),
                  ),
                ),
                
                // 其他页面
                Center(child: Text('其他页面内容')),
              ],
            ),
          ),
        ],
      ),
    );
  }
}