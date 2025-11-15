# -*- coding: utf-8 -*-
"""基础信息管理页面（PySide6）

需求参考：《PySide前端页面设计需求文档》5. 基础信息管理页面
"""

from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox,
    QDialog, QTextEdit, QRadioButton, QButtonGroup, QFormLayout
)

from service.base_info_service import BaseInfoService
from model.base_info import BaseInfo
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class BaseInfoWindow(QWidget):
    """基础信息管理主页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = BaseInfoService()
        self.current_type = None
        self._init_ui()
        self._load_types()

    # ---------------- UI 构建 -----------------
    def _init_ui(self):
        self.setObjectName("BaseInfoWindow")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 顶部操作区域
        top_layout = QHBoxLayout()

        self.btn_add = QPushButton("新增(&N)")
        self.btn_edit = QPushButton("编辑(&E)")
        self.btn_delete = QPushButton("删除(&D)")
        self.btn_refresh = QPushButton("刷新(&R)")
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("编码/名称 模糊搜索…")
        self.btn_search = QPushButton("搜索(&F)")

        for btn in (self.btn_add, self.btn_edit, self.btn_delete, self.btn_refresh, self.btn_search):
            btn.setMinimumWidth(80)

        top_layout.addWidget(self.btn_add)
        top_layout.addWidget(self.btn_edit)
        top_layout.addWidget(self.btn_delete)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("快速搜索:"))
        top_layout.addWidget(self.edit_search)
        top_layout.addWidget(self.btn_search)

        # 中间：左侧类型选择 + 右侧表格
        middle_layout = QHBoxLayout()

        # 左侧类型
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("信息类型"))
        self.combo_type = QComboBox()
        left_layout.addWidget(self.combo_type)
        left_layout.addStretch()

        # 右侧表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "信息类型", "信息编码", "信息名称", "描述", "状态", "创建时间"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        middle_layout.addLayout(left_layout, 1)
        middle_layout.addWidget(self.table, 4)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)

        # 信号连接
        self.combo_type.currentIndexChanged.connect(self._on_type_changed)
        self.btn_refresh.clicked.connect(self.refresh_table)
        self.btn_search.clicked.connect(self._on_search)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.table.cellDoubleClicked.connect(lambda *_: self._on_edit())

        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            #BaseInfoWindow {
                background-color: #ffffff;
            }
            QTableWidget {
                gridline-color: #ddd;
            }
        """)

    # ------------- 数据加载 & 刷新 ----------------
    def _load_types(self):
        """预置常用类型，可根据需要扩展。"""
        # 这里直接写死几种常见类型，实际也可以从数据库 distinct(info_type) 查询
        types = [
            ("category", "类别"),
            ("unit", "单位"),
        ]
        self.combo_type.clear()
        for value, text in types:
            self.combo_type.addItem(text, value)
        if types:
            self.current_type = types[0][0]
            self.refresh_table()

    def _on_type_changed(self, index: int):
        self.current_type = self.combo_type.itemData(index)
        self.refresh_table()

    def refresh_table(self):
        """根据当前类型刷新表格"""
        try:
            if not self.current_type:
                return
            records: List[BaseInfo] = self.service.get_base_info_by_type(self.current_type)
            keyword = self.edit_search.text().strip()
            if keyword:
                records = [
                    r for r in records
                    if (r.info_code and keyword in r.info_code)
                    or (r.info_name and keyword in r.info_name)
                ]

            self.table.setRowCount(len(records))
            for row, item in enumerate(records):
                self.table.setItem(row, 0, QTableWidgetItem(str(item.id)))
                self.table.setItem(row, 1, QTableWidgetItem(item.info_type or ""))
                self.table.setItem(row, 2, QTableWidgetItem(item.info_code or ""))
                self.table.setItem(row, 3, QTableWidgetItem(item.info_name or ""))
                self.table.setItem(row, 4, QTableWidgetItem(item.description or ""))
                status_text = "启用" if item.status == 1 else "禁用"
                status_item = QTableWidgetItem(status_text)
                if item.status == 1:
                    status_item.setForeground(Qt.darkGreen)
                else:
                    status_item.setForeground(Qt.red)
                self.table.setItem(row, 5, status_item)
                self.table.setItem(
                    row,
                    6,
                    QTableWidgetItem(
                        item.create_time.strftime("%Y-%m-%d %H:%M:%S")
                        if item.create_time
                        else ""
                    ),
                )
        except Exception as e:
            logger.error(f"加载基础信息失败: {e}")
            QMessageBox.critical(self, "错误", f"加载数据失败: {e}")

    # ------------- 事件处理 -----------------
    def _get_selected_id(self) -> int:
        row = self.table.currentRow()
        if row < 0:
            return 0
        item = self.table.item(row, 0)
        return int(item.text()) if item else 0

    def _on_search(self):
        self.refresh_table()

    def _on_add(self):
        if not self.current_type:
            QMessageBox.warning(self, "提示", "请先选择信息类型")
            return
        dialog = BaseInfoEditDialog(self.current_type, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def _on_edit(self):
        id_ = self._get_selected_id()
        if not id_:
            QMessageBox.information(self, "提示", "请先选择要编辑的记录")
            return
        base_info = self.service.get_base_info(id_)
        if not base_info:
            QMessageBox.warning(self, "提示", "记录不存在或已被删除")
            self.refresh_table()
            return
        dialog = BaseInfoEditDialog(self.current_type, base_info=base_info, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def _on_delete(self):
        id_ = self._get_selected_id()
        if not id_:
            QMessageBox.information(self, "提示", "请先选择要删除的记录")
            return
        if QMessageBox.question(self, "确认删除", "确定要删除选中的基础信息吗？") != QMessageBox.Yes:
            return
        try:
            self.service.delete_base_info(id_)
            QMessageBox.information(self, "成功", "删除成功")
            self.refresh_table()
        except Exception as e:
            QMessageBox.warning(self, "警告", str(e))


class BaseInfoEditDialog(QDialog):
    """新增/编辑基础信息对话框"""

    def __init__(self, info_type: str, base_info: BaseInfo | None = None, parent=None):
        super().__init__(parent)
        self.service = BaseInfoService()
        self.info_type = info_type
        self.base_info = base_info
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        self.setWindowTitle("基础信息 - 新增" if not self.base_info else "基础信息 - 编辑")
        self.resize(420, 260)
        self.setModal(True)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # 信息类型只读
        self.edit_type = QLineEdit(self)
        self.edit_type.setReadOnly(True)

        self.edit_code = QLineEdit(self)
        self.edit_name = QLineEdit(self)
        self.text_desc = QTextEdit(self)

        # 状态单选
        self.radio_enabled = QRadioButton("启用")
        self.radio_disabled = QRadioButton("禁用")
        self.status_group = QButtonGroup(self)
        self.status_group.addButton(self.radio_enabled, 1)
        self.status_group.addButton(self.radio_disabled, 0)
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.radio_enabled)
        status_layout.addWidget(self.radio_disabled)

        form.addRow("信息类型:", self.edit_type)
        form.addRow("信息编码:", self.edit_code)
        form.addRow("信息名称:", self.edit_name)
        form.addRow("描述:", self.text_desc)
        form.addRow("状态:", status_layout)

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
        self.edit_type.setText(self.info_type)
        if self.base_info:
            self.edit_code.setText(self.base_info.info_code or "")
            self.edit_name.setText(self.base_info.info_name or "")
            self.text_desc.setPlainText(self.base_info.description or "")
            if self.base_info.status == 1:
                self.radio_enabled.setChecked(True)
            else:
                self.radio_disabled.setChecked(True)
        else:
            self.radio_enabled.setChecked(True)

    def _on_ok(self):
        info_name = self.edit_name.text().strip()
        if not info_name:
            QMessageBox.warning(self, "提示", "信息名称为必填项")
            self.edit_name.setFocus()
            return

        info_code = self.edit_code.text().strip() or None
        description = self.text_desc.toPlainText().strip() or None
        status = 1 if self.radio_enabled.isChecked() else 0

        if self.base_info:
            bi = self.base_info
            bi.info_name = info_name
            bi.info_code = info_code
            bi.description = description
            bi.status = status
            try:
                self.service.update_base_info(bi)
                QMessageBox.information(self, "成功", "更新成功")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
        else:
            bi = BaseInfo(
                info_type=self.info_type,
                info_name=info_name,
                info_code=info_code,
                description=description,
                status=status,
            )
            try:
                self.service.add_base_info(bi)
                QMessageBox.information(self, "成功", "新增成功")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
