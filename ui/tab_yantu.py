from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

from core.yantu_engine import YantuEngine
from PyQt5.QtGui import QFont

class TabYantu(QWidget):
    def __init__(self, ai_client):
        super().__init__()
        self.ai_client = ai_client
        self.engine = YantuEngine(ai_client)
        self.current_filter = "全部"
        self.chart_canvas = None

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

        title = QLabel("🏛️  桥梁演化时间轴")
        title.setFont(self.get_font(16, "semibold"))
        title.setStyleSheet(f"color: {self.TEXT_PRIMARY}; padding: 4px 0;")
        layout.addWidget(title)

        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            background-color: {self.BG_SURFACE};
            border-radius: 12px;
            border: 1px solid {self.BORDER_SUBTLE};
            padding: 14px;
        """)
        filter_layout = QVBoxLayout(filter_frame)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(10)

        filter_title = QLabel("🔍 类型筛选")
        filter_title.setFont(self.get_font(12, "medium"))
        filter_title.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
        filter_layout.addWidget(filter_title)

        bridge_types = ["全部", "拱桥", "梁桥", "悬索桥", "廊桥", "启闭式"]
        self.type_buttons = []
        for btype in bridge_types:
            btn = QPushButton(btype)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(self.get_font(12))
            btn.clicked.connect(lambda checked, t=btype: self.filter_by_type(t))
            self.type_buttons.append(btn)
            filter_layout.addWidget(btn)

        self.type_buttons[0].setChecked(True)
        self.update_filter_buttons_style()

        layout.addWidget(filter_frame)

        timeline = self.engine.get_timeline()
        self.timeline_frames = []
        for item in timeline:
            item_frame = self.create_timeline_item(item)
            layout.addWidget(item_frame)
            self.timeline_frames.append((item_frame, item))

        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            background-color: {self.BG_SURFACE};
            border-radius: 12px;
            border: 1px solid {self.BORDER_SUBTLE};
            padding: 14px;
        """)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(10)

        stats_title = QLabel("📊 统计信息")
        stats_title.setFont(self.get_font(12, "medium"))
        stats_title.setStyleSheet(f"color: {self.ACCENT_GOLD};")
        stats_layout.addWidget(stats_title)

        self.stat_count = QLabel(f"显示 {len(timeline)}/{len(timeline)} 座桥梁")
        self.stat_count.setFont(self.get_font(13, "medium"))
        self.stat_count.setStyleSheet(f"color: {self.TEXT_PRIMARY};")
        stats_layout.addWidget(self.stat_count)

        stat_items = [
            ("历史桥梁", f"{len(timeline)} 座"),
            ("最早建造", "赵州桥·隋605年"),
            ("最新建造", "永济桥·民国1911年"),
        ]
        for label, value in stat_items:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFont(self.get_font(11))
            lbl.setStyleSheet(f"color: {self.TEXT_TERTIARY};")
            row.addWidget(lbl)
            row.addStretch()
            val = QLabel(value)
            val.setFont(self.get_font(11))
            val.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
            row.addWidget(val)
            stats_layout.addLayout(row)

        layout.addWidget(stats_frame)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def create_timeline_item(self, item):
        dynasty_colors = {
            '隋': '#c9a227', '宋': '#d4b84a', '金': '#3a7a9a',
            '清': '#2d8a4e', '唐': '#8a6ab8', '民国': '#a07040'
        }
        border_color = dynasty_colors.get(item['dynasty'], '#c9a227')

        item_frame = QFrame()
        item_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.BG_SURFACE};
                border-left: 3px solid {border_color};
                border-radius: 8px;
                padding: 12px;
                margin: 4px 0;
            }}
        """)

        item_layout = QVBoxLayout(item_frame)
        item_layout.setContentsMargins(14, 10, 10, 10)
        item_layout.setSpacing(6)

        name_label = QLabel(f"{item['dynasty']} · {item['name']}")
        name_label.setFont(self.get_font(13, "semibold"))
        name_label.setStyleSheet(f"color: {self.ACCENT_GOLD};")
        item_layout.addWidget(name_label)

        info_label = QLabel(f"{item['year']}年 | {item['type']}")
        info_label.setFont(self.get_font(11))
        info_label.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
        item_layout.addWidget(info_label)

        loc_label = QLabel(f"📍 {item['location']}")
        loc_label.setFont(self.get_font(11))
        loc_label.setStyleSheet(f"color: {self.TEXT_TERTIARY};")
        item_layout.addWidget(loc_label)

        desc_label = QLabel(item['desc'])
        desc_label.setFont(self.get_font(11))
        desc_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; line-height: 1.5;")
        desc_label.setWordWrap(True)
        item_layout.addWidget(desc_label)

        return item_frame

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

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title = QLabel("📈  演化图谱可视化")
        title.setFont(self.get_font(16, "semibold"))
        title.setStyleSheet(f"color: {self.TEXT_PRIMARY};")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.filter_status = QLabel("全部类型")
        self.filter_status.setFont(self.get_font(11, "medium"))
        self.filter_status.setFixedHeight(28)
        self.filter_status.setAlignment(Qt.AlignCenter)
        self.filter_status.setStyleSheet(f"""
            background-color: {self.BG_CARD};
            color: {self.PRIMARY_BRIGHT};
            border-radius: 14px;
            padding: 0 14px;
            font-size: 11px;
        """)
        header_layout.addWidget(self.filter_status)

        layout.addLayout(header_layout)

        self.chart_container = QFrame()
        self.chart_container.setStyleSheet(f"""
            background-color: {self.BG_CARD};
            border-radius: 12px;
            border: 1px solid {self.BORDER_SUBTLE};
        """)
        chart_layout = QVBoxLayout(self.chart_container)
        chart_layout.setContentsMargins(10, 10, 10, 10)

        self.chart_canvas = self.create_evolution_chart()
        chart_layout.addWidget(self.chart_canvas)
        layout.addWidget(self.chart_container, 1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        refresh_btn = QPushButton("🔄 刷新图表")
        refresh_btn.setFont(self.get_font(12, "medium"))
        refresh_btn.setFixedHeight(36)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.BG_CARD};
                color: {self.TEXT_SECONDARY};
                border: 1px solid {self.BORDER_NORMAL};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.BG_HOVER};
                border-color: {self.PRIMARY};
                color: {self.TEXT_PRIMARY};
            }}
        """)
        refresh_btn.clicked.connect(self.refresh_chart)
        btn_layout.addWidget(refresh_btn)
        layout.addLayout(btn_layout)

        return frame

    def create_evolution_chart(self, filter_type="全部"):
        fig = Figure(figsize=(7, 4.5), facecolor='#202020')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#202020')

        timeline = self.engine.get_timeline()

        if filter_type == "全部":
            filtered = timeline
        else:
            filter_map = {
                "拱桥": "拱",
                "梁桥": "梁",
                "悬索桥": "悬",
                "廊桥": "廊",
                "启闭式": "启闭"
            }
            filter_key = filter_map.get(filter_type, "")
            filtered = [b for b in timeline if filter_key in b.get('type', '')]

        if not filtered:
            ax.text(0.5, 0.5, '没有找到匹配的桥梁', ha='center', va='center',
                   color='#606060', fontsize=14)
            fig.tight_layout()
            canvas = FigureCanvas(fig)
            canvas.setStyleSheet("background-color: transparent;")
            return canvas

        years = [int(b['year']) for b in filtered]
        names = [b['name'] for b in filtered]
        significance = [b['significance'] for b in filtered]
        dynasties = [b['dynasty'] for b in filtered]

        colors_map = {
            '隋': '#c9a227', '宋': '#d4b84a', '金': '#3a7a9a',
            '清': '#2d8a4e', '唐': '#8a6ab8', '民国': '#a07040'
        }
        colors = [colors_map.get(d, '#606060') for d in dynasties]

        ax.scatter(years, significance, s=[s * 50 for s in significance],
                   c=colors, alpha=0.85, edgecolors='#404040', linewidths=1.5, zorder=3)

        sorted_data = sorted(zip(years, significance), key=lambda x: x[0])
        if len(sorted_data) > 1:
            ax.plot([x[0] for x in sorted_data], [x[1] for x in sorted_data],
                    color='#c9a227', alpha=0.3, linewidth=2, linestyle='--', zorder=2)

        for year, name, sig in zip(years, names, significance):
            ax.annotate(name, (year, sig), textcoords="offset points",
                        xytext=(0, 12), ha='center',
                        fontsize=9, color='#a0a0a0',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#262626',
                                  edgecolor='#404040', alpha=0.9))

        title_suffix = f" - {filter_type}" if filter_type != "全部" else ""
        ax.set_xlabel('年代', color='#606060', fontsize=11)
        ax.set_ylabel('历史意义', color='#606060', fontsize=11)
        ax.set_title(f'中国古代桥梁演化轨迹{title_suffix}', color='#c9a227',
                    fontsize=13, fontweight='bold', pad=12)

        ax.tick_params(colors='#606060', labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#333333')
        ax.spines['left'].set_color('#333333')
        ax.grid(True, color='#2a2a2a', alpha=0.5)

        legend_elements = [mpatches.Patch(color=v, label=k)
                         for k, v in colors_map.items() if k in dynasties]
        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper left',
                     facecolor='#202020', edgecolor='#333333',
                     labelcolor='#a0a0a0', fontsize=9,
                     framealpha=0.9)

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: transparent;")
        return canvas

    def update_filter_buttons_style(self):
        for btn in self.type_buttons:
            if btn.isChecked():
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {self.PRIMARY_LIGHT},
                            stop:1 {self.PRIMARY});
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 10px 14px;
                        font-size: 12px;
                        font-weight: 500;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.BG_CARD};
                        color: {self.TEXT_SECONDARY};
                        border: 1px solid {self.BORDER_SUBTLE};
                        border-radius: 8px;
                        padding: 10px 14px;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.BG_HOVER};
                        color: {self.TEXT_PRIMARY};
                        border-color: {self.PRIMARY};
                    }}
                """)

    def refresh_chart(self):
        if self.chart_canvas:
            self.chart_canvas.deleteLater()
        self.chart_canvas = self.create_evolution_chart(self.current_filter)
        self.chart_container.layout().addWidget(self.chart_canvas)

    def filter_by_type(self, bridge_type):
        self.current_filter = bridge_type

        self.update_filter_buttons_style()

        self.filter_status.setText(bridge_type)

        self.update_timeline_display(bridge_type)

        self.refresh_chart()

    def update_timeline_display(self, filter_type):
        timeline = self.engine.get_timeline()

        if filter_type == "全部":
            filtered = timeline
        else:
            filter_map = {
                "拱桥": "拱",
                "梁桥": "梁",
                "悬索桥": "悬",
                "廊桥": "廊",
                "启闭式": "启闭"
            }
            filter_key = filter_map.get(filter_type, "")
            filtered = [b for b in timeline if filter_key in b.get('type', '')]

        total = len(timeline)
        shown = len(filtered)
        self.stat_count.setText(f"显示 {shown}/{total} 座桥梁")

        for frame, item in self.timeline_frames:
            if filter_type == "全部":
                frame.setVisible(True)
            else:
                filter_map = {
                    "拱桥": "拱",
                    "梁桥": "梁",
                    "悬索桥": "悬",
                    "廊桥": "廊",
                    "启闭式": "启闭"
                }
                filter_key = filter_map.get(filter_type, "")
                is_visible = filter_key in item.get('type', '')
                frame.setVisible(is_visible)

    def update_api_key(self, key):
        self.engine.set_api_key(key)
