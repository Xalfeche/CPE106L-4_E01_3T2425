from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from models_users import User
from database import SessionLocal
import bcrypt

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register")
        self.setFixedSize(300, 250)
        
        layout = QVBoxLayout()
        
        self.name_label = QLabel("Full Name:")
        self.name_input = QLineEdit()
        
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.confirm_label = QLabel("Confirm Password:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register_user)
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_label)
        layout.addWidget(self.confirm_input)
        layout.addWidget(self.register_button)
        
        self.setLayout(layout)
    
    def register_user(self):
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if password != confirm:
            QMessageBox.warning(self, "Registration Failed", "Passwords don't match")
            return
        
        db = SessionLocal()
        try:
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                QMessageBox.warning(self, "Registration Failed", "Email already registered")
                return
            
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            new_user = User(
                name=name,
                email=email,
                hashed_password=hashed_password,
                is_admin=False
            )
            
            db.add(new_user)
            db.commit()
            QMessageBox.information(self, "Success", "User registered successfully")
            self.accept()
        finally:
            db.close()