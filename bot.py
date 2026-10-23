import os
import re
import asyncio
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import google.generativeai as genai
import edge_tts

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

today_date = datetime.now().strftime("%Y-%m-%d")

# دالة سحب أحدث الأبحاث الطبية الحقيقية من PubMed
def fetch_latest_pubmed_papers():
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": "(artificial intelligence[Title/Abstract]) AND (clinical diagnosis[Title/Abstract] OR medicine[Title/Abstract])",
            "sort": "date",
            "retmax": 1,
            "retmode": "json"
        }
        res = requests.get(search_url, params=search_params, timeout=10).json()
        id_list = res.get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            return "لا توجد بيانات بحثية جديدة اليوم، اعتمد على المعطيات السريرية العامة."

        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml"
        }
        xml_data = requests.get(fetch_url, params=fetch_params, timeout=10).text
        root = ET.fromstring(xml_data)
        
        for article in root.findall(".//PubmedArticle"):
            title = article.findtext(".//ArticleTitle", default="")
            abstract = " ".join([elem.text for elem in article.findall(".//AbstractText") if elem.text])
            if title and abstract:
                return f"Title: {title}\nAbstract: {abstract[:600]}..."
        
        return "بحث حديث في مجال الذكاء الاصطناعي الطبي والتشخيص السريري."
    except Exception as e:
        print("PubMed fetch error:", e)
        return "تعذر جلب البحث اليوم، اعتمد على أحدث التقنيات السريرية."

pubmed_context = fetch_latest_pubmed_papers()

prompt = f"""
أنت مساعد ذكي ومحترف. اليوم هو {today_date}.
قم إعداد تقرير يومي منظم، منسق، ومرتب تماماً في **4 أقسام رئيسية** كالتالي:

1. 🤖 AI & Machine Learning Trends
2. 🩺 AI in Medicine & Clinical Practice
3. 📈 Digital & Medical Marketing
4. 🔬 PubMed Research Spotlight (أحدث الأبحاث الطبية)

بيانات البحث العلمي المسحوبة اليوم من PubMed للقسم الرابع:
{pubmed_context}

شروط التنسيق والكتابة الصارمة جداً لمنع أي تداخل أو نص "سايح":
- ابدأ التقرير النهائي فوراً بهذه الروشة في السطر الأول تماماً:
📅 تقرير المستشار الذكي | التاريخ: {today_date}
- ممنوع كتابة فقرات طويلة ومترابطة؛ اجعل كل قسم مكوناً من **نقاط محددة وصغيرة (Bullet Points)** متبوعة بإيموجي ومسافات واضحة مريحة للعين.
- في القسم الرابع (🔬 PubMed Research Spotlight)، نظّم الملخص بهذه الطريقة تماماً:
  • 📌 عنوان البحث: [...]
  • 💡 الفكرة الأساسية: [...]
  • 🎯 النتيجة الإكلينيكية: [...]
- الشرح والتحليل يكون باللغة العربية الفصحى السلسة، مع إبقاء الـ Medical & Technical Terms باللغة الإنجليزية حصراً داخل الجمل.
- لا تزيد إجمالي الكلمات عن 2500 حرف ليكون التقرير مركزاً وخفيفاً وخالياً من الحشو.
"""

def generate_report():
    available_models = [
        m.name for m in genai.list_models() 
        if 'generateContent' in m.supported_generation_methods and 'thinking' not in m.name.lower()
    ]
    available_models.sort(reverse=True)

    for model_name in available_models:
        try:
            print(f"Trying model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.6} # تقليل العشوائية لضمان التنسيق الدقيق
            )
            text = response.text
            
            if "📅" in text:
                text = "📅" + text.rsplit("📅", 1)[-1]
                
            return text.strip()
        except Exception as e:
            print(f"Skipped {model_name} due to error: {e}")
            continue
            
    raise Exception("No working model found.")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    max_length = 4000
    for i in range(0, len(text), max_length):
        chunk = text[i:i + max_length]
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": chunk}
        requests.post(url, json=payload)

def clean_text_for_audio(text):
    # تنظيف الرموز لضمان قراءة صوتية سلسة وبدون تلعثم
    cleaned = re.sub(r'[#*`_~—\-+=|•🔹🔬💡🛠️🚀🤖🩺📈📅📱1️⃣2️⃣3️⃣4️⃣•📌]', ' ', text)
    return cleaned

async def create_audio(text, filename="briefing.mp3"):
    clean_text = clean_text_for_audio(text)
    # استخدام صوت عصبي فائق النقاء والوضوح واحترافي جداً
    voice = "ar-EG-SalmaNeural"
    communicate = edge_tts.Communicate(clean_text, voice, rate="+0%")
    await communicate.save(filename)

def send_telegram_audio(filename="briefing.mp3"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAudio"
    with open(filename, "rb") as audio_file:
        files = {"audio": audio_file}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "title": f"الخلاصة الصوتية - {today_date}",
            "performer": "Smart Consultant AI",
            "caption": "🎧 الملخص الصوتي الجديد بصوت أوضح ومنسق بالكامل!"
        }
        requests.post(url, data=data, files=files)

if __name__ == "__main__":
    report_text = generate_report()
    
    # 1. إرسال التقرير المكتوب منسقاً في 4 أقسام
    send_telegram_message(report_text)
    
    # 2. توليد وإرسال التسجيل الصوتي بالصوت الجديد المطور
    print("Generating upgraded audio briefing...")
    asyncio.run(create_audio(report_text))
    send_telegram_audio()
