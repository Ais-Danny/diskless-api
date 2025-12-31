# 磁盘无盘化管理系统

基于 Flask 的磁盘无盘化管理系统，支持 PVE (Proxmox VE) 虚拟机磁盘管理，集成 TrueNAS 存储服务。

## 系统要求

- **Python**: 3.13.1+
- **TrueNAS**: SCALE-25.10.0.1+
- **MySQL**: 8.0+
- **操作系统**: Linux/Windows/macOS

## 核心功能

### 🔧 磁盘管理
- **快照管理**: 创建、查询、克隆快照
- **数据集操作**: 快照克隆、差分目录管理
- **文件系统**: 数据集创建、删除、配置

### 📁 NFS 共享管理
- **共享创建**: 基于路径的 NFS 共享创建
- **共享删除**: 按路径批量删除 NFS 共享
- **存在检查**: 验证 NFS 共享是否存在

### 🔗 SSH 远程操作
- **远程执行**: 安全 SSH 命令执行
- **文件传输**: SFTP 文件上传下载
- **连接管理**: 连接超时、错误处理

### 🎯 PVE 集成
- **VM 配置**: PVE 虚拟机磁盘配置
- **自动化**: 脚本自动执行和配置
- **网络配置**: IP 地址、网关自动设置

### 🛡️ 安全认证
- **双 Token**: 短效 Token + 长效 Refresh Token
- **MD5 加盐**: 用户密码安全加密
- **JWT 认证**: 标准 JWT 令牌机制

### 📊 监控与日志
- **实时日志**: 彩色控制台输出
- **文件日志**: 按日期自动分割
- **第三方库屏蔽**: 抑制 paramiko、websocket 等库冗余日志

## 技术栈

- **后端**: Flask 3.1.0 + SQLAlchemy 2.0.37
- **数据库**: MySQL with connection pooling
- **存储**: TrueNAS API integration
- **认证**: PyJWT 2.10.1
- **SSH**: paramiko
- **日志**: Python logging + colorama

## 项目结构

```
diskless/
├── src/
│   ├── controllers/          # API 控制器
│   ├── services/            # 业务逻辑层
│   ├── utils/               # 工具模块
│   │   ├── logs.py          # 日志系统
│   │   ├── ssh/             # SSH 客户端
│   │   └── truenas/         # TrueNAS API
│   ├── model/               # 数据模型
│   └── main.py              # 应用入口
├── tool/
│   └── create_engine.py     # 数据库模型生成器
├── logs/                    # 日志目录
└── docs/                    # 文档
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境

复制配置文件模板：
```bash
cp config_template.yaml config.yaml
```

编辑 `config.yaml` 配置数据库、TrueNAS 等参数。

### 运行应用

#### 本地运行
```bash
python app.py
```

#### Docker 容器化部署

**环境要求：**
- Docker Engine 20.10+
- Docker Compose 2.0+

**服务架构：**
- **py_flask**: Flask 应用容器（Python 3.13.1）
- **nginx**: 反向代理容器（nginx:alpine）

**启动容器：**
```bash
# 构建并启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f py_flask
docker-compose logs -f nginx
```

**容器管理：**
```bash
# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 重新构建镜像
docker-compose up -d --build

# 进入容器执行命令
docker-compose exec py_flask bash
```

**端口访问：**
- 应用访问：http://localhost:8080
- API 文档：http://localhost:8080/doc

**配置说明：**
- 容器自动设置时区为 `Asia/Shanghai`
- 使用阿里云 PyPI 源加速依赖安装
- 代码目录挂载到容器 `/app` 目录，支持热更新

## 配置说明

```yaml
model: dev  # 选择对应环境配置文件

configs:
  # 开发环境配置
  - name: dev
    dist: ./dist  # 前端静态文件目录
    port: 8080     # Flask 应用端口
    md5_salt: aisdanny  # MD5 加盐值
    
    jwt:  # JWT 认证配置
      key: JwtKey123
      token_expire_minutes: 120   # 短 Token 过期时间
      refresh_key: JwtRefreshKey123
      refresh_token_expire_minutes: 7200  # 长 Token 过期时间
    
    mysql:  # MySQL 数据库配置
      host: 192.168.3.30
      port: 3306
      username: root
      password: root
      database: aisdanny_db
      pool_size: 10  # 连接池大小
      max_overflow: 20  # 连接池溢出限制
    
    truenas:  # TrueNAS 配置
      host: 192.168.3.40
      api_key: your_api_key
      api_secret: your_api_secret
    
    diskless:  # 磁盘无盘化配置
      pve:
        host: 192.168.3.50
        username: root
        password: pve_password
        pve_base: tank/pve
        pve_client: tank/pve_client
```

## API 文档

启动应用后访问: `http://localhost:8080/doc`

## 开发工具

### 数据库模型生成

使用 `tool/create_engine.py` 自动生成 SQLAlchemy 模型类：

```bash
python tool/create_engine.py
```