-- ============================================
-- 仓库货品管理系统 - 初始数据脚本
-- 数据库：warehouse_manage
-- ============================================

USE warehouse_manage;

-- ============================================
-- 1. 插入基础信息数据
-- ============================================

-- 插入单位信息
INSERT INTO base_info (info_type, info_name, info_code, description, status) VALUES
('unit', '个', 'UNIT001', '计量单位：个', 1),
('unit', '件', 'UNIT002', '计量单位：件', 1),
('unit', '箱', 'UNIT003', '计量单位：箱', 1),
('unit', '包', 'UNIT004', '计量单位：包', 1),
('unit', '千克', 'UNIT005', '计量单位：千克', 1),
('unit', '吨', 'UNIT006', '计量单位：吨', 1),
('unit', '升', 'UNIT007', '计量单位：升', 1),
('unit', '米', 'UNIT008', '计量单位：米', 1);

-- 插入类别信息
INSERT INTO base_info (info_type, info_name, info_code, description, status) VALUES
('category', '电子产品', 'CAT001', '电子产品类别', 1),
('category', '食品饮料', 'CAT002', '食品饮料类别', 1),
('category', '服装鞋帽', 'CAT003', '服装鞋帽类别', 1),
('category', '日用品', 'CAT004', '日用品类别', 1),
('category', '建材', 'CAT005', '建材类别', 1),
('category', '其他', 'CAT999', '其他类别', 1);

-- ============================================
-- 2. 插入默认管理员用户
-- 密码：admin123 (使用MD5加密后的值)
-- MD5('admin123') = 0192023a7bbd73250516f069df18b500
-- ============================================
INSERT INTO user (username, password, real_name, role, status) VALUES
('admin', '0192023a7bbd73250516f069df18b500', '系统管理员', 'admin', 1);

-- ============================================
-- 3. 插入示例仓库数据（可选）
-- ============================================
INSERT INTO warehouse (warehouse_code, warehouse_name, address, manager, phone, capacity, description, status) VALUES
('WH001', '主仓库', '北京市朝阳区xxx路xxx号', '张三', '010-12345678', 10000.00, '主仓库，用于存储主要货品', 1);

-- ============================================
-- 4. 插入示例供应商/客户数据（可选）
-- ============================================
INSERT INTO supplier_client (code, name, type, contact_person, phone, email, address, description, status) VALUES
('SUP001', '供应商A', 1, '王五', '010-11111111', 'supplier_a@example.com', '北京市丰台区xxx路xxx号', '主要供应商', 1),
('SUP002', '供应商B', 1, '赵六', '010-22222222', 'supplier_b@example.com', '北京市石景山区xxx路xxx号', '辅助供应商', 1),
('CLI001', '客户A', 2, '孙七', '010-33333333', 'client_a@example.com', '北京市通州区xxx路xxx号', '主要客户', 1),
('CLI002', '客户B', 2, '周八', '010-44444444', 'client_b@example.com', '北京市昌平区xxx路xxx号', '辅助客户', 1);

-- ============================================
-- 脚本执行完成
-- ============================================
-- 注意：密码加密说明
-- 默认管理员密码：admin123
-- MD5加密后的值：0192023a7bbd73250516f069df18b500
-- 如需修改密码，请使用MD5或其他加密算法对密码进行加密后更新
-- ============================================

