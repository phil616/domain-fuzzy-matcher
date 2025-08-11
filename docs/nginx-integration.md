# Nginx 集成指南

## 集成方案

### 方案一：Nginx + uWSGI + Python 后端

这是推荐的生产环境部署方案，提供最佳的性能和稳定性。

#### 架构图

```
[用户请求] → [Nginx] → [uWSGI] → [Python应用] → [域名匹配系统]
                ↓
           [静态文件服务]
           [负载均衡]
           [SSL终端]
```

### 方案二：Nginx + Lua 脚本

使用Nginx的Lua模块直接在Nginx层面处理域名匹配，适合高并发场景。

### 方案三：Nginx + 外部API服务

将域名匹配系统作为独立的微服务，通过HTTP API与Nginx通信。
