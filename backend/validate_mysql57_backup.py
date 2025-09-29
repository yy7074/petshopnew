#!/usr/bin/env python3
"""
MySQL 5.7 备份文件验证工具
验证备份文件的完整性、兼容性和数据一致性
"""

import os
import re
import json
import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class BackupValidator:
    def __init__(self, backup_dir: str = None):
        self.backup_dir = Path(backup_dir) if backup_dir else Path(__file__).parent / "backups"
        self.temp_db_name = "petshop_validation_temp"
        self.config = self.get_database_config()
        
    def get_database_config(self) -> Dict[str, str]:
        """获取数据库配置"""
        database_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/petshop_auction")
        
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
    
    def find_latest_backup_info(self) -> Optional[str]:
        """查找最新的备份信息文件"""
        info_files = list(self.backup_dir.glob("backup_info_*.json"))
        if not info_files:
            return None
        return str(max(info_files, key=lambda x: x.stat().st_mtime))
    
    def load_backup_info(self, info_file: str) -> Optional[Dict]:
        """加载备份信息"""
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载备份信息失败: {e}")
            return None
    
    def validate_file_integrity(self, backup_info: Dict) -> Dict[str, bool]:
        """验证文件完整性"""
        print("🔍 验证文件完整性...")
        results = {}
        
        for file_info in backup_info.get('backup_files', []):
            filepath = file_info['filepath']
            expected_hash = file_info['md5_hash']
            expected_size = file_info['size_bytes']
            
            if not Path(filepath).exists():
                print(f"❌ 文件不存在: {Path(filepath).name}")
                results[filepath] = False
                continue
            
            # 检查文件大小
            actual_size = Path(filepath).stat().st_size
            if actual_size != expected_size:
                print(f"❌ 文件大小不匹配: {Path(filepath).name} (期望: {expected_size}, 实际: {actual_size})")
                results[filepath] = False
                continue
            
            # 检查MD5哈希
            actual_hash = self.calculate_file_hash(filepath)
            if actual_hash != expected_hash:
                print(f"❌ 文件哈希不匹配: {Path(filepath).name}")
                results[filepath] = False
                continue
            
            print(f"✅ 文件完整: {Path(filepath).name}")
            results[filepath] = True
        
        return results
    
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
    
    def validate_sql_syntax(self, sql_file: str) -> Tuple[bool, List[str]]:
        """验证SQL文件语法"""
        print(f"📝 验证SQL语法: {Path(sql_file).name}")
        
        errors = []
        warnings = []
        
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查基本SQL语法问题
            syntax_checks = [
                (r'CREATE TABLE.*\(\s*\)', "空表定义"),
                (r'INSERT INTO.*\(\s*\)', "空插入语句"),
                (r'ENGINE=\w+.*ENGINE=\w+', "重复ENGINE定义"),
                (r'CHARACTER SET.*CHARACTER SET', "重复字符集定义"),
                (r'COLLATE.*COLLATE', "重复排序规则定义"),
            ]
            
            for pattern, description in syntax_checks:
                if re.search(pattern, content, re.IGNORECASE):
                    errors.append(f"语法问题: {description}")
            
            # 检查MySQL 5.7兼容性
            compatibility_checks = [
                (r'utf8mb4_0900_ai_ci', "使用了MySQL 8.0+排序规则"),
                (r'utf8_0900_ai_ci', "使用了MySQL 8.0+排序规则"),
                (r'/\*!80[0-9]{3}', "包含MySQL 8.0+特有注释"),
                (r'DEFAULT ENCRYPTION=', "使用了MySQL 8.0+加密选项"),
                (r'INVISIBLE', "使用了MySQL 8.0+不可见索引"),
            ]
            
            for pattern, description in compatibility_checks:
                if re.search(pattern, content, re.IGNORECASE):
                    errors.append(f"兼容性问题: {description}")
            
            # 检查推荐的设置
            recommended_checks = [
                (r'CHARACTER SET utf8mb4', "使用utf8mb4字符集"),
                (r'COLLATE utf8mb4_unicode_ci', "使用utf8mb4_unicode_ci排序规则"),
                (r'ENGINE=InnoDB', "使用InnoDB存储引擎"),
            ]
            
            for pattern, description in recommended_checks:
                if not re.search(pattern, content, re.IGNORECASE):
                    warnings.append(f"建议: {description}")
            
            if errors:
                print(f"❌ 发现 {len(errors)} 个错误:")
                for error in errors:
                    print(f"   - {error}")
            
            if warnings:
                print(f"⚠️  发现 {len(warnings)} 个警告:")
                for warning in warnings:
                    print(f"   - {warning}")
            
            if not errors and not warnings:
                print("✅ SQL语法验证通过")
                
            return len(errors) == 0, errors + warnings
            
        except Exception as e:
            error_msg = f"验证过程中发生错误: {e}"
            print(f"❌ {error_msg}")
            return False, [error_msg]
    
    def test_restore_backup(self, backup_file: str) -> Tuple[bool, str]:
        """测试备份恢复（使用临时数据库）"""
        print(f"🔄 测试备份恢复: {Path(backup_file).name}")
        
        try:
            # 创建临时数据库
            print("1. 创建临时测试数据库...")
            create_cmd = [
                'mysql',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["username"]}',
                f'--password={self.config["password"]}',
                f'--execute=DROP DATABASE IF EXISTS {self.temp_db_name}; CREATE DATABASE {self.temp_db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
            ]
            result = subprocess.run(create_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return False, f"创建临时数据库失败: {result.stderr}"
            
            # 恢复备份到临时数据库
            print("2. 恢复备份到临时数据库...")
            restore_cmd = [
                'mysql',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["username"]}',
                f'--password={self.config["password"]}',
                '--default-character-set=utf8mb4',
                self.temp_db_name
            ]
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                result = subprocess.run(restore_cmd, stdin=f, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"恢复备份失败: {result.stderr}"
            
            # 验证表结构
            print("3. 验证表结构...")
            verify_cmd = [
                'mysql',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["username"]}',
                f'--password={self.config["password"]}',
                f'--database={self.temp_db_name}',
                '--execute=SHOW TABLES;',
                '--skip-column-names',
                '--silent'
            ]
            result = subprocess.run(verify_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"验证表结构失败: {result.stderr}"
            
            tables = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            table_count = len(tables)
            
            print(f"✅ 恢复测试成功，共恢复 {table_count} 个表")
            
            return True, f"恢复测试成功，共恢复 {table_count} 个表"
            
        except Exception as e:
            return False, f"恢复测试失败: {e}"
        
        finally:
            # 清理临时数据库
            try:
                cleanup_cmd = [
                    'mysql',
                    f'--host={self.config["host"]}',
                    f'--port={self.config["port"]}',
                    f'--user={self.config["username"]}',
                    f'--password={self.config["password"]}',
                    f'--execute=DROP DATABASE IF EXISTS {self.temp_db_name};'
                ]
                subprocess.run(cleanup_cmd, capture_output=True)
                print("🧹 临时数据库已清理")
            except:
                pass
    
    def compare_with_original(self, backup_info: Dict) -> Dict[str, any]:
        """与原数据库比较"""
        print("📊 与原数据库比较...")
        
        comparison = {
            'table_count_match': False,
            'table_names_match': False,
            'missing_tables': [],
            'extra_tables': []
        }
        
        try:
            # 获取原数据库表列表
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
            
            if result.returncode != 0:
                print(f"❌ 无法获取原数据库表列表: {result.stderr}")
                return comparison
            
            original_tables = set(line.strip() for line in result.stdout.strip().split('\n') if line.strip())
            backup_tables = set(backup_info['database']['tables'])
            
            # 比较表数量
            comparison['table_count_match'] = len(original_tables) == len(backup_tables)
            
            # 比较表名
            comparison['table_names_match'] = original_tables == backup_tables
            comparison['missing_tables'] = list(original_tables - backup_tables)
            comparison['extra_tables'] = list(backup_tables - original_tables)
            
            if comparison['table_count_match'] and comparison['table_names_match']:
                print("✅ 表结构与原数据库完全匹配")
            else:
                print(f"⚠️  表结构不完全匹配:")
                print(f"   原数据库表数量: {len(original_tables)}")
                print(f"   备份表数量: {len(backup_tables)}")
                
                if comparison['missing_tables']:
                    print(f"   缺失的表: {', '.join(comparison['missing_tables'])}")
                
                if comparison['extra_tables']:
                    print(f"   多余的表: {', '.join(comparison['extra_tables'])}")
            
        except Exception as e:
            print(f"❌ 比较过程中发生错误: {e}")
        
        return comparison
    
    def generate_validation_report(self, backup_info: Dict, validation_results: Dict) -> str:
        """生成验证报告"""
        timestamp = backup_info['timestamp']
        report_filename = f"validation_report_{timestamp}.md"
        report_path = self.backup_dir / report_filename
        
        report_content = f"""# MySQL 5.7 备份验证报告

## 基本信息
- **验证时间**: {validation_results.get('validation_time', 'N/A')}
- **备份时间**: {backup_info['created_at']}
- **数据库**: {backup_info['database']['name']}
- **数据库版本**: {backup_info['database']['version']}
- **表数量**: {backup_info['database']['table_count']}

## 文件完整性检查
"""
        
        file_integrity = validation_results.get('file_integrity', {})
        for filepath, is_valid in file_integrity.items():
            filename = Path(filepath).name
            status = "✅ 通过" if is_valid else "❌ 失败"
            report_content += f"- **{filename}**: {status}\n"
        
        report_content += "\n## SQL语法验证\n"
        sql_validation = validation_results.get('sql_validation', {})
        for filepath, (is_valid, messages) in sql_validation.items():
            filename = Path(filepath).name
            status = "✅ 通过" if is_valid else "❌ 失败"
            report_content += f"- **{filename}**: {status}\n"
            
            if messages:
                for message in messages:
                    report_content += f"  - {message}\n"
        
        report_content += "\n## 恢复测试\n"
        restore_test = validation_results.get('restore_test', {})
        for filepath, (is_success, message) in restore_test.items():
            filename = Path(filepath).name
            status = "✅ 成功" if is_success else "❌ 失败"
            report_content += f"- **{filename}**: {status}\n"
            report_content += f"  - {message}\n"
        
        report_content += "\n## 数据一致性检查\n"
        comparison = validation_results.get('comparison', {})
        if comparison:
            table_match = "✅ 匹配" if comparison.get('table_names_match', False) else "❌ 不匹配"
            report_content += f"- **表结构匹配**: {table_match}\n"
            
            if comparison.get('missing_tables'):
                report_content += f"- **缺失表**: {', '.join(comparison['missing_tables'])}\n"
            
            if comparison.get('extra_tables'):
                report_content += f"- **多余表**: {', '.join(comparison['extra_tables'])}\n"
        
        report_content += f"\n## 备份文件列表\n"
        for file_info in backup_info['backup_files']:
            report_content += f"- **{file_info['filename']}** ({file_info['type']})\n"
            report_content += f"  - 大小: {file_info['size_mb']} MB\n"
            report_content += f"  - MD5: `{file_info['md5_hash']}`\n"
        
        report_content += f"\n## 使用建议\n"
        report_content += f"1. 建议优先使用完整备份文件进行恢复\n"
        report_content += f"2. 在生产环境恢复前，请先在测试环境验证\n"
        report_content += f"3. 恢复前请确保MySQL版本为5.7或更高版本\n"
        report_content += f"4. 建议使用utf8mb4字符集和utf8mb4_unicode_ci排序规则\n"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"📋 验证报告已生成: {report_filename}")
            return str(report_path)
        except Exception as e:
            print(f"❌ 生成验证报告失败: {e}")
            return ""
    
    def validate_all(self) -> bool:
        """执行完整验证流程"""
        print("🔍 MySQL 5.7 备份验证工具")
        print("=" * 50)
        
        # 查找备份信息文件
        info_file = self.find_latest_backup_info()
        if not info_file:
            print("❌ 没有找到备份信息文件")
            return False
        
        print(f"📋 使用备份信息: {Path(info_file).name}")
        
        # 加载备份信息
        backup_info = self.load_backup_info(info_file)
        if not backup_info:
            return False
        
        validation_results = {
            'validation_time': f"{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        # 1. 验证文件完整性
        print("\n" + "="*30)
        validation_results['file_integrity'] = self.validate_file_integrity(backup_info)
        
        # 2. 验证SQL语法
        print("\n" + "="*30)
        validation_results['sql_validation'] = {}
        for file_info in backup_info['backup_files']:
            filepath = file_info['filepath']
            if Path(filepath).exists() and filepath.endswith('.sql'):
                is_valid, messages = self.validate_sql_syntax(filepath)
                validation_results['sql_validation'][filepath] = (is_valid, messages)
        
        # 3. 测试恢复
        print("\n" + "="*30)
        validation_results['restore_test'] = {}
        # 只测试完整备份文件
        for file_info in backup_info['backup_files']:
            if file_info['type'] == '完整备份':
                filepath = file_info['filepath']
                if Path(filepath).exists():
                    is_success, message = self.test_restore_backup(filepath)
                    validation_results['restore_test'][filepath] = (is_success, message)
                    break
        
        # 4. 与原数据库比较
        print("\n" + "="*30)
        validation_results['comparison'] = self.compare_with_original(backup_info)
        
        # 5. 生成验证报告
        print("\n" + "="*30)
        report_path = self.generate_validation_report(backup_info, validation_results)
        
        # 总结
        print("\n🎉 验证完成!")
        
        all_files_valid = all(validation_results['file_integrity'].values())
        all_sql_valid = all(result[0] for result in validation_results['sql_validation'].values())
        all_restore_success = all(result[0] for result in validation_results['restore_test'].values())
        
        if all_files_valid and all_sql_valid and all_restore_success:
            print("✅ 所有验证项目都通过了!")
            return True
        else:
            print("⚠️  部分验证项目未通过，请查看详细报告")
            return False

if __name__ == "__main__":
    import sys
    
    backup_dir = sys.argv[1] if len(sys.argv) > 1 else None
    validator = BackupValidator(backup_dir)
    
    success = validator.validate_all()
    sys.exit(0 if success else 1)
