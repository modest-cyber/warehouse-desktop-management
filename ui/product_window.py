# -*- coding: utf-8 -*-
"""货品信息管理页面（PySide6）

需求参考：《PySide前端页面设计需求文档》6. 货品信息管理页面
"""

from typing import List, Optional
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox
)

from service.product_service import ProductService
from service.base_info_service import BaseInfoService
from model.product import Product
from model.base_info import BaseInfo
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class ProductWindow(QWidget):
    """货品信息管理页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = ProductService()
        self.base_info_service = BaseInfoService()
        self._init_ui()
        self.refresh_table()

    def _init_ui(self):
        self.setObjectName("ProductWindow")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 顶部操作
        top_layout = QHBoxLayout()
        self.btn_add = QPushButton("新增(&N)")
        self.btn_edit = QPushButton("编辑(&E)")
        self.btn_delete = QPushButton("删除(&D)")
        self.btn_refresh = QPushButton("刷新(&R)")
        self.btn_import = QPushButton("导入")
        self.btn_export = QPushButton("导出")
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("货品编码/名称 搜索…")
        self.btn_search = QPushButton("搜索(&F)")

        for btn in (
            self.btn_add,
            self.btn_edit,
            self.btn_delete,
            self.btn_refresh,
            self.btn_import,
            self.btn_export,
            self.btn_search,
        ):
            btn.setMinimumWidth(70)

        top_layout.addWidget(self.btn_add)
        top_layout.addWidget(self.btn_edit)
        top_layout.addWidget(self.btn_delete)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addWidget(self.btn_import)
        top_layout.addWidget(self.btn_export)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("搜索:"))
        top_layout.addWidget(self.edit_search)
        top_layout.addWidget(self.btn_search)

        # 中间表格
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "货品编码",
            "货品名称",
            "类别",
            "单位",
            "规格",
            "单价",
            "最低库存",
            "最高库存",
            "状态",
            "创建时间",
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table)

        # 信号
        self.btn_refresh.clicked.connect(self.refresh_table)
        self.btn_search.clicked.connect(self._on_search)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_import.clicked.connect(lambda: QMessageBox.information(self, "提示", "导入功能暂未实现"))
        self.btn_export.clicked.connect(lambda: QMessageBox.information(self, "提示", "导出功能暂未实现"))
        self.table.cellDoubleClicked.connect(lambda *_: self._on_edit())

    # ------------- 数据加载 ------------
    def refresh_table(self):
        try:
            products: List[Product] = self.service.get_all_product()
            keyword = self.edit_search.text().strip()
            if keyword:
                products = [
                    p
                    for p in products
                    if (p.product_code and keyword in p.product_code)
                    or (p.product_name and keyword in p.product_name)
                ]

            # 预加载类别/单位名称
            base_infos = self.base_info_service.get_all_base_info()
            category_map = {b.id: b.info_name for b in base_infos if b.info_type == "category"}
            unit_map = {b.id: b.info_name for b in base_infos if b.info_type == "unit"}

            self.table.setRowCount(len(products))
            for row, p in enumerate(products):
                self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
                self.table.setItem(row, 1, QTableWidgetItem(p.product_code or ""))
                self.table.setItem(row, 2, QTableWidgetItem(p.product_name or ""))
                self.table.setItem(row, 3, QTableWidgetItem(category_map.get(p.category_id, "")))
                self.table.setItem(row, 4, QTableWidgetItem(unit_map.get(p.unit_id, "")))
                self.table.setItem(row, 5, QTableWidgetItem(p.specification or ""))
                self.table.setItem(
                    row,
                    6,
                    QTableWidgetItem(f"{float(p.price):.2f}" if p.price is not None else ""),
                )
                self.table.setItem(row, 7, QTableWidgetItem(str(p.min_stock)))
                self.table.setItem(row, 8, QTableWidgetItem(str(p.max_stock)))
                status_item = QTableWidgetItem("启用" if p.status == 1 else "禁用")
                if p.status == 1:
                    status_item.setForeground(Qt.darkGreen)
                else:
                    status_item.setForeground(Qt.red)
                self.table.setItem(row, 9, status_item)
                self.table.setItem(
                    row,
                    10,
                    QTableWidgetItem(
                        p.create_time.strftime("%Y-%m-%d %H:%M:%S") if p.create_time else ""
                    ),
                )
        except Exception as e:
            logger.error(f"加载货品数据失败: {e}")
            QMessageBox.critical(self, "错误", f"加载数据失败: {e}")

    def _get_selected_id(self) -> Optional[int]:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    # ------------- 事件 ------------
    def _on_search(self):
        self.refresh_table()

    def _on_add(self):
        dialog = ProductEditDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def _on_edit(self):
        pid = self._get_selected_id()
        if not pid:
            QMessageBox.information(self, "提示", "请先选择要编辑的记录")
            return
        product = self.service.get_product(pid)
        if not product:
            QMessageBox.warning(self, "提示", "记录不存在或已被删除")
            self.refresh_table()
            return
        dialog = ProductEditDialog(product=product, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def _on_delete(self):
        pid = self._get_selected_id()
        if not pid:
            QMessageBox.information(self, "提示", "请先选择要删除的记录")
            return
        if QMessageBox.question(self, "确认删除", "确定要删除选中的货品吗？") != QMessageBox.Yes:
            return
        try:
            self.service.delete_product(pid)
            QMessageBox.information(self, "成功", "删除成功")
            self.refresh_table()
        except Exception as e:
            QMessageBox.warning(self, "警告", str(e))


class ProductEditDialog(QDialog):
    """新增/编辑货品信息对话框"""

    def __init__(self, product: Optional[Product] = None, parent=None):
        super().__init__(parent)
        self.service = ProductService()
        self.base_info_service = BaseInfoService()
        self.product = product
        self._init_ui()
        self._load_base_info()
        self._load_data()

    def _init_ui(self):
        self.setWindowTitle("货品信息 - 新增" if not self.product else "货品信息 - 编辑")
        self.resize(480, 360)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.edit_code = QLineEdit(self)
        self.edit_name = QLineEdit(self)
        self.combo_category = QComboBox(self)
        self.combo_unit = QComboBox(self)
        self.edit_spec = QLineEdit(self)
        self.spin_price = QDoubleSpinBox(self)
        self.spin_price.setDecimals(2)
        self.spin_price.setRange(0, 99999999)
        self.spin_min = QSpinBox(self)
        self.spin_min.setRange(0, 999999999)
        self.spin_max = QSpinBox(self)
        self.spin_max.setRange(0, 999999999)
        self.text_desc = QTextEdit(self)
        self.combo_status = QComboBox(self)
        self.combo_status.addItem("启用", 1)
        self.combo_status.addItem("禁用", 0)

        form.addRow("货品编码:", self.edit_code)
        form.addRow("货品名称:", self.edit_name)
        form.addRow("类别:", self.combo_category)
        form.addRow("单位:", self.combo_unit)
        form.addRow("规格:", self.edit_spec)
        form.addRow("单价:", self.spin_price)
        form.addRow("最低库存:", self.spin_min)
        form.addRow("最高库存:", self.spin_max)
        form.addRow("描述:", self.text_desc)
        form.addRow("状态:", self.combo_status)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_ok = QPushButton("确定(&S)")
        self.btn_cancel = QPushButton("取消(&C)")
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.btn_ok.clicked.connect(self._on_ok)
        self.btn_cancel.clicked.connect(self.reject)

    def _load_base_info(self):
        """加载类别/单位下拉"""
        try:
            infos: List[BaseInfo] = self.base_info_service.get_all_base_info()
            categories = [i for i in infos if i.info_type == "category" and i.status == 1]
            units = [i for i in infos if i.info_type == "unit" and i.status == 1]

            self.combo_category.clear()
            self.combo_category.addItem("(未选择)", None)
            for c in categories:
                self.combo_category.addItem(c.info_name, c.id)

            self.combo_unit.clear()
            self.combo_unit.addItem("(未选择)", None)
            for u in units:
                self.combo_unit.addItem(u.info_name, u.id)
        except Exception as e:
            logger.error(f"加载基础信息失败: {e}")

    def _load_data(self):
        if not self.product:
            # 新增时，编码可以留空自动生成
            self.spin_min.setValue(0)
            self.spin_max.setValue(0)
            self.combo_status.setCurrentIndex(0)
            return

        p = self.product
        self.edit_code.setText(p.product_code or "")
        self.edit_name.setText(p.product_name or "")
        self.edit_spec.setText(p.specification or "")
        if p.price is not None:
            self.spin_price.setValue(float(p.price))
        self.spin_min.setValue(p.min_stock)
        self.spin_max.setValue(p.max_stock)
        self.text_desc.setPlainText(p.description or "")
        # select category
        self._set_combo_by_data(self.combo_category, p.category_id)
        self._set_combo_by_data(self.combo_unit, p.unit_id)
        # 状态
        index = self.combo_status.findData(p.status)
        if index >= 0:
            self.combo_status.setCurrentIndex(index)

    @staticmethod
    def _set_combo_by_data(combo: QComboBox, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                break

    def _on_ok(self):
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "货品名称为必填项")
            self.edit_name.setFocus()
            return

        code = self.edit_code.text().strip() or None
        category_id = self.combo_category.currentData()
        unit_id = self.combo_unit.currentData()
        spec = self.edit_spec.text().strip() or None
        price_value = Decimal(str(self.spin_price.value())) if self.spin_price.value() > 0 else None
        min_stock = self.spin_min.value()
        max_stock = self.spin_max.value()
        status = self.combo_status.currentData()
        desc = self.text_desc.toPlainText().strip() or None

        if max_stock and min_stock > max_stock:
            QMessageBox.warning(self, "提示", "最低库存不能大于最高库存")
            return

        if self.product:
            p = self.product
            p.product_code = code or p.product_code
            p.product_name = name
            p.category_id = category_id
            p.unit_id = unit_id
            p.specification = spec
            p.price = price_value
            p.min_stock = min_stock
            p.max_stock = max_stock
            p.description = desc
            p.status = status
            try:
                self.service.update_product(p)
                QMessageBox.information(self, "成功", "更新成功")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
        else:
            p = Product(
                product_code=code,
                product_name=name,
                category_id=category_id,
                unit_id=unit_id,
                specification=spec,
                price=price_value,
                min_stock=min_stock,
                max_stock=max_stock,
                description=desc,
                status=status,
            )
            try:
                self.service.add_product(p)
                QMessageBox.information(self, "成功", "新增成功")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
