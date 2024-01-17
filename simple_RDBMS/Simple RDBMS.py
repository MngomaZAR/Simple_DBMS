import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QTableView, QMessageBox, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel
from PyQt5.QtWidgets import QInputDialog


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('my_database.db')

        if not self.db.open():
            QMessageBox.critical(self, 'Error', 'Cannot open database')
            return

        self.conn = sqlite3.connect('my_database.db')
        self.cursor = self.conn.cursor()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_input_section()
        self.init_buttons()
        self.init_table_view()

        self.show()

    def init_input_section(self):
        self.input_box = QLineEdit()
        self.layout.addWidget(self.input_box)

    def init_buttons(self):
        self.add_button = self.create_button('Add', self.add_data)
        self.clear_button = self.create_button('Clear', self.clear_input)
        self.view_button = self.create_button('View Data', self.view_data)
        self.update_button = self.create_button('Update Data', self.update_data)
        self.delete_button = self.create_button('Delete Data', self.delete_data)

        self.layout.addStretch()
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.clear_button)
        self.layout.addWidget(self.view_button)
        self.layout.addWidget(self.update_button)
        self.layout.addWidget(self.delete_button)

    def init_table_view(self):
        self.model = QSqlQueryModel()
        self.model.setQuery('SELECT * FROM my_table')

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.layout.addWidget(self.table_view)

    def create_table(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS my_table (data TEXT)')
        self.conn.commit()

    def create_button(self, text, function):
        button = QPushButton(text)
        button.clicked.connect(function)
        return button

    def add_data(self):
        data = self.input_box.text().strip()

        if not data:
            QMessageBox.warning(self, 'Warning', 'Please enter some data')
            return

        try:
            self.cursor.execute('INSERT INTO my_table (data) VALUES (?)', (data,))
            self.conn.commit()
            QMessageBox.information(self, 'Success', 'Data added successfully')
            self.clear_input()
            self.view_data()  # Refresh the table
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def clear_input(self):
        self.input_box.clear()

    def view_data(self):
        self.model.setQuery('SELECT * FROM my_table')

    def update_data(self):
        selected_row = self.table_view.currentIndex().row()

        if selected_row == -1:
            QMessageBox.warning(self, 'Warning', 'Please select a row to update')
            return

        new_data, ok = QInputDialog.getText(self, 'Update Data', 'Enter new data:')

        if ok:
            try:
                self.model.setData(self.model.index(selected_row, 0), new_data)
                self.conn.commit()
                QMessageBox.information(self, 'Success', 'Data updated successfully')
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def delete_data(self):
        selected_row = self.table_view.currentIndex().row()

        if selected_row == -1:
            QMessageBox.warning(self, 'Warning', 'Please select a row to delete')
            return

        confirm = QMessageBox.question(self, 'Confirm Deletion', 'Are you sure you want to delete this data?',
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            try:
                self.model.removeRow(selected_row)
                self.conn.commit()
                QMessageBox.information(self, 'Success', 'Data deleted successfully')
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    sys.exit(app.exec_())
