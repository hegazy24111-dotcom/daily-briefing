import os
import requests
import google.generativeai as genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# البحث تلقائياً عن الموديلات المتاحة والمدعومة في حسابك لتجنب خطأ 404 نهائياً
available_models = [
    m.name for m in genai.list_models() 
    if 'generateContent' in m.supported_generation_methods
]

print("Available models:", available_models)

# اختيار موديل flash المتاح تلقائياً أو أول موديل شغال في القائمة
selected_model = next((m for m in available_models if 'flash' in m), available_models[0])
print("Using model:", selected_model)

model = genai.GenerativeModel(selected_model)

prompt = """
أنت مساعد ذكي ومحترف. قم بإعداد تقرير يومي مختصر ومنظم ومقسّم إلى 3 أقسام رئيسية كالتالي:
1. 🤖 AI & Machine Learning Trends
2. 🩺 AI in Medicine & Clinical Practice
3. 📈 Digital & Medical Marketing

شروط الكتابة:
- الشرح والتحليل يكون باللغة العربية الفصحى السلسة والمفهومة.
- أي Medical Term أو Technical Term (مثل Machine Learning, Clinical Diagnosis, Medical Marketing, Target Audience, ROI) يجب أن تبقى باللغة الإنجليزية حصراً في نص الجملة.
- تجنب تماماً أي تفاصيل معقدة تخص الشركات الناشئة أو الـ Startups، واجعل التركيز عملي ومباشر.
"""

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == "__main__":
    response = model.generate_content(prompt)
    report_text = response.text
    res = send_telegram_message(report_text)
    print("Telegram response:", res)
