# -*- coding: utf-8 -*-
"""
仓库信息模型
封装warehouse表的数据结构
"""

from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal


class Warehouse:
    """仓库信息模型类"""
    
    def __init__(self, id: Optional[int] = None, warehouse_code: str = None,
                 warehouse_name: str = None, address: Optional[str] = None,
                 manager: Optional[str] = None, phone: Optional[str] = None,
                 capacity: Optional[Decimal] = None, description: Optional[str] = None,
                 status: int = 1, create_time: Optional[datetime] = None,
                 update_time: Optional[datetime] = None, **kwargs):
        """
        初始化仓库对象
        
        Args:
            id: 主键ID
            warehouse_code: 仓库编码
            warehouse_name: 仓库名称
            address: 地址
            manager: 负责人
            phone: 联系电话
            capacity: 容量
            description: 描述
            status: 状态（1-启用，0-禁用）
            create_time: 创建时间
            update_time: 更新时间
        """
        self.id = id
        self.warehouse_code = warehouse_code
        self.warehouse_name = warehouse_name
        self.address = address
        self.manager = manager
        self.phone = phone
        self.capacity = capacity
        self.description = description
        self.status = status
        self.create_time = create_time
        self.update_time = update_time
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Warehouse':
        """
        从字典创建对象
        
        Args:
            data: 字典数据
            
        Returns:
            Warehouse: 仓库对象
        """
        # 处理capacity字段
        if 'capacity' in data and data['capacity'] is not None:
            if isinstance(data['capacity'], str):
                data['capacity'] = Decimal(data['capacity'])
            elif isinstance(data['capacity'], (int, float)):
                data['capacity'] = Decimal(str(data['capacity']))
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            dict: 字典数据
        """
        return {
            'id': self.id,
            'warehouse_code': self.warehouse_code,
            'warehouse_name': self.warehouse_name,
            'address': self.address,
            'manager': self.manager,
            'phone': self.phone,
            'capacity': float(self.capacity) if self.capacity is not None else None,
            'description': self.description,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }
    
    def validate(self) -> tuple:
        """
        数据验证方法
        
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        if not self.warehouse_name:
            errors.append("仓库名称不能为空")
        
        if not self.warehouse_code:
            errors.append("仓库编码不能为空")
        
        if self.capacity is not None and self.capacity < 0:
            errors.append("容量不能小于0")
        
        if self.status not in [0, 1]:
            errors.append("状态值必须是0或1")
        
        return len(errors) == 0, errors
    
    def __repr__(self):
        return f"<Warehouse(id={self.id}, warehouse_code='{self.warehouse_code}', warehouse_name='{self.warehouse_name}')>"

