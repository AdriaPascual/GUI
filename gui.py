from PyQt5.QtWidgets import QApplication, QDialog
import sys
import login
import window

if __name__ == '__main__':
    app = QApplication(sys.argv)

    new_login = login.Login()

    new_login.show()

    if new_login.exec() == QDialog.Accepted:
        window = window.CenterWindow()
        window.show()
        sys.exit(app.exec())

