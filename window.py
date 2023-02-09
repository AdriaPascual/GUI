from PyQt5.QtWidgets import (
    QMainWindow,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTableWidgetItem,
    QTableWidget,
    QHeaderView
)
import sqlite3
import patients_labels
from config.config import cfg_item


class CenterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Centered Window")
        self.setGeometry(cfg_item("geometry","x"), cfg_item("geometry","y"), cfg_item("geometry","width"), cfg_item("geometry","height"))

        self.conn = sqlite3.connect(cfg_item("database", "db_file_name"))
        self.cursor = self.conn.cursor()

        self.line_edit = QLineEdit()
        self.search_button = QPushButton(cfg_item("buttons_principal_window", "search_button"))
        self.delete_button = QPushButton(cfg_item("buttons_principal_window", "delete_button"))
        self.update_button = QPushButton(cfg_item("buttons_principal_window", "update_button"))
        self.form_button = QPushButton(cfg_item("buttons_principal_window", "form_button"))
        self.view_button = QPushButton(cfg_item("buttons_principal_window", "view_button"))

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(cfg_item("table_widget", "table_horizontal_header_labels"))
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout = QVBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.search_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.form_button)
        layout.addWidget(self.table_widget)
        layout.addWidget(self.update_button)
        layout.addWidget(self.view_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.search_button.clicked.connect(self.search_data)
        self.delete_button.clicked.connect(self.delete_text)
        self.form_button.clicked.connect(self.open_form)
        self.update_button.clicked.connect(self.update_table_widget)
        self.view_button.clicked.connect(self.view_data)

        query = "SELECT ID, Nombre, Correo, Teléfono FROM text_entries"
        result = self.cursor.execute(query)

        for row_index, row_data in enumerate(result):
            self.table_widget.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.table_widget.setItem(row_index, col_index, QTableWidgetItem(str(data)))

    def search_data(self):
        search_text = self.line_edit.text()
        query = "SELECT ID, Nombre, Correo, Teléfono FROM text_entries WHERE Nombre LIKE '%{}%' OR Correo LIKE '%{}%' OR Teléfono LIKE '%{}%'".format(search_text, search_text, search_text)
        result = self.cursor.execute(query)

        self.table_widget.setRowCount(0)

        for row_index, row_data in enumerate(result):
            self.table_widget.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.table_widget.setItem(row_index, col_index, QTableWidgetItem(str(data)))

    def delete_text(self):
        selected_rows = self.table_widget.selectedIndexes()
        if not selected_rows:
            return

        selected_row = selected_rows[0].row()
        selected_item = self.table_widget.item(selected_row, 0)
        if not selected_item:
            return

        selected_id = int(selected_item.text())
        query = "DELETE FROM text_entries WHERE ID={}".format(selected_id)
        self.cursor.execute(query)
        self.conn.commit()
        self.table_widget.removeRow(selected_row)

    def open_form(self):
        self.form_window = patients_labels.PatientForm()
        self.form_window.show()

    def update_table_widget(self):
        # Borrar todos los datos actuales del QTableWidget
        self.table_widget.setRowCount(0)

        # Recuperar los nuevos datos de la base de datos
        query = "SELECT ID, Nombre, Correo, Teléfono FROM text_entries"
        result = self.cursor.execute(query)

        # Insertar los nuevos datos en el QTableWidget
        for row_index, row_data in enumerate(result):
            self.table_widget.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.table_widget.setItem(row_index, col_index, QTableWidgetItem(str(data)))

    def view_data(self):
        selected_rows = self.table_widget.selectedIndexes()
        if not selected_rows:
            return

        selected_row = selected_rows[0].row()
        selected_item = self.table_widget.item(selected_row, 0)
        if not selected_item:
            return

        selected_id = int(selected_item.text())
        query = "SELECT * FROM text_entries WHERE ID={}".format(selected_id)
        result = self.cursor.execute(query).fetchone()

        self.view_window = QMainWindow()
        self.view_window.setWindowTitle("Información del paciente")

        patient_form = patients_labels.PatientForm()
        patient_form.name.setText(result[1])
        patient_form.age.setText(str(result[2]))
        patient_form.email.setText(result[3])
        patient_form.phone.setText(str(result[4]))
        patient_form.consult_reason.setText(result[5])
        patient_form.history.setText(result[6])
        patient_form.session.setText(result[7])
        patient_form.save_button.setEnabled(False)

        self.view_window.setCentralWidget(patient_form)

        self.view_window.show()







