import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QMessageBox, QDialog)
from autho_login import LoginDialog
from autho_register import RegisterDialog
from views_rider import RiderView
from views_driver import DriverView
from models_users import User
from admin_ui import AdminView
from database import Base, engine, SessionLocal
import bcrypt
from datetime import datetime

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123"
ADMIN_NAME = "Admin"

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CommunityConnect")
        self.setGeometry(100, 100, 800, 600)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.current_user = None
        self.check_admin_user()
        self.show_login()
    
    def check_admin_user(self):
        db = SessionLocal()
        try:
            admin_exists = db.query(User).filter(User.email == ADMIN_EMAIL).first()
            
            if not admin_exists:
                hashed_password = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
                admin_user = User(
                    name=ADMIN_NAME,
                    email=ADMIN_EMAIL,
                    hashed_password=hashed_password,
                    is_admin=True,
                    created_at=datetime.utcnow()
                )
                db.add(admin_user)
                db.commit()
                print("Admin user created successfully")
        finally:
            db.close()
    
    def show_login(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            self.current_user = login_dialog.user
            self.show_main_view()
    
    def show_register(self):
        register_dialog = RegisterDialog(self)
        if register_dialog.exec_() == QDialog.Accepted:
            self.show_login()
    
    def show_main_view(self):
        if self.current_user.is_admin:
            view = AdminView(self.current_user)
        elif hasattr(self.current_user, 'is_driver') and self.current_user.is_driver:
            view = DriverView(self.current_user)
        else:
            view = RiderView(self.current_user)
        
        self.stacked_widget.addWidget(view)
        self.stacked_widget.setCurrentWidget(view)

if __name__ == "__main__":
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())