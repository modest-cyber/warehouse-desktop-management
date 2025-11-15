# -*- coding: utf-8 -*-
"""
日志工具类
提供统一的日志记录功能
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class Logger:
    """日志工具类"""
    
    _loggers = {}
    _log_dir = 'logs'
    
    @classmethod
    def _ensure_log_dir(cls):
        """确保日志目录存在"""
        if not os.path.exists(cls._log_dir):
            os.makedirs(cls._log_dir)
    
    @classmethod
    def get_logger(cls, name='warehouse_system'):
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            logging.Logger: 日志记录器对象
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        cls._ensure_log_dir()
        
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 文件处理器（按日期分割）
        log_file = os.path.join(cls._log_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        cls._loggers[name] = logger
        return logger

