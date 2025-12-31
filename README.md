# 仓库货品管理系统

一个基于 Python 和 PySide6 开发的桌面端仓库货品管理系统，提供完整的仓库管理功能，包括产品管理、库存管理、出入库管理、供应商客户管理等。

## 功能特性

### 1. 系统管理
- 系统初始化与配置
- 数据库连接管理
- 日志系统
- 用户管理

### 2. 基础信息管理
- 仓库信息管理
- 产品分类管理
- 单位管理

### 3. 产品管理
- 产品信息的增删改查
- 产品图片管理
- 产品库存预警

### 4. 库存管理
- 库存查询
- 库存盘点
- 库存调整

### 5. 出入库管理
- 采购入库
- 销售出库
- 调拨入库/出库
- 其他出入库
- 出入库记录查询

### 6. 供应商与客户管理
- 供应商信息管理
- 客户信息管理
- 往来单位管理

### 7. 查询与统计
- 库存查询
- 出入库记录查询
- 库存统计报表
- 业务数据统计

## 技术栈

- **开发语言**：Python 3.11+
- **GUI框架**：PySide6
- **数据库**：MySQL/PostgreSQL (通过配置文件切换)
- **设计模式**：MVC (Model-View-Controller)
- **日志系统**：Python logging 模块
- **打包工具**：PyInstaller (已生成可执行文件)

## 项目结构

```
warehouse-desktop-manage/
├── build/                 # PyInstaller 构建输出目录
├── config/                # 配置文件相关
│   └── database.py        # 数据库配置
├── dao/                   # 数据访问层
│   ├── base_dao.py        # 基础 DAO 类
│   ├── db_connection.py   # 数据库连接管理
│   ├── inventory_dao.py   # 库存数据访问
│   ├── product_dao.py     # 产品数据访问
│   └── ...                # 其他数据访问类
├── logs/                  # 日志文件目录
├── model/                 # 数据模型层
│   ├── product.py         # 产品模型
│   ├── inventory.py       # 库存模型
│   └── ...                # 其他模型类
├── service/               # 业务逻辑层
│   ├── product_service.py # 产品业务逻辑
│   ├── inventory_service.py # 库存业务逻辑
│   └── ...                # 其他业务逻辑类
├── sql/                   # SQL 脚本
│   ├── init_database.sql  # 数据库初始化脚本
│   ├── init_data.sql      # 初始数据脚本
│   └── README.md          # SQL 脚本说明
├── ui/                    # 界面层 (主要使用)
│   ├── main_freame.py     # 主窗口
│   ├── product_window.py  # 产品管理窗口
│   ├── inventory_window.py # 库存管理窗口
│   └── ...                # 其他界面类
├── utils/                 # 工具类
│   ├── logger.py          # 日志工具
│   └── validator.py       # 验证工具
├── main.py                # 主程序入口
├── WarehouseManageSystem.exe # 可执行文件
└── WarehouseManageSystem.spec # PyInstaller 配置文件
```

## 安装说明

### 1. 从可执行文件运行

直接运行 `WarehouseManageSystem.exe` 即可启动系统，无需安装 Python 环境。

### 2. 从源代码运行

#### 环境要求
- Python 3.11+
- MySQL/PostgreSQL 数据库

#### 安装步骤

1. 克隆或下载项目代码
2. 安装依赖包
   ```bash
   pip install -r requirements.txt
   ```
3. 配置数据库连接
   - 编辑 `config/database.py` 文件，设置数据库连接参数
4. 初始化数据库
   - 执行 `sql/init_database.sql` 创建数据库和表
   - 执行 `sql/init_data.sql` 插入初始数据
5. 运行程序
   ```bash
   python main.py
   ```

## 使用方法

### 首次运行

1. 启动系统后，系统会自动初始化配置和数据库连接
2. 系统会检查配置文件和数据库连接状态
3. 如果初始化成功，将进入主窗口
4. 默认使用管理员账号自动登录

### 主要操作流程

1. **基础信息设置**：首先在基础信息管理中设置仓库、产品分类、单位等基础数据
2. **产品管理**：添加产品信息，包括产品名称、分类、规格、单位等
3. **采购入库**：通过采购入库功能将产品录入库存
4. **销售出库**：通过销售出库功能记录产品出库
5. **库存查询**：随时查询产品库存状态
6. **报表统计**：生成各类统计报表

## 配置说明

### 数据库配置

修改 `config/database.py` 文件中的数据库连接参数：

```python
# 数据库类型：mysql 或 postgresql
DB_TYPE = "mysql"

# 数据库连接参数
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "warehouse_manage",
    "user": "root",
    "password": "password"
}
```

### 日志配置

日志文件默认保存在 `logs/` 目录下，按模块和日期生成不同的日志文件。

## 注意事项

1. 首次运行前请确保已正确配置数据库连接
2. 建议定期备份数据库，以防数据丢失
3. 系统默认使用管理员账号自动登录，建议在正式环境中修改登录机制
4. 出入库操作请谨慎，避免误操作导致库存数据错误
5. 定期清理日志文件，避免占用过多磁盘空间

## 开发说明

### 代码结构

- **Model层**：定义数据模型，对应数据库表结构
- **DAO层**：负责数据库操作，实现数据的增删改查
- **Service层**：实现业务逻辑，调用DAO层完成数据操作
- **UI层**：实现用户界面，处理用户交互，调用Service层完成业务逻辑

### 添加新功能

1. 在Model层定义对应的数据模型
2. 在DAO层实现数据访问方法
3. 在Service层实现业务逻辑
4. 在UI层添加对应的界面和交互

### 打包成可执行文件

使用PyInstaller打包：

```bash
pyinstaller --onefile --windowed WarehouseManageSystem.spec
```

## 故障排除

### 1. 数据库连接失败
- 检查数据库服务是否运行
- 检查数据库连接参数是否正确
- 检查数据库用户权限

### 2. 系统初始化失败
- 检查配置文件是否存在且格式正确
- 检查日志文件，查看详细错误信息

### 3. 界面显示异常
- 检查PySide6版本是否兼容
- 尝试重新运行程序

## 更新日志

### V1.0.0 
- 初始版本发布
- 实现基础功能：产品管理、库存管理、出入库管理
- 支持MySQL和PostgreSQL数据库
- 提供可执行文件


## 许可证

[MIT License](LICENSE)
