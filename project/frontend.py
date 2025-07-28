import flet as ft
import requests
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import io
import base64
from datetime import datetime
import time
import json

API = "http://127.0.0.1:5000"

# --- NEW MAP GENERATION FUNCTION ---
def generate_map_with_pin_matplotlib(longitude, latitude, title="Pinned Location"):
    plt.ioff() # Turn off interactive mode to prevent showing interactive plots
    fig, ax = plt.subplots(figsize=(6, 4)) # Adjusted size for better fit in Flet
    
    # Set limits based on the pin location, giving some surrounding area
    # Simple +/- 0.05 degrees for demonstration zoom, adjust as needed
    lat_min, lat_max = latitude - 0.05, latitude + 0.05
    lon_min, lon_max = longitude - 0.05, longitude + 0.05

    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    
    # Plot the pin (red circle marker)
    ax.plot(longitude, latitude, 'ro', markersize=10, label='Pinned Location') 
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True)
    ax.legend()

    # Save plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    plt.close(fig) # Close the figure to free memory

    # Encode to base64
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Default coordinates for Taytay, Calabarzon, Philippines
DEFAULT_LATITUDE = 14.5688
DEFAULT_LONGITUDE = 121.1354


def main(page: ft.Page):
    page.title = "CommunityConnect"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_100
    page.window.width = 1200
    page.window.height = 800
    page.window.maximized = True
    
    token = None
    current_user = {"name": "", "email": "", "is_admin": False}
    
    # Login UI
    login_email = ft.TextField(
        label="Email",
        width=300,
        border_radius=25,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
    )
    
    login_password = ft.TextField(
        label="Password",
        password=True,
        width=300,
        border_radius=25,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
    )
    login_status = ft.Text()
    
    # Register UI
    register_name = ft.TextField(
        label="Name",
        width=300,
        border_radius=25,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
    )
    register_email = ft.TextField(
        label="Email",
        width=300,
        border_radius=25,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
    )
    register_password = ft.TextField(
        label="Password",
        password=True,
        width=300,
        border_radius=25,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
    )
    register_confirm = ft.TextField(
        label="Confirm Password",
        password=True,
        width=300,
        border_radius=25,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
    )
    register_status = ft.Text()
    
    def show_login(e=None):
        page.controls.clear()
        page.add(ft.Column([
            ft.Text("CommunityConnect", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
            ft.Text("Login", size=30, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            login_email,
            ft.Container(height=10),
            login_password,
            ft.Container(height=20),
            ft.ElevatedButton("Login", on_click=do_login, width=150, height=40),
            ft.Container(height=10),
            login_status,
            ft.Container(height=20),
            ft.TextButton("Don't have an account? Register", on_click=show_register)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        page.update()
    
    def show_register(e=None):
        page.controls.clear()
        page.add(ft.Column([
            ft.Text("CommunityConnect", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
            ft.Text("Register", size=30, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            register_name,
            ft.Container(height=10),
            register_email,
            ft.Container(height=10),
            register_password,
            ft.Container(height=10),
            register_confirm,
            ft.Container(height=20),
            ft.ElevatedButton("Register", on_click=do_register, width=150, height=40),
            ft.Container(height=10),
            register_status,
            ft.Container(height=20),
            ft.TextButton("Already have an account? Login", on_click=show_login)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        page.update()
    
    def do_login(e):
        nonlocal token, current_user
        if not (login_email.value and login_password.value):
            login_status.value = "❌ Fill all fields"
            login_status.color = ft.Colors.RED_400
            page.update()
            return
        
        try:
            res = requests.post(f"{API}/login", data={
                "username": login_email.value,
                "password": login_password.value
            })
            if res.ok:
                data = res.json()
                token = data["access_token"]
                
                user_res = requests.get(f"{API}/user/me", headers={"Authorization": f"Bearer {token}"})
                if user_res.ok:
                    current_user = user_res.json()
                    show_main_app()
                else:
                    login_status.value = "❌ Failed to get user details"
                    login_status.color = ft.Colors.RED_400
            else:
                login_status.value = f"❌ Login failed: {res.text}"
                login_status.color = ft.Colors.RED_400
        except Exception as ex:
            login_status.value = f"❌ Connection error: {str(ex)}"
            login_status.color = ft.Colors.RED_400
        page.update()
    
    def do_register(e):
        if not (register_name.value and register_email.value and register_password.value and register_confirm.value):
            register_status.value = "❌ Fill all fields"
            register_status.color = ft.Colors.RED_400
            page.update()
            return
        
        if register_password.value != register_confirm.value:
            register_status.value = "❌ Passwords do not match"
            register_status.color = ft.Colors.RED_400
            page.update()
            return
        
        try:
            res = requests.post(f"{API}/register", json={
                "name": register_name.value,
                "email": register_email.value,
                "password": register_password.value
            })
            if res.ok:
                register_status.value = "✅ Registration successful! Please login."
                register_status.color = ft.Colors.GREEN_400
                # Clear fields
                register_name.value = ""
                register_email.value = ""
                register_password.value = ""
                register_confirm.value = ""
            else:
                register_status.value = f"❌ Registration failed: {res.text}"
                register_status.color = ft.Colors.RED_400
        except Exception as ex:
            register_status.value = f"❌ Connection error: {str(ex)}"
            register_status.color = ft.Colors.RED_400
        page.update()
    
    def logout(e):
        nonlocal token, current_user
        token = None
        current_user = {"name": "", "email": "", "is_admin": False}
        show_login()
    
    def show_main_app():
        page.controls.clear()
        
        # Create tabs based on user role
        tab_list = [
            ft.Tab(text="Rider", icon=ft.Icons.PERSON),
            ft.Tab(text="Driver", icon=ft.Icons.DIRECTIONS_CAR),
        ]
        
        if current_user.get("is_admin", False):
            tab_list.append(ft.Tab(text="Admin", icon=ft.Icons.BAR_CHART))
        
        tabs = ft.Tabs(
            selected_index=0,
            tabs=tab_list,
            expand=1,
        )
        
        # Header with user info and logout
        header = ft.Container(
            content=ft.Row([
                ft.Text("CommunityConnect", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
                ft.Row([
                    ft.Text(f"Welcome, {current_user.get('name', '')}", size=16),
                    ft.ElevatedButton("Logout", on_click=logout, bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE)
                ], spacing=20)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            margin=ft.margin.only(bottom=20)
        )
        
        page.add(header, tabs)
        
        # Update tabs content
        tabs.tabs[0].content = create_rider_tab()
        tabs.tabs[1].content = create_driver_tab()
        if current_user.get("is_admin", False):
            tabs.tabs[2].content = create_admin_tab()
        
        page.update()
    
    def create_rider_tab():
        # Rider UI
        pickup = ft.TextField(
            label="Pick Up (Long,Lat)",
            width=300,
            border_radius=25,
            bgcolor=ft.Colors.WHITE,
            border_color=ft.Colors.GREY_300,
            content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
            hint_text="e.g., -73.985,40.758"
        )
        
        dropoff = ft.TextField(
            label="Drop Off (Long,Lat)",
            width=300,
            border_radius=25,
            bgcolor=ft.Colors.WHITE,
            border_color=ft.Colors.GREY_300,
            content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
            hint_text="e.g., -74.006,40.712"
        )
        
        stat_r = ft.Text(color=ft.Colors.RED_400)

        # Map image control
        map_image_control = ft.Image(
            src_base64=None, # Will be set on initial load or button click
            width=400,
            height=300,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10,
            border=ft.border.all(2, ft.Colors.BLUE_GREY_200)
        )

        def update_map(e=None):
            try:
                coords_str = pickup.value
                if not coords_str:
                    map_image_control.src_base64 = generate_map_with_pin_matplotlib(DEFAULT_LONGITUDE, DEFAULT_LATITUDE, "Taytay, Philippines (Default)")
                    stat_r.value = "" # Clear status if coords are empty
                    page.update()
                    return

                lon_str, lat_str = coords_str.split(',')
                lon = float(lon_str.strip())
                lat = float(lat_str.strip())
                map_image_control.src_base64 = generate_map_with_pin_matplotlib(lon, lat, f"Pickup: {lat:.4f}, {lon:.4f}")
                stat_r.value = "Map updated successfully with pickup location!"
                stat_r.color = ft.Colors.GREEN_400
                page.update()
            except ValueError:
                stat_r.value = "❌ Invalid coordinates format. Use Longitude,Latitude (e.g., -73.985,40.758)"
                stat_r.color = ft.Colors.RED_400
                page.update()
            except Exception as ex:
                stat_r.value = f"❌ Map error: {str(ex)}"
                stat_r.color = ft.Colors.RED_400
                page.update()
        
        # Initial map display when rider tab is created/refreshed
        # Use current pickup value if available, otherwise default.
        if pickup.value: # If the text field already has a value (e.g., after a partial interaction)
            try:
                lon_str, lat_str = pickup.value.split(',')
                initial_lon, initial_lat = float(lon_str.strip()), float(lat_str.strip())
                map_image_control.src_base64 = generate_map_with_pin_matplotlib(initial_lon, initial_lat, f"Pickup: {initial_lat:.4f}, {initial_lon:.4f}")
            except ValueError:
                # Fallback to default if parsing fails
                map_image_control.src_base64 = generate_map_with_pin_matplotlib(DEFAULT_LONGITUDE, DEFAULT_LATITUDE, "Taytay, Philippines (Default)")
        else:
            map_image_control.src_base64 = generate_map_with_pin_matplotlib(DEFAULT_LONGITUDE, DEFAULT_LATITUDE, "Taytay, Philippines (Default)")


        def book(e):
            if not (pickup.value and dropoff.value):
                stat_r.value = "❌ Fill all fields"
                stat_r.color = ft.Colors.RED_400
                page.update()
                return
            
            try:
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                res = requests.post(f"{API}/rides/request", json={
                    "pickup_location": pickup.value,
                    "dropoff_location": dropoff.value,
                    "requested_time": "ASAP"
                }, headers=headers)
                if res.ok:
                    d = res.json()
                    stat_r.value = f"✅ Ride requested! Distance: {d['distance_m']:.0f}m, Duration: {d['duration_s']:.0f}s"
                    stat_r.color = ft.Colors.GREEN_400
                    # Clear fields and update map to default after successful booking
                    pickup.value = ""
                    dropoff.value = ""
                    map_image_control.src_base64 = generate_map_with_pin_matplotlib(DEFAULT_LONGITUDE, DEFAULT_LATITUDE, "Taytay, Philippines (Default)")
                else:
                    stat_r.value = f"❌ Error: {res.text}"
                    stat_r.color = ft.Colors.RED_400
            except Exception as ex:
                stat_r.value = f"❌ Connection Error: {str(ex)}"
                stat_r.color = ft.Colors.RED_400
            page.update()
        
        # Structure the rider tab content
        left_controls = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=24, color=ft.Colors.WHITE),
                    ft.Text("Request a Ride", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                ], spacing=10),
                ft.Container(height=20),
                ft.Text(f"User: {current_user.get('name', '')} ({current_user.get('email', '')})", color=ft.Colors.WHITE),
                ft.Container(height=20),
                pickup,
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Show Pickup on Map",
                    on_click=update_map,
                    bgcolor=ft.Colors.PURPLE_400,
                    color=ft.Colors.WHITE,
                    width=200,
                    height=40,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20))
                ),
                ft.Container(height=10),
                dropoff,
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Request Ride",
                    on_click=book,
                    bgcolor=ft.Colors.BLUE_400,
                    color=ft.Colors.WHITE,
                    width=200,
                    height=45,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=20)
                    )
                ),
                ft.Container(height=10),
                stat_r
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.START),
            padding=30,
            bgcolor=ft.Colors.GREY_600,
            border_radius=10,
            width=350
        )
        
        return ft.Container(
            content=ft.Row([
                left_controls,
                ft.Container(width=50),
                ft.Column([
                    map_image_control, # This is now the actual map
                    ft.Text(
                        "Enter coordinates (Long,Lat) for pickup and click 'Show Pickup on Map'.",
                        size=14,
                        color=ft.Colors.BLACK54,
                        text_align=ft.TextAlign.CENTER
                    )
                ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   spacing=10,
                   width=400, # Match width of map_image_control
                   height=350, # Sufficient height for map and text
                   bgcolor=ft.Colors.BLUE_GREY_100, # Background to match old placeholder
                   border_radius=10,
                   border=ft.border.all(2, ft.Colors.BLUE_GREY_200),
                   alignment=ft.alignment.center
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True,
            padding=20
        )
    
    def create_driver_tab():
        driver_table_rows = []
        driver_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Rider")),
                ft.DataColumn(ft.Text("Pickup")),
                ft.DataColumn(ft.Text("Dropoff")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[]
        )
        
        status_text = ft.Text("Loading pending rides...", color=ft.Colors.BLUE_400)
        
        def load_pending():
            driver_table_rows.clear()
            driver_table.rows.clear()
            try:
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                resp = requests.get(f"{API}/rides/pending", headers=headers)
                if resp.ok:
                    rides = resp.json()
                    driver_table_rows.extend(rides)
                    
                    if not rides:
                        status_text.value = "No pending rides available"
                        status_text.color = ft.Colors.ORANGE_400
                    else:
                        status_text.value = f"Found {len(rides)} pending rides"
                        status_text.color = ft.Colors.GREEN_400
                        
                        for r in rides:
                            driver_table.rows.append(
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(ft.Text(str(r["id"]))),
                                        ft.DataCell(ft.Text(r["rider_name"])),
                                        ft.DataCell(ft.Text(r["pickup_location"][:20] + "..." if len(r["pickup_location"]) > 20 else r["pickup_location"])),
                                        ft.DataCell(ft.Text(r["dropoff_location"][:20] + "..." if len(r["dropoff_location"]) > 20 else r["dropoff_location"])),
                                        ft.DataCell(
                                            ft.Row([
                                                ft.IconButton(
                                                    icon=ft.Icons.CHECK_CIRCLE,
                                                    icon_color=ft.Colors.GREEN_400,
                                                    icon_size=24,
                                                    on_click=lambda e, ride_id=r["id"]: accept_ride(ride_id)
                                                ),
                                            ], spacing=5)
                                        ),
                                    ]
                                )
                            )
                else:
                    status_text.value = f"Failed to load rides: {resp.text}"
                    status_text.color = ft.Colors.RED_400
            except Exception as ex:
                status_text.value = f"Connection error: {str(ex)}"
                status_text.color = ft.Colors.RED_400
            page.update()
        
        def accept_ride(ride_id):
            try:
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                resp = requests.post(f"{API}/rides/accept/{ride_id}", headers=headers)
                if resp.ok:
                    status_text.value = f"✅ Ride {ride_id} accepted successfully!"
                    status_text.color = ft.Colors.GREEN_400
                    load_pending()  # Refresh the list
                else:
                    status_text.value = f"❌ Failed to accept ride: {resp.text}"
                    status_text.color = ft.Colors.RED_400
            except Exception as ex:
                status_text.value = f"❌ Connection error: {str(ex)}"
                status_text.color = ft.Colors.RED_400
            page.update()
        
        # Load pending rides initially
        load_pending()
        
        driver_controls = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.DIRECTIONS_CAR, size=24, color=ft.Colors.WHITE),
                    ft.Text("Driver Dashboard", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                ], spacing=10),
                ft.Container(height=20),
                ft.Text(f"Driver: {current_user.get('name', '')}", color=ft.Colors.WHITE),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Refresh Rides",
                    on_click=lambda e: load_pending(),
                    bgcolor=ft.Colors.BLUE_400,
                    color=ft.Colors.WHITE,
                    width=200,
                    height=40,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=20)
                    )
                ),
                ft.Container(height=10),
                status_text,
                ft.Container(height=20),
                ft.Container(
                    content=driver_table,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    padding=10,
                    width=700,
                    height=300
                )
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
            bgcolor=ft.Colors.GREY_600,
            border_radius=10,
            width=800
        )
        
        return ft.Container(
            content=driver_controls,
            alignment=ft.alignment.center,
            expand=True,
            padding=20
        )
    
    def create_admin_tab():
        def show_stats(e):
            try:
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                data = requests.get(f"{API}/analytics/ride_counts", headers=headers).json()
                days = [d["day"] for d in data]
                cnts = [d["count"] for d in data]
                
                plt.figure(figsize=(10, 6))
                plt.bar(days, cnts, color='skyblue')
                plt.title("Rides per Weekday", fontsize=16)
                plt.xlabel("Day of Week (1=Sunday)", fontsize=12)
                plt.ylabel("Number of Rides", fontsize=12)
                plt.xticks(range(1, 8), ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.tight_layout()
                plt.show()
            except Exception as ex:
                print(f"Error generating chart: {ex}")
        
        def show_user_stats(e):
            try:
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                data = requests.get(f"{API}/analytics/user_rides", headers=headers).json()
                users = [d["rider_name"] for d in data]
                cnts = [d["count"] for d in data]
                
                plt.figure(figsize=(10, 6))
                plt.bar(users, cnts, color='lightgreen')
                plt.title("Rides per User", fontsize=16)
                plt.xlabel("User", fontsize=12)  
                plt.ylabel("Number of Rides", fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.tight_layout()
                plt.show()
            except Exception as ex:
                print(f"Error generating chart: {ex}")
                
        def load_recent_rides():
            try:
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                resp = requests.get(f"{API}/analytics/recent_rides", headers=headers)
                if resp.ok:
                    return resp.json()
                return []
            except:
                return []
        
        recent_rides_data = load_recent_rides()
        recent_rides_rows = []
        for ride in recent_rides_data:
            recent_rides_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(ride.get("id", "")))),
                        ft.DataCell(ft.Text(ride.get("rider_name", ""))),
                        ft.DataCell(ft.Text(ride.get("pickup_location", "")[:20] + "..." if len(ride.get("pickup_location", "")) > 20 else ride.get("pickup_location", ""))),
                        ft.DataCell(ft.Text(ride.get("dropoff_location", "")[:20] + "..." if len(ride.get("dropoff_location", "")) > 20 else ride.get("dropoff_location", ""))),
                        ft.DataCell(ft.Text(ride.get("status", ""))),
                    ]
                )
            )
        
        admin_controls = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=24, color=ft.Colors.WHITE),
                    ft.Text("Admin Dashboard", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                ], spacing=10),
                ft.Container(height=20),
                ft.Text(f"Admin: {current_user.get('name', '')}", color=ft.Colors.WHITE),
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton(
                        "Show Weekly Ride Stats",
                        on_click=show_stats,
                        bgcolor=ft.Colors.BLUE_400,
                        color=ft.Colors.WHITE,
                        width=250,
                        height=50,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=20)
                        )
                    ),
                    ft.Container(width=20),
                    ft.ElevatedButton(
                        "Show User Ride Stats",
                        on_click=show_user_stats,
                        bgcolor=ft.Colors.GREEN_400,
                        color=ft.Colors.WHITE,
                        width=250,
                        height=50,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=20)
                        )
                    )
                ]),
                ft.Container(height=30),
                ft.Text("Recent Rides", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(height=10),
                ft.Container(
                    content=ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
                            ft.DataColumn(ft.Text("Rider", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
                            ft.DataColumn(ft.Text("Pickup", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
                            ft.DataColumn(ft.Text("Dropoff", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
                            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
                        ],
                        rows=recent_rides_rows,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                    ),
                    padding=10,
                    width=800,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10
                )
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
            bgcolor=ft.Colors.GREY_600,
            border_radius=10,
            width=900
        )
        
        return ft.Container(
            content=admin_controls,
            alignment=ft.alignment.center,
            expand=True,
            padding=20
        )
    
    show_login()

if __name__ == "__main__":
    ft.app(target=main, port=8080)