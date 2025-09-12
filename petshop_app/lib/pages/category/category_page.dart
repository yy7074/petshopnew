import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class CategoryPage extends StatefulWidget {
  const CategoryPage({super.key});

  @override
  State<CategoryPage> createState() => _CategoryPageState();
}

class _CategoryPageState extends State<CategoryPage> {
  int selectedMainCategoryIndex = 0;
  String searchQuery = '';

  // 主分类列表
  final List<Map<String, dynamic>> mainCategories = [
    {'name': '猫咪', 'icon': Icons.pets},
    {'name': '狗狗', 'icon': Icons.pets},
    {'name': '爬宠', 'icon': Icons.pets},
    {'name': '小宠', 'icon': Icons.pets},
    {'name': '鹦鹉', 'icon': Icons.pets},
    {'name': '鸟类', 'icon': Icons.pets},
    {'name': '昆虫', 'icon': Icons.pets},
    {'name': '大型宠物', 'icon': Icons.pets},
    {'name': '变异宠物', 'icon': Icons.pets},
  ];

  // 子分类数据
  final Map<String, List<String>> subCategories = {
    '猫咪': [
      '蓝白',
      '蓝猫',
      '金渐层',
      '银渐层',
      '纯白猫',
      '虎斑',
      '加白',
      '橘猫',
      '狸花猫',
      '奶牛猫',
      '三花猫',
      '黑猫',
      '布偶',
      '缅因',
      '波斯猫',
      '金吉拉',
      '拿破仑',
      '无毛猫',
      '德文卷毛',
      '豹猫',
      '美国卷耳猫',
      '矮脚猫',
      '暹罗猫',
      '挪威森林猫'
    ],
    '狗狗': [
      '金毛',
      '拉布拉多',
      '哈士奇',
      '萨摩耶',
      '阿拉斯加',
      '边牧',
      '德牧',
      '泰迪',
      '比熊',
      '博美',
      '柯基',
      '法斗',
      '英斗',
      '雪纳瑞',
      '贵宾',
      '吉娃娃'
    ],
    '爬宠': ['蜥蜴', '蛇类', '龟类', '蛙类', '壁虎', '变色龙', '鬣蜥', '守宫'],
    '小宠': ['仓鼠', '荷兰猪', '兔子', '龙猫', '松鼠', '刺猬', '花枝鼠', '沙鼠'],
    '鹦鹉': ['虎皮鹦鹉', '玄凤鹦鹉', '牡丹鹦鹉', '和尚鹦鹉', '太阳锥尾', '灰鹦鹉', '金刚鹦鹉', '小太阳'],
    '鸟类': ['文鸟', '珍珠鸟', '金丝雀', '画眉', '八哥', '鹩哥', '百灵', '云雀'],
    '昆虫': ['甲虫', '螳螂', '竹节虫', '蝴蝶', '蛾子', '蟋蟀', '螽斯', '天牛'],
    '大型宠物': ['马', '驴', '羊', '猪', '牛', '鹿', '骆驼', '鸵鸟'],
    '变异宠物': ['白化', '黑化', '黄化', '蓝化', '派特', '珍珠', '肉桂', '橄榄'],
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: SafeArea(
        child: Column(
          children: [
            // 搜索栏
            _buildSearchBar(),

            // 主内容区域
            Expanded(
              child: Row(
                children: [
                  // 左侧主分类导航
                  _buildMainCategoryList(),

                  // 右侧子分类内容
                  _buildSubCategoryContent(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建搜索栏
  Widget _buildSearchBar() {
    return Container(
      margin: EdgeInsets.all(16.w),
      height: 40.h,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          SizedBox(width: 16.w),
          Icon(
            Icons.search,
            size: 20.w,
            color: const Color(0xFF999999),
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: TextField(
              decoration: const InputDecoration(
                hintText: '搜索产品',
                hintStyle: TextStyle(
                  color: Color(0xFF999999),
                ),
                border: InputBorder.none,
              ),
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF333333),
              ),
              onChanged: (value) {
                setState(() {
                  searchQuery = value;
                });
              },
            ),
          ),
        ],
      ),
    );
  }

  // 构建左侧主分类列表
  Widget _buildMainCategoryList() {
    return Container(
      width: 100.w, // 固定宽度
      color: Colors.white,
      child: ListView.builder(
        itemCount: mainCategories.length,
        itemBuilder: (context, index) {
          final category = mainCategories[index];
          final isSelected = index == selectedMainCategoryIndex;

          return GestureDetector(
            onTap: () {
              setState(() {
                selectedMainCategoryIndex = index;
              });
            },
            child: Container(
              height: 50.h,
              decoration: BoxDecoration(
                color: isSelected ? const Color(0xFF9C4DFF) : Colors.white,
                border: isSelected
                    ? const Border(
                        left: BorderSide(
                          color: Color(0xFF9C4DFF),
                          width: 3,
                        ),
                      )
                    : null,
              ),
              child: Center(
                child: Text(
                  category['name'],
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: isSelected ? Colors.white : const Color(0xFF333333),
                    fontWeight:
                        isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  // 构建右侧子分类内容
  Widget _buildSubCategoryContent() {
    final selectedCategory = mainCategories[selectedMainCategoryIndex]['name'];
    final subCats = subCategories[selectedCategory] ?? [];

    return Expanded(
      child: Container(
        color: const Color(0xFFF5F5F5),
        padding: EdgeInsets.all(16.w),
        child: GridView.builder(
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3, // 3列布局
            crossAxisSpacing: 12.w,
            mainAxisSpacing: 12.h,
            childAspectRatio: 2.5, // 调整宽高比
          ),
          itemCount: subCats.length,
          itemBuilder: (context, index) {
            final subCat = subCats[index];
            return GestureDetector(
              onTap: () {
                // 这里可以处理子分类点击事件
                print('点击了子分类: $subCat');
              },
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8.r),
                  border: Border.all(
                    color: const Color(0xFFE0E0E0),
                    width: 1,
                  ),
                ),
                child: Center(
                  child: Text(
                    subCat,
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: const Color(0xFF333333),
                      fontWeight: FontWeight.w500,
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
