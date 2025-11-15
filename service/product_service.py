# -*- coding: utf-8 -*-
"""
货品信息Service
实现货品的业务逻辑处理
"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from dao.product_dao import ProductDAO
from dao.base_info_dao import BaseInfoDAO
from model.product import Product
from utils.validator import Validator
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class ProductService:
    """货品信息Service类"""
    
    def __init__(self):
        """初始化Service"""
        self.dao = ProductDAO()
        self.base_info_dao = BaseInfoDAO()
        self.validator = Validator()
    
    def add_product(self, product: Product) -> Product:
        """
        添加货品信息
        
        Args:
            product: 货品对象
            
        Returns:
            Product: 添加成功的货品对象
            
        Raises:
            ValueError: 数据验证失败时抛出异常
        """
        # 如果未提供product_code，自动生成
        if not product.product_code:
            product.product_code = self.generate_product_code()
        
        # 数据验证
        is_valid, errors = self.validate_product(product)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证编码唯一性
        is_unique, error_msg = self.validator.validate_unique_code(
            product.product_code, self.dao, 'product_code'
        )
        if not is_unique:
            raise ValueError(error_msg)
        
        # 插入数据库
        product.id = self.dao.insert(product)
        logger.info(f"添加货品信息成功: ID={product.id}, product_code={product.product_code}")
        return product
    
    def update_product(self, product: Product) -> bool:
        """
        更新货品信息
        
        Args:
            product: 货品对象
            
        Returns:
            bool: 是否更新成功
            
        Raises:
            ValueError: 数据验证失败时抛出异常
        """
        # 数据验证
        is_valid, errors = self.validate_product(product)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证编码唯一性（排除自己）
        if product.product_code:
            is_unique, error_msg = self.validator.validate_unique_code(
                product.product_code, self.dao, 'product_code', exclude_id=product.id
            )
            if not is_unique:
                raise ValueError(error_msg)
        
        # 更新数据库
        result = self.dao.update(product)
        logger.info(f"更新货品信息成功: ID={product.id}")
        return result
    
    def delete_product(self, id: int) -> bool:
        """
        删除货品信息
        
        Args:
            id: 货品ID
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            Exception: 删除失败时抛出异常
        """
        # 检查是否被引用
        if self.dao.check_reference(id):
            raise Exception("该货品已被库存表或出入库记录表引用，无法删除")
        
        result = self.dao.delete(id)
        logger.info(f"删除货品信息成功: ID={id}")
        return result
    
    def get_product(self, id: int) -> Optional[Product]:
        """
        获取货品信息
        
        Args:
            id: 货品ID
            
        Returns:
            Product: 货品对象，如果不存在返回None
        """
        return self.dao.get_by_id(id)
    
    def get_product_by_code(self, product_code: str) -> Optional[Product]:
        """
        根据编码获取货品
        
        Args:
            product_code: 货品编码
            
        Returns:
            Product: 货品对象，如果不存在返回None
        """
        return self.dao.get_by_code(product_code)
    
    def search_product(self, keyword: str) -> List[Product]:
        """
        搜索货品（按编码或名称）
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 货品对象列表
        """
        # 先按编码精确查询
        product = self.dao.get_by_code(keyword)
        if product:
            return [product]
        
        # 再按名称模糊查询
        return self.dao.search_by_name(keyword)
    
    def get_all_product(self) -> List[Product]:
        """
        获取所有货品
        
        Returns:
            list: 货品对象列表
        """
        return self.dao.get_all()
    
    def generate_product_code(self) -> str:
        """
        生成货品编码（格式：P+日期+序号）
        
        Returns:
            str: 生成的货品编码
        """
        date_str = datetime.now().strftime('%Y%m%d')
        prefix = f'P{date_str}'
        
        # 查询当天已有的最大序号（使用参数化查询）
        sql = "SELECT product_code FROM product WHERE product_code LIKE %s ORDER BY product_code DESC LIMIT 1"
        params = (f'{prefix}%',)
        result = self.dao.fetch_one(sql, params)
        
        if result:
            last_code = result['product_code']
            last_num = int(last_code[-4:])  # 取最后4位作为序号
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def validate_product(self, product: Product) -> tuple:
        """
        验证货品数据
        
        Args:
            product: 货品对象
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证product_name不能为空
        is_valid, error_msg = self.validator.validate_not_empty(product.product_name, "货品名称")
        if not is_valid:
            errors.append(error_msg)
        
        # 验证product_code不能为空
        is_valid, error_msg = self.validator.validate_not_empty(product.product_code, "货品编码")
        if not is_valid:
            errors.append(error_msg)
        
        # 验证category_id和unit_id必须从base_info表中选择
        if product.category_id:
            category = self.base_info_dao.get_by_id(product.category_id)
            if not category or category.info_type != 'category':
                errors.append("类别ID无效或不是类别类型")
            elif category.status == 0:
                errors.append("所选类别已禁用")
        
        if product.unit_id:
            unit = self.base_info_dao.get_by_id(product.unit_id)
            if not unit or unit.info_type != 'unit':
                errors.append("单位ID无效或不是单位类型")
            elif unit.status == 0:
                errors.append("所选单位已禁用")
        
        # 验证price如果存在必须大于等于0
        if product.price is not None:
            is_valid, error_msg = self.validator.validate_number(
                float(product.price), min_value=0, field_name="单价"
            )
            if not is_valid:
                errors.append(error_msg)
        
        # 验证min_stock不能大于max_stock
        if product.min_stock > product.max_stock:
            errors.append("最低库存不能大于最高库存")
        
        # 验证status值
        if product.status not in [0, 1]:
            errors.append("状态值必须是0或1")
        
        return len(errors) == 0, errors

