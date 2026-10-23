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

# دالة سحب أحدث الأبحاث الطبية من PubMed
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
            return "No recent data found. Use general clinical intelligence."

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
        
        return "Recent AI in medical diagnosis research."
    except Exception as e:
        print("PubMed fetch error:", e)
        return "Using standard clinical AI metrics."

pubmed_context = fetch_latest_pubmed_papers()

prompt = f"""
[SYSTEM: NEXUS_AI_CORE]
[DATE: {today_date}]
[MODE: FUTURISTIC_NEO_UI]

أنت مستشار ذكي برتبة نظام ذكاء اصطناعي مستقبلي. قم بإعداد تقرير يومي منظم ومقسم بدقة إلى **4 أقسام رئيسية** بالأسلوب التالي:

1. 🤖 AI & Machine Learning Trends
2. 🩺 AI in Medicine & Clinical Practice
3. 📈 Digital & Medical Marketing
4. 🔬 PubMed Research Spotlight

بيانات البحث العلمي المسحوبة اليوم من PubMed للقسم الرابع:
{pubmed_context}

شروط التنسيق الفيوتشرستيك الصارمة:
- ابدأ التقرير بالكامل بهذا الشكل السيبراني الثابت في السطر الأول تماماً بدون أي حرف قبله:
⚡ // [CYBER_BRIEFING] - DATE: {today_date}

- ممنوع استخدام علامة الشباك (#) أو النجوم المزدوجة (**) أو الماركداون القديم نهائياً.
- استخدم أقواس سيبرانية وتصميم نقي ومرتب للعين (مثل استخدام ◼ ، ─── ، 『 』 ، ⚡).
- اجعل كل قسم مكوناً من نقاط واضحة ومباشرة ومفصولة بمسافات نظيفة.
- في القسم الرابع (🔬 PubMed Research Spotlight)، نظّم البيانات كالتالي:
  ◼ [Research_Title]: [...]
  ◼ [Core_Idea]: [...]
  ◼ [Clinical_Outcome]: [...]
- الشرح باللغة العربية الفصحى السلسة والمفهومة، مع إبقاء الـ Medical & Technical Terms باللغة الإنجليزية بوضوح.
- اجعل التقرير مكثفاً وعملياً وخالياً من الحشو في حدود 2500 حرف.
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
                generation_config={"temperature": 0.6}
            )
            text = response.text
            
            if "CYBER_BRIEFING" in text:
                text = "⚡ // [CYBER_BRIEFING]" + text.rsplit("CYBER_BRIEFING", 1)[-1]
                
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
        res = requests.post(url, json=payload)
        print("Telegram message response:", res.json())

def clean_text_for_audio(text):
    cleaned = re.sub(r'[#*`_~—\-+=|•⚡//\[\]{}◼───『』1️⃣2️⃣3️⃣4️⃣]', ' ', text)
    return cleaned

async def create_audio(text, filename="briefing.mp3"):
    clean_text = clean_text_for_audio(text)
    if not clean_text.strip():
        clean_text = "تقرير المستشار الذكي اليومي."
    voice = "ar-SA-ZahraNeural"
    communicate = edge_tts.Communicate(clean_text, voice, rate="+2%")
    await communicate.save(filename)

def send_telegram_audio(filename="briefing.mp3"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAudio"
    if not os.path.exists(filename):
        print("Audio file does not exist.")
        return
    with open(filename, "rb") as audio_file:
        files = {"audio": audio_file}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "title": f"Cyber Briefing - {today_date}",
            "performer": "NEXUS AI",
            "caption": "🎧 البودكاست السيبراني اليومي جاهز للاستماع!"
        }
        res = requests.post(url, data=data, files=files)
        print("Audio response:", res.json())

if __name__ == "__main__":
    report_text = generate_report()
    
    # 1. إرسال التقرير المكتوب أولاً وضمان وصوله بنجاح تام
    print("Sending text report...")
    send_telegram_message(report_text)
    
    # 2. محاولة توليد وإرسال الصوت مع حماية كاملة لتجنب إيقاف السكربت لو حدث حظر للشبكة
    try:
        print("Generating futuristic audio briefing...")
        asyncio.run(create_audio(report_text))
        send_telegram_audio()
    except Exception as audio_err:
        print(f"Audio generation skipped gracefully due to network/server restriction: {audio_err}")
