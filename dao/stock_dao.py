# -*- coding: utf-8 -*-
"""
入库/出库记录DAO
实现stock_record表的所有数据库操作
"""

from typing import List, Optional
from datetime import datetime
from dao.base_dao import BaseDAO
from model.stock_record import StockRecord
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class StockDAO(BaseDAO):
    """入库/出库记录DAO类"""
    
    def insert(self, stock_record: StockRecord) -> int:
        """
        插入出入库记录
        
        Args:
            stock_record: 出入库记录对象
            
        Returns:
            int: 插入记录的ID
        """
        sql = """
            INSERT INTO stock_record (record_no, record_type, warehouse_id, product_id, 
                                    quantity, unit_price, total_amount, supplier_client_id, 
                                    operator, record_date, remark)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
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
        
        connection = None
        try:
            connection = self.db_connection.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                connection.commit()
                stock_record.id = cursor.lastrowid
                logger.info(f"插入出入库记录成功: ID={stock_record.id}, record_no={stock_record.record_no}")
                return stock_record.id
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"插入出入库记录失败: {str(e)}")
            raise Exception(f"插入出入库记录失败: {str(e)}")
        finally:
            if connection:
                self.db_connection.close_connection(connection)
    
    def update(self, stock_record: StockRecord) -> bool:
        """
        更新出入库记录（一般不允许更新）
        
        Args:
            stock_record: 出入库记录对象
            
        Returns:
            bool: 是否更新成功
        """
        sql = """
            UPDATE stock_record 
            SET record_type=%s, warehouse_id=%s, product_id=%s, quantity=%s, 
                unit_price=%s, total_amount=%s, supplier_client_id=%s, 
                operator=%s, record_date=%s, remark=%s
            WHERE id=%s
        """
        params = (
            stock_record.record_type,
            stock_record.warehouse_id,
            stock_record.product_id,
            stock_record.quantity,
            stock_record.unit_price,
            stock_record.total_amount,
            stock_record.supplier_client_id,
            stock_record.operator,
            stock_record.record_date,
            stock_record.remark,
            stock_record.id
        )
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"更新出入库记录成功: ID={stock_record.id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"更新出入库记录失败: {str(e)}")
            raise
    
    def delete(self, id: int) -> bool:
        """
        删除出入库记录（一般不允许删除）
        
        Args:
            id: 记录ID
            
        Returns:
            bool: 是否删除成功
        """
        sql = "DELETE FROM stock_record WHERE id=%s"
        params = (id,)
        
        try:
            affected_rows = self.execute_update(sql, params)
            logger.info(f"删除出入库记录成功: ID={id}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"删除出入库记录失败: {str(e)}")
            raise
    
    def get_by_id(self, id: int) -> Optional[StockRecord]:
        """
        根据ID查询
        
        Args:
            id: 记录ID
            
        Returns:
            StockRecord: 出入库记录对象，如果不存在返回None
        """
        sql = "SELECT * FROM stock_record WHERE id=%s"
        params = (id,)
        
        result = self.fetch_one(sql, params)
        if result:
            return StockRecord.from_dict(result)
        return None
    
    def get_by_record_no(self, record_no: str) -> Optional[StockRecord]:
        """
        根据单据号查询
        
        Args:
            record_no: 单据号
            
        Returns:
            StockRecord: 出入库记录对象，如果不存在返回None
        """
        sql = "SELECT * FROM stock_record WHERE record_no=%s"
        params = (record_no,)
        
        result = self.fetch_one(sql, params)
        if result:
            return StockRecord.from_dict(result)
        return None
    
    def get_by_warehouse(self, warehouse_id: int, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[StockRecord]:
        """
        根据仓库和时间范围查询
        
        Args:
            warehouse_id: 仓库ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            list: 出入库记录对象列表
        """
        sql = "SELECT * FROM stock_record WHERE warehouse_id=%s"
        params = [warehouse_id]
        
        if start_date:
            sql += " AND record_date >= %s"
            params.append(start_date)
        
        if end_date:
            sql += " AND record_date <= %s"
            params.append(end_date)
        
        sql += " ORDER BY record_date DESC, id DESC"
        
        results = self.fetch_all(sql, tuple(params))
        return [StockRecord.from_dict(row) for row in results]
    
    def get_by_product(self, product_id: int, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[StockRecord]:
        """
        根据货品和时间范围查询
        
        Args:
            product_id: 货品ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            list: 出入库记录对象列表
        """
        sql = "SELECT * FROM stock_record WHERE product_id=%s"
        params = [product_id]
        
        if start_date:
            sql += " AND record_date >= %s"
            params.append(start_date)
        
        if end_date:
            sql += " AND record_date <= %s"
            params.append(end_date)
        
        sql += " ORDER BY record_date DESC, id DESC"
        
        results = self.fetch_all(sql, tuple(params))
        return [StockRecord.from_dict(row) for row in results]
    
    def get_by_type(self, record_type: int, start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> List[StockRecord]:
        """
        根据类型和时间范围查询
        
        Args:
            record_type: 记录类型（1-入库，2-出库）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            list: 出入库记录对象列表
        """
        sql = "SELECT * FROM stock_record WHERE record_type=%s"
        params = [record_type]
        
        if start_date:
            sql += " AND record_date >= %s"
            params.append(start_date)
        
        if end_date:
            sql += " AND record_date <= %s"
            params.append(end_date)
        
        sql += " ORDER BY record_date DESC, id DESC"
        
        results = self.fetch_all(sql, tuple(params))
        return [StockRecord.from_dict(row) for row in results]
    
    def get_all(self) -> List[StockRecord]:
        """
        查询所有记录
        
        Returns:
            list: 出入库记录对象列表
        """
        sql = "SELECT * FROM stock_record ORDER BY record_date DESC, id DESC"
        results = self.fetch_all(sql)
        return [StockRecord.from_dict(row) for row in results]
    
    def get_statistics(self, warehouse_id: Optional[int] = None,
                      product_id: Optional[int] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> dict:
        """
        统计查询
        
        Args:
            warehouse_id: 仓库ID（可选）
            product_id: 货品ID（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            dict: 统计结果
        """
        sql = "SELECT record_type, SUM(quantity) as total_quantity, SUM(total_amount) as total_amount FROM stock_record WHERE 1=1"
        params = []
        
        if warehouse_id:
            sql += " AND warehouse_id=%s"
            params.append(warehouse_id)
        
        if product_id:
            sql += " AND product_id=%s"
            params.append(product_id)
        
        if start_date:
            sql += " AND record_date >= %s"
            params.append(start_date)
        
        if end_date:
            sql += " AND record_date <= %s"
            params.append(end_date)
        
        sql += " GROUP BY record_type"
        
        results = self.fetch_all(sql, tuple(params) if params else None)
        
        statistics = {
            'in_stock': {'quantity': 0, 'amount': 0},
            'out_stock': {'quantity': 0, 'amount': 0}
        }
        
        for row in results:
            if row['record_type'] == 1:
                statistics['in_stock']['quantity'] = row['total_quantity'] or 0
                statistics['in_stock']['amount'] = float(row['total_amount'] or 0)
            elif row['record_type'] == 2:
                statistics['out_stock']['quantity'] = row['total_quantity'] or 0
                statistics['out_stock']['amount'] = float(row['total_amount'] or 0)
        
        return statistics

