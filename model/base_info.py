# -*- coding: utf-8 -*-
"""
基础信息模型
封装base_info表的数据结构
"""

from datetime import datetime
from typing import Optional, Dict, Any


class BaseInfo:
    """基础信息模型类"""
    
    def __init__(self, id: Optional[int] = None, info_type: str = None,
                 info_name: str = None, info_code: Optional[str] = None,
                 description: Optional[str] = None, status: int = 1,
                 create_time: Optional[datetime] = None,
                 update_time: Optional[datetime] = None, **kwargs):
        """
        初始化基础信息对象
        
        Args:
            id: 主键ID
            info_type: 信息类型
            info_name: 信息名称
            info_code: 信息编码
            description: 描述
            status: 状态（1-启用，0-禁用）
            create_time: 创建时间
            update_time: 更新时间
        """
        self.id = id
        self.info_type = info_type
        self.info_name = info_name
        self.info_code = info_code
        self.description = description
        self.status = status
        self.create_time = create_time
        self.update_time = update_time
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseInfo':
        """
        从字典创建对象
        
        Args:
            data: 字典数据
            
        Returns:
            BaseInfo: 基础信息对象
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
            'info_type': self.info_type,
            'info_name': self.info_name,
            'info_code': self.info_code,
            'description': self.description,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }
    
    def __repr__(self):
        return f"<BaseInfo(id={self.id}, info_type='{self.info_type}', info_name='{self.info_name}')>"

