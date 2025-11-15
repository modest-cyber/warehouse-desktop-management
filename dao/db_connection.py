# -*- coding: utf-8 -*-
"""
数据库连接工具
封装PyMySQL数据库连接操作
"""

import pymysql
from config.database import get_db_config, validate_config
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class DatabaseConnection:
    """数据库连接管理类"""
    
    @staticmethod
    def get_connection():
        """
        获取数据库连接对象
        
        Returns:
            pymysql.Connection: 数据库连接对象
            
        Raises:
            Exception: 连接失败时抛出异常
        """
        try:
            validate_config()
            config = get_db_config()
            
            connection = pymysql.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                charset=config['charset'],
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
            
            logger.info(f"数据库连接成功: {config['host']}:{config['port']}/{config['database']}")
            return connection
            
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise Exception(f"数据库连接失败: {str(e)}")
    
    @staticmethod
    def close_connection(connection):
        """
        关闭数据库连接
        
        Args:
            connection: 数据库连接对象
        """
        if connection:
            try:
                connection.close()
                logger.info("数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭数据库连接失败: {str(e)}")
    
    @staticmethod
    def test_connection():
        """
        测试数据库连接是否正常
        
        Returns:
            bool: 连接是否正常
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("数据库连接测试成功")
                return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False
        finally:
            if connection:
                DatabaseConnection.close_connection(connection)

