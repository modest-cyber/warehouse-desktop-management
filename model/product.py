# -*- coding: utf-8 -*-
"""
货品信息模型
封装product表的数据结构
"""

from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal


class Product:
    """货品信息模型类"""
    
    def __init__(self, id: Optional[int] = None, product_code: str = None,
                 product_name: str = None, category_id: Optional[int] = None,
                 unit_id: Optional[int] = None, specification: Optional[str] = None,
                 price: Optional[Decimal] = None, min_stock: int = 0,
                 max_stock: int = 0, description: Optional[str] = None,
                 status: int = 1, create_time: Optional[datetime] = None,
                 update_time: Optional[datetime] = None, **kwargs):
        """
        初始化货品对象
        
        Args:
            id: 主键ID
            product_code: 货品编码
            product_name: 货品名称
            category_id: 类别ID
            unit_id: 单位ID
            specification: 规格
            price: 单价
            min_stock: 最低库存
            max_stock: 最高库存
            description: 描述
            status: 状态（1-启用，0-禁用）
            create_time: 创建时间
            update_time: 更新时间
        """
        self.id = id
        self.product_code = product_code
        self.product_name = product_name
        self.category_id = category_id
        self.unit_id = unit_id
        self.specification = specification
        self.price = price
        self.min_stock = min_stock
        self.max_stock = max_stock
        self.description = description
        self.status = status
        self.create_time = create_time
        self.update_time = update_time
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """
        从字典创建对象
        
        Args:
            data: 字典数据
            
        Returns:
            Product: 货品对象
        """
        # 处理price字段，可能是字符串或Decimal
        if 'price' in data and data['price'] is not None:
            if isinstance(data['price'], str):
                data['price'] = Decimal(data['price'])
            elif isinstance(data['price'], (int, float)):
                data['price'] = Decimal(str(data['price']))
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            dict: 字典数据
        """
        return {
            'id': self.id,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'category_id': self.category_id,
            'unit_id': self.unit_id,
            'specification': self.specification,
            'price': float(self.price) if self.price is not None else None,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
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
        
        if not self.product_name:
            errors.append("货品名称不能为空")
        
        if self.price is not None and self.price < 0:
            errors.append("单价不能小于0")
        
        if self.min_stock > self.max_stock:
            errors.append("最低库存不能大于最高库存")
        
        return len(errors) == 0, errors
    
    def __repr__(self):
        return f"<Product(id={self.id}, product_code='{self.product_code}', product_name='{self.product_name}')>"

