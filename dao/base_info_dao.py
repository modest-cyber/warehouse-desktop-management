# -*- coding: utf-8 -*-
"""
基础信息DAO
实现base_info表的所有数据库操作
"""

from typing import List, Optional
from dao.base_dao import BaseDAO
from model.base_info import BaseInfo
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class BaseInfoDAO(BaseDAO):
    """基础信息DAO类"""
    
    def insert(self, base_info: BaseInfo) -> int:
        """
        插入基础信息
        
        Args:
            base_info: 基础信息对象
            
        Returns:
            int: 插入记录的ID
        """
        sql = """
            INSERT INTO base_info (info_type, info_name, info_code, description, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            base_info.info_type,
            base_info.info_name,
            base_info.info_code,
            base_info.description,
            base_info.status
        )
        
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                connection.commit()
                base_info.id = cursor.lastrowid
                logger.info(f"插入基础信息成功: ID={base_info.id}, info_name={base_info.info_name}")
                return base_info.id
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"插入基础信息失败: {str(e)}")
            raise Exception(f"插入基础信息失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def update(self, base_info: BaseInfo) -> bool:
        """
        更新基础信息
        
        Args:
            base_info: 基础信息对象
            
        Returns:
            bool: 是否更新成功
        """
        sql = """
            UPDATE base_info 
            SET info_type=%s, info_name=%s, info_code=%s, description=%s, status=%s
            WHERE id=%s
        """
        params = (
            base_info.info_type,
            base_info.info_name,
            base_info.info_code,
            base_info.description,
            base_info.status,
            base_info.id
        )
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"更新基础信息成功: ID={base_info.id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"更新基础信息失败: {str(e)}")
            raise
    
    def delete(self, id: int) -> bool:
        """
        删除基础信息（需要检查是否被引用）
        
        Args:
            id: 基础信息ID
            
        Returns:
            bool: 是否删除成功
        """
        # 先检查是否被引用
        if self.check_reference(id):
            raise Exception("该基础信息已被其他表引用，无法删除")
        
        sql = "DELETE FROM base_info WHERE id=%s"
        params = (id,)
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"删除基础信息成功: ID={id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"删除基础信息失败: {str(e)}")
            raise
    
    def get_by_id(self, id: int) -> Optional[BaseInfo]:
        """
        根据ID查询
        
        Args:
            id: 基础信息ID
            
        Returns:
            BaseInfo: 基础信息对象，如果不存在返回None
        """
        sql = "SELECT * FROM base_info WHERE id=%s"
        params = (id,)
        
        result = self.fetch_one(sql, params)
        if result:
            return BaseInfo.from_dict(result)
        return None
    
    def get_by_type(self, info_type: str) -> List[BaseInfo]:
        """
        根据类型查询
        
        Args:
            info_type: 信息类型
            
        Returns:
            list: 基础信息对象列表
        """
        sql = "SELECT * FROM base_info WHERE info_type=%s AND status=1 ORDER BY id"
        params = (info_type,)
        
        results = self.fetch_all(sql, params)
        return [BaseInfo.from_dict(row) for row in results]
    
    def get_all(self) -> List[BaseInfo]:
        """
        查询所有记录
        
        Returns:
            list: 基础信息对象列表
        """
        sql = "SELECT * FROM base_info ORDER BY id"
        results = self.fetch_all(sql)
        return [BaseInfo.from_dict(row) for row in results]
    
    def check_reference(self, id: int) -> bool:
        """
        检查是否被其他表引用
        
        Args:
            id: 基础信息ID
            
        Returns:
            bool: 是否被引用
        """
        # 检查是否被product表的category_id或unit_id引用
        sql = """
            SELECT COUNT(*) as count FROM product 
            WHERE category_id=%s OR unit_id=%s
        """
        params = (id, id)
        
        result = self.fetch_one(sql, params)
        return result['count'] > 0 if result else False

