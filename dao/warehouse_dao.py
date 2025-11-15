# -*- coding: utf-8 -*-
"""
仓库信息DAO
实现warehouse表的所有数据库操作
"""

from typing import List, Optional
from dao.base_dao import BaseDAO
from model.warehouse import Warehouse
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class WarehouseDAO(BaseDAO):
    """仓库信息DAO类"""
    
    def insert(self, warehouse: Warehouse) -> int:
        """
        插入仓库信息
        
        Args:
            warehouse: 仓库对象
            
        Returns:
            int: 插入记录的ID
        """
        sql = """
            INSERT INTO warehouse (warehouse_code, warehouse_name, address, manager, 
                                  phone, capacity, description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            warehouse.warehouse_code,
            warehouse.warehouse_name,
            warehouse.address,
            warehouse.manager,
            warehouse.phone,
            warehouse.capacity,
            warehouse.description,
            warehouse.status
        )
        
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                connection.commit()
                warehouse.id = cursor.lastrowid
                logger.info(f"插入仓库信息成功: ID={warehouse.id}, warehouse_code={warehouse.warehouse_code}")
                return warehouse.id
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"插入仓库信息失败: {str(e)}")
            raise Exception(f"插入仓库信息失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def update(self, warehouse: Warehouse) -> bool:
        """
        更新仓库信息
        
        Args:
            warehouse: 仓库对象
            
        Returns:
            bool: 是否更新成功
        """
        sql = """
            UPDATE warehouse 
            SET warehouse_name=%s, address=%s, manager=%s, phone=%s, 
                capacity=%s, description=%s, status=%s
            WHERE id=%s
        """
        params = (
            warehouse.warehouse_name,
            warehouse.address,
            warehouse.manager,
            warehouse.phone,
            warehouse.capacity,
            warehouse.description,
            warehouse.status,
            warehouse.id
        )
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"更新仓库信息成功: ID={warehouse.id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"更新仓库信息失败: {str(e)}")
            raise
    
    def delete(self, id: int) -> bool:
        """
        删除仓库信息（需要检查是否被引用）
        
        Args:
            id: 仓库ID
            
        Returns:
            bool: 是否删除成功
        """
        # 先检查是否被引用
        if self.check_reference(id):
            raise Exception("该仓库已被库存表或出入库记录表引用，无法删除")
        
        sql = "DELETE FROM warehouse WHERE id=%s"
        params = (id,)
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"删除仓库信息成功: ID={id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"删除仓库信息失败: {str(e)}")
            raise
    
    def get_by_id(self, id: int) -> Optional[Warehouse]:
        """
        根据ID查询
        
        Args:
            id: 仓库ID
            
        Returns:
            Warehouse: 仓库对象，如果不存在返回None
        """
        sql = "SELECT * FROM warehouse WHERE id=%s"
        params = (id,)
        
        result = self.fetch_one(sql, params)
        if result:
            return Warehouse.from_dict(result)
        return None
    
    def get_by_code(self, warehouse_code: str) -> Optional[Warehouse]:
        """
        根据编码查询
        
        Args:
            warehouse_code: 仓库编码
            
        Returns:
            Warehouse: 仓库对象，如果不存在返回None
        """
        sql = "SELECT * FROM warehouse WHERE warehouse_code=%s"
        params = (warehouse_code,)
        
        result = self.fetch_one(sql, params)
        if result:
            return Warehouse.from_dict(result)
        return None
    
    def search_by_name(self, keyword: str) -> List[Warehouse]:
        """
        根据名称模糊查询
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 仓库对象列表
        """
        sql = "SELECT * FROM warehouse WHERE warehouse_name LIKE %s ORDER BY id"
        params = (f'%{keyword}%',)
        
        results = self.fetch_all(sql, params)
        return [Warehouse.from_dict(row) for row in results]
    
    def get_all(self) -> List[Warehouse]:
        """
        查询所有记录
        
        Returns:
            list: 仓库对象列表
        """
        sql = "SELECT * FROM warehouse ORDER BY id"
        results = self.fetch_all(sql)
        return [Warehouse.from_dict(row) for row in results]
    
    def get_active_warehouses(self) -> List[Warehouse]:
        """
        查询所有启用的仓库
        
        Returns:
            list: 仓库对象列表
        """
        sql = "SELECT * FROM warehouse WHERE status=1 ORDER BY id"
        results = self.fetch_all(sql)
        return [Warehouse.from_dict(row) for row in results]
    
    def check_reference(self, id: int) -> bool:
        """
        检查是否被库存表或出入库记录表引用
        
        Args:
            id: 仓库ID
            
        Returns:
            bool: 是否被引用
        """
        # 检查是否被inventory表引用
        sql1 = "SELECT COUNT(*) as count FROM inventory WHERE warehouse_id=%s"
        result1 = self.fetch_one(sql1, (id,))
        
        # 检查是否被stock_record表引用
        sql2 = "SELECT COUNT(*) as count FROM stock_record WHERE warehouse_id=%s"
        result2 = self.fetch_one(sql2, (id,))
        
        count1 = result1['count'] if result1 else 0
        count2 = result2['count'] if result2 else 0
        
        return (count1 + count2) > 0

