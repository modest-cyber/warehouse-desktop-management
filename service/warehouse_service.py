# -*- coding: utf-8 -*-
"""
仓库信息Service
实现仓库信息的业务逻辑处理
"""

from typing import List, Optional
from datetime import datetime
from dao.warehouse_dao import WarehouseDAO
from model.warehouse import Warehouse
from utils.validator import Validator
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class WarehouseService:
    """仓库信息Service类"""
    
    def __init__(self):
        """初始化Service"""
        self.dao = WarehouseDAO()
        self.validator = Validator()
    
    def add_warehouse(self, warehouse: Warehouse) -> Warehouse:
        """
        添加仓库信息
        
        Args:
            warehouse: 仓库对象
            
        Returns:
            Warehouse: 添加成功的仓库对象
            
        Raises:
            ValueError: 数据验证失败时抛出异常
        """
        # 如果未提供warehouse_code，自动生成
        if not warehouse.warehouse_code:
            warehouse.warehouse_code = self.generate_warehouse_code()
        
        # 数据验证
        is_valid, errors = self.validate_warehouse(warehouse)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证编码唯一性
        is_unique, error_msg = self.validator.validate_unique_code(
            warehouse.warehouse_code, self.dao, 'warehouse_code'
        )
        if not is_unique:
            raise ValueError(error_msg)
        
        # 插入数据库
        warehouse.id = self.dao.insert(warehouse)
        logger.info(f"添加仓库信息成功: ID={warehouse.id}, warehouse_code={warehouse.warehouse_code}")
        return warehouse
    
    def update_warehouse(self, warehouse: Warehouse) -> bool:
        """
        更新仓库信息
        
        Args:
            warehouse: 仓库对象
            
        Returns:
            bool: 是否更新成功
            
        Raises:
            ValueError: 数据验证失败时抛出异常
        """
        # 数据验证
        is_valid, errors = self.validate_warehouse(warehouse)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证编码唯一性（排除自己）
        if warehouse.warehouse_code:
            is_unique, error_msg = self.validator.validate_unique_code(
                warehouse.warehouse_code, self.dao, 'warehouse_code', exclude_id=warehouse.id
            )
            if not is_unique:
                raise ValueError(error_msg)
        
        # 更新数据库
        result = self.dao.update(warehouse)
        logger.info(f"更新仓库信息成功: ID={warehouse.id}")
        return result
    
    def delete_warehouse(self, id: int) -> bool:
        """
        删除仓库信息
        
        Args:
            id: 仓库ID
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            Exception: 删除失败时抛出异常
        """
        # 检查是否被引用
        if self.dao.check_reference(id):
            raise Exception("该仓库已被库存表或出入库记录表引用，无法删除")
        
        result = self.dao.delete(id)
        logger.info(f"删除仓库信息成功: ID={id}")
        return result
    
    def get_warehouse(self, id: int) -> Optional[Warehouse]:
        """
        获取仓库信息
        
        Args:
            id: 仓库ID
            
        Returns:
            Warehouse: 仓库对象，如果不存在返回None
        """
        return self.dao.get_by_id(id)
    
    def get_warehouse_by_code(self, warehouse_code: str) -> Optional[Warehouse]:
        """
        根据编码获取仓库
        
        Args:
            warehouse_code: 仓库编码
            
        Returns:
            Warehouse: 仓库对象，如果不存在返回None
        """
        return self.dao.get_by_code(warehouse_code)
    
    def search_warehouse(self, keyword: str) -> List[Warehouse]:
        """
        搜索仓库（按编码或名称）
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 仓库对象列表
        """
        # 先按编码精确查询
        warehouse = self.dao.get_by_code(keyword)
        if warehouse:
            return [warehouse]
        
        # 再按名称模糊查询
        return self.dao.search_by_name(keyword)
    
    def get_all_warehouse(self) -> List[Warehouse]:
        """
        获取所有仓库
        
        Returns:
            list: 仓库对象列表
        """
        return self.dao.get_all()
    
    def get_active_warehouses(self) -> List[Warehouse]:
        """
        获取所有启用的仓库
        
        Returns:
            list: 仓库对象列表
        """
        return self.dao.get_active_warehouses()
    
    def generate_warehouse_code(self) -> str:
        """
        生成仓库编码（格式：WH+日期+序号）
        
        Returns:
            str: 生成的仓库编码
        """
        date_str = datetime.now().strftime('%Y%m%d')
        prefix = f'WH{date_str}'
        
        # 查询当天已有的最大序号
        sql = "SELECT warehouse_code FROM warehouse WHERE warehouse_code LIKE %s ORDER BY warehouse_code DESC LIMIT 1"
        params = (f'{prefix}%',)
        result = self.dao.fetch_one(sql, params)
        
        if result:
            last_code = result['warehouse_code']
            last_num = int(last_code[-4:])  # 取最后4位作为序号
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def validate_warehouse(self, warehouse: Warehouse) -> tuple:
        """
        验证仓库数据
        
        Args:
            warehouse: 仓库对象
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证warehouse_name不能为空
        is_valid, error_msg = self.validator.validate_not_empty(warehouse.warehouse_name, "仓库名称")
        if not is_valid:
            errors.append(error_msg)
        
        # 验证warehouse_code不能为空
        is_valid, error_msg = self.validator.validate_not_empty(warehouse.warehouse_code, "仓库编码")
        if not is_valid:
            errors.append(error_msg)
        
        # 验证capacity如果存在必须大于等于0
        if warehouse.capacity is not None:
            is_valid, error_msg = self.validator.validate_number(
                float(warehouse.capacity), min_value=0, field_name="容量"
            )
            if not is_valid:
                errors.append(error_msg)
        
        # 验证status值
        if warehouse.status not in [0, 1]:
            errors.append("状态值必须是0或1")
        
        return len(errors) == 0, errors

