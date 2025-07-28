import multiprocessing
import time
import uvicorn
import subprocess
import sys
import requests
import os

def run_backend():
    """Run the FastAPI backend server"""
    try:
        import backend
        uvicorn.run("backend:app", host="0.0.0.0", port=5000, reload=False)
    except Exception as e:
        print(f"Error starting backend: {e}")

def run_frontend():
    """Run the Flet frontend application"""
    try:
        import frontend
        import flet as ft
        ft.app(target=frontend.main, port=8080, host="0.0.0.0")
    except Exception as e:
        print(f"Error starting frontend: {e}")

def check_backend_health():
    """Check if backend is running and healthy"""
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=2)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("Starting CommunityConnect Application...")
    print("=" * 50)
    
    # Start backend process
    print("🚀 Starting backend server...")
    backend_process = multiprocessing.Process(target=run_backend)
    backend_process.start()
    
    # Wait for backend to be ready
    print("⏳ Waiting for backend to start...")
    backend_ready = False
    for i in range(30):  # Wait up to 30 seconds
        if check_backend_health():
            print("✅ Backend is ready!")
            backend_ready = True
            break
        else:
            print(f"⏳ Backend not ready yet, retrying... ({i+1}/30)")
            time.sleep(1)
    
    if not backend_ready:
        print("❌ Backend failed to start in time. Exiting.")
        backend_process.terminate()
        backend_process.join()
        sys.exit(1)
    
    # Start frontend process
    print("🖥️  Starting frontend application...")
    frontend_process = multiprocessing.Process(target=run_frontend)
    frontend_process.start()
    
    print("🎉 CommunityConnect is now running!")
    print("📱 Frontend: http://localhost:8080")
    print("🔧 Backend API: http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000/docs")
    print("\n💡 Default admin credentials:")
    print("   Email: admin@example.com")
    print("   Password: Admin123")
    print("\nPress Ctrl+C to stop the application")
    
    try:
        # Keep the main process alive and monitor child processes
        while True:
            if not backend_process.is_alive():
                print("❌ Backend process died. Stopping application.")
                break
            if not frontend_process.is_alive():
                print("❌ Frontend process died. Stopping application.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down CommunityConnect...")
    
    # Clean up processes
    print("🧹 Cleaning up processes...")
    if backend_process.is_alive():
        backend_process.terminate()
    if frontend_process.is_alive():
        frontend_process.terminate()
    
    backend_process.join(timeout=5)
    frontend_process.join(timeout=5)
    
    print("👋 CommunityConnect has been stopped. Goodbye!")