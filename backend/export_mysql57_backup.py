#!/usr/bin/env python3
"""
MySQL 5.7 兼容备份导出脚本
适配MySQL 5.7的数据库备份文件生成器
"""

import os
import re
import subprocess
import datetime
from pathlib import Path

def get_database_config():
    """从环境配置获取数据库连接信息"""
    database_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/petshop_auction")
    
    # 解析数据库URL
    # mysql+pymysql://username:password@host:port/database
    pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, database_url)
    
    if match:
        return {
            'username': match.group(1),
            'password': match.group(2),
            'host': match.group(3),
            'port': match.group(4),
            'database': match.group(5)
        }
    else:
        # 默认配置
        return {
            'username': 'root',
            'password': '123456',
            'host': 'localhost',
            'port': '3306',
            'database': 'petshop_auction'
        }

def create_mysql57_compatible_dump():
    """创建MySQL 5.7兼容的数据库备份"""
    
    # 获取数据库配置
    config = get_database_config()
    
    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"petshop_auction_mysql57_backup_{timestamp}.sql"
    backup_path = Path(__file__).parent / backup_filename
    
    print(f"正在创建MySQL 5.7兼容的备份文件: {backup_filename}")
    print(f"数据库: {config['database']} @ {config['host']}:{config['port']}")
    
    # mysqldump命令参数 - 针对MySQL 5.7优化
    mysqldump_cmd = [
        'mysqldump',
        '--single-transaction',  # 保证数据一致性
        '--routines',            # 导出存储过程和函数
        '--triggers',            # 导出触发器
        '--lock-tables=false',   # 不锁表
        '--add-drop-table',      # 添加DROP TABLE语句
        '--create-options',      # 包含表创建选项
        '--quick',               # 快速导出
        '--extended-insert',     # 使用扩展插入语法
        '--default-character-set=utf8mb4',  # 设置字符集
        '--skip-comments',       # 跳过注释以减少兼容性问题
        '--compact',             # 紧凑输出格式
        f'--host={config["host"]}',
        f'--port={config["port"]}',
        f'--user={config["username"]}',
        f'--password={config["password"]}',
        config['database']
    ]
    
    try:
        # 执行mysqldump命令
        print("正在导出数据库...")
        with open(backup_path, 'w', encoding='utf-8') as f:
            # 添加MySQL 5.7兼容性头部
            f.write("-- MySQL 5.7 Compatible Database Backup\n")
            f.write(f"-- Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Database: {config['database']}\n")
            f.write("-- Compatible with MySQL 5.7+\n\n")
            
            # 设置兼容性选项
            f.write("/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;\n")
            f.write("/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;\n")
            f.write("/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;\n")
            f.write("/*!40101 SET NAMES utf8mb4 */;\n")
            f.write("/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;\n")
            f.write("/*!40103 SET TIME_ZONE='+00:00' */;\n")
            f.write("/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;\n")
            f.write("/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;\n")
            f.write("/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;\n")
            f.write("/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;\n\n")
            
            # 执行mysqldump
            result = subprocess.run(mysqldump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                print(f"错误: {result.stderr}")
                return False
            
            # 处理输出以确保MySQL 5.7兼容性
            dump_content = result.stdout
            
            # 替换不兼容的排序规则
            dump_content = dump_content.replace('utf8mb4_0900_ai_ci', 'utf8mb4_unicode_ci')
            dump_content = dump_content.replace('utf8_0900_ai_ci', 'utf8_unicode_ci')
            
            # 移除MySQL 8.0+特有的功能
            dump_content = re.sub(r'/\*!80[0-9]{3}[^*]*\*/', '', dump_content)
            
            # 写入处理后的内容
            f.write(dump_content)
            
            # 添加恢复设置的尾部
            f.write("\n/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;\n")
            f.write("/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;\n")
            f.write("/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;\n")
            f.write("/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;\n")
            f.write("/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;\n")
            f.write("/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;\n")
            f.write("/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;\n")
            f.write("/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;\n")
        
        print(f"✅ 备份成功完成!")
        print(f"📁 备份文件: {backup_path}")
        print(f"📊 文件大小: {backup_path.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ mysqldump执行失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 创建备份时发生错误: {e}")
        return False

def create_restore_script():
    """创建恢复脚本"""
    restore_script = """#!/bin/bash
# MySQL 5.7 数据库恢复脚本

# 配置信息
DB_HOST="localhost"
DB_PORT="3306"
DB_USER="root"
DB_PASSWORD="123456"
DB_NAME="petshop_auction"

# 获取最新的备份文件
BACKUP_FILE=$(ls -t petshop_auction_mysql57_backup_*.sql | head -n 1)

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ 没有找到备份文件"
    exit 1
fi

echo "🔄 正在恢复数据库: $BACKUP_FILE"

# 创建数据库（如果不存在）
mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 恢复数据
mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD --default-character-set=utf8mb4 $DB_NAME < "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ 数据库恢复成功!"
else
    echo "❌ 数据库恢复失败!"
    exit 1
fi
"""
    
    script_path = Path(__file__).parent / "restore_mysql57_backup.sh"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(restore_script)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    print(f"📝 已创建恢复脚本: {script_path}")

if __name__ == "__main__":
    print("🚀 MySQL 5.7 兼容备份工具")
    print("=" * 50)
    
    # 检查mysqldump是否可用
    try:
        subprocess.run(['mysqldump', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 错误: 未找到mysqldump命令，请确保MySQL客户端已安装")
        exit(1)
    
    # 创建备份
    if create_mysql57_compatible_dump():
        create_restore_script()
        print("\n🎉 所有操作完成!")
        print("\n使用说明:")
        print("1. 备份文件已生成，可直接在MySQL 5.7中使用")
        print("2. 使用restore_mysql57_backup.sh脚本可以快速恢复数据库")
        print("3. 或手动执行: mysql -u用户名 -p --default-character-set=utf8mb4 数据库名 < 备份文件.sql")
    else:
        print("❌ 备份创建失败!")
        exit(1)
