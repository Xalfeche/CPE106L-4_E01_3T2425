from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import requests

API = "http://127.0.0.1:5001"

class DriverTab(QWidget):
    def __init__(self, token, user_data):
        super().__init__()
        self.token = token
        self.user_data = user_data
        
        self.init_ui()
        self.load_pending_rides()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Driver Dashboard")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        driver_info = QLabel(f"Driver: {self.user_data.get('name', '')}")
        driver_info.setStyleSheet("color: white;")
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(driver_info)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Rides")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border-radius: 20px;
                padding: 10px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        refresh_btn.clicked.connect(self.load_pending_rides)
        
        # Status label
        self.status_label = QLabel("Loading pending rides...")
        self.status_label.setStyleSheet("color: #2196f3;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Rides table
        self.rides_table = QTableWidget()
        self.rides_table.setColumnCount(5)
        self.rides_table.setHorizontalHeaderLabels(["ID", "Rider", "Pickup", "Dropoff", "Actions"])
        self.rides_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: none;
            }
        """)
        self.rides_table.horizontalHeader().setStretchLastSection(True)
        self.rides_table.verticalHeader().setVisible(False)
        self.rides_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Add widgets to layout
        layout.addLayout(header)
        layout.addWidget(refresh_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.rides_table)
        
        self.setLayout(layout)
    
    def load_pending_rides(self):
        self.rides_table.setRowCount(0)
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{API}/rides/pending", headers=headers)
            
            if resp.ok:
                rides = resp.json()
                
                if not rides:
                    self.status_label.setText("No pending rides available")
                    self.status_label.setStyleSheet("color: #ff9800;")
                else:
                    self.status_label.setText(f"Found {len(rides)} pending rides")
                    self.status_label.setStyleSheet("color: #4caf50;")
                    
                    self.rides_table.setRowCount(len(rides))
                    for row, ride in enumerate(rides):
                        self.rides_table.setItem(row, 0, QTableWidgetItem(str(ride["id"])))
                        self.rides_table.setItem(row, 1, QTableWidgetItem(str(ride.get("rider_name", "N/A"))))
                        
                        pickup = str(ride.get("pickup_location", ""))
                        self.rides_table.setItem(row, 2, QTableWidgetItem(pickup[:20] + "..." if len(pickup) > 20 else pickup))
                        
                        dropoff = str(ride.get("dropoff_location", ""))
                        self.rides_table.setItem(row, 3, QTableWidgetItem(dropoff[:20] + "..." if len(dropoff) > 20 else dropoff))
                        
                        # Accept button
                        accept_btn = QPushButton("Accept")
                        accept_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #4caf50;
                                color: white;
                                border-radius: 10px;
                                padding: 5px;
                            }
                            QPushButton:hover {
                                background-color: #388e3c;
                            }
                        """)
                        accept_btn.clicked.connect(lambda _, ride_id=ride["id"]: self.accept_ride(ride_id))
                        
                        cell_widget = QWidget()
                        cell_layout = QHBoxLayout(cell_widget)
                        cell_layout.addWidget(accept_btn)
                        cell_layout.setAlignment(Qt.AlignCenter)
                        cell_layout.setContentsMargins(0, 0, 0, 0)
                        
                        self.rides_table.setCellWidget(row, 4, cell_widget)
            else:
                self.status_label.setText(f"Failed to load rides: {resp.text}")
                self.status_label.setStyleSheet("color: red;")
        except Exception as ex:
            self.status_label.setText(f"Connection error: {str(ex)}")
            self.status_label.setStyleSheet("color: red;")
    
    def accept_ride(self, ride_id):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.post(f"{API}/rides/accept/{ride_id}", headers=headers)
            
            if resp.ok:
                self.status_label.setText(f"Ride {ride_id} accepted successfully!")
                self.status_label.setStyleSheet("color: #4caf50;")
                self.load_pending_rides()
            else:
                self.status_label.setText(f"Failed to accept ride: {resp.text}")
                self.status_label.setStyleSheet("color: red;")
        except Exception as ex:
            self.status_label.setText(f"Connection error: {str(ex)}")
            self.status_label.setStyleSheet("color: red;")