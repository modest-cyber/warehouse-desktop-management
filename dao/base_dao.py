# -*- coding: utf-8 -*-
"""
DAO基类
提供通用的数据库操作方法
"""

from typing import List, Dict, Any, Optional, Callable
from dao.db_connection import DatabaseConnection
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class BaseDAO:
    """DAO基类"""
    
    def __init__(self):
        """初始化DAO"""
        self.db_connection = DatabaseConnection
    
    def execute_query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        执行查询操作
        
        Args:
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            list: 查询结果列表
            
        Raises:
            Exception: 查询失败时抛出异常
        """
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchall()
                logger.debug(f"执行查询: {sql}, 参数: {params}, 结果数: {len(results)}")
                return results
        except Exception as e:
            logger.error(f"查询执行失败: {sql}, 错误: {str(e)}")
            raise Exception(f"查询执行失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def execute_update(self, sql: str, params: tuple = None) -> int:
        """
        执行更新操作（INSERT、UPDATE、DELETE）
        
        Args:
            sql: SQL更新语句
            params: 更新参数
            
        Returns:
            int: 受影响的行数
            
        Raises:
            Exception: 更新失败时抛出异常
        """
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, params)
                connection.commit()
                logger.info(f"执行更新: {sql}, 参数: {params}, 影响行数: {affected_rows}")
                return affected_rows
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"更新执行失败: {sql}, 错误: {str(e)}")
            raise Exception(f"更新执行失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def execute_transaction(self, operations: List[Callable]) -> bool:
        """
        执行事务操作
        
        Args:
            operations: 操作函数列表，每个函数接收connection参数
            
        Returns:
            bool: 是否执行成功
            
        Raises:
            Exception: 事务执行失败时抛出异常
        """
        connection = None
        try:
            connection = self.db_connection.get_connection()
            for operation in operations:
                operation(connection)
            connection.commit()
            logger.info(f"事务执行成功，操作数: {len(operations)}")
            return True
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"事务执行失败: {str(e)}")
            raise Exception(f"事务执行失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def fetch_one(self, sql: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        获取单条记录
        
        Args:
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            dict: 单条记录，如果不存在返回None
        """
        results = self.execute_query(sql, params)
        return results[0] if results else None
    
    def fetch_all(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        获取多条记录
        
        Args:
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            list: 记录列表
        """
        return self.execute_query(sql, params)

