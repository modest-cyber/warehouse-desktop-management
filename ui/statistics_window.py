# -*- coding: utf-8 -*-
"""库存统计页面（PySide6）

需求参考：《PySide前端页面设计需求文档》13. 库存统计页面
（图表展示可选，此处先实现表格+导出功能）
"""

from typing import List, Optional, Dict, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

from service.query_service import QueryService
from service.inventory_service import InventoryService
from service.warehouse_service import WarehouseService
from service.product_service import ProductService
from model.warehouse import Warehouse
from model.product import Product
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class StatisticsWindow(QWidget):
    """库存统计页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.query_service = QueryService()
        self.inventory_service = InventoryService()
        self.warehouse_service = WarehouseService()
        self.product_service = ProductService()
        self._init_ui()
        self._load_filters()
        self.refresh_table()

    def _init_ui(self):
        self.setObjectName("StatisticsWindow")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 顶部：统计维度
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("统计类型:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItem("按仓库", "warehouse")
        self.combo_mode.addItem("按货品", "product")
        self.combo_mode.addItem("预警统计", "warning")
        top_layout.addWidget(self.combo_mode)

        top_layout.addWidget(QLabel("仓库:"))
        self.combo_warehouse = QComboBox()
        top_layout.addWidget(self.combo_warehouse)

        top_layout.addWidget(QLabel("货品:"))
        self.combo_product = QComboBox()
        top_layout.addWidget(self.combo_product)

        self.btn_refresh = QPushButton("刷新(&R)")
        self.btn_export = QPushButton("导出")
        top_layout.addWidget(self.btn_refresh)
        top_layout.addWidget(self.btn_export)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # 中间表格
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        main_layout.addWidget(self.table)

        # 信号
        self.btn_refresh.clicked.connect(self.refresh_table)
        self.btn_export.clicked.connect(self._on_export)
        self.combo_mode.currentIndexChanged.connect(self.refresh_table)

    def _load_filters(self):
        try:
            # 仓库列表
            self.combo_warehouse.clear()
            self.combo_warehouse.addItem("全部", None)
            warehouses: List[Warehouse] = self.warehouse_service.get_all_warehouse()
            for w in warehouses:
                self.combo_warehouse.addItem(w.warehouse_name, w.id)

            # 货品列表
            self.combo_product.clear()
            self.combo_product.addItem("全部", None)
            products: List[Product] = self.product_service.get_all_product()
            for p in products:
                self.combo_product.addItem(f"{p.product_code}-{p.product_name}", p.id)
        except Exception as e:
            logger.error(f"加载统计维度失败: {e}")

    def refresh_table(self):
        mode = self.combo_mode.currentData()
        if mode == "warehouse":
            self._load_by_warehouse()
        elif mode == "product":
            self._load_by_product()
        else:
            self._load_warning()

    # --------- 按仓库统计 ---------
    def _load_by_warehouse(self):
        try:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels([
                "仓库",
                "库存数量",
                "库存价值",
                "货品种类数",
            ])

            wh_id = self.combo_warehouse.currentData()
            warehouses: List[Warehouse]
            if wh_id:
                w = self.warehouse_service.get_warehouse(wh_id)
                warehouses = [w] if w else []
            else:
                warehouses = self.warehouse_service.get_all_warehouse()

            self.table.setRowCount(len(warehouses))
            for row, w in enumerate(warehouses):
                stats = self.query_service.get_warehouse_statistics(w.id)
                self.table.setItem(row, 0, QTableWidgetItem(stats.get("warehouse_name", "")))
                self.table.setItem(row, 1, QTableWidgetItem(str(stats.get("total_quantity", 0))))
                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(f"{stats.get('total_value', 0.0):.2f}"),
                )
                self.table.setItem(row, 3, QTableWidgetItem(str(stats.get("product_count", 0))))
        except Exception as e:
            logger.error(f"按仓库统计失败: {e}")
            QMessageBox.critical(self, "错误", f"统计失败: {e}")

    # --------- 按货品统计 ---------
    def _load_by_product(self):
        try:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels([
                "货品",
                "库存数量",
                "库存价值",
                "分布仓库数",
            ])

            prod_id = self.combo_product.currentData()
            products: List[Product]
            if prod_id:
                p = self.product_service.get_product(prod_id)
                products = [p] if p else []
            else:
                products = self.product_service.get_all_product()

            self.table.setRowCount(len(products))
            for row, p in enumerate(products):
                stats = self.query_service.get_product_statistics(p.id)
                self.table.setItem(row, 0, QTableWidgetItem(stats.get("product_name", "")))
                self.table.setItem(row, 1, QTableWidgetItem(str(stats.get("total_quantity", 0))))
                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(f"{stats.get('total_value', 0.0):.2f}"),
                )
                self.table.setItem(row, 3, QTableWidgetItem(str(stats.get("warehouse_count", 0))))
        except Exception as e:
            logger.error(f"按货品统计失败: {e}")
            QMessageBox.critical(self, "错误", f"统计失败: {e}")

    # --------- 预警统计 ---------
    def _load_warning(self):
        try:
            # 将低库存和超库存合并在一个列表展示
            low_list = self.inventory_service.get_low_stock()
            over_list = self.inventory_service.get_over_stock()
            rows = []
            for item in low_list:
                rows.append(("低库存", item))
            for item in over_list:
                rows.append(("超库存", item))

            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                "预警类型",
                "仓库",
                "货品",
                "当前库存",
                "最低/最高",
                "差值",
                "备注",
            ])

            self.table.setRowCount(len(rows))
            for row, (wtype, info) in enumerate(rows):
                inv = info["inventory"]
                product = info["product"]
                wh = self.warehouse_service.get_warehouse(inv.warehouse_id)
                self.table.setItem(row, 0, QTableWidgetItem(wtype))
                self.table.setItem(row, 1, QTableWidgetItem(wh.warehouse_name if wh else ""))
                self.table.setItem(row, 2, QTableWidgetItem(product.product_name if product else ""))
                self.table.setItem(row, 3, QTableWidgetItem(str(info.get("current_quantity", 0))))
                if wtype == "低库存":
                    range_text = f"min={info.get('min_stock', 0)}"
                else:
                    range_text = f"max={info.get('max_stock', 0)}"
                self.table.setItem(row, 4, QTableWidgetItem(range_text))
                self.table.setItem(row, 5, QTableWidgetItem(str(info.get("difference", 0))))
                self.table.setItem(row, 6, QTableWidgetItem(""))
        except Exception as e:
            logger.error(f"预警统计失败: {e}")
            QMessageBox.critical(self, "错误", f"统计失败: {e}")

    def _on_export(self):
        try:
            from PySide6.QtWidgets import QFileDialog

            row_count = self.table.rowCount()
            col_count = self.table.columnCount()
            if row_count == 0 or col_count == 0:
                QMessageBox.information(self, "提示", "当前无数据可导出")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出库存统计",
                "库存统计.xlsx",
                "Excel 文件 (*.xlsx)"
            )
            if not file_path:
                return

            headers = [self.table.horizontalHeaderItem(i).text() for i in range(col_count)]
            data: List[Dict[str, Any]] = []
            for r in range(row_count):
                row_dict: Dict[str, Any] = {}
                for c, header in enumerate(headers):
                    item = self.table.item(r, c)
                    row_dict[header] = item.text() if item else ""
                data.append(row_dict)

            self.query_service.export_to_excel(
                data,
                file_path,
                sheet_name="库存统计",
                headers=headers,
            )
            QMessageBox.information(self, "成功", "导出成功")
        except Exception as e:
            logger.error(f"导出库存统计失败: {e}")
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
