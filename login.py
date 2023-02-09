from PyQt5 import QtWidgets, QtWidgets
from config.config import cfg_item


class Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        

        self.text_name = QtWidgets.QLineEdit(self)
        self.text_pass = QtWidgets.QLineEdit(self)
        self.button_login = QtWidgets.QPushButton(cfg_item("login_page", "button_login"), self)
        self.button_login.clicked.connect(self.handle_login)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.text_name)
        layout.addWidget(self.text_pass)
        layout.addWidget(self.button_login)
        
    def handle_login(self):
        # Chekea el usuario y contraseña
        if self.text_name.text() == cfg_item("login_page", "user_name") and self.text_pass.text() == cfg_item("login_page", "password"):
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                "Usuario o contraseña incorrectos"
            )


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)









