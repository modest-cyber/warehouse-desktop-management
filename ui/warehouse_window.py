# -*- coding: utf-8 -*-
"""仓库信息管理页面（PySide6）

需求参考：《PySide前端页面设计需求文档》7. 仓库信息管理页面
"""

from typing import List, Optional
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QTextEdit, QDoubleSpinBox
)

from service.warehouse_service import WarehouseService
from model.warehouse import Warehouse
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class WarehouseWindow(QWidget):
    """仓库信息管理页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = WarehouseService()
        self._init_ui()
        self.refresh_table()

    def _init_ui(self):
        self.setObjectName("WarehouseWindow")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        top_layout = QHBoxLayout()
        self.btn_add = QPushButton("新增(&N)")
        self.btn_edit = QPushButton("编辑(&E)")
        self.btn_delete = QPushButton("删除(&D)")
        self.btn_refresh = QPushButton("刷新(&R)")
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("仓库编码/名称 搜索…")
        self.btn_search = QPushButton("搜索(&F)")

        for btn in (self.btn_add, self.btn_edit, self.btn_delete, self.btn_refresh, self.btn_search):
            btn.setMinimumWidth(70)

        top_layout.addWidget(self.btn_add)
        top_layout.addWidget(self.btn_edit)
        top_layout.addWidget(self.btn_delete)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("搜索:"))
        top_layout.addWidget(self.edit_search)
        top_layout.addWidget(self.btn_search)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "仓库编码",
            "仓库名称",
            "地址",
            "负责人",
            "联系电话",
            "容量",
            "状态",
            "创建时间",
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table)

        self.btn_refresh.clicked.connect(self.refresh_table)
        self.btn_search.clicked.connect(self._on_search)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.table.cellDoubleClicked.connect(lambda *_: self._on_edit())

    def refresh_table(self):
        try:
            warehouses: List[Warehouse] = self.service.get_all_warehouse()
            keyword = self.edit_search.text().strip()
            if keyword:
                warehouses = [
                    w
                    for w in warehouses
                    if (w.warehouse_code and keyword in w.warehouse_code)
                    or (w.warehouse_name and keyword in w.warehouse_name)
                ]

            self.table.setRowCount(len(warehouses))
            for row, w in enumerate(warehouses):
                self.table.setItem(row, 0, QTableWidgetItem(str(w.id)))
                self.table.setItem(row, 1, QTableWidgetItem(w.warehouse_code or ""))
                self.table.setItem(row, 2, QTableWidgetItem(w.warehouse_name or ""))
                self.table.setItem(row, 3, QTableWidgetItem(w.address or ""))
                self.table.setItem(row, 4, QTableWidgetItem(w.manager or ""))
                self.table.setItem(row, 5, QTableWidgetItem(w.phone or ""))
                self.table.setItem(
                    row,
                    6,
                    QTableWidgetItem(str(float(w.capacity)) if w.capacity is not None else ""),
                )
                status_item = QTableWidgetItem("启用" if w.status == 1 else "禁用")
                status_item.setForeground(Qt.darkGreen if w.status == 1 else Qt.red)
                self.table.setItem(row, 7, status_item)
                self.table.setItem(
                    row,
                    8,
                    QTableWidgetItem(
                        w.create_time.strftime("%Y-%m-%d %H:%M:%S") if w.create_time else ""
                    ),
                )
        except Exception as e:
            logger.error(f"加载仓库数据失败: {e}")
            QMessageBox.critical(self, "错误", f"加载数据失败: {e}")

    def _get_selected_id(self) -> Optional[int]:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _on_search(self):
        self.refresh_table()

    def _on_add(self):
        dialog = WarehouseEditDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def _on_edit(self):
        wid = self._get_selected_id()
        if not wid:
            QMessageBox.information(self, "提示", "请先选择要编辑的记录")
            return
        warehouse = self.service.get_warehouse(wid)
        if not warehouse:
            QMessageBox.warning(self, "提示", "记录不存在或已被删除")
            self.refresh_table()
            return
        dialog = WarehouseEditDialog(warehouse=warehouse, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def _on_delete(self):
        wid = self._get_selected_id()
        if not wid:
            QMessageBox.information(self, "提示", "请先选择要删除的记录")
            return
        if QMessageBox.question(self, "确认删除", "确定要删除选中的仓库吗？") != QMessageBox.Yes:
            return
        try:
            self.service.delete_warehouse(wid)
            QMessageBox.information(self, "成功", "删除成功")
            self.refresh_table()
        except Exception as e:
            QMessageBox.warning(self, "警告", str(e))


class WarehouseEditDialog(QDialog):
    """新增/编辑 仓库 信息对话框"""

    def __init__(self, warehouse: Optional[Warehouse] = None, parent=None):
        super().__init__(parent)
        self.service = WarehouseService()
        self.warehouse = warehouse
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        self.setWindowTitle("仓库信息 - 新增" if not self.warehouse else "仓库信息 - 编辑")
        self.resize(480, 320)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.edit_code = QLineEdit(self)
        self.edit_name = QLineEdit(self)
        self.edit_address = QLineEdit(self)
        self.edit_manager = QLineEdit(self)
        self.edit_phone = QLineEdit(self)
        self.spin_capacity = QDoubleSpinBox(self)
        self.spin_capacity.setRange(0, 999999999)
        self.text_desc = QTextEdit(self)
        self.combo_status = QComboBox(self)
        self.combo_status.addItem("启用", 1)
        self.combo_status.addItem("禁用", 0)

        form.addRow("仓库编码:", self.edit_code)
        form.addRow("仓库名称:", self.edit_name)
        form.addRow("地址:", self.edit_address)
        form.addRow("负责人:", self.edit_manager)
        form.addRow("联系电话:", self.edit_phone)
        form.addRow("容量:", self.spin_capacity)
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

    def _load_data(self):
        if not self.warehouse:
            self.combo_status.setCurrentIndex(0)
            return
        w = self.warehouse
        self.edit_code.setText(w.warehouse_code or "")
        self.edit_name.setText(w.warehouse_name or "")
        self.edit_address.setText(w.address or "")
        self.edit_manager.setText(w.manager or "")
        self.edit_phone.setText(w.phone or "")
        if w.capacity is not None:
            self.spin_capacity.setValue(float(w.capacity))
        self.text_desc.setPlainText(w.description or "")
        idx = self.combo_status.findData(w.status)
        if idx >= 0:
            self.combo_status.setCurrentIndex(idx)

    def _on_ok(self):
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "仓库名称为必填项")
            self.edit_name.setFocus()
            return

        code = self.edit_code.text().strip() or None
        address = self.edit_address.text().strip() or None
        manager = self.edit_manager.text().strip() or None
        phone = self.edit_phone.text().strip() or None
        capacity = Decimal(str(self.spin_capacity.value())) if self.spin_capacity.value() > 0 else None
        desc = self.text_desc.toPlainText().strip() or None
        status = self.combo_status.currentData()

        if self.warehouse:
            w = self.warehouse
            w.warehouse_code = code or w.warehouse_code
            w.warehouse_name = name
            w.address = address
            w.manager = manager
            w.phone = phone
            w.capacity = capacity
            w.description = desc
            w.status = status
            try:
                self.service.update_warehouse(w)
                QMessageBox.information(self, "成功", "更新成功")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
        else:
            w = Warehouse(
                warehouse_code=code,
                warehouse_name=name,
                address=address,
                manager=manager,
                phone=phone,
                capacity=capacity,
                description=desc,
                status=status,
            )
            try:
                self.service.add_warehouse(w)
                QMessageBox.information(self, "成功", "新增成功")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
