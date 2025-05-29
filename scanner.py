import socket
import threading
from queue import Queue
from datetime import datetime

# Target and settings
target = input("Enter the host to scan (IP or domain): ")
start_port = int(input("Enter the starting port number: "))
end_port = int(input("Enter the ending port number: "))
timeout = float(input("Set socket timeout (e.g., 1.0): "))
thread_count = int(input("Number of threads (e.g., 100): "))

# Resolve domain to IP
try:
    target_ip = socket.gethostbyname(target)
except socket.gaierror:
    print("[!] Could not resolve host.")
    exit()

# Thread-safe queue
queue = Queue()

# Scan a single port
def scan_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            try:
                # Try to get banner
                sock.sendall(b"HEAD / HTTP/1.1\r\nHost: google.com\r\n\r\n")
                banner = sock.recv(1024).decode().strip()
            except:
                banner = "No banner received"
            print(f"[+] Port {port} is OPEN - {banner}")
        sock.close()
    except Exception as e:
        pass

# Worker thread function
def thread_worker():
    while not queue.empty():
        port = queue.get()
        scan_port(port)
        queue.task_done()

# Fill the queue with ports
for port in range(start_port, end_port + 1):
    queue.put(port)

print(f"\n[+] Starting scan on {target_ip}")
start_time = datetime.now()

# Launch threads
for _ in range(thread_count):
    t = threading.Thread(target=thread_worker)
    t.daemon = True
    t.start()

# Wait for all threads to finish
queue.join()

end_time = datetime.now()
print(f"\n[+] Scan completed in {end_time - start_time}")
