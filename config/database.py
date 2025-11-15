# -*- coding: utf-8 -*-
"""
数据库配置文件
提供数据库连接配置信息
"""

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123',
    'database': 'warehouse_manage',
    'charset': 'utf8mb4'
}


def get_db_config():
    """
    获取数据库配置信息
    
    Returns:
        dict: 数据库配置字典
    """
    return DB_CONFIG.copy()


def validate_config():
    """
    验证配置信息是否完整
    
    Returns:
        bool: 配置是否有效
        
    Raises:
        ValueError: 配置项缺失时抛出异常
    """
    required_keys = ['host', 'port', 'user', 'password', 'database', 'charset']
    
    for key in required_keys:
        if key not in DB_CONFIG:
            raise ValueError(f"数据库配置缺少必要项: {key}")
        if DB_CONFIG[key] is None or DB_CONFIG[key] == '':
            raise ValueError(f"数据库配置项 {key} 不能为空")
    
    return True

