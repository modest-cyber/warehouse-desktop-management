# -*- coding: utf-8 -*-
"""
入库/出库记录模型
封装stock_record表的数据结构
"""

from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal


class StockRecord:
    """入库/出库记录模型类"""
    
    def __init__(self, id: Optional[int] = None, record_no: str = None,
                 record_type: int = None, warehouse_id: int = None,
                 product_id: int = None, quantity: int = None,
                 unit_price: Optional[Decimal] = None,
                 total_amount: Optional[Decimal] = None,
                 supplier_client_id: Optional[int] = None,
                 operator: Optional[str] = None,
                 record_date: Optional[datetime] = None,
                 remark: Optional[str] = None,
                 create_time: Optional[datetime] = None, **kwargs):
        """
        初始化出入库记录对象
        
        Args:
            id: 主键ID
            record_no: 单据号
            record_type: 类型（1-入库，2-出库）
            warehouse_id: 仓库ID
            product_id: 货品ID
            quantity: 数量
            unit_price: 单价
            total_amount: 总金额
            supplier_client_id: 供应商/客户ID
            operator: 操作人
            record_date: 操作日期
            remark: 备注
            create_time: 创建时间
        """
        self.id = id
        self.record_no = record_no
        self.record_type = record_type
        self.warehouse_id = warehouse_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_amount = total_amount
        self.supplier_client_id = supplier_client_id
        self.operator = operator
        self.record_date = record_date
        self.remark = remark
        self.create_time = create_time
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StockRecord':
        """
        从字典创建对象
        
        Args:
            data: 字典数据
            
        Returns:
            StockRecord: 出入库记录对象
        """
        # 处理price和total_amount字段
        for field in ['unit_price', 'total_amount']:
            if field in data and data[field] is not None:
                if isinstance(data[field], str):
                    data[field] = Decimal(data[field])
                elif isinstance(data[field], (int, float)):
                    data[field] = Decimal(str(data[field]))
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            dict: 字典数据
        """
        return {
            'id': self.id,
            'record_no': self.record_no,
            'record_type': self.record_type,
            'warehouse_id': self.warehouse_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price is not None else None,
            'total_amount': float(self.total_amount) if self.total_amount is not None else None,
            'supplier_client_id': self.supplier_client_id,
            'operator': self.operator,
            'record_date': self.record_date.strftime('%Y-%m-%d %H:%M:%S') if self.record_date else None,
            'remark': self.remark,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None
        }
    
    def validate(self) -> tuple:
        """
        数据验证方法
        
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        if not self.record_no:
            errors.append("单据号不能为空")
        
        if self.record_type not in [1, 2]:
            errors.append("记录类型必须是1（入库）或2（出库）")
        
        if not self.warehouse_id:
            errors.append("仓库ID不能为空")
        
        if not self.product_id:
            errors.append("货品ID不能为空")
        
        if not self.quantity or self.quantity <= 0:
            errors.append("数量必须大于0")
        
        if self.unit_price is not None and self.unit_price < 0:
            errors.append("单价不能小于0")
        
        if not self.record_date:
            errors.append("操作日期不能为空")
        
        return len(errors) == 0, errors
    
    def is_in_stock(self) -> bool:
        """
        判断是否为入库
        
        Returns:
            bool: 是否为入库
        """
        return self.record_type == 1
    
    def is_out_stock(self) -> bool:
        """
        判断是否为出库
        
        Returns:
            bool: 是否为出库
        """
        return self.record_type == 2
    
    def calculate_total_amount(self) -> Decimal:
        """
        计算总金额
        
        Returns:
            Decimal: 总金额
        """
        if self.quantity and self.unit_price:
            self.total_amount = Decimal(str(self.quantity)) * self.unit_price
            return self.total_amount
        return Decimal('0')
    
    def __repr__(self):
        type_name = "入库" if self.record_type == 1 else "出库"
        return f"<StockRecord(id={self.id}, record_no='{self.record_no}', type={type_name}, quantity={self.quantity})>"

