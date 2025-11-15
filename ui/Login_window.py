# -*- coding: utf-8 -*-
"""
登录窗口
"""
import sys
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap
from utils.logger import Logger
from service.user_service import UserService

logger = Logger.get_logger(__name__)

class LoginWindow(QDialog):
    """登录窗口"""
    
    def __init__(self):
        super().__init__()
        self.user_service = UserService()
        self.init_ui()
        self.setup_style()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("仓库货品管理系统 - 登录")
        self.setFixedSize(400, 300)
        self.setWindowModality(Qt.ApplicationModal)
        
        # 居中显示
        self.center_on_screen()
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title_label = QLabel("仓库货品管理系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("微软雅黑", 18, QFont.Bold)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 用户名输入
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        username_label.setFixedWidth(60)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        main_layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        password_label.setFixedWidth(60)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("请输入密码")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        main_layout.addLayout(password_layout)
        
        # 记住密码
        self.remember_checkbox = QCheckBox("记住密码")
        main_layout.addWidget(self.remember_checkbox)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setFixedHeight(40)
        self.login_button.clicked.connect(self.login)
        main_layout.addWidget(self.login_button)
        
        self.setLayout(main_layout)
        
        # 回车键登录
        self.password_input.returnPressed.connect(self.login)
        
        # 设置焦点
        self.username_input.setFocus()
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-family: "微软雅黑";
                font-size: 12px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #404040;
                border-radius: 4px;
                font-size: 12px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #0078d4;
                background-color: #333333;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QCheckBox {
                color: #cccccc;
                font-size: 12px;
            }
            QCheckBox::indicator {
                border: 1px solid #404040;
                background-color: #2d2d2d;
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
            }
        """)
        
    def center_on_screen(self):
        """窗口居中显示"""
        screen = self.screen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
        
    def login(self):
        """登录处理"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # 验证输入
        if not username:
            QMessageBox.warning(self, "警告", "请输入用户名")
            self.username_input.setFocus()
            return
            
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            self.password_input.setFocus()
            return
            
        try:
            # 验证用户（调用 UserService.login）
            user = self.user_service.login(username, password)
            if user:
                logger.info(f"用户 {username} 登录成功")
                QMessageBox.information(self, "成功", "登录成功")

                # 记住密码处理（占位，后续可实现本地加密存储）
                if self.remember_checkbox.isChecked():
                    # TODO: 实现记住密码功能（加密本地存储账号信息）
                    pass

                self.user = user
                self.accept()  # 关闭对话框，返回QDialog.Accepted
            else:
                logger.warning(f"用户 {username} 登录失败")
                QMessageBox.critical(self, "错误", "用户名或密码错误")
                self.password_input.clear()
                self.password_input.setFocus()

        except Exception as e:
            logger.error(f"登录过程中发生错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"登录失败: {str(e)}")
            
    def get_user(self):
        """获取登录用户信息"""
        return getattr(self, 'user', None)