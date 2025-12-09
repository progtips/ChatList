"""Диалог для улучшения промтов"""
import logging
from typing import Optional, List
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QComboBox, QCheckBox, QListWidget, QListWidgetItem, QMessageBox,
    QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from models import Model
from prompt_assistant import PromptAssistant

logger = logging.getLogger(__name__)


class ImprovePromptThread(QThread):
    """Поток для асинхронного улучшения промта"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, assistant: PromptAssistant, prompt: str, model: Model,
                 generate_variants: bool = True, adapt_for_type: Optional[str] = None):
        super().__init__()
        self.assistant = assistant
        self.prompt = prompt
        self.model = model
        self.generate_variants = generate_variants
        self.adapt_for_type = adapt_for_type
    
    def run(self):
        """Выполнить улучшение промта"""
        try:
            self.progress.emit("Улучшение промта...")
            result = self.assistant.improve_with_variants(
                self.prompt,
                self.model,
                self.generate_variants,
                self.adapt_for_type
            )
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Ошибка при улучшении промта: {str(e)}")
            self.finished.emit({
                'success': False,
                'error': f'Ошибка: {str(e)}'
            })


class PromptImprovementDialog(QDialog):
    """Диалог для улучшения промтов"""
    
    def __init__(self, parent=None, original_prompt: str = "", models: List[Model] = None):
        super().__init__(parent)
        self.original_prompt = original_prompt
        self.models = models or []
        self.selected_variant = None
        self.assistant = PromptAssistant()
        
        self.setWindowTitle("Улучшение промта")
        self.setMinimumSize(900, 700)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Выбор модели
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Модель для улучшения:"))
        self.model_combo = QComboBox()
        for model in self.models:
            self.model_combo.addItem(model.name, model)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # Опции
        options_group = QGroupBox("Опции")
        options_layout = QVBoxLayout()
        
        self.variants_checkbox = QCheckBox("Генерировать варианты переформулировки (2-3 шт.)")
        self.variants_checkbox.setChecked(True)
        options_layout.addWidget(self.variants_checkbox)
        
        self.adapt_checkbox = QCheckBox("Адаптировать под тип модели")
        self.adapt_checkbox.setChecked(False)
        options_layout.addWidget(self.adapt_checkbox)
        
        adapt_type_layout = QHBoxLayout()
        adapt_type_layout.addWidget(QLabel("Тип адаптации:"))
        self.adapt_type_combo = QComboBox()
        self.adapt_type_combo.addItems(["Код", "Анализ", "Креатив"])
        self.adapt_type_combo.setEnabled(False)
        self.adapt_checkbox.toggled.connect(self.adapt_type_combo.setEnabled)
        adapt_type_layout.addWidget(self.adapt_type_combo)
        adapt_type_layout.addStretch()
        options_layout.addLayout(adapt_type_layout)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Исходный промт
        layout.addWidget(QLabel("Исходный промт:"))
        self.original_text = QTextEdit()
        self.original_text.setPlainText(self.original_prompt)
        self.original_text.setReadOnly(True)
        self.original_text.setMaximumHeight(100)
        layout.addWidget(self.original_text)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Улучшенный промт
        layout.addWidget(QLabel("Улучшенный промт:"))
        self.improved_text = QTextEdit()
        self.improved_text.setPlaceholderText("Здесь появится улучшенная версия промта...")
        self.improved_text.setMaximumHeight(120)
        layout.addWidget(self.improved_text)
        
        # Адаптированный промт (если выбран)
        self.adapted_group = QGroupBox("Адаптированный промт")
        adapted_layout = QVBoxLayout()
        self.adapted_text = QTextEdit()
        self.adapted_text.setPlaceholderText("Здесь появится адаптированная версия...")
        self.adapted_text.setMaximumHeight(100)
        adapted_layout.addWidget(self.adapted_text)
        self.adapted_group.setLayout(adapted_layout)
        self.adapted_group.setVisible(False)
        layout.addWidget(self.adapted_group)
        
        # Альтернативные варианты
        variants_group = QGroupBox("Альтернативные варианты")
        variants_layout = QVBoxLayout()
        
        self.variants_list = QListWidget()
        self.variants_list.setMaximumHeight(150)
        self.variants_list.itemDoubleClicked.connect(self.on_variant_selected)
        variants_layout.addWidget(self.variants_list)
        
        variants_buttons = QHBoxLayout()
        self.use_variant_button = QPushButton("Использовать выбранный вариант")
        self.use_variant_button.clicked.connect(self.on_use_variant)
        self.use_variant_button.setEnabled(False)
        variants_buttons.addWidget(self.use_variant_button)
        variants_buttons.addStretch()
        variants_layout.addLayout(variants_buttons)
        
        variants_group.setLayout(variants_layout)
        layout.addWidget(variants_group)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.improve_button = QPushButton("Улучшить")
        self.improve_button.clicked.connect(self.on_improve)
        buttons_layout.addWidget(self.improve_button)
        
        self.use_improved_button = QPushButton("Использовать улучшенный")
        self.use_improved_button.clicked.connect(self.on_use_improved)
        self.use_improved_button.setEnabled(False)
        self.use_improved_button.setToolTip("Подставить улучшенный промт в поле ввода")
        buttons_layout.addWidget(self.use_improved_button)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.reject)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Подключаем обработчик выбора варианта
        self.variants_list.itemSelectionChanged.connect(self.on_variant_selection_changed)
    
    def on_improve(self):
        """Обработчик кнопки 'Улучшить'"""
        if not self.original_prompt.strip():
            QMessageBox.warning(self, "Ошибка", "Введите промт для улучшения!")
            return
        
        if self.model_combo.count() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет доступных моделей!")
            return
        
        # Получаем выбранную модель
        model = self.model_combo.currentData()
        if not model:
            QMessageBox.warning(self, "Ошибка", "Выберите модель!")
            return
        
        # Получаем опции
        generate_variants = self.variants_checkbox.isChecked()
        adapt_for_type = None
        if self.adapt_checkbox.isChecked():
            adapt_type_map = {
                "Код": "code",
                "Анализ": "analysis",
                "Креатив": "creative"
            }
            adapt_for_type = adapt_type_map.get(self.adapt_type_combo.currentText())
        
        # Очищаем предыдущие результаты
        self.improved_text.clear()
        self.adapted_text.clear()
        self.variants_list.clear()
        self.use_improved_button.setEnabled(False)
        self.adapted_group.setVisible(False)
        
        # Показываем прогресс
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.improve_button.setEnabled(False)
        
        # Запускаем улучшение в отдельном потоке
        self.improve_thread = ImprovePromptThread(
            self.assistant,
            self.original_prompt,
            model,
            generate_variants,
            adapt_for_type
        )
        self.improve_thread.finished.connect(self.on_improvement_finished)
        self.improve_thread.progress.connect(self.progress_bar.setFormat)
        self.improve_thread.start()
    
    def on_improvement_finished(self, result: dict):
        """Обработчик завершения улучшения"""
        self.progress_bar.setVisible(False)
        self.improve_button.setEnabled(True)
        
        if not result.get('success'):
            error = result.get('error', 'Неизвестная ошибка')
            QMessageBox.critical(self, "Ошибка", f"Не удалось улучшить промт:\n{error}")
            return
        
        # Отображаем улучшенный промт
        improved = result.get('improved_prompt')
        if improved:
            self.improved_text.setPlainText(improved)
            self.use_improved_button.setEnabled(True)
        
        # Отображаем адаптированный промт
        adapted = result.get('adapted_prompt')
        if adapted:
            self.adapted_text.setPlainText(adapted)
            self.adapted_group.setVisible(True)
        
        # Отображаем варианты
        variants = result.get('variants', [])
        if variants:
            for i, variant in enumerate(variants, 1):
                item = QListWidgetItem(f"Вариант {i}: {variant[:100]}...")
                item.setData(Qt.UserRole, variant)
                self.variants_list.addItem(item)
        
        if improved or variants or adapted:
            QMessageBox.information(self, "Успех", "Промт успешно улучшен!")
    
    def on_variant_selection_changed(self):
        """Обработчик изменения выбора варианта"""
        has_selection = len(self.variants_list.selectedItems()) > 0
        self.use_variant_button.setEnabled(has_selection)
    
    def on_variant_selected(self, item: QListWidgetItem):
        """Обработчик двойного клика по варианту"""
        self.on_use_variant()
    
    def on_use_variant(self):
        """Использовать выбранный вариант"""
        selected_items = self.variants_list.selectedItems()
        if not selected_items:
            return
        
        variant = selected_items[0].data(Qt.UserRole)
        self.selected_variant = variant
        self.accept()
    
    def on_use_improved(self):
        """Использовать улучшенный промт"""
        improved = self.improved_text.toPlainText().strip()
        if improved:
            self.selected_variant = improved
            self.accept()
    
    def get_selected_prompt(self) -> Optional[str]:
        """Получить выбранный промт"""
        return self.selected_variant

