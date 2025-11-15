# -*- coding: utf-8 -*-
"""系统设置页面（PySide6）

需求参考：《PySide前端页面设计需求文档》16. 系统设置页面

说明：
- 数据库设置：当前实现支持查看和修改内存中的 DB_CONFIG，并测试连接；配置文件持久化需后续扩展。
- 系统参数、界面设置：提供基本 UI 及内存级别设置示例。
"""

from typing import Dict, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTabWidget, QMessageBox, QComboBox, QSpinBox
)

from service.system_service import SystemService
from config.database import get_db_config, DB_CONFIG
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class SettingsWindow(QWidget):
    """系统设置页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.system_service = SystemService()
        self._init_ui()
        self._load_db_config()

    def _init_ui(self):
        self.setObjectName("SettingsWindow")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        self.tabs = QTabWidget(self)
        main_layout.addWidget(self.tabs)

        # --- 数据库设置 Tab ---
        db_tab = QWidget()
        db_layout = QVBoxLayout(db_tab)

        form_rows = []
        def add_row(label_text: str, widget):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(80)
            row.addWidget(lbl)
            row.addWidget(widget)
            db_layout.addLayout(row)
            form_rows.append((lbl, widget))

        self.edit_host = QLineEdit()
        self.edit_port = QLineEdit()
        self.edit_user = QLineEdit()
        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.Password)
        self.edit_database = QLineEdit()
        self.edit_charset = QLineEdit()

        add_row("主机:", self.edit_host)
        add_row("端口:", self.edit_port)
        add_row("用户名:", self.edit_user)
        add_row("密码:", self.edit_password)
        add_row("数据库:", self.edit_database)
        add_row("字符集:", self.edit_charset)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_test_conn = QPushButton("测试连接")
        self.btn_save_db = QPushButton("保存配置")
        btn_row.addWidget(self.btn_test_conn)
        btn_row.addWidget(self.btn_save_db)
        db_layout.addLayout(btn_row)

        self.tabs.addTab(db_tab, "数据库设置")

        # --- 系统参数 Tab ---
        sys_tab = QWidget()
        sys_layout = QVBoxLayout(sys_tab)
        sys_layout.addWidget(QLabel("系统参数（示例占位，需结合业务扩展持久化配置）"))

        row_warn = QHBoxLayout()
        row_warn.addWidget(QLabel("默认低库存系数:"))
        self.spin_low_factor = QSpinBox()
        self.spin_low_factor.setRange(50, 100)
        self.spin_low_factor.setValue(100)
        row_warn.addWidget(self.spin_low_factor)
        row_warn.addStretch()
        sys_layout.addLayout(row_warn)

        row_backup = QHBoxLayout()
        row_backup.addWidget(QLabel("数据备份路径:"))
        self.edit_backup_path = QLineEdit()
        row_backup.addWidget(self.edit_backup_path)
        btn_choose_backup = QPushButton("选择…")
        row_backup.addWidget(btn_choose_backup)
        sys_layout.addLayout(row_backup)

        btn_sys_row = QHBoxLayout()
        btn_sys_row.addStretch()
        self.btn_save_sys = QPushButton("保存参数")
        btn_sys_row.addWidget(self.btn_save_sys)
        sys_layout.addLayout(btn_sys_row)

        self.tabs.addTab(sys_tab, "系统参数")

        # --- 界面设置 Tab ---
        ui_tab = QWidget()
        ui_layout = QVBoxLayout(ui_tab)

        row_theme = QHBoxLayout()
        row_theme.addWidget(QLabel("主题:"))
        self.combo_theme = QComboBox()
        self.combo_theme.addItem("浅色", "light")
        self.combo_theme.addItem("深色", "dark")
        row_theme.addWidget(self.combo_theme)
        row_theme.addStretch()
        ui_layout.addLayout(row_theme)

        row_font = QHBoxLayout()
        row_font.addWidget(QLabel("字体大小:"))
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(10, 20)
        self.spin_font_size.setValue(12)
        row_font.addWidget(self.spin_font_size)
        row_font.addStretch()
        ui_layout.addLayout(row_font)

        row_lang = QHBoxLayout()
        row_lang.addWidget(QLabel("语言:"))
        self.combo_lang = QComboBox()
        self.combo_lang.addItem("中文", "zh")
        self.combo_lang.addItem("English", "en")
        row_lang.addWidget(self.combo_lang)
        row_lang.addStretch()
        ui_layout.addLayout(row_lang)

        btn_ui_row = QHBoxLayout()
        btn_ui_row.addStretch()
        self.btn_apply_ui = QPushButton("应用")
        btn_ui_row.addWidget(self.btn_apply_ui)
        ui_layout.addLayout(btn_ui_row)

        self.tabs.addTab(ui_tab, "界面设置")

        # 信号
        self.btn_test_conn.clicked.connect(self._on_test_connection)
        self.btn_save_db.clicked.connect(self._on_save_db)
        self.btn_save_sys.clicked.connect(self._on_save_sys)
        self.btn_apply_ui.clicked.connect(self._on_apply_ui)

    def _load_db_config(self):
        try:
            cfg = get_db_config()
            self.edit_host.setText(str(cfg.get("host", "")))
            self.edit_port.setText(str(cfg.get("port", "")))
            self.edit_user.setText(str(cfg.get("user", "")))
            self.edit_password.setText(str(cfg.get("password", "")))
            self.edit_database.setText(str(cfg.get("database", "")))
            self.edit_charset.setText(str(cfg.get("charset", "")))
        except Exception as e:
            logger.error(f"加载数据库配置失败: {e}")

    def _collect_db_config(self) -> Dict[str, Any]:
        cfg: Dict[str, Any] = {}
        cfg["host"] = self.edit_host.text().strip()
        cfg["port"] = int(self.edit_port.text().strip() or 0)
        cfg["user"] = self.edit_user.text().strip()
        cfg["password"] = self.edit_password.text().strip()
        cfg["database"] = self.edit_database.text().strip()
        cfg["charset"] = self.edit_charset.text().strip() or "utf8mb4"
        return cfg

    # ------- 数据库设置操作 -------
    def _on_test_connection(self):
        try:
            # 使用当前表单中的配置临时更新 DB_CONFIG
            cfg = self._collect_db_config()
            DB_CONFIG.update(cfg)
            ok = self.system_service.check_database_connection()
            if ok:
                QMessageBox.information(self, "成功", "数据库连接成功")
            else:
                QMessageBox.warning(self, "警告", "数据库连接失败，请检查配置")
        except Exception as e:
            logger.error(f"测试数据库连接失败: {e}")
            QMessageBox.critical(self, "错误", f"测试连接失败: {e}")

    def _on_save_db(self):
        try:
            cfg = self._collect_db_config()
            DB_CONFIG.update(cfg)
            QMessageBox.information(self, "成功", "数据库配置已更新（当前运行有效，重启后需重新加载或实现持久化）")
        except Exception as e:
            logger.error(f"保存数据库配置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    # ------- 系统参数操作（示例） -------
    def _on_save_sys(self):
        # 当前仅做示例，不做持久化
        low_factor = self.spin_low_factor.value()
        backup_path = self.edit_backup_path.text().strip()
        logger.info(f"系统参数更新: low_factor={low_factor}, backup_path={backup_path}")
        QMessageBox.information(self, "成功", "系统参数已保存（示例，未做持久化）")

    # ------- 界面设置操作 -------
    def _on_apply_ui(self):
        theme = self.combo_theme.currentData()
        font_size = self.spin_font_size.value()
        # 简单应用字体大小
        self.setStyleSheet(f"font-size: {font_size}px;")
        # 主题切换示例
        if theme == "dark":
            self.window().setStyleSheet("background-color: #303030; color: #ffffff;")
        else:
            self.window().setStyleSheet("")
        QMessageBox.information(self, "成功", "界面设置已应用（仅当前会话有效）")
