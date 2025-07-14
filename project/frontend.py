import flet as ft
import requests
import matplotlib.pyplot as plt

API = "http://localhost:8000"

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
    
    # Rider UI
    name = ft.TextField(
        label="Name",
        width=200,
        border_radius=25,
        bgcolor=ft.Colors.WHITE,
        border_color=ft.Colors.GREY_300,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
    )
    
    pickup = ft.TextField(
        label="Pick Up",
        width=200,
        border_radius=25,
        bgcolor=ft.Colors.WHITE,
        border_color=ft.Colors.GREY_300,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
    )
    
    dropoff = ft.TextField(
        label="Drop Off",
        width=200,
        border_radius=25,
        bgcolor=ft.Colors.WHITE,
        border_color=ft.Colors.GREY_300,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
    )
    
    stat_r = ft.Text(color=ft.Colors.RED_400)
    
    def book(e):
        if not (name.value and pickup.value and dropoff.value):
            stat_r.value = "❌ Fill all fields"
            page.update()
            return
        
        try:
            res = requests.post(f"{API}/rides/request", json={
                "rider_name": name.value,
                "pickup_location": pickup.value,
                "dropoff_location": dropoff.value,
                "requested_time": "ASAP"
            })
            if res.ok:
                d = res.json()
                stat_r.value = f"✅ {d['distance_m']}m, {d['duration_s']}s"
                stat_r.color = ft.Colors.GREEN_400
            else:
                stat_r.value = "❌ Error"
                stat_r.color = ft.Colors.RED_400
        except:
            stat_r.value = "❌ Connection Error"
            stat_r.color = ft.Colors.RED_400
        page.update()
    
    # Map placeholder 
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
    
    # Left side controls
    left_controls = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PERSON, size=24, color=ft.Colors.WHITE),
                ft.Text("Rider", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ], spacing=10),
            ft.Container(height=20),  # Spacer
            name,
            ft.Container(height=10),
            dropoff,
            ft.Container(height=10),
            pickup,
            ft.Container(height=20),
            ft.ElevatedButton(
                "Submit",
                on_click=book,
                bgcolor=ft.Colors.BLUE_400,
                color=ft.Colors.WHITE,
                width=150,
                height=40,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=20)
                )
            ),
            stat_r
        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.START),
        padding=30,
        bgcolor=ft.Colors.GREY_600,
        border_radius=10,
        width=300
    )
    
    rider_v = ft.Container(
        content=ft.Row([
            left_controls,
            ft.Container(width=20),  # Spacer
            map_placeholder
        ], alignment=ft.MainAxisAlignment.CENTER, expand=True),
        alignment=ft.alignment.center,
        expand=True
    )
    
    # Driver UI
    driver_table_rows = []
    
    def load_pending(_=None):
        driver_table_rows.clear()
        try:
            resp = requests.get(f"{API}/rides/pending")
            for r in resp.json():
                driver_table_rows.append(r)
        except:
            # Add sample data for demonstration
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
    
    # Driver table content
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
    
    # Driver left side controls
    driver_left_controls = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.DIRECTIONS_CAR, size=24, color=ft.Colors.WHITE),
                ft.Text("Driver", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ], spacing=10),
            ft.Container(height=20),  # Spacer
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
    
    driver_v = ft.Container(
        content=ft.Row([
            driver_left_controls,
            ft.Container(width=20),  # Spacer
            map_placeholder
        ], alignment=ft.MainAxisAlignment.CENTER, expand=True),
        alignment=ft.alignment.center,
        expand=True
    )
    
    # Admin UI
    def show_stats(e):
        try:
            data = requests.get(f"{API}/analytics/ride_counts").json()
            days = [d["day"] for d in data]
            cnts = [d["count"] for d in data]
            plt.figure()
            plt.bar(days, cnts)
            plt.title("Rides per Weekday")
            plt.xlabel("Day (1=Sunday)")
            plt.ylabel("Count")
            plt.tight_layout()
            plt.show()
        except:
            pass
    
    # Chart placeholder
    chart_placeholder = ft.Container(
        content=ft.Column([
            # Create a simple bar chart visualization
            ft.Row([
                ft.Container(
                    width=20,
                    height=40,
                    bgcolor=ft.Colors.GREEN_400,
                    border_radius=2
                ),
                ft.Container(
                    width=20,
                    height=60,
                    bgcolor=ft.Colors.ORANGE_400,
                    border_radius=2
                ),
                ft.Container(
                    width=20,
                    height=80,
                    bgcolor=ft.Colors.BLUE_400,
                    border_radius=2
                ),
            ], spacing=5, alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(
                content=ft.Icon(
                    ft.Icons.TRENDING_UP,
                    size=30,
                    color=ft.Colors.ORANGE_400
                ),
                margin=ft.margin.only(top=10)
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=250,
        height=150,
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        border=ft.border.all(1, ft.Colors.GREY_300),
        alignment=ft.alignment.center
    )
    
    # Admin left side controls
    admin_left_controls = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=24, color=ft.Colors.WHITE),
                ft.Text("Admin", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ], spacing=10),
            ft.Container(height=20),  # Spacer
            ft.Text(
                "Statistics",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            ft.Container(height=10),
            chart_placeholder,
            ft.Container(height=20),
            ft.ElevatedButton(
                "Show Weekly Ride Stats",
                on_click=show_stats,
                bgcolor=ft.Colors.BLUE_400,
                color=ft.Colors.WHITE,
                width=200,
                height=40,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=20)
                )
            )
        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.START),
        padding=30,
        bgcolor=ft.Colors.GREY_600,
        border_radius=10,
        width=350
    )
    
    admin_v = ft.Container(
        content=admin_left_controls,
        alignment=ft.alignment.center,
        expand=True
    )
    
    # Tab content switcher
    def tab_changed(e):
        # Clear all controls
        page.controls.clear()
        
        # Create main content with the selected tab
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
    
    # Wrap everything in a centered column
    main_content = ft.Column([
        ft.Container(
            content=tabs,
            alignment=ft.alignment.center,
            width=800
        ),
        rider_v
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
    
    page.add(main_content)

ft.app(target=main)