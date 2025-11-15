# -*- coding: utf-8 -*-
"""出入库记录查询页面（PySide6）

需求参考：《PySide前端页面设计需求文档》12. 出入库记录查询页面
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)

from service.query_service import QueryService
from service.warehouse_service import WarehouseService
from service.product_service import ProductService
from service.supplier_client_service import SupplierClientService
from model.stock_record import StockRecord
from model.warehouse import Warehouse
from model.product import Product
from model.supplier_client import SupplierClient
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class RecordQueryWindow(QWidget):
    """出入库记录查询页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.query_service = QueryService()
        self.warehouse_service = WarehouseService()
        self.product_service = ProductService()
        self.supplier_service = SupplierClientService()
        self._init_ui()
        self._load_filters()

    def _init_ui(self):
        self.setObjectName("RecordQueryWindow")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 顶部：查询条件区
        cond_layout = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("仓库:"))
        self.combo_warehouse = QComboBox()
        row1.addWidget(self.combo_warehouse)

        row1.addWidget(QLabel("货品:"))
        self.combo_product = QComboBox()
        row1.addWidget(self.combo_product)

        row1.addWidget(QLabel("供/客:"))
        self.combo_supplier_client = QComboBox()
        row1.addWidget(self.combo_supplier_client)

        cond_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("类型:"))
        self.combo_type = QComboBox()
        self.combo_type.addItem("全部", None)
        self.combo_type.addItem("入库", 1)
        self.combo_type.addItem("出库", 2)
        row2.addWidget(self.combo_type)

        row2.addWidget(QLabel("开始日期:"))
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        row2.addWidget(self.date_start)

        row2.addWidget(QLabel("结束日期:"))
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        row2.addWidget(self.date_end)

        cond_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("单据号:"))
        self.edit_record_no = QLineEdit()
        row3.addWidget(self.edit_record_no)

        row3.addWidget(QLabel("操作人:"))
        self.edit_operator = QLineEdit()
        row3.addWidget(self.edit_operator)

        self.btn_query = QPushButton("查询(&Q)")
        self.btn_reset = QPushButton("重置(&R)")
        self.btn_export = QPushButton("导出")
        row3.addWidget(self.btn_query)
        row3.addWidget(self.btn_reset)
        row3.addWidget(self.btn_export)
        row3.addStretch()

        cond_layout.addLayout(row3)

        main_layout.addLayout(cond_layout)

        # 中间：结果表格
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "单据号",
            "类型",
            "仓库",
            "货品",
            "数量",
            "单价",
            "总金额",
            "供/客",
            "操作人",
            "操作日期",
            "备注",
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        main_layout.addWidget(self.table)

        # 底部统计
        stat_layout = QHBoxLayout()
        self.label_in_qty = QLabel("入库总数量: 0")
        self.label_in_amt = QLabel("入库总金额: 0.00")
        self.label_out_qty = QLabel("出库总数量: 0")
        self.label_out_amt = QLabel("出库总金额: 0.00")
        self.label_net_qty = QLabel("净入库数量: 0")
        self.label_net_amt = QLabel("净入库金额: 0.00")
        stat_layout.addWidget(self.label_in_qty)
        stat_layout.addWidget(self.label_in_amt)
        stat_layout.addWidget(self.label_out_qty)
        stat_layout.addWidget(self.label_out_amt)
        stat_layout.addWidget(self.label_net_qty)
        stat_layout.addWidget(self.label_net_amt)
        stat_layout.addStretch()

        main_layout.addLayout(stat_layout)

        # 信号
        self.btn_query.clicked.connect(self._on_query)
        self.btn_reset.clicked.connect(self._on_reset)
        self.btn_export.clicked.connect(self._on_export)

    def _load_filters(self):
        try:
            # 仓库
            self.combo_warehouse.clear()
            self.combo_warehouse.addItem("全部", None)
            warehouses: List[Warehouse] = self.warehouse_service.get_all_warehouse()
            for w in warehouses:
                self.combo_warehouse.addItem(w.warehouse_name, w.id)

            # 货品
            self.combo_product.clear()
            self.combo_product.addItem("全部", None)
            products: List[Product] = self.product_service.get_all_product()
            for p in products:
                self.combo_product.addItem(f"{p.product_code}-{p.product_name}", p.id)

            # 供/客
            self.combo_supplier_client.clear()
            self.combo_supplier_client.addItem("全部", None)
            all_sc: List[SupplierClient] = self.supplier_service.get_all_supplier_client()
            for sc in all_sc:
                type_text = "供应商" if sc.type == 1 else "客户"
                self.combo_supplier_client.addItem(f"{type_text}-{sc.name}", sc.id)

            # 默认日期范围：本月
            today = date.today()
            self.date_end.setDate(QDate(today.year, today.month, today.day))
            self.date_start.setDate(QDate(today.year, today.month, 1))
        except Exception as e:
            logger.error(f"加载查询条件失败: {e}")

    # --------- 查询逻辑 ---------
    def _collect_conditions(self) -> Dict[str, Any]:
        cond: Dict[str, Any] = {}
        wh_id = self.combo_warehouse.currentData()
        if wh_id:
            cond["warehouse_id"] = wh_id
        prod_id = self.combo_product.currentData()
        if prod_id:
            cond["product_id"] = prod_id
        sc_id = self.combo_supplier_client.currentData()
        if sc_id:
            cond["supplier_client_id"] = sc_id
        rt = self.combo_type.currentData()
        if rt:
            cond["record_type"] = rt

        if self.date_start.date().isValid():
            d = self.date_start.date()
            cond["start_date"] = datetime(d.year(), d.month(), d.day())
        if self.date_end.date().isValid():
            d = self.date_end.date()
            cond["end_date"] = datetime(d.year(), d.month(), d.day(), 23, 59, 59)

        if self.edit_record_no.text().strip():
            cond["record_no"] = self.edit_record_no.text().strip()
        if self.edit_operator.text().strip():
            cond["operator"] = self.edit_operator.text().strip()

        return cond

    def _on_query(self):
        try:
            cond = self._collect_conditions()
            records: List[StockRecord] = self.query_service.query_stock_records(cond)

            warehouses = {w.id: w for w in self.warehouse_service.get_all_warehouse()}
            products = {p.id: p for p in self.product_service.get_all_product()}
            sc_map = {s.id: s for s in self.supplier_service.get_all_supplier_client()}

            self.table.setRowCount(len(records))

            in_qty = in_amt = out_qty = out_amt = 0.0

            for row, r in enumerate(records):
                self.table.setItem(row, 0, QTableWidgetItem(str(r.id)))
                self.table.setItem(row, 1, QTableWidgetItem(r.record_no or ""))
                type_text = "入库" if r.record_type == 1 else "出库"
                self.table.setItem(row, 2, QTableWidgetItem(type_text))

                wh = warehouses.get(r.warehouse_id)
                self.table.setItem(row, 3, QTableWidgetItem(wh.warehouse_name if wh else ""))
                p = products.get(r.product_id)
                self.table.setItem(row, 4, QTableWidgetItem(p.product_name if p else ""))
                self.table.setItem(row, 5, QTableWidgetItem(str(r.quantity)))
                self.table.setItem(
                    row,
                    6,
                    QTableWidgetItem(f"{float(r.unit_price):.2f}" if r.unit_price is not None else ""),
                )
                self.table.setItem(
                    row,
                    7,
                    QTableWidgetItem(f"{float(r.total_amount):.2f}" if r.total_amount is not None else ""),
                )

                sc = sc_map.get(r.supplier_client_id)
                if sc:
                    sc_text = ("供应商" if sc.type == 1 else "客户") + "-" + (sc.name or "")
                else:
                    sc_text = ""
                self.table.setItem(row, 8, QTableWidgetItem(sc_text))

                self.table.setItem(row, 9, QTableWidgetItem(r.operator or ""))
                self.table.setItem(
                    row,
                    10,
                    QTableWidgetItem(
                        r.record_date.strftime("%Y-%m-%d %H:%M:%S") if r.record_date else ""
                    ),
                )
                self.table.setItem(row, 11, QTableWidgetItem(r.remark or ""))

                if r.record_type == 1:
                    in_qty += r.quantity or 0
                    if r.total_amount:
                        in_amt += float(r.total_amount)
                else:
                    out_qty += r.quantity or 0
                    if r.total_amount:
                        out_amt += float(r.total_amount)

            net_qty = in_qty - out_qty
            net_amt = in_amt - out_amt
            self.label_in_qty.setText(f"入库总数量: {int(in_qty)}")
            self.label_in_amt.setText(f"入库总金额: {in_amt:.2f}")
            self.label_out_qty.setText(f"出库总数量: {int(out_qty)}")
            self.label_out_amt.setText(f"出库总金额: {out_amt:.2f}")
            self.label_net_qty.setText(f"净入库数量: {int(net_qty)}")
            self.label_net_amt.setText(f"净入库金额: {net_amt:.2f}")
        except Exception as e:
            logger.error(f"查询出入库记录失败: {e}")
            QMessageBox.critical(self, "错误", f"查询失败: {e}")

    def _on_reset(self):
        self.combo_warehouse.setCurrentIndex(0)
        self.combo_product.setCurrentIndex(0)
        self.combo_supplier_client.setCurrentIndex(0)
        self.combo_type.setCurrentIndex(0)
        self.edit_record_no.clear()
        self.edit_operator.clear()
        self.table.setRowCount(0)
        self.label_in_qty.setText("入库总数量: 0")
        self.label_in_amt.setText("入库总金额: 0.00")
        self.label_out_qty.setText("出库总数量: 0")
        self.label_out_amt.setText("出库总金额: 0.00")
        self.label_net_qty.setText("净入库数量: 0")
        self.label_net_amt.setText("净入库金额: 0.00")

    def _on_export(self):
        try:
            from PySide6.QtWidgets import QFileDialog

            row_count = self.table.rowCount()
            if row_count == 0:
                QMessageBox.information(self, "提示", "当前无数据可导出")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出出入库记录",
                "出入库记录.xlsx",
                "Excel 文件 (*.xlsx)"
            )
            if not file_path:
                return

            headers = [
                "ID",
                "单据号",
                "类型",
                "仓库",
                "货品",
                "数量",
                "单价",
                "总金额",
                "供/客",
                "操作人",
                "操作日期",
                "备注",
            ]
            data = []
            for r in range(row_count):
                row_dict: Dict[str, Any] = {}
                for c, header in enumerate(headers):
                    item = self.table.item(r, c)
                    row_dict[header] = item.text() if item else ""
                data.append(row_dict)

            self.query_service.export_to_excel(
                data,
                file_path,
                sheet_name="出入库记录",
                headers=headers,
            )
            QMessageBox.information(self, "成功", "导出成功")
        except Exception as e:
            logger.error(f"导出出入库记录失败: {e}")
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
