# -*- coding: utf-8 -*-
"""
库存模型
封装inventory表的数据结构
"""

from datetime import datetime
from typing import Optional, Dict, Any


class Inventory:
    """库存模型类"""
    
    def __init__(self, id: Optional[int] = None, warehouse_id: int = None,
                 product_id: int = None, quantity: int = 0,
                 last_in_date: Optional[datetime] = None,
                 last_out_date: Optional[datetime] = None,
                 update_time: Optional[datetime] = None, **kwargs):
        """
        初始化库存对象
        
        Args:
            id: 主键ID
            warehouse_id: 仓库ID
            product_id: 货品ID
            quantity: 库存数量
            last_in_date: 最后入库日期
            last_out_date: 最后出库日期
            update_time: 更新时间
        """
        self.id = id
        self.warehouse_id = warehouse_id
        self.product_id = product_id
        self.quantity = quantity
        self.last_in_date = last_in_date
        self.last_out_date = last_out_date
        self.update_time = update_time
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Inventory':
        """
        从字典创建对象
        
        Args:
            data: 字典数据
            
        Returns:
            Inventory: 库存对象
        """
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            dict: 字典数据
        """
        return {
            'id': self.id,
            'warehouse_id': self.warehouse_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'last_in_date': self.last_in_date.strftime('%Y-%m-%d %H:%M:%S') if self.last_in_date else None,
            'last_out_date': self.last_out_date.strftime('%Y-%m-%d %H:%M:%S') if self.last_out_date else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }
    
    def validate(self) -> tuple:
        """
        数据验证方法
        
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        if not self.warehouse_id:
            errors.append("仓库ID不能为空")
        
        if not self.product_id:
            errors.append("货品ID不能为空")
        
        if self.quantity < 0:
            errors.append("库存数量不能为负数")
        
        return len(errors) == 0, errors
    
    def __repr__(self):
        return f"<Inventory(id={self.id}, warehouse_id={self.warehouse_id}, product_id={self.product_id}, quantity={self.quantity})>"

