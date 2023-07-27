# Cloudflare DDNS 服务

该项目实现了一个 Cloudflare DDNS 服务，用于将动态 IPv4/iPv6 地址自动更新到 Cloudflare DNS 记录。

## 安装与配置

### 1. 克隆该项目到本地：

```
git clone https://github.com/your_username/cloudflare-ddns.git
```

### 2. 安装所需依赖：

```
pip install -r requirements.txt
```

### 3. 配置 Cloudflare API Token 和其他选项：
```
- interval: 180  #更新 IP 地址的间隔（单位：秒）
  api_token:     #Cloudflare API Token
  zone_id:       #Cloudflare Zone ID
  dns_name:      #需要更新的域名
  ip_type:       #IP 地址类型（ipv4 或 ipv6）
  proxied: true  #是否启用 Cloudflare 的代理（True 或 False）
```
### 4. 启动 Cloudflare DDNS 服务

###### 注：第4、5、6步命令根据平台选择不同的脚本

要启动 Cloudflare DDNS 服务，打开命令行窗口，切换到项目目录下的bin，然后执行以下命令：

windows：

```
run.bat start
```

linux：

```
run.sh start
```

Cloudflare DDNS 服务将会在后台启动，并且将日志记录到 `项目目录下的bin\log\log.txt` 文件中。你可以查看日志文件以了解服务的运行情况。

### 5. 停止 Cloudflare DDNS 服务

如果需要停止 Cloudflare DDNS 服务，执行以下命令：

```
run.bat/run.sh stop
```

### 6. 重启 Cloudflare DDNS 服务

如果需要重启 Cloudflare DDNS 服务，执行以下命令：

```
run.bat/run.sh restart
```

### 注意事项

- 在启动 Cloudflare DDNS 服务之前，请确保已经完成了配置步骤，并且 Python 环境已经正确设置。
- 请不要修改 `pid.txt` 文件，这个文件用于存储服务的进程ID，以便后续停止服务时使用。
- 直接运行项目目录下的src/main.py在终端目录生成`config.yml`，日志在终端输出不额外生成日志文件
- 使用`run.bat/run.sh`运行，配置文件在`项目目录下的bin/config`文件夹下，日志在`项目目录下的bin/log`文件夹下
- 如果你需要添加更多的域名配置，可以在 `config.yml` 文件中继续添加。

## 许可证

本项目遵循 MIT 许可证。详细信息请查阅 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎大家一起贡献代码或提出问题。

## 联系方式

如有问题，请联系：15047150695@163.com