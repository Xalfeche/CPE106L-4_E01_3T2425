import flet as ft
import requests
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64
import math
from PIL import Image, ImageDraw
import time

class CommunityConnectApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.token = None
        self.current_user = None
        self.backend_url = "http://localhost:5000"
        
        # Map variables
        self.selected_pickup = None  # (x, y) coordinates on map
        self.selected_dropoff = None  # (x, y) coordinates on map
        self.active_ride = None  # For driver's current ride
        
        # Setup page
        self.page.title = "CommunityConnect - Ride Sharing"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.padding = 0
        
        # Initialize UI
        self.init_auth_ui()
        
    def init_auth_ui(self):
        """Initialize authentication UI"""
        self.page.clean()
        
        # Login form
        self.email_field = ft.TextField(
            label="Email",
            width=300,
            autofocus=True
        )
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        # Register form fields
        self.reg_name_field = ft.TextField(label="Name", width=300)
        self.reg_email_field = ft.TextField(label="Email", width=300)
        self.reg_password_field = ft.TextField(label="Password", password=True, width=300)
        self.reg_confirm_field = ft.TextField(label="Confirm Password", password=True, width=300)
        
        # Status text
        self.status_text = ft.Text(color="red")
        
        # Login tab
        login_tab = ft.Tab(
            text="Login",
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Login to CommunityConnect", size=24, weight=ft.FontWeight.BOLD),
                    self.email_field,
                    self.password_field,
                    ft.ElevatedButton("Login", on_click=self.login),
                    self.status_text
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                padding=40
            )
        )
        
        # Register tab
        register_tab = ft.Tab(
            text="Register",
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Register for CommunityConnect", size=24, weight=ft.FontWeight.BOLD),
                    self.reg_name_field,
                    self.reg_email_field,
                    self.reg_password_field,
                    self.reg_confirm_field,
                    ft.ElevatedButton("Register", on_click=self.register),
                    self.status_text,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                padding=40
            )
        )
        
        # Main container
        main_container = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(
                        "CommunityConnect",
                        size=40,
                        weight=ft.FontWeight.BOLD,
                        color="white"
                    ),
                    bgcolor="blue",
                    padding=20,
                    alignment=ft.alignment.center
                ),
                ft.Tabs(
                    tabs=[login_tab, register_tab],
                    expand=True
                )
            ]),
            expand=True
        )
        
        self.page.add(main_container)
        self.page.update()
    
    def show_status(self, message, is_error=False):
        """Show status message"""
        self.status_text.value = message
        self.status_text.color = "red" if is_error else "green"
        self.page.update()
    
    def login(self, e):
        """Handle login"""
        try:
            data = {
                'username': self.email_field.value,
                'password': self.password_field.value
            }
            
            response = requests.post(f"{self.backend_url}/login", data=data)
            
            if response.status_code == 200:
                result = response.json()
                self.token = result['access_token']
                
                # Get user details
                headers = {'Authorization': f'Bearer {self.token}'}
                user_response = requests.get(f"{self.backend_url}/user/me", headers=headers)
                
                if user_response.status_code == 200:
                    self.current_user = user_response.json()
                    self.init_main_ui()
                else:
                    self.show_status("Failed to get user details", True)
            else:
                self.show_status("Login failed: Invalid credentials", True)
        except Exception as ex:
            self.show_status(f"Connection error: {str(ex)}", True)
    
    def register(self, e):
        """Handle registration"""
        if self.reg_password_field.value != self.reg_confirm_field.value:
            self.show_status("Passwords do not match", True)
            return
        
        try:
            data = {
                'name': self.reg_name_field.value,
                'email': self.reg_email_field.value,
                'password': self.reg_password_field.value
            }
            
            response = requests.post(f"{self.backend_url}/register", json=data)
            
            if response.status_code == 201:
                self.show_status("Registration successful! Please login.")
                # Clear form
                for field in [self.reg_name_field, self.reg_email_field, self.reg_password_field, self.reg_confirm_field]:
                    field.value = ""
                self.page.update()
            else:
                self.show_status("Registration failed", True)
        except Exception as ex:
            self.show_status(f"Connection error: {str(ex)}", True)
    
    def init_main_ui(self):
        """Initialize main application UI"""
        self.page.clean()
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Text(f"Welcome, {self.current_user['name']}!", size=20, weight=ft.FontWeight.BOLD, color="white"),
                ft.ElevatedButton("Logout", on_click=self.logout, bgcolor="red")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="blue",
            padding=20
        )
        
        # Create tabs
        tabs = [
            ft.Tab(text="🚗 Rider", content=self.create_rider_tab()),
            ft.Tab(text="🚙 Driver", content=self.create_driver_tab())
        ]
        
        if self.current_user.get('is_admin', False):
            tabs.append(ft.Tab(text="📊 Admin", content=self.create_admin_tab()))
        
        # Main container
        main_container = ft.Column([
            header,
            ft.Tabs(tabs=tabs, expand=True)
        ], expand=True)
        
        self.page.add(main_container)
        self.page.update()
        
        # Load initial data
        self.load_pending_rides()
        if self.current_user.get('is_admin', False):
            self.load_admin_data()
    
    def create_rider_tab(self):
        """Create rider interface with interactive map for pinning"""
        # Map display
        self.route_map = ft.Container(
            content=ft.Text("Tap on the map to set pickup and dropoff locations", text_align=ft.TextAlign.CENTER),
            bgcolor="#f5f5f5",
            padding=20,
            border_radius=10,
            height=300,
            width=600,
            on_click=self.handle_map_tap
        )
        
        # Coordinate displays
        self.pickup_display = ft.Text("Pickup: Not set")
        self.dropoff_display = ft.Text("Dropoff: Not set")
        
        # Route info display
        self.route_info = ft.Container(
            content=ft.Column([
                ft.Text("Route Information", weight=ft.FontWeight.BOLD),
                ft.Text("Set pickup and dropoff locations to see route details")
            ]),
            bgcolor="#e3f2fd",
            padding=15,
            border_radius=5,
            visible=False
        )
        
        # Status text
        self.ride_status = ft.Text(color="green")
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Request a Ride", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Tap on the map to set pickup (first tap) and dropoff (second tap) locations:"),
                        self.route_map,
                        ft.Row([self.pickup_display, self.dropoff_display]),
                        ft.Row([
                            ft.ElevatedButton("Calculate Route", on_click=self.calculate_route),
                            ft.ElevatedButton("Clear", on_click=self.clear_route)
                        ]),
                        self.route_info,
                        ft.ElevatedButton(
                            "Request Ride",
                            on_click=self.request_ride,
                            bgcolor="green",
                            color="white"
                        ),
                        self.ride_status
                    ], spacing=15),
                    bgcolor="#f5f5f5",
                    padding=20,
                    border_radius=10
                )
            ], spacing=20),
            padding=20
        )
    
    def handle_map_tap(self, e: ft.TapEvent):
        """Handle tap on map to set pickup/dropoff locations"""
        if not self.selected_pickup:
            self.selected_pickup = (e.local_x, e.local_y)
            self.pickup_display.value = f"Pickup: {e.local_x:.1f}, {e.local_y:.1f}"
        elif not self.selected_dropoff:
            self.selected_dropoff = (e.local_x, e.local_y)
            self.dropoff_display.value = f"Dropoff: {e.local_x:.1f}, {e.local_y:.1f}"
        self.update_map()
        self.page.update()

    def update_map(self):
        """Update the map visualization with pins and route"""
        try:
            img_width, img_height = 580, 280
            img = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(img)
            # Draw grid
            for i in range(0, img_width, 50):
                draw.line([(i, 0), (i, img_height)], fill='#f0f0f0', width=1)
            for i in range(0, img_height, 50):
                draw.line([(0, i), (img_width, i)], fill='#f0f0f0', width=1)
            # Draw pickup marker
            if self.selected_pickup:
                x, y = self.selected_pickup
                marker_size = 8
                draw.ellipse([
                    x - marker_size, y - marker_size,
                    x + marker_size, y + marker_size
                ], fill='green', outline='darkgreen', width=2)
                draw.text((x + 10, y - 15), "Pickup", fill='green')
            # Draw dropoff marker
            if self.selected_dropoff:
                x, y = self.selected_dropoff
                marker_size = 8
                draw.ellipse([
                    x - marker_size, y - marker_size,
                    x + marker_size, y + marker_size
                ], fill='red', outline='darkred', width=2)
                draw.text((x + 10, y - 15), "Dropoff", fill='red')
            # Draw route line
            if self.selected_pickup and self.selected_dropoff:
                x1, y1 = self.selected_pickup
                x2, y2 = self.selected_dropoff
                draw.line([(x1, y1), (x2, y2)], fill='#667eea', width=4)
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            self.route_map.content = ft.Image(
                src_base64=image_base64,
                width=580,
                height=280,
                fit=ft.ImageFit.CONTAIN
            )
        except Exception as ex:
            print(f"Error updating map: {ex}")
    
    def calculate_route(self, e):
        """Calculate route between pickup and dropoff"""
        if not self.selected_pickup or not self.selected_dropoff:
            self.ride_status.value = "Please select both pickup and dropoff points"
            self.ride_status.color = "red"
            self.page.update()
            return
        
        try:
            # Calculate distance
            x1, y1 = self.selected_pickup
            x2, y2 = self.selected_dropoff
            dx = x2 - x1
            dy = y2 - y1
            distance_km = math.sqrt(dx*dx + dy*dy) * 0.1  # Scale to km
            
            # Estimate time (assuming average speed of 30 km/h in city)
            estimated_time = (distance_km / 30) * 60  # minutes
            
            # Update route info
            self.route_info.content = ft.Column([
                ft.Text("Route Information", weight=ft.FontWeight.BOLD),
                ft.Text(f"Distance: {distance_km:.1f} km"),
                ft.Text(f"Estimated time: {estimated_time:.0f} minutes"),
                ft.Text(f"Pickup: {x1:.1f}, {y1:.1f}"),
                ft.Text(f"Dropoff: {x2:.1f}, {y2:.1f}")
            ])
            self.route_info.visible = True
            
            self.ride_status.value = "Route calculated successfully!"
            self.ride_status.color = "green"
            
        except Exception as ex:
            self.ride_status.value = f"Error calculating route: {str(ex)}"
            self.ride_status.color = "red"
        
        self.page.update()
    
    def clear_route(self, e):
        """Clear route information"""
        self.selected_pickup = None
        self.selected_dropoff = None
        self.route_info.visible = False
        self.pickup_display.value = "Pickup: Not set"
        self.dropoff_display.value = "Dropoff: Not set"
        self.ride_status.value = ""
        self.route_map.content = ft.Text("Tap on the map to set pickup and dropoff locations", text_align=ft.TextAlign.CENTER)
        self.page.update()
    
    def request_ride(self, e):
        """Request a ride"""
        if not self.selected_pickup or not self.selected_dropoff:
            self.ride_status.value = "Please select both pickup and dropoff points"
            self.ride_status.color = "red"
            self.page.update()
            return
        
        try:
            # Convert screen coordinates to string
            x1, y1 = self.selected_pickup
            x2, y2 = self.selected_dropoff
            pickup_str = f"{x1},{y1}"
            dropoff_str = f"{x2},{y2}"
            
            headers = {'Authorization': f'Bearer {self.token}'}
            data = {
                'pickup_location': pickup_str,
                'dropoff_location': dropoff_str,
                'requested_time': 'ASAP'
            }
            
            response = requests.post(f"{self.backend_url}/rides/request", json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.ride_status.value = f"Ride requested successfully! Distance: {result.get('distance_m', 0):.0f}m"
                self.ride_status.color = "green"
                self.clear_route(None)
            else:
                self.ride_status.value = "Failed to request ride"
                self.ride_status.color = "red"
                
        except Exception as ex:
            self.ride_status.value = f"Error: {str(ex)}"
            self.ride_status.color = "red"
        
        self.page.update()
    
    def create_driver_tab(self):
        """Create driver interface with active ride view"""
        self.pending_rides_column = ft.Column(spacing=10)
        
        # Container for active ride
        self.active_ride_container = ft.Container(visible=False)
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Pending Rides", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("Refresh", on_click=self.load_pending_rides)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.active_ride_container,
                ft.Container(
                    content=self.pending_rides_column,
                    bgcolor="#f5f5f5",
                    padding=20,
                    border_radius=10,
                    expand=True
                )
            ], spacing=20),
            padding=20
        )
    
    def load_pending_rides(self, e=None):
        """Load pending rides for driver"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{self.backend_url}/rides/pending", headers=headers)
            
            if response.status_code == 200:
                rides = response.json()
                self.pending_rides_column.controls.clear()
                
                if not rides:
                    self.pending_rides_column.controls.append(
                        ft.Text("No pending rides available", size=16, color="grey")
                    )
                else:
                    for ride in rides:
                        ride_card = ft.Container(
                            content=ft.Column([
                                ft.Text(f"Ride #{ride['id']} - {ride['rider_name']}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Pickup: {ride['pickup_location']}"),
                                ft.Text(f"Dropoff: {ride['dropoff_location']}"),
                                ft.Text(f"Distance: {ride.get('distance_m', 'N/A')}m"),
                                ft.ElevatedButton(
                                    "Accept Ride",
                                    on_click=lambda e, ride_id=ride['id']: self.accept_ride(ride_id),
                                    bgcolor="green",
                                    color="white"
                                )
                            ], spacing=5),
                            bgcolor="white",
                            padding=15,
                            border_radius=8,
                            border=ft.border.all(1, "grey")
                        )
                        self.pending_rides_column.controls.append(ride_card)
                
                # Show pending rides and hide active ride
                self.active_ride_container.visible = False
                self.pending_rides_column.visible = True
                self.page.update()
                
        except Exception as ex:
            print(f"Error loading pending rides: {ex}")
    
    def accept_ride(self, ride_id):
        """Accept a ride and show the route"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(f"{self.backend_url}/rides/accept/{ride_id}", headers=headers)
            
            if response.status_code == 200:
                # Store active ride
                self.active_ride = ride_id
                
                # Get ride details
                ride_response = requests.get(f"{self.backend_url}/rides/{ride_id}", headers=headers)
                if ride_response.status_code == 200:
                    ride = ride_response.json()
                    self.show_active_ride(ride)
                else:
                    self.show_status("Ride accepted, but failed to get details", True)
            else:
                self.show_status("Failed to accept ride", True)
        except Exception as ex:
            self.show_status(f"Error: {str(ex)}", True)
    
    def show_active_ride(self, ride):
        """Display the active ride with the route"""
        try:
            # Parse coordinates
            pickup_parts = ride['pickup_location'].split(',')
            dropoff_parts = ride['dropoff_location'].split(',')
            pickup_coords = (float(pickup_parts[0]), float(pickup_parts[1]))
            dropoff_coords = (float(dropoff_parts[0]), float(dropoff_parts[1]))
            
            # Generate route map
            distance_km = ride.get('distance_m', 0) / 1000
            map_image = self.generate_route_map(pickup_coords, dropoff_coords, distance_km)
            
            # Create UI
            map_display = ft.Image(
                src_base64=map_image,
                width=500,
                height=300,
                fit=ft.ImageFit.CONTAIN
            ) if map_image else ft.Text("Route map unavailable")
            
            self.active_ride_container.content = ft.Column([
                ft.Text("Active Ride", size=20, weight=ft.FontWeight.BOLD),
                map_display,
                ft.ElevatedButton(
                    "Passenger Dropped",
                    on_click=self.complete_ride,
                    bgcolor="green",
                    color="white"
                )
            ])
            self.active_ride_container.visible = True
            self.pending_rides_column.visible = False
            self.page.update()
            
        except Exception as ex:
            print(f"Error showing active ride: {ex}")
    
    def generate_route_map(self, pickup_coords, dropoff_coords, distance_km):
        """Generate a route map visualization"""
        try:
            # Create a simple map image showing the route
            img_width, img_height = 480, 280
            img = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Calculate relative positions (normalize coordinates to image size)
            pickup_x = int((pickup_coords[0] + 180) / 360 * img_width)
            pickup_y = int((90 - pickup_coords[1]) / 180 * img_height)
            dropoff_x = int((dropoff_coords[0] + 180) / 360 * img_width)
            dropoff_y = int((90 - dropoff_coords[1]) / 180 * img_height)
            
            # Draw background grid
            for i in range(0, img_width, 50):
                draw.line([(i, 0), (i, img_height)], fill='#f0f0f0', width=1)
            for i in range(0, img_height, 50):
                draw.line([(0, i), (img_width, i)], fill='#f0f0f0', width=1)
            
            # Draw route line
            draw.line([(pickup_x, pickup_y), (dropoff_x, dropoff_y)], fill='#667eea', width=4)
            
            # Draw pickup marker (green circle)
            marker_size = 8
            draw.ellipse([
                pickup_x - marker_size, pickup_y - marker_size,
                pickup_x + marker_size, pickup_y + marker_size
            ], fill='green', outline='darkgreen', width=2)
            
            # Draw dropoff marker (red circle)
            draw.ellipse([
                dropoff_x - marker_size, dropoff_y - marker_size,
                dropoff_x + marker_size, dropoff_y + marker_size
            ], fill='red', outline='darkred', width=2)
            
            # Add labels
            draw.text((pickup_x + 10, pickup_y - 15), "Pickup", fill='green')
            draw.text((dropoff_x + 10, dropoff_y - 15), "Dropoff", fill='red')
            
            # Add distance info
            draw.text((10, 10), f"Distance: {distance_km:.1f} km", fill='black')
            draw.text((10, 30), f"Route Overview", fill='black')
            
            # Convert to base64 for display
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            
            return image_base64
            
        except Exception as ex:
            print(f"Error generating route map: {ex}")
            return None
    
    def complete_ride(self, e):
        """Mark the active ride as completed"""
        if not self.active_ride:
            return
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(
                f"{self.backend_url}/rides/complete/{self.active_ride}", 
                headers=headers
            )
            
            if response.status_code == 200:
                # Reset UI
                self.active_ride = None
                self.active_ride_container.visible = False
                self.pending_rides_column.visible = True
                self.load_pending_rides()
                
                # Show confirmation
                self.show_status("Ride completed successfully!")
            else:
                self.show_status("Failed to complete ride", True)
                
        except Exception as ex:
            self.show_status(f"Error: {str(ex)}", True)
        
        self.page.update()
    
    def create_admin_tab(self):
        """Create admin interface with analytics"""
        self.admin_stats = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("0", size=36, weight=ft.FontWeight.BOLD, color="blue"),
                    ft.Text("Total Rides")
                ], alignment=ft.MainAxisAlignment.CENTER),
                bgcolor="#e3f2fd",
                padding=20,
                border_radius=10,
                width=200,
                height=120
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("0", size=36, weight=ft.FontWeight.BOLD, color="green"),
                    ft.Text("Today's Rides")
                ], alignment=ft.MainAxisAlignment.CENTER),
                bgcolor="#e8f5e8",
                padding=20,
                border_radius=10,
                width=200,
                height=120
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("$0", size=36, weight=ft.FontWeight.BOLD, color="orange"),
                    ft.Text("Today's Revenue")
                ], alignment=ft.MainAxisAlignment.CENTER),
                bgcolor="#fff3e0",
                padding=20,
                border_radius=10,
                width=200,
                height=120
            )
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        
        # Chart container
        self.chart_container = ft.Container(
            content=ft.Text("Loading analytics chart...", text_align=ft.TextAlign.CENTER),
            bgcolor="white",
            padding=20,
            border_radius=10,
            height=400
        )
        
        # Recent rides list
        self.recent_rides_column = ft.Column(spacing=10)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Admin Dashboard", size=24, weight=ft.FontWeight.BOLD),
                self.admin_stats,
                ft.Text("Weekly Ride Analytics", size=18, weight=ft.FontWeight.BOLD),
                self.chart_container,
                ft.Text("Recent Rides", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.recent_rides_column,
                    bgcolor="#f5f5f5",
                    padding=20,
                    border_radius=10,
                    height=300
                )
            ], spacing=20),
            padding=20
        )
    
    def load_admin_data(self):
        """Load admin dashboard data"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # Get recent rides for analytics
            recent_response = requests.get(f"{self.backend_url}/analytics/recent_rides", headers=headers)
            pending_response = requests.get(f"{self.backend_url}/rides/pending", headers=headers)
            
            if recent_response.status_code == 200:
                recent_rides = recent_response.json()
                pending_rides = pending_response.json() if pending_response.status_code == 200 else []
                
                # Calculate statistics
                total_rides = len(recent_rides)
                today = datetime.now().date()
                today_rides = len([r for r in recent_rides if datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')).date() == today])
                today_revenue = today_rides * 15.0  # Assume $15 per ride
                
                # Update stats cards
                stats_cards = self.admin_stats.controls
                stats_cards[0].content.controls[0].value = str(total_rides)
                stats_cards[1].content.controls[0].value = str(today_rides)
                stats_cards[2].content.controls[0].value = f"${today_revenue:.0f}"
                
                # Generate analytics chart
                self.generate_analytics_chart(recent_rides)
                
                # Update recent rides list
                self.update_recent_rides_list(recent_rides[:10])  # Show last 10
                
                self.page.update()
                
        except Exception as ex:
            print(f"Error loading admin data: {ex}")
    
    def generate_analytics_chart(self, rides):
        """Generate matplotlib chart for ride analytics"""
        try:
            # Prepare data for last 7 days
            end_date = datetime.now().date()
            dates = [(end_date - timedelta(days=i)) for i in range(6, -1, -1)]
            ride_counts = []
            revenues = []
            
            for date in dates:
                day_rides = len([r for r in rides if datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')).date() == date])
                ride_counts.append(day_rides)
                revenues.append(day_rides * 15.0)  # $15 per ride
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            fig.suptitle('Weekly Ride Analytics', fontsize=16, fontweight='bold')
            
            # Rides chart
            ax1.bar(dates, ride_counts, color='#667eea', alpha=0.7)
            ax1.set_title('Daily Rides')
            ax1.set_ylabel('Number of Rides')
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            
            # Revenue chart
            ax2.bar(dates, revenues, color='#28a745', alpha=0.7)
            ax2.set_title('Daily Revenue')
            ax2.set_ylabel('Revenue ($)')
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            
            plt.tight_layout()
            
            # Convert to base64 image
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            # Update chart container
            self.chart_container.content = ft.Image(
                src_base64=image_base64,
                width=800,
                height=400,
                fit=ft.ImageFit.CONTAIN
            )
            
        except Exception as ex:
            print(f"Error generating chart: {ex}")
            self.chart_container.content = ft.Text(f"Error generating chart: {str(ex)}")
    
    def update_recent_rides_list(self, rides):
        """Update recent rides list"""
        self.recent_rides_column.controls.clear()
        
        if not rides:
            self.recent_rides_column.controls.append(
                ft.Text("No recent rides", color="grey")
            )
        else:
            for ride in rides:
                ride_card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Ride #{ride['id']}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Status: {ride['status']}", color="blue")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"Rider: {ride['rider_name']}"),
                        ft.Text(f"Pickup: {ride['pickup_location']}"),
                        ft.Text(f"Dropoff: {ride['dropoff_location']}"),
                        ft.Text(f"Driver: {ride.get('driver_name', 'Not assigned')}")
                    ], spacing=3),
                    bgcolor="white",
                    padding=10,
                    border_radius=5,
                    border=ft.border.all(1, "grey")
                )
                self.recent_rides_column.controls.append(ride_card)
    
    def logout(self, e):
        """Handle logout"""
        self.token = None
        self.current_user = None
        self.init_auth_ui()

def main(page: ft.Page):
    app = CommunityConnectApp(page)

if __name__ == "__main__":
    # Try desktop first, fallback to web if libraries not available
    try:
        ft.app(target=main, port=8080)
    except Exception as e:
        print(f"Desktop mode failed ({e}), trying web mode...")
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)