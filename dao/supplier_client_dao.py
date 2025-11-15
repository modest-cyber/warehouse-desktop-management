# -*- coding: utf-8 -*-
"""
供应商/客户信息DAO
实现supplier_client表的所有数据库操作
"""

from typing import List, Optional
from dao.base_dao import BaseDAO
from model.supplier_client import SupplierClient
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class SupplierClientDAO(BaseDAO):
    """供应商/客户信息DAO类"""
    
    def insert(self, supplier_client: SupplierClient) -> int:
        """
        插入供应商/客户信息
        
        Args:
            supplier_client: 供应商/客户对象
            
        Returns:
            int: 插入记录的ID
        """
        sql = """
            INSERT INTO supplier_client (code, name, type, contact_person, phone, 
                                       email, address, description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            supplier_client.code,
            supplier_client.name,
            supplier_client.type,
            supplier_client.contact_person,
            supplier_client.phone,
            supplier_client.email,
            supplier_client.address,
            supplier_client.description,
            supplier_client.status
        )
        
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                connection.commit()
                supplier_client.id = cursor.lastrowid
                logger.info(f"插入供应商/客户信息成功: ID={supplier_client.id}, code={supplier_client.code}")
                return supplier_client.id
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"插入供应商/客户信息失败: {str(e)}")
            raise Exception(f"插入供应商/客户信息失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def update(self, supplier_client: SupplierClient) -> bool:
        """
        更新供应商/客户信息
        
        Args:
            supplier_client: 供应商/客户对象
            
        Returns:
            bool: 是否更新成功
        """
        sql = """
            UPDATE supplier_client 
            SET name=%s, type=%s, contact_person=%s, phone=%s, email=%s, 
                address=%s, description=%s, status=%s
            WHERE id=%s
        """
        params = (
            supplier_client.name,
            supplier_client.type,
            supplier_client.contact_person,
            supplier_client.phone,
            supplier_client.email,
            supplier_client.address,
            supplier_client.description,
            supplier_client.status,
            supplier_client.id
        )
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"更新供应商/客户信息成功: ID={supplier_client.id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"更新供应商/客户信息失败: {str(e)}")
            raise
    
    def delete(self, id: int) -> bool:
        """
        删除供应商/客户信息（需要检查是否被引用）
        
        Args:
            id: 供应商/客户ID
            
        Returns:
            bool: 是否删除成功
        """
        # 先检查是否被引用
        if self.check_reference(id):
            raise Exception("该供应商/客户已被出入库记录表引用，无法删除")
        
        sql = "DELETE FROM supplier_client WHERE id=%s"
        params = (id,)
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"删除供应商/客户信息成功: ID={id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"删除供应商/客户信息失败: {str(e)}")
            raise
    
    def get_by_id(self, id: int) -> Optional[SupplierClient]:
        """
        根据ID查询
        
        Args:
            id: 供应商/客户ID
            
        Returns:
            SupplierClient: 供应商/客户对象，如果不存在返回None
        """
        sql = "SELECT * FROM supplier_client WHERE id=%s"
        params = (id,)
        
        result = self.fetch_one(sql, params)
        if result:
            return SupplierClient.from_dict(result)
        return None
    
    def get_by_code(self, code: str) -> Optional[SupplierClient]:
        """
        根据编码查询
        
        Args:
            code: 编码
            
        Returns:
            SupplierClient: 供应商/客户对象，如果不存在返回None
        """
        sql = "SELECT * FROM supplier_client WHERE code=%s"
        params = (code,)
        
        result = self.fetch_one(sql, params)
        if result:
            return SupplierClient.from_dict(result)
        return None
    
    def search_by_name(self, keyword: str) -> List[SupplierClient]:
        """
        根据名称模糊查询
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 供应商/客户对象列表
        """
        sql = "SELECT * FROM supplier_client WHERE name LIKE %s ORDER BY id"
        params = (f'%{keyword}%',)
        
        results = self.fetch_all(sql, params)
        return [SupplierClient.from_dict(row) for row in results]
    
    def get_by_type(self, type_value: int) -> List[SupplierClient]:
        """
        根据类型查询（1-供应商，2-客户）
        
        Args:
            type_value: 类型值
            
        Returns:
            list: 供应商/客户对象列表
        """
        sql = "SELECT * FROM supplier_client WHERE type=%s ORDER BY id"
        params = (type_value,)
        
        results = self.fetch_all(sql, params)
        return [SupplierClient.from_dict(row) for row in results]
    
    def get_all(self) -> List[SupplierClient]:
        """
        查询所有记录
        
        Returns:
            list: 供应商/客户对象列表
        """
        sql = "SELECT * FROM supplier_client ORDER BY id"
        results = self.fetch_all(sql)
        return [SupplierClient.from_dict(row) for row in results]
    
    def get_suppliers(self) -> List[SupplierClient]:
        """
        查询所有供应商
        
        Returns:
            list: 供应商对象列表
        """
        return self.get_by_type(1)
    
    def get_clients(self) -> List[SupplierClient]:
        """
        查询所有客户
        
        Returns:
            list: 客户对象列表
        """
        return self.get_by_type(2)
    
    def check_reference(self, id: int) -> bool:
        """
        检查是否被出入库记录表引用
        
        Args:
            id: 供应商/客户ID
            
        Returns:
            bool: 是否被引用
        """
        sql = "SELECT COUNT(*) as count FROM stock_record WHERE supplier_client_id=%s"
        result = self.fetch_one(sql, (id,))
        return result['count'] > 0 if result else False

