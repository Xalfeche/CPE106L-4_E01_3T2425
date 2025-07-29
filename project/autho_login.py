from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from models_users import User
from database import SessionLocal
import bcrypt
import jwt
from datetime import datetime, timedelta
import os

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.authenticate)
        
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
    
    def authenticate(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user or not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
                QMessageBox.warning(self, "Login Failed", "Invalid credentials")
                return
            
            # Create JWT token
            payload = {"sub": email, "exp": datetime.utcnow() + timedelta(hours=24)}
            token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
            
            self.accept()  # Close dialog with success
            return token
        finally:
            db.close()