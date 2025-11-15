# -*- coding: utf-8 -*-
"""入库管理页面（PySide6）

需求参考：《PySide前端页面设计需求文档》9. 入库管理页面
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
from model.stock_record import StockRecord
from model.warehouse import Warehouse
from model.product import Product
from model.supplier_client import SupplierClient
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class StockInWindow(QWidget):
    """入库管理页面"""

    def __init__(self, operator: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.stock_service = StockService()
        self.warehouse_service = WarehouseService()
        self.product_service = ProductService()
        self.supplier_service = SupplierClientService()
        self._init_ui()
        self._load_basic_data()
        self._reset_form()
        if operator:
            self.set_current_user(operator)
        self._load_today_records()

    def _init_ui(self):
        self.setObjectName("StockInWindow")
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 左侧：入库单表单
        form_layout = QVBoxLayout()

        # 标题
        title = QLabel("入库单录入")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        form_layout.addWidget(title)

        # 字段
        self.edit_record_no = QLineEdit()
        self.edit_record_no.setReadOnly(True)

        self.combo_warehouse = QComboBox()
        self.combo_product = QComboBox()
        self.spin_quantity = QSpinBox()
        self.spin_quantity.setRange(1, 999999999)
        self.spin_unit_price = QDoubleSpinBox()
        self.spin_unit_price.setRange(0, 99999999)
        self.spin_unit_price.setDecimals(2)
        self.edit_total_amount = QLineEdit()
        self.edit_total_amount.setReadOnly(True)
        self.combo_supplier = QComboBox()
        self.edit_operator = QLineEdit()
        self.edit_operator.setReadOnly(True)
        self.date_record = QDateEdit()
        self.date_record.setCalendarPopup(True)
        self.date_record.setDate(QDate.currentDate())
        self.text_remark = QTextEdit()

        form_grid = QVBoxLayout()

        def row(label_text: str, widget):
            row_layout = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(80)
            row_layout.addWidget(lbl)
            row_layout.addWidget(widget)
            form_grid.addLayout(row_layout)

        row("单据号:", self.edit_record_no)
        row("仓库:", self.combo_warehouse)
        row("货品:", self.combo_product)
        row("数量:", self.spin_quantity)
        row("单价:", self.spin_unit_price)
        row("总金额:", self.edit_total_amount)
        row("供应商:", self.combo_supplier)
        row("操作人:", self.edit_operator)
        row("操作日期:", self.date_record)

        form_layout.addLayout(form_grid)

        # 备注
        remark_lbl = QLabel("备注:")
        form_layout.addWidget(remark_lbl)
        form_layout.addWidget(self.text_remark)

        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("保存(&S)")
        self.btn_reset = QPushButton("重置(&R)")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_reset)
        form_layout.addLayout(btn_layout)

        # 右侧：今日入库记录
        right_layout = QVBoxLayout()
        right_title = QLabel("今日入库记录")
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
        self.spin_quantity.valueChanged.connect(self._update_total_amount)
        self.spin_unit_price.valueChanged.connect(self._update_total_amount)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_reset.clicked.connect(self._reset_form)

    # ------------- 数据加载 -------------
    def _load_basic_data(self):
        try:
            # 仓库（启用的）
            warehouses: List[Warehouse] = self.warehouse_service.get_active_warehouses()
            self.combo_warehouse.clear()
            for w in warehouses:
                self.combo_warehouse.addItem(w.warehouse_name, w.id)

            # 货品（启用的）
            products: List[Product] = self.product_service.get_all_product()
            self.combo_product.clear()
            for p in products:
                if p.status == 1:
                    self.combo_product.addItem(f"{p.product_code}-{p.product_name}", p.id)

            # 供应商
            suppliers: List[SupplierClient] = self.supplier_service.get_suppliers()
            self.combo_supplier.clear()
            self.combo_supplier.addItem("(可选)", None)
            for s in suppliers:
                self.combo_supplier.addItem(s.name, s.id)
        except Exception as e:
            logger.error(f"加载基础数据失败: {e}")

    def _load_today_records(self):
        """加载今日入库记录列表"""
        try:
            today = datetime.now().date()
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today, datetime.max.time())
            from service.query_service import QueryService

            qs = QueryService()
            records = qs.query_stock_records({"record_type": 1, "start_date": start, "end_date": end})

            # 预取名称
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
            logger.error(f"加载今日入库记录失败: {e}")

    # ------------- 表单逻辑 -------------
    def _generate_record_no(self) -> str:
        return self.stock_service.generate_record_no(1)

    def _reset_form(self):
        try:
            self.edit_record_no.setText(self._generate_record_no())
        except Exception as e:
            logger.error(f"生成单据号失败: {e}")
            self.edit_record_no.setText("")
        self.combo_warehouse.setCurrentIndex(0 if self.combo_warehouse.count() > 0 else -1)
        self.combo_product.setCurrentIndex(0 if self.combo_product.count() > 0 else -1)
        self.spin_quantity.setValue(1)
        self.spin_unit_price.setValue(0.0)
        self.edit_total_amount.setText("0.00")
        self.combo_supplier.setCurrentIndex(0 if self.combo_supplier.count() > 0 else -1)
        self.date_record.setDate(QDate.currentDate())
        self.text_remark.clear()

    def set_current_user(self, username: str):
        """供外部注入当前登录用户用户名，用于操作人字段显示"""
        self.edit_operator.setText(username or "")

    def _update_total_amount(self):
        qty = self.spin_quantity.value()
        price = self.spin_unit_price.value()
        total = qty * price
        self.edit_total_amount.setText(f"{total:.2f}")

    def _on_save(self):
        # 仓库/货品必选
        warehouse_id = self.combo_warehouse.currentData()
        product_id = self.combo_product.currentData()
        if not warehouse_id:
            QMessageBox.warning(self, "提示", "请选择仓库")
            return
        if not product_id:
            QMessageBox.warning(self, "提示", "请选择货品")
            return

        quantity = self.spin_quantity.value()
        if quantity <= 0:
            QMessageBox.warning(self, "提示", "数量必须大于0")
            return

        record_qdate: QDate = self.date_record.date()
        record_pydate = date(record_qdate.year(), record_qdate.month(), record_qdate.day())
        if record_pydate > date.today():
            QMessageBox.warning(self, "提示", "操作日期不能晚于今天")
            return

        try:
            record = StockRecord(
                record_no=self.edit_record_no.text() or None,
                record_type=1,
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=Decimal(str(self.spin_unit_price.value())) if self.spin_unit_price.value() > 0 else None,
                supplier_client_id=self.combo_supplier.currentData(),
                operator=self.edit_operator.text() or None,
                record_date=datetime.combine(record_pydate, datetime.now().time()),
                remark=self.text_remark.toPlainText().strip() or None,
            )
            self.stock_service.add_in_stock(record)
            QMessageBox.information(self, "成功", "入库记录保存成功")
            self._reset_form()
            self._load_today_records()
        except Exception as e:
            logger.error(f"保存入库记录失败: {e}")
            QMessageBox.critical(self, "错误", f"保存失败: {e}")
            return

        # 保存成功后，重新生成单据号
        try:
            self.edit_record_no.setText(self._generate_record_no())
        except Exception:
            pass
