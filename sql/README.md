# SQL脚本使用说明

## 文件说明

### 1. init_database.sql
数据库结构初始化脚本，包含：
- 创建数据库 warehouse_manage
- 创建所有7个数据表
- 创建所有索引和外键约束

### 2. init_data.sql
初始数据脚本，包含：
- 基础信息数据（单位、类别）
- 默认管理员用户（用户名：admin，密码：admin123）
- 示例仓库数据（可选）
- 示例供应商/客户数据（可选）

## 使用方法

### 方法一：使用MySQL命令行

```bash
# 1. 登录MySQL（使用root账号，密码123）
mysql -u root -p123

# 2. 执行数据库初始化脚本
source sql/init_database.sql

# 3. 执行初始数据脚本
source sql/init_data.sql
```

### 方法二：使用命令行直接执行

```bash
# 执行数据库初始化脚本
mysql -u root -p123 < sql/init_database.sql

# 执行初始数据脚本
mysql -u root -p123 < sql/init_data.sql
```

### 方法三：使用MySQL Workbench或Navicat

1. 打开MySQL Workbench或Navicat
2. 连接到MySQL服务器（用户名：root，密码：123）
3. 依次执行 `init_database.sql` 和 `init_data.sql` 文件

## 默认账号信息

- **用户名**：admin
- **密码**：admin123
- **角色**：admin

**注意**：密码已使用MD5加密存储，实际存储值为：`0192023a7bbd73250516f069df18b500`

## 数据库信息

- **数据库名**：warehouse_manage
- **字符集**：utf8mb4
- **排序规则**：utf8mb4_general_ci
- **存储引擎**：InnoDB

## 注意事项

1. 执行脚本前请确保MySQL服务已启动
2. 如果数据库已存在，脚本会创建新的数据库（不会删除现有数据）
3. 如需重新初始化，请先手动删除现有数据库
4. 初始数据中的示例数据可以根据实际需求修改或删除

