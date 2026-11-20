import sys
import socket
import uvicorn

def is_port_free(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) != 0

def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    for port in range(start_port, start_port + max_attempts):
        if is_port_free(port):
            return port
    return start_port

def main():
    host = "127.0.0.1"
    port = find_available_port(8000)
    
    print("=" * 60)
    print(" 🚀 OmniSEO & AI Studio - Launching Application")
    print("=" * 60)
    print(f" Web Dashboard: http://{host}:{port}")
    print(f" API Docs:      http://{host}:{port}/docs")
    print("=" * 60)
    print(" Press Ctrl+C to stop the server.\n")

    uvicorn.run("app.main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()
