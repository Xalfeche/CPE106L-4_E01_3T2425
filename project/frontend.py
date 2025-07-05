import flet as ft
import requests
import matplotlib.pyplot as plt

API = "http://localhost:8000"

def main(page: ft.Page):
    page.title = "CommunityConnect"
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
    name    = ft.TextField(label="Name", width=300)
    pickup  = ft.TextField(label="Pickup", width=300)
    dropoff = ft.TextField(label="Drop-off", width=300)
    stat_r  = ft.Text()

    def book(e):
        if not (name.value and pickup.value and dropoff.value):
            stat_r.value = "❌ Fill all fields"
            page.update(); return
        res = requests.post(f"{API}/rides/request", json={
            "rider_name": name.value,
            "pickup_location": pickup.value,
            "dropoff_location": dropoff.value,
            "requested_time": "ASAP"
        })
        if res.ok:
            d = res.json()
            stat_r.value = f"✅ {d['distance_m']}m, {d['duration_s']}s"
        else:
            stat_r.value = "❌ Error"
        page.update()

    rider_v = ft.Column([
        ft.Text("Book a Ride", size=20, weight="bold"),
        name, pickup, dropoff,
        ft.ElevatedButton("Submit", on_click=book),
        stat_r
    ], spacing=10)

    # Driver UI
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Pickup")),
            ft.DataColumn(ft.Text("Drop-off")),
            ft.DataColumn(ft.Text("Action")),
        ],
        rows=[]
    )

    def load_pending(_=None):
        table.rows.clear()
        resp = requests.get(f"{API}/rides/pending")
        for r in resp.json():
            btn = ft.ElevatedButton("Accept", on_click=lambda e, id=r["_id"]: accept(id))
            table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r["_id"]))),
                ft.DataCell(ft.Text(r["pickup_location"])),
                ft.DataCell(ft.Text(r["dropoff_location"])),
                ft.DataCell(btn),
            ]))
        page.update()

    def accept(rid):
        requests.post(f"{API}/rides/accept/{rid}")
        load_pending()

    driver_v = ft.Column([
        ft.Text("Pending Rides", size=20, weight="bold"),
        table,
        ft.ElevatedButton("Refresh", on_click=load_pending)
    ], spacing=10)

    # Admin UI
    def show_stats(e):
        data = requests.get(f"{API}/analytics/ride_counts").json()
        days  = [d["day"] for d in data]
        cnts  = [d["count"] for d in data]
        plt.figure()
        plt.bar(days, cnts)
        plt.title("Rides per Weekday")
        plt.xlabel("Day (1=Sunday)")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.show()

    admin_v = ft.Column([
        ft.Text("Analytics", size=20, weight="bold"),
        ft.ElevatedButton("Show Weekly Ride Stats", on_click=show_stats)
    ], spacing=10)

    # Tab content switcher
    def tab_changed(e):
        page.controls.pop()
        page.add([rider_v, driver_v, admin_v][e.control.selected_index])
        page.update()

    tabs.on_change = tab_changed
    page.add(tabs, rider_v)

ft.app(target=main)
