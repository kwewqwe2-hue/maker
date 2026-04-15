import os
import requests
import json
import base64
from io import BytesIO

class AIClient:
    def __init__(self, api_key=None, api_url=None, model=None):
        self.api_key = api_key or os.environ.get("SF_API_KEY", "")
        self.api_url = api_url or "https://api.siliconflow.cn/v1"
        self.model = model or "Qwen/Qwen2.5-7B-Instruct"

    def set_api_key(self, api_key):
        self.api_key = api_key

    def set_model(self, model):
        self.model = model

    def chat(self, messages, temperature=0.7, max_tokens=2000):
        if not self.api_key:
            return {"error": "\u8bf7\u5148\u914d\u7f6eAPI\u5bc6\u94a5", "choices": [{"message": {"content": "\u9519\u8bef\uff1a\u8bf7\u5148\u5728\u8bbe\u7f6e\u4e2d\u914d\u7f6eAPI\u5bc6\u94a5\uff01\n\n\u5982\u679c\u8fd8\u6ca1\u6709API\u5bc6\u94a5\uff0c\u8bf7\u8bbf\u95ee https://siliconflow.cn \u6ce8\u518c\u5e76\u83b7\u53d6\u514d\u8d39API\u5bc6\u94a5\u3002"}}]}

        url = f"{self.api_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "\u8bf7\u6c42\u8d85\u65f6\uff0c\u8bf7\u68c0\u67e5\u7f51\u7edc\u8fde\u63a5", "choices": [{"message": {"content": "\u8bf7\u6c42\u8d85\u65f6\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002"}}]}
        except requests.exceptions.ConnectionError:
            return {"error": "\u7f51\u7edc\u8fde\u63a5\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u7f51\u7edc", "choices": [{"message": {"content": "\u7f51\u7edc\u8fde\u63a5\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u7f51\u7edc\u8bbe\u7f6e\u3002"}}]}
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                return {"error": "API\u5bc6\u94a5\u65e0\u6548", "choices": [{"message": {"content": "API\u5bc6\u94a5\u65e0\u6548\uff0c\u8bf7\u68c0\u67e5\u662f\u5426\u6b63\u786e\u914d\u7f6e\u3002"}}]}
            elif response.status_code == 429:
                return {"error": "\u8bf7\u6c42\u8fc7\u4e8e\u9891\u7e41", "choices": [{"message": {"content": "\u8bf7\u6c42\u8fc7\u4e8e\u9891\u7e41\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002"}}]}
            else:
                return {"error": str(e), "choices": [{"message": {"content": f"\u8bf7\u6c42\u5931\u8d25\uff1a{e}"}}]}
        except Exception as e:
            return {"error": str(e), "choices": [{"message": {"content": f"\u53d1\u751f\u9519\u8bef\uff1a{e}"}}]}

    def chat_with_image(self, image_path, text_prompt, system_prompt=""):
        if not self.api_key:
            return {"choices": [{"message": {"content": "\u9519\u8bef\uff1a\u8bf7\u5148\u914d\u7f6eAPI\u5bc6\u94a5\uff01"}}]}

        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        content = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
            {"type": "text", "text": text_prompt}
        ]
        messages.append({"role": "user", "content": content})

        url = f"{self.api_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "Qwen/Qwen2-VL-7B-Instruct",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"choices": [{"message": {"content": f"\u56fe\u7247\u5206\u6790\u5931\u8d25\uff1a{e}"}}]}

    def simple_chat(self, user_text, system_text=""):
        messages = []
        if system_text:
            messages.append({"role": "system", "content": system_text})
        messages.append({"role": "user", "content": user_text})
        result = self.chat(messages)
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        return str(result.get("error", "\u672a\u77e5\u9519\u8bef"))

def test_api_key(api_key):
    client = AIClient(api_key=api_key)
    result = client.simple_chat("\u4f60\u597d\uff0c\u8bf7\u56de\u590d'\u6d4b\u8bd5\u6210\u529f'\uff0c\u4e0d\u8981\u8d85\u8fc710\u4e2a\u5b57\u3002", "\u4f60\u662f\u4e00\u4e2a\u7b80\u5355\u7684\u52a9\u624b\u3002")
    if "\u6d4b\u8bd5\u6210\u529f" in result:
        return True, "API\u5bc6\u94a5\u6709\u6548\uff0c\u8fde\u63a5\u6210\u529f\uff01"
    elif "\u9519\u8bef" in result or "\u65e0\u6548" in result:
        return False, result
    else:
        return False, f"API\u54cd\u5e94\u5f02\u5e38\uff1a{result[:100]}"
