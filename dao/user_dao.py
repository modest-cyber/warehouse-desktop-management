# -*- coding: utf-8 -*-
"""
用户DAO
实现user表的所有数据库操作
"""

from typing import List, Optional
from dao.base_dao import BaseDAO
from model.user import User
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class UserDAO(BaseDAO):
    """用户DAO类"""
    
    def insert(self, user: User) -> int:
        """
        插入用户信息
        
        Args:
            user: 用户对象
            
        Returns:
            int: 插入记录的ID
        """
        sql = """
            INSERT INTO user (username, password, real_name, role, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            user.username,
            user.password,
            user.real_name,
            user.role,
            user.status
        )
        
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                connection.commit()
                user.id = cursor.lastrowid
                logger.info(f"插入用户信息成功: ID={user.id}, username={user.username}")
                return user.id
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"插入用户信息失败: {str(e)}")
            raise Exception(f"插入用户信息失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def update(self, user: User) -> bool:
        """
        更新用户信息（不更新密码）
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 是否更新成功
        """
        sql = """
            UPDATE user 
            SET username=%s, real_name=%s, role=%s, status=%s
            WHERE id=%s
        """
        params = (
            user.username,
            user.real_name,
            user.role,
            user.status,
            user.id
        )
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"更新用户信息成功: ID={user.id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"更新用户信息失败: {str(e)}")
            raise
    
    def update_password(self, id: int, new_password: str) -> bool:
        """
        更新密码
        
        Args:
            id: 用户ID
            new_password: 新密码（已加密）
            
        Returns:
            bool: 是否更新成功
        """
        sql = "UPDATE user SET password=%s WHERE id=%s"
        params = (new_password, id)
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"更新用户密码成功: ID={id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"更新用户密码失败: {str(e)}")
            raise
    
    def delete(self, id: int) -> bool:
        """
        删除用户信息（需要检查是否为默认管理员）
        
        Args:
            id: 用户ID
            
        Returns:
            bool: 是否删除成功
        """
        # 先检查是否为默认管理员
        user = self.get_by_id(id)
        if user and user.username == 'admin':
            raise Exception("默认管理员不能删除")
        
        sql = "DELETE FROM user WHERE id=%s"
        params = (id,)
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"删除用户信息成功: ID={id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"删除用户信息失败: {str(e)}")
            raise
    
    def get_by_id(self, id: int) -> Optional[User]:
        """
        根据ID查询
        
        Args:
            id: 用户ID
            
        Returns:
            User: 用户对象，如果不存在返回None
        """
        sql = "SELECT * FROM user WHERE id=%s"
        params = (id,)
        
        result = self.fetch_one(sql, params)
        if result:
            return User.from_dict(result)
        return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名查询
        
        Args:
            username: 用户名
            
        Returns:
            User: 用户对象，如果不存在返回None
        """
        sql = "SELECT * FROM user WHERE username=%s"
        params = (username,)
        
        result = self.fetch_one(sql, params)
        if result:
            return User.from_dict(result)
        return None
    
    def get_all(self) -> List[User]:
        """
        查询所有用户
        
        Returns:
            list: 用户对象列表
        """
        sql = "SELECT * FROM user ORDER BY id"
        results = self.fetch_all(sql)
        return [User.from_dict(row) for row in results]
    
    def get_active_users(self) -> List[User]:
        """
        查询所有启用的用户
        
        Returns:
            list: 用户对象列表
        """
        sql = "SELECT * FROM user WHERE status=1 ORDER BY id"
        results = self.fetch_all(sql)
        return [User.from_dict(row) for row in results]
    
    def verify_login(self, username: str, password: str) -> Optional[User]:
        """
        验证用户登录
        
        Args:
            username: 用户名
            password: 明文密码
            
        Returns:
            User: 用户对象，如果验证失败返回None
        """
        user = self.get_by_username(username)
        if not user:
            return None
        
        # 验证密码
        if not User.verify_password(password, user.password):
            return None
        
        # 验证用户状态
        if not user.is_active():
            return None
        
        return user

