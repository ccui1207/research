import socket
import sys

if len(sys.argv) < 2:
    print("用法: python3 pc_scan.py <SERVER_IP> [port1 port2 ...]")
    print("示例: python3 pc_scan.py 192.168.1.10 8080 9090")
    sys.exit(1)

server_ip = sys.argv[1]
ports = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else [8080, 9090]

for port in ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    try:
        ret = s.connect_ex((server_ip, port))
        if ret == 0:
            print(f"{port}: OPEN")
        else:
            print(f"{port}: CLOSED_OR_FILTERED (connect_ex={ret})")
    except socket.timeout:
        print(f"{port}: FILTERED_OR_TIMEOUT")
    except Exception as e:
        print(f"{port}: ERROR ({e})")
    finally:
        s.close()