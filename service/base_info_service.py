# -*- coding: utf-8 -*-
"""
基础信息Service
实现基础信息的业务逻辑处理
"""

from typing import List, Optional
from dao.base_info_dao import BaseInfoDAO
from model.base_info import BaseInfo
from utils.validator import Validator
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class BaseInfoService:
    """基础信息Service类"""
    
    def __init__(self):
        """初始化Service"""
        self.dao = BaseInfoDAO()
        self.validator = Validator()
    
    def add_base_info(self, base_info: BaseInfo) -> BaseInfo:
        """
        添加基础信息
        
        Args:
            base_info: 基础信息对象
            
        Returns:
            BaseInfo: 添加成功的基础信息对象
            
        Raises:
            ValueError: 数据验证失败时抛出异常
        """
        # 数据验证
        is_valid, errors = self.validate_base_info(base_info)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证编码唯一性（如果提供）
        if base_info.info_code:
            is_unique, error_msg = self.validator.validate_unique_code(
                base_info.info_code, self.dao, 'info_code'
            )
            if not is_unique:
                raise ValueError(error_msg)
        
        # 插入数据库
        base_info.id = self.dao.insert(base_info)
        logger.info(f"添加基础信息成功: ID={base_info.id}, info_name={base_info.info_name}")
        return base_info
    
    def update_base_info(self, base_info: BaseInfo) -> bool:
        """
        更新基础信息
        
        Args:
            base_info: 基础信息对象
            
        Returns:
            bool: 是否更新成功
            
        Raises:
            ValueError: 数据验证失败时抛出异常
        """
        # 数据验证
        is_valid, errors = self.validate_base_info(base_info)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证编码唯一性（如果提供，排除自己）
        if base_info.info_code:
            is_unique, error_msg = self.validator.validate_unique_code(
                base_info.info_code, self.dao, 'info_code', exclude_id=base_info.id
            )
            if not is_unique:
                raise ValueError(error_msg)
        
        # 更新数据库
        result = self.dao.update(base_info)
        logger.info(f"更新基础信息成功: ID={base_info.id}")
        return result
    
    def delete_base_info(self, id: int) -> bool:
        """
        删除基础信息
        
        Args:
            id: 基础信息ID
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            Exception: 删除失败时抛出异常
        """
        # 检查是否被引用
        if self.dao.check_reference(id):
            raise Exception("该基础信息已被其他表引用，无法删除")
        
        result = self.dao.delete(id)
        logger.info(f"删除基础信息成功: ID={id}")
        return result
    
    def get_base_info(self, id: int) -> Optional[BaseInfo]:
        """
        获取基础信息
        
        Args:
            id: 基础信息ID
            
        Returns:
            BaseInfo: 基础信息对象，如果不存在返回None
        """
        return self.dao.get_by_id(id)
    
    def get_base_info_by_type(self, info_type: str) -> List[BaseInfo]:
        """
        根据类型获取基础信息列表
        
        Args:
            info_type: 信息类型
            
        Returns:
            list: 基础信息对象列表
        """
        return self.dao.get_by_type(info_type)
    
    def get_all_base_info(self) -> List[BaseInfo]:
        """
        获取所有基础信息
        
        Returns:
            list: 基础信息对象列表
        """
        return self.dao.get_all()
    
    def validate_base_info(self, base_info: BaseInfo) -> tuple:
        """
        验证基础信息数据
        
        Args:
            base_info: 基础信息对象
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证info_name不能为空
        is_valid, error_msg = self.validator.validate_not_empty(base_info.info_name, "信息名称")
        if not is_valid:
            errors.append(error_msg)
        
        # 验证info_type不能为空
        is_valid, error_msg = self.validator.validate_not_empty(base_info.info_type, "信息类型")
        if not is_valid:
            errors.append(error_msg)
        
        # 验证status值
        if base_info.status not in [0, 1]:
            errors.append("状态值必须是0或1")
        
        return len(errors) == 0, errors

