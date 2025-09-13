import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class TradeRulesPage extends StatelessWidget {
  const TradeRulesPage({super.key});

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
          '交易规则与服务协议',
          style: TextStyle(
            color: Colors.black,
            fontSize: 16.sp,
            fontWeight: FontWeight.w500,
          ),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(20.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Text(
                '交易规则与服务协议',
                style: TextStyle(
                  fontSize: 18.sp,
                  fontWeight: FontWeight.w600,
                  color: Colors.black,
                ),
              ),
            ),
            SizedBox(height: 20.h),
            
            Text(
              '交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容交易规则与服务协议内容',
              style: TextStyle(
                fontSize: 14.sp,
                height: 1.5,
                color: Colors.grey[700],
              ),
              textAlign: TextAlign.justify,
            ),
          ],
        ),
      ),
    );
  }
}