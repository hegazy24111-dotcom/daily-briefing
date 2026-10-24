import os
import re
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

daily_angles = [
    "Focus on: Agentic AI Workflows, Clinical Decision Support Systems (CDSS) in Emergency/ICU, and Patient Acquisition Funnels.",
    "Focus on: Small Language Models (SLMs) & On-Device AI, AI in Radiology/Pathology Diagnostics, and Medical Personal Branding.",
    "Focus on: Retrieval-Augmented Generation (RAG) Knowledge Bases, Predictive Analytics in Chronic Diseases, and High-Converting Healthcare Content.",
    "Focus on: Multimodal AI Reasoning, AI-Assisted Precision Medicine & Genomics, and Conversion Rate Optimization (CRO) for Clinics.",
    "Focus on: AI Automation & API Integrations, Remote Patient Monitoring (RPM) & Wearable Algorithms, and Patient Retention Strategies.",
    "Focus on: Synthetic Data & Privacy-Preserving AI, AI in Triage & Clinical Workflow Optimization, and Short-Form Video Marketing for Doctors.",
    "Focus on: Autonomous Research Agents, Early Biomarker Detection via Deep Learning, and Marketing Analytics & ROAS in Healthcare."
]

todays_angle = daily_angles[day_of_year % len(daily_angles)]

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
            
            abstract_parts = []
            for elem in article.findall(".//AbstractText"):
                label = elem.attrib.get("Label", "")
                if elem.text:
                    abstract_parts.append(f"[{label}]: {elem.text}" if label else elem.text)
            
            abstract = " ".join(abstract_parts)
            if title and abstract:
                pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{selected_id}/"
                return f"Title: {title}\nURL: {pubmed_url}\nFull Abstract: {abstract[:2500]}"
        
        return "Recent clinical AI diagnostic research."
    except Exception as e:
        print("PubMed fetch error:", e)
        return "Using standard clinical AI metrics."

pubmed_context = fetch_latest_pubmed_papers()

prompt = f"""
أنت مستشار ذكي ومحترف في الذكاء الاصطناعي، التكنولوجيا الطبية، والتسويق الصحي.
قم بإعداد تقرير يومي غني بالمعلومات القيمة والدقيقة، ومصمم باستخدام **Telegram HTML** النظيف والحديث.

زاوية التركيز اليوم لمنع التكرار:
{todays_angle}

بيانات البحث العلمي المسحوبة اليوم من PubMed للقسم الرابع:
{pubmed_context}

شروط التنسيق والكتابة الصارمة جداً:
1. استخدم فقط وسوم HTML المدعومة في تيليجرام التالية: <b> للخط العريض، <code> للكبسولات التقنية، <blockquote> للكروت المدمجة، و <a href="URL"> للروابط.
2. ممنوع تماماً استخدام أي نجوم (**)، أو شبابيك (#)، أو خطوط طويلة (─── أو ━━━)، أو رموز شجرية (├─ أو ┏━━)، أو وسوم مثل <br> أو <p> أو ```html.
3. اكتب بلغة عربية فصحى سلسة وواضحة، مع إبقاء المصطلحات التقنية والطبية باللغة الإنجليزية داخل الجمل.
4. التزم حرفياً بهيكل القالب التالي وابدأ ردك فوراً بسطر العنوان الأول دون أي مقدمات:

<code>NEXUS BRIEFING</code> • <code>{today_date}</code>

<code>01 // AI & MACHINE LEARNING</code>

▫️ <b>[اسم التقنية الأولى بالإنجليزية]</b>
<blockquote>[اشرح آلية عمل التقنية بعمق ووضوح في جملتين، ثم اذكر تطبيقها العملي المباشر]</blockquote>

▫️ <b>[اسم التقنية الثانية بالإنجليزية]</b>
<blockquote>[اشرح آلية عمل التقنية بعمق ووضوح في جملتين، ثم اذكر تطبيقها العملي المباشر]</blockquote>

<code>02 // CLINICAL & MEDICAL AI</code>

▫️ <b>[اسم التقنية أو التطبيق السريري الأول بالإنجليزية]</b>
<blockquote>[اشرح كيف تعمل هذه التقنية طبياً، وما هو أثرها الإكلينيكي المباشر في التشخيص أو العلاج]</blockquote>

▫️ <b>[اسم التقنية أو التطبيق السريري الثاني بالإنجليزية]</b>
<blockquote>[اشرح كيف تعمل هذه التقنية طبياً، وما هو أثرها الإكلينيكي المباشر في التشخيص أو العلاج]</blockquote>

<code>03 //
