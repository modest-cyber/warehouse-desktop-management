# -*- coding: utf-8 -*-
"""
用户模型
封装user表的数据结构
"""

import hashlib
from datetime import datetime
from typing import Optional, Dict, Any


class User:
    """用户模型类"""
    
    def __init__(self, id: Optional[int] = None, username: str = None,
                 password: str = None, real_name: Optional[str] = None,
                 role: str = 'admin', status: int = 1,
                 create_time: Optional[datetime] = None,
                 update_time: Optional[datetime] = None, **kwargs):
        """
        初始化用户对象
        
        Args:
            id: 主键ID
            username: 用户名
            password: 密码（加密存储）
            real_name: 真实姓名
            role: 角色
            status: 状态（1-启用，0-禁用）
            create_time: 创建时间
            update_time: 更新时间
        """
        self.id = id
        self.username = username
        self.password = password
        self.real_name = real_name
        self.role = role
        self.status = status
        self.create_time = create_time
        self.update_time = update_time
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        从字典创建对象
        
        Args:
            data: 字典数据
            
        Returns:
            User: 用户对象
        """
        return cls(**data)
    
    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """
        转换为字典格式（默认不包含密码）
        
        Args:
            include_password: 是否包含密码
            
        Returns:
            dict: 字典数据
        """
        result = {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'role': self.role,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }
        
        if include_password:
            result['password'] = self.password
        
        return result
    
    def validate(self) -> tuple:
        """
        数据验证方法
        
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        if not self.username:
            errors.append("用户名不能为空")
        elif len(self.username) < 3:
            errors.append("用户名长度至少3位")
        
        if not self.password:
            errors.append("密码不能为空")
        elif len(self.password) < 6:
            errors.append("密码长度至少6位")
        
        if self.status not in [0, 1]:
            errors.append("状态值必须是0或1")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def encrypt_password(password: str) -> str:
        """
        加密密码（使用MD5）
        
        Args:
            password: 明文密码
            
        Returns:
            str: 加密后的密码
        """
        return hashlib.md5(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            hashed_password: 加密后的密码
            
        Returns:
            bool: 密码是否正确
        """
        return User.encrypt_password(password) == hashed_password
    
    def is_active(self) -> bool:
        """
        判断用户是否启用
        
        Returns:
            bool: 是否启用
        """
        return self.status == 1
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}', status={self.status})>"

