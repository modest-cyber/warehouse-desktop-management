# -*- coding: utf-8 -*-
"""修改密码对话框（PySide6）

需求参考：《PySide前端页面设计需求文档》15. 修改密码页面
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QHBoxLayout, QMessageBox
)

from model.user import User
from service.user_service import UserService
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class ChangePasswordDialog(QDialog):
    """修改密码对话框"""

    def __init__(self, user: User, parent=None):
        super().__init__(parent)
        self.user = user
        self.service = UserService()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("修改密码")
        self.resize(350, 200)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.edit_old = QLineEdit(self)
        self.edit_old.setEchoMode(QLineEdit.Password)
        self.edit_new = QLineEdit(self)
        self.edit_new.setEchoMode(QLineEdit.Password)
        self.edit_confirm = QLineEdit(self)
        self.edit_confirm.setEchoMode(QLineEdit.Password)

        form.addRow("旧密码:", self.edit_old)
        form.addRow("新密码:", self.edit_new)
        form.addRow("确认新密码:", self.edit_confirm)
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

    def _on_ok(self):
        old = self.edit_old.text().strip()
        new = self.edit_new.text().strip()
        confirm = self.edit_confirm.text().strip()

        if not old:
            QMessageBox.warning(self, "提示", "请输入旧密码")
            self.edit_old.setFocus()
            return
        if not new:
            QMessageBox.warning(self, "提示", "请输入新密码")
            self.edit_new.setFocus()
            return
        if len(new) < 6:
            QMessageBox.warning(self, "提示", "新密码长度至少6位")
            self.edit_new.setFocus()
            return
        if new != confirm:
            QMessageBox.warning(self, "提示", "两次输入的新密码不一致")
            self.edit_confirm.setFocus()
            return

        try:
            self.service.change_password(self.user.id, old, new)
            QMessageBox.information(self, "成功", "密码修改成功，请妥善保管新密码")
            self.accept()
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            QMessageBox.critical(self, "错误", str(e))
