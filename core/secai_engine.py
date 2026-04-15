import os
import colorsys
from PIL import Image
import numpy as np
from core.ai_client import AIClient

PALACE_COLORS = {
    "\u6545\u5bab\u7ea2": {
        "hex": "#C1453F",
        "rgb": (193, 69, 63),
        "name": "\u6545\u5bab\u7ea2 / \u6731\u7ea2",
        "desc": "\u7d2b\u7984\u57ce\u5bab\u5899\u7684\u6807\u51c6\u7ea2\u8272\uff0c\u6e90\u81ea\u6731\u7802\u989c\u6599\uff0c\u8c61\u5f81\u7687\u5bb6\u5a01\u4e25\u4e0e\u559c\u5e86",
        "usage": "\u7528\u4e8e\u5ba1\u6bbf\u5916\u5899\u3001\u5bab\u95e8\u3001\u67f1\u5b50",
        "cultural": "\u7ea2\u8272\u5728\u4e2d\u534e\u6587\u5316\u4e2d\u8c61\u5f81\u559c\u5e86\u3001\u5409\u7965\u3001\u70ed\u70c8"
    },
    "\u6d41\u79bb\u9ec4": {
        "hex": "#F5C84C",
        "rgb": (245, 200, 76),
        "name": "\u6d41\u79bb\u9ec4",
        "desc": "\u9ec4\u8272\u662f\u7687\u5bb6\u4e13\u7528\u8272\u5f69\uff0c\u6d41\u79bb\u74f6\u7684\u91d1\u9ec4\u8272\u662f\u5ba1\u6bbf\u5c4b\u9876\u7684\u4ee3\u8868\u8272",
        "usage": "\u7528\u4e8e\u5ba1\u6bbf\u5c4b\u9876\u3001\u7687\u5bb6\u5668\u7269",
        "cultural": "\u9ec4\u8272\u8c61\u5f81\u4e2d\u592e\u3001\u7687\u6743\uff0c\u9ec4\u8272\u6d41\u79bb\u74f6\u53ea\u6709\u7687\u5bb6\u5efa\u7b51\u624d\u80fd\u4f7f\u7528"
    },
    "\u9752\u7eff": {
        "hex": "#2E8B57",
        "rgb": (46, 139, 87),
        "name": "\u9752\u7eff\u8272",
        "desc": "\u5efa\u7b51\u5f69\u753b\u4e2d\u7684\u91cd\u8981\u914d\u8272\uff0c\u5982\u65cb\u5b50\u5f69\u753b\u7684\u9752\u7eff\u53e0\u6655",
        "usage": "\u7528\u4e8e\u5f69\u753b\u3001\u6a84\u4e0b\u9634\u5f71\u90e8\u5206",
        "cultural": "\u9752\u7eff\u8272\u6709\u51b7\u8272\u540e\u9000\u611f\uff0c\u6d82\u4e8e\u6a84\u4e0b\u589e\u52a0\u5efa\u7b51\u6df1\u5ea6\u611f"
    },
    "\u6d01\u767d": {
        "hex": "#F5F5F0",
        "rgb": (245, 245, 240),
        "name": "\u6c49\u767d\u7389\u767d",
        "desc": "\u6545\u5bab\u53f0\u57fa\u3001\u6905\u6760\u4f7f\u7528\u7684\u767d\u8272\u5927\u7406\u77f3\uff0c\u989c\u8272\u6e29\u6da6\u6d01\u767d",
        "usage": "\u7528\u4e8e\u987b\u5f25\u5ea7\u53f0\u57fa\u3001\u6905\u6760\u3001\u4e39\u9655\u77f3",
        "cultural": "\u767d\u8272\u8c61\u5f81\u7eaf\u51c0\uff0c\u4e0e\u7ea2\u5899\u9ec4\u74f6\u5f62\u6210\u9c9c\u660e\u5bf9\u6bd4"
    },
    "\u7384\u9752": {
        "hex": "#1C1C2E",
        "rgb": (28, 28, 46),
        "name": "\u7384\u9752\u8272",
        "desc": "\u6df1\u6c89\u7684\u9752\u9ed1\u8272\uff0c\u7528\u4e8e\u5c4b\u810a\u3001\u5c71\u82b1\u7b49\u90e8\u4f4d",
        "usage": "\u7528\u4e8e\u5c4b\u9875\u6b63\u810a\u3001\u5782\u810a",
        "cultural": "\u9ed1\u8272\u5c5e\u6c34\uff0c\u7528\u4e8e\u5c4b\u9876\u6709\u9547\u706b\u4e4b\u610f"
    },
    "\u94dc\u91d1": {
        "hex": "#B8860B",
        "rgb": (184, 134, 11),
        "name": "\u94dc\u91d1\u8272",
        "desc": "\u9530\u91d1\u94dc\u74f6\u548c\u88c5\u9970\u6784\u4ef6\u7684\u91d1\u8272",
        "usage": "\u7528\u4e8e\u592a\u548c\u6bbf\u5c4b\u9876\u3001\u93ae\u91d1\u88c5\u9970",
        "cultural": "\u91d1\u8272\u8c61\u5f81\u81f3\u9ad8\u65e0\u4e0a\u7684\u7687\u6743"
    }
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def get_color_name(rgb):
    r, g, b = rgb[0]/255, rgb[1]/255, rgb[2]/255

    for name, info in PALACE_COLORS.items():
        pr, pg, pb = info["rgb"]
        dr, dg, db = (r - pr/255), (g - pg/255), (b - pb/255)
        distance = (dr**2 + dg**2 + db**2) ** 0.5
        if distance < 0.3:
            return name, info
    return None, None

def extract_dominant_colors(image_path, num_colors=5):
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        img = img.resize((150, 150))
        pixels = np.array(img)

        pixels = pixels.reshape(-1, 3)

        def color_distance(c1, c2):
            return np.sqrt(np.sum((c1 - c2) ** 2))

        np.random.seed(42)
        centroids = pixels[np.random.choice(len(pixels), min(num_colors, 5), replace=False)]

        for _ in range(20):
            distances = np.array([[color_distance(p, c) for c in centroids] for p in pixels])
            labels = np.argmin(distances, axis=1)

            new_centroids = np.array([
                pixels[labels == i].mean(axis=0) if np.any(labels == i) else centroids[i]
                for i in range(len(centroids))
            ])

            if np.allclose(centroids, new_centroids, atol=1.0):
                break
            centroids = new_centroids

        colors = []
        for centroid in centroids:
            r, g, b = int(centroid[0]), int(centroid[1]), int(centroid[2])
            hex_color = rgb_to_hex(r, g, b)
            name, info = get_color_name((r, g, b))
            if name:
                desc = info["desc"]
            else:
                desc = f"RGB({r},{g},{b})"
            colors.append({
                "rgb": (r, g, b),
                "hex": hex_color,
                "name": name or "\u672a\u5339\u914d\u8272\u5f69",
                "description": desc
            })

        return sorted(colors, key=lambda x: np.mean(x["rgb"]), reverse=True)
    except Exception as e:
        return []

class SecaiEngine:
    def __init__(self, ai_client=None):
        self.ai = ai_client or AIClient()
        self.palace_colors = PALACE_COLORS
        self.chat_history = []

    def set_api_key(self, api_key):
        self.ai.set_api_key(api_key)

    def analyze_colors(self, image_path):
        colors = extract_dominant_colors(image_path, num_colors=5)
        if not colors:
            return {"error": "\u65e0\u6cd5\u8bfb\u53d6\u56fe\u7247\u6216\u56fe\u7247\u683c\u5f0f\u4e0d\u652f\u6301"}

        matched = []
        for c in colors:
            name, info = get_color_name(c["rgb"])
            if name:
                matched.append({
                    **c,
                    "palace_match": name,
                    "palace_info": info
                })

        return {
            "extracted_colors": colors,
            "matched_palace_colors": matched,
            "total_colors": len(colors)
        }

    def ask(self, question):
        if self.ai.api_key:
            prompt = f"""\u4f60\u662f\u4e00\u4f4d\u4e2d\u56fd\u53e4\u4ee3\u5efa\u7b51\u8272\u5f69\u7814\u7a76\u4e13\u5bb6\uff0c\u5c3d\u7cbe\u901a\u6545\u5bab\u7b49\u7687\u5bb6\u5efa\u7b51\u7684\u8272\u5f69\u4f53\u7cfb\u3002

\u3010\u6545\u5bab\u8272\u5f69\u4f53\u7cfb\u3011
{self._format_palace_colors()}

\u8bf7\u56de\u7b54\u5173\u4e8e\u5efa\u7b51\u8272\u5f69\u7684\u95ee\u9898\uff1a
\u95ee\u9898\uff1a{question}

\u56de\u7b54\u8981\u6c42\uff1a\u4e13\u4e1a\u3001\u51c6\u786e\uff0c\u7ed3\u5408\u6545\u5bab\u7b49\u7687\u5bb6\u5efa\u7b51\u7684\u8272\u5f69\u5b9e\u4f8b\u548c\u6587\u5316\u5185\u6db5\u3002"""

            result = self.ai.chat([
                {"role": "system", "content": "\u4f60\u662f\u4e00\u4f4d\u4e2d\u56fd\u53e4\u4ee3\u5efa\u7b51\u8272\u5f69\u7814\u7a76\u4e13\u5bb6\u3002"},
                {"role": "user", "content": prompt}
            ])

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            return f"AI\u5206\u6790\u5931\u8d25\uff1a{result.get('error', '\u672a\u77e5\u9519\u8bef')}"
        else:
            return self._get_local_response(question)

    def _format_palace_colors(self):
        lines = []
        for name, info in self.palace_colors.items():
            lines.append(f"\u25a0 {name} ({info['hex']})")
            lines.append(f"  \u63cf\u8ff0\uff1a{info['desc']}")
            lines.append(f"  \u7528\u9014\uff1a{info['usage']}")
            lines.append(f"  \u6587\u5316\uff1a{info['cultural']}")
            lines.append("")
        return "\n".join(lines)

    def _get_local_response(self, question):
        q = question.lower()

        if "\u63d0\u53d6" in q or "\u5206\u6790" in q or "\u989c\u8272" in q:
            return """\u8272\u5f69\u5206\u6790\u529f\u80fd\uff1a
\u60a8\u53ef\u4ee5\u4e0a\u4f20\u4e2d\u56fd\u53e4\u4ee3\u5efa\u7b51\u7684\u56fe\u7247\uff0c\u7cfb\u7edf\u5c06\u81ea\u52a8\u63d0\u53d6\u56fe\u7247\u4e2d\u7684\u4e3b\u8981\u8272\u5f69\uff0c\u5e76\u4e0e\u6545\u5bab\u8272\u5f69\u4f53\u7cfb\u8fdb\u884c\u5339\u914d\u3002

\u652f\u6301\u7684\u56fe\u7247\u683c\u5f0f\uff1aJPG\u3001PNG\u3001BMP

\u8bf7\u70b9\u51fb"\u4e0a\u4f20\u56fe\u7247"\u6309\u94ae\u9009\u62e9\u56fe\u7247\u8fdb\u884c\u8272\u5f69\u5206\u6790\u3002"""

        for name, info in self.palace_colors.items():
            if name.replace("\u6545\u5bab", "").replace("\u6d41\u79bb", "").replace("\u9752\u7eff", "").replace("\u6d01\u767d", "").replace("\u7384\u9752", "").replace("\u94dc\u91d1", "") in q:
                return f"""\u3010{name}\u3011
\u63cf\u8ff0\uff1a{info['desc']}
\u7528\u9014\uff1a{info['usage']}
\u6587\u5316\u542b\u4e49\uff1a{info['cultural']}
RGB\uff1a{info['rgb']}
HEX\uff1a{info['hex']}"""

        return f"""\u62b1\u6b49\uff0c\u5f53\u524d\u672a\u914d\u7f6eAI\u5bc6\u94a5\u3002\u4ee5\u4e0b\u662f\u6545\u5bab\u8272\u5f69\u4f53\u7cfb\u7b80\u4ecb\uff1a

\u3010\u6545\u5bab\u4e94\u5927\u4ee3\u8868\u8272\u5f69\u3011
1. \u6545\u5bab\u7ea2 #C1453F - \u5bab\u5899\u6807\u51c6\u7ea2\u8272\uff0c\u8c61\u5f81\u7687\u5bb6\u5a01\u4e25
2. \u6d41\u79bb\u9ec4 #F5C84C - \u7687\u5bb6\u4e13\u7528\uff0c\u9ec4\u8272\u6d41\u79bb\u74f6
3. \u9752\u7eff\u8272 #2E8B57 - \u5f69\u753b\u914d\u8272\uff0c\u589e\u52a0\u5efa\u7b51\u6df1\u5ea6\u611f
4. \u6c49\u767d\u7389\u767d #F5F5F0 - \u53f0\u57fa\u6905\u6760\uff0c\u7eaf\u51c0\u9ad8\u96c5
5. \u7384\u9752\u8272 #1C1C2E - \u5c4b\u810a\u6b63\u8272\uff0c\u954d\u706b\u4e4b\u610f

\u60a8\u53ef\u4ee5\u5c1d\u8bd5\u8be2\u95ee\uff1a
• \u6545\u5bab\u7ea2\u6709\u4ec0\u4e48\u6587\u5316\u542b\u4e49\uff1f
• \u4e3a\u4ec0\u4e48\u5ba1\u6bbf\u5c4b\u9876\u7528\u9ec4\u8272\uff1f
• \u5982\u4f55\u4f7f\u7528\u8272\u5f69\u5206\u6790\u529f\u80fd\uff1f"""

    def get_palace_colors(self):
        return self.palace_colors
