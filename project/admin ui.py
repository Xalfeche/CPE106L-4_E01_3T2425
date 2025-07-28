import flet as ft
import requests
import matplotlib.pyplot as plt

API = "http://localhost:8000"

def create_admin_ui(page):
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
    
    chart_placeholder = ft.Container(
        content=ft.Column([
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
    
    admin_left_controls = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=24, color=ft.Colors.WHITE),
                ft.Text("Admin", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ], spacing=10),
            ft.Container(height=20),
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
    
    return ft.Container(
        content=admin_left_controls,
        alignment=ft.alignment.center,
        expand=True
    )