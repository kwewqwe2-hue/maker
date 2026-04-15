from data.wenku_knowledge import get_answer as get_local_answer, get_bridge_info, YINGZAO_FASHI_KNOWLEDGE, WENKU_QUESTIONS, ANCIENT_ARCHITECTURE_DATA, BRIDGE_ARCHITECTURE
from core.ai_client import AIClient

class WenkuEngine:
    def __init__(self, ai_client=None):
        self.ai = ai_client or AIClient()
        self.knowledge = YINGZAO_FASHI_KNOWLEDGE
        self.questions = WENKU_QUESTIONS
        self.architecture_data = ANCIENT_ARCHITECTURE_DATA
        self.bridge_data = BRIDGE_ARCHITECTURE
        self.chat_history = []
    
    def set_api_key(self, api_key):
        self.ai.set_api_key(api_key)
    
    def ask(self, question, with_image=False, image_path=None):
        local_answer = self._get_local_answer(question)
        
        if self.ai.api_key:
            prompt = f"""你是一位精通《营造法式》和中国古代建筑典籍的专家。

参考知识：
{self.knowledge}

【建筑类型数据】
{self._format_architecture_data()}

请回答以下问题，如果参考知识中有相关信息，请优先结合参考知识回答：
问题：{question}

回答要求：专业、准确、结合《营造法式》的具体内容，尽量引用原文或具体数据。"""
            
            if with_image and image_path:
                result = self.ai.chat_with_image(
                    image_path,
                    f"请仔细观察这张图片，这是一张中国古代建筑的图片。请结合以下问题进行分析：{question}",
                    "你是一位中国古代建筑研究专家，擅长观察和分析古建筑图片。"
                )
            else:
                result = self.ai.chat([{"role": "system", "content": "你是一位精通《营造法式》和中国古代建筑典籍的专家。"}, 
                                       {"role": "user", "content": prompt}])
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            return f"AI分析失败：{result.get('error', '未知错误')}"
        else:
            if local_answer:
                return local_answer
            return self._get_fallback_response(question)
    
    def _format_architecture_data(self):
        lines = []
        for category, items in self.architecture_data.items():
            lines.append(f"\n【{category}】")
            if isinstance(items, dict):
                for name, info in items.items():
                    lines.append(f"• {name}：")
                    if isinstance(info, dict):
                        for k, v in info.items():
                            lines.append(f"  {k}：{v}")
                    else:
                        lines.append(f"  {info}")
        lines.append("\n【著名古桥】")
        if isinstance(self.bridge_data, dict) and "著名古桥" in self.bridge_data:
            for name, info in self.bridge_data["著名古桥"].items():
                lines.append(f"• {name}（{info.get('年代', '')}）：{info.get('desc', '')}")
        return "\n".join(lines)
    
    def _get_local_answer(self, question):
        q = question.lower()
        
        if "桥" in q:
            for bridge_name in ["赵州桥", "卢沟桥", "洛阳桥", "泸定桥", "广济桥", "十七孔桥"]:
                if bridge_name in q:
                    info = get_bridge_info(bridge_name)
                    if info:
                        result = f"【{bridge_name}】\n"
                        for key, value in info.items():
                            result += f"{key}：{value}\n"
                        return result
        
        for category, items in self.architecture_data.items():
            if category in q:
                result = f"【{category}】\n"
                if isinstance(items, dict):
                    for name, info in items.items():
                        result += f"\n{name}："
                        if isinstance(info, dict):
                            for k, v in info.items():
                                result += f"\n  {k}：{v}"
                        else:
                            result += f" {info}"
                return result
        
        local = get_local_answer(question)
        if local:
            return local
        
        return None
    
    def _get_fallback_response(self, question):
        keywords = {
            "斗栱": self.questions.get("斗栱"),
            "材分": self.questions.get("材分制"),
            "营造法式": self.questions.get("营造法式"),
            "屋顶": self.questions.get("屋顶"),
            "彩画": self.questions.get("彩画"),
            "柱础": self.questions.get("柱础"),
            "大木作": self.questions.get("大木作"),
            "小木作": self.questions.get("小木作"),
            "基座": self.questions.get("基座"),
            "榫卯": self.questions.get("榫卯"),
            "举折": self.questions.get("举折"),
            "色彩": self.questions.get("色彩等级"),
            "结构": self.questions.get("结构体系"),
        }
        for kw, ans in keywords.items():
            if kw in question:
                return ans
        
        intro = """【《营造法式》基础知识】

《营造法式》是北宋李诫编修的建筑技术专书，是中国古代最完整的建筑技术专著。

核心内容包括：
1. 壕寨制度：地基与基础的施工规范
2. 石作制度：石料的加工与砌筑
3. 大木作制度：木构架设计，包括梁、柱、斗栱等
4. 小木作制度：门、窗、栏杆等细部构件
5. 彩画作制度：建筑彩画的配色与纹样规范

重要术语：
• 斗栱：中国古代木结构特有的承重构件
• 材分制：以"材"作为木构建筑的模数制度，1材=15分
• 举架：屋面坡度的确定方法

中国古代建筑色彩等级：
• 最高：金色、黄琉璃瓦、朱红墙柱（皇宫）
• 其次：绿色琉璃瓦、青绿彩画（寺庙）
• 普通：灰瓦、朱红或黑色门窗
• 民居：灰瓦、白墙

您可以尝试询问以下问题：
• 什么是斗栱？
• 什么是材分制？
• 中国古建筑屋顶有哪些等级？
• 《营造法式》的主要内容是什么？
• 赵州桥的建造技术特点？

如需完整智能问答功能，请配置API密钥。
配置方法：点击右上角"设置API"按钮，输入从 https://siliconflow.cn 获取的免费API密钥。"""
        return intro
    
    def get_knowledge_intro(self):
        return self.knowledge
    
    def get_topic_list(self):
        return list(self.questions.keys())
