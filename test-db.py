"""Тестовая программа для просмотра и редактирования SQLite базы данных"""
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QLabel,
    QLineEdit, QTextEdit, QDialogButtonBox, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QAbstractItemView, QHeaderView,
    QSpinBox, QComboBox
)
from PyQt5.QtCore import Qt
from typing import Optional, List, Dict, Any


class EditRowDialog(QDialog):
    """Диалог для редактирования/создания строки"""
    
    def __init__(self, parent=None, columns: List[str] = None, row_data: Optional[Dict] = None):
        super().__init__(parent)
        self.columns = columns or []
        self.row_data = row_data or {}
        self.setWindowTitle("Редактировать строку" if row_data else "Новая строка")
        self.setMinimumSize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.fields = {}
        for col in self.columns:
            layout.addWidget(QLabel(f"{col}:"))
            
            # Используем QTextEdit для длинных текстов, QLineEdit для коротких
            if col.lower() in ['prompt', 'response_text', 'response', 'text', 'content', 'description']:
                field = QTextEdit()
                field.setMaximumHeight(100)
                if col in self.row_data:
                    field.setPlainText(str(self.row_data[col]))
            else:
                field = QLineEdit()
                if col in self.row_data:
                    field.setText(str(self.row_data[col]))
            
            self.fields[col] = field
            layout.addWidget(field)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_data(self) -> Dict[str, Any]:
        """Получить данные из полей"""
        data = {}
        for col, field in self.fields.items():
            if isinstance(field, QTextEdit):
                data[col] = field.toPlainText()
            else:
                data[col] = field.text()
        return data


class TableViewDialog(QDialog):
    """Диалог для просмотра и редактирования таблицы"""
    
    def __init__(self, parent=None, db_path: str = "", table_name: str = ""):
        super().__init__(parent)
        self.db_path = db_path
        self.table_name = table_name
        self.conn = None
        self.current_page = 1
        self.page_size = 50
        self.total_rows = 0
        self.columns = []
        
        self.setWindowTitle(f"Таблица: {table_name}")
        self.setMinimumSize(1000, 700)
        self.init_ui()
        self.load_table_info()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Панель управления пагинацией
        pagination_layout = QHBoxLayout()
        
        pagination_layout.addWidget(QLabel("Страница:"))
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setMaximum(1)
        self.page_spin.valueChanged.connect(self.on_page_changed)
        pagination_layout.addWidget(self.page_spin)
        
        pagination_layout.addWidget(QLabel("из"))
        self.total_pages_label = QLabel("1")
        pagination_layout.addWidget(self.total_pages_label)
        
        pagination_layout.addWidget(QLabel("Строк на странице:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["25", "50", "100", "200"])
        self.page_size_combo.setCurrentText(str(self.page_size))
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        pagination_layout.addWidget(self.page_size_combo)
        
        pagination_layout.addStretch()
        
        self.total_rows_label = QLabel("Всего строк: 0")
        pagination_layout.addWidget(self.total_rows_label)
        
        layout.addLayout(pagination_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Кнопки CRUD
        buttons_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Создать")
        self.create_button.clicked.connect(self.on_create)
        buttons_layout.addWidget(self.create_button)
        
        self.update_button = QPushButton("Редактировать")
        self.update_button.clicked.connect(self.on_update)
        self.update_button.setEnabled(False)
        buttons_layout.addWidget(self.update_button)
        
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.on_delete)
        self.delete_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_data)
        buttons_layout.addWidget(self.refresh_button)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Подключаем обработчик выбора строки
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def connect_db(self):
        """Подключиться к базе данных"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к БД: {str(e)}")
            return False
    
    def load_table_info(self):
        """Загрузить информацию о таблице"""
        if not self.connect_db():
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Получаем список колонок
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns_info = cursor.fetchall()
            self.columns = [col[1] for col in columns_info]
            
            # Получаем общее количество строк
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            self.total_rows = cursor.fetchone()[0]
            
            # Обновляем интерфейс
            total_pages = max(1, (self.total_rows + self.page_size - 1) // self.page_size)
            self.page_spin.setMaximum(total_pages)
            self.total_pages_label.setText(str(total_pages))
            self.total_rows_label.setText(f"Всего строк: {self.total_rows}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке информации о таблице: {str(e)}")
    
    def load_data(self):
        """Загрузить данные таблицы с пагинацией"""
        if not self.conn:
            if not self.connect_db():
                return
        
        try:
            cursor = self.conn.cursor()
            
            # Вычисляем OFFSET и LIMIT
            offset = (self.current_page - 1) * self.page_size
            limit = self.page_size
            
            # Получаем данные
            query = f"SELECT * FROM {self.table_name} LIMIT ? OFFSET ?"
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()
            
            # Настраиваем таблицу
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(self.columns))
            self.table.setHorizontalHeaderLabels(self.columns)
            
            # Заполняем данные
            for row_idx, row in enumerate(rows):
                for col_idx, col_name in enumerate(self.columns):
                    value = row[col_name]
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    self.table.setItem(row_idx, col_idx, item)
            
            # Автоматическая ширина колонок
            self.table.resizeColumnsToContents()
            
            # Обновляем номер страницы
            self.page_spin.setValue(self.current_page)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных: {str(e)}")
    
    def on_page_changed(self, page: int):
        """Обработчик изменения страницы"""
        self.current_page = page
        self.load_data()
    
    def on_page_size_changed(self, size_str: str):
        """Обработчик изменения размера страницы"""
        self.page_size = int(size_str)
        self.load_table_info()
        self.current_page = 1
        self.load_data()
    
    def on_selection_changed(self):
        """Обработчик изменения выбора строки"""
        has_selection = len(self.table.selectedItems()) > 0
        self.update_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def get_selected_row_data(self) -> Optional[Dict]:
        """Получить данные выбранной строки"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        
        row_idx = selected_rows[0].row()
        row_data = {}
        for col_idx, col_name in enumerate(self.columns):
            item = self.table.item(row_idx, col_idx)
            row_data[col_name] = item.text() if item else ""
        
        return row_data
    
    def get_primary_key(self) -> Optional[str]:
        """Получить имя первичного ключа"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns_info = cursor.fetchall()
            for col in columns_info:
                if col[5] == 1:  # pk flag
                    return col[1]
        except:
            pass
        return None
    
    def on_create(self):
        """Создать новую строку"""
        dialog = EditRowDialog(self, self.columns)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                cursor = self.conn.cursor()
                
                # Формируем запрос INSERT
                columns_str = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])
                values = list(data.values())
                
                query = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})"
                cursor.execute(query, values)
                self.conn.commit()
                
                QMessageBox.information(self, "Успех", "Строка успешно создана!")
                self.load_table_info()
                self.load_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при создании строки: {str(e)}")
    
    def on_update(self):
        """Редактировать выбранную строку"""
        row_data = self.get_selected_row_data()
        if not row_data:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для редактирования!")
            return
        
        primary_key = self.get_primary_key()
        if not primary_key:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить первичный ключ!")
            return
        
        dialog = EditRowDialog(self, self.columns, row_data)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            try:
                cursor = self.conn.cursor()
                
                # Формируем запрос UPDATE
                set_clause = ", ".join([f"{col} = ?" for col in new_data.keys() if col != primary_key])
                values = [new_data[col] for col in new_data.keys() if col != primary_key]
                values.append(row_data[primary_key])  # WHERE условие
                
                query = f"UPDATE {self.table_name} SET {set_clause} WHERE {primary_key} = ?"
                cursor.execute(query, values)
                self.conn.commit()
                
                QMessageBox.information(self, "Успех", "Строка успешно обновлена!")
                self.load_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении строки: {str(e)}")
    
    def on_delete(self):
        """Удалить выбранную строку"""
        row_data = self.get_selected_row_data()
        if not row_data:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления!")
            return
        
        primary_key = self.get_primary_key()
        if not primary_key:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить первичный ключ!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить эту строку?\n{primary_key} = {row_data[primary_key]}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                cursor = self.conn.cursor()
                query = f"DELETE FROM {self.table_name} WHERE {primary_key} = ?"
                cursor.execute(query, (row_data[primary_key],))
                self.conn.commit()
                
                QMessageBox.information(self, "Успех", "Строка успешно удалена!")
                self.load_table_info()
                self.load_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении строки: {str(e)}")
    
    def closeEvent(self, event):
        """Закрытие соединения при закрытии диалога"""
        if self.conn:
            self.conn.close()
        event.accept()


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.db_path = ""
        self.setWindowTitle("Просмотр SQLite базы данных")
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Кнопка выбора файла
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Файл не выбран")
        file_layout.addWidget(self.file_label)
        
        select_button = QPushButton("Выбрать файл БД")
        select_button.clicked.connect(self.on_select_file)
        file_layout.addWidget(select_button)
        
        layout.addLayout(file_layout)
        
        # Список таблиц
        layout.addWidget(QLabel("Таблицы:"))
        self.tables_list = QListWidget()
        self.tables_list.itemDoubleClicked.connect(self.on_open_table)
        layout.addWidget(self.tables_list)
        
        # Кнопка открыть
        self.open_button = QPushButton("Открыть")
        self.open_button.clicked.connect(self.on_open_table)
        self.open_button.setEnabled(False)
        layout.addWidget(self.open_button)
    
    def on_select_file(self):
        """Выбрать файл базы данных"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл SQLite", "", "SQLite Files (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if filename:
            self.db_path = filename
            self.file_label.setText(f"Файл: {filename}")
            self.load_tables()
    
    def load_tables(self):
        """Загрузить список таблиц из базы данных"""
        if not self.db_path:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем список таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            self.tables_list.clear()
            for table in tables:
                self.tables_list.addItem(table[0])
            
            conn.close()
            self.open_button.setEnabled(len(tables) > 0)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить таблицы: {str(e)}")
    
    def on_open_table(self):
        """Открыть выбранную таблицу"""
        current_item = self.tables_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу!")
            return
        
        table_name = current_item.text()
        dialog = TableViewDialog(self, self.db_path, table_name)
        dialog.exec_()


def main():
    """Главная функция"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

