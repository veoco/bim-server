# bim-server

bim-berver 是现代网络性能监控平台的服务器后端，与 bench.im 网页前端和 bim 客户端共同构成一个完整的网络监控解决方案。该平台旨在替代传统的 Smokeping，提供更直观、更易用的网络延迟与可达性可视化体验，并支持动态管理监控节点和目标。

## 项目概述

网页前端： https://github.com/veoco/bench.im

服务器后端（本项目）：https://github.com/veoco/bim-server

监控客户端：https://github.com/veoco/bim

## 编译步骤

```
https://github.com/veoco/bim-server.git
cd bim-server
cargo build -r
```

## 运行方法

从发布页面下载后解压：

```
tar -xf bim-server-x86_64-unknown-linux-musl.tar.gz
```

同目录下编写 `.env` 文件：

```
DATABASE_URL=sqlite:db.sqlite3?mode=rwc
ADMIN_PASSWORD=your_pass_word
```

运行：

```
./bim-server
```

## systemd 部署

编写 `/etc/systemd/system/bim-server.service` ：

```
[Unit]
Description=bim-server
After=network.target

[Service]
WorkingDirectory=/your_path
ExecStart=/your_path/bim-server
User=your_user
Group=your_group

[Install]
WantedBy=multi-user.target
```