"""Диалоговые окна для управления данными"""
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QDialogButtonBox,
    QAbstractItemView, QHeaderView, QComboBox, QCheckBox, QMessageBox,
    QFileDialog
)
from PyQt5.QtCore import Qt
import json
from datetime import datetime


class PromptsManageDialog(QDialog):
    """Диалог для управления промтами с поиском и сортировкой"""
    
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Управление промтами")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_prompts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Поиск и сортировка
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.load_prompts)
        search_layout.addWidget(self.search_edit)
        
        search_layout.addWidget(QLabel("Сортировать по:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Дата", "Промт"])
        self.sort_combo.currentTextChanged.connect(self.load_prompts)
        search_layout.addWidget(self.sort_combo)
        
        layout.addLayout(search_layout)
        
        # Таблица промтов
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Дата", "Промт"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 150)
        layout.addWidget(self.table)
        
        # Кнопки CRUD
        buttons_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Создать")
        self.create_button.clicked.connect(self.on_create)
        buttons_layout.addWidget(self.create_button)
        
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.on_edit)
        self.edit_button.setEnabled(False)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.on_delete)
        self.delete_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_button)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        # Подключаем обработчик выбора строки
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def load_prompts(self):
        """Загрузить промты из БД"""
        if not self.db:
            return
        
        search = self.search_edit.text().strip()
        sort_by = self.sort_combo.currentText().lower()
        
        # Маппинг названий колонок
        sort_mapping = {
            "дата": "date",
            "промт": "prompt"
        }
        order_by = sort_mapping.get(sort_by, "date")
        
        prompts = self.db.get_prompts(search=search if search else None, order_by=order_by)
        
        self.table.setRowCount(len(prompts))
        for row, prompt in enumerate(prompts):
            self.table.setItem(row, 0, QTableWidgetItem(str(prompt.get('id', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(prompt.get('date', '')))
            self.table.setItem(row, 2, QTableWidgetItem(prompt.get('prompt', '')[:200]))
    
    def on_selection_changed(self):
        """Обработчик изменения выбора строки"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def on_create(self):
        """Создать новый промт"""
        from main import PromptDialog
        dialog = PromptDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data['prompt']:
                self.db.create_prompt(data['prompt'], data['tags'] if data['tags'] else None)
                self.load_prompts()
                QMessageBox.information(self, "Успех", "Промт создан!")
    
    def on_edit(self):
        """Редактировать выбранный промт"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите промт для редактирования!")
            return
        
        prompt_id = int(self.table.item(current_row, 0).text())
        prompt_data = self.db.get_prompt_by_id(prompt_id)
        
        if prompt_data:
            from main import PromptDialog
            dialog = PromptDialog(self, prompt_data)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                if data['prompt']:
                    self.db.update_prompt(prompt_id, data['prompt'], data['tags'] if data['tags'] else None)
                    self.load_prompts()
                    QMessageBox.information(self, "Успех", "Промт обновлен!")
    
    def on_delete(self):
        """Удалить выбранный промт"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите промт для удаления!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите удалить этот промт?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            prompt_id = int(self.table.item(current_row, 0).text())
            if self.db.delete_prompt(prompt_id):
                self.load_prompts()
                QMessageBox.information(self, "Успех", "Промт удален!")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить промт!")


class ModelsManageDialog(QDialog):
    """Диалог для управления моделями"""
    
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Управление моделями")
        self.setMinimumSize(900, 600)
        self.init_ui()
        self.load_models()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Таблица моделей
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "API URL", "API ID", "Тип", "Активна", "Дата создания"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 80)
        layout.addWidget(self.table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.on_edit)
        buttons_layout.addWidget(self.edit_button)
        
        self.toggle_button = QPushButton("Переключить активность")
        self.toggle_button.clicked.connect(self.on_toggle)
        buttons_layout.addWidget(self.toggle_button)
        
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.on_delete)
        buttons_layout.addWidget(self.delete_button)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def load_models(self):
        """Загрузить модели из БД"""
        if not self.db:
            return
        
        models = self.db.get_all_models()
        self.table.setRowCount(len(models))
        for row, model in enumerate(models):
            self.table.setItem(row, 0, QTableWidgetItem(str(model.get('id', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(model.get('name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(model.get('api_url', '')[:50]))
            self.table.setItem(row, 3, QTableWidgetItem(model.get('api_id', '')))
            self.table.setItem(row, 4, QTableWidgetItem(model.get('model_type', '')))
            self.table.setItem(row, 5, QTableWidgetItem("Да" if model.get('is_active') else "Нет"))
            self.table.setItem(row, 6, QTableWidgetItem(model.get('created_at', '')))
    
    def on_edit(self):
        """Редактировать выбранную модель"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите модель для редактирования!")
            return
        
        model_id = int(self.table.item(current_row, 0).text())
        model_data = self.db.get_model_by_id(model_id)
        
        if model_data:
            from main import ModelDialog
            dialog = ModelDialog(self, model_data)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                if all([data['name'], data['api_url'], data['api_id'], data['api_key_env_var'], data['model_type']]):
                    try:
                        self.db.update_model(
                            model_id,
                            name=data['name'],
                            api_url=data['api_url'],
                            api_id=data['api_id'],
                            api_key_env_var=data['api_key_env_var'],
                            model_type=data['model_type'],
                            is_active=data['is_active']
                        )
                        self.load_models()
                        QMessageBox.information(self, "Успех", "Модель обновлена!")
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", f"Не удалось обновить модель: {str(e)}")
    
    def on_toggle(self):
        """Переключить активность модели"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите модель!")
            return
        
        model_id = int(self.table.item(current_row, 0).text())
        if self.db.toggle_model_active(model_id):
            self.load_models()
            QMessageBox.information(self, "Успех", "Активность модели изменена!")
    
    def on_delete(self):
        """Удалить выбранную модель"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите модель для удаления!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите удалить эту модель?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            model_id = int(self.table.item(current_row, 0).text())
            if self.db.delete_model(model_id):
                self.load_models()
                QMessageBox.information(self, "Успех", "Модель удалена!")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить модель!")


class ResultsDialog(QDialog):
    """Диалог для просмотра сохраненных результатов с поиском, сортировкой и экспортом"""
    
    def __init__(self, parent=None, db: Optional[object] = None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Сохраненные результаты")
        self.setMinimumSize(1000, 700)
        self.init_ui()
        self.load_results()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Поиск и сортировка
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.load_results)
        search_layout.addWidget(self.search_edit)
        
        search_layout.addWidget(QLabel("Сортировать по:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Дата создания", "Модель", "Промт"])
        self.sort_combo.currentTextChanged.connect(self.load_results)
        search_layout.addWidget(self.sort_combo)
        
        layout.addLayout(search_layout)
        
        # Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Промт", "Модель", "Ответ", "Дата"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(4, 150)
        layout.addWidget(self.table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.export_md_button = QPushButton("Экспорт в Markdown")
        self.export_md_button.clicked.connect(self.export_to_markdown)
        buttons_layout.addWidget(self.export_md_button)
        
        self.export_json_button = QPushButton("Экспорт в JSON")
        self.export_json_button.clicked.connect(self.export_to_json)
        buttons_layout.addWidget(self.export_json_button)
        
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.on_delete)
        buttons_layout.addWidget(self.delete_button)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def load_results(self):
        """Загрузить результаты из БД"""
        if not self.db:
            return
        
        search = self.search_edit.text().strip()
        sort_by = self.sort_combo.currentText()
        
        # Маппинг названий колонок
        sort_mapping = {
            "Дата создания": "created_at",
            "Модель": "model_name",
            "Промт": "prompt_text"
        }
        order_by = sort_mapping.get(sort_by, "created_at")
        
        results = self.db.get_results(search=search if search else None, order_by=order_by)
        
        self.table.setRowCount(len(results))
        self.table.setWordWrap(True)  # Включить перенос слов
        self.table.verticalHeader().setDefaultSectionSize(100)  # Высота строки по умолчанию
        
        for row, result in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(str(result.get('id', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(result.get('prompt_text', '')[:100]))
            self.table.setItem(row, 2, QTableWidgetItem(result.get('model_name', '')))
            
            # Ответ с многострочным отображением
            response_text = result.get('response_text', '')
            response_item = QTableWidgetItem(response_text)
            response_item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
            response_item.setFlags(response_item.flags() | Qt.TextWordWrap)
            
            # Вычисляем высоту строки на основе длины текста
            text_lines = len(response_text.split('\n')) + (len(response_text) // 80)
            min_height = max(100, min(300, text_lines * 25))
            self.table.setRowHeight(row, min_height)
            
            self.table.setItem(row, 3, response_item)
            self.table.setItem(row, 4, QTableWidgetItem(result.get('created_at', '')))
    
    def export_to_markdown(self):
        """Экспортировать результаты в Markdown"""
        if not self.db:
            return
        
        # Получаем выбранные строки или все результаты
        selected_rows = [item.row() for item in self.table.selectedItems()]
        if not selected_rows:
            # Если ничего не выбрано, экспортируем все видимые результаты
            selected_rows = list(range(self.table.rowCount()))
        
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Нет результатов для экспорта!")
            return
        
        # Получаем уникальные ID результатов
        result_ids = set()
        for row in selected_rows:
            result_id = int(self.table.item(row, 0).text())
            result_ids.add(result_id)
        
        # Загружаем полные данные результатов
        results = []
        for result_id in result_ids:
            all_results = self.db.get_results()
            for r in all_results:
                if r['id'] == result_id:
                    results.append(r)
                    break
        
        if not results:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить результаты!")
            return
        
        # Выбираем файл для сохранения
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как Markdown", "", "Markdown Files (*.md);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("# Экспорт результатов ChatList\n\n")
                    f.write(f"Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"Всего результатов: {len(results)}\n\n")
                    f.write("---\n\n")
                    
                    for i, result in enumerate(results, 1):
                        f.write(f"## Результат #{i}\n\n")
                        f.write(f"**Модель:** {result.get('model_name', 'Unknown')}\n\n")
                        f.write(f"**Дата:** {result.get('created_at', '')}\n\n")
                        f.write(f"**Промт:**\n\n{result.get('prompt_text', '')}\n\n")
                        f.write(f"**Ответ:**\n\n{result.get('response_text', '')}\n\n")
                        f.write("---\n\n")
                
                QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать: {str(e)}")
    
    def export_to_json(self):
        """Экспортировать результаты в JSON"""
        if not self.db:
            return
        
        # Получаем выбранные строки или все результаты
        selected_rows = [item.row() for item in self.table.selectedItems()]
        if not selected_rows:
            selected_rows = list(range(self.table.rowCount()))
        
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Нет результатов для экспорта!")
            return
        
        # Получаем уникальные ID результатов
        result_ids = set()
        for row in selected_rows:
            result_id = int(self.table.item(row, 0).text())
            result_ids.add(result_id)
        
        # Загружаем полные данные результатов
        results = []
        for result_id in result_ids:
            all_results = self.db.get_results()
            for r in all_results:
                if r['id'] == result_id:
                    results.append(r)
                    break
        
        if not results:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить результаты!")
            return
        
        # Выбираем файл для сохранения
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                export_data = {
                    'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_results': len(results),
                    'results': results
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать: {str(e)}")
    
    def on_delete(self):
        """Удалить выбранный результат"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите результат для удаления!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите удалить этот результат?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result_id = int(self.table.item(current_row, 0).text())
            if self.db.delete_result(result_id):
                self.load_results()
                QMessageBox.information(self, "Успех", "Результат удален!")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить результат!")

