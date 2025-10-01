import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../services/api_service.dart';

class TestApiPage extends StatefulWidget {
  const TestApiPage({super.key});

  @override
  State<TestApiPage> createState() => _TestApiPageState();
}

class _TestApiPageState extends State<TestApiPage> {
  final ApiService _apiService = ApiService();
  String _testResult = '点击测试按钮开始测试API连接...';
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('API连接测试'),
        backgroundColor: const Color(0xFF9C4DFF),
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'API测试',
              style: TextStyle(
                fontSize: 24.sp,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF333333),
              ),
            ),
            SizedBox(height: 20.h),

            // API地址显示
            Container(
              padding: EdgeInsets.all(12.w),
              decoration: BoxDecoration(
                color: const Color(0xFFF5F5F5),
                borderRadius: BorderRadius.circular(8.r),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'API地址:',
                    style: TextStyle(
                      fontSize: 14.sp,
                      fontWeight: FontWeight.w600,
                      color: const Color(0xFF666666),
                    ),
                  ),
                  SizedBox(height: 4.h),
                  Text(
                    'http://39.96.177.57:3000/api/v1',
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: const Color(0xFF9C4DFF),
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
            ),

            SizedBox(height: 20.h),

            // 测试按钮
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _testApiConnection,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF9C4DFF),
                  foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(vertical: 12.h),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                ),
                child: _isLoading
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 16.w,
                            height: 16.w,
                            child: const CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          ),
                          SizedBox(width: 8.w),
                          const Text('测试中...'),
                        ],
                      )
                    : const Text('测试API连接'),
              ),
            ),

            SizedBox(height: 20.h),

            // 测试结果
            Container(
              width: double.infinity,
              padding: EdgeInsets.all(12.w),
              decoration: BoxDecoration(
                color: const Color(0xFFF8F9FA),
                borderRadius: BorderRadius.circular(8.r),
                border: Border.all(
                  color: const Color(0xFFE9ECEF),
                  width: 1,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '测试结果:',
                    style: TextStyle(
                      fontSize: 14.sp,
                      fontWeight: FontWeight.w600,
                      color: const Color(0xFF333333),
                    ),
                  ),
                  SizedBox(height: 8.h),
                  Text(
                    _testResult,
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: const Color(0xFF666666),
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _testApiConnection() async {
    setState(() {
      _isLoading = true;
      _testResult = '正在测试API连接...';
    });

    try {
      // 测试根路径
      final rootResponse = await _apiService.get('/');
      _testResult = '✅ 根路径测试成功\n';
      _testResult += '状态码: ${rootResponse.statusCode}\n';
      _testResult += '响应: ${rootResponse.data}\n\n';

      // 测试健康检查
      final healthResponse = await _apiService.get('/health');
      _testResult += '✅ 健康检查测试成功\n';
      _testResult += '状态码: ${healthResponse.statusCode}\n';
      _testResult += '响应: ${healthResponse.data}\n\n';

      _testResult += '🎉 所有API测试通过！应用可以正常连接后台服务。';
    } catch (e) {
      _testResult = '❌ API连接测试失败\n';
      _testResult += '错误信息: $e\n\n';
      _testResult += '请检查:\n';
      _testResult += '1. 网络连接是否正常\n';
      _testResult += '2. 后台服务是否正在运行\n';
      _testResult += '3. 域名是否可以正常访问';
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
}
