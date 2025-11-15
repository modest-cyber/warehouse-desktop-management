# -*- coding: utf-8 -*-
"""
货品信息DAO
实现product表的所有数据库操作
"""

from typing import List, Optional
from dao.base_dao import BaseDAO
from model.product import Product
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class ProductDAO(BaseDAO):
    """货品信息DAO类"""
    
    def insert(self, product: Product) -> int:
        """
        插入货品信息
        
        Args:
            product: 货品对象
            
        Returns:
            int: 插入记录的ID
        """
        sql = """
            INSERT INTO product (product_code, product_name, category_id, unit_id, 
                                specification, price, min_stock, max_stock, description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            product.product_code,
            product.product_name,
            product.category_id,
            product.unit_id,
            product.specification,
            product.price,
            product.min_stock,
            product.max_stock,
            product.description,
            product.status
        )
        
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                connection.commit()
                product.id = cursor.lastrowid
                logger.info(f"插入货品信息成功: ID={product.id}, product_code={product.product_code}")
                return product.id
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"插入货品信息失败: {str(e)}")
            raise Exception(f"插入货品信息失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def update(self, product: Product) -> bool:
        """
        更新货品信息
        
        Args:
            product: 货品对象
            
        Returns:
            bool: 是否更新成功
        """
        sql = """
            UPDATE product 
            SET product_name=%s, category_id=%s, unit_id=%s, specification=%s,
                price=%s, min_stock=%s, max_stock=%s, description=%s, status=%s
            WHERE id=%s
        """
        params = (
            product.product_name,
            product.category_id,
            product.unit_id,
            product.specification,
            product.price,
            product.min_stock,
            product.max_stock,
            product.description,
            product.status,
            product.id
        )
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"更新货品信息成功: ID={product.id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"更新货品信息失败: {str(e)}")
            raise
    
    def delete(self, id: int) -> bool:
        """
        删除货品信息（需要检查是否被引用）
        
        Args:
            id: 货品ID
            
        Returns:
            bool: 是否删除成功
        """
        # 先检查是否被引用
        if self.check_reference(id):
            raise Exception("该货品已被库存表或出入库记录表引用，无法删除")
        
        sql = "DELETE FROM product WHERE id=%s"
        params = (id,)
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"删除货品信息成功: ID={id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"删除货品信息失败: {str(e)}")
            raise
    
    def get_by_id(self, id: int) -> Optional[Product]:
        """
        根据ID查询
        
        Args:
            id: 货品ID
            
        Returns:
            Product: 货品对象，如果不存在返回None
        """
        sql = "SELECT * FROM product WHERE id=%s"
        params = (id,)
        
        result = self.fetch_one(sql, params)
        if result:
            return Product.from_dict(result)
        return None
    
    def get_by_code(self, product_code: str) -> Optional[Product]:
        """
        根据编码查询
        
        Args:
            product_code: 货品编码
            
        Returns:
            Product: 货品对象，如果不存在返回None
        """
        sql = "SELECT * FROM product WHERE product_code=%s"
        params = (product_code,)
        
        result = self.fetch_one(sql, params)
        if result:
            return Product.from_dict(result)
        return None
    
    def search_by_name(self, keyword: str) -> List[Product]:
        """
        根据名称模糊查询
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 货品对象列表
        """
        sql = "SELECT * FROM product WHERE product_name LIKE %s ORDER BY id"
        params = (f'%{keyword}%',)
        
        results = self.fetch_all(sql, params)
        return [Product.from_dict(row) for row in results]
    
    def get_all(self) -> List[Product]:
        """
        查询所有记录
        
        Returns:
            list: 货品对象列表
        """
        sql = "SELECT * FROM product ORDER BY id"
        results = self.fetch_all(sql)
        return [Product.from_dict(row) for row in results]
    
    def check_reference(self, id: int) -> bool:
        """
        检查是否被库存表或出入库记录表引用
        
        Args:
            id: 货品ID
            
        Returns:
            bool: 是否被引用
        """
        # 检查是否被inventory表引用
        sql1 = "SELECT COUNT(*) as count FROM inventory WHERE product_id=%s"
        result1 = self.fetch_one(sql1, (id,))
        
        # 检查是否被stock_record表引用
        sql2 = "SELECT COUNT(*) as count FROM stock_record WHERE product_id=%s"
        result2 = self.fetch_one(sql2, (id,))
        
        count1 = result1['count'] if result1 else 0
        count2 = result2['count'] if result2 else 0
        
        return (count1 + count2) > 0

