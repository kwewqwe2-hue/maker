# -*- coding: utf-8 -*-
import os
import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QStackedWidget,
                             QMessageBox, QTextEdit, QLineEdit, QScrollArea,
                             QGroupBox, QFrame, QSizePolicy, QTabWidget, QDialog,
                             QFormLayout, QComboBox, QSplitter)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPainter, QLinearGradient, QPen, QBrush, QPainterPath

from ui.tab_wenku import TabWenku
from ui.tab_yantu import TabYantu
from ui.tab_secai import TabSecai
from ui.unified_ai_panel import UnifiedAIPanel
from core.ai_client import AIClient, test_api_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PremiumColors:
    BG_DEEPEST = "#080808"
    BG_DEEP = "#0d0d0d"
    BG_PRIMARY = "#141414"
    BG_SURFACE = "#1a1a1a"
    BG_CARD = "#202020"
    BG_ELEVATED = "#262626"
    BG_HOVER = "#2d2d2d"
    PRIMARY_DARK = "#0a4a4a"
    PRIMARY = "#0d5c5c"
    PRIMARY_LIGHT = "#108080"
    PRIMARY_BRIGHT = "#14a0a0"
    ACCENT_GOLD = "#c9a227"
    ACCENT_GOLD_LIGHT = "#d4b84a"
    ACCENT_GOLD_DIM = "#8a7020"
    TEXT_PRIMARY = "#f0f0f0"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_TERTIARY = "#606060"
    TEXT_DISABLED = "#404040"
    SUCCESS = "#2d8a4e"
    WARNING = "#b8860b"
    ERROR = "#a03030"
    INFO = "#3a7a9a"
    BORDER_SUBTLE = "#2a2a2a"
    BORDER_NORMAL = "#333333"
    BORDER_STRONG = "#404040"
    DIVIDER = "#252525"

def get_font(size, weight="normal"):
    weights = {"thin": 100, "light": 300, "normal": 400, "medium": 500, "semibold": 600, "bold": 700}
    return QFont("Microsoft YaHei", size, weights.get(weight, 400))

def create_architecture_icon(size=44, colors=None):
    if colors is None:
        colors = {
            "PRIMARY": "#0d5c5c",
            "PRIMARY_BRIGHT": "#14a0a0",
            "PRIMARY_LIGHT": "#108080",
            "ACCENT_GOLD": "#c9a227",
            "TEXT_PRIMARY": "#f0f0f0",
            "BORDER_NORMAL": "#404040",
        }

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    w, h = size, size
    cx, cy = w // 2, h // 2

    painter.setPen(Qt.NoPen)
    gradient = QLinearGradient(0, 0, w, h)
    gradient.setColorAt(0, QColor(colors["PRIMARY"]))
    gradient.setColorAt(1, QColor(colors["PRIMARY_BRIGHT"]))
    painter.setBrush(QBrush(gradient))
    painter.drawEllipse(2, 2, w - 4, h - 4)

    gold = QColor(colors["ACCENT_GOLD"])
    light = QColor(colors["PRIMARY_LIGHT"])
    white = QColor(colors["TEXT_PRIMARY"])
    gray = QColor(colors["BORDER_NORMAL"])

    roof_path = QPainterPath()
    roof_path.moveTo(cx, cy - 10)
    roof_path.lineTo(cx - 14, cy - 2)
    roof_path.lineTo(cx - 16, cy)
    roof_path.lineTo(cx + 16, cy)
    roof_path.lineTo(cx + 14, cy - 2)
    roof_path.closeSubpath()

    painter.setPen(QPen(gold, 1.2))
    painter.setBrush(QBrush(light))
    painter.drawPath(roof_path)

    painter.setPen(QPen(gold, 1.5))
    painter.drawLine(cx, cy - 10, cx - 14, cy - 2)
    painter.drawLine(cx, cy - 10, cx + 14, cy - 2)

    painter.setBrush(QBrush(gold))
    painter.drawEllipse(cx - 2, cy - 11, 4, 3)
    painter.drawEllipse(cx + 2, cy - 11, 4, 3)

    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(white))
    painter.drawRect(cx - 9, cy + 1, 3, 7)
    painter.drawRect(cx + 6, cy + 1, 3, 7)

    painter.setPen(QPen(gold, 0.8))
    painter.drawLine(cx - 9, cy + 2, cx + 9, cy + 2)

    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(gray))
    painter.drawRect(cx - 11, cy + 8, 22, 2)

    painter.end()
    return pixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ai_client = AIClient()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("营造智绘 - 中国古代建筑遗产智能认知系统")
        self.setGeometry(100, 100, 1500, 950)
        self.setMinimumSize(1200, 800)

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {PremiumColors.BG_PRIMARY};
            }}
            QLabel {{
                color: {PremiumColors.TEXT_PRIMARY};
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            }}
            QPushButton {{
                background-color: {PremiumColors.PRIMARY};
                color: {PremiumColors.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {PremiumColors.PRIMARY_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {PremiumColors.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {PremiumColors.BG_HOVER};
                color: {PremiumColors.TEXT_DISABLED};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QLineEdit, QTextEdit {{
                background-color: {PremiumColors.BG_CARD};
                color: {PremiumColors.TEXT_PRIMARY};
                border: 1px solid {PremiumColors.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {PremiumColors.PRIMARY_BRIGHT};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {PremiumColors.BG_DEEP};
                width: 8px;
                margin: 4px 0;
            }}
            QScrollBar::handle:vertical {{
                background: {PremiumColors.BORDER_NORMAL};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {PremiumColors.BORDER_STRONG};
            }}
            QScrollBar:add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {PremiumColors.BG_DEEP};
                height: 8px;
                margin: 0 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {PremiumColors.BORDER_NORMAL};
                border-radius: 4px;
                min-width: 30px;
            }}
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.create_header()
        main_layout.addWidget(self.header_widget)

        self.create_main_content()
        main_layout.addWidget(self.content_splitter, 1)

    def create_header(self):
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(72)
        self.header_widget.setStyleSheet(f"""
            background-color: {PremiumColors.BG_SURFACE};
            border-bottom: 1px solid {PremiumColors.BORDER_SUBTLE};
        """)

        layout = QHBoxLayout(self.header_widget)
        layout.setContentsMargins(28, 0, 28, 0)

        logo_container = QHBoxLayout()
        logo_container.setSpacing(14)

        icon_label = QLabel()
        icon_label.setFixedSize(44, 44)

        icon_pixmap = create_architecture_icon(44, {
            "PRIMARY": "#0d5c5c",
            "PRIMARY_BRIGHT": "#14a0a0",
            "PRIMARY_LIGHT": "#108080",
            "ACCENT_GOLD": "#c9a227",
            "TEXT_PRIMARY": "#f0f0f0",
            "BORDER_NORMAL": "#404040",
        })

        icon_label.setPixmap(icon_pixmap)
        logo_container.addWidget(icon_label)

        title_container = QVBoxLayout()
        title_container.setSpacing(2)

        title = QLabel("营造智绘")
        title.setFont(get_font(22, "semibold"))
        title.setStyleSheet(f"color: {PremiumColors.TEXT_PRIMARY};")
        title_container.addWidget(title)

        subtitle = QLabel("中国古代建筑遗产智能认知系统")
        subtitle.setFont(get_font(11, "normal"))
        subtitle.setStyleSheet(f"color: {PremiumColors.TEXT_TERTIARY};")
        title_container.addWidget(subtitle)

        logo_container.addLayout(title_container)
        layout.addLayout(logo_container)

        divider = QFrame()
        divider.setFixedSize(1, 36)
        divider.setStyleSheet(f"background-color: {PremiumColors.BORDER_SUBTLE};")
        layout.addWidget(divider)

        layout.addStretch()

        status_container = QHBoxLayout()
        status_container.setSpacing(12)

        self.api_status_label = QLabel()
        self.api_status_label.setFixedHeight(32)
        self.api_status_label.setAlignment(Qt.AlignCenter)
        self.api_status_label.setFont(get_font(12, "medium"))
        self.api_status_label.setStyleSheet(f"""
            background-color: {PremiumColors.BG_CARD};
            color: {PremiumColors.TEXT_SECONDARY};
            border-radius: 6px;
            padding: 0 14px;
        """)
        self.api_status_label.setText("  AI 未连接  ")
        status_container.addWidget(self.api_status_label)

        settings_btn = QPushButton("设置")
        settings_btn.setFixedSize(90, 36)
        settings_btn.setFont(get_font(13, "medium"))
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PremiumColors.BG_CARD};
                color: {PremiumColors.TEXT_SECONDARY};
                border: 1px solid {PremiumColors.BORDER_NORMAL};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {PremiumColors.BG_HOVER};
                border-color: {PremiumColors.BORDER_STRONG};
                color: {PremiumColors.TEXT_PRIMARY};
            }}
        """)
        settings_btn.clicked.connect(self.show_settings)
        status_container.addWidget(settings_btn)

        layout.addLayout(status_container)

    def create_main_content(self):
        self.content_splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 16, 20, 16)
        left_layout.setSpacing(16)

        nav_widget = QWidget()
        nav_widget.setFixedHeight(52)
        nav_widget.setStyleSheet(f"""
            background-color: {PremiumColors.BG_SURFACE};
            border-radius: 12px;
            border: 1px solid {PremiumColors.BORDER_SUBTLE};
        """)
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(6, 6, 6, 6)
        nav_layout.setSpacing(4)

        self.nav_buttons = []
        nav_items = [
            ("📜  知识典籍", self.show_wenku),
            ("🏛️  桥梁演化", self.show_yantu),
            ("🎨  宫殿色彩", self.show_secai),
        ]

        for i, (name, callback) in enumerate(nav_items):
            btn = QPushButton(name)
            btn.setFixedHeight(40)
            btn.setFont(get_font(13, "medium"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)

        nav_layout.addStretch()

        if self.nav_buttons:
            self.update_nav_style(0)

        left_layout.addWidget(nav_widget)

        self.tab_wenku = TabWenku(self.ai_client)
        self.tab_yantu = TabYantu(self.ai_client)
        self.tab_secai = TabSecai(self.ai_client)

        self.content_widget = QStackedWidget()
        self.content_widget.addWidget(self.tab_wenku)
        self.content_widget.addWidget(self.tab_yantu)
        self.content_widget.addWidget(self.tab_secai)
        self.content_widget.setCurrentIndex(0)

        left_layout.addWidget(self.content_widget, 1)

        self.ai_panel = UnifiedAIPanel(
            self.ai_client,
            title="智能助手",
            system_prompt="你是一位专业、友好的中国古代建筑研究专家助手。精通《营造法式》、古建筑构造、桥梁历史、建筑色彩等知识。请用简洁专业的语言回答用户问题。"
        )
        self.ai_panel.setFixedWidth(400)

        self.content_splitter.addWidget(left_widget)
        self.content_splitter.addWidget(self.ai_panel)
        self.content_splitter.setStretchFactor(0, 3)
        self.content_splitter.setStretchFactor(1, 1)
        self.content_splitter.setCollapsible(0, False)
        self.content_splitter.setCollapsible(1, False)
        self.content_splitter.setStyleSheet(f"""
            QSplitter {{
                background-color: {PremiumColors.BG_PRIMARY};
            }}
            QSplitter::handle {{
                background-color: {PremiumColors.BORDER_SUBTLE};
                width: 1px;
            }}
        """)

    def update_nav_style(self, active_index):
        for i, btn in enumerate(self.nav_buttons):
            if i == active_index:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {PremiumColors.PRIMARY_LIGHT},
                            stop:1 {PremiumColors.PRIMARY});
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 0 20px;
                        font-size: 13px;
                        font-weight: 500;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {PremiumColors.TEXT_SECONDARY};
                        border: none;
                        border-radius: 8px;
                        padding: 0 20px;
                        font-size: 13px;
                    }}
                    QPushButton:hover {{
                        background-color: {PremiumColors.BG_HOVER};
                        color: {PremiumColors.TEXT_PRIMARY};
                    }}
                """)

    def show_wenku(self):
        self.content_widget.setCurrentIndex(0)
        self.update_nav_style(0)

    def show_yantu(self):
        self.content_widget.setCurrentIndex(1)
        self.update_nav_style(1)

    def show_secai(self):
        self.content_widget.setCurrentIndex(2)
        self.update_nav_style(2)

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("API 设置")
        dialog.setFixedSize(520, 380)
        dialog.setStyleSheet(f"QDialog {{ background-color: {PremiumColors.BG_PRIMARY}; }}")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(28, 24, 28, 24)

        title = QLabel("API 配置")
        title.setFont(get_font(20, "semibold"))
        title.setStyleSheet(f"color: {PremiumColors.TEXT_PRIMARY};")
        layout.addWidget(title)

        info_frame = QFrame()
        info_frame.setStyleSheet(f"background-color: {PremiumColors.BG_CARD}; border-radius: 10px; border: 1px solid {PremiumColors.BORDER_SUBTLE}; padding: 16px;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(12)

        info_title = QLabel("免费 API 申请步骤")
        info_title.setFont(get_font(14, "medium"))
        info_title.setStyleSheet(f"color: {PremiumColors.ACCENT_GOLD};")
        info_layout.addWidget(info_title)

        steps = [
            "1. 访问 https://siliconflow.cn 注册账号",
            "2. 登录后在控制台找到「API密钥」",
            "3. 点击「新建密钥」并复制",
            "4. 将密钥粘贴到下方并保存"
        ]
        for step in steps:
            step_label = QLabel(step)
            step_label.setFont(get_font(12))
            step_label.setStyleSheet(f"color: {PremiumColors.TEXT_SECONDARY};")
            info_layout.addWidget(step_label)

        layout.addWidget(info_frame)

        key_label = QLabel("API 密钥")
        key_label.setFont(get_font(13, "medium"))
        key_label.setStyleSheet(f"color: {PremiumColors.TEXT_SECONDARY};")
        layout.addWidget(key_label)

        api_key_input = QLineEdit()
        api_key_input.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxx")
        api_key_input.setFont(get_font(13))
        if self.ai_client.api_key:
            api_key_input.setText(self.ai_client.api_key)
        layout.addWidget(api_key_input)

        model_label = QLabel("使用模型")
        model_label.setFont(get_font(13, "medium"))
        model_label.setStyleSheet(f"color: {PremiumColors.TEXT_SECONDARY};")
        layout.addWidget(model_label)

        model_combo = QComboBox()
        model_combo.addItems([
            "Qwen/Qwen2.5-7B-Instruct (推荐 · 通用问答)",
            "Qwen/Qwen2-VL-7B-Instruct (多模态 · 能看图)",
            "THUDM/glm-4v-9b (多模态 · 智谱)",
        ])
        model_combo.setFixedHeight(44)
        model_combo.setFont(get_font(13))
        model_combo.setStyleSheet(f"QComboBox {{ background-color: {PremiumColors.BG_CARD}; color: {PremiumColors.TEXT_PRIMARY}; border: 1px solid {PremiumColors.BORDER_SUBTLE}; border-radius: 8px; padding: 0 16px; }}")
        layout.addWidget(model_combo)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        test_btn = QPushButton("测试连接")
        test_btn.setFixedHeight(44)
        test_btn.setFont(get_font(14, "medium"))
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PremiumColors.BG_CARD};
                color: {PremiumColors.TEXT_PRIMARY};
                border: 1px solid {PremiumColors.BORDER_NORMAL};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                border-color: {PremiumColors.ACCENT_GOLD};
            }}
        """)

        save_btn = QPushButton("保存配置")
        save_btn.setFixedHeight(44)
        save_btn.setFont(get_font(14, "medium"))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {PremiumColors.PRIMARY_LIGHT},
                    stop:1 {PremiumColors.PRIMARY});
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {PremiumColors.PRIMARY_BRIGHT},
                    stop:1 {PremiumColors.PRIMARY_LIGHT});
            }}
        """)

        def do_test():
            key = api_key_input.text().strip()
            if not key:
                QMessageBox.warning(dialog, "提示", "请先输入 API 密钥")
                return
            test_btn.setText("测试中...")
            test_btn.setEnabled(False)
            ok, msg = test_api_key(key)
            test_btn.setText("测试连接")
            test_btn.setEnabled(True)
            if ok:
                QMessageBox.information(dialog, "成功", msg)
            else:
                QMessageBox.warning(dialog, "失败", msg)

        def do_save():
            key = api_key_input.text().strip()
            self.ai_client.set_api_key(key)
            if key:
                self.api_status_label.setText("  ● AI 已连接  ")
                self.api_status_label.setStyleSheet(f"""
                    background-color: {PremiumColors.BG_CARD};
                    color: {PremiumColors.SUCCESS};
                    border-radius: 6px;
                    padding: 0 14px;
                    font-size: 12px;
                """)
            else:
                self.api_status_label.setText("  AI 未连接  ")
                self.api_status_label.setStyleSheet(f"""
                    background-color: {PremiumColors.BG_CARD};
                    color: {PremiumColors.TEXT_SECONDARY};
                    border-radius: 6px;
                    padding: 0 14px;
                    font-size: 12px;
                """)
            self.tab_wenku.update_api_key(key)
            self.tab_yantu.update_api_key(key)
            self.tab_secai.update_api_key(key)
            self.ai_panel.update_api_key(key)
            dialog.accept()

        test_btn.clicked.connect(do_test)
        save_btn.clicked.connect(do_save)

        btn_layout.addWidget(test_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

        dialog.exec_()
