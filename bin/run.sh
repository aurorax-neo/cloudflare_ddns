#!/bin/bash

# 设置Python脚本路径和日志文件路径
SCRIPT_PATH="../src/main.py"
LOG_FILE="log/log.txt"

cd "$(dirname "$0")"
start() {
  mkdir -p log 2>/dev/null
  mkdir -p config 2>/dev/null
  echo "Starting the cloudflare_ddns..."
  nohup python3 -u "$SCRIPT_PATH" --configpath ./config/config.yml >>"$LOG_FILE" 2>&1 &
  echo "cloudflare_ddns started."
}

stop() {
  echo "Stopping the cloudflare_ddns..."
  # 获取正在运行的Python脚本的进程ID（PID）并终止它
  pid=$(<PID.txt)
  if [ -n "$pid" ]; then
    kill "$pid"
    echo "cloudflare_ddns stopped."
  else
    echo "cloudflare_ddns is not running."
  fi
}

restart() {
  stop
  start
}

# 根据传入的命令执行相应的操作
case "$1" in
start)
  start
  ;;
stop)
  stop
  ;;
restart)
  restart
  ;;
*)
  echo "Usage: $0 {start|stop|restart}"
  exit 1
  ;;
esac
