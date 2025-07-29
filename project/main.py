import subprocess
import time
<<<<<<< HEAD
import sys
import requests
import signal
import os
=======
import uvicorn
import flet as ft
from rider_ui import create_rider_ui
from driver_ui import create_driver_ui
from admin_ui import create_admin_ui

def main(page: ft.Page):
    page.title = "CommunityConnect"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_100
    page.window_width = 1200
    page.window_height = 800
    page.window_maximized = True
    
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Rider", icon=ft.Icons.PERSON),
            ft.Tab(text="Driver", icon=ft.Icons.DIRECTIONS_CAR),
            ft.Tab(text="Admin", icon=ft.Icons.BAR_CHART),
        ],
        expand=1,
    )
    
    rider_v = create_rider_ui(page)
    driver_v = create_driver_ui(page)
    admin_v = create_admin_ui(page)
    
    def tab_changed(e):
        page.controls.clear()
        
        selected_content = [rider_v, driver_v, admin_v][e.control.selected_index]
        
        main_content = ft.Column([
            ft.Container(
                content=tabs,
                alignment=ft.alignment.center,
                width=800
            ),
            selected_content
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        
        page.add(main_content)
        page.update()
    
    tabs.on_change = tab_changed
    
    main_content = ft.Column([
        ft.Container(
            content=tabs,
            alignment=ft.alignment.center,
            width=800
        ),
        rider_v
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
    
    page.add(main_content)
>>>>>>> refs/remotes/origin/main

def check_backend_health():
    """Check if backend is ready"""
    try:
        response = requests.get("http://localhost:5000/")
        return response.status_code == 200
    except:
        return False

<<<<<<< HEAD
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
=======
def run_frontend():
    ft.app(target=main)

if __name__ == "__main__":
    p = multiprocessing.Process(target=run_backend)
    p.start()
    time.sleep(1)
    ft.app(target=main)
    p.join()
>>>>>>> refs/remotes/origin/main
