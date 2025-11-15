-- ============================================
-- 仓库货品管理系统 - 数据库初始化脚本
-- 数据库：warehouse_manage
-- MySQL版本：5.7+
-- 字符集：utf8mb4
-- 存储引擎：InnoDB
-- ============================================

-- 删除已存在的数据库（谨慎使用）
-- DROP DATABASE IF EXISTS warehouse_manage;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS warehouse_manage 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_general_ci;

-- 使用数据库
USE warehouse_manage;

-- ============================================
-- 1. 基础信息表（base_info）
-- ============================================
CREATE TABLE base_info (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    info_type VARCHAR(50) NOT NULL COMMENT '信息类型（单位、类别等）',
    info_name VARCHAR(100) NOT NULL COMMENT '信息名称',
    info_code VARCHAR(50) COMMENT '信息编码',
    description TEXT COMMENT '描述',
    status TINYINT DEFAULT 1 COMMENT '状态（1-启用，0-禁用）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基础信息表';

-- 创建索引
CREATE INDEX idx_info_type ON base_info(info_type);

-- ============================================
-- 2. 货品信息表（product）
-- ============================================
CREATE TABLE product (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    product_code VARCHAR(50) UNIQUE NOT NULL COMMENT '货品编码',
    product_name VARCHAR(100) NOT NULL COMMENT '货品名称',
    category_id INT COMMENT '类别ID',
    unit_id INT COMMENT '单位ID',
    specification VARCHAR(200) COMMENT '规格',
    price DECIMAL(10,2) COMMENT '单价',
    min_stock INT DEFAULT 0 COMMENT '最低库存',
    max_stock INT DEFAULT 0 COMMENT '最高库存',
    description TEXT COMMENT '描述',
    status TINYINT DEFAULT 1 COMMENT '状态（1-启用，0-禁用）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (category_id) REFERENCES base_info(id) ON UPDATE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES base_info(id) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='货品信息表';

-- 创建索引
CREATE INDEX idx_category_id ON product(category_id);
CREATE INDEX idx_unit_id ON product(unit_id);

-- ============================================
-- 3. 仓库信息表（warehouse）
-- ============================================
CREATE TABLE warehouse (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    warehouse_code VARCHAR(50) UNIQUE NOT NULL COMMENT '仓库编码',
    warehouse_name VARCHAR(100) NOT NULL COMMENT '仓库名称',
    address VARCHAR(200) COMMENT '地址',
    manager VARCHAR(50) COMMENT '负责人',
    phone VARCHAR(20) COMMENT '联系电话',
    capacity DECIMAL(10,2) COMMENT '容量',
    description TEXT COMMENT '描述',
    status TINYINT DEFAULT 1 COMMENT '状态（1-启用，0-禁用）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='仓库信息表';

-- ============================================
-- 4. 供应商/客户信息表（supplier_client）
-- ============================================
CREATE TABLE supplier_client (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    code VARCHAR(50) UNIQUE NOT NULL COMMENT '编码',
    name VARCHAR(100) NOT NULL COMMENT '名称',
    type TINYINT NOT NULL COMMENT '类型（1-供应商，2-客户）',
    contact_person VARCHAR(50) COMMENT '联系人',
    phone VARCHAR(20) COMMENT '联系电话',
    email VARCHAR(100) COMMENT '邮箱',
    address VARCHAR(200) COMMENT '地址',
    description TEXT COMMENT '描述',
    status TINYINT DEFAULT 1 COMMENT '状态（1-启用，0-禁用）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商/客户信息表';

-- 创建索引
CREATE INDEX idx_type ON supplier_client(type);

-- ============================================
-- 5. 入库/出库记录表（stock_record）
-- ============================================
CREATE TABLE stock_record (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    record_no VARCHAR(50) UNIQUE NOT NULL COMMENT '单据号',
    record_type TINYINT NOT NULL COMMENT '类型（1-入库，2-出库）',
    warehouse_id INT NOT NULL COMMENT '仓库ID',
    product_id INT NOT NULL COMMENT '货品ID',
    quantity INT NOT NULL COMMENT '数量',
    unit_price DECIMAL(10,2) COMMENT '单价',
    total_amount DECIMAL(10,2) COMMENT '总金额',
    supplier_client_id INT COMMENT '供应商/客户ID',
    operator VARCHAR(50) COMMENT '操作人',
    record_date DATETIME NOT NULL COMMENT '操作日期',
    remark TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(id) ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON UPDATE CASCADE,
    FOREIGN KEY (supplier_client_id) REFERENCES supplier_client(id) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库/出库记录表';

-- 创建索引
CREATE INDEX idx_warehouse_id ON stock_record(warehouse_id);
CREATE INDEX idx_product_id ON stock_record(product_id);
CREATE INDEX idx_record_type ON stock_record(record_type);
CREATE INDEX idx_record_date ON stock_record(record_date);

-- ============================================
-- 6. 库存表（inventory）
-- ============================================
CREATE TABLE inventory (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    warehouse_id INT NOT NULL COMMENT '仓库ID',
    product_id INT NOT NULL COMMENT '货品ID',
    quantity INT DEFAULT 0 COMMENT '库存数量',
    last_in_date DATETIME COMMENT '最后入库日期',
    last_out_date DATETIME COMMENT '最后出库日期',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_warehouse_product (warehouse_id, product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(id) ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存表';

-- 创建索引
CREATE INDEX idx_warehouse_id_inv ON inventory(warehouse_id);
CREATE INDEX idx_product_id_inv ON inventory(product_id);

-- ============================================
-- 7. 用户表（user）
-- ============================================
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码（加密存储）',
    real_name VARCHAR(50) COMMENT '真实姓名',
    role VARCHAR(20) DEFAULT 'admin' COMMENT '角色',
    status TINYINT DEFAULT 1 COMMENT '状态（1-启用，0-禁用）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ============================================
-- 脚本执行完成
-- ============================================

