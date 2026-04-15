from data.yantu_data import (
    BRIDGE_DATA, BRIDGE_TYPES, BRIDGE_TIMELINE, 
    BRIDGE_REGIONS, BRIDGE_ARCHITECT_TECHNIQUES, SPECIAL_BRIDGE_FEATURES,
    get_bridges_by_dynasty, get_all_bridges, search_bridges,
    get_bridge_technique, get_bridge_features, get_bridge_conservation_info
)
from core.ai_client import AIClient

class YantuEngine:
    def __init__(self, ai_client=None):
        self.ai = ai_client or AIClient()
        self.bridge_data = BRIDGE_DATA
        self.bridge_types = BRIDGE_TYPES
        self.timeline = BRIDGE_TIMELINE
        self.regions = BRIDGE_REGIONS
        self.chat_history = []
    
    def set_api_key(self, api_key):
        self.ai.set_api_key(api_key)
    
    def get_timeline(self):
        return self.timeline
    
    def get_periods(self):
        return list(self.bridge_data.keys())
    
    def get_period_info(self, period_key):
        return self.bridge_data.get(period_key, {})
    
    def get_type_info(self, type_key):
        return self.bridge_types.get(type_key, {})
    
    def get_regions(self):
        return self.regions
    
    def search(self, keyword):
        return search_bridges(keyword)
    
    def get_technique(self, bridge_name):
        return get_bridge_technique(bridge_name)
    
    def ask(self, question):
        local_info = self._get_local_info(question)
        
        if self.ai.api_key:
            prompt = f"""你是一位中国古代桥梁建筑史专家。以下是中国古代桥梁的时空演化数据：

【历史分期】
{self._format_periods()}

【代表桥梁】
{self._format_timeline()}

【桥型分类】
{self._format_types()}

【建造技术】
{self._format_techniques()}

请回答关于中国古代桥梁的问题：
问题：{question}

回答要求：专业、准确，结合提供的桥梁数据，尽量提及具体的桥梁名称、年代和技术特点。"""
            
            result = self.ai.chat([
                {"role": "system", "content": "你是一位中国古代桥梁建筑史专家。"},
                {"role": "user", "content": prompt}
            ])
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            return f"AI分析失败：{result.get('error', '未知错误')}"
        else:
            if local_info:
                return local_info
            return self._get_local_response(question)
    
    def _format_periods(self):
        lines = []
        for period, info in self.bridge_data.items():
            lines.append(f"■ {period}")
            lines.append(f"  代表：{', '.join(info.get('代表建筑', []))}")
            lines.append(f"  特点：{info.get('特点', '')}")
            lines.append(f"  技术：{info.get('技术', '')}")
            lines.append(f"  地域：{info.get('地域', '')}")
            lines.append("")
        return "\n".join(lines)
    
    def _format_timeline(self):
        lines = []
        for b in self.timeline:
            lines.append(f"• {b['dynasty']}·{b['name']}（{b['year']}年）| {b['type']} | {b['location']}")
            lines.append(f"  {b['desc']}")
        return "\n".join(lines)
    
    def _format_types(self):
        lines = []
        for tname, tinfo in self.bridge_types.items():
            lines.append(f"■ {tname}")
            lines.append(f"  描述：{tinfo['desc']}")
            lines.append(f"  历史：{tinfo['历史']}")
            lines.append(f"  代表：{tinfo['代表']}")
            if '技术' in tinfo:
                lines.append(f"  技术：{tinfo['技术']}")
            lines.append("")
        return "\n".join(lines)
    
    def _format_techniques(self):
        lines = []
        for name, tech in BRIDGE_ARCHITECT_TECHNIQUES.items():
            lines.append(f"◆ {name}")
            for key, value in tech.items():
                lines.append(f"  {key}：{value}")
            lines.append("")
        return "\n".join(lines)
    
    def _get_local_info(self, question):
        q = question.lower()
        
        if "建造技术" in q or "建造方法" in q or "怎么建" in q:
            for name in ["赵州桥", "卢沟桥", "洛阳桥", "泸定桥"]:
                if name in q:
                    tech = get_bridge_technique(name)
                    if tech:
                        result = f"【{name}建造技术】\n"
                        for key, value in tech.items():
                            result += f"{key}：{value}\n"
                        return result
        
        if "雕刻" in q or "石狮" in q:
            features = get_bridge_features("桥上雕刻")
            if features:
                result = "【古桥雕刻艺术】\n"
                for name, desc in features.items():
                    result += f"{name}：{desc}\n"
                return result
        
        if "文学" in q or "诗词" in q or "典故" in q:
            features = get_bridge_features("桥梁与文学")
            if features:
                result = "【桥梁与文学】\n"
                for name, desc in features.items():
                    result += f"{name}：{desc}\n"
                return result
        
        if "保护" in q or "修缮" in q or "维修" in q:
            info = get_bridge_conservation_info()
            result = "【古桥保护知识】\n"
            result += f"保护原则：{info['古桥保护原则']}\n\n"
            for name, desc in info.items():
                if name != "古桥保护原则":
                    result += f"{name}：{desc}\n\n"
            return result
        
        for bridge_type, info in self.bridge_types.items():
            if bridge_type in q:
                result = f"【{bridge_type}】\n"
                result += f"描述：{info['desc']}\n"
                result += f"历史：{info['历史']}\n"
                result += f"代表桥梁：{info['代表']}\n"
                if '技术' in info:
                    result += f"技术特点：{info['技术']}\n"
                return result
        
        return None
    
    def _get_local_response(self, question):
        q = question.lower()
        
        if "演化" in q or "历史" in q or "发展" in q:
            return self._format_periods()
        
        if "类型" in q or "桥型" in q or "分类" in q:
            return self._format_types()
        
        if "著名" in q or "代表" in q or "有名" in q:
            return "中国古代著名桥梁：\n" + self._format_timeline()
        
        results = self.search(question)
        if results:
            return "搜索结果：\n" + "\n".join([f"• {r.get('name','')}: {r.get('desc','')}" for r in results[:5]])
        
        return """抱歉，当前未配置AI密钥，无法进行智能问答。

【中国古代桥梁知识简介】

中国古代桥梁按结构分为四大类型：
1. 梁桥：以梁承重，最古老的形式
2. 拱桥：以拱券承重，技术成熟于隋唐
3. 悬索桥：以缆索吊挂，泸定桥为代表
4. 廊桥：桥上有廊屋，侗族地区多见

中国古代著名桥梁：
• 赵州桥（隋·605年）：世界上现存最早的敞肩石拱桥
• 卢沟桥（金·1189年）：北京现存最古老的石拱桥，桥上石狮闻名
• 泸定桥（清·1705年）：铁链悬索桥，全长103米
• 十七孔桥（清·1701年）：颐和园标志性建筑
• 洛阳桥（宋·1053年）：首创筏型基础和牡蛎固基技术

请配置API密钥以获取完整的智能问答功能。
配置方法：点击右上角"设置API"按钮，输入从 https://siliconflow.cn 获取的免费API密钥。"""
    
    def get_timeline_json(self):
        return self.timeline
