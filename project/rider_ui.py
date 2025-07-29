from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSlot
import folium
import io
import requests
import json
from PyQt5.QtCore import pyqtSignal, QObject

API = "http://127.0.0.1:5001"  # Make sure this matches your backend API

class Bridge(QObject):
    locationClicked = pyqtSignal(float, float)
    
    def __init__(self):
        super().__init__()
        print("Bridge object created")
    
    @pyqtSlot(float, float, result=bool)
    def onLocationClicked(self, lat, lng):
        """Method to be called from JavaScript - emits the signal internally"""
        print(f"Bridge received location click: {lat}, {lng}")
        self.locationClicked.emit(lat, lng)
        return True
    
    @pyqtSlot(result=str)
    def testConnection(self):
        """Test method to verify bridge connection"""
        print("Bridge connection test called")
        return "Bridge connected successfully"

class RiderTab(QWidget):
    def __init__(self, token, user_data):
        super().__init__()
        self.token = token
        self.user_data = user_data
        self.selected_pickup = None
        self.selected_dropoff = None
        self.click_mode = "pickup"  # Tracks whether next click is pickup or dropoff
        self.bridge = Bridge()
        self.channel = QWebChannel()
        self.init_ui()
    
    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - controls
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #424242;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                color: white;
            }
        """)
        left_panel.setFixedWidth(350)
        
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)
        left_layout.setSpacing(15)
        
        # Title
        title = QLabel("Request a Ride")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        
        # User info
        user_info = QLabel(f"User: {self.user_data.get('name', '')} ({self.user_data.get('email', '')})")
        
        # Pickup and dropoff inputs
        self.pickup_input = QLineEdit()
        self.pickup_input.setPlaceholderText("Pick Up (Long,Lat)")
        self.pickup_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 15px;
                padding: 10px;
                border: 1px solid #ccc;
            }
        """)
        
        self.dropoff_input = QLineEdit()
        self.dropoff_input.setPlaceholderText("Drop Off (Long,Lat)")
        self.dropoff_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 15px;
                padding: 10px;
                border: 1px solid #ccc;
            }
        """)
        
        # Toggle button for selecting pickup/dropoff
        self.toggle_btn = QPushButton("Click to Set Pickup Location")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border-radius: 20px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_click_mode)
        
        # Clear button
        clear_btn = QPushButton("Clear Locations")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #fb8c00;
                color: white;
                border-radius: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        clear_btn.clicked.connect(self.clear_locations)
        
        # Request ride button
        request_btn = QPushButton("Request Ride")
        request_btn.setStyleSheet("""
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
        request_btn.clicked.connect(self.book_ride)
        
        # Status label
        self.status_label = QLabel("Click the button above, then click on the map to set pickup location")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #2196f3;")
        
        # Add widgets to left layout
        left_layout.addWidget(title)
        left_layout.addWidget(user_info)
        left_layout.addWidget(self.pickup_input)
        left_layout.addWidget(self.dropoff_input)
        left_layout.addWidget(self.toggle_btn)
        left_layout.addWidget(clear_btn)
        left_layout.addWidget(request_btn)
        left_layout.addWidget(self.status_label)
        
        left_panel.setLayout(left_layout)
        
        # Right panel - map
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                border: 2px solid #cfd8dc;
            }
        """)
        right_panel.setFixedSize(600, 420)
        
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Create the map widget
        self.map_view = QWebEngineView()
        self.init_map()
        
        instructions = QLabel("Use the toggle button to switch between pickup and dropoff, then click on the map")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #616161; font-size: 11px;")
        instructions.setWordWrap(True)
        
        right_layout.addWidget(self.map_view)
        right_layout.addWidget(instructions)
        right_panel.setLayout(right_layout)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addSpacing(50)
        main_layout.addWidget(right_panel)
        
        self.setLayout(main_layout)
        
        # Connect bridge signals
        self.bridge.locationClicked.connect(self.handle_map_click)
    
    def init_map(self):
        """Initialize the Folium map"""
        self.map = folium.Map(location=[14.5995, 120.9842], zoom_start=12)  # Manila, Philippines
        self.setup_map_view()
    
    def setup_map_view(self):
        """Setup the map view with QWebChannel integration"""
        # Save map to HTML
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        html_content = data.getvalue().decode()
        
        # Inject QWebChannel script and custom JavaScript
        qwebchannel_script = """
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script>
            var bridge = null;
            var mapClickHandler = null;
            var channelReady = false;
            
            function setupWebChannel() {
                console.log('Setting up WebChannel...');
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    console.log('WebChannel initialized, objects:', Object.keys(channel.objects));
                    bridge = channel.objects.bridge;
                    channelReady = true;
                    
                    // Debug: Log all available methods on bridge
                    if (bridge) {
                        console.log('Bridge object found. Available properties/methods:');
                        for (let prop in bridge) {
                            console.log('  - ' + prop + ': ' + typeof bridge[prop]);
                        }
                        
                        // Test the connection
                        if (typeof bridge.testConnection === 'function') {
                            try {
                                bridge.testConnection(function(result) {
                                    console.log('Test connection result:', result);
                                });
                            } catch (e) {
                                console.log('Test connection error:', e);
                            }
                        }
                        
                        // Check for our method
                        if (typeof bridge.onLocationClicked === 'function') {
                            console.log('onLocationClicked method found - setting up map click handler');
                            setupMapClickHandler();
                        } else {
                            console.error('onLocationClicked method not found on bridge object');
                        }
                    } else {
                        console.error('Bridge object not found in channel');
                    }
                });
            }
            
            function setupMapClickHandler() {
                console.log('Setting up map click handler...');
                
                // Function to find and setup map click handler
                function addClickHandler() {
                    // Find the map object (Folium creates a global map variable)
                    var mapKeys = Object.keys(window).filter(key => key.startsWith('map_'));
                    console.log('Available map keys:', mapKeys);
                    
                    if (mapKeys.length > 0) {
                        var mapObj = window[mapKeys[0]];
                        console.log('Map object found:', mapKeys[0], mapObj);
                        
                        // Remove existing handler if any
                        if (mapClickHandler) {
                            mapObj.off('click', mapClickHandler);
                            console.log('Removed old click handler');
                        }
                        
                        // Add new click handler
                        mapClickHandler = function(e) {
                            console.log('Map clicked at:', e.latlng.lat, e.latlng.lng);
                            console.log('Bridge available:', !!bridge, 'Channel ready:', channelReady);
                            
                            if (bridge && channelReady) {
                                try {
                                    // Call the method instead of trying to emit signal directly
                                    bridge.onLocationClicked(e.latlng.lat, e.latlng.lng);
                                    console.log('Location click sent to bridge successfully');
                                } catch (error) {
                                    console.error('Error calling bridge method:', error);
                                }
                            } else {
                                console.error('Bridge not ready or not available');
                            }
                        };
                        
                        mapObj.on('click', mapClickHandler);
                        console.log('Click handler added successfully');
                        return true;
                    }
                    console.log('No map object found yet');
                    return false;
                }
                
                // Try to add handler immediately, then retry if needed
                if (!addClickHandler()) {
                    var retryCount = 0;
                    var checkMap = setInterval(function() {
                        retryCount++;
                        console.log('Retry attempt:', retryCount);
                        if (addClickHandler() || retryCount > 30) {
                            clearInterval(checkMap);
                            if (retryCount > 30) {
                                console.error('Failed to setup map click handler after 30 attempts');
                            }
                        }
                    }, 200);
                }
            }
            
            // Initialize when DOM is ready
            if (document.readyState === 'complete') {
                setTimeout(setupWebChannel, 200);
            } else {
                window.addEventListener('load', function() {
                    setTimeout(setupWebChannel, 200);
                });
            }
        </script>
        """
        
        # Insert the script before the closing body tag
        html_content = html_content.replace('</body>', qwebchannel_script + '</body>')
        
        # Set HTML content first
        self.map_view.setHtml(html_content)
        
        # Use a timer to ensure proper initialization order
        QTimer.singleShot(1000, self.setup_web_channel)
        
        # Debug: Verify the channel setup
        print(f"Bridge registered with channel. Bridge type: {type(self.bridge)}")
        print(f"Bridge has locationClicked: {hasattr(self.bridge, 'locationClicked')}")
    
    def setup_web_channel(self):
        """Setup the web channel after a delay to ensure HTML is loaded"""
        # Register bridge with channel and set channel to page
        self.channel.registerObject("bridge", self.bridge)
        self.map_view.page().setWebChannel(self.channel)
        print("WebChannel setup completed")
    
    def toggle_click_mode(self):
        """Toggle between pickup and dropoff selection mode"""
        if self.click_mode == "pickup":
            self.click_mode = "dropoff"
            self.toggle_btn.setText("Click to Set Dropoff Location")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff5722;
                    color: white;
                    border-radius: 20px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e64a19;
                }
            """)
            self.status_label.setText("Now click on the map to set dropoff location")
            self.status_label.setStyleSheet("color: #ff5722;")
        else:
            self.click_mode = "pickup"
            self.toggle_btn.setText("Click to Set Pickup Location")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border-radius: 20px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.status_label.setText("Now click on the map to set pickup location")
            self.status_label.setStyleSheet("color: #4caf50;")
    
    def handle_map_click(self, lat, lng):
        """Handle map click events"""
        coord_str = f"{lng:.6f},{lat:.6f}"
        
        if self.click_mode == "pickup":
            self.selected_pickup = (lat, lng)
            self.pickup_input.setText(coord_str)
            self.status_label.setText(f"✓ Pickup set! Now click toggle button to set dropoff location")
            self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        else:
            self.selected_dropoff = (lat, lng)
            self.dropoff_input.setText(coord_str)
            self.status_label.setText(f"✓ Dropoff set! You can now request the ride")
            self.status_label.setStyleSheet("color: #ff5722; font-weight: bold;")
        
        # Update map markers
        self.update_map_markers()
    
    def update_map_markers(self):
        """Update the map with current markers"""
        # Create new map centered on Manila (fixed the location issue)
        self.map = folium.Map(location=[14.5995, 120.9842], zoom_start=12)
        
        # Add pickup marker if exists
        if self.selected_pickup:
            folium.Marker(
                location=self.selected_pickup,
                popup="Pickup Location",
                tooltip="Pickup",
                icon=folium.Icon(color='green', icon='play')
            ).add_to(self.map)
        
        # Add dropoff marker if exists
        if self.selected_dropoff:
            folium.Marker(
                location=self.selected_dropoff,
                popup="Dropoff Location", 
                tooltip="Dropoff",
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(self.map)
        
        # Add route if both points exist
        if self.selected_pickup and self.selected_dropoff:
            folium.PolyLine(
                locations=[self.selected_pickup, self.selected_dropoff],
                color='blue',
                weight=3,
                opacity=0.8,
                popup="Route"
            ).add_to(self.map)
            
            # Fit map to show both markers
            bounds = [self.selected_pickup, self.selected_dropoff]
            self.map.fit_bounds(bounds, padding=(20, 20))
        
        # Refresh the map view
        self.setup_map_view()
    
    def clear_locations(self):
        """Clear all selected locations"""
        self.selected_pickup = None
        self.selected_dropoff = None
        self.pickup_input.clear()
        self.dropoff_input.clear()
        self.click_mode = "pickup"
        self.toggle_btn.setText("Click to Set Pickup Location")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border-radius: 20px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.status_label.setText("Locations cleared. Click the button above, then click on map to set pickup location.")
        self.status_label.setStyleSheet("color: #2196f3;")
        self.update_map_markers()
    
    def book_ride(self):
        """Book the ride with selected pickup and dropoff locations"""
        pickup = self.pickup_input.text()
        dropoff = self.dropoff_input.text()
        
        if not pickup or not dropoff:
            self.status_label.setText("⚠️ Please set both pickup and dropoff locations first")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            res = requests.post(f"{API}/rides/request", json={
                "pickup_location": pickup,
                "dropoff_location": dropoff,
                "requested_time": "ASAP"
            }, headers=headers)
            
            if res.ok:
                data = res.json()
                distance = data.get('distance_m', 0)
                self.status_label.setText(f"🚗 Ride requested successfully! Distance: {distance:.0f}m")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.clear_locations()
            else:
                error_msg = res.json().get('message', res.text) if res.headers.get('content-type') == 'application/json' else res.text
                self.status_label.setText(f"❌ Error: {error_msg}")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
        except Exception as ex:
            self.status_label.setText(f"🔌 Connection Error: {str(ex)}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")