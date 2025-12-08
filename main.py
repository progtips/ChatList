"""Основной модуль GUI интерфейса ChatList"""
import sys
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QCheckBox, QMenuBar, QMenu, QMessageBox, QDialog, QLabel,
    QLineEdit, QDialogButtonBox, QHeaderView, QAbstractItemView,
    QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from db import Database
from network import NetworkManager
import logging


class SendRequestThread(QThread):
    """Поток для асинхронной отправки запросов"""
    finished = pyqtSignal(list)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, network_manager: NetworkManager, prompt: str, models: List):
        super().__init__()
        self.network_manager = network_manager
        self.prompt = prompt
        self.models = models
    
    def run(self):
        """Выполнить запросы в отдельном потоке"""
        try:
            self.progress.emit("Отправка запросов...")
            logging.info(f"Отправка промта в {len(self.models)} моделей")
            results = self.network_manager.send_to_all_models(self.prompt, self.models)
            logging.info(f"Получено {len(results)} результатов")
            self.finished.emit(results)
        except Exception as e:
            error_msg = f"Ошибка при отправке запросов: {str(e)}"
            logging.error(error_msg)
            self.error.emit(error_msg)


class PromptDialog(QDialog):
    """Диалог для создания/редактирования промта"""
    
    def __init__(self, parent=None, prompt_data: Optional[Dict] = None):
        super().__init__(parent)
        self.prompt_data = prompt_data
        self.setWindowTitle("Редактировать промт" if prompt_data else "Новый промт")
        self.setModal(True)
        self.init_ui()
        
        if prompt_data:
            self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Промт
        layout.addWidget(QLabel("Промт:"))
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setMinimumHeight(100)
        layout.addWidget(self.prompt_edit)
        
        # Теги
        layout.addWidget(QLabel("Теги (через запятую):"))
        self.tags_edit = QLineEdit()
        layout.addWidget(self.tags_edit)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Загрузить данные промта"""
        if self.prompt_data:
            self.prompt_edit.setPlainText(self.prompt_data.get('prompt', ''))
            self.tags_edit.setText(self.prompt_data.get('tags', ''))
    
    def get_data(self) -> Dict:
        """Получить данные из диалога"""
        return {
            'prompt': self.prompt_edit.toPlainText().strip(),
            'tags': self.tags_edit.text().strip()
        }


class ModelDialog(QDialog):
    """Диалог для добавления/редактирования модели"""
    
    def __init__(self, parent=None, model_data: Optional[Dict] = None):
        super().__init__(parent)
        self.model_data = model_data
        self.setWindowTitle("Редактировать модель" if model_data else "Новая модель")
        self.setModal(True)
        self.init_ui()
        
        if model_data:
            self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Название
        layout.addWidget(QLabel("Название:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # API URL
        layout.addWidget(QLabel("API URL:"))
        self.api_url_edit = QLineEdit()
        layout.addWidget(self.api_url_edit)
        
        # API ID
        layout.addWidget(QLabel("API ID (model):"))
        self.api_id_edit = QLineEdit()
        layout.addWidget(self.api_id_edit)
        
        # API Key Env Var
        layout.addWidget(QLabel("Имя переменной окружения с API-ключом:"))
        self.api_key_env_var_edit = QLineEdit()
        layout.addWidget(self.api_key_env_var_edit)
        
        # Тип модели
        layout.addWidget(QLabel("Тип модели (openai/deepseek/groq):"))
        self.model_type_edit = QLineEdit()
        layout.addWidget(self.model_type_edit)
        
        # Активна
        self.is_active_checkbox = QCheckBox("Активна")
        self.is_active_checkbox.setChecked(True)
        layout.addWidget(self.is_active_checkbox)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Загрузить данные модели"""
        if self.model_data:
            self.name_edit.setText(self.model_data.get('name', ''))
            self.api_url_edit.setText(self.model_data.get('api_url', ''))
            self.api_id_edit.setText(self.model_data.get('api_id', ''))
            self.api_key_env_var_edit.setText(self.model_data.get('api_key_env_var', ''))
            self.model_type_edit.setText(self.model_data.get('model_type', ''))
            self.is_active_checkbox.setChecked(bool(self.model_data.get('is_active', 1)))
    
    def get_data(self) -> Dict:
        """Получить данные из диалога"""
        return {
            'name': self.name_edit.text().strip(),
            'api_url': self.api_url_edit.text().strip(),
            'api_id': self.api_id_edit.text().strip(),
            'api_key_env_var': self.api_key_env_var_edit.text().strip(),
            'model_type': self.model_type_edit.text().strip().lower(),
            'is_active': 1 if self.is_active_checkbox.isChecked() else 0
        }




class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.network_manager = NetworkManager()
        self.temp_results: List[Dict] = []  # Временное хранилище результатов
        self.current_prompt_id: Optional[int] = None
        
        self.init_ui()
        self.load_prompts()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("ChatList - Сравнение ответов нейросетей")
        self.setGeometry(100, 100, 1200, 800)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Область ввода промта
        prompt_layout = QHBoxLayout()
        prompt_layout.addWidget(QLabel("Промт:"))
        
        self.prompt_combo = QComboBox()
        self.prompt_combo.setEditable(True)
        self.prompt_combo.currentTextChanged.connect(self.on_prompt_changed)
        prompt_layout.addWidget(self.prompt_combo, 3)
        
        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.on_send_clicked)
        prompt_layout.addWidget(self.send_button)
        
        main_layout.addLayout(prompt_layout)
        
        # Область текста промта
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("Введите промт или выберите из списка...")
        self.prompt_text.setMaximumHeight(150)
        main_layout.addWidget(self.prompt_text)
        
        # Индикатор загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Выбрать", "Модель", "Ответ"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setColumnWidth(0, 80)
        self.results_table.setColumnWidth(1, 150)
        # Настройка для многострочного отображения в колонке "Ответ"
        self.results_table.verticalHeader().setDefaultSectionSize(100)  # Высота строки по умолчанию
        self.results_table.setWordWrap(True)  # Включить перенос слов
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # Выбор целой строки
        main_layout.addWidget(self.results_table)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Сохранить выбранные")
        self.save_button.clicked.connect(self.on_save_clicked)
        self.save_button.setEnabled(False)
        buttons_layout.addWidget(self.save_button)
        
        self.open_button = QPushButton("Открыть")
        self.open_button.clicked.connect(self.on_open_selected_result)
        self.open_button.setEnabled(False)
        buttons_layout.addWidget(self.open_button)
        
        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        buttons_layout.addWidget(self.clear_button)
        
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Подключаем обработчик выбора строки для активации кнопки "Открыть"
        self.results_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Статусная строка
        self.statusBar().showMessage("Готово")
        
        # Создаем меню
        self.create_menu()
    
    def create_menu(self):
        """Создать меню приложения"""
        menubar = self.menuBar()
        
        # Меню "Промты"
        prompts_menu = menubar.addMenu("Промты")
        prompts_menu.addAction("Новый промт", self.on_new_prompt)
        prompts_menu.addAction("Управление промтами", self.on_manage_prompts)
        
        # Меню "Модели"
        models_menu = menubar.addMenu("Модели")
        models_menu.addAction("Добавить модель", self.on_add_model)
        models_menu.addAction("Управление моделями", self.on_manage_models)
        
        # Меню "Результаты"
        results_menu = menubar.addMenu("Результаты")
        results_menu.addAction("Просмотр результатов", self.on_view_results)
        
        # Меню "Настройки"
        settings_menu = menubar.addMenu("Настройки")
        settings_menu.addAction("Настройки", self.on_settings)
    
    def load_prompts(self):
        """Загрузить список промтов в выпадающий список"""
        self.prompt_combo.clear()
        prompts = self.db.get_prompts()
        for prompt in prompts:
            self.prompt_combo.addItem(
                f"{prompt['prompt'][:50]}... ({prompt['date'][:10]})",
                prompt['id']
            )
    
    def on_prompt_changed(self, text: str):
        """Обработчик изменения промта в списке"""
        current_id = self.prompt_combo.currentData()
        if current_id:
            prompt = self.db.get_prompt_by_id(current_id)
            if prompt:
                self.prompt_text.setPlainText(prompt['prompt'])
                self.current_prompt_id = prompt['id']
    
    def on_send_clicked(self):
        """Обработчик кнопки 'Отправить'"""
        prompt_text = self.prompt_text.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Ошибка", "Введите промт!")
            return
        
        # Очищаем временную таблицу
        self.temp_results.clear()
        self.results_table.setRowCount(0)
        self.save_button.setEnabled(False)
        
        # Получаем активные модели
        models_data = self.db.get_active_models()
        if not models_data:
            QMessageBox.warning(self, "Ошибка", "Нет активных моделей! Добавьте модели в меню 'Модели'.")
            return
        
        # Создаем экземпляры моделей
        from models import ModelFactory
        models = []
        for model_data in models_data:
            model = ModelFactory.create_model_from_db(model_data)
            if model:
                models.append(model)
        
        if not models:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить модели!")
            return
        
        # Отправляем запросы в отдельном потоке
        self.statusBar().showMessage("Отправка запросов...")
        self.send_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        
        self.request_thread = SendRequestThread(self.network_manager, prompt_text, models)
        self.request_thread.finished.connect(self.on_requests_finished)
        self.request_thread.progress.connect(self.statusBar().showMessage)
        self.request_thread.error.connect(self.on_request_error)
        self.request_thread.start()
    
    def on_requests_finished(self, results: List[Dict]):
        """Обработчик завершения запросов"""
        self.send_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(f"Запросы завершены. Получено ответов: {len(results)}")
        
        # Сохраняем результаты во временное хранилище
        self.temp_results = results
        
        # Подсчитываем успешные и неуспешные запросы
        success_count = sum(1 for r in results if r.get('success'))
        error_count = len(results) - success_count
        
        if error_count > 0:
            self.statusBar().showMessage(
                f"Запросы завершены. Успешно: {success_count}, Ошибок: {error_count}"
            )
        
        # Отображаем результаты в таблице
        self.results_table.setRowCount(len(results))
        for row, result in enumerate(results):
            # Чекбокс
            checkbox = QCheckBox()
            self.results_table.setCellWidget(row, 0, checkbox)
            checkbox.stateChanged.connect(self.on_checkbox_changed)
            
            # Модель
            model_item = QTableWidgetItem(result.get('model_name', 'Unknown'))
            self.results_table.setItem(row, 1, model_item)
            
            # Ответ (многострочное поле)
            if result.get('success'):
                response_text = result.get('response', 'Нет ответа')
                response_item = QTableWidgetItem(response_text)
                response_item.setForeground(Qt.darkGreen)  # Зеленый цвет для успешных ответов
            else:
                error_msg = result.get('error', 'Неизвестная ошибка')
                response_text = f"❌ {error_msg}"
                response_item = QTableWidgetItem(response_text)
                response_item.setForeground(Qt.red)  # Красный цвет для ошибок
            
            # Настройка многострочного отображения
            response_item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)  # Выравнивание по верху и слева
            response_item.setFlags(response_item.flags() | Qt.TextWordWrap)  # Разрешить перенос слов
            
            # Вычисляем высоту строки на основе длины текста
            text_lines = len(response_text.split('\n')) + (len(response_text) // 80)  # Примерно 80 символов на строку
            min_height = max(100, min(300, text_lines * 25))  # Минимум 100, максимум 300 пикселей
            self.results_table.setRowHeight(row, min_height)
            
            self.results_table.setItem(row, 2, response_item)
        
        self.on_checkbox_changed()  # Обновляем состояние кнопки сохранения
    
    def on_checkbox_changed(self):
        """Обработчик изменения чекбоксов"""
        has_selected = False
        for row in range(self.results_table.rowCount()):
            checkbox = self.results_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                has_selected = True
                break
        self.save_button.setEnabled(has_selected)
    
    def on_save_clicked(self):
        """Обработчик кнопки 'Сохранить выбранные'"""
        prompt_text = self.prompt_text.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Ошибка", "Нет промта для сохранения!")
            return
        
        # Сохраняем промт, если его еще нет в БД
        if not self.current_prompt_id:
            self.current_prompt_id = self.db.create_prompt(prompt_text)
        
        # Собираем выбранные результаты
        results_to_save = []
        # Получаем словарь моделей для поиска ID по имени
        all_models = {m['name']: m['id'] for m in self.db.get_all_models()}
        
        for row in range(self.results_table.rowCount()):
            checkbox = self.results_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                result = self.temp_results[row]
                if result.get('success'):
                    model_name = result.get('model_name', 'Unknown')
                    model_id = all_models.get(model_name)
                    results_to_save.append({
                        'prompt_id': self.current_prompt_id,
                        'model_id': model_id,
                        'prompt_text': prompt_text,
                        'model_name': model_name,
                        'response_text': result.get('response', ''),
                        'metadata': None
                    })
        
        if not results_to_save:
            QMessageBox.warning(self, "Ошибка", "Выберите результаты для сохранения!")
            return
        
        # Сохраняем в БД
        saved_count = self.db.save_results(results_to_save)
        QMessageBox.information(self, "Успех", f"Сохранено результатов: {saved_count}")
        
        # Очищаем временную таблицу
        self.on_clear_clicked()
    
    def on_request_error(self, error_msg: str):
        """Обработчик ошибки при отправке запросов"""
        self.send_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Ошибка", error_msg)
        self.statusBar().showMessage("Ошибка при отправке запросов")
    
    def on_clear_clicked(self):
        """Обработчик кнопки 'Очистить'"""
        self.temp_results.clear()
        self.results_table.setRowCount(0)
        self.save_button.setEnabled(False)
        self.open_button.setEnabled(False)
        self.statusBar().showMessage("Очищено")
    
    def on_selection_changed(self):
        """Обработчик изменения выбора строки в таблице"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        self.open_button.setEnabled(len(selected_rows) > 0)
    
    def on_open_selected_result(self):
        """Обработчик кнопки 'Открыть' для просмотра выбранного результата в Markdown"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для просмотра!")
            return
        
        row = selected_rows[0].row()
        if row < 0 or row >= len(self.temp_results):
            return
        
        result = self.temp_results[row]
        model_name = result.get('model_name', 'Unknown')
        
        if result.get('success'):
            response_text = result.get('response', 'Нет ответа')
        else:
            error_msg = result.get('error', 'Неизвестная ошибка')
            response_text = f"# Ошибка\n\n{error_msg}"
        
        # Получаем промт из текстового поля
        prompt_text = self.prompt_text.toPlainText().strip()
        
        # Создаем Markdown контент
        from datetime import datetime
        md_content = f"""# Результат от модели: {model_name}

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Промт

{prompt_text}

---

## Ответ

{response_text}
"""
        
        # Открываем диалог просмотра
        from markdown_viewer import MarkdownViewDialog
        dialog = MarkdownViewDialog(self, md_content, model_name)
        dialog.exec_()
    
    def on_new_prompt(self):
        """Создать новый промт"""
        dialog = PromptDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data['prompt']:
                self.db.create_prompt(data['prompt'], data['tags'] if data['tags'] else None)
                self.load_prompts()
                QMessageBox.information(self, "Успех", "Промт сохранен!")
    
    def on_manage_prompts(self):
        """Управление промтами"""
        from dialogs import PromptsManageDialog
        dialog = PromptsManageDialog(self, self.db)
        dialog.exec_()
        self.load_prompts()  # Обновляем список после закрытия диалога
    
    def on_add_model(self):
        """Добавить новую модель"""
        dialog = ModelDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if all([data['name'], data['api_url'], data['api_id'], data['api_key_env_var'], data['model_type']]):
                try:
                    self.db.create_model(
                        data['name'],
                        data['api_url'],
                        data['api_id'],
                        data['api_key_env_var'],
                        data['model_type'],
                        data['is_active']
                    )
                    QMessageBox.information(self, "Успех", "Модель добавлена!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось добавить модель: {str(e)}")
            else:
                QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
    
    def on_manage_models(self):
        """Управление моделями"""
        from dialogs import ModelsManageDialog
        dialog = ModelsManageDialog(self, self.db)
        dialog.exec_()
    
    def on_view_results(self):
        """Просмотр сохраненных результатов"""
        from dialogs import ResultsDialog
        dialog = ResultsDialog(self, self.db)
        dialog.exec_()
    
    def on_settings(self):
        """Настройки программы"""
        QMessageBox.information(self, "Информация", "Функция настроек будет реализована позже")
    
    def closeEvent(self, event):
        """Обработчик закрытия приложения"""
        self.db.close()
        event.accept()


def main():
    """Главная функция"""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('chatlist.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
