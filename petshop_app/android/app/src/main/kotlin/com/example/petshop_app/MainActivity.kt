package com.example.petshop_app

import android.os.Build
import android.os.Bundle
import android.view.View
import android.view.WindowManager
import io.flutter.embedding.android.FlutterActivity

class MainActivity : FlutterActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        try {
            // 简化的窗口设置，避免与Flutter的SafeArea冲突
            window.statusBarColor = android.graphics.Color.TRANSPARENT
            window.navigationBarColor = android.graphics.Color.WHITE
            
            // Release模式下的安全设置
            try {
                val isDebug = (applicationInfo.flags and android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0
                if (!isDebug) {
                    // 在release模式下禁用截屏
                    window.setFlags(
                        WindowManager.LayoutParams.FLAG_SECURE,
                        WindowManager.LayoutParams.FLAG_SECURE
                    )
                }
            } catch (e: Exception) {
                // 忽略错误
            }
            
        } catch (e: Exception) {
            // 捕获异常，防止崩溃
            e.printStackTrace()
        }
    }
}
