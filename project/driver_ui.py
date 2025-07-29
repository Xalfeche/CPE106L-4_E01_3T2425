import flet as ft
import requests

API = "http://localhost:8000"

def create_driver_ui(page):
    driver_table_rows = []
    
    def load_pending(_=None):
        driver_table_rows.clear()
        try:
            resp = requests.get(f"{API}/rides/pending")
            for r in resp.json():
                driver_table_rows.append(r)
        except:
            driver_table_rows.extend([
                {"_id": "001", "pickup_location": "Downtown", "dropoff_location": "Airport"},
                {"_id": "002", "pickup_location": "Mall", "dropoff_location": "University"},
            ])
        page.update()
    
    def accept(rid):
        try:
            requests.post(f"{API}/rides/accept/{rid}")
            load_pending()
        except:
            pass
    
    def create_driver_table():
        if not driver_table_rows:
            load_pending()
        
        rows = []
        for r in driver_table_rows:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(r["_id"]))),
                        ft.DataCell(ft.Text(r["pickup_location"])),
                        ft.DataCell(ft.Text(r["dropoff_location"])),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.CHECK_CIRCLE,
                                    icon_color=ft.Colors.GREEN_400,
                                    icon_size=24,
                                    on_click=lambda e, id=r["_id"]: accept(id)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CANCEL,
                                    icon_color=ft.Colors.RED_400,
                                    icon_size=24,
                                    on_click=lambda e: None
                                )
                            ], spacing=5)
                        ),
                    ]
                )
            )
        
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Pick Up", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Drop Off", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Action", weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            column_spacing=20,
            data_row_min_height=50,
            data_row_max_height=60
        )
    
    map_placeholder = ft.Container(
        content=ft.Column([
            ft.Text(
                "Placeholer for",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK54
            ),
            ft.Text(
                "Maps",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK54
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=250,
        height=150,
        bgcolor=ft.Colors.BLUE_GREY_100,
        border_radius=10,
        border=ft.border.all(2, ft.Colors.BLUE_GREY_200),
        alignment=ft.alignment.center
    )
    
    driver_left_controls = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.DIRECTIONS_CAR, size=24, color=ft.Colors.WHITE),
                ft.Text("Driver", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ], spacing=10),
            ft.Container(height=20),
            ft.Container(
                content=create_driver_table(),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=10,
                width=450,
                height=250
            )
        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.START),
        padding=30,
        bgcolor=ft.Colors.GREY_600,
        border_radius=10,
        width=550
    )
    
    return ft.Container(
        content=ft.Row([
            driver_left_controls,
            ft.Container(width=20),
            map_placeholder
        ], alignment=ft.MainAxisAlignment.CENTER, expand=True),
        alignment=ft.alignment.center,
        expand=True
    )