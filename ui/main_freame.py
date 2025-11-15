# -*- coding: utf-8 -*-
"""
主窗口
"""
import sys
from datetime import datetime
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QMenuBar, QToolBar, QStatusBar, QTabWidget, 
                             QLabel, QMessageBox, QSplitter)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QFont
from utils.logger import Logger

logger = Logger.get_logger(__name__)

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_style()
        self.setup_timer()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("仓库货品管理系统")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # 中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # 标签页容器
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        main_layout.addWidget(self.tab_widget)
        
        # 显示欢迎页面
        self.show_welcome_page()
        
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 基础数据菜单
        base_data_menu = menubar.addMenu('基础数据(&B)')
        
        base_info_action = QAction('基础信息管理(&I)', self)
        base_info_action.triggered.connect(lambda: self.open_tab('base_info', '基础信息管理'))
        base_data_menu.addAction(base_info_action)
        
        product_action = QAction('货品信息管理(&P)', self)
        product_action.triggered.connect(lambda: self.open_tab('product', '货品信息管理'))
        base_data_menu.addAction(product_action)
        
        warehouse_action = QAction('仓库信息管理(&W)', self)
        warehouse_action.triggered.connect(lambda: self.open_tab('warehouse', '仓库信息管理'))
        base_data_menu.addAction(warehouse_action)
        
        supplier_client_action = QAction('供应商/客户管理(&S)', self)
        supplier_client_action.triggered.connect(lambda: self.open_tab('supplier_client', '供应商/客户管理'))
        base_data_menu.addAction(supplier_client_action)
        
        # 业务操作菜单
        business_menu = menubar.addMenu('业务操作(&O)')
        
        stock_in_action = QAction('入库管理(&I)', self)
        stock_in_action.triggered.connect(lambda: self.open_tab('stock_in', '入库管理'))
        business_menu.addAction(stock_in_action)
        
        stock_out_action = QAction('出库管理(&O)', self)
        stock_out_action.triggered.connect(lambda: self.open_tab('stock_out', '出库管理'))
        business_menu.addAction(stock_out_action)
        
        inventory_action = QAction('库存查询(&V)', self)
        inventory_action.triggered.connect(lambda: self.open_tab('inventory', '库存查询'))
        business_menu.addAction(inventory_action)
        
        # 查询统计菜单
        query_menu = menubar.addMenu('查询统计(&Q)')
        
        record_query_action = QAction('出入库记录查询(&R)', self)
        record_query_action.triggered.connect(lambda: self.open_tab('record_query', '出入库记录查询'))
        query_menu.addAction(record_query_action)
        
        statistics_action = QAction('库存统计(&S)', self)
        statistics_action.triggered.connect(lambda: self.open_tab('statistics', '库存统计'))
        query_menu.addAction(statistics_action)
        
        export_action = QAction('数据导出(&E)', self)
        export_action.triggered.connect(self.export_data)
        query_menu.addAction(export_action)
        
        # 系统管理菜单
        system_menu = menubar.addMenu('系统管理(&S)')
        
        user_management_action = QAction('用户管理(&U)', self)
        user_management_action.triggered.connect(lambda: self.open_tab('user_management', '用户管理'))
        system_menu.addAction(user_management_action)
        
        change_password_action = QAction('修改密码(&C)', self)
        change_password_action.triggered.connect(self.change_password)
        system_menu.addAction(change_password_action)
        
        settings_action = QAction('系统设置(&S)', self)
        settings_action.triggered.connect(lambda: self.open_tab('settings', '系统设置'))
        system_menu.addAction(settings_action)
        
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        system_menu.addAction(about_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        manual_action = QAction('使用说明(&M)', self)
        manual_action.triggered.connect(self.show_manual)
        help_menu.addAction(manual_action)
        
        shortcuts_action = QAction('快捷键(&K)', self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 入库按钮
        stock_in_action = QAction('入库', self)
        stock_in_action.triggered.connect(lambda: self.open_tab('stock_in', '入库管理'))
        toolbar.addAction(stock_in_action)
        
        # 出库按钮
        stock_out_action = QAction('出库', self)
        stock_out_action.triggered.connect(lambda: self.open_tab('stock_out', '出库管理'))
        toolbar.addAction(stock_out_action)
        
        toolbar.addSeparator()
        
        # 库存查询按钮
        inventory_action = QAction('库存查询', self)
        inventory_action.triggered.connect(lambda: self.open_tab('inventory', '库存查询'))
        toolbar.addAction(inventory_action)
        
        # 出入库记录查询按钮
        record_query_action = QAction('出入库记录', self)
        record_query_action.triggered.connect(lambda: self.open_tab('record_query', '出入库记录查询'))
        toolbar.addAction(record_query_action)
        
        toolbar.addSeparator()
        
        # 用户管理按钮
        user_management_action = QAction('用户管理', self)
        user_management_action.triggered.connect(lambda: self.open_tab('user_management', '用户管理'))
        toolbar.addAction(user_management_action)
        
        toolbar.addSeparator()
        
        # 退出按钮
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        toolbar.addAction(exit_action)
        
    def setup_statusbar(self):
        """设置状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # 左侧：当前用户信息
        self.user_label = QLabel(f"用户: {self.user.real_name} ({self.user.role})")
        self.statusbar.addWidget(self.user_label)
        
        # 中间：系统时间
        self.time_label = QLabel()
        self.statusbar.addPermanentWidget(self.time_label)
        
        # 右侧：数据库连接状态
        self.db_status_label = QLabel()
        self.db_status_label.setStyleSheet("color: green;")
        self.db_status_label.setText("数据库: 已连接")
        self.statusbar.addPermanentWidget(self.db_status_label)
        
    def setup_timer(self):
        """设置定时器"""
        # 更新时间显示
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 每秒更新一次
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-bottom: 1px solid #404040;
            }
            QMenuBar::item {
                padding: 5px 10px;
                background-color: transparent;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #404040;
                color: #ffffff;
            }
            QToolBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-bottom: 1px solid #404040;
                spacing: 3px;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
                border-bottom: 2px solid #0078d4;
            }
            QStatusBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-top: 1px solid #404040;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #555555;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #0078d4;
                color: #ffffff;
            }
        """)
        
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"时间: {current_time}")
        
    def show_welcome_page(self):
        """显示欢迎页面"""
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)
        
        # 欢迎标题
        welcome_label = QLabel("欢迎使用仓库货品管理系统")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_font = QFont("微软雅黑", 24, QFont.Bold)
        welcome_label.setFont(welcome_font)
        welcome_label.setStyleSheet("color: #0078d4; margin: 50px; background-color: #1e1e1e;")
        layout.addWidget(welcome_label)
        
        # 用户信息
        user_info_label = QLabel(f"当前用户: {self.user.real_name} ({self.user.role})")
        user_info_label.setAlignment(Qt.AlignCenter)
        user_info_font = QFont("微软雅黑", 14)
        user_info_label.setFont(user_info_font)
        user_info_label.setStyleSheet("color: #cccccc; margin: 20px; background-color: #1e1e1e;")
        layout.addWidget(user_info_label)
        
        # 使用提示
        tips_label = QLabel("请从菜单栏或工具栏选择功能模块")
        tips_label.setAlignment(Qt.AlignCenter)
        tips_font = QFont("微软雅黑", 12)
        tips_label.setFont(tips_font)
        tips_label.setStyleSheet("color: #999999; margin: 20px; background-color: #1e1e1e;")
        layout.addWidget(tips_label)
        
        layout.addStretch()
        
        self.tab_widget.addTab(welcome_widget, "欢迎")
        
    def open_tab(self, tab_type, title):
        """打开标签页"""
        # 检查是否已经打开该标签页
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == title:
                self.tab_widget.setCurrentIndex(i)
                return
                
        try:
            # 动态导入相应的页面模块
            if tab_type == 'base_info':
                from .base_info_window import BaseInfoWindow
                widget = BaseInfoWindow()
            elif tab_type == 'product':
                from .product_window import ProductWindow
                widget = ProductWindow()
            elif tab_type == 'warehouse':
                from .warehouse_window import WarehouseWindow
                widget = WarehouseWindow()
            elif tab_type == 'supplier_client':
                from .supplier_client_window import SupplierClientWindow
                widget = SupplierClientWindow()
            elif tab_type == 'stock_in':
                from .stock_in_window import StockInWindow
                widget = StockInWindow(operator=self.user.username)
            elif tab_type == 'stock_out':
                from .stock_out_window import StockOutWindow
                widget = StockOutWindow(operator=self.user.username)
            elif tab_type == 'inventory':
                from .inventory_window import InventoryWindow
                widget = InventoryWindow()
            elif tab_type == 'record_query':
                from .record_query_window import RecordQueryWindow
                widget = RecordQueryWindow()
            elif tab_type == 'statistics':
                from .statistics_window import StatisticsWindow
                widget = StatisticsWindow()
            elif tab_type == 'user_management':
                from .user_management_window import UserManagementWindow
                widget = UserManagementWindow(self.user)
            elif tab_type == 'settings':
                from .settings_window import SettingsWindow
                widget = SettingsWindow()
            else:
                logger.warning(f"未知的标签页类型: {tab_type}")
                return
                
            self.tab_widget.addTab(widget, title)
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
            
        except ImportError as e:
            logger.error(f"导入模块失败: {str(e)}")
            QMessageBox.warning(self, "警告", f"该功能模块尚未实现: {title}")
        except Exception as e:
            logger.error(f"打开标签页失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"打开页面失败: {str(e)}")
            
    def close_tab(self, index):
        """关闭标签页"""
        # 不允许关闭欢迎页面
        if self.tab_widget.tabText(index) == "欢迎":
            return
            
        self.tab_widget.removeTab(index)
        
    def change_password(self):
        """修改密码"""
        from .change_password_dialog import ChangePasswordDialog
        dialog = ChangePasswordDialog(self.user, self)
        dialog.exec()
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "仓库货品管理系统\n"
                         "版本: 1.0.0\n"
                         "开发语言: Python\n"
                         "GUI框架: PySide6\n"
                         "数据库: MySQL")
        
    def show_manual(self):
        """显示使用说明"""
        QMessageBox.information(self, "使用说明", 
                              "1. 通过菜单栏或工具栏访问各功能模块\n"
                              "2. 支持多标签页同时打开\n"
                              "3. 使用快捷键提高操作效率\n"
                              "4. 详细操作请参考各模块的帮助文档")
        
    def show_shortcuts(self):
        """显示快捷键"""
        shortcuts_text = """
        常用快捷键:
        Ctrl+N: 新增
        Ctrl+E: 编辑
        Ctrl+D: 删除
        Ctrl+S: 保存
        Ctrl+F: 搜索
        Ctrl+R: 刷新
        F5: 刷新
        Esc: 关闭对话框/取消
        Enter: 确认/保存
        Ctrl+Q: 退出程序
        """
        QMessageBox.information(self, "快捷键", shortcuts_text)
        
    def export_data(self):
        """数据导出"""
        QMessageBox.information(self, "提示", "数据导出功能正在开发中")
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(self, '确认退出', 
                                   '确定要退出仓库货品管理系统吗？',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            logger.info("用户退出系统")
            event.accept()
        else:
            event.ignore()