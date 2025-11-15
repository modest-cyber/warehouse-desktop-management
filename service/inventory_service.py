# -*- coding: utf-8 -*-
"""
库存管理Service
实现库存查询和管理的业务逻辑
"""

from typing import List, Optional, Dict, Any
from dao.inventory_dao import InventoryDAO
from dao.product_dao import ProductDAO
from model.inventory import Inventory
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class InventoryService:
    """库存管理Service类"""
    
    def __init__(self):
        """初始化Service"""
        self.dao = InventoryDAO()
        self.product_dao = ProductDAO()
    
    def get_inventory(self, warehouse_id: int, product_id: int) -> Optional[Inventory]:
        """
        获取指定仓库和货品的库存
        
        Args:
            warehouse_id: 仓库ID
            product_id: 货品ID
            
        Returns:
            Inventory: 库存对象，如果不存在返回None
        """
        return self.dao.get_by_warehouse_product(warehouse_id, product_id)
    
    def get_inventory_by_warehouse(self, warehouse_id: int) -> List[Inventory]:
        """
        获取指定仓库的所有库存
        
        Args:
            warehouse_id: 仓库ID
            
        Returns:
            list: 库存对象列表
        """
        return self.dao.get_by_warehouse(warehouse_id)
    
    def get_inventory_by_product(self, product_id: int) -> List[Inventory]:
        """
        获取指定货品的所有库存
        
        Args:
            product_id: 货品ID
            
        Returns:
            list: 库存对象列表
        """
        return self.dao.get_by_product(product_id)
    
    def get_all_inventory(self) -> List[Inventory]:
        """
        获取所有库存
        
        Returns:
            list: 库存对象列表
        """
        return self.dao.get_all()
    
    def check_stock_warning(self, warehouse_id: int, product_id: int) -> Dict[str, Any]:
        """
        检查库存预警
        
        Args:
            warehouse_id: 仓库ID
            product_id: 货品ID
            
        Returns:
            dict: 预警信息，包含：
                - has_warning: 是否有预警
                - warning_type: 预警类型（'low'低库存，'over'超库存，None无预警）
                - current_quantity: 当前库存
                - min_stock: 最低库存
                - max_stock: 最高库存
        """
        inventory = self.dao.get_by_warehouse_product(warehouse_id, product_id)
        product = self.product_dao.get_by_id(product_id)
        
        if not inventory:
            return {
                'has_warning': False,
                'warning_type': None,
                'current_quantity': 0,
                'min_stock': product.min_stock if product else 0,
                'max_stock': product.max_stock if product else 0
            }
        
        current_quantity = inventory.quantity
        min_stock = product.min_stock if product else 0
        max_stock = product.max_stock if product else 0
        
        warning_type = None
        has_warning = False
        
        if current_quantity < min_stock:
            warning_type = 'low'
            has_warning = True
        elif max_stock > 0 and current_quantity > max_stock:
            warning_type = 'over'
            has_warning = True
        
        return {
            'has_warning': has_warning,
            'warning_type': warning_type,
            'current_quantity': current_quantity,
            'min_stock': min_stock,
            'max_stock': max_stock
        }
    
    def get_stock_warnings(self) -> List[Dict[str, Any]]:
        """
        获取所有库存预警信息
        
        Returns:
            list: 预警信息列表，每个元素包含库存信息和预警类型
        """
        all_inventory = self.dao.get_all()
        warnings = []
        
        for inventory in all_inventory:
            warning_info = self.check_stock_warning(inventory.warehouse_id, inventory.product_id)
            if warning_info['has_warning']:
                warning_info['inventory'] = inventory
                warnings.append(warning_info)
        
        return warnings
    
    def get_low_stock(self) -> List[Dict[str, Any]]:
        """
        获取低库存列表（低于最低库存）
        
        Returns:
            list: 低库存信息列表
        """
        all_inventory = self.dao.get_all()
        low_stocks = []
        
        for inventory in all_inventory:
            product = self.product_dao.get_by_id(inventory.product_id)
            if product and inventory.quantity < product.min_stock:
                low_stocks.append({
                    'inventory': inventory,
                    'product': product,
                    'current_quantity': inventory.quantity,
                    'min_stock': product.min_stock,
                    'difference': inventory.quantity - product.min_stock
                })
        
        return low_stocks
    
    def get_over_stock(self) -> List[Dict[str, Any]]:
        """
        获取超库存列表（高于最高库存）
        
        Returns:
            list: 超库存信息列表
        """
        all_inventory = self.dao.get_all()
        over_stocks = []
        
        for inventory in all_inventory:
            product = self.product_dao.get_by_id(inventory.product_id)
            if product and product.max_stock > 0 and inventory.quantity > product.max_stock:
                over_stocks.append({
                    'inventory': inventory,
                    'product': product,
                    'current_quantity': inventory.quantity,
                    'max_stock': product.max_stock,
                    'difference': inventory.quantity - product.max_stock
                })
        
        return over_stocks

