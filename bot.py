import os
import requests
from datetime import datetime
import google.generativeai as genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# تحديد تاريخ اليوم وزاوية تركيز مختلفة لكل يوم في الأسبوع لمنع التكرار نهائياً
today_date = datetime.now().strftime("%Y-%m-%d")
day_of_year = datetime.now().timetuple().tm_yday

daily_themes = [
    "أدوات عملية جديدة، تطبيقات التشخيص السريري، واستراتيجيات الاستحواذ على المرضى (Patient Acquisition)",
    "تحليل حالات عملية (Case Studies)، الذكاء الاصطناعي في الأشعة والتحاليل، وبناء العلامة التجارية للأطباء (Personal Branding)",
    "الأتمتة الذكية (Workflow Automation)، الطب التنبؤي (Predictive Medicine)، وكتابة المحتوى الطبي التسويقي",
    "تقنيات الـ Large Language Models، تقليل الأخطاء الطبية، وتحسين معدل التحويل في الإعلانات الطبية (Conversion Rate Optimization)",
    "أخلاقيات ودقة الـ AI، متابعة المرضى عن بُعد (Telemedicine & Remote Monitoring)، واستراتيجيات الاحتفاظ بالمرضى (Patient Retention)",
    "مهارات الـ Prompt Engineering المتقدمة، الذكاء الاصطناعي في الصيدلة والأدوية، والتسويق عبر الفيديو القصير للعيادات",
    "تحليل البيانات الضخمة، إدارة العيادات والمستشفيات ذكياً، وقياس العائد على الاستثمار (ROI & Analytics) في الحملات الطبية"
]

todays_theme = daily_themes[day_of_year % len(daily_themes)]

prompt = f"""
أنت مستشار ذكي ومحترف. اليوم هو {today_date}.
قم بإعداد تقرير يومي متجدد ومبتكر ومقسّم إلى 3 أقسام رئيسية كالتالي:
1. 🤖 AI & Machine Learning Trends
2. 🩺 AI in Medicine & Clinical Practice
3. 📈 Digital & Medical Marketing

زاوية التركيز الخاصة بيوم ({today_date}) لمنع التكرار:
ركز اليوم بشكل خاص على: ({todays_theme}).

شروط الكتابة الهامة:
- تجنب الكلام العام الإنشائي المكرر؛ قدم في كل قسم: (أداة عملية محددة، أو تقنية دقيقة، أو سيناريو تطبيقي/Case Study، أو نصيحة قابلة للتنفيذ فوراً).
- الشرح والتحليل يكون باللغة العربية الفصحى السلسة والمفهومة.
- أي Medical Term أو Technical Term (مثل Machine Learning, Clinical Diagnosis, Medical Marketing, Target Audience, ROI) يجب أن تبقى باللغة الإنجليزية حصراً في نص الجملة.
- تجنب تماماً أي تفاصيل معقدة تخص الشركات الناشئة أو الـ Startups، واجعل التركيز عملي ومباشر.
- لا تستخدم رموز الماركداون المعقدة، ونسّق العناوين والنقاط بالإيموجي بشكل أنيق ومريح للعين، بحيث لا يتجاوز التقرير 3000 حرف.
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
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.85} # رفع درجة التنوع والابتكار يومياً
            )
            print(f"Success with {model_name}!")
            return response.text
        except Exception as e:
            print(f"Skipped {model_name} due to error: {e}")
            continue
            
    raise Exception("No working model found in the list.")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    max_length = 4000
    
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
