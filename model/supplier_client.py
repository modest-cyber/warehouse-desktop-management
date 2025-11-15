# -*- coding: utf-8 -*-
"""
供应商/客户信息模型
封装supplier_client表的数据结构
"""

from datetime import datetime
from typing import Optional, Dict, Any


class SupplierClient:
    """供应商/客户信息模型类"""
    
    def __init__(self, id: Optional[int] = None, code: str = None,
                 name: str = None, type: int = None,
                 contact_person: Optional[str] = None, phone: Optional[str] = None,
                 email: Optional[str] = None, address: Optional[str] = None,
                 description: Optional[str] = None, status: int = 1,
                 create_time: Optional[datetime] = None,
                 update_time: Optional[datetime] = None, **kwargs):
        """
        初始化供应商/客户对象
        
        Args:
            id: 主键ID
            code: 编码
            name: 名称
            type: 类型（1-供应商，2-客户）
            contact_person: 联系人
            phone: 联系电话
            email: 邮箱
            address: 地址
            description: 描述
            status: 状态（1-启用，0-禁用）
            create_time: 创建时间
            update_time: 更新时间
        """
        self.id = id
        self.code = code
        self.name = name
        self.type = type
        self.contact_person = contact_person
        self.phone = phone
        self.email = email
        self.address = address
        self.description = description
        self.status = status
        self.create_time = create_time
        self.update_time = update_time
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupplierClient':
        """
        从字典创建对象
        
        Args:
            data: 字典数据
            
        Returns:
            SupplierClient: 供应商/客户对象
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
            'code': self.code,
            'name': self.name,
            'type': self.type,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
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
        
        if not self.name:
            errors.append("名称不能为空")
        
        if not self.code:
            errors.append("编码不能为空")
        
        if self.type not in [1, 2]:
            errors.append("类型值必须是1（供应商）或2（客户）")
        
        if self.status not in [0, 1]:
            errors.append("状态值必须是0或1")
        
        return len(errors) == 0, errors
    
    def is_supplier(self) -> bool:
        """
        判断是否为供应商
        
        Returns:
            bool: 是否为供应商
        """
        return self.type == 1
    
    def is_client(self) -> bool:
        """
        判断是否为客户
        
        Returns:
            bool: 是否为客户
        """
        return self.type == 2
    
    def __repr__(self):
        type_name = "供应商" if self.type == 1 else "客户"
        return f"<SupplierClient(id={self.id}, code='{self.code}', name='{self.name}', type={type_name})>"

