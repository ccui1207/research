#!/usr/bin/env python3
import socket
import sys
import time
from datetime import datetime

PORTS = (8080, 8081, 8082, 8083, 8084, 8085, 8086)

STATUS_WIDTH = 22
LINE_WIDTH = 72


def check_once(host: str, timeout: float):
    results = []
    for port in PORTS:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            ret = s.connect_ex((host, port))
            if ret == 0:
                status = "OPEN"
            else:
                status = f"NO_CONNECT({ret})"
        except socket.timeout:
            status = "TIMEOUT"
        except Exception as e:
            status = f"ERROR({type(e).__name__})"
        finally:
            s.close()
        results.append((port, status))
    return results


def summarize(results):
    open_count = sum(1 for _, s in results if s == "OPEN")
    timeout_count = sum(1 for _, s in results if s == "TIMEOUT")
    no_connect_count = sum(1 for _, s in results if s.startswith("NO_CONNECT"))
    error_count = sum(1 for _, s in results if s.startswith("ERROR"))
    return open_count, timeout_count, no_connect_count, error_count


def print_header(host: str, interval: float, timeout: float):
    print("=" * LINE_WIDTH)
    print("端口探测演示")
    print("-" * LINE_WIDTH)
    print(f"目标主机 : {host}")
    print(f"探测端口 : {PORTS}")
    print(f"探测间隔 : {interval}s")
    print(f"连接超时 : {timeout}s")
    print("停止方式 : Ctrl+C")
    print("=" * LINE_WIDTH)
    print()


def print_round(results, round_no: int):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    open_count, timeout_count, no_connect_count, error_count = summarize(results)

    print("─" * LINE_WIDTH)
    print(f"第 {round_no:03d} 轮   {now}")
    print("─" * LINE_WIDTH)

    for port, status in results:
        print(f"  端口 {port:<5} | 状态: {status:<{STATUS_WIDTH}}")

    print("─" * LINE_WIDTH)
    print(
        f"统计  OPEN: {open_count:<2}   "
        f"NO_CONNECT: {no_connect_count:<2}   "
        f"TIMEOUT: {timeout_count:<2}   "
        f"ERROR: {error_count:<2}"
    )
    print()


def main():
    if len(sys.argv) < 2:
        print("用法: python3 lab_probe_client.py <SERVER_IP> [interval_seconds] [timeout_seconds]")
        print("示例: python3 lab_probe_client.py 39.105.160.189 5 1.5")
        sys.exit(1)

    host = sys.argv[1]
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5

    print_header(host, interval, timeout)

    round_no = 1
    try:
        while True:
            results = check_once(host, timeout)
            print_round(results, round_no)
            round_no += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()