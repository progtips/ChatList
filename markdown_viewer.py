"""Диалог для просмотра Markdown контента"""
import markdown
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MarkdownViewDialog(QDialog):
    """Диалог для просмотра Markdown на весь экран"""
    
    def __init__(self, parent=None, md_content: str = "", title: str = "Просмотр"):
        super().__init__(parent)
        self.setWindowTitle(f"Просмотр: {title}")
        self.setMinimumSize(1200, 800)
        self.md_content = md_content
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Текстовый браузер для отображения HTML (из Markdown)
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        
        # Настройка шрифта
        font = QFont("Consolas", 11)
        self.text_browser.setFont(font)
        
        # Конвертируем Markdown в HTML
        html_content = self.convert_markdown_to_html(self.md_content)
        self.text_browser.setHtml(html_content)
        
        layout.addWidget(self.text_browser)
        
        # Кнопка закрытия
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def convert_markdown_to_html(self, md_text: str) -> str:
        """Конвертировать Markdown в HTML с красивым стилем"""
        try:
            # Конвертируем Markdown в HTML
            html = markdown.markdown(
                md_text,
                extensions=['fenced_code', 'tables', 'nl2br', 'codehilite']
            )
            
            # Добавляем красивые стили
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #ffffff;
                    }}
                    h1 {{
                        color: #2c3e50;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 10px;
                        margin-top: 0;
                    }}
                    h2 {{
                        color: #34495e;
                        border-bottom: 2px solid #ecf0f1;
                        padding-bottom: 8px;
                        margin-top: 30px;
                    }}
                    h3 {{
                        color: #7f8c8d;
                        margin-top: 25px;
                    }}
                    code {{
                        background-color: #f4f4f4;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 0.9em;
                    }}
                    pre {{
                        background-color: #2c3e50;
                        color: #ecf0f1;
                        padding: 15px;
                        border-radius: 5px;
                        overflow-x: auto;
                        border-left: 4px solid #3498db;
                    }}
                    pre code {{
                        background-color: transparent;
                        color: inherit;
                        padding: 0;
                    }}
                    blockquote {{
                        border-left: 4px solid #3498db;
                        margin: 0;
                        padding-left: 20px;
                        color: #7f8c8d;
                        font-style: italic;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 12px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #3498db;
                        color: white;
                        font-weight: bold;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    a {{
                        color: #3498db;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    hr {{
                        border: none;
                        border-top: 2px solid #ecf0f1;
                        margin: 30px 0;
                    }}
                    strong {{
                        color: #2c3e50;
                        font-weight: 600;
                    }}
                    ul, ol {{
                        padding-left: 30px;
                    }}
                    li {{
                        margin: 5px 0;
                    }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """
            return styled_html
        except Exception as e:
            # Если не удалось конвертировать, показываем как простой текст
            return f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        line-height: 1.6;
                        padding: 20px;
                        white-space: pre-wrap;
                    }}
                </style>
            </head>
            <body>
                <h2>Ошибка форматирования:</h2>
                <p>{str(e)}</p>
                <hr>
                <h2>Исходный текст:</h2>
                <pre>{md_text}</pre>
            </body>
            </html>
            """

