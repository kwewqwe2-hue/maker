from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel,
    QScrollArea, QFrame, QComboBox, QListWidget,
    QListWidgetItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtBoundSignal
from PyQt5.QtGui import QFont, QColor, QPalette

class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, ai_client, messages):
        super().__init__()
        self.ai_client = ai_client
        self.messages = messages

    def run(self):
        try:
            result = self.ai_client.chat(self.messages)
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                self.finished.emit(content)
            elif "error" in result:
                self.error.emit(result["error"])
            else:
                self.error.emit("未知错误")
        except Exception as e:
            self.error.emit(str(e))

class UnifiedAIPanel(QWidget):
    response_ready = pyqtBoundSignal = None

    def __init__(self, ai_client, title="智能助手", system_prompt=""):
        super().__init__()
        self.ai_client = ai_client
        self.title = title
        self.system_prompt = system_prompt or "你是一位专业、友好的中国古代建筑研究专家助手。"
        self.chat_history = [{"role": "system", "content": self.system_prompt}]
        self.current_worker = None
        self.is_asking = False

        self.BG_DEEPEST = "#080808"
        self.BG_PRIMARY = "#141414"
        self.BG_SURFACE = "#1a1a1a"
        self.BG_CARD = "#202020"
        self.BG_ELEVATED = "#262626"
        self.BG_HOVER = "#2d2d2d"
        self.PRIMARY_DARK = "#0a4a4a"
        self.PRIMARY = "#0d5c5c"
        self.PRIMARY_LIGHT = "#108080"
        self.PRIMARY_BRIGHT = "#14a0a0"
        self.ACCENT_GOLD = "#c9a227"
        self.TEXT_PRIMARY = "#f0f0f0"
        self.TEXT_SECONDARY = "#a0a0a0"
        self.TEXT_TERTIARY = "#606060"
        self.TEXT_DISABLED = "#404040"
        self.SUCCESS = "#2d8a4e"
        self.BORDER_SUBTLE = "#2a2a2a"
        self.BORDER_NORMAL = "#333333"

        self.init_ui()

    def get_font(self, size, weight="normal"):
        weights = {"thin": 100, "light": 300, "normal": 400, "medium": 500, "semibold": 600, "bold": 700}
        return QFont("Microsoft YaHei", size, weights.get(weight, 400))

    def init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.BG_SURFACE};
            }}
            QTextEdit {{
                background-color: {self.BG_CARD};
                color: {self.TEXT_PRIMARY};
                border: none;
                border-radius: 12px;
                padding: 16px;
                font-size: 13px;
                line-height: 1.6;
            }}
            QLineEdit {{
                background-color: {self.BG_CARD};
                color: {self.TEXT_PRIMARY};
                border: 1px solid {self.BORDER_SUBTLE};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {self.PRIMARY_BRIGHT};
            }}
            QLineEdit::placeholder {{
                color: {self.TEXT_TERTIARY};
            }}
            QPushButton {{
                background-color: {self.PRIMARY};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {self.PRIMARY_LIGHT};
            }}
            QPushButton:disabled {{
                background-color: {self.BG_HOVER};
                color: {self.TEXT_DISABLED};
            }}
            QComboBox {{
                background-color: {self.BG_CARD};
                color: {self.TEXT_PRIMARY};
                border: 1px solid {self.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        title_label = QLabel(f"💬 {self.title}")
        title_label.setFont(self.get_font(16, "semibold"))
        title_label.setStyleSheet(f"color: {self.TEXT_PRIMARY};")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.status_label = QLabel("未连接")
        self.status_label.setFont(self.get_font(11, "normal"))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(26)
        self.status_label.setStyleSheet(f"""
            background-color: {self.BG_CARD};
            color: {self.TEXT_TERTIARY};
            border-radius: 13px;
            padding: 0 12px;
            font-size: 11px;
        """)
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "通用问答",
            "图片分析",
            "建筑知识",
            "桥梁历史"
        ])
        self.mode_combo.setFixedHeight(36)
        self.mode_combo.setFont(self.get_font(12))
        layout.addWidget(self.mode_combo)

        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet("border: none; background-color: transparent;")
        self.chat_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()

        self.chat_area.setWidget(self.chat_content)
        layout.addWidget(self.chat_area, 1)

        self.add_welcome_message()

        input_frame = QFrame()
        input_frame.setStyleSheet(f"""
            background-color: {self.BG_CARD};
            border-radius: 12px;
            border: 1px solid {self.BORDER_SUBTLE};
        """)
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 10, 12, 10)
        input_layout.setSpacing(10)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入您的问题，按 Enter 发送...")
        self.input_box.setFont(self.get_font(13))
        self.input_box.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_box)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedHeight(38)
        self.send_btn.setFont(self.get_font(13, "medium"))
        self.send_btn.clicked.connect(self.send_message)
        btn_layout.addWidget(self.send_btn)

        input_layout.addLayout(btn_layout)

        layout.addWidget(input_frame)

        self.update_status()

    def add_welcome_message(self):
        welcome_html = f"""
        <div style="padding: 16px;">
            <div style="background-color: {self.BG_CARD}; border-radius: 12px; padding: 16px;">
                <div style="color: {self.ACCENT_GOLD}; font-size: 14px; font-weight: 500; margin-bottom: 10px;">
                    欢迎使用智能助手
                </div>
                <div style="color: {self.TEXT_SECONDARY}; font-size: 12px; line-height: 1.6;">
                    我可以帮您解答关于中国古代建筑的问题，包括：
                </div>
                <ul style="color: {self.TEXT_SECONDARY}; font-size: 12px; line-height: 1.8; margin: 10px 0 0 0; padding-left: 18px;">
                    <li>《营造法式》术语解析</li>
                    <li>古建筑构造与工艺</li>
                    <li>桥梁历史与技术</li>
                    <li>宫殿色彩与文化</li>
                </ul>
                <div style="color: {self.TEXT_TERTIARY}; font-size: 11px; margin-top: 12px;">
                    💡 提示：请先在设置中配置 API 密钥以启用 AI 功能
                </div>
            </div>
        </div>
        """
        self._add_html_message(welcome_html)

    def _add_html_message(self, html):
        msg_frame = QFrame()
        msg_frame.setStyleSheet(f"background-color: transparent;")
        msg_layout = QVBoxLayout(msg_frame)
        msg_layout.setContentsMargins(0, 0, 0, 0)

        content_label = QLabel(html)
        content_label.setStyleSheet("background-color: transparent;")
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        msg_layout.addWidget(content_label)

        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_frame)
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )

    def update_api_status(self):
        self.update_status()

    def update_status(self):
        if self.ai_client and self.ai_client.api_key:
            self.status_label.setText("已连接")
            self.status_label.setStyleSheet(f"""
                background-color: {self.BG_CARD};
                color: {self.SUCCESS};
                border-radius: 13px;
                padding: 0 12px;
                font-size: 11px;
            """)
        else:
            self.status_label.setText("未连接")
            self.status_label.setStyleSheet(f"""
                background-color: {self.BG_CARD};
                color: {self.TEXT_TERTIARY};
                border-radius: 13px;
                padding: 0 12px;
                font-size: 11px;
            """)

    def send_message(self):
        if self.is_asking:
            return

        question = self.input_box.text().strip()
        if not question:
            return

        self.add_message(question, is_user=True)
        self.input_box.clear()

        self.is_asking = True
        self.send_btn.setEnabled(False)
        self.add_loading_message()

        mode = self.mode_combo.currentIndex()
        self._prepare_and_ask(question, mode)

    def _prepare_and_ask(self, question, mode):
        system_prompts = {
            0: "你是一位专业、友好的中国古代建筑研究专家助手。请用简洁专业的语言回答问题。",
            1: "你是一位中国古代建筑研究专家，擅长观察和分析古建筑图片。请仔细观察用户提供的图片并进行专业分析。",
            2: "你是《营造法式》和中国古代建筑典籍的专家，精通营造法式术语、建筑构件、色彩等级等知识。请结合专业知识回答问题。",
            3: "你是一位中国古代桥梁建筑史专家，熟悉各种古桥的建造技术、历史演变和艺术特色。请回答关于中国古代桥梁的问题。"
        }

        mode_system = system_prompts.get(mode, system_prompts[0])

        self.chat_history.append({"role": "user", "content": question})

        messages = [{"role": "system", "content": mode_system}]
        messages.extend(self.chat_history[1:])

        self.current_worker = AIWorker(self.ai_client, messages)
        self.current_worker.finished.connect(lambda r: self._on_answer_received(r, mode))
        self.current_worker.error.connect(self._on_error)
        self.current_worker.start()

    def _on_answer_received(self, answer, mode):
        self.remove_loading_message()

        self.chat_history.append({"role": "assistant", "content": answer})
        self.add_message(answer, is_user=False)

        self.is_asking = False
        self.send_btn.setEnabled(True)

    def _on_error(self, error):
        self.remove_loading_message()
        self.add_message(f"发生错误：{error}", is_user=False, is_error=True)
        self.is_asking = False
        self.send_btn.setEnabled(True)

    def add_message(self, text, is_user=False, is_error=False):
        if is_user:
            bubble_html = f"""
            <div style="background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self.PRIMARY}, stop:1 {self.PRIMARY_LIGHT});
                border-radius: 14px; padding: 12px 16px; margin: 4px 0;">
                <div style="color: white; font-size: 13px; line-height: 1.5;">{text}</div>
            </div>
            """
        elif is_error:
            bubble_html = f"""
            <div style="background-color: {self.BG_CARD};
                border: 1px solid {self.BORDER_NORMAL}; border-radius: 14px; padding: 12px 16px; margin: 4px 0;">
                <div style="color: #d04040; font-size: 13px; line-height: 1.5;">{text}</div>
            </div>
            """
        else:
            bubble_html = f"""
            <div style="background-color: {self.BG_CARD};
                border-radius: 14px; padding: 12px 16px; margin: 4px 0;">
                <div style="color: {self.TEXT_PRIMARY}; font-size: 13px; line-height: 1.6; white-space: pre-wrap;">{text}</div>
            </div>
            """

        self._add_html_message(bubble_html)

    def add_loading_message(self):
        loading_html = f"""
        <div style="background-color: {self.BG_CARD}; border-radius: 14px; padding: 14px 16px; margin: 4px 0;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="color: {self.TEXT_SECONDARY}; font-size: 13px;">AI 正在思考</div>
                <div style="display: flex; gap: 4px;">
                    <div style="width: 6px; height: 6px; background-color: {self.PRIMARY}; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both;"></div>
                    <div style="width: 6px; height: 6px; background-color: {self.PRIMARY_LIGHT}; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out 0.16s both;"></div>
                    <div style="width: 6px; height: 6px; background-color: {self.PRIMARY_BRIGHT}; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out 0.32s both;"></div>
                </div>
            </div>
            <style>
                @keyframes bounce {{
                    0%, 80%, 100% {{ transform: scale(0); }}
                    40% {{ transform: scale(1); }}
                }}
            </style>
        </div>
        """
        self.loading_html = loading_html
        self.loading_frame = QFrame()
        self.loading_frame.setStyleSheet("background-color: transparent;")
        loading_layout = QVBoxLayout(self.loading_frame)
        loading_layout.setContentsMargins(0, 0, 0, 0)

        loading_label = QLabel(loading_html)
        loading_label.setStyleSheet("background-color: transparent;")
        loading_layout.addWidget(loading_label)

        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.loading_frame)
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )

    def remove_loading_message(self):
        if hasattr(self, 'loading_frame'):
            self.loading_frame.deleteLater()

    def clear_chat(self):
        while self.chat_layout.count() > 1:
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.chat_history = [{"role": "system", "content": self.system_prompt}]

    def update_api_key(self, key):
        if hasattr(self.ai_client, 'set_api_key'):
            self.ai_client.set_api_key(key)
        self.update_status()

    def set_system_prompt(self, prompt):
        self.system_prompt = prompt
        self.chat_history = [{"role": "system", "content": prompt}]
