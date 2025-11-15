# -*- coding: utf-8 -*-
"""用户管理页面（PySide6）

需求参考：《PySide前端页面设计需求文档》14. 用户管理页面
"""

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QComboBox
)

from service.user_service import UserService
from model.user import User
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class UserManagementWindow(QWidget):
    """用户管理页面"""

    def __init__(self, current_user: User, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.service = UserService()
        self._init_ui()
        self.refresh_table()

    def _init_ui(self):
        self.setObjectName("UserManagementWindow")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        top_layout = QHBoxLayout()
        self.btn_add = QPushButton("新增(&N)")
        self.btn_edit = QPushButton("编辑(&E)")
        self.btn_delete = QPushButton("删除(&D)")
        self.btn_refresh = QPushButton("刷新(&R)")
        self.btn_reset_pwd = QPushButton("重置密码")
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("用户名/姓名 搜索…")
        self.btn_search = QPushButton("搜索(&F)")

        for btn in (self.btn_add, self.btn_edit, self.btn_delete, self.btn_refresh, self.btn_reset_pwd, self.btn_search):
            btn.setMinimumWidth(80)

        top_layout.addWidget(self.btn_add)
        top_layout.addWidget(self.btn_edit)
        top_layout.addWidget(self.btn_delete)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addWidget(self.btn_reset_pwd)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("搜索:"))
        top_layout.addWidget(self.edit_search)
        top_layout.addWidget(self.btn_search)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "用户名",
            "真实姓名",
            "角色",
            "状态",
            "创建时间",
            "更新时间",
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
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
        self.btn_reset_pwd.clicked.connect(self._on_reset_pwd)
        self.table.cellDoubleClicked.connect(lambda *_: self._on_edit())

    def _get_selected_id(self) -> Optional[int]:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def refresh_table(self):
        try:
            users: List[User] = self.service.get_all_users()
            keyword = self.edit_search.text().strip()
            if keyword:
                users = [u for u in users if keyword in (u.username or "") or keyword in (u.real_name or "")]

            self.table.setRowCount(len(users))
            for row, u in enumerate(users):
                self.table.setItem(row, 0, QTableWidgetItem(str(u.id)))
                self.table.setItem(row, 1, QTableWidgetItem(u.username or ""))
                self.table.setItem(row, 2, QTableWidgetItem(u.real_name or ""))
                self.table.setItem(row, 3, QTableWidgetItem(u.role or ""))
                status_item = QTableWidgetItem("启用" if u.status == 1 else "禁用")
                status_item.setForeground(Qt.darkGreen if u.status == 1 else Qt.red)
                self.table.setItem(row, 4, status_item)
                self.table.setItem(
                    row,
                    5,
                    QTableWidgetItem(u.create_time.strftime("%Y-%m-%d %H:%M:%S") if u.create_time else ""),
                )
                self.table.setItem(
                    row,
                    6,
                    QTableWidgetItem(u.update_time.strftime("%Y-%m-%d %H:%M:%S") if u.update_time else ""),
                )
        except Exception as e:
            logger.error(f"加载用户数据失败: {e}")
            QMessageBox.critical(self, "错误", f"加载数据失败: {e}")

    def _on_search(self):
        self.refresh_table()

    def _on_add(self):
        dialog = UserEditDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def _on_edit(self):
        uid = self._get_selected_id()
        if not uid:
            QMessageBox.information(self, "提示", "请先选择要编辑的用户")
            return
        user = self.service.get_user(uid)
        if not user:
            QMessageBox.warning(self, "提示", "用户不存在或已被删除")
            self.refresh_table()
            return
        dialog = UserEditDialog(user=user, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def _on_delete(self):
        uid = self._get_selected_id()
        if not uid:
            QMessageBox.information(self, "提示", "请先选择要删除的用户")
            return
        if QMessageBox.question(self, "确认删除", "确定要删除选中的用户吗？") != QMessageBox.Yes:
            return
        try:
            self.service.delete_user(uid, current_user_id=self.current_user.id)
            QMessageBox.information(self, "成功", "删除成功")
            self.refresh_table()
        except Exception as e:
            QMessageBox.warning(self, "警告", str(e))

    def _on_reset_pwd(self):
        uid = self._get_selected_id()
        if not uid:
            QMessageBox.information(self, "提示", "请先选择要重置密码的用户")
            return
        if QMessageBox.question(self, "确认重置", "确定要重置该用户密码吗？") != QMessageBox.Yes:
            return
        from PySide6.QtWidgets import QInputDialog
        new_pwd, ok = QInputDialog.getText(self, "重置密码", "请输入新密码:")
        if not ok:
            return
        new_pwd = new_pwd.strip()
        if len(new_pwd) < 6:
            QMessageBox.warning(self, "提示", "新密码长度至少6位")
            return
        try:
            self.service.reset_password(uid, new_pwd)
            QMessageBox.information(self, "成功", "密码重置成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))


class UserEditDialog(QDialog):
    """新增/编辑用户对话框"""

    def __init__(self, user: Optional[User] = None, parent=None):
        super().__init__(parent)
        self.service = UserService()
        self.user = user
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        self.setWindowTitle("用户 - 新增" if not self.user else "用户 - 编辑")
        self.resize(400, 260)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.edit_username = QLineEdit(self)
        self.edit_password = QLineEdit(self)
        self.edit_password.setEchoMode(QLineEdit.Password)
        self.edit_realname = QLineEdit(self)
        self.combo_role = QComboBox(self)
        self.combo_role.addItem("admin", "admin")
        self.combo_status = QComboBox(self)
        self.combo_status.addItem("启用", 1)
        self.combo_status.addItem("禁用", 0)

        form.addRow("用户名:", self.edit_username)
        form.addRow("密码:", self.edit_password)
        form.addRow("真实姓名:", self.edit_realname)
        form.addRow("角色:", self.combo_role)
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
        if not self.user:
            # 新增时默认启用
            self.combo_status.setCurrentIndex(0)
            return
        u = self.user
        self.edit_username.setText(u.username or "")
        self.edit_realname.setText(u.real_name or "")
        idx = self.combo_role.findData(u.role)
        if idx >= 0:
            self.combo_role.setCurrentIndex(idx)
        idx = self.combo_status.findData(u.status)
        if idx >= 0:
            self.combo_status.setCurrentIndex(idx)
        # 编辑时密码不可修改
        self.edit_password.setPlaceholderText("编辑时密码不可修改")
        self.edit_password.setEnabled(False)

    def _on_ok(self):
        username = self.edit_username.text().strip()
        if not username:
            QMessageBox.warning(self, "提示", "用户名不能为空")
            self.edit_username.setFocus()
            return

        real_name = self.edit_realname.text().strip() or None
        role = self.combo_role.currentData()
        status = self.combo_status.currentData()

        if self.user:
            u = self.user
            u.username = username
            u.real_name = real_name
            u.role = role
            u.status = status
            try:
                self.service.update_user(u)
                QMessageBox.information(self, "成功", "更新成功")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
        else:
            password = self.edit_password.text().strip()
            if not password:
                QMessageBox.warning(self, "提示", "新增用户时密码必填")
                self.edit_password.setFocus()
                return
            if len(password) < 6:
                QMessageBox.warning(self, "提示", "密码长度至少6位")
                return
            u = User(
                username=username,
                password=password,
                real_name=real_name,
                role=role,
                status=status,
            )
            try:
                self.service.add_user(u)
                QMessageBox.information(self, "成功", "新增成功")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
