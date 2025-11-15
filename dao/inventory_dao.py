# -*- coding: utf-8 -*-
"""
库存DAO
实现inventory表的所有数据库操作
"""

from typing import List, Optional
from datetime import datetime
from dao.base_dao import BaseDAO
from model.inventory import Inventory
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class InventoryDAO(BaseDAO):
    """库存DAO类"""
    
    def insert(self, inventory: Inventory) -> int:
        """
        插入库存记录
        
        Args:
            inventory: 库存对象
            
        Returns:
            int: 插入记录的ID
        """
        sql = """
            INSERT INTO inventory (warehouse_id, product_id, quantity, last_in_date, last_out_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            inventory.warehouse_id,
            inventory.product_id,
            inventory.quantity,
            inventory.last_in_date,
            inventory.last_out_date
        )
        
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                connection.commit()
                inventory.id = cursor.lastrowid
                logger.info(f"插入库存记录成功: ID={inventory.id}, warehouse_id={inventory.warehouse_id}, product_id={inventory.product_id}")
                return inventory.id
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"插入库存记录失败: {str(e)}")
            raise Exception(f"插入库存记录失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def update_quantity(self, warehouse_id: int, product_id: int, 
                       quantity_change: int, is_in: bool, 
                       record_date: Optional[datetime] = None) -> bool:
        """
        更新库存数量
        
        Args:
            warehouse_id: 仓库ID
            product_id: 货品ID
            quantity_change: 数量变化（正数表示增加，负数表示减少）
            is_in: 是否为入库
            record_date: 操作日期
            
        Returns:
            bool: 是否更新成功
        """
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                # 先查询是否存在库存记录
                sql_check = "SELECT id, quantity FROM inventory WHERE warehouse_id=%s AND product_id=%s"
                cursor.execute(sql_check, (warehouse_id, product_id))
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有记录
                    new_quantity = existing['quantity'] + quantity_change
                    if new_quantity < 0:
                        raise Exception(f"库存不足，当前库存：{existing['quantity']}，需要：{abs(quantity_change)}")
                    
                    if is_in:
                        sql_update = """
                            UPDATE inventory 
                            SET quantity=%s, last_in_date=%s 
                            WHERE warehouse_id=%s AND product_id=%s
                        """
                        cursor.execute(sql_update, (new_quantity, record_date, warehouse_id, product_id))
                    else:
                        sql_update = """
                            UPDATE inventory 
                            SET quantity=%s, last_out_date=%s 
                            WHERE warehouse_id=%s AND product_id=%s
                        """
                        cursor.execute(sql_update, (new_quantity, record_date, warehouse_id, product_id))
                else:
                    # 创建新记录（只允许入库时创建）
                    if not is_in:
                        raise Exception("库存不存在，无法出库")
                    
                    new_quantity = quantity_change
                    sql_insert = """
                        INSERT INTO inventory (warehouse_id, product_id, quantity, last_in_date)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert, (warehouse_id, product_id, new_quantity, record_date))
                
                connection.commit()
                logger.info(f"更新库存成功: warehouse_id={warehouse_id}, product_id={product_id}, quantity_change={quantity_change}")
                return True
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"更新库存失败: {str(e)}")
            raise
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def get_by_id(self, id: int) -> Optional[Inventory]:
        """
        根据ID查询
        
        Args:
            id: 库存ID
            
        Returns:
            Inventory: 库存对象，如果不存在返回None
        """
        sql = "SELECT * FROM inventory WHERE id=%s"
        params = (id,)
        
        result = self.fetch_one(sql, params)
        if result:
            return Inventory.from_dict(result)
        return None
    
    def get_by_warehouse_product(self, warehouse_id: int, product_id: int) -> Optional[Inventory]:
        """
        根据仓库和货品查询
        
        Args:
            warehouse_id: 仓库ID
            product_id: 货品ID
            
        Returns:
            Inventory: 库存对象，如果不存在返回None
        """
        sql = "SELECT * FROM inventory WHERE warehouse_id=%s AND product_id=%s"
        params = (warehouse_id, product_id)
        
        result = self.fetch_one(sql, params)
        if result:
            return Inventory.from_dict(result)
        return None
    
    def get_by_warehouse(self, warehouse_id: int) -> List[Inventory]:
        """
        根据仓库查询所有库存
        
        Args:
            warehouse_id: 仓库ID
            
        Returns:
            list: 库存对象列表
        """
        sql = "SELECT * FROM inventory WHERE warehouse_id=%s ORDER BY product_id"
        params = (warehouse_id,)
        
        results = self.fetch_all(sql, params)
        return [Inventory.from_dict(row) for row in results]
    
    def get_by_product(self, product_id: int) -> List[Inventory]:
        """
        根据货品查询所有库存
        
        Args:
            product_id: 货品ID
            
        Returns:
            list: 库存对象列表
        """
        sql = "SELECT * FROM inventory WHERE product_id=%s ORDER BY warehouse_id"
        params = (product_id,)
        
        results = self.fetch_all(sql, params)
        return [Inventory.from_dict(row) for row in results]
    
    def get_all(self) -> List[Inventory]:
        """
        查询所有库存记录
        
        Returns:
            list: 库存对象列表
        """
        sql = "SELECT * FROM inventory ORDER BY warehouse_id, product_id"
        results = self.fetch_all(sql)
        return [Inventory.from_dict(row) for row in results]
    
    def check_stock(self, warehouse_id: int, product_id: int, required_quantity: int) -> bool:
        """
        检查库存是否充足
        
        Args:
            warehouse_id: 仓库ID
            product_id: 货品ID
            required_quantity: 需要的数量
            
        Returns:
            bool: 库存是否充足
        """
        inventory = self.get_by_warehouse_product(warehouse_id, product_id)
        if not inventory:
            return False
        return inventory.quantity >= required_quantity

