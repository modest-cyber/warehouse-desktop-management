# -*- coding: utf-8 -*-
"""
入库/出库管理Service
实现入库/出库的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from dao.stock_dao import StockDAO
from dao.inventory_dao import InventoryDAO
from dao.warehouse_dao import WarehouseDAO
from dao.product_dao import ProductDAO
from model.stock_record import StockRecord
from utils.validator import Validator
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class StockService:
    """入库/出库管理Service类"""
    
    def __init__(self):
        """初始化Service"""
        self.dao = StockDAO()
        self.inventory_dao = InventoryDAO()
        self.warehouse_dao = WarehouseDAO()
        self.product_dao = ProductDAO()
        self.validator = Validator()
    
    def add_in_stock(self, stock_record: StockRecord) -> StockRecord:
        """
        添加入库记录
        
        Args:
            stock_record: 入库记录对象
            
        Returns:
            StockRecord: 添加成功的入库记录对象
            
        Raises:
            ValueError: 数据验证失败时抛出异常
            Exception: 业务规则检查失败时抛出异常
        """
        # 设置记录类型为入库
        stock_record.record_type = 1
        
        # 如果未提供单据号，自动生成
        if not stock_record.record_no:
            stock_record.record_no = self.generate_record_no(1)
        
        # 数据验证
        is_valid, errors = self.validate_stock_record(stock_record)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证仓库状态必须为启用
        warehouse = self.warehouse_dao.get_by_id(stock_record.warehouse_id)
        if not warehouse:
            raise Exception("仓库不存在")
        if warehouse.status != 1:
            raise Exception("仓库已禁用，无法进行入库操作")
        
        # 验证货品状态必须为启用
        product = self.product_dao.get_by_id(stock_record.product_id)
        if not product:
            raise Exception("货品不存在")
        if product.status != 1:
            raise Exception("货品已禁用，无法进行入库操作")
        
        # 自动计算总金额
        stock_record.calculate_total_amount()
        
        # 使用事务同时插入记录和更新库存
        connection = None
        try:
            connection = self.dao.db_connection.get_connection()
            with connection.cursor() as cursor:
                # 插入出入库记录
                sql_record = """
                    INSERT INTO stock_record (record_no, record_type, warehouse_id, product_id, 
                                            quantity, unit_price, total_amount, supplier_client_id, 
                                            operator, record_date, remark)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params_record = (
                    stock_record.record_no,
                    stock_record.record_type,
                    stock_record.warehouse_id,
                    stock_record.product_id,
                    stock_record.quantity,
                    stock_record.unit_price,
                    stock_record.total_amount,
                    stock_record.supplier_client_id,
                    stock_record.operator,
                    stock_record.record_date,
                    stock_record.remark
                )
                cursor.execute(sql_record, params_record)
                stock_record.id = cursor.lastrowid
                
                # 更新库存
                self._update_inventory_in_transaction(cursor, stock_record, True)
                
                connection.commit()
                logger.info(f"添加入库记录成功: ID={stock_record.id}, record_no={stock_record.record_no}")
                return stock_record
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"添加入库记录失败: {str(e)}")
            raise
        finally:
            if connection:
                self.dao.db_connection.close_connection(connection)
    
    def add_out_stock(self, stock_record: StockRecord) -> StockRecord:
        """
        添加出库记录
        
        Args:
            stock_record: 出库记录对象
            
        Returns:
            StockRecord: 添加成功的出库记录对象
            
        Raises:
            ValueError: 数据验证失败时抛出异常
            Exception: 业务规则检查失败时抛出异常
        """
        # 设置记录类型为出库
        stock_record.record_type = 2
        
        # 如果未提供单据号，自动生成
        if not stock_record.record_no:
            stock_record.record_no = self.generate_record_no(2)
        
        # 数据验证
        is_valid, errors = self.validate_stock_record(stock_record)
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        # 验证仓库状态必须为启用
        warehouse = self.warehouse_dao.get_by_id(stock_record.warehouse_id)
        if not warehouse:
            raise Exception("仓库不存在")
        if warehouse.status != 1:
            raise Exception("仓库已禁用，无法进行出库操作")
        
        # 验证货品状态必须为启用
        product = self.product_dao.get_by_id(stock_record.product_id)
        if not product:
            raise Exception("货品不存在")
        if product.status != 1:
            raise Exception("货品已禁用，无法进行出库操作")
        
        # 验证库存数量必须充足
        if not self.inventory_dao.check_stock(
            stock_record.warehouse_id, stock_record.product_id, stock_record.quantity
        ):
            inventory = self.inventory_dao.get_by_warehouse_product(
                stock_record.warehouse_id, stock_record.product_id
            )
            current_stock = inventory.quantity if inventory else 0
            raise Exception(f"库存不足，当前库存：{current_stock}，需要：{stock_record.quantity}")
        
        # 自动计算总金额
        stock_record.calculate_total_amount()
        
        # 使用事务同时插入记录和更新库存
        connection = None
        try:
            connection = self.dao.db_connection.get_connection()
            with connection.cursor() as cursor:
                # 插入出入库记录
                sql_record = """
                    INSERT INTO stock_record (record_no, record_type, warehouse_id, product_id, 
                                            quantity, unit_price, total_amount, supplier_client_id, 
                                            operator, record_date, remark)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params_record = (
                    stock_record.record_no,
                    stock_record.record_type,
                    stock_record.warehouse_id,
                    stock_record.product_id,
                    stock_record.quantity,
                    stock_record.unit_price,
                    stock_record.total_amount,
                    stock_record.supplier_client_id,
                    stock_record.operator,
                    stock_record.record_date,
                    stock_record.remark
                )
                cursor.execute(sql_record, params_record)
                stock_record.id = cursor.lastrowid
                
                # 更新库存（减少）
                self._update_inventory_in_transaction(cursor, stock_record, False)
                
                connection.commit()
                logger.info(f"添加出库记录成功: ID={stock_record.id}, record_no={stock_record.record_no}")
                return stock_record
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"添加出库记录失败: {str(e)}")
            raise
        finally:
            if connection:
                self.dao.db_connection.close_connection(connection)
    
    def _update_inventory_in_transaction(self, cursor, stock_record: StockRecord, is_in: bool):
        """
        在事务中更新库存（内部方法）
        
        Args:
            cursor: 数据库游标
            stock_record: 出入库记录对象
            is_in: 是否为入库
        """
        warehouse_id = stock_record.warehouse_id
        product_id = stock_record.product_id
        quantity = stock_record.quantity
        record_date = stock_record.record_date
        
        # 查询是否存在库存记录
        sql_check = "SELECT id, quantity FROM inventory WHERE warehouse_id=%s AND product_id=%s"
        cursor.execute(sql_check, (warehouse_id, product_id))
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            if is_in:
                new_quantity = existing['quantity'] + quantity
                sql_update = """
                    UPDATE inventory 
                    SET quantity=%s, last_in_date=%s 
                    WHERE warehouse_id=%s AND product_id=%s
                """
                cursor.execute(sql_update, (new_quantity, record_date, warehouse_id, product_id))
            else:
                new_quantity = existing['quantity'] - quantity
                if new_quantity < 0:
                    raise Exception(f"库存不足，当前库存：{existing['quantity']}，需要：{quantity}")
                sql_update = """
                    UPDATE inventory 
                    SET quantity=%s, last_out_date=%s 
                    WHERE warehouse_id=%s AND product_id=%s
                """
                cursor.execute(sql_update, (new_quantity, record_date, warehouse_id, product_id))
        else:
            # 创建新记录（只允许入库时创建）
            if not is_in:
                raise Exception("库存不存在，无法出库")
            
            new_quantity = quantity
            sql_insert = """
                INSERT INTO inventory (warehouse_id, product_id, quantity, last_in_date)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (warehouse_id, product_id, new_quantity, record_date))
    
    def get_stock_record(self, id: int) -> Optional[StockRecord]:
        """
        获取出入库记录
        
        Args:
            id: 记录ID
            
        Returns:
            StockRecord: 出入库记录对象，如果不存在返回None
        """
        return self.dao.get_by_id(id)
    
    def get_stock_record_by_no(self, record_no: str) -> Optional[StockRecord]:
        """
        根据单据号获取
        
        Args:
            record_no: 单据号
            
        Returns:
            StockRecord: 出入库记录对象，如果不存在返回None
        """
        return self.dao.get_by_record_no(record_no)
    
    def search_stock_records(self, conditions: Dict[str, Any]) -> List[StockRecord]:
        """
        根据条件搜索出入库记录
        
        Args:
            conditions: 查询条件字典，可包含：
                - warehouse_id: 仓库ID
                - product_id: 货品ID
                - record_type: 记录类型
                - start_date: 开始日期
                - end_date: 结束日期
                - record_no: 单据号（模糊查询）
                - operator: 操作人（模糊查询）
            
        Returns:
            list: 出入库记录对象列表
        """
        sql = "SELECT * FROM stock_record WHERE 1=1"
        params = []
        
        if conditions.get('warehouse_id'):
            sql += " AND warehouse_id=%s"
            params.append(conditions['warehouse_id'])
        
        if conditions.get('product_id'):
            sql += " AND product_id=%s"
            params.append(conditions['product_id'])
        
        if conditions.get('record_type'):
            sql += " AND record_type=%s"
            params.append(conditions['record_type'])
        
        if conditions.get('start_date'):
            sql += " AND record_date >= %s"
            params.append(conditions['start_date'])
        
        if conditions.get('end_date'):
            sql += " AND record_date <= %s"
            params.append(conditions['end_date'])
        
        if conditions.get('record_no'):
            sql += " AND record_no LIKE %s"
            params.append(f"%{conditions['record_no']}%")
        
        if conditions.get('operator'):
            sql += " AND operator LIKE %s"
            params.append(f"%{conditions['operator']}%")
        
        sql += " ORDER BY record_date DESC, id DESC"
        
        results = self.dao.fetch_all(sql, tuple(params) if params else None)
        return [StockRecord.from_dict(row) for row in results]
    
    def get_statistics(self, conditions: Dict[str, Any]) -> dict:
        """
        统计出入库数据
        
        Args:
            conditions: 查询条件字典
            
        Returns:
            dict: 统计结果
        """
        return self.dao.get_statistics(
            conditions.get('warehouse_id'),
            conditions.get('product_id'),
            conditions.get('start_date'),
            conditions.get('end_date')
        )
    
    def generate_record_no(self, record_type: int) -> str:
        """
        生成单据号
        
        Args:
            record_type: 记录类型（1-入库，2-出库）
            
        Returns:
            str: 生成的单据号
        """
        date_str = datetime.now().strftime('%Y%m%d')
        
        if record_type == 1:
            prefix = f'RK{date_str}'
        elif record_type == 2:
            prefix = f'CK{date_str}'
        else:
            prefix = f'SR{date_str}'
        
        # 查询当天已有的最大序号
        sql = "SELECT record_no FROM stock_record WHERE record_no LIKE %s ORDER BY record_no DESC LIMIT 1"
        params = (f'{prefix}%',)
        result = self.dao.fetch_one(sql, params)
        
        if result:
            last_code = result['record_no']
            last_num = int(last_code[-4:])  # 取最后4位作为序号
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def calculate_total_amount(self, quantity: int, unit_price: Optional[Decimal]) -> Decimal:
        """
        计算总金额
        
        Args:
            quantity: 数量
            unit_price: 单价
            
        Returns:
            Decimal: 总金额
        """
        if quantity and unit_price:
            return Decimal(str(quantity)) * unit_price
        return Decimal('0')
    
    def validate_stock_record(self, stock_record: StockRecord) -> tuple:
        """
        验证出入库记录数据
        
        Args:
            stock_record: 出入库记录对象
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证record_no不能为空
        is_valid, error_msg = self.validator.validate_not_empty(stock_record.record_no, "单据号")
        if not is_valid:
            errors.append(error_msg)
        
        # 验证record_type
        if stock_record.record_type not in [1, 2]:
            errors.append("记录类型必须是1（入库）或2（出库）")
        
        # 验证warehouse_id不能为空
        if not stock_record.warehouse_id:
            errors.append("仓库ID不能为空")
        
        # 验证product_id不能为空
        if not stock_record.product_id:
            errors.append("货品ID不能为空")
        
        # 验证数量必须大于0
        if not stock_record.quantity or stock_record.quantity <= 0:
            errors.append("数量必须大于0")
        
        # 验证单价如果存在必须大于等于0
        if stock_record.unit_price is not None:
            is_valid, error_msg = self.validator.validate_number(
                float(stock_record.unit_price), min_value=0, field_name="单价"
            )
            if not is_valid:
                errors.append(error_msg)
        
        # 验证record_date不能为空且不能晚于当前日期
        if not stock_record.record_date:
            errors.append("操作日期不能为空")
        elif stock_record.record_date > datetime.now():
            errors.append("操作日期不能晚于当前日期")
        
        return len(errors) == 0, errors

