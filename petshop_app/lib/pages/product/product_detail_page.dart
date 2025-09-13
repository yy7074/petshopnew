import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:card_swiper/card_swiper.dart';
import '../../constants/app_colors.dart';

class ProductDetailPage extends StatefulWidget {
  final Map<String, dynamic>? productData;

  const ProductDetailPage({super.key, this.productData});

  @override
  State<ProductDetailPage> createState() => _ProductDetailPageState();
}

class _ProductDetailPageState extends State<ProductDetailPage> {
  int currentImageIndex = 0;
  final TextEditingController _bidController = TextEditingController();
  final TextEditingController _messageController = TextEditingController();

  final List<String> productImages = [
    'assets/images/aquarium1.jpg',
    'assets/images/aquarium2.jpg',
    'assets/images/aquarium3.jpg',
  ];

  final List<Map<String, dynamic>> bidHistory = [
    {'user': '用户A', 'price': 450, 'time': '23:45'},
    {'user': '用户B', 'price': 440, 'time': '23:40'},
    {'user': '用户C', 'price': 435, 'time': '23:35'},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: Colors.black, size: 20.w),
          onPressed: () => Navigator.pop(context),
        ),
        title: Row(
          children: [
            CircleAvatar(
              radius: 16.w,
              backgroundImage: const AssetImage('assets/images/avatar1.jpg'),
            ),
            SizedBox(width: 8.w),
            Text(
              '招财猫旺财狗',
              style: TextStyle(
                color: Colors.black,
                fontSize: 16.sp,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              // Navigate to store
            },
            child: Text(
              '进店',
              style: TextStyle(
                color: Colors.blue,
                fontSize: 14.sp,
              ),
            ),
          ),
          SizedBox(width: 16.w),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Product Image Swiper
                  Container(
                    height: 300.h,
                    child: Stack(
                      children: [
                        Swiper(
                          itemCount: productImages.length,
                          itemBuilder: (context, index) {
                            return Container(
                              margin: EdgeInsets.symmetric(horizontal: 16.w),
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(8.w),
                                image: const DecorationImage(
                                  image: AssetImage('assets/images/aquarium1.jpg'),
                                  fit: BoxFit.cover,
                                ),
                              ),
                            );
                          },
                          pagination: SwiperPagination(
                            builder: DotSwiperPaginationBuilder(
                              color: Colors.white.withOpacity(0.5),
                              activeColor: Colors.white,
                              size: 6.w,
                              activeSize: 6.w,
                            ),
                          ),
                          onIndexChanged: (index) {
                            setState(() {
                              currentImageIndex = index;
                            });
                          },
                        ),
                      ],
                    ),
                  ),
                  
                  // Service Guarantee Banner
                  Container(
                    margin: EdgeInsets.all(16.w),
                    padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
                    decoration: BoxDecoration(
                      color: Colors.purple.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8.w),
                      border: Border.all(color: Colors.purple.withOpacity(0.3)),
                    ),
                    child: GestureDetector(
                      onTap: () => _showServiceGuarantee(),
                      child: Row(
                        children: [
                          Icon(
                            Icons.verified_user,
                            color: Colors.purple,
                            size: 16.w,
                          ),
                          SizedBox(width: 8.w),
                          Expanded(
                            child: Text(
                              '服务保障 · 无理由退货免税 · 包邮 · 商品审核 · ...',
                              style: TextStyle(
                                color: Colors.purple,
                                fontSize: 12.sp,
                              ),
                            ),
                          ),
                          Icon(
                            Icons.arrow_forward_ios,
                            color: Colors.purple,
                            size: 12.w,
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Product Info
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16.w),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '宠物标题宠物标题宠物标题宠物标题宠物标题宠物标题',
                          style: TextStyle(
                            fontSize: 16.sp,
                            fontWeight: FontWeight.w600,
                            height: 1.4,
                          ),
                        ),
                        SizedBox(height: 8.h),
                        Row(
                          children: [
                            Container(
                              padding: EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
                              decoration: BoxDecoration(
                                color: Colors.orange,
                                borderRadius: BorderRadius.circular(2.w),
                              ),
                              child: Text(
                                '包邮',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 10.sp,
                                ),
                              ),
                            ),
                          ],
                        ),
                        SizedBox(height: 12.h),
                        Row(
                          children: [
                            Text(
                              '当前竞价:',
                              style: TextStyle(
                                fontSize: 14.sp,
                                color: Colors.grey[600],
                              ),
                            ),
                            SizedBox(width: 8.w),
                            Text(
                              '¥432',
                              style: TextStyle(
                                fontSize: 24.sp,
                                color: Colors.red,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Spacer(),
                            GestureDetector(
                              onTap: () => _showBidHistory(),
                              child: Text(
                                '查看详情',
                                style: TextStyle(
                                  fontSize: 14.sp,
                                  color: Colors.blue,
                                ),
                              ),
                            ),
                          ],
                        ),
                        SizedBox(height: 8.h),
                        Text(
                          '加价幅度不低于: ¥8',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: Colors.grey[600],
                          ),
                        ),
                        SizedBox(height: 16.h),
                        Row(
                          children: [
                            Icon(
                              Icons.star,
                              color: Colors.orange,
                              size: 16.w,
                            ),
                            SizedBox(width: 4.w),
                            Text(
                              '竞拍火热，加价确底不慎',
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

                  SizedBox(height: 24.h),

                  // Bid History
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16.w),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '竞拍记录',
                          style: TextStyle(
                            fontSize: 16.sp,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        SizedBox(height: 12.h),
                        ...bidHistory.map((bid) => Container(
                          padding: EdgeInsets.symmetric(vertical: 8.h),
                          child: Row(
                            children: [
                              CircleAvatar(
                                radius: 16.w,
                                child: Text(
                                  bid['user'][2],
                                  style: TextStyle(fontSize: 12.sp),
                                ),
                              ),
                              SizedBox(width: 12.w),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      bid['user'],
                                      style: TextStyle(
                                        fontSize: 14.sp,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                    Text(
                                      '出价 ¥${bid['price']}',
                                      style: TextStyle(
                                        fontSize: 12.sp,
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Text(
                                bid['time'],
                                style: TextStyle(
                                  fontSize: 12.sp,
                                  color: Colors.grey[500],
                                ),
                              ),
                            ],
                          ),
                        )).toList(),
                      ],
                    ),
                  ),

                  SizedBox(height: 100.h),
                ],
              ),
            ),
          ),
          
          // Bottom Action Bar
          Container(
            padding: EdgeInsets.all(16.w),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: SafeArea(
              child: Row(
                children: [
                  GestureDetector(
                    onTap: () => _showChatDialog(),
                    child: Container(
                      padding: EdgeInsets.symmetric(horizontal: 24.w, vertical: 12.h),
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.purple),
                        borderRadius: BorderRadius.circular(20.w),
                      ),
                      child: Text(
                        '咨询',
                        style: TextStyle(
                          color: Colors.purple,
                          fontSize: 14.sp,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: GestureDetector(
                      onTap: () => _showBiddingDialog(),
                      child: Container(
                        padding: EdgeInsets.symmetric(vertical: 16.h),
                        decoration: BoxDecoration(
                          color: Colors.purple,
                          borderRadius: BorderRadius.circular(25.w),
                        ),
                        child: Center(
                          child: Text(
                            '我要出价',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 16.sp,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showServiceGuarantee() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.8,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20.w),
            topRight: Radius.circular(20.w),
          ),
        ),
        child: Column(
          children: [
            Container(
              padding: EdgeInsets.all(20.w),
              decoration: BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: Colors.grey.shade200),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.security,
                    color: Colors.purple,
                    size: 24.w,
                  ),
                  SizedBox(width: 8.w),
                  Text(
                    '平台保障',
                    style: TextStyle(
                      fontSize: 18.sp,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Spacer(),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: Icon(Icons.close),
                  ),
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.all(20.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '放心参拍，售后无忧，宠物通义为您保驾护航',
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: Colors.grey[600],
                      ),
                    ),
                    SizedBox(height: 24.h),
                    
                    _buildGuaranteeItem(
                      icon: Icons.assignment_return,
                      title: '无理由退货退款',
                      subtitle: '在符合无理由退货标准的情况下可申请无理由退货',
                      description: '特别注意：无实际责任的门费不支持退货退款。',
                    ),
                    
                    _buildGuaranteeItem(
                      icon: Icons.local_shipping,
                      title: '包邮',
                      subtitle: '全平台所有商品，非偏远地区包邮发货发货家(新疆、西藏地区',
                      description: '需要补运费35-50元费用)',
                    ),
                    
                    _buildGuaranteeItem(
                      icon: Icons.search,
                      title: '商品审核',
                      subtitle: '平台审核部审核动品，售后售后且均受到放心心保障',
                      description: '',
                    ),
                    
                    _buildGuaranteeItem(
                      icon: Icons.verified,
                      title: '拍宠有道官方认定',
                      subtitle: '本商品已被拍宠有道官方认定，已购买保险，请放心心拍',
                      description: '',
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGuaranteeItem({
    required IconData icon,
    required String title,
    required String subtitle,
    required String description,
  }) {
    return Container(
      margin: EdgeInsets.only(bottom: 24.h),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(8.w),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: Colors.grey[600], size: 20.w),
              SizedBox(width: 12.w),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                color: Colors.grey[400],
                size: 12.w,
              ),
            ],
          ),
          if (subtitle.isNotEmpty) ...[
            SizedBox(height: 8.h),
            Text(
              subtitle,
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.grey[700],
              ),
            ),
          ],
          if (description.isNotEmpty) ...[
            SizedBox(height: 4.h),
            Text(
              description,
              style: TextStyle(
                fontSize: 12.sp,
                color: Colors.grey[500],
              ),
            ),
          ],
        ],
      ),
    );
  }

  void _showBiddingDialog() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20.w),
            topRight: Radius.circular(20.w),
          ),
        ),
        child: Column(
          children: [
            Container(
              padding: EdgeInsets.all(20.w),
              decoration: BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: Colors.grey.shade200),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    width: 60.w,
                    height: 60.w,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8.w),
                      image: const DecorationImage(
                        image: AssetImage('assets/images/aquarium1.jpg'),
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '宠物标题宠物标题宠物标题宠物标...',
                          style: TextStyle(
                            fontSize: 14.sp,
                            fontWeight: FontWeight.w500,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        SizedBox(height: 4.h),
                        Container(
                          padding: EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
                          decoration: BoxDecoration(
                            color: Colors.orange,
                            borderRadius: BorderRadius.circular(2.w),
                          ),
                          child: Text(
                            '包邮',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 10.sp,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: Icon(Icons.close),
                  ),
                ],
              ),
            ),
            
            Expanded(
              child: Padding(
                padding: EdgeInsets.all(20.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          '当前竞价:',
                          style: TextStyle(
                            fontSize: 16.sp,
                            color: Colors.grey[600],
                          ),
                        ),
                        SizedBox(width: 8.w),
                        Text(
                          '¥432',
                          style: TextStyle(
                            fontSize: 24.sp,
                            color: Colors.red,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Spacer(),
                        IconButton(
                          onPressed: () => Navigator.pop(context),
                          icon: Icon(Icons.close),
                        ),
                      ],
                    ),
                    SizedBox(height: 8.h),
                    Text(
                      '加价幅度不低于50%',
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: Colors.grey[600],
                      ),
                    ),
                    SizedBox(height: 24.h),
                    
                    Row(
                      children: [
                        Icon(
                          Icons.warning,
                          color: Colors.orange,
                          size: 16.w,
                        ),
                        SizedBox(width: 8.w),
                        Text(
                          '竞拍火热，加价确底不慎:',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: Colors.grey[600],
                          ),
                        ),
                        SizedBox(width: 4.w),
                        Text(
                          '¥8',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: Colors.red,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                    
                    SizedBox(height: 24.h),
                    
                    Row(
                      children: [
                        Expanded(
                          child: GestureDetector(
                            onTap: () => setState(() => _bidController.text = '440'),
                            child: Container(
                              padding: EdgeInsets.symmetric(vertical: 12.h),
                              decoration: BoxDecoration(
                                border: Border.all(
                                  color: _bidController.text == '440' ? Colors.red : Colors.grey.shade300,
                                ),
                                borderRadius: BorderRadius.circular(6.w),
                              ),
                              child: Center(
                                child: Text(
                                  '¥440',
                                  style: TextStyle(
                                    color: _bidController.text == '440' ? Colors.red : Colors.black,
                                    fontSize: 14.sp,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                        SizedBox(width: 12.w),
                        Expanded(
                          child: GestureDetector(
                            onTap: () => setState(() => _bidController.text = '448'),
                            child: Container(
                              padding: EdgeInsets.symmetric(vertical: 12.h),
                              decoration: BoxDecoration(
                                border: Border.all(
                                  color: _bidController.text == '448' ? Colors.red : Colors.grey.shade300,
                                ),
                                borderRadius: BorderRadius.circular(6.w),
                              ),
                              child: Center(
                                child: Text(
                                  '¥448',
                                  style: TextStyle(
                                    color: _bidController.text == '448' ? Colors.red : Colors.black,
                                    fontSize: 14.sp,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                        SizedBox(width: 12.w),
                        Expanded(
                          child: Container(
                            padding: EdgeInsets.symmetric(vertical: 12.h),
                            decoration: BoxDecoration(
                              border: Border.all(color: Colors.grey.shade300),
                              borderRadius: BorderRadius.circular(6.w),
                            ),
                            child: Center(
                              child: Text(
                                '其他价格 >',
                                style: TextStyle(
                                  fontSize: 12.sp,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            
            Container(
              padding: EdgeInsets.all(20.w),
              child: Column(
                children: [
                  GestureDetector(
                    onTap: () {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('出价成功！')),
                      );
                    },
                    child: Container(
                      width: double.infinity,
                      padding: EdgeInsets.symmetric(vertical: 16.h),
                      decoration: BoxDecoration(
                        color: Colors.purple,
                        borderRadius: BorderRadius.circular(25.w),
                      ),
                      child: Center(
                        child: Text(
                          '确定出价',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16.sp,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(height: 12.h),
                  Row(
                    children: [
                      Icon(
                        Icons.check_circle,
                        color: Colors.purple,
                        size: 16.w,
                      ),
                      SizedBox(width: 8.w),
                      Text(
                        '本次选择确定出价',
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
          ],
        ),
      ),
    );
  }

  void _showChatDialog() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatPage(),
      ),
    );
  }

  void _showBidHistory() {
    // Show bid history modal
  }
}

class ChatPage extends StatefulWidget {
  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> messages = [
    {
      'isUser': false,
      'message': '发什么快递呀',
      'time': '23:44',
      'status': '已读',
    },
    {
      'isUser': true,
      'message': '都可以的亲',
      'time': '23:45',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: Colors.black, size: 20.w),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          '招财猫旺财狗',
          style: TextStyle(
            color: Colors.black,
            fontSize: 16.sp,
            fontWeight: FontWeight.w500,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {},
            child: Text(
              '进店',
              style: TextStyle(
                color: Colors.blue,
                fontSize: 14.sp,
              ),
            ),
          ),
          SizedBox(width: 16.w),
        ],
      ),
      body: Column(
        children: [
          // Product Info Header
          Container(
            padding: EdgeInsets.all(16.w),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              border: Border(
                bottom: BorderSide(color: Colors.grey.shade200),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 60.w,
                  height: 60.w,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8.w),
                    image: const DecorationImage(
                      image: AssetImage('assets/images/aquarium1.jpg'),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                SizedBox(width: 12.w),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '宠物标题宠物标题宠物标题宠物标...',
                        style: TextStyle(
                          fontSize: 14.sp,
                          fontWeight: FontWeight.w500,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      SizedBox(height: 4.h),
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
                        decoration: BoxDecoration(
                          color: Colors.orange,
                          borderRadius: BorderRadius.circular(2.w),
                        ),
                        child: Text(
                          '包邮',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 10.sp,
                          ),
                        ),
                      ),
                      SizedBox(height: 4.h),
                      Text(
                        '¥432',
                        style: TextStyle(
                          fontSize: 16.sp,
                          color: Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                TextButton(
                  onPressed: () {},
                  child: Text(
                    '查看详情',
                    style: TextStyle(
                      color: Colors.blue,
                      fontSize: 12.sp,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Messages
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.all(16.w),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final message = messages[index];
                final isUser = message['isUser'] as bool;
                
                return Container(
                  margin: EdgeInsets.only(bottom: 16.h),
                  child: Column(
                    children: [
                      Text(
                        message['time'],
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: Colors.grey[500],
                        ),
                      ),
                      SizedBox(height: 8.h),
                      Row(
                        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (!isUser) ...[
                            CircleAvatar(
                              radius: 16.w,
                              backgroundImage: const AssetImage('assets/images/avatar1.jpg'),
                            ),
                            SizedBox(width: 8.w),
                          ],
                          Flexible(
                            child: Container(
                              padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 8.h),
                              decoration: BoxDecoration(
                                color: isUser ? Colors.purple : Colors.grey[200],
                                borderRadius: BorderRadius.circular(8.w),
                              ),
                              child: Text(
                                message['message'],
                                style: TextStyle(
                                  fontSize: 14.sp,
                                  color: isUser ? Colors.white : Colors.black,
                                ),
                              ),
                            ),
                          ),
                          if (isUser) ...[
                            SizedBox(width: 8.w),
                            CircleAvatar(
                              radius: 16.w,
                              backgroundImage: const AssetImage('assets/images/avatar2.jpg'),
                            ),
                          ],
                        ],
                      ),
                      if (message['status'] != null) ...[
                        SizedBox(height: 4.h),
                        Text(
                          message['status'],
                          style: TextStyle(
                            fontSize: 10.sp,
                            color: Colors.grey[500],
                          ),
                        ),
                      ],
                    ],
                  ),
                );
              },
            ),
          ),

          // Message Input
          Container(
            padding: EdgeInsets.all(16.w),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border(
                top: BorderSide(color: Colors.grey.shade200),
              ),
            ),
            child: SafeArea(
              child: Row(
                children: [
                  IconButton(
                    onPressed: () {},
                    icon: Icon(
                      Icons.keyboard_voice,
                      size: 24.w,
                    ),
                  ),
                  Expanded(
                    child: Container(
                      padding: EdgeInsets.symmetric(horizontal: 12.w),
                      decoration: BoxDecoration(
                        color: Colors.grey[100],
                        borderRadius: BorderRadius.circular(20.w),
                      ),
                      child: TextField(
                        controller: _messageController,
                        decoration: const InputDecoration(
                          border: InputBorder.none,
                          hintText: '请输入消息...',
                        ),
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () {},
                    icon: Icon(
                      Icons.sentiment_satisfied_alt,
                      size: 24.w,
                    ),
                  ),
                  IconButton(
                    onPressed: () {},
                    icon: Icon(
                      Icons.add,
                      size: 24.w,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
