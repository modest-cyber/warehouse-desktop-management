# -*- coding: utf-8 -*-
"""
仓库货品管理系统 - 主程序入口
"""

import sys
import traceback
from config.database import validate_config
from dao.db_connection import DatabaseConnection
from utils.logger import Logger

logger = Logger.get_logger(__name__)


def init_system():
    """
    初始化系统
    
    Returns:
        bool: 初始化是否成功
    """
    try:
        # 1. 加载配置文件
        logger.info("正在加载配置文件...")
        validate_config()
        logger.info("配置文件加载成功")
        
        # 2. 初始化日志系统（已在Logger类中自动初始化）
        logger.info("日志系统初始化成功")
        
        # 3. 测试数据库连接
        logger.info("正在测试数据库连接...")
        db_connection = DatabaseConnection()
        if db_connection.test_connection():
            logger.info("数据库连接测试成功")
            return True
        else:
            logger.error("数据库连接测试失败")
            print("错误：数据库连接失败，请检查数据库配置和连接状态")
            return False
            
    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"错误：系统初始化失败 - {str(e)}")
        return False


def start_application():
    """启动应用程序主循环（PySide6）"""
    # 日志与控制台输出
    logger.info("=" * 50)
    logger.info("仓库货品管理系统启动")
    logger.info("=" * 50)

    print("=" * 50)
    print("仓库货品管理系统")
    print("=" * 50)
    print("系统初始化中...")

    # 初始化系统（配置、日志、数据库连接）
    if not init_system():
        print("系统初始化失败，程序退出")
        sys.exit(1)

    print("系统初始化成功！")
    print("=" * 50)

    # 启动 PySide6 UI：先登录，再进入主窗口
    from PySide6.QtWidgets import QApplication, QDialog
    from ui.Login_window import LoginWindow
    from ui.main_freame import MainWindow

    app = QApplication(sys.argv)

    # 显示登录窗口
    login_dialog = LoginWindow()
    if login_dialog.exec() != QDialog.Accepted:
        logger.info("用户取消登录，程序退出")
        return

    user = login_dialog.get_user()
    if not user:
        logger.error("登录窗口未返回用户对象，程序退出")
        return

    logger.info(f"使用用户: {user.username}")

    # 显示主窗口
    main_window = MainWindow(user)
    main_window.show()

    logger.info("进入 Qt 事件循环")
    app.exec()
    logger.info("应用程序主循环结束")


def main():
    """
    主函数
    """
    try:
        start_application()
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        print("\n程序已退出")
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"错误：程序运行出错 - {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

