import sys
import re
import socket
import threading
import time
from queue import Queue
from queue import Empty

usage ="Usage python scan.py <host> <start_port> <end_port> or python scan.py <host> <port1> <port2> ..."

print("-"*50)
print("Simple Port Scanner")
print("-"*50)

start_time = time.time()

if(len(sys.argv)<3):
    print(usage)
    sys.exit()

try:
    target = socket.gethostbyname(sys.argv[1])
except socket.gaierror:
    print("Name Resolution Error")
    sys.exit()

ports_to_scan = []

for arg in sys.argv[2:]:
    if "-" in arg:
        try:
            start, end = map(int, arg.split("-"))
            if start > end:
                raise ValueError("Invalid Port Range")
            ports_to_scan.extend(range(start, end+1))
        except ValueError as e:
            print(f"Invalid Port Range: {arg} - {e}")
            sys.exit()
    elif re.match(r"^\d+$", arg):
        try:
            port = int(arg)
            ports_to_scan.append(port)
        except ValueError as e:
            print(f"Invalid Port Number: {arg}")
            sys.exit()
    else:
        print("Invalid Port Specification: {arg}")
        sys.exit()

print(f"Scanning Host: {target}")
open_ports = []

def scan_port(port):
    try:
        s =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        conn = s.connect_ex((target, port))
        s.close()
        if not conn:
            open_ports.append(port)
            print(f"Port {port} is OPEN")
    except Exception as e:
        print(f"Error scanning port {port}: {e}")

def worker():
    while True:
        try:
            port = queue.get(timeout=2)
            scan_port(port)
            queue.task_done()
        except Empty:
            break

queue = Queue()

for port in ports_to_scan:
    queue.put(port)

num_threads = 1024

threads = []

for _ in range(num_threads):
    thread = threading.Thread(target=worker)
    threads.append(thread)
    thread.start()

queue.join()

for thread in threads:
    thread.join()

end_time = time.time()
print("Open Ports:", open_ports)
print("Time Elasped", end_time - start_time, "seconds") 
 