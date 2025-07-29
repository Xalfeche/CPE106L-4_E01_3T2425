from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import requests
import matplotlib.pyplot as plt

API = "http://127.0.0.1:5001"

class AdminTab(QWidget):
    def __init__(self, token, user_data):
        super().__init__()
        self.token = token
        self.user_data = user_data
        
        self.init_ui()
        self.load_recent_rides()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Admin Dashboard")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        admin_info = QLabel(f"Admin: {self.user_data.get('name', '')}")
        admin_info.setStyleSheet("color: white;")
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(admin_info)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        weekly_stats_btn = QPushButton("Show Weekly Ride Stats")
        weekly_stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border-radius: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        weekly_stats_btn.clicked.connect(self.show_weekly_stats)
        
        user_stats_btn = QPushButton("Show User Ride Stats")
        user_stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #43a047;
                color: white;
                border-radius: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        user_stats_btn.clicked.connect(self.show_user_stats)
        
        buttons_layout.addWidget(weekly_stats_btn)
        buttons_layout.addSpacing(20)
        buttons_layout.addWidget(user_stats_btn)
        
        # Recent rides title
        recent_title = QLabel("Recent Rides")
        recent_title.setFont(QFont('Arial', 14, QFont.Bold))
        recent_title.setStyleSheet("color: white;")
        
        # Recent rides table
        self.recent_rides_table = QTableWidget()
        self.recent_rides_table.setColumnCount(5)
        self.recent_rides_table.setHorizontalHeaderLabels(["ID", "Rider", "Pickup", "Dropoff", "Status"])
        self.recent_rides_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
        """)
        self.recent_rides_table.horizontalHeader().setStretchLastSection(True)
        self.recent_rides_table.verticalHeader().setVisible(False)
        self.recent_rides_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Add widgets to layout
        layout.addLayout(header)
        layout.addLayout(buttons_layout)
        layout.addSpacing(30)
        layout.addWidget(recent_title)
        layout.addWidget(self.recent_rides_table)
        
        self.setLayout(layout)
    
    def show_weekly_stats(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
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
            QMessageBox.critical(self, "Error", f"Error generating chart: {ex}")
    
    def show_user_stats(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
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
            QMessageBox.critical(self, "Error", f"Error generating chart: {ex}")
    
    def load_recent_rides(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{API}/analytics/recent_rides", headers=headers)
            
            if resp.ok:
                rides = resp.json()
                self.recent_rides_table.setRowCount(len(rides))
                
                for row, ride in enumerate(rides):
                    self.recent_rides_table.setItem(row, 0, QTableWidgetItem(str(ride.get("id", ""))))
                    self.recent_rides_table.setItem(row, 1, QTableWidgetItem(ride.get("rider_name", "")))
                    
                    pickup = ride.get("pickup_location", "")
                    self.recent_rides_table.setItem(row, 2, QTableWidgetItem(
                        pickup[:20] + "..." if len(pickup) > 20 else pickup
                    ))
                    
                    dropoff = ride.get("dropoff_location", "")
                    self.recent_rides_table.setItem(row, 3, QTableWidgetItem(
                        dropoff[:20] + "..." if len(dropoff) > 20 else dropoff
                    ))
                    
                    self.recent_rides_table.setItem(row, 4, QTableWidgetItem(ride.get("status", "")))
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Failed to load recent rides: {ex}")