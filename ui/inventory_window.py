# -*- coding: utf-8 -*-
"""库存管理/查询页面（PySide6）

需求参考：《PySide前端页面设计需求文档》11. 库存管理页面
"""

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

from service.inventory_service import InventoryService
from service.product_service import ProductService
from service.warehouse_service import WarehouseService
from service.query_service import QueryService
from model.inventory import Inventory
from model.product import Product
from model.warehouse import Warehouse
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class InventoryWindow(QWidget):
    """库存管理/查询页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.inventory_service = InventoryService()
        self.product_service = ProductService()
        self.warehouse_service = WarehouseService()
        self.query_service = QueryService()
        self._init_ui()
        self._load_filters()
        self.refresh_table()

    def _init_ui(self):
        self.setObjectName("InventoryWindow")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 顶部筛选
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("仓库:"))
        self.combo_warehouse = QComboBox()
        top_layout.addWidget(self.combo_warehouse)

        top_layout.addWidget(QLabel("货品:"))
        self.edit_product_keyword = QLineEdit()
        self.edit_product_keyword.setPlaceholderText("编码/名称 模糊查询")
        top_layout.addWidget(self.edit_product_keyword)

        top_layout.addWidget(QLabel("预警:"))
        self.combo_warning = QComboBox()
        self.combo_warning.addItem("全部", "all")
        self.combo_warning.addItem("低库存", "low")
        self.combo_warning.addItem("超库存", "over")
        self.combo_warning.addItem("正常", "normal")
        top_layout.addWidget(self.combo_warning)

        self.btn_search = QPushButton("查询(&F)")
        self.btn_export = QPushButton("导出")
        top_layout.addWidget(self.btn_search)
        top_layout.addWidget(self.btn_export)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # 中间表格
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "仓库",
            "货品编码",
            "货品名称",
            "当前库存",
            "最低库存",
            "最高库存",
            "预警状态",
            "最后入库日期",
            "最后出库日期",
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        main_layout.addWidget(self.table)

        # 底部统计
        bottom_layout = QHBoxLayout()
        self.label_total_quantity = QLabel("总库存数量: 0")
        self.label_total_value = QLabel("总库存价值: 0.00")
        self.label_product_count = QLabel("货品种类数: 0")
        self.label_low_count = QLabel("低库存数: 0")
        self.label_over_count = QLabel("超库存数: 0")
        bottom_layout.addWidget(self.label_total_quantity)
        bottom_layout.addWidget(self.label_total_value)
        bottom_layout.addWidget(self.label_product_count)
        bottom_layout.addWidget(self.label_low_count)
        bottom_layout.addWidget(self.label_over_count)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

        # 信号
        self.btn_search.clicked.connect(self.refresh_table)
        self.btn_export.clicked.connect(self._on_export)

    def _load_filters(self):
        try:
            self.combo_warehouse.clear()
            self.combo_warehouse.addItem("全部", None)
            warehouses: List[Warehouse] = self.warehouse_service.get_all_warehouse()
            for w in warehouses:
                self.combo_warehouse.addItem(w.warehouse_name, w.id)
        except Exception as e:
            logger.error(f"加载仓库列表失败: {e}")

    def refresh_table(self):
        try:
            warehouse_id = self.combo_warehouse.currentData()
            keyword = self.edit_product_keyword.text().strip()
            warning_filter = self.combo_warning.currentData()

            inventories: List[Inventory]
            if warehouse_id:
                inventories = self.inventory_service.get_inventory_by_warehouse(warehouse_id)
            else:
                inventories = self.inventory_service.get_all_inventory()

            products = {p.id: p for p in self.product_service.get_all_product()}
            warehouses = {w.id: w for w in self.warehouse_service.get_all_warehouse()}

            # 预警与关键字过滤
            filtered_rows = []
            for inv in inventories:
                product: Optional[Product] = products.get(inv.product_id)
                if not product:
                    continue
                # 货品关键字过滤
                if keyword:
                    code = product.product_code or ""
                    name = product.product_name or ""
                    if keyword not in code and keyword not in name:
                        continue

                warning_info = self.inventory_service.check_stock_warning(inv.warehouse_id, inv.product_id)
                warning_type = warning_info["warning_type"]
                # 预警筛选
                if warning_filter == "low" and warning_type != "low":
                    continue
                if warning_filter == "over" and warning_type != "over":
                    continue
                if warning_filter == "normal" and warning_type is not None:
                    continue

                filtered_rows.append((inv, product, warehouses.get(inv.warehouse_id), warning_info))

            self.table.setRowCount(len(filtered_rows))
            for row, (inv, product, wh, warning_info) in enumerate(filtered_rows):
                self.table.setItem(row, 0, QTableWidgetItem(str(inv.id)))
                self.table.setItem(row, 1, QTableWidgetItem(wh.warehouse_name if wh else ""))
                self.table.setItem(row, 2, QTableWidgetItem(product.product_code or ""))
                self.table.setItem(row, 3, QTableWidgetItem(product.product_name or ""))
                self.table.setItem(row, 4, QTableWidgetItem(str(inv.quantity)))
                self.table.setItem(row, 5, QTableWidgetItem(str(product.min_stock)))
                self.table.setItem(row, 6, QTableWidgetItem(str(product.max_stock)))

                wt = warning_info["warning_type"]
                if wt == "low":
                    text = "低库存"
                    color = Qt.red
                elif wt == "over":
                    text = "超库存"
                    color = Qt.yellow
                else:
                    text = "正常"
                    color = Qt.darkGreen
                item_warning = QTableWidgetItem(text)
                item_warning.setForeground(color)
                self.table.setItem(row, 7, item_warning)

                self.table.setItem(
                    row,
                    8,
                    QTableWidgetItem(
                        inv.last_in_date.strftime("%Y-%m-%d %H:%M:%S") if inv.last_in_date else ""
                    ),
                )
                self.table.setItem(
                    row,
                    9,
                    QTableWidgetItem(
                        inv.last_out_date.strftime("%Y-%m-%d %H:%M:%S") if inv.last_out_date else ""
                    ),
                )

            # 更新统计
            self._update_statistics(warehouse_id)
        except Exception as e:
            logger.error(f"加载库存数据失败: {e}")
            QMessageBox.critical(self, "错误", f"加载数据失败: {e}")

    def _update_statistics(self, warehouse_id: Optional[int]):
        try:
            stats = self.query_service.get_inventory_statistics(warehouse_id)
            self.label_total_quantity.setText(f"总库存数量: {stats['total_quantity']}")
            self.label_total_value.setText(f"总库存价值: {stats['total_value']:.2f}")
            self.label_product_count.setText(f"货品种类数: {stats['product_count']}")
            self.label_low_count.setText(f"低库存数: {stats['low_stock_count']}")
            self.label_over_count.setText(f"超库存数: {stats['over_stock_count']}")
        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")

    def _on_export(self):
        """导出当前表格数据到 Excel"""
        try:
            from PySide6.QtWidgets import QFileDialog

            row_count = self.table.rowCount()
            if row_count == 0:
                QMessageBox.information(self, "提示", "当前无数据可导出")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出库存数据",
                "库存数据.xlsx",
                "Excel 文件 (*.xlsx)"
            )
            if not file_path:
                return

            # 收集当前表格数据
            data = []
            headers = [
                "ID",
                "仓库",
                "货品编码",
                "货品名称",
                "当前库存",
                "最低库存",
                "最高库存",
                "预警状态",
                "最后入库日期",
                "最后出库日期",
            ]
            for r in range(row_count):
                row_dict = {}
                for c, header in enumerate(headers):
                    item = self.table.item(r, c)
                    row_dict[header] = item.text() if item else ""
                data.append(row_dict)

            self.query_service.export_to_excel(data, file_path, sheet_name="库存数据", headers=headers)
            QMessageBox.information(self, "成功", "导出成功")
        except Exception as e:
            logger.error(f"导出库存数据失败: {e}")
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
