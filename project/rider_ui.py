import flet as ft
import requests

API = "http://localhost:8000"

def create_rider_ui(page):
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
    
    left_controls = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PERSON, size=24, color=ft.Colors.WHITE),
                ft.Text("Rider", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ], spacing=10),
            ft.Container(height=20),
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
    
    return ft.Container(
        content=ft.Row([
            left_controls,
            ft.Container(width=20),
            map_placeholder
        ], alignment=ft.MainAxisAlignment.CENTER, expand=True),
        alignment=ft.alignment.center,
        expand=True
    )