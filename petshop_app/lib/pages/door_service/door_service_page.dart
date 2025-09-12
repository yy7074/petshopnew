import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../constants/app_colors.dart';

class DoorServicePage extends StatefulWidget {
  const DoorServicePage({super.key});

  @override
  State<DoorServicePage> createState() => _DoorServicePageState();
}

class _DoorServicePageState extends State<DoorServicePage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ScrollController _scrollController = ScrollController();

  // 宠物洗澡服务数据
  final List<Map<String, dynamic>> _petGroomingServices = [
    {
      'id': '1',
      'shopName': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=1001',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'address': '历下区经十路与舜义路碧桂园凤凰中心b座116室',
      'distance': '距您1.2千米',
      'services': [
        {'name': '【猫咪洗澡】猫咪基础洗护，不限体重', 'price': 50},
        {'name': '【狗狗洗澡】狗狗基础洗护，0-1.5kg', 'price': 50},
      ],
    },
    {
      'id': '2',
      'shopName': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=1002',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'address': '历下区经十路与舜义路碧桂园凤凰中心b座116室',
      'distance': '距您1.2千米',
      'services': [
        {'name': '【猫咪洗澡】猫咪基础洗护，不限体重', 'price': 50},
        {'name': '【狗狗洗澡】狗狗基础洗护，0-1.5kg', 'price': 50},
      ],
    },
    {
      'id': '3',
      'shopName': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=1003',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'address': '历下区经十路与舜义路碧桂园凤凰中心b座116室',
      'distance': '距您1.2千米',
      'services': [
        {'name': '【猫咪洗澡】猫咪基础洗护，不限体重', 'price': 50},
        {'name': '【狗狗洗澡】狗狗基础洗护，0-1.5kg', 'price': 50},
      ],
    },
    {
      'id': '4',
      'shopName': '招财猫旺财狗',
      'avatar': 'https://picsum.photos/60/60?random=1004',
      'rating': 4.0,
      'followers': '4.4万粉丝',
      'address': '历下区经十路与舜义路碧桂园凤凰中心b座116室',
      'distance': '距您1.2千米',
      'services': [
        {'name': '【猫咪洗澡】猫咪基础洗护，不限体重', 'price': 50},
        {'name': '【狗狗洗澡】狗狗基础洗护，0-1.5kg', 'price': 50},
      ],
    },
  ];

  // 鱼缸造景服务数据
  final List<Map<String, dynamic>> _aquariumDesignServices = [
    {
      'id': '1',
      'shopName': '水族专家工作室',
      'avatar': 'https://picsum.photos/60/60?random=1101',
      'rating': 4.5,
      'followers': '3.2万粉丝',
      'address': '市中区泉城路188号水族城2楼',
      'distance': '距您2.5千米',
      'services': [
        {'name': '【鱼缸造景】淡水缸基础造景，包材料', 'price': 200},
        {'name': '【水草造景】专业水草造景设计', 'price': 150},
      ],
    },
    {
      'id': '2',
      'shopName': '海洋世界造景',
      'avatar': 'https://picsum.photos/60/60?random=1102',
      'rating': 4.2,
      'followers': '2.8万粉丝',
      'address': '历城区工业南路海洋城3楼',
      'distance': '距您3.1千米',
      'services': [
        {'name': '【海水缸造景】海水缸专业造景', 'price': 350},
        {'name': '【珊瑚缸造景】珊瑚缸定制造景', 'price': 480},
      ],
    },
  ];

  // 鱼缸维修服务数据
  final List<Map<String, dynamic>> _aquariumRepairServices = [
    {
      'id': '1',
      'shopName': '专业鱼缸维修',
      'avatar': 'https://picsum.photos/60/60?random=1201',
      'rating': 4.3,
      'followers': '1.5万粉丝',
      'address': '槐荫区经四路鱼缸维修中心',
      'distance': '距您1.8千米',
      'services': [
        {'name': '【鱼缸漏水维修】专业补漏，质保1年', 'price': 80},
        {'name': '【过滤系统维修】过滤设备检修', 'price': 60},
      ],
    },
    {
      'id': '2',
      'shopName': '水族设备维护',
      'avatar': 'https://picsum.photos/60/60?random=1202',
      'rating': 4.1,
      'followers': '8800粉丝',
      'address': '天桥区无影山路水族维修部',
      'distance': '距您4.2千米',
      'services': [
        {'name': '【加热棒更换】专业加热设备更换', 'price': 40},
        {'name': '【水泵维修】各类水泵检修保养', 'price': 70},
      ],
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.black87),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          '上门服务',
          style: TextStyle(
            color: Colors.black87,
            fontSize: 18.sp,
            fontWeight: FontWeight.w600,
          ),
        ),
        bottom: PreferredSize(
          preferredSize: Size.fromHeight(50.h),
          child: Container(
            color: Colors.white,
            child: TabBar(
              controller: _tabController,
              indicatorColor: AppColors.primary,
              indicatorWeight: 3.0,
              indicatorSize: TabBarIndicatorSize.label,
              labelColor: AppColors.primary,
              unselectedLabelColor: Colors.grey[600],
              labelStyle: TextStyle(
                fontSize: 16.sp,
                fontWeight: FontWeight.w600,
              ),
              unselectedLabelStyle: TextStyle(
                fontSize: 16.sp,
                fontWeight: FontWeight.normal,
              ),
              tabs: const [
                Tab(text: '宠物洗澡'),
                Tab(text: '鱼缸造景'),
                Tab(text: '鱼缸维修'),
              ],
            ),
          ),
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildServiceList(_petGroomingServices),
          _buildServiceList(_aquariumDesignServices),
          _buildServiceList(_aquariumRepairServices),
        ],
      ),
    );
  }

  Widget _buildServiceList(List<Map<String, dynamic>> services) {
    return ListView.builder(
      controller: _scrollController,
      padding: EdgeInsets.all(16.w),
      itemCount: services.length,
      itemBuilder: (context, index) {
        final service = services[index];
        return _buildServiceCard(service);
      },
    );
  }

  Widget _buildServiceCard(Map<String, dynamic> service) {
    final services = service['services'] as List<Map<String, dynamic>>;

    return Container(
      margin: EdgeInsets.only(bottom: 16.h),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.08),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 服务商头部信息
            Row(
              children: [
                CircleAvatar(
                  radius: 30.r,
                  backgroundImage: NetworkImage(service['avatar']),
                ),
                SizedBox(width: 12.w),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        service['shopName'],
                        style: TextStyle(
                          fontSize: 16.sp,
                          fontWeight: FontWeight.w600,
                          color: Colors.black87,
                        ),
                      ),
                      SizedBox(height: 4.h),
                      Row(
                        children: [
                          // 星级评分
                          ...List.generate(5, (index) {
                            return Icon(
                              index < service['rating'].floor()
                                  ? Icons.star
                                  : Icons.star_border,
                              color: const Color(0xFFFFB74D),
                              size: 14.sp,
                            );
                          }),
                          SizedBox(width: 8.w),
                          Text(
                            service['followers'],
                            style: TextStyle(
                              fontSize: 12.sp,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 6.h),
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.circular(15.r),
                  ),
                  child: Text(
                    '进店',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12.sp,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),

            SizedBox(height: 12.h),

            // 地址信息
            GestureDetector(
              onTap: () {
                // TODO: 打开地图导航
              },
              child: Container(
                padding: EdgeInsets.all(12.w),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: BorderRadius.circular(8.r),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.location_on,
                      size: 16.sp,
                      color: Colors.grey[600],
                    ),
                    SizedBox(width: 8.w),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            service['address'],
                            style: TextStyle(
                              fontSize: 14.sp,
                              color: Colors.black87,
                            ),
                          ),
                          SizedBox(height: 2.h),
                          Text(
                            service['distance'],
                            style: TextStyle(
                              fontSize: 12.sp,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ),
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 14.sp,
                      color: Colors.grey[400],
                    ),
                  ],
                ),
              ),
            ),

            SizedBox(height: 16.h),

            // 服务项目列表
            ...services.map((serviceItem) => _buildServiceItem(serviceItem)).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildServiceItem(Map<String, dynamic> serviceItem) {
    return Container(
      margin: EdgeInsets.only(bottom: 12.h),
      child: Row(
        children: [
          Text(
            '¥${serviceItem['price']}',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.w600,
              color: AppColors.primary,
            ),
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: Text(
              serviceItem['name'],
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.black87,
                height: 1.3,
              ),
            ),
          ),
          GestureDetector(
            onTap: () {
              // TODO: 预约服务
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('预约 ${serviceItem['name']} 成功！'),
                  backgroundColor: AppColors.primary,
                ),
              );
            },
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h),
              decoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12.r),
                border: Border.all(color: AppColors.primary, width: 1),
              ),
              child: Text(
                '预约',
                style: TextStyle(
                  color: AppColors.primary,
                  fontSize: 12.sp,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}