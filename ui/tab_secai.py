from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QScrollArea, QFrame, QFileDialog,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QFont

from core.secai_engine import SecaiEngine, PALACE_COLORS

class SecaiWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, engine, image_path):
        super().__init__()
        self.engine = engine
        self.image_path = image_path

    def run(self):
        try:
            result = self.engine.analyze_colors(self.image_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class TabSecai(QWidget):
    def __init__(self, ai_client):
        super().__init__()
        self.ai_client = ai_client
        self.engine = SecaiEngine(ai_client)
        self.current_image = None
        self.analyzed_colors = []

        self.BG_PRIMARY = "#141414"
        self.BG_SURFACE = "#1a1a1a"
        self.BG_CARD = "#202020"
        self.BG_HOVER = "#2d2d2d"
        self.PRIMARY = "#0d5c5c"
        self.PRIMARY_LIGHT = "#108080"
        self.PRIMARY_BRIGHT = "#14a0a0"
        self.ACCENT_GOLD = "#c9a227"
        self.ACCENT_GOLD_LIGHT = "#d4b84a"
        self.TEXT_PRIMARY = "#f0f0f0"
        self.TEXT_SECONDARY = "#a0a0a0"
        self.TEXT_TERTIARY = "#606060"
        self.BORDER_SUBTLE = "#2a2a2a"
        self.BORDER_NORMAL = "#333333"
        self.SUCCESS = "#2d8a4e"
        self.ERROR = "#a03030"

        self.init_ui()

    def get_font(self, size, weight="normal"):
        weights = {"thin": 100, "light": 300, "normal": 400, "medium": 500, "semibold": 600, "bold": 700}
        return QFont("Microsoft YaHei", size, weights.get(weight, 400))

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        left_panel = self.create_left_panel()
        center_panel = self.create_center_panel()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStyleSheet(f"""
            QSplitter {{
                background-color: {self.BG_PRIMARY};
            }}
            QSplitter::handle {{
                background-color: {self.BORDER_SUBTLE};
                width: 1px;
            }}
        """)

        main_layout.addWidget(splitter)

    def create_left_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {self.BG_PRIMARY};")

        content = QFrame()
        content.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 12, 16)
        layout.setSpacing(16)

        title = QLabel("🏮  故宫五大代表色彩")
        title.setFont(self.get_font(16, "semibold"))
        title.setStyleSheet(f"color: {self.TEXT_PRIMARY}; padding: 4px 0;")
        layout.addWidget(title)

        self.colors_container = QFrame()
        self.colors_container.setStyleSheet(f"""
            background-color: {self.BG_SURFACE};
            border-radius: 14px;
            border: 1px solid {self.BORDER_SUBTLE};
            padding: 14px;
        """)
        self.colors_layout = QVBoxLayout(self.colors_container)
        self.colors_layout.setContentsMargins(8, 8, 8, 8)
        self.colors_layout.setSpacing(10)

        self.init_palace_colors()

        layout.addWidget(self.colors_container)

        self.match_label = QLabel("📋 上传建筑图片以提取色彩")
        self.match_label.setFont(self.get_font(11))
        self.match_label.setWordWrap(True)
        self.match_label.setStyleSheet(f"""
            color: {self.TEXT_TERTIARY};
            background-color: {self.BG_SURFACE};
            border-radius: 8px;
            padding: 12px;
            font-size: 11px;
        """)
        layout.addWidget(self.match_label)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def init_palace_colors(self):
        while self.colors_layout.count():
            child = self.colors_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for name, info in PALACE_COLORS.items():
            color_frame = self.create_color_item(
                name,
                info['hex'],
                info['desc'],
                info['usage'],
                info['cultural']
            )
            self.colors_layout.addWidget(color_frame)

    def create_color_item(self, name, hex_color, desc, usage, cultural, is_extracted=False):
        color_frame = QFrame()
        border_color = self.PRIMARY if is_extracted else self.BORDER_SUBTLE

        color_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.BG_CARD};
                border: 1px solid {border_color};
                border-radius: 10px;
                padding: 12px;
                margin: 3px 0;
            }}
        """)

        layout = QVBoxLayout(color_frame)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        color_block = QFrame()
        color_block.setFixedSize(70, 42)
        color_block.setStyleSheet(f"""
            QFrame {{
                background-color: {hex_color};
                border-radius: 6px;
                border: 1px solid rgba(255,255,255,0.1);
            }}
        """)
        header_layout.addWidget(color_block)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        name_label = QLabel(name)
        name_label.setFont(self.get_font(14, "semibold"))
        name_label.setStyleSheet(f"color: {self.TEXT_PRIMARY};")
        info_layout.addWidget(name_label)

        hex_label = QLabel(hex_color)
        hex_label.setFont(self.get_font(12))
        hex_label.setStyleSheet(f"color: {self.TEXT_TERTIARY};")
        info_layout.addWidget(hex_label)

        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        desc_label = QLabel(desc)
        desc_label.setFont(self.get_font(12))
        desc_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; line-height: 1.4;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        if usage:
            usage_label = QLabel(f"用途：{usage}")
            usage_label.setFont(self.get_font(11))
            usage_label.setStyleSheet(f"color: {self.ACCENT_GOLD}; font-size: 11px;")
            layout.addWidget(usage_label)

        if cultural:
            cultural_label = QLabel(f"文化：{cultural}")
            cultural_label.setFont(self.get_font(11))
            cultural_label.setStyleSheet(f"color: {self.TEXT_TERTIARY}; font-size: 11px;")
            cultural_label.setWordWrap(True)
            layout.addWidget(cultural_label)

        return color_frame

    def create_center_panel(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {self.BG_SURFACE};
            border-radius: 14px;
            border: 1px solid {self.BORDER_SUBTLE};
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        title = QLabel("🎨  建筑色彩分析")
        title.setFont(self.get_font(16, "semibold"))
        title.setStyleSheet(f"color: {self.TEXT_PRIMARY};")
        layout.addWidget(title)

        upload_btn = QPushButton("📁  上传建筑图片")
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.setFont(self.get_font(14, "medium"))
        upload_btn.setFixedHeight(46)
        upload_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.PRIMARY_LIGHT},
                    stop:1 {self.PRIMARY});
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0 28px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.PRIMARY_BRIGHT},
                    stop:1 {self.PRIMARY_LIGHT});
            }}
        """)
        upload_btn.clicked.connect(self.upload_image)
        layout.addWidget(upload_btn)

        result_frame = QFrame()
        result_frame.setStyleSheet(f"""
            background-color: {self.BG_CARD};
            border-radius: 12px;
            border: 1px solid {self.BORDER_SUBTLE};
            padding: 16px;
        """)
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(14)

        result_title = QLabel("📊 分析结果")
        result_title.setFont(self.get_font(13, "semibold"))
        result_title.setStyleSheet(f"color: {self.ACCENT_GOLD};")
        result_layout.addWidget(result_title)

        self.analysis_result = QLabel("请上传图片开始分析")
        self.analysis_result.setFont(self.get_font(12))
        self.analysis_result.setWordWrap(True)
        self.analysis_result.setStyleSheet(f"color: {self.TEXT_TERTIARY}; font-size: 12px;")
        result_layout.addWidget(self.analysis_result)

        preview_label = QLabel("提取色彩")
        preview_label.setFont(self.get_font(11, "medium"))
        preview_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 11px;")
        result_layout.addWidget(preview_label)

        self.color_preview_frame = QFrame()
        self.color_preview_frame.setStyleSheet("background-color: transparent;")
        self.color_preview_layout = QHBoxLayout(self.color_preview_frame)
        self.color_preview_layout.setContentsMargins(0, 6, 0, 6)
        self.color_preview_layout.addStretch()
        result_layout.addWidget(self.color_preview_frame)

        layout.addWidget(result_frame)

        self.status_label = QLabel("")
        self.status_label.setFont(self.get_font(12))
        self.status_label.setStyleSheet(f"color: {self.SUCCESS}; font-size: 12px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        layout.addStretch()

        return frame

    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择建筑图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.current_image = path
            self.analyze_current_image()

    def analyze_current_image(self):
        if not self.current_image:
            return

        self.status_label.setText("正在分析色彩...")
        self.status_label.setVisible(True)
        self.analysis_result.setText("正在提取图片中的主要色彩，请稍候...")

        while self.color_preview_layout.count():
            child = self.color_preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.worker = SecaiWorker(self.engine, self.current_image)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_analysis_finished(self, result):
        self.status_label.setVisible(False)

        if "error" in result:
            self.analysis_result.setText(f"分析失败：{result['error']}")
            return

        colors = result.get("extracted_colors", [])
        matched = result.get("matched_palace_colors", [])

        if not colors:
            self.analysis_result.setText("未能提取到图片色彩，请尝试其他图片")
            return

        while self.color_preview_layout.count():
            child = self.color_preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for c in colors[:6]:
            color_widget = QFrame()
            color_widget.setFixedSize(48, 48)
            color_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: {c['hex']};
                    border-radius: 8px;
                    border: 1px solid rgba(255,255,255,0.1);
                }}
            """)
            color_widget.setToolTip(f"{c['hex']} - {c.get('name', '未知')}")
            self.color_preview_layout.addWidget(color_widget)

        self.color_preview_layout.addStretch()

        self.update_colors_display(colors, matched)

        lines = [f"成功提取 {len(colors)} 种主要色彩：\n"]
        matched_count = 0

        for i, c in enumerate(colors, 1):
            name = c.get('name', '未知')
            if name and name != '未匹配色彩':
                matched_count += 1
                lines.append(f"{i}. {c['hex']} → 【{name}】匹配")
            else:
                lines.append(f"{i}. {c['hex']} → 未匹配宫殿色彩")

        if matched_count > 0:
            lines.append(f"\n共匹配 {matched_count}/{len(colors)} 种宫殿色彩")
            self.match_label.setText(f"✓ 成功匹配 {matched_count} 种宫殿代表色！")
            self.match_label.setStyleSheet(f"""
                color: {self.SUCCESS};
                background-color: {self.BG_SURFACE};
                border-radius: 8px;
                padding: 12px;
                font-size: 11px;
            """)
        else:
            self.match_label.setText("⚠ 未匹配到宫殿色彩，建议上传更清晰的中国古建筑图片")
            self.match_label.setStyleSheet(f"""
                color: {self.ERROR};
                background-color: {self.BG_SURFACE};
                border-radius: 8px;
                padding: 12px;
                font-size: 11px;
            """)

        self.analysis_result.setText("\n".join(lines))

    def update_colors_display(self, extracted_colors, matched_palace_colors):
        while self.colors_layout.count():
            child = self.colors_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        matched_map = {}
        for mc in matched_palace_colors:
            matched_map[mc['hex'].lower()] = mc['palace_info']

        for c in extracted_colors[:6]:
            hex_color = c['hex']
            name = c.get('name', '提取色彩')
            desc = c.get('description', '从图片中提取的主要色彩')

            if hex_color.lower() in matched_map:
                palace_info = matched_map[hex_color.lower()]
                desc = palace_info.get('desc', desc)
                name = palace_info.get('name', name)
            else:
                name = name if name != '未匹配色彩' else '提取色彩'

            color_frame = self.create_color_item(
                name,
                hex_color,
                desc,
                "",
                "",
                is_extracted=True
            )
            self.colors_layout.addWidget(color_frame)

        if len(extracted_colors) < len(PALACE_COLORS):
            separator = QLabel("—— 其他宫殿代表色 ——")
            separator.setFont(self.get_font(11))
            separator.setAlignment(Qt.AlignCenter)
            separator.setStyleSheet(f"color: {self.TEXT_TERTIARY}; font-size: 11px; padding: 8px;")
            self.colors_layout.addWidget(separator)

            for name, info in PALACE_COLORS.items():
                hex_c = info['hex'].lower()
                if hex_c not in [c['hex'].lower() for c in extracted_colors[:6]]:
                    color_frame = self.create_color_item(
                        name,
                        info['hex'],
                        info['desc'],
                        info['usage'],
                        info['cultural'],
                        is_extracted=False
                    )
                    self.colors_layout.addWidget(color_frame)

    def on_analysis_error(self, error):
        self.status_label.setVisible(False)
        self.analysis_result.setText(f"分析失败：{error}")

    def update_api_key(self, key):
        self.engine.set_api_key(key)
