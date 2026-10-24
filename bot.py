import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import google.generativeai as genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

today_date = datetime.now().strftime("%Y-%m-%d")
day_of_year = datetime.now().timetuple().tm_yday

# زوايا تركيز متغيرة يومياً لضمان عمق المعلومات وعدم تكرار نفس الأفكار التقليدية
daily_angles = [
    "Focus on: Agentic AI Workflows, Clinical Decision Support Systems (CDSS) in Emergency/ICU, and Patient Acquisition Funnels.",
    "Focus on: Small Language Models (SLMs) & On-Device AI, AI in Radiology/Pathology Diagnostics, and Medical Personal Branding.",
    "Focus on: Retrieval-Augmented Generation (RAG) Knowledge Bases, Predictive Analytics in Chronic Diseases, and High-Converting Healthcare Content.",
    "Focus on: Multimodal AI Reasoning, AI-Assisted Precision Medicine & Genomics, and Conversion Rate Optimization (CRO) for Clinics.",
    "Focus on: AI Automation & API Integrations, Remote Patient Monitoring (RPM) & Wearable Algorithms, and Patient Retention Strategies.",
    "Focus on: Synthetic Data & Privacy-Preserving AI, AI in Triage & Clinical Workflow Optimization, and Short-Form Video Marketing for Doctors.",
    "Focus on: Autonomous Coding/Research Agents, Early Biomarker Detection via Deep Learning, and Marketing Analytics & ROAS in Healthcare."
]

todays_angle = daily_angles[day_of_year % len(daily_angles)]

# دالة مطورة لسحب بحث كامل (بما في ذلك النتائج والخلاصة والرابط) من PubMed
def fetch_latest_pubmed_papers():
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": "(artificial intelligence[Title/Abstract] OR machine learning[Title/Abstract] OR deep learning[Title/Abstract]) AND (clinical[Title/Abstract] OR diagnosis[Title/Abstract] OR patient[Title/Abstract]) AND hasabstract",
            "sort": "date",
            "retmax": 5,
            "retmode": "json"
        }
        res = requests.get(search_url, params=search_params, timeout=10).json()
        id_list = res.get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            return "No recent data found. Use advanced clinical AI trial intelligence."

        # اختيار بحث مختلف بناءً على اليوم لضمان التجدد
        selected_id = id_list[day_of_year % len(id_list)]

        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": selected_id,
            "retmode": "xml"
        }
        xml_data = requests.get(fetch_url, params=fetch_params, timeout=10).text
        root = ET.fromstring(xml_data)
        
        for article in root.findall(".//PubmedArticle"):
            title = article.findtext(".//ArticleTitle", default="")
            journal = article.findtext(".//Journal/Title", default="Medical Journal")
            
            abstract_parts = []
            for elem in article.findall(".//AbstractText"):
                label = elem.attrib.get("Label", "")
                if elem.text:
                    abstract_parts.append(f"[{label}]: {elem.text}" if label else elem.text)
            
            abstract = " ".join(abstract_parts)
            if title and abstract:
                pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{selected_id}/"
                return f"Title: {title}\nJournal: {journal}\nURL: {pubmed_url}\nFull Abstract: {abstract[:2500]}"
        
        return "Recent clinical AI diagnostic research."
    except Exception as e:
        print("PubMed fetch error:", e)
        return "Using standard clinical AI metrics."

pubmed_context = fetch_latest_pubmed_papers()

prompt = f"""
[SYSTEM: NEXUS_AI_CORE // V4.0]
[DATE: {today_date}]
[DIRECTIVE: HIGH_DENSITY_INTELLIGENCE_BRIEFING]

أنت الآن النظام الذكي "NEXUS_AI_CORE"، مستشار استراتيجي متقدم في تقنيات الـ AI، التكنولوجيا الطبية، والتسويق الصحي الرقمي.
مهمتك إعداد تقرير استخباراتي يومي فائق الاحترافية، غني بالمعلومات الدقيقة والتطبيقية، ومصمم بواجهة سيبرانية (Futuristic UI) مريحة جداً للعين.

زاوية التركيز الإجبارية لليوم لمنع التكرار السطحي:
{todays_angle}

بيانات البحث العلمي المسحوبة اليوم من PubMed للقسم الرابع:
{pubmed_context}

⚠️ شروط جودة المعلومات (صارمة جداً):
1. ممنوع الكلام الإنشائي أو التعريفات المدرسية المكررة؛ ادخل في صلب التقنية المتقدمة، كيف تعمل برمجياً أو علمياً، وكيف تُطبّق عملياً على أرض الواقع.
2. في كل قسم من الأقسام الثلاثة الأولى، قدّم **نقطتين دسمتين (2 Deep-Dive Points)**؛ كل نقطة مقسمة شجرياً إلى: (الآلية التقنية/العلمية + التطبيق العملي المباشر أو الأثر الرقمي).
3. في قسم PubMed، استخرج النتائج الفعلية والأثر الإكلينيكي من ملخص البحث المرفق بدقة، وضع رابط البحث في النهاية.
4. اكتب بلغة عربية فصحى رصينة وسلسة، مع إبقاء جميع الـ Medical & Technical Terms باللغة الإنجليزية داخل السياق.
5. ممنوع تماماً استخدام رموز الماركداون مثل النجوم (**) أو الشباك (#). التزم حرفياً بقالب التصميم السيبراني أدناه.

⚠️ القالب البصري الإجباري (ابدأ ردك فوراً من السطر الأول في القالب بدون أي كلمة قبله):

⚡ // [CYBER_BRIEFING] — {today_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┏━━ 『 01 // 🤖 AI & MACHINE LEARNING 』
┃
◈ [اسم التقنية أو المنهجية الأولى بالإنجليزية]
├─ 💡 الآلية: [شرح عميق ومكثف لآلية العمل في سطرين]
╰─ 🎯 التطبيق: [مثال تطبيقي محدد أو فائدة عملية مباشرة]

◈ [اسم التقنية أو المنهجية الثانية بالإنجليزية]
├─ 💡 الآلية: [شرح عميق ومكثف لآلية العمل في سطرين]
╰─ 🎯 التطبيق: [مثال تطبيقي محدد أو فائدة عملية مباشرة]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┏━━ 『 02 // 🩺 CLINICAL & MEDICAL AI 』
┃
◈ [اسم التقنية أو التطبيق السريري الأول بالإنجليزية]
├─ 💡 الآلية: [شرح دقيق لكيفية عمل الخوارزمية طبياً وسريرياً]
╰─ 🎯 الأثر الإكلينيكي: [كيف تغير قرار الطبيب أو تحسن نتائج المريض]

◈ [اسم التقنية أو التطبيق السريري الثاني بالإنجليزية]
├─ 💡 الآلية: [شرح دقيق لكيفية عمل الخوارزمية طبياً وسريرياً]
╰─ 🎯 الأثر الإكلينيكي: [كيف تغير قرار الطبيب أو تحسن نتائج المريض]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┏━━ 『 03 // 📈 MEDICAL & DIGITAL MARKETING 』
┃
◈ [اسم الاستراتيجية أو الأداة التسويقية الأولى بالإنجليزية]
├─ 💡 التكتيك: [شرح الفكرة التسويقية وكيفية توظيف الذكاء الاصطناعي فيها]
╰─ 🎯 خطوة تنفيذية: [نصيحة عملية قابلة للتطبيق لرفع الـ ROI أو الـ Conversion]

◈ [اسم الاستراتيجية أو الأداة التسويقية الثانية بالإنجليزية]
├─ 💡 التكتيك: [شرح الفكرة التسويقية وكيفية توظيف الذكاء الاصطناعي فيها]
╰─ 🎯 خطوة تنفيذية: [نصيحة عملية قابلة للتطبيق لرفع الـ ROI أو الـ Conversion]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┏━━ 『 04 // 🔬 PUBMED RESEARCH SPOTLIGHT 』
┃
◼ [Title]: [عنوان البحث باللغة الإنجليزية كما ورد]
├─ 🏛️ [Methodology & Idea]: [شرح فكرة الدراسة والمنهجية والمشكلة التي تحلها بتفصيل واضح]
├─ 📊 [Key Findings]: [أهم النتائج التي توصلت إليها الدراسة من واقع الملخص]
├─ 🩺 [Clinical Takeaway]: [الخلاصة التطبيقية: ماذا يستفيد الطبيب أو الباحث من هذه الورقة؟]
╰─ 🔗 [Source]: [ضع رابط البحث URL المرفق هنا]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
─── 『 STATUS: SYSTEM_OPTIMAL // END_TRANSMISSION 』 ───
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
                generation_config={"temperature": 0.7}
            )
            text = response.text
            
            # قص نظيف بدون تكرار الأقواس
            if "[CYBER_BRIEFING]" in text:
                text = "⚡ // [CYBER_BRIEFING]" + text.rsplit("[CYBER_BRIEFING]", 1)[-1]
                
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
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "disable_web_page_preview": True # لمنع معاينة اللينك الضخمة أسفل الرسالة والحفاظ على نظافة التصميم
        }
        res = requests.post(url, json=payload)
        print("Telegram message response:", res.json())

if __name__ == "__main__":
    report_text = generate_report()
    print("Sending upgraded text report...")
    send_telegram_message(report_text)
