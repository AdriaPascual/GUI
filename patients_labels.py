from PyQt5 import QtWidgets
import sqlite3
import datetime
from reportlab.pdfgen import canvas
import shutil
import os
from config.config import cfg_item


class PatientForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        self.name = QtWidgets.QLineEdit()
        self.age = QtWidgets.QLineEdit()
        self.email = QtWidgets.QLineEdit()
        self.phone = QtWidgets.QLineEdit()
        self.consult_reason = QtWidgets.QLineEdit()
        self.history = QtWidgets.QTextEdit()
        self.session = QtWidgets.QTextEdit()
        self.save_button = QtWidgets.QPushButton(cfg_item("patients_labels_window", "save_button"))
        self.export_button = QtWidgets.QPushButton(cfg_item("patients_labels_window", "pdf_button"))
        self.pdf_list = QtWidgets.QListWidget()


        layout = QtWidgets.QFormLayout()
        layout.addRow("Nombre:", self.name)
        layout.addRow("Edad:", self.age)
        layout.addRow("Correo:", self.email)
        layout.addRow("Teléfono:", self.phone)
        layout.addRow("Motivo de la consulta:", self.consult_reason)
        layout.addRow("Antecedentes:", self.history)
        layout.addRow("Sesión:", self.session)
        layout.addWidget(self.save_button)
        layout.addWidget(self.export_button)

        self.save_button.clicked.connect(self.save_form_text)
        self.export_button.clicked.connect(self.generate_pdf)


        self.setLayout(layout)
        self.setWindowTitle("Formulario Paciente")

    def save_form_text(self):
        # Conectar a la base de datos
        conn = sqlite3.connect(cfg_item("database", "db_file_name"))
        cursor = conn.cursor()

        # Crear la tabla si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS text_entries (
            ID integer primary key autoincrement,
            Nombre text,
            Edad text,
            Correo text,
            Teléfono text,
            Motivo text,
            Antecedentes text,
            Sesion text,
            PDF blob
        )
        """)

        # Recuperar los datos del formulario
        name = self.name.text()
        age = self.age.text()
        email = self.email.text()
        phone = self.phone.text()
        consult_reason = self.consult_reason.text()
        history = self.history.toPlainText()
        session = self.session.toPlainText()

        # Verificar si el paciente ya existe en la base de datos
        cursor.execute("SELECT ID FROM text_entries WHERE Nombre=? AND Edad=? AND Correo=?", (name, age, email))
        result = cursor.fetchone()

        # Ejecutar una consulta de inserción o actualización
        if result:
            # Actualizar el registro existente
            patient_id = result[0]
            cursor.execute("""
            UPDATE text_entries
            SET Teléfono=?, Motivo=?, Antecedentes=?, Sesion=?
            WHERE ID=?
            """, (phone, consult_reason, history, session, patient_id))
        else:
            # Crear un nuevo registro
            cursor.execute("""
            INSERT INTO text_entries (Nombre, Edad, Correo, Teléfono, Motivo, Antecedentes, Sesion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, age, email, phone, consult_reason, history, session))

        # Guardar los cambios y cerrar la conexión
        conn.commit()
        conn.close()

    
    def generate_pdf(self):
        # Crear el archivo PDF
        
        self.patient_data = {
            "nombre": self.name.text(),
            "edad": self.age.text(),
            "correo": self.email.text(),
            "telefono": self.phone.text(),
            "motivo_consulta": self.consult_reason.text(),
            "antecedentes": self.history.toPlainText(),
            "sesion": self.session.toPlainText()
        }

        psychologist_data = {
            "Nombre de la Psicóloga": cfg_item("psychologist", "psychologist_name"),
            "Número de colegiada": cfg_item("psychologist", "collegiate_number"),
            "Fecha": datetime.datetime.now()
        }

        self.file_name = self.patient_data['nombre'] + '_' + str(psychologist_data['Fecha'].date()) + '.pdf'

        with open(self.file_name, "wb") as pdf_file:
            pdf = canvas.Canvas(pdf_file)

            # Escribir el encabezado con la información de la psicóloga
            y = cfg_item("pdf_settings_header", "header_y")
            for key, value in psychologist_data.items():
                pdf.drawString(cfg_item("pdf_settings_header", "header_x"), y, key + ": " + str(value))
                y -= cfg_item("pdf_settings_header", "y_rest")

            # Escribir los datos del paciente
            y = cfg_item("pdf_settings_patient", "header_y")
            for key, value in self.patient_data.items():
                pdf.drawString(cfg_item("pdf_settings_patient", "header_x"), y, key + ": " + str(value))
                y -= cfg_item("pdf_settings_patient", "y_rest")

            # Guardar el PDF
            pdf.save()
            # Obtener la ruta al directorio de descargas
            downloads_folder = os.path.expanduser("~/Downloads/")

            # Crear la ruta completa al archivo en el directorio de descargas
            file_path = os.path.join(downloads_folder, self.file_name)

            # Copiar el archivo al directorio de descargas
            shutil.copy(self.file_name, file_path)

        # Abrir el archivo PDF
        with open(self.file_name, 'rb') as pdf_file:
            pdf_data = pdf_file.read()

        # Conectar a la base de datos
        conn = sqlite3.connect(cfg_item("database", "db_file_name"))
        cursor = conn.cursor()

        # Recuperar los demás datos del formulario
        name = self.name.text()
        age = self.age.text()
        email = self.email.text()
        phone = self.phone.text()
        consult_reason = self.consult_reason.text()
        history = self.history.toPlainText()
        session = self.session.toPlainText()

        # Ejecutar la consulta de inserción
        cursor.execute("""
        INSERT INTO text_entries (Nombre, Edad, Correo, Teléfono, Motivo, Antecedentes, Sesion, PDF)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, email, phone, consult_reason, history, session, sqlite3.Binary(pdf_data)))

        conn.close()
            


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        self.patient_form = PatientForm()

        form_button = QtWidgets.QPushButton("Abrir Formulario")
        form_button.clicked.connect(self.patient_form.show)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(form_button)

        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
        self.setWindowTitle("Ventana Pacientes")

