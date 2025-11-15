# -*- coding: utf-8 -*-
"""
供应商/客户信息Service
实现供应商/客户信息的业务逻辑处理
"""

from typing import List, Optional
from datetime import datetime
from dao.supplier_client_dao import SupplierClientDAO
from model.supplier_client import SupplierClient
from utils.validator import Validator
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class SupplierClientService:
    """供应商/客户信息Service类"""
    
    def __init__(self):
        """初始化Service"""
        self.dao = SupplierClientDAO()
        self.validator = Validator()
    
    def add_supplier_client(self, supplier_client: SupplierClient) -> SupplierClient:
        """
        添加供应商/客户信息
        
        Args:
            supplier_client: 供应商/客户对象
            
        Returns:
            SupplierClient: 添加成功的供应商/客户对象
            
        Raises:
            ValueError: 数据验证失败时抛出异常
        """
        # 如果未提供code，自动生成
        if not supplier_client.code:
            supplier_client.code = self.generate_code(supplier_client.type)
        
        # 数据验证
        is_valid, errors = self.validate_supplier_client(supplier_client)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证编码唯一性
        is_unique, error_msg = self.validator.validate_unique_code(
            supplier_client.code, self.dao, 'code'
        )
        if not is_unique:
            raise ValueError(error_msg)
        
        # 插入数据库
        supplier_client.id = self.dao.insert(supplier_client)
        logger.info(f"添加供应商/客户信息成功: ID={supplier_client.id}, code={supplier_client.code}")
        return supplier_client
    
    def update_supplier_client(self, supplier_client: SupplierClient) -> bool:
        """
        更新供应商/客户信息
        
        Args:
            supplier_client: 供应商/客户对象
            
        Returns:
            bool: 是否更新成功
            
        Raises:
            ValueError: 数据验证失败时抛出异常
        """
        # 数据验证
        is_valid, errors = self.validate_supplier_client(supplier_client)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证编码唯一性（排除自己）
        if supplier_client.code:
            is_unique, error_msg = self.validator.validate_unique_code(
                supplier_client.code, self.dao, 'code', exclude_id=supplier_client.id
            )
            if not is_unique:
                raise ValueError(error_msg)
        
        # 更新数据库
        result = self.dao.update(supplier_client)
        logger.info(f"更新供应商/客户信息成功: ID={supplier_client.id}")
        return result
    
    def delete_supplier_client(self, id: int) -> bool:
        """
        删除供应商/客户信息
        
        Args:
            id: 供应商/客户ID
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            Exception: 删除失败时抛出异常
        """
        # 检查是否被引用
        if self.dao.check_reference(id):
            raise Exception("该供应商/客户已被出入库记录表引用，无法删除")
        
        result = self.dao.delete(id)
        logger.info(f"删除供应商/客户信息成功: ID={id}")
        return result
    
    def get_supplier_client(self, id: int) -> Optional[SupplierClient]:
        """
        获取供应商/客户信息
        
        Args:
            id: 供应商/客户ID
            
        Returns:
            SupplierClient: 供应商/客户对象，如果不存在返回None
        """
        return self.dao.get_by_id(id)
    
    def get_supplier_client_by_code(self, code: str) -> Optional[SupplierClient]:
        """
        根据编码获取
        
        Args:
            code: 编码
            
        Returns:
            SupplierClient: 供应商/客户对象，如果不存在返回None
        """
        return self.dao.get_by_code(code)
    
    def search_supplier_client(self, keyword: str) -> List[SupplierClient]:
        """
        搜索供应商/客户
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 供应商/客户对象列表
        """
        # 先按编码精确查询
        supplier_client = self.dao.get_by_code(keyword)
        if supplier_client:
            return [supplier_client]
        
        # 再按名称模糊查询
        return self.dao.search_by_name(keyword)
    
    def get_all_supplier_client(self) -> List[SupplierClient]:
        """
        获取所有记录
        
        Returns:
            list: 供应商/客户对象列表
        """
        return self.dao.get_all()
    
    def get_suppliers(self) -> List[SupplierClient]:
        """
        获取所有供应商
        
        Returns:
            list: 供应商对象列表
        """
        return self.dao.get_suppliers()
    
    def get_clients(self) -> List[SupplierClient]:
        """
        获取所有客户
        
        Returns:
            list: 客户对象列表
        """
        return self.dao.get_clients()
    
    def generate_code(self, type_value: int) -> str:
        """
        生成编码（根据类型生成不同前缀）
        
        Args:
            type_value: 类型（1-供应商，2-客户）
            
        Returns:
            str: 生成的编码
        """
        date_str = datetime.now().strftime('%Y%m%d')
        
        if type_value == 1:
            prefix = f'SUP{date_str}'
        elif type_value == 2:
            prefix = f'CLI{date_str}'
        else:
            prefix = f'SC{date_str}'
        
        # 查询当天已有的最大序号
        sql = "SELECT code FROM supplier_client WHERE code LIKE %s ORDER BY code DESC LIMIT 1"
        params = (f'{prefix}%',)
        result = self.dao.fetch_one(sql, params)
        
        if result:
            last_code = result['code']
            last_num = int(last_code[-4:])  # 取最后4位作为序号
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def validate_supplier_client(self, supplier_client: SupplierClient) -> tuple:
        """
        验证数据
        
        Args:
            supplier_client: 供应商/客户对象
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证name不能为空
        is_valid, error_msg = self.validator.validate_not_empty(supplier_client.name, "名称")
        if not is_valid:
            errors.append(error_msg)
        
        # 验证code不能为空
        is_valid, error_msg = self.validator.validate_not_empty(supplier_client.code, "编码")
        if not is_valid:
            errors.append(error_msg)
        
        # 验证type的值只能是1或2
        if supplier_client.type not in [1, 2]:
            errors.append("类型值必须是1（供应商）或2（客户）")
        
        # 验证email格式（如果提供）
        if supplier_client.email:
            is_valid, error_msg = self.validator.validate_email(supplier_client.email)
            if not is_valid:
                errors.append(error_msg)
        
        # 验证status值
        if supplier_client.status not in [0, 1]:
            errors.append("状态值必须是0或1")
        
        return len(errors) == 0, errors

