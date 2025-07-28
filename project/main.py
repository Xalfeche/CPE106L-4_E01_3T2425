import subprocess
import time
import sys
import requests
import signal
import os

def check_backend_health():
    """Check if backend is ready"""
    try:
        response = requests.get("http://localhost:5000/")
        return response.status_code == 200
    except:
        return False

def wait_for_backend(max_retries=30):
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to start...")
    
    for i in range(max_retries):
        if check_backend_health():
            print("✅ Backend is ready!")
            return True
        else:
            print(f"⏳ Backend not ready yet, retrying... ({i+1}/{max_retries})")
            time.sleep(1)
    
    print("❌ Backend failed to start within timeout")
    return False

def cleanup_processes():
    """Clean up background processes"""
    print("🧹 Cleaning up processes...")

if __name__ == "__main__":
    print("Starting CommunityConnect Application...")
    print("=" * 50)
    
    backend_process = None
    frontend_process = None
    
    def signal_handler(sig, frame):
        cleanup_processes()
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Start backend server
        print("🚀 Starting backend server...")
        backend_process = subprocess.Popen([
            sys.executable, "-c",
            "import uvicorn; uvicorn.run('backend:app', host='0.0.0.0', port=5000, reload=False)"
        ])
        
        # Wait for backend to be ready
        if not wait_for_backend():
            print("❌ Backend failed to start. Exiting.")
            sys.exit(1)
        
        # Start frontend application
        print("🖥️  Starting frontend application...")
        print("🎉 CommunityConnect is now running!")
        print("📱 Frontend: http://localhost:8080")
        print("🔧 Backend API: http://localhost:5000")
        print("📚 API Documentation: http://localhost:5000/docs")
        print("\n💡 Default admin credentials:")
        print("   Email: admin@example.com")
        print("   Password: Admin123")
        print("\nPress Ctrl+C to stop the application")
        
        # Run frontend
        frontend_process = subprocess.Popen([sys.executable, "flet_app.py"])
        
        # Wait for processes to complete
        try:
            frontend_process.wait()
        except KeyboardInterrupt:
            pass
        
        # Check if frontend process died unexpectedly
        if frontend_process.poll() is not None and frontend_process.returncode != 0:
            print("❌ Frontend process died. Stopping application.")
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
    
    finally:
        cleanup_processes()
        if backend_process:
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
        
        if frontend_process:
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                frontend_process.kill()
    
    print("👋 CommunityConnect has been stopped. Goodbye!")