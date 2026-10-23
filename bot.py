import os
import requests
import google.generativeai as genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

prompt = """
أنت مساعد ذكي ومحترف. قم بإعداد تقرير يومي مختصر جداً ومنظم ومقسّم إلى 3 أقسام رئيسية كالتالي:
1. 🤖 AI & Machine Learning Trends
2. 🩺 AI in Medicine & Clinical Practice
3. 📈 Digital & Medical Marketing

شروط الكتابة:
- الشرح والتحليل يكون باللغة العربية الفصحى السلسة والمفهومة.
- أي Medical Term أو Technical Term (مثل Machine Learning, Clinical Diagnosis, Medical Marketing, Target Audience, ROI) يجب أن تبقى باللغة الإنجليزية حصراً في نص الجملة.
- تجنب تماماً أي تفاصيل معقدة تخص الشركات الناشئة أو الـ Startups، واجعل التركيز عملي ومباشر.
- اجعل التقرير مركزاً في نقاط سريعة بحيث لا يتجاوز إجمالي التقرير 3000 حرف.
"""

def generate_report():
    available_models = [
        m.name for m in genai.list_models() 
        if 'generateContent' in m.supported_generation_methods
    ]
    available_models.sort(reverse=True)
    print("All available models:", available_models)

    for model_name in available_models:
        try:
            print(f"Trying model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            print(f"Success with {model_name}!")
            return response.text
        except Exception as e:
            print(f"Skipped {model_name} due to error: {e}")
            continue
            
    raise Exception("No working model found in the list.")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    max_length = 4000
    
    # تقسيم الرسالة تلقائياً إذا كانت أطول من حد تيليجرام المسموح
    for i in range(0, len(text), max_length):
        chunk = text[i:i + max_length]
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk
        }
        response = requests.post(url, json=payload)
        print(f"Part {i//max_length + 1} response:", response.json())

if __name__ == "__main__":
    report_text = generate_report()
    send_telegram_message(report_text)
