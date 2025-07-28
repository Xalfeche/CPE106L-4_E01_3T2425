import multiprocessing
import time
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

def run_backend():
    uvicorn.run("backend:app", host="127.0.0.1", port=8000)

def run_frontend():
    ft.app(target=main)

if __name__ == "__main__":
    p = multiprocessing.Process(target=run_backend)
    p.start()
    time.sleep(1)
    ft.app(target=main)
    p.join()