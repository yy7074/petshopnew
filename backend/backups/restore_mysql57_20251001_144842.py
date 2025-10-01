#!/usr/bin/env python3
"""
MySQL 5.7 数据库恢复脚本 (Python版本)
生成时间: 2025-10-01 14:48:43
"""

import subprocess
import sys
import os
from pathlib import Path

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': '3306',
    'user': 'root',
    'password': '123456',
    'database': 'petshop_auction'
}

def restore_database(backup_file: str):
    """恢复数据库"""
    print("🔄 MySQL 5.7 数据库恢复工具")
    print("=" * 40)
    
    # 检查备份文件
    if not Path(backup_file).exists():
        print(f"❌ 备份文件不存在: {backup_file}")
        return False
    
    print(f"📁 使用备份文件: {backup_file}")
    
    # 确认操作
    response = input(f"⚠️  警告: 此操作将覆盖现有数据库 '{DB_CONFIG['database']}' (y/N): ")
    if response.lower() != 'y':
        print("操作已取消")
        return False
    
    try:
        # 测试连接
        print("🔍 测试数据库连接...")
        test_cmd = [
            'mysql',
            f'--host={DB_CONFIG["host"]}',
            f'--port={DB_CONFIG["port"]}',
            f'--user={DB_CONFIG["user"]}',
            f'--password={DB_CONFIG["password"]}',
            '--execute=SELECT 1;'
        ]
        result = subprocess.run(test_cmd, capture_output=True)
        if result.returncode != 0:
            print("❌ 数据库连接失败")
            return False
        
        # 创建数据库
        print("🏗️  创建数据库...")
        create_cmd = [
            'mysql',
            f'--host={DB_CONFIG["host"]}',
            f'--port={DB_CONFIG["port"]}',
            f'--user={DB_CONFIG["user"]}',
            f'--password={DB_CONFIG["password"]}',
            f'--execute=CREATE DATABASE IF NOT EXISTS {DB_CONFIG["database"]} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
        ]
        subprocess.run(create_cmd, check=True)
        
        # 恢复数据
        print("📥 正在恢复数据库...")
        restore_cmd = [
            'mysql',
            f'--host={DB_CONFIG["host"]}',
            f'--port={DB_CONFIG["port"]}',
            f'--user={DB_CONFIG["user"]}',
            f'--password={DB_CONFIG["password"]}',
            '--default-character-set=utf8mb4',
            DB_CONFIG["database"]
        ]
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            result = subprocess.run(restore_cmd, stdin=f, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 数据库恢复成功!")
            
            # 验证结果
            verify_cmd = [
                'mysql',
                f'--host={DB_CONFIG["host"]}',
                f'--port={DB_CONFIG["port"]}',
                f'--user={DB_CONFIG["user"]}',
                f'--password={DB_CONFIG["password"]}',
                f'--database={DB_CONFIG["database"]}',
                '--execute=SHOW TABLES;',
                '--skip-column-names'
            ]
            result = subprocess.run(verify_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                table_count = len([line for line in result.stdout.strip().split('\n') if line.strip()])
                print(f"📊 恢复了 {table_count} 个表")
            
            print("🎉 恢复操作完成!")
            return True
        else:
            print(f"❌ 数据库恢复失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 恢复过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        backup_file = sys.argv[1]
    else:
        # 自动选择最新的完整备份
        backup_files = list(Path("backups").glob("petshop_complete_mysql57_*.sql"))
        if backup_files:
            backup_file = str(max(backup_files, key=lambda x: x.stat().st_mtime))
        else:
            print("❌ 没有找到备份文件")
            print("用法: python restore_mysql57.py [备份文件路径]")
            sys.exit(1)
    
    success = restore_database(backup_file)
    sys.exit(0 if success else 1)
