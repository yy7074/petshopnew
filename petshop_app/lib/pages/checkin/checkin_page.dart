import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../services/checkin_service.dart';

class CheckinPage extends StatefulWidget {
  const CheckinPage({super.key});

  @override
  State<CheckinPage> createState() => _CheckinPageState();
}

class _CheckinPageState extends State<CheckinPage> {
  final CheckinService _checkinService = CheckinService();
  
  int _consecutiveDays = 0;
  int _diamondBalance = 0;
  bool _todayChecked = false;
  bool _yesterdayChecked = false;
  bool _dayBeforeYesterdayChecked = false;
  bool _isLoading = false;
  CheckinStatus? _checkinStatus;

  @override
  void initState() {
    super.initState();
    _loadCheckinStatus();
  }

  Future<void> _loadCheckinStatus() async {
    setState(() {
      _isLoading = true;
    });

    final result = await _checkinService.getCheckinStatus();
    if (result.success && result.data != null) {
      setState(() {
        _checkinStatus = result.data!;
        _consecutiveDays = result.data!.consecutiveDays;
        _todayChecked = result.data!.isCheckedToday;
        _diamondBalance = 23400; // 这里应该从用户信息API获取
        _isLoading = false;
      });
    } else {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.message),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          child: Column(
            children: [
              SizedBox(height: 16.h),
              _buildHeader(),
              SizedBox(height: 24.h),
              _buildUserStatus(),
              SizedBox(height: 24.h),
              _buildRewardDescription(),
              SizedBox(height: 20.h),
              _buildDailyCards(),
              SizedBox(height: 24.h),
              _buildRewardGrid(),
              SizedBox(height: 100.h),
            ],
          ),
        ),
      ),
    );
  }

  // 构建头部
  Widget _buildHeader() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          // 返回按钮
          GestureDetector(
            onTap: () {
              Navigator.pop(context);
            },
            child: Container(
              width: 36.w,
              height: 36.w,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(18.r),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.08),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Icon(
                Icons.arrow_back_ios_new,
                size: 18.w,
                color: const Color(0xFF333333),
              ),
            ),
          ),
          SizedBox(width: 16.w),
          // 标题
          Expanded(
            child: Text(
              '签到',
              style: TextStyle(
                fontSize: 18.sp,
                color: const Color(0xFF333333),
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          SizedBox(width: 52.w), // 占位，保持标题居中
        ],
      ),
    );
  }

  // 构建用户状态
  Widget _buildUserStatus() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          // 头像
          Container(
            width: 48.w,
            height: 48.w,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xFFF0F0F0),
            ),
            child: ClipOval(
              child: CachedNetworkImage(
                imageUrl: 'https://picsum.photos/100/100?random=avatar',
                fit: BoxFit.cover,
                placeholder: (context, url) => Container(
                  color: const Color(0xFFF0F0F0),
                  child: const Icon(
                    Icons.person,
                    color: Color(0xFF999999),
                  ),
                ),
                errorWidget: (context, url, error) => Container(
                  color: const Color(0xFFF0F0F0),
                  child: const Icon(
                    Icons.person,
                    color: Color(0xFF999999),
                  ),
                ),
              ),
            ),
          ),
          SizedBox(width: 12.w),
          // 连续签到天数
          Text(
            '已连续签到${_consecutiveDays}天',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w500,
            ),
          ),
          const Spacer(),
          // 钻石余额
          Row(
            children: [
              Icon(
                Icons.diamond,
                size: 16.w,
                color: const Color(0xFF2196F3),
              ),
              SizedBox(width: 4.w),
              Text(
                '$_diamondBalance',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: const Color(0xFF333333),
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // 构建奖励说明
  Widget _buildRewardDescription() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          Text(
            '签到领钻石购物可抵扣',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w500,
            ),
          ),
          const Spacer(),
          // 签到规则按钮
          GestureDetector(
            onTap: () {
              _showRulesDialog();
            },
            child: Row(
              children: [
                Container(
                  width: 16.w,
                  height: 16.w,
                  decoration: BoxDecoration(
                    color: const Color(0xFF9C4DFF),
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      '①',
                      style: TextStyle(
                        fontSize: 10.sp,
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
                SizedBox(width: 4.w),
                Text(
                  '签到规则',
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: const Color(0xFF9C4DFF),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 构建每日签到卡片
  Widget _buildDailyCards() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Row(
        children: [
          // 前天
          Expanded(
            child: _buildDayCard(
              '前天',
              _dayBeforeYesterdayChecked,
              _dayBeforeYesterdayChecked ? '+1' : '未签到',
              false,
            ),
          ),
          SizedBox(width: 8.w),
          // 昨天
          Expanded(
            child: _buildDayCard(
              '昨天',
              _yesterdayChecked,
              _yesterdayChecked ? '+1' : '未签到',
              false,
            ),
          ),
          SizedBox(width: 8.w),
          // 今天
          Expanded(
            child: _buildDayCard(
              '今天',
              _todayChecked,
              _todayChecked ? '+1' : '签到',
              !_todayChecked,
            ),
          ),
          SizedBox(width: 8.w),
          // 明天
          Expanded(
            child: _buildDayCard(
              '明天',
              false,
              '未开放',
              false,
            ),
          ),
        ],
      ),
    );
  }

  // 构建单日卡片
  Widget _buildDayCard(String day, bool isChecked, String text, bool isToday) {
    Color backgroundColor;
    Color textColor;
    Color iconColor;

    if (isChecked) {
      backgroundColor = const Color(0xFF9C4DFF);
      textColor = Colors.white;
      iconColor = const Color(0xFF2196F3);
    } else if (isToday) {
      backgroundColor = const Color(0xFF9C4DFF).withOpacity(0.8);
      textColor = Colors.white;
      iconColor = const Color(0xFF2196F3);
    } else {
      backgroundColor = const Color(0xFFF0F0F0);
      textColor = const Color(0xFF999999);
      iconColor = const Color(0xFF999999);
    }

    return GestureDetector(
      onTap: (day == '今天') ? _performCheckin : null,
      child: Container(
        height: 80.h,
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(12.r),
          boxShadow: isChecked || isToday
              ? [
                  BoxShadow(
                    color: const Color(0xFF9C4DFF).withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ]
              : null,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 钻石图标
            Icon(
              Icons.diamond,
              size: 20.w,
              color: iconColor,
            ),
            SizedBox(height: 4.h),
            // 天数
            Text(
              day,
              style: TextStyle(
                fontSize: 12.sp,
                color: textColor,
                fontWeight: FontWeight.w500,
              ),
            ),
            SizedBox(height: 2.h),
            // 状态文本
            Text(
              text,
              style: TextStyle(
                fontSize: 10.sp,
                color: textColor,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建奖励网格
  Widget _buildRewardGrid() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题
          Text(
            '连续签到奖励',
            style: TextStyle(
              fontSize: 16.sp,
              color: const Color(0xFF333333),
              fontWeight: FontWeight.w600,
            ),
          ),
          SizedBox(height: 16.h),
          // 奖励网格
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 4,
              crossAxisSpacing: 8.w,
              mainAxisSpacing: 8.h,
              childAspectRatio: 1.2,
            ),
            itemCount: 24, // 4-27天
            itemBuilder: (context, index) {
              int day = index + 4;
              bool isSpecialDay = day == 7; // 第7天特殊奖励
              int reward = isSpecialDay ? 5 : 1;

              return Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8.r),
                  border: Border.all(
                    color: const Color(0xFFE0E0E0),
                    width: 1,
                  ),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // 钻石图标
                    Icon(
                      Icons.diamond,
                      size: 16.w,
                      color: const Color(0xFF2196F3),
                    ),
                    SizedBox(height: 4.h),
                    // 天数
                    Text(
                      '第${day}天',
                      style: TextStyle(
                        fontSize: 10.sp,
                        color: const Color(0xFF666666),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    SizedBox(height: 2.h),
                    // 奖励
                    Text(
                      '钻石$reward',
                      style: TextStyle(
                        fontSize: 9.sp,
                        color: const Color(0xFF666666),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  // 执行签到
  void _performCheckin() async {
    if (_isLoading) return;

    // 如果已签到，显示已签到提示
    if (_todayChecked) {
      _showAlreadyCheckedDialog();
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final result = await _checkinService.dailyCheckin();
    
    setState(() {
      _isLoading = false;
    });

    if (result.success && result.data != null) {
      setState(() {
        _todayChecked = true;
        _consecutiveDays = result.data!.checkinInfo.consecutiveDays;
        _diamondBalance += result.data!.checkinInfo.rewardPoints;
      });
      
      _showSuccessDialog(result.data!.checkinInfo);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.message),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  // 显示已签到提示弹窗
  void _showAlreadyCheckedDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20.r),
        ),
        contentPadding: EdgeInsets.zero,
        content: Container(
          width: 280.w,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20.r),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 顶部插图区域
              Container(
                width: double.infinity,
                height: 120.h,
                decoration: BoxDecoration(
                  color: const Color(0xFFF8F9FA),
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(20.r),
                    topRight: Radius.circular(20.r),
                  ),
                ),
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    Container(
                      width: 80.w,
                      height: 80.w,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(40.r),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.1),
                            blurRadius: 15,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Icon(
                        Icons.check_circle,
                        size: 45.w,
                        color: const Color(0xFF4CAF50),
                      ),
                    ),
                  ],
                ),
              ),

              // 内容区域
              Padding(
                padding: EdgeInsets.all(24.w),
                child: Column(
                  children: [
                    // 标题
                    Text(
                      '今日已签到',
                      style: TextStyle(
                        fontSize: 22.sp,
                        color: const Color(0xFF333333),
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    SizedBox(height: 16.h),

                    // 签到信息
                    Container(
                      width: double.infinity,
                      padding: EdgeInsets.symmetric(
                          horizontal: 16.w, vertical: 16.h),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8F9FA),
                        borderRadius: BorderRadius.circular(12.r),
                        border: Border.all(
                          color: const Color(0xFFE0E0E0),
                          width: 1,
                        ),
                      ),
                      child: Column(
                        children: [
                          Text(
                            '您今天已经完成签到了',
                            style: TextStyle(
                              fontSize: 16.sp,
                              color: const Color(0xFF666666),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          SizedBox(height: 8.h),
                          Text(
                            '已连续签到${_consecutiveDays}天',
                            style: TextStyle(
                              fontSize: 14.sp,
                              color: const Color(0xFF666666),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                    SizedBox(height: 24.h),

                    // 确定按钮
                    GestureDetector(
                      onTap: () {
                        Navigator.pop(context);
                      },
                      child: Container(
                        width: double.infinity,
                        padding: EdgeInsets.symmetric(vertical: 16.h),
                        decoration: BoxDecoration(
                          color: const Color(0xFF9C4DFF),
                          borderRadius: BorderRadius.circular(12.r),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF9C4DFF).withOpacity(0.3),
                              blurRadius: 8,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Text(
                          '确定',
                          style: TextStyle(
                            fontSize: 16.sp,
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // 显示签到规则弹窗
  void _showRulesDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16.r),
        ),
        title: Text(
          '签到规则',
          style: TextStyle(
            fontSize: 18.sp,
            color: const Color(0xFF333333),
            fontWeight: FontWeight.w700,
          ),
          textAlign: TextAlign.center,
        ),
        content: Container(
          width: double.maxFinite,
          padding: EdgeInsets.symmetric(vertical: 8.h),
          child: Text(
            '这是一段签到规则，弹窗为通用格式，比如每日签到奖励多少钻石，连续几天奖励多少钻石，每多少钻石购物时可抵扣多少元。这是一段签到规则，弹窗为通用格式，比如每日签到奖励多少钻石，连续几天奖励多少钻石，每多少钻石购物时可抵扣多少元。',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF666666),
              height: 1.6,
            ),
            textAlign: TextAlign.left,
          ),
        ),
        actions: [
          Container(
            width: double.infinity,
            margin: EdgeInsets.only(top: 8.h),
            child: TextButton(
              onPressed: () {
                Navigator.pop(context);
              },
              style: TextButton.styleFrom(
                padding: EdgeInsets.zero,
              ),
              child: Container(
                width: double.infinity,
                padding: EdgeInsets.symmetric(vertical: 14.h),
                decoration: BoxDecoration(
                  color: const Color(0xFF9C4DFF),
                  borderRadius: BorderRadius.circular(12.r),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF9C4DFF).withOpacity(0.3),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Text(
                  '确定',
                  style: TextStyle(
                    fontSize: 16.sp,
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 显示签到成功弹窗
  void _showSuccessDialog(CheckinInfo checkinInfo) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20.r),
        ),
        contentPadding: EdgeInsets.zero,
        content: Container(
          width: 280.w,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20.r),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 顶部插图区域
              Container(
                width: double.infinity,
                height: 120.h,
                decoration: BoxDecoration(
                  color: const Color(0xFFF8F9FA),
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(20.r),
                    topRight: Radius.circular(20.r),
                  ),
                ),
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    // 3D手绘风格插图
                    Container(
                      width: 80.w,
                      height: 80.w,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(40.r),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.1),
                            blurRadius: 15,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          // 手绘风格的成功图标
                          Icon(
                            Icons.check_circle,
                            size: 45.w,
                            color: const Color(0xFF4CAF50),
                          ),
                          // 添加一些装饰元素
                          Positioned(
                            top: 15.h,
                            right: 15.w,
                            child: Container(
                              width: 8.w,
                              height: 8.w,
                              decoration: BoxDecoration(
                                color: const Color(0xFFFF9800),
                                shape: BoxShape.circle,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              // 内容区域
              Padding(
                padding: EdgeInsets.all(24.w),
                child: Column(
                  children: [
                    // 成功标题
                    Text(
                      '签到成功',
                      style: TextStyle(
                        fontSize: 22.sp,
                        color: const Color(0xFF333333),
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    SizedBox(height: 20.h),

                    // 奖励信息
                    Container(
                      width: double.infinity,
                      padding: EdgeInsets.symmetric(
                          horizontal: 16.w, vertical: 16.h),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8F9FA),
                        borderRadius: BorderRadius.circular(12.r),
                        border: Border.all(
                          color: const Color(0xFFE0E0E0),
                          width: 1,
                        ),
                      ),
                      child: Column(
                        children: [
                          // 今日签到奖励
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.diamond,
                                size: 18.w,
                                color: const Color(0xFF2196F3),
                              ),
                              SizedBox(width: 6.w),
                              Text(
                                '今日签到 +${checkinInfo.rewardPoints} 钻石',
                                style: TextStyle(
                                  fontSize: 16.sp,
                                  color: const Color(0xFF333333),
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 12.h),
                          // 连续签到天数
                          Text(
                            '已连续签到${checkinInfo.consecutiveDays}天',
                            style: TextStyle(
                              fontSize: 14.sp,
                              color: const Color(0xFF666666),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                    SizedBox(height: 24.h),

                    // 确定按钮
                    GestureDetector(
                      onTap: () {
                        Navigator.pop(context);
                      },
                      child: Container(
                        width: double.infinity,
                        padding: EdgeInsets.symmetric(vertical: 16.h),
                        decoration: BoxDecoration(
                          color: const Color(0xFF9C4DFF),
                          borderRadius: BorderRadius.circular(12.r),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF9C4DFF).withOpacity(0.3),
                              blurRadius: 8,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Text(
                          '确定',
                          style: TextStyle(
                            fontSize: 16.sp,
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
