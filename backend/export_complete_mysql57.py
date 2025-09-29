#!/usr/bin/env python3
"""
完整的MySQL 5.7兼容数据导出工具
包含数据验证、完整性检查和多种导出选项
"""

import os
import re
import subprocess
import datetime
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class MySQL57Exporter:
    def __init__(self):
        self.config = self.get_database_config()
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(__file__).parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def get_database_config(self) -> Dict[str, str]:
        """从环境配置获取数据库连接信息"""
        database_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/petshop_auction")
        
        # 解析数据库URL
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
            return {
                'username': 'root',
                'password': '123456',
                'host': 'localhost',
                'port': '3306',
                'database': 'petshop_auction'
            }
    
    def check_mysql_connection(self) -> bool:
        """检查MySQL连接是否正常"""
        try:
            cmd = [
                'mysql',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["username"]}',
                f'--password={self.config["password"]}',
                '--execute=SELECT 1;'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_database_info(self) -> Dict:
        """获取数据库基本信息"""
        try:
            # 获取数据库版本
            cmd = [
                'mysql',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["username"]}',
                f'--password={self.config["password"]}',
                '--execute=SELECT VERSION();',
                '--skip-column-names',
                '--silent'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            version = result.stdout.strip() if result.returncode == 0 else "未知"
            
            # 获取表数量
            cmd = [
                'mysql',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["username"]}',
                f'--password={self.config["password"]}',
                f'--database={self.config["database"]}',
                '--execute=SHOW TABLES;',
                '--skip-column-names',
                '--silent'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            tables = result.stdout.strip().split('\n') if result.returncode == 0 else []
            
            # 获取数据库大小
            cmd = [
                'mysql',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["username"]}',
                f'--password={self.config["password"]}',
                '--execute=SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS "DB Size in MB" FROM information_schema.tables WHERE table_schema="{}";'.format(self.config["database"]),
                '--skip-column-names',
                '--silent'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            size = result.stdout.strip() if result.returncode == 0 else "未知"
            
            return {
                'version': version,
                'tables': [t for t in tables if t.strip()],
                'table_count': len([t for t in tables if t.strip()]),
                'size_mb': size
            }
        except Exception as e:
            print(f"获取数据库信息失败: {e}")
            return {}
    
    def create_structure_only_dump(self) -> str:
        """创建仅结构的备份文件"""
        filename = f"petshop_structure_mysql57_{self.timestamp}.sql"
        filepath = self.backup_dir / filename
        
        cmd = [
            'mysqldump',
            '--single-transaction',
            '--routines',
            '--triggers',
            '--no-data',  # 仅结构，不包含数据
            '--add-drop-table',
            '--create-options',
            '--default-character-set=utf8mb4',
            '--skip-comments',
            f'--host={self.config["host"]}',
            f'--port={self.config["port"]}',
            f'--user={self.config["username"]}',
            f'--password={self.config["password"]}',
            self.config['database']
        ]
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                self._write_header(f, "结构备份")
                
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    print(f"结构备份失败: {result.stderr}")
                    return ""
                
                # 处理MySQL 5.7兼容性
                content = self._make_mysql57_compatible(result.stdout)
                f.write(content)
                self._write_footer(f)
                
            print(f"✅ 结构备份完成: {filename}")
            return str(filepath)
        except Exception as e:
            print(f"❌ 结构备份失败: {e}")
            return ""
    
    def create_data_only_dump(self) -> str:
        """创建仅数据的备份文件"""
        filename = f"petshop_data_mysql57_{self.timestamp}.sql"
        filepath = self.backup_dir / filename
        
        cmd = [
            'mysqldump',
            '--single-transaction',
            '--no-create-info',  # 仅数据，不包含结构
            '--extended-insert',
            '--quick',
            '--lock-tables=false',
            '--default-character-set=utf8mb4',
            '--skip-comments',
            '--compact',
            f'--host={self.config["host"]}',
            f'--port={self.config["port"]}',
            f'--user={self.config["username"]}',
            f'--password={self.config["password"]}',
            self.config['database']
        ]
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                self._write_header(f, "数据备份")
                
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    print(f"数据备份失败: {result.stderr}")
                    return ""
                
                # 处理MySQL 5.7兼容性
                content = self._make_mysql57_compatible(result.stdout)
                f.write(content)
                self._write_footer(f)
                
            print(f"✅ 数据备份完成: {filename}")
            return str(filepath)
        except Exception as e:
            print(f"❌ 数据备份失败: {e}")
            return ""
    
    def create_complete_dump(self) -> str:
        """创建完整备份文件（结构+数据）"""
        filename = f"petshop_complete_mysql57_{self.timestamp}.sql"
        filepath = self.backup_dir / filename
        
        cmd = [
            'mysqldump',
            '--single-transaction',
            '--routines',
            '--triggers',
            '--lock-tables=false',
            '--add-drop-table',
            '--create-options',
            '--quick',
            '--extended-insert',
            '--default-character-set=utf8mb4',
            '--skip-comments',
            '--compact',
            f'--host={self.config["host"]}',
            f'--port={self.config["port"]}',
            f'--user={self.config["username"]}',
            f'--password={self.config["password"]}',
            self.config['database']
        ]
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                self._write_header(f, "完整备份")
                
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    print(f"完整备份失败: {result.stderr}")
                    return ""
                
                # 处理MySQL 5.7兼容性
                content = self._make_mysql57_compatible(result.stdout)
                f.write(content)
                self._write_footer(f)
                
            print(f"✅ 完整备份完成: {filename}")
            return str(filepath)
        except Exception as e:
            print(f"❌ 完整备份失败: {e}")
            return ""
    
    def _write_header(self, f, backup_type: str):
        """写入备份文件头部"""
        f.write(f"-- MySQL 5.7 Compatible Database Backup ({backup_type})\n")
        f.write(f"-- Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Database: {self.config['database']}\n")
        f.write(f"-- Host: {self.config['host']}:{self.config['port']}\n")
        f.write("-- Compatible with MySQL 5.7+\n")
        f.write("-- Charset: utf8mb4\n\n")
        
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
    
    def _write_footer(self, f):
        """写入备份文件尾部"""
        f.write("\n-- Restore settings\n")
        f.write("/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;\n")
        f.write("/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;\n")
        f.write("/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;\n")
        f.write("/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;\n")
        f.write("/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;\n")
        f.write("/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;\n")
        f.write("/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;\n")
        f.write("/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;\n")
    
    def _make_mysql57_compatible(self, content: str) -> str:
        """使内容兼容MySQL 5.7"""
        # 替换不兼容的排序规则
        content = content.replace('utf8mb4_0900_ai_ci', 'utf8mb4_unicode_ci')
        content = content.replace('utf8_0900_ai_ci', 'utf8_unicode_ci')
        content = content.replace('utf8mb4_0900_as_ci', 'utf8mb4_unicode_ci')
        
        # 移除MySQL 8.0+特有的功能
        content = re.sub(r'/\*!80[0-9]{3}[^*]*\*/', '', content)
        
        # 移除不兼容的存储引擎选项
        content = re.sub(r'DEFAULT ENCRYPTION=\'[^\']*\'', '', content)
        
        # 处理JSON类型（MySQL 5.7.8+支持）
        # 如果需要兼容更早版本，可以将JSON替换为TEXT
        
        return content
    
    def calculate_file_hash(self, filepath: str) -> str:
        """计算文件MD5哈希值"""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def create_backup_info(self, backup_files: List[str], db_info: Dict) -> str:
        """创建备份信息文件"""
        info_filename = f"backup_info_{self.timestamp}.json"
        info_filepath = self.backup_dir / info_filename
        
        backup_info = {
            "timestamp": self.timestamp,
            "created_at": datetime.datetime.now().isoformat(),
            "database": {
                "name": self.config["database"],
                "host": self.config["host"],
                "port": self.config["port"],
                "version": db_info.get("version", "未知"),
                "size_mb": db_info.get("size_mb", "未知"),
                "table_count": db_info.get("table_count", 0),
                "tables": db_info.get("tables", [])
            },
            "backup_files": []
        }
        
        for filepath in backup_files:
            if filepath and Path(filepath).exists():
                file_stat = Path(filepath).stat()
                backup_info["backup_files"].append({
                    "filename": Path(filepath).name,
                    "filepath": filepath,
                    "size_bytes": file_stat.st_size,
                    "size_mb": round(file_stat.st_size / 1024 / 1024, 2),
                    "md5_hash": self.calculate_file_hash(filepath),
                    "type": self._get_backup_type(Path(filepath).name)
                })
        
        try:
            with open(info_filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
            print(f"📋 备份信息文件: {info_filename}")
            return str(info_filepath)
        except Exception as e:
            print(f"❌ 创建备份信息失败: {e}")
            return ""
    
    def _get_backup_type(self, filename: str) -> str:
        """根据文件名判断备份类型"""
        if "structure" in filename:
            return "结构备份"
        elif "data" in filename:
            return "数据备份"
        elif "complete" in filename:
            return "完整备份"
        else:
            return "未知类型"
    
    def create_restore_scripts(self):
        """创建恢复脚本"""
        # Bash恢复脚本
        bash_script = f'''#!/bin/bash
# MySQL 5.7 数据库恢复脚本
# 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 配置信息
DB_HOST="{self.config["host"]}"
DB_PORT="{self.config["port"]}"
DB_USER="{self.config["username"]}"
DB_PASSWORD="{self.config["password"]}"
DB_NAME="{self.config["database"]}"

# 颜色输出
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo "🔄 MySQL 5.7 数据库恢复工具"
echo "================================"

# 检查MySQL客户端
if ! command -v mysql &> /dev/null; then
    echo "${{RED}}❌ MySQL客户端未安装${{NC}}"
    exit 1
fi

# 获取备份文件
if [ -n "$1" ]; then
    BACKUP_FILE="$1"
else
    # 自动选择最新的完整备份
    BACKUP_FILE=$(ls -t backups/petshop_complete_mysql57_*.sql 2>/dev/null | head -n 1)
    if [ -z "$BACKUP_FILE" ]; then
        echo "${{RED}}❌ 没有找到备份文件${{NC}}"
        echo "用法: $0 [备份文件路径]"
        exit 1
    fi
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "${{RED}}❌ 备份文件不存在: $BACKUP_FILE${{NC}}"
    exit 1
fi

echo "${{YELLOW}}📁 使用备份文件: $BACKUP_FILE${{NC}}"

# 确认操作
echo "${{YELLOW}}⚠️  警告: 此操作将覆盖现有数据库 '$DB_NAME'${{NC}}"
read -p "是否继续? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 0
fi

# 测试数据库连接
echo "🔍 测试数据库连接..."
if ! mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "SELECT 1;" > /dev/null 2>&1; then
    echo "${{RED}}❌ 数据库连接失败${{NC}}"
    exit 1
fi

# 创建数据库（如果不存在）
echo "🏗️  创建数据库..."
mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 恢复数据
echo "📥 正在恢复数据库..."
if mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD --default-character-set=utf8mb4 $DB_NAME < "$BACKUP_FILE"; then
    echo "${{GREEN}}✅ 数据库恢复成功!${{NC}}"
    
    # 验证恢复结果
    echo "🔍 验证恢复结果..."
    TABLE_COUNT=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -D$DB_NAME -e "SHOW TABLES;" | wc -l)
    echo "${{GREEN}}📊 恢复了 $((TABLE_COUNT-1)) 个表${{NC}}"
else
    echo "${{RED}}❌ 数据库恢复失败!${{NC}}"
    exit 1
fi

echo "${{GREEN}}🎉 恢复操作完成!${{NC}}"
'''
        
        bash_script_path = self.backup_dir / f"restore_mysql57_{self.timestamp}.sh"
        with open(bash_script_path, 'w', encoding='utf-8') as f:
            f.write(bash_script)
        os.chmod(bash_script_path, 0o755)
        
        # Python恢复脚本
        python_script = f'''#!/usr/bin/env python3
"""
MySQL 5.7 数据库恢复脚本 (Python版本)
生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import subprocess
import sys
import os
from pathlib import Path

# 数据库配置
DB_CONFIG = {{
    'host': '{self.config["host"]}',
    'port': '{self.config["port"]}',
    'user': '{self.config["username"]}',
    'password': '{self.config["password"]}',
    'database': '{self.config["database"]}'
}}

def restore_database(backup_file: str):
    """恢复数据库"""
    print("🔄 MySQL 5.7 数据库恢复工具")
    print("=" * 40)
    
    # 检查备份文件
    if not Path(backup_file).exists():
        print(f"❌ 备份文件不存在: {{backup_file}}")
        return False
    
    print(f"📁 使用备份文件: {{backup_file}}")
    
    # 确认操作
    response = input(f"⚠️  警告: 此操作将覆盖现有数据库 '{{DB_CONFIG['database']}}' (y/N): ")
    if response.lower() != 'y':
        print("操作已取消")
        return False
    
    try:
        # 测试连接
        print("🔍 测试数据库连接...")
        test_cmd = [
            'mysql',
            f'--host={{DB_CONFIG["host"]}}',
            f'--port={{DB_CONFIG["port"]}}',
            f'--user={{DB_CONFIG["user"]}}',
            f'--password={{DB_CONFIG["password"]}}',
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
            f'--host={{DB_CONFIG["host"]}}',
            f'--port={{DB_CONFIG["port"]}}',
            f'--user={{DB_CONFIG["user"]}}',
            f'--password={{DB_CONFIG["password"]}}',
            f'--execute=CREATE DATABASE IF NOT EXISTS {{DB_CONFIG["database"]}} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
        ]
        subprocess.run(create_cmd, check=True)
        
        # 恢复数据
        print("📥 正在恢复数据库...")
        restore_cmd = [
            'mysql',
            f'--host={{DB_CONFIG["host"]}}',
            f'--port={{DB_CONFIG["port"]}}',
            f'--user={{DB_CONFIG["user"]}}',
            f'--password={{DB_CONFIG["password"]}}',
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
                f'--host={{DB_CONFIG["host"]}}',
                f'--port={{DB_CONFIG["port"]}}',
                f'--user={{DB_CONFIG["user"]}}',
                f'--password={{DB_CONFIG["password"]}}',
                f'--database={{DB_CONFIG["database"]}}',
                '--execute=SHOW TABLES;',
                '--skip-column-names'
            ]
            result = subprocess.run(verify_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                table_count = len([line for line in result.stdout.strip().split('\\n') if line.strip()])
                print(f"📊 恢复了 {{table_count}} 个表")
            
            print("🎉 恢复操作完成!")
            return True
        else:
            print(f"❌ 数据库恢复失败: {{result.stderr}}")
            return False
            
    except Exception as e:
        print(f"❌ 恢复过程中发生错误: {{e}}")
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
'''
        
        python_script_path = self.backup_dir / f"restore_mysql57_{self.timestamp}.py"
        with open(python_script_path, 'w', encoding='utf-8') as f:
            f.write(python_script)
        os.chmod(python_script_path, 0o755)
        
        print(f"📝 恢复脚本已创建:")
        print(f"   - Bash: {bash_script_path.name}")
        print(f"   - Python: {python_script_path.name}")
    
    def export_all(self):
        """执行完整导出流程"""
        print("🚀 MySQL 5.7 完整数据导出工具")
        print("=" * 50)
        
        # 检查MySQL连接
        if not self.check_mysql_connection():
            print("❌ 数据库连接失败，请检查配置")
            return False
        
        # 获取数据库信息
        print("📊 获取数据库信息...")
        db_info = self.get_database_info()
        if db_info:
            print(f"   数据库版本: {db_info.get('version', '未知')}")
            print(f"   数据库大小: {db_info.get('size_mb', '未知')} MB")
            print(f"   表数量: {db_info.get('table_count', 0)}")
        
        # 创建备份文件
        backup_files = []
        
        print("\\n📦 创建备份文件...")
        
        # 创建结构备份
        print("1. 创建结构备份...")
        structure_file = self.create_structure_only_dump()
        if structure_file:
            backup_files.append(structure_file)
        
        # 创建数据备份
        print("2. 创建数据备份...")
        data_file = self.create_data_only_dump()
        if data_file:
            backup_files.append(data_file)
        
        # 创建完整备份
        print("3. 创建完整备份...")
        complete_file = self.create_complete_dump()
        if complete_file:
            backup_files.append(complete_file)
        
        # 创建备份信息
        print("4. 创建备份信息...")
        info_file = self.create_backup_info(backup_files, db_info)
        
        # 创建恢复脚本
        print("5. 创建恢复脚本...")
        self.create_restore_scripts()
        
        # 显示结果
        print("\\n🎉 导出完成!")
        print(f"📁 备份目录: {self.backup_dir}")
        print("\\n📋 生成的文件:")
        
        for filepath in backup_files:
            if filepath and Path(filepath).exists():
                size_mb = Path(filepath).stat().st_size / 1024 / 1024
                backup_type = self._get_backup_type(Path(filepath).name)
                print(f"   - {Path(filepath).name} ({backup_type}, {size_mb:.2f} MB)")
        
        if info_file:
            print(f"   - {Path(info_file).name} (备份信息)")
        
        print("\\n📖 使用说明:")
        print("1. 完整备份文件可直接在MySQL 5.7中使用")
        print("2. 使用恢复脚本可以快速恢复数据库")
        print("3. 结构和数据备份可以分别用于不同场景")
        print("4. 备份信息文件包含详细的备份元数据")
        
        return len(backup_files) > 0

if __name__ == "__main__":
    exporter = MySQL57Exporter()
    success = exporter.export_all()
    exit(0 if success else 1)
