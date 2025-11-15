# -*- coding: utf-8 -*-
"""
系统管理Service
实现系统管理相关功能
"""

from typing import Dict, Any
from dao.db_connection import DatabaseConnection
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class SystemService:
    """系统管理Service类"""
    
    def __init__(self):
        """初始化Service"""
        self.db_connection = DatabaseConnection()
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息
        
        Returns:
            dict: 系统信息，包含：
                - database_version: 数据库版本
                - table_count: 表数量
                - database_name: 数据库名称
        """
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                # 获取数据库版本
                cursor.execute("SELECT VERSION() as version")
                version_result = cursor.fetchone()
                database_version = version_result['version'] if version_result else 'Unknown'
                
                # 获取数据库名称
                cursor.execute("SELECT DATABASE() as db_name")
                db_result = cursor.fetchone()
                database_name = db_result['db_name'] if db_result else 'Unknown'
                
                # 获取表数量
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                """, (database_name,))
                table_result = cursor.fetchone()
                table_count = table_result['count'] if table_result else 0
                
                return {
                    'database_version': database_version,
                    'database_name': database_name,
                    'table_count': table_count
                }
        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}")
            raise Exception(f"获取系统信息失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def check_database_connection(self) -> bool:
        """
        检查数据库连接
        
        Returns:
            bool: 连接是否正常
        """
        return self.db_connection.test_connection()
    
    def backup_database(self, backup_path: str) -> bool:
        """
        备份数据库（可选功能）
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 是否备份成功
            
        Note:
            此功能需要mysqldump命令，实际使用时需要根据环境配置
        """
        try:
            from config.database import get_db_config
            import subprocess
            import os
            
            config = get_db_config()
            
            # 构建mysqldump命令
            cmd = [
                'mysqldump',
                f'-h{config["host"]}',
                f'-P{config["port"]}',
                f'-u{config["user"]}',
                f'-p{config["password"]}',
                '--single-transaction',
                '--routines',
                '--triggers',
                config['database']
            ]
            
            # 执行备份
            with open(backup_path, 'w', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                logger.info(f"数据库备份成功: {backup_path}")
                return True
            else:
                logger.error(f"数据库备份失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"数据库备份失败: {str(e)}")
            raise Exception(f"数据库备份失败: {str(e)}")
    
    def restore_database(self, backup_path: str) -> bool:
        """
        恢复数据库（可选功能）
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 是否恢复成功
            
        Note:
            此功能需要mysql命令，实际使用时需要根据环境配置
            恢复操作会清空现有数据，请谨慎使用
        """
        try:
            from config.database import get_db_config
            import subprocess
            
            config = get_db_config()
            
            # 构建mysql命令
            cmd = [
                'mysql',
                f'-h{config["host"]}',
                f'-P{config["port"]}',
                f'-u{config["user"]}',
                f'-p{config["password"]}',
                config['database']
            ]
            
            # 执行恢复
            with open(backup_path, 'r', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                logger.info(f"数据库恢复成功: {backup_path}")
                return True
            else:
                logger.error(f"数据库恢复失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"数据库恢复失败: {str(e)}")
            raise Exception(f"数据库恢复失败: {str(e)}")

