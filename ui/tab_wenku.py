from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame,
    QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QFont

from data.wenku_knowledge import (
    get_term, get_architecture, get_bridge,
    search_all, get_all_terms, get_all_architectures, get_all_bridges
)

class TabWenku(QWidget):
    def __init__(self, ai_client):
        super().__init__()
        self.ai_client = ai_client
        self.current_item = None
        self.search_results = []

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

        self.left_panel = self.create_left_panel()
        main_layout.addWidget(self.left_panel, 1)

        self.right_panel = self.create_right_panel()
        main_layout.addWidget(self.right_panel, 2)

    def create_left_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            border: none;
            background-color: {self.BG_PRIMARY};
        """)

        container = QFrame()
        container.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 12, 16)
        layout.setSpacing(16)

        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
            background-color: {self.BG_SURFACE};
            border-radius: 12px;
            border: 1px solid {self.BORDER_SUBTLE};
            padding: 14px;
        """)
        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)

        search_label = QLabel("🔍 搜索知识库")
        search_label.setFont(self.get_font(12, "medium"))
        search_label.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索词条...")
        self.search_input.setFont(self.get_font(13))
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.BG_CARD};
                color: {self.TEXT_PRIMARY};
                border: 1px solid {self.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {self.PRIMARY_BRIGHT};
            }}
            QLineEdit::placeholder {{
                color: {self.TEXT_TERTIARY};
            }}
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)

        self.search_result_label = QLabel("")
        self.search_result_label.setFont(self.get_font(11))
        self.search_result_label.setStyleSheet(f"color: {self.TEXT_TERTIARY};")
        self.search_result_label.setVisible(False)
        search_layout.addWidget(self.search_result_label)

        layout.addWidget(search_frame)

        self.search_results_list = QListWidget()
        self.search_results_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.BG_SURFACE};
                border: 1px solid {self.BORDER_SUBTLE};
                border-radius: 10px;
                color: {self.TEXT_PRIMARY};
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-radius: 6px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: {self.PRIMARY};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {self.BG_HOVER};
            }}
        """)
        self.search_results_list.itemClicked.connect(self.on_search_item_clicked)
        self.search_results_list.setVisible(False)
        layout.addWidget(self.search_results_list)

        term_frame = self.create_category_frame("📜 核心术语", self.create_term_items)
        layout.addWidget(term_frame)

        arch_frame = self.create_category_frame("🏛️ 建筑类型", self.create_architecture_items)
        layout.addWidget(arch_frame)

        bridge_frame = self.create_category_frame("🌉 著名古桥", self.create_bridge_items)
        layout.addWidget(bridge_frame)

        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def create_category_frame(self, title, create_func):
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {self.BG_SURFACE};
            border-radius: 14px;
            border: 1px solid {self.BORDER_SUBTLE};
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setFont(self.get_font(14, "semibold"))
        title_label.setStyleSheet(f"color: {self.ACCENT_GOLD};")
        layout.addWidget(title_label)

        items = create_func()
        for item_name, item_data in items:
            btn = QPushButton(item_name)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(self.get_font(12))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.BG_CARD};
                    color: {self.TEXT_SECONDARY};
                    border: 1px solid {self.BORDER_SUBTLE};
                    border-radius: 8px;
                    padding: 10px 14px;
                    text-align: left;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {self.BG_HOVER};
                    color: {self.TEXT_PRIMARY};
                    border-color: {self.PRIMARY};
                }}
            """)
            btn.clicked.connect(lambda checked, n=item_name, d=item_data: self.show_term_detail(n, d))
            layout.addWidget(btn)

        return frame

    def create_term_items(self):
        return [
            ("斗栱", ("term", "斗栱")),
            ("材分制", ("term", "材分制")),
            ("营造法式", ("term", "营造法式")),
            ("屋顶形制", ("term", "屋顶")),
            ("建筑彩画", ("term", "彩画")),
            ("柱础", ("term", "柱础")),
            ("大木作", ("term", "大木作")),
            ("小木作", ("term", "小木作")),
            ("基座与台基", ("term", "基座")),
            ("榫卯结构", ("term", "榫卯")),
            ("举折与屋顶坡度", ("term", "举折")),
            ("建筑色彩等级", ("term", "色彩等级")),
            ("木结构体系", ("term", "结构体系")),
            ("石作制度", ("term", "石作")),
            ("瓦作制度", ("term", "瓦作")),
            ("砖作制度", ("term", "砖作")),
            ("藻井", ("term", "藻井")),
            ("栏杆", ("term", "栏杆")),
            ("吻兽与脊饰", ("term", "吻兽")),
            ("开间与进深", ("term", "开间")),
        ]

    def create_architecture_items(self):
        return [
            ("紫禁城（故宫）", ("architecture", "紫禁城")),
            ("太和殿", ("architecture", "太和殿")),
            ("佛光寺东大殿", ("architecture", "佛光寺东大殿")),
            ("应县木塔", ("architecture", "应县木塔")),
            ("布达拉宫", ("architecture", "布达拉宫")),
            ("颐和园", ("architecture", "颐和园")),
            ("拙政园", ("architecture", "拙政园")),
            ("圆明园", ("architecture", "圆明园")),
            ("长城", ("architecture", "长城")),
            ("南京城墙", ("architecture", "南京城墙")),
            ("徽派建筑", ("architecture", "徽派建筑")),
            ("客家土楼", ("architecture", "客家土楼")),
            ("山西大院", ("architecture", "山西大院")),
            ("明十三陵", ("architecture", "明十三陵")),
            ("秦始皇陵", ("architecture", "秦始皇陵")),
        ]

    def create_bridge_items(self):
        return [
            ("赵州桥", ("bridge", "赵州桥")),
            ("卢沟桥", ("bridge", "卢沟桥")),
            ("洛阳桥", ("bridge", "洛阳桥")),
            ("泸定桥", ("bridge", "泸定桥")),
            ("十七孔桥", ("bridge", "十七孔桥")),
            ("广济桥", ("bridge", "广济桥")),
        ]

    def show_term_detail(self, name, data):
        try:
            self.detail_scroll.verticalScrollBar().setValue(0)
        except:
            pass
        self.show_content(name, data)

    def show_content(self, name, data):
        self.current_item = (name, data)
        item_type, item_name = data if isinstance(data, tuple) else ("term", name)
        self.show_detail(item_type, item_name)

    def show_detail(self, item_type, item_name):
        try:
            if item_type == "term":
                info = get_term(item_name)
                if info:
                    title = info.get("title", item_name)
                    content = info.get("content", "")
                    category = info.get("category", "")
                    self.detail_title.setText(f"📜 {title}")
                    self.detail_text.setHtml(self.make_html(title, content, category))
            elif item_type == "architecture":
                info = get_architecture(item_name)
                if info:
                    title = info.get("title", item_name)
                    content = info.get("content", "")
                    category = info.get("category", "")
                    self.detail_title.setText(f"🏛️ {title}")
                    self.detail_text.setHtml(self.make_html(title, content, category))
            elif item_type == "bridge":
                info = get_bridge(item_name)
                if info:
                    title = info.get("title", item_name)
                    content = info.get("content", "")
                    category = info.get("category", "")
                    self.detail_title.setText(f"🌉 {title}")
                    self.detail_text.setHtml(self.make_html(title, content, category))
        except Exception as e:
            print(f"Error showing detail: {e}")

    def make_html(self, title, content, category=""):
        cat_html = f'<span style="color:{self.ACCENT_GOLD}; font-size:12px;">分类：{category}</span>' if category else ""

        lines = content.split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('<div style="height: 8px;"></div>')
            elif line.startswith('【') and line.endswith('】'):
                formatted_lines.append(f'<h3 style="color:{self.ACCENT_GOLD}; margin-top:18px; margin-bottom:8px; font-size:14px;">{line}</h3>')
            elif line.startswith('|'):
                formatted_lines.append(f'<div style="font-family:monospace; font-size:11px; color:{self.TEXT_TERTIARY}; background-color:{self.BG_CARD}; padding:6px 10px; border-radius:4px; margin:4px 0;">{line}</div>')
            elif line.startswith('- '):
                formatted_lines.append(f'<li style="color:{self.TEXT_SECONDARY}; margin:4px 0; font-size:13px;">{line[2:]}</li>')
            else:
                formatted_lines.append(f'<p style="margin:6px 0; font-size:13px; color:{self.TEXT_SECONDARY}; line-height:1.7;">{line}</p>')

        formatted_content = ''.join(formatted_lines)

        return f"""
        <div style="color: {self.TEXT_PRIMARY}; font-size: 14px;">
            <h2 style="color: {self.TEXT_PRIMARY}; margin-bottom: 6px; font-size:20px; font-weight:600;">{title}</h2>
            {cat_html}
            <div style="height: 1px; background-color: {self.BORDER_SUBTLE}; margin: 16px 0;"></div>
            <div style="line-height: 1.7;">
                {formatted_content}
            </div>
        </div>
        """

    def on_search_changed(self, text):
        if not text or len(text.strip()) < 1:
            self.search_result_label.setVisible(False)
            self.search_results_list.setVisible(False)
            return

        results = search_all(text.strip())
        self.search_results = results

        if results:
            self.search_result_label.setText(f"找到 {len(results)} 个相关词条")
            self.search_result_label.setVisible(True)
            self.search_results_list.setVisible(True)

            self.search_results_list.clear()
            for r in results[:15]:
                item_type = r.get("type", "")
                item_name = r.get("name", "")
                item_title = r.get("title", "")
                item_category = r.get("category", "")
                icon = {"term": "📜", "architecture": "🏛️", "bridge": "🌉"}.get(item_type, "📄")
                display_text = f"{icon}  {item_title}  [{item_category}]"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, (item_type, item_name))
                self.search_results_list.addItem(item)
        else:
            self.search_result_label.setText("未找到相关词条")
            self.search_result_label.setVisible(True)
            self.search_results_list.setVisible(False)

    def on_search_item_clicked(self, item):
        data = item.data(Qt.UserRole)
        if data:
            item_type, item_name = data
            self.show_detail(item_type, item_name)

    def create_right_panel(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {self.BG_SURFACE};
            border-radius: 14px;
            border: 1px solid {self.BORDER_SUBTLE};
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        self.detail_title = QLabel("📜  请选择词条查看详情")
        self.detail_title.setFont(self.get_font(18, "semibold"))
        self.detail_title.setStyleSheet(f"color: {self.TEXT_PRIMARY}; padding: 4px 0;")
        layout.addWidget(self.detail_title)

        self.detail_scroll = QScrollArea()
        self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                border-radius: 12px;
                background-color: {self.BG_CARD};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {self.BG_CARD};
                width: 8px;
                margin: 8px 0;
            }}
            QScrollBar::handle:vertical {{
                background: {self.BORDER_NORMAL};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.BORDER_NORMAL};
            }}
        """)

        content_widget = QFrame()
        content_widget.setStyleSheet("background-color: transparent;")

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setFont(self.get_font(14))
        self.detail_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.BG_CARD};
                color: {self.TEXT_PRIMARY};
                border: none;
                font-size: 14px;
            }}
        """)
        self.detail_text.setHtml("""
        <div style="color: #606060; font-size: 14px; text-align: center; padding: 40px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">📚</div>
            <div style="color: #a0a0a0; font-size: 15px;">欢迎使用古代建筑知识库</div>
            <div style="color: #606060; font-size: 13px; margin-top: 12px;">请从左侧选择词条查看详情</div>
        </div>
        """)

        content_layout.addWidget(self.detail_text)
        self.detail_scroll.setWidget(content_widget)
        layout.addWidget(self.detail_scroll, 1)

        return frame

    def update_api_key(self, key):
        pass
