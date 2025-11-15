# -*- coding: utf-8 -*-
"""供应商/客户信息管理页面（PySide6）

需求参考：《PySide前端页面设计需求文档》8. 供应商/客户信息管理页面
"""

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QTextEdit, QComboBox
)

from service.supplier_client_service import SupplierClientService
from model.supplier_client import SupplierClient
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class SupplierClientWindow(QWidget):
    """供应商/客户信息管理页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = SupplierClientService()
        self.current_type_filter: Optional[int] = None
        self._init_ui()
        self.refresh_table()

    def _init_ui(self):
        self.setObjectName("SupplierClientWindow")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 顶部操作
        top_layout = QHBoxLayout()
        self.btn_add = QPushButton("新增(&N)")
        self.btn_edit = QPushButton("编辑(&E)")
        self.btn_delete = QPushButton("删除(&D)")
        self.btn_refresh = QPushButton("刷新(&R)")
        self.btn_filter_all = QPushButton("全部")
        self.btn_filter_supplier = QPushButton("供应商")
        self.btn_filter_client = QPushButton("客户")
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("编码/名称 搜索…")
        self.btn_search = QPushButton("搜索(&F)")

        for btn in (
            self.btn_add,
            self.btn_edit,
            self.btn_delete,
            self.btn_refresh,
            self.btn_filter_all,
            self.btn_filter_supplier,
            self.btn_filter_client,
            self.btn_search,
        ):
            btn.setMinimumWidth(70)

        top_layout.addWidget(self.btn_add)
        top_layout.addWidget(self.btn_edit)
        top_layout.addWidget(self.btn_delete)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_filter_all)
        top_layout.addWidget(self.btn_filter_supplier)
        top_layout.addWidget(self.btn_filter_client)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("搜索:"))
        top_layout.addWidget(self.edit_search)
        top_layout.addWidget(self.btn_search)

        # 中间表格
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "编码",
            "名称",
            "类型",
            "联系人",
            "联系电话",
            "邮箱",
            "地址",
            "状态",
            "创建时间",
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
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
        self.btn_filter_all.clicked.connect(lambda: self._set_type_filter(None))
        self.btn_filter_supplier.clicked.connect(lambda: self._set_type_filter(1))
        self.btn_filter_client.clicked.connect(lambda: self._set_type_filter(2))
        self.table.cellDoubleClicked.connect(lambda *_: self._on_edit())

    def _set_type_filter(self, t: Optional[int]):
        self.current_type_filter = t
        self.refresh_table()

    def refresh_table(self):
        try:
            records: List[SupplierClient] = self.service.get_all_supplier_client()
            if self.current_type_filter:
                records = [r for r in records if r.type == self.current_type_filter]

            keyword = self.edit_search.text().strip()
            if keyword:
                records = [
                    r
                    for r in records
                    if (r.code and keyword in r.code)
                    or (r.name and keyword in r.name)
                ]

            self.table.setRowCount(len(records))
            for row, r in enumerate(records):
                self.table.setItem(row, 0, QTableWidgetItem(str(r.id)))
                self.table.setItem(row, 1, QTableWidgetItem(r.code or ""))
                self.table.setItem(row, 2, QTableWidgetItem(r.name or ""))
                type_text = "供应商" if r.type == 1 else "客户"
                self.table.setItem(row, 3, QTableWidgetItem(type_text))
                self.table.setItem(row, 4, QTableWidgetItem(r.contact_person or ""))
                self.table.setItem(row, 5, QTableWidgetItem(r.phone or ""))
                self.table.setItem(row, 6, QTableWidgetItem(r.email or ""))
                self.table.setItem(row, 7, QTableWidgetItem(r.address or ""))
                status_item = QTableWidgetItem("启用" if r.status == 1 else "禁用")
                status_item.setForeground(Qt.darkGreen if r.status == 1 else Qt.red)
                self.table.setItem(row, 8, status_item)
                self.table.setItem(
                    row,
                    9,
                    QTableWidgetItem(
                        r.create_time.strftime("%Y-%m-%d %H:%M:%S") if r.create_time else ""
                    ),
                )
        except Exception as e:
            logger.error(f"加载供应商/客户数据失败: {e}")
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
        dialog = SupplierClientEditDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def _on_edit(self):
        sid = self._get_selected_id()
        if not sid:
            QMessageBox.information(self, "提示", "请先选择要编辑的记录")
            return
        record = self.service.get_supplier_client(sid)
        if not record:
            QMessageBox.warning(self, "提示", "记录不存在或已被删除")
            self.refresh_table()
            return
        dialog = SupplierClientEditDialog(record=record, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def _on_delete(self):
        sid = self._get_selected_id()
        if not sid:
            QMessageBox.information(self, "提示", "请先选择要删除的记录")
            return
        if QMessageBox.question(self, "确认删除", "确定要删除选中的记录吗？") != QMessageBox.Yes:
            return
        try:
            self.service.delete_supplier_client(sid)
            QMessageBox.information(self, "成功", "删除成功")
            self.refresh_table()
        except Exception as e:
            QMessageBox.warning(self, "警告", str(e))


class SupplierClientEditDialog(QDialog):
    """新增/编辑 供应商/客户 对话框"""

    def __init__(self, record: Optional[SupplierClient] = None, parent=None):
        super().__init__(parent)
        self.service = SupplierClientService()
        self.record = record
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        self.setWindowTitle("供应商/客户 - 新增" if not self.record else "供应商/客户 - 编辑")
        self.resize(480, 320)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.combo_type = QComboBox(self)
        self.combo_type.addItem("供应商", 1)
        self.combo_type.addItem("客户", 2)
        self.edit_code = QLineEdit(self)
        self.edit_name = QLineEdit(self)
        self.edit_contact = QLineEdit(self)
        self.edit_phone = QLineEdit(self)
        self.edit_email = QLineEdit(self)
        self.edit_address = QLineEdit(self)
        self.text_desc = QTextEdit(self)
        self.combo_status = QComboBox(self)
        self.combo_status.addItem("启用", 1)
        self.combo_status.addItem("禁用", 0)

        form.addRow("类型:", self.combo_type)
        form.addRow("编码:", self.edit_code)
        form.addRow("名称:", self.edit_name)
        form.addRow("联系人:", self.edit_contact)
        form.addRow("联系电话:", self.edit_phone)
        form.addRow("邮箱:", self.edit_email)
        form.addRow("地址:", self.edit_address)
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
        if not self.record:
            self.combo_status.setCurrentIndex(0)
            return
        r = self.record
        idx_type = self.combo_type.findData(r.type)
        if idx_type >= 0:
            self.combo_type.setCurrentIndex(idx_type)
        self.edit_code.setText(r.code or "")
        self.edit_name.setText(r.name or "")
        self.edit_contact.setText(r.contact_person or "")
        self.edit_phone.setText(r.phone or "")
        self.edit_email.setText(r.email or "")
        self.edit_address.setText(r.address or "")
        self.text_desc.setPlainText(r.description or "")
        idx_status = self.combo_status.findData(r.status)
        if idx_status >= 0:
            self.combo_status.setCurrentIndex(idx_status)

    def _on_ok(self):
        t = self.combo_type.currentData()
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "名称为必填项")
            self.edit_name.setFocus()
            return

        code = self.edit_code.text().strip() or None
        contact = self.edit_contact.text().strip() or None
        phone = self.edit_phone.text().strip() or None
        email = self.edit_email.text().strip() or None
        address = self.edit_address.text().strip() or None
        desc = self.text_desc.toPlainText().strip() or None
        status = self.combo_status.currentData()

        if self.record:
            r = self.record
            r.type = t
            r.code = code or r.code
            r.name = name
            r.contact_person = contact
            r.phone = phone
            r.email = email
            r.address = address
            r.description = desc
            r.status = status
            try:
                self.service.update_supplier_client(r)
                QMessageBox.information(self, "成功", "更新成功")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
        else:
            r = SupplierClient(
                type=t,
                code=code,
                name=name,
                contact_person=contact,
                phone=phone,
                email=email,
                address=address,
                description=desc,
                status=status,
            )
            try:
                self.service.add_supplier_client(r)
                QMessageBox.information(self, "成功", "新增成功")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
