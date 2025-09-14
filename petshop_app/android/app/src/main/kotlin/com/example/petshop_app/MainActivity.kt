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
            // 确保窗口设置正确
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                // Android 11+ 
                window.setDecorFitsSystemWindows(false)
            } else {
                // Android 10 及以下
                @Suppress("DEPRECATION")
                window.decorView.systemUiVisibility = (
                    View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                )
            }
            
            // 设置状态栏透明
            window.statusBarColor = android.graphics.Color.TRANSPARENT
            
            // 确保窗口背景为白色
            window.navigationBarColor = android.graphics.Color.WHITE
            
            // 防止窗口被系统UI覆盖
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                window.attributes.layoutInDisplayCutoutMode = 
                    WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
            }
            
            // Release模式下的额外配置
            if (!BuildConfig.DEBUG) {
                // 禁用调试相关功能
                window.setFlags(
                    WindowManager.LayoutParams.FLAG_SECURE,
                    WindowManager.LayoutParams.FLAG_SECURE
                )
            }
            
        } catch (e: Exception) {
            // Release模式下捕获异常，防止崩溃
            e.printStackTrace()
        }
    }
}
