from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import requests

API = "http://127.0.0.1:5001"

class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CommunityConnect - Login")
        self.setFixedSize(400, 400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("CommunityConnect")
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1e88e5;")
        
        # Login form
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                border-radius: 15px;
                padding: 10px;
                border: 1px solid #ccc;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border-radius: 15px;
                padding: 10px;
                border: 1px solid #ccc;
            }
        """)
        
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("""
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
        login_btn.clicked.connect(self.do_login)
        
        register_btn = QPushButton("Don't have an account? Register")
        register_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #1e88e5;
                border: none;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        register_btn.clicked.connect(self.show_register)
        
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def do_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            self.show_error("Please fill in all fields")
            return
            
        try:
            res = requests.post(f"{API}/login", data={
                "username": email,
                "password": password
            })
            
            if res.ok:
                data = res.json()
                token = data["access_token"]
                
                # Get user details
                user_res = requests.get(f"{API}/user/me", headers={"Authorization": f"Bearer {token}"})
                if user_res.ok:
                    user_data = user_res.json()
                    self.login_success.emit({"token": token, "user": user_data})
                else:
                    self.show_error("Failed to get user details")
            else:
                self.show_error(f"Login failed: {res.text}")
        except Exception as ex:
            self.show_error(f"Connection error: {str(ex)}")
    
    def show_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
    
    def show_error(self, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: red;")

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CommunityConnect - Register")
        self.setFixedSize(400, 500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Register")
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        # Form fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm Password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        
        # Style inputs
        for input_field in [self.name_input, self.email_input, self.password_input, self.confirm_input]:
            input_field.setStyleSheet("""
                QLineEdit {
                    border-radius: 15px;
                    padding: 10px;
                    border: 1px solid #ccc;
                    min-width: 250px;
                }
            """)
        
        # Register button
        register_btn = QPushButton("Register")
        register_btn.setStyleSheet("""
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
        register_btn.clicked.connect(self.do_register)
        
        # Login link
        login_btn = QPushButton("Already have an account? Login")
        login_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #1e88e5;
                border: none;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        login_btn.clicked.connect(self.show_login)
        
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.name_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_input)
        layout.addWidget(register_btn)
        layout.addWidget(login_btn)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def do_register(self):
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not all([name, email, password, confirm]):
            self.show_error("Please fill in all fields")
            return
            
        if password != confirm:
            self.show_error("Passwords do not match")
            return
            
        try:
            res = requests.post(f"{API}/register", json={
                "name": name,
                "email": email,
                "password": password
            })
            
            if res.ok:
                self.show_success("Registration successful! Please login.")
                # Clear fields
                self.name_input.clear()
                self.email_input.clear()
                self.password_input.clear()
                self.confirm_input.clear()
            else:
                self.show_error(f"Registration failed: {res.text}")
        except Exception as ex:
            self.show_error(f"Connection error: {str(ex)}")
    
    def show_login(self):
        self.close()
    
    def show_error(self, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: red;")
    
    def show_success(self, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: green;")