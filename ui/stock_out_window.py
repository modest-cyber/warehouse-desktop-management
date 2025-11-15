# -*- coding: utf-8 -*-
"""出库管理页面（PySide6）

需求参考：《PySide前端页面设计需求文档》10. 出库管理页面
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

from service.stock_service import StockService
from service.warehouse_service import WarehouseService
from service.product_service import ProductService
from service.supplier_client_service import SupplierClientService
from service.inventory_service import InventoryService
from model.stock_record import StockRecord
from model.warehouse import Warehouse
from model.product import Product
from model.supplier_client import SupplierClient
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class StockOutWindow(QWidget):
    """出库管理页面"""

    def __init__(self, operator: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.stock_service = StockService()
        self.warehouse_service = WarehouseService()
        self.product_service = ProductService()
        self.supplier_service = SupplierClientService()
        self.inventory_service = InventoryService()
        self._init_ui()
        self._load_basic_data()
        self._reset_form()
        if operator:
            self.set_current_user(operator)
        self._load_today_records()

    def _init_ui(self):
        self.setObjectName("StockOutWindow")
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 左侧：出库单表单
        form_layout = QVBoxLayout()

        title = QLabel("出库单录入")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #E91E63;")
        form_layout.addWidget(title)

        self.edit_record_no = QLineEdit()
        self.edit_record_no.setReadOnly(True)

        self.combo_warehouse = QComboBox()
        self.combo_product = QComboBox()
        self.edit_current_stock = QLineEdit()
        self.edit_current_stock.setReadOnly(True)
        self.spin_quantity = QSpinBox()
        self.spin_quantity.setRange(1, 999999999)
        self.spin_unit_price = QDoubleSpinBox()
        self.spin_unit_price.setRange(0, 99999999)
        self.spin_unit_price.setDecimals(2)
        self.edit_total_amount = QLineEdit()
        self.edit_total_amount.setReadOnly(True)
        self.combo_client = QComboBox()
        self.edit_operator = QLineEdit()
        self.edit_operator.setReadOnly(True)
        self.date_record = QDateEdit()
        self.date_record.setCalendarPopup(True)
        self.date_record.setDate(QDate.currentDate())
        self.text_remark = QTextEdit()

        form_grid = QVBoxLayout()

        def row(label_text: str, widget):
            r = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(80)
            r.addWidget(lbl)
            r.addWidget(widget)
            form_grid.addLayout(r)

        row("单据号:", self.edit_record_no)
        row("仓库:", self.combo_warehouse)
        row("货品:", self.combo_product)
        row("当前库存:", self.edit_current_stock)
        row("数量:", self.spin_quantity)
        row("单价:", self.spin_unit_price)
        row("总金额:", self.edit_total_amount)
        row("客户:", self.combo_client)
        row("操作人:", self.edit_operator)
        row("操作日期:", self.date_record)

        form_layout.addLayout(form_grid)

        form_layout.addWidget(QLabel("备注:"))
        form_layout.addWidget(self.text_remark)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("保存(&S)")
        self.btn_reset = QPushButton("重置(&R)")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_reset)
        form_layout.addLayout(btn_layout)

        # 右侧：今日出库记录
        right_layout = QVBoxLayout()
        right_title = QLabel("今日出库记录")
        right_title.setAlignment(Qt.AlignCenter)
        right_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        right_layout.addWidget(right_title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "单据号",
            "仓库",
            "货品",
            "数量",
            "金额",
            "操作人",
            "时间",
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        right_layout.addWidget(self.table)

        main_layout.addLayout(form_layout, 2)
        main_layout.addLayout(right_layout, 3)

        # 信号
        self.combo_warehouse.currentIndexChanged.connect(self._update_current_stock)
        self.combo_product.currentIndexChanged.connect(self._update_current_stock)
        self.spin_quantity.valueChanged.connect(self._update_total_amount)
        self.spin_unit_price.valueChanged.connect(self._update_total_amount)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_reset.clicked.connect(self._reset_form)

    # ----------- 数据加载 -----------
    def _load_basic_data(self):
        try:
            warehouses: List[Warehouse] = self.warehouse_service.get_active_warehouses()
            self.combo_warehouse.clear()
            for w in warehouses:
                self.combo_warehouse.addItem(w.warehouse_name, w.id)

            products: List[Product] = self.product_service.get_all_product()
            self.combo_product.clear()
            for p in products:
                if p.status == 1:
                    self.combo_product.addItem(f"{p.product_code}-{p.product_name}", p.id)

            clients: List[SupplierClient] = self.supplier_service.get_clients()
            self.combo_client.clear()
            self.combo_client.addItem("(可选)", None)
            for c in clients:
                self.combo_client.addItem(c.name, c.id)
        except Exception as e:
            logger.error(f"加载基础数据失败: {e}")

    def _load_today_records(self):
        try:
            today = datetime.now().date()
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today, datetime.max.time())
            from service.query_service import QueryService

            qs = QueryService()
            records = qs.query_stock_records({"record_type": 2, "start_date": start, "end_date": end})

            warehouses = {w.id: w for w in self.warehouse_service.get_all_warehouse()}
            products = {p.id: p for p in self.product_service.get_all_product()}

            self.table.setRowCount(len(records))
            for row, r in enumerate(records):
                self.table.setItem(row, 0, QTableWidgetItem(r.record_no or ""))
                self.table.setItem(row, 1, QTableWidgetItem(warehouses.get(r.warehouse_id).warehouse_name if warehouses.get(r.warehouse_id) else ""))
                self.table.setItem(row, 2, QTableWidgetItem(products.get(r.product_id).product_name if products.get(r.product_id) else ""))
                self.table.setItem(row, 3, QTableWidgetItem(str(r.quantity)))
                self.table.setItem(row, 4, QTableWidgetItem(f"{float(r.total_amount):.2f}" if r.total_amount else ""))
                self.table.setItem(row, 5, QTableWidgetItem(r.operator or ""))
                self.table.setItem(
                    row,
                    6,
                    QTableWidgetItem(r.record_date.strftime("%Y-%m-%d %H:%M:%S") if r.record_date else ""),
                )
        except Exception as e:
            logger.error(f"加载今日出库记录失败: {e}")

    # ----------- 表单逻辑 -----------
    def _generate_record_no(self) -> str:
        return self.stock_service.generate_record_no(2)

    def _reset_form(self):
        try:
            self.edit_record_no.setText(self._generate_record_no())
        except Exception as e:
            logger.error(f"生成单据号失败: {e}")
            self.edit_record_no.setText("")
        if self.combo_warehouse.count() > 0:
            self.combo_warehouse.setCurrentIndex(0)
        if self.combo_product.count() > 0:
            self.combo_product.setCurrentIndex(0)
        self.edit_current_stock.setText("0")
        self.spin_quantity.setValue(1)
        self.spin_unit_price.setValue(0.0)
        self.edit_total_amount.setText("0.00")
        if self.combo_client.count() > 0:
            self.combo_client.setCurrentIndex(0)
        self.date_record.setDate(QDate.currentDate())
        self.text_remark.clear()

    def set_current_user(self, username: str):
        self.edit_operator.setText(username or "")

    def _update_current_stock(self):
        warehouse_id = self.combo_warehouse.currentData()
        product_id = self.combo_product.currentData()
        if not warehouse_id or not product_id:
            self.edit_current_stock.setText("0")
            return
        try:
            inv = self.inventory_service.get_inventory(warehouse_id, product_id)
            qty = inv.quantity if inv else 0
            self.edit_current_stock.setText(str(qty))
        except Exception as e:
            logger.error(f"查询库存失败: {e}")
            self.edit_current_stock.setText("0")

    def _update_total_amount(self):
        qty = self.spin_quantity.value()
        price = self.spin_unit_price.value()
        self.edit_total_amount.setText(f"{qty * price:.2f}")

    def _on_save(self):
        warehouse_id = self.combo_warehouse.currentData()
        product_id = self.combo_product.currentData()
        if not warehouse_id:
            QMessageBox.warning(self, "提示", "请选择仓库")
            return
        if not product_id:
            QMessageBox.warning(self, "提示", "请选择货品")
            return

        quantity = self.spin_quantity.value()
        current_stock = int(self.edit_current_stock.text() or "0")
        if quantity <= 0:
            QMessageBox.warning(self, "提示", "数量必须大于0")
            return
        if quantity > current_stock:
            QMessageBox.warning(self, "提示", f"数量不能大于当前库存（{current_stock}）")
            return

        record_qdate: QDate = self.date_record.date()
        record_pydate = date(record_qdate.year(), record_qdate.month(), record_qdate.day())
        if record_pydate > date.today():
            QMessageBox.warning(self, "提示", "操作日期不能晚于今天")
            return

        try:
            record = StockRecord(
                record_no=self.edit_record_no.text() or None,
                record_type=2,
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=Decimal(str(self.spin_unit_price.value())) if self.spin_unit_price.value() > 0 else None,
                supplier_client_id=self.combo_client.currentData(),
                operator=self.edit_operator.text() or None,
                record_date=datetime.combine(record_pydate, datetime.now().time()),
                remark=self.text_remark.toPlainText().strip() or None,
            )
            self.stock_service.add_out_stock(record)
            QMessageBox.information(self, "成功", "出库记录保存成功")
            self._reset_form()
            self._load_today_records()
        except Exception as e:
            logger.error(f"保存出库记录失败: {e}")
            QMessageBox.critical(self, "错误", f"保存失败: {e}")
            return

        try:
            self.edit_record_no.setText(self._generate_record_no())
        except Exception:
            pass
