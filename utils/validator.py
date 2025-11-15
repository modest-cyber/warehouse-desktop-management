# -*- coding: utf-8 -*-
"""
数据验证工具类
提供数据格式验证和业务规则验证方法
"""

import re
from typing import Optional, List, Tuple


class Validator:
    """数据验证工具类"""
    
    @staticmethod
    def validate_string(value: str, min_length: int = 0, max_length: int = None, 
                       field_name: str = '字段') -> Tuple[bool, str]:
        """
        验证字符串长度
        
        Args:
            value: 要验证的字符串值
            min_length: 最小长度
            max_length: 最大长度（None表示不限制）
            field_name: 字段名称，用于错误提示
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if value is None:
            return False, f"{field_name}不能为空"
        
        if not isinstance(value, str):
            return False, f"{field_name}必须是字符串类型"
        
        if len(value) < min_length:
            return False, f"{field_name}长度不能少于{min_length}个字符"
        
        if max_length is not None and len(value) > max_length:
            return False, f"{field_name}长度不能超过{max_length}个字符"
        
        return True, ""
    
    @staticmethod
    def validate_number(value, min_value: float = None, max_value: float = None,
                       field_name: str = '字段') -> Tuple[bool, str]:
        """
        验证数值范围
        
        Args:
            value: 要验证的数值
            min_value: 最小值（None表示不限制）
            max_value: 最大值（None表示不限制）
            field_name: 字段名称，用于错误提示
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if value is None:
            return False, f"{field_name}不能为空"
        
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return False, f"{field_name}必须是数字类型"
        
        if min_value is not None and num_value < min_value:
            return False, f"{field_name}不能小于{min_value}"
        
        if max_value is not None and num_value > max_value:
            return False, f"{field_name}不能大于{max_value}"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        验证邮箱格式
        
        Args:
            email: 要验证的邮箱地址
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not email:
            return True, ""  # 邮箱可以为空
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, ""
        else:
            return False, "邮箱格式不正确"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        验证电话号码格式
        
        Args:
            phone: 要验证的电话号码
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not phone:
            return True, ""  # 电话可以为空
        
        # 支持多种电话格式：固定电话、手机号
        pattern = r'^(\d{3,4}-?\d{7,8}|\d{11})$'
        if re.match(pattern, phone):
            return True, ""
        else:
            return False, "电话号码格式不正确"
    
    @staticmethod
    def validate_not_empty(value, field_name: str = '字段') -> Tuple[bool, str]:
        """
        验证非空
        
        Args:
            value: 要验证的值
            field_name: 字段名称，用于错误提示
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if value is None:
            return False, f"{field_name}不能为空"
        
        if isinstance(value, str) and value.strip() == '':
            return False, f"{field_name}不能为空"
        
        return True, ""
    
    @staticmethod
    def validate_unique_code(code: str, dao_instance, field_name: str = 'code',
                            exclude_id: int = None) -> Tuple[bool, str]:
        """
        验证编码唯一性（需要数据库查询）
        
        Args:
            code: 要验证的编码
            dao_instance: DAO实例，用于查询数据库
            field_name: 数据库字段名
            exclude_id: 排除的ID（用于更新时排除自己）
            
        Returns:
            Tuple[bool, str]: (是否唯一, 错误信息)
        """
        if not code:
            return True, ""  # 编码可以为空
        
        try:
            # 根据不同的DAO调用不同的查询方法
            if hasattr(dao_instance, 'get_by_code'):
                existing = dao_instance.get_by_code(code)
                if existing and (exclude_id is None or existing.id != exclude_id):
                    return False, f"编码{code}已存在"
            elif hasattr(dao_instance, 'get_by_' + field_name):
                method = getattr(dao_instance, 'get_by_' + field_name)
                existing = method(code)
                if existing and (exclude_id is None or existing.id != exclude_id):
                    return False, f"编码{code}已存在"
            
            return True, ""
        except Exception as e:
            # 查询出错时，为了不影响业务，返回True
            return True, ""
    
    @staticmethod
    def validate_batch(validations: List[Tuple[bool, str]]) -> Tuple[bool, List[str]]:
        """
        批量验证
        
        Args:
            validations: 验证结果列表，每个元素是(是否有效, 错误信息)的元组
            
        Returns:
            Tuple[bool, List[str]]: (是否全部有效, 错误信息列表)
        """
        errors = []
        for is_valid, error_msg in validations:
            if not is_valid:
                errors.append(error_msg)
        
        return len(errors) == 0, errors

