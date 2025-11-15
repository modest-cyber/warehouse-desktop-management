# -*- coding: utf-8 -*-
"""
用户管理Service
实现用户管理的业务逻辑处理
"""

from typing import List, Optional
from dao.user_dao import UserDAO
from model.user import User
from utils.validator import Validator
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class UserService:
    """用户管理Service类"""
    
    def __init__(self):
        """初始化Service"""
        self.dao = UserDAO()
        self.validator = Validator()
    
    def add_user(self, user: User) -> User:
        """
        添加用户
        
        Args:
            user: 用户对象
            
        Returns:
            User: 添加成功的用户对象
            
        Raises:
            ValueError: 数据验证失败时抛出异常
        """
        # 数据验证
        is_valid, errors = self.validate_user(user)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证username唯一性
        existing_user = self.dao.get_by_username(user.username)
        if existing_user:
            raise ValueError(f"用户名{user.username}已存在")
        
        # 验证username长度
        is_valid, error_msg = self.validator.validate_string(
            user.username, min_length=3, field_name="用户名"
        )
        if not is_valid:
            raise ValueError(error_msg)
        
        # 验证password长度
        is_valid, error_msg = self.validate_password(user.password)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 密码加密存储
        user.password = User.encrypt_password(user.password)
        
        # role默认为'admin'
        if not user.role:
            user.role = 'admin'
        
        # 插入数据库
        user.id = self.dao.insert(user)
        logger.info(f"添加用户成功: ID={user.id}, username={user.username}")
        return user
    
    def update_user(self, user: User) -> bool:
        """
        更新用户信息（不能修改密码）
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 是否更新成功
            
        Raises:
            ValueError: 数据验证失败时抛出异常
        """
        # 数据验证
        is_valid, errors = self.validate_user(user, check_password=False)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证username唯一性（排除当前用户）
        existing_user = self.dao.get_by_username(user.username)
        if existing_user and existing_user.id != user.id:
            raise ValueError(f"用户名{user.username}已存在")
        
        # 验证username长度
        is_valid, error_msg = self.validator.validate_string(
            user.username, min_length=3, field_name="用户名"
        )
        if not is_valid:
            raise ValueError(error_msg)
        
        # 更新数据库（不更新密码）
        result = self.dao.update(user)
        logger.info(f"更新用户信息成功: ID={user.id}")
        return result
    
    def delete_user(self, id: int, current_user_id: Optional[int] = None) -> bool:
        """
        删除用户
        
        Args:
            id: 用户ID
            current_user_id: 当前登录用户ID（用于检查不能删除自己）
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            Exception: 删除失败时抛出异常
        """
        # 检查是否为默认管理员
        user = self.dao.get_by_id(id)
        if user and user.username == 'admin':
            raise Exception("默认管理员不能删除")
        
        # 检查不能删除自己
        if current_user_id and id == current_user_id:
            raise Exception("不能删除自己")
        
        result = self.dao.delete(id)
        logger.info(f"删除用户成功: ID={id}")
        return result
    
    def get_user(self, id: int) -> Optional[User]:
        """
        获取用户信息
        
        Args:
            id: 用户ID
            
        Returns:
            User: 用户对象，如果不存在返回None
        """
        return self.dao.get_by_id(id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            User: 用户对象，如果不存在返回None
        """
        return self.dao.get_by_username(username)
    
    def get_all_users(self) -> List[User]:
        """
        获取所有用户
        
        Returns:
            list: 用户对象列表
        """
        return self.dao.get_all()
    
    def login(self, username: str, password: str) -> Optional[User]:
        """
        用户登录验证
        
        Args:
            username: 用户名
            password: 密码（明文）
            
        Returns:
            User: 用户对象（不包含密码），如果验证失败返回None
        """
        user = self.dao.verify_login(username, password)
        if user:
            # 返回用户信息，但不包含密码
            logger.info(f"用户登录成功: username={username}")
            return user
        else:
            logger.warning(f"用户登录失败: username={username}")
            return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码（明文）
            new_password: 新密码（明文）
            
        Returns:
            bool: 是否修改成功
            
        Raises:
            ValueError: 验证失败时抛出异常
            Exception: 业务规则检查失败时抛出异常
        """
        # 获取用户信息
        user = self.dao.get_by_id(user_id)
        if not user:
            raise Exception("用户不存在")
        
        # 验证旧密码
        if not User.verify_password(old_password, user.password):
            raise ValueError("旧密码不正确")
        
        # 验证新密码长度
        is_valid, error_msg = self.validate_password(new_password)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 加密新密码
        encrypted_password = User.encrypt_password(new_password)
        
        # 更新密码
        result = self.dao.update_password(user_id, encrypted_password)
        logger.info(f"修改密码成功: user_id={user_id}")
        return result
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """
        重置密码（管理员操作）
        
        Args:
            user_id: 用户ID
            new_password: 新密码（明文）
            
        Returns:
            bool: 是否重置成功
            
        Raises:
            ValueError: 验证失败时抛出异常
        """
        # 验证新密码长度
        is_valid, error_msg = self.validate_password(new_password)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 加密新密码
        encrypted_password = User.encrypt_password(new_password)
        
        # 更新密码
        result = self.dao.update_password(user_id, encrypted_password)
        logger.info(f"重置密码成功: user_id={user_id}")
        return result
    
    def validate_user(self, user: User, check_password: bool = True) -> tuple:
        """
        验证用户数据
        
        Args:
            user: 用户对象
            check_password: 是否检查密码
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证username不能为空
        is_valid, error_msg = self.validator.validate_not_empty(user.username, "用户名")
        if not is_valid:
            errors.append(error_msg)
        elif len(user.username) < 3:
            errors.append("用户名长度至少3位")
        
        # 验证password（如果需要）
        if check_password:
            is_valid, error_msg = self.validator.validate_not_empty(user.password, "密码")
            if not is_valid:
                errors.append(error_msg)
            elif len(user.password) < 6:
                errors.append("密码长度至少6位")
        
        # 验证status值
        if user.status not in [0, 1]:
            errors.append("状态值必须是0或1")
        
        return len(errors) == 0, errors
    
    def validate_password(self, password: str) -> tuple:
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not password:
            return False, "密码不能为空"
        
        if len(password) < 6:
            return False, "密码长度至少6位"
        
        return True, ""

