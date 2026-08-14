import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse
import base64
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Silk Creators - Live Cocoon Rates",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Function to get sharp image in ORIGINAL rectangular shape (no circle crop)
def get_profile_image():
    for fname in ["arun_magar.jpg", "arun_magar.png", "arun_magar.jpeg"]:
        if os.path.exists(fname):
            with open(fname, "rb") as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                ext = fname.split('.')[-1]
                return f"data:image/{ext};base64,{encoded}"
    return "https://ui-avatars.com/api/?name=Arun+Magar&background=2563EB&color=fff&size=128"

img_src = get_profile_image()
wa_qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://wa.me/919637008151"

# 2. Complete Robust Multilingual Translations Dictionary (I18N)
TEXTS = {
    "English": {
        "app_title": "🌾 Silk Creators - Live Cocoon Rates",
        "app_motto": "Cocooning Dreams, Creating Futures",
        "app_subtitle": "Dedicated to Farmers Service | Live Cocoon Market Rates across India",
        "select_date": "📅 Select Date:",
        "refresh_btn": "🔄 Refresh Data",
        "share_wa": "📲 Share WhatsApp",
        "calc_title": "🧮 Farmer Revenue Estimator (Compare Income Across All Mandis)",
        "calc_sub": "💰 Compare Your Expected Income Across All Mandis",
        "harvest_qty": "Enter your Harvest Weight (in Kg):",
        "calc_info": "Showing total payout comparisons for {qty} Kg of cocoons on {date}.",
        "top_mandis_title": "🏆 Top Highest Paying Mandis Today",
        "top_bv": "⚪ Top 3 BV Markets (Highest Rates)",
        "top_cb": "🟡 Top 3 CB Markets (Highest Rates)",
        "search_label": "🔍 Search Mandi / Market Name:",
        "sec1_title": "📋 SECTION 1: LIVE MARKET TABLES (SIDE-BY-SIDE)",
        "sec2_title": "📊 SECTION 2: MARKET VISUALIZATIONS & PRICE TRENDS",
        "bv_header": "⚪ Bi-Voltine (BV) – ದ್ವಿತಳಿ",
        "cb_header": "🟡 Cross-Breed (CB) – ಮಿಶ್ರತಳಿ",
        "lowest": "Lowest Rate",
        "highest": "Highest Rate",
        "avg": "Average Rate",
        "download_btn": "📥 Download Today's Rates Report (CSV / Excel)",
        "bar_title": "📊 Market Rate Comparison (🔴 Min | 🟢 Max | 🟡 Avg)",
        "line_title": "📈 Day-wise Price Trajectory Trend",
        "line_mandi_select": "🎯 Select Market for Day-wise Price Trajectory:",
        "exp_inc": "Expected Income (Avg)",
        "max_inc": "Max Potential Income",
        "avg_rate": "Avg Rate",
        "mandi_col": "Market Name"
    },
    "Kannada (ಕನ್ನಡ)": {
        "app_title": "🌾 ಸಿಲ್ಕ್ ಕ್ರಿಯೇಟರ್ಸ್ - ರೇಷ್ಮೆ ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು",
        "app_motto": "ರೇಷ್ಮೆ ಮಾರುಕಟ್ಟೆಯ ಕನಸುಗಳಿಗೆ ಹೊಸ ಜೀವ",
        "app_subtitle": "ರೈತರ ಸೇವೆಗೆ ಮೀಸಲಾಗಿದೆ | ಭಾರತದಾದ್ಯಂತ ಲೈವ್ ರೇಷ್ಮೆ ಮಾರುಕಟ್ಟೆ ದರಗಳು",
        "select_date": "📅 ದಿನಾಂಕವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "refresh_btn": "🔄 ನವೀಕರಿಸಿ (Refresh)",
        "share_wa": "📲 WhatsApp ನಲ್ಲಿ ಹಂಚಿಕೊಳ್ಳಿ",
        "calc_title": "🧮 ರೈತರ ಆದಾಯ ಲೆಕ್ಕಾಚಾರ (ಎಲ್ಲಾ ಮಾರುಕಟ್ಟೆಗಳ ಹೋಲಿಕೆ)",
        "calc_sub": "💰 ನಿಮ್ಮ ಒಟ್ಟು ನಿರೀಕ್ಷಿತ ಆದಾಯವನ್ನು ಎಲ್ಲಾ ಮಾರುಕಟ್ಟೆಗಳಲ್ಲಿ ಹೋಲಿಸಿ",
        "harvest_qty": "ನಿಮ್ಮ ರೇಷ್ಮೆ ಗೂಡಿನ ತೂಕವನ್ನು ನಮೂದಿಸಿ (Kg):",
        "calc_info": "{date} ರ ದರಗಳ ಆಧಾರದ ಮೇಲೆ {qty} Kg ಗೂಡಿಗೆ ನಿರೀಕ್ಷಿತ ಆದಾಯದ ಹೋಲಿಕೆ.",
        "top_mandis_title": "🏆 ಇಂದಿನ ಗರಿಷ್ಠ ದರ ನೀಡುವ ಮಾರುಕಟ್ಟೆಗಳು",
        "top_bv": "⚪ ಟಾಪ್ 3 BV ಮಾರುಕಟ್ಟೆಗಳು (ಗರಿಷ್ಠ ದರ)",
        "top_cb": "🟡 ಟಾಪ್ 3 CB ಮಾರುಕಟ್ಟೆಗಳು (ಗರಿಷ್ಠ ದರ)",
        "search_label": "🔍 ಮಾರುಕಟ್ಟೆ ಹೆಸರನ್ನು ಹುಡುಕಿ:",
        "sec1_title": "📋 ವಿಭಾಗ 1: ಲೈವ್ ಮಾರುಕಟ್ಟೆ ಕೋಷ್ಟಕಗಳು",
        "sec2_title": "📊 ವಿಭಾಗ 2: ಮಾರುಕಟ್ಟೆ ನಕ್ಷೆಗಳು ಮತ್ತು ದರ ಟ್ರೆಂಡ್‌ಗಳು",
        "bv_header": "⚪ ಬೈವೋಲ್ಟೈನ್ (BV) – ದ್ವಿತಳಿ",
        "cb_header": "🟡 ಕ್ರಾಸ್-ಬ್ರೀಡ್ (CB) – ಮಿಶ್ರತಳಿ",
        "lowest": "ಕನಿಷ್ಠ ದರ",
        "highest": "ಗರಿಷ್ಠ ದರ",
        "avg": "ಸರಾಸರಿ ದರ",
        "download_btn": "📥 ಇಂದಿನ ದರ ವರದಿಯನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ (CSV/Excel)",
        "bar_title": "📊 ಮಾರುಕಟ್ಟೆ ದರಗಳ ಹೋಲಿಕೆ (🔴 ಕನಿಷ್ಠ | 🟢 ಗರಿಷ್ಠ | 🟡 ಸರಾಸರಿ)",
        "line_title": "📈 ದಿನನಿತ್ಯದ ದರ ಬದಲಾವಣೆ ಟ್ರೆಂಡ್",
        "line_mandi_select": "🎯 ದರ ಟ್ರೆಂಡ್ ನೋಡಲು ಮಾರುಕಟ್ಟೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "exp_inc": "ನಿರೀಕ್ಷಿತ ಆದಾಯ (ಸರಾಸರಿ)",
        "max_inc": "ಗರಿಷ್ಠ ಸಾಮರ್ಥ್ಯದ ಆದಾಯ",
        "avg_rate": "ಸರಾಸರಿ ದರ",
        "mandi_col": "ಮಾರುಕಟ್ಟೆ ಹೆಸರು"
    },
    "Hindi (हिंदी)": {
        "app_title": "🌾 सिल्क क्रिएटर्स - लाइव रेशम बाज़ार भाव",
        "app_motto": "रेशम उद्योग में किसानों का विश्वास",
        "app_subtitle": "किसानों की सेवा में समर्पित | भारतभर के रेशम बाज़ार रेट",
        "select_date": "📅 तिथि चुनें:",
        "refresh_btn": "🔄 ताज़ा करें (Refresh)",
        "share_wa": "📲 WhatsApp पर शेयर करें",
        "calc_title": "🧮 किसान आय कैलकुलेटर (सभी मंडियों की तुलना करें)",
        "calc_sub": "💰 सभी मंडियों में अपनी अनुमानित आय की तुलना करें",
        "harvest_qty": "अपनी रेशम उपज का वजन दर्ज करें (Kg में):",
        "calc_info": "{date} की दरों के आधार पर {qty} Kg उपज के लिए अनुमानित आय तुलना।",
        "top_mandis_title": "🏆 आज की उच्चतम रेट वाली मंडियां",
        "top_bv": "⚪ टॉप 3 BV मंडियां (उच्चतम रेट)",
        "top_cb": "🟡 टॉप 3 CB मंडियां (उच्चतम रेट)",
        "search_label": "🔍 मंडी का नाम खोजें:",
        "sec1_title": "📋 अनुभाग 1: लाइव बाज़ार तालिकाएं (आमने-सामने)",
        "sec2_title": "📊 अनुभाग 2: बाज़ार चार्ट और मूल्य रुझान",
        "bv_header": "⚪ बाई-वोल्टाइन (BV) रेशम",
        "cb_header": "🟡 क्रॉस-ब्रीड (CB) रेशम",
        "lowest": "न्यूनतम दर",
        "highest": "अधिकतम दर",
        "avg": "औसत दर",
        "download_btn": "📥 आज की रिपोर्ट डाउनलोड करें (CSV/Excel)",
        "bar_title": "📊 मंडी रेट तुलना (🔴 न्यूनतम | 🟢 अधिकतम | 🟡 औसत)",
        "line_title": "📈 दैनिक मूल्य रुझान ट्रेंड",
        "line_mandi_select": "🎯 मूल्य रुझान देखने के लिए मंडी चुनें:",
        "exp_inc": "अनुमानित आय (औसत)",
        "max_inc": "अधिकतम संभावित आय",
        "avg_rate": "औसत दर",
        "mandi_col": "मंडी नाम"
    },
    "Telugu (తెలుగు)": {
        "app_title": "🌾 సిల్క్ క్రియేటర్స్ - లైవ్ పట్టు కాయల ధరలు",
        "app_motto": "పట్టు రైతుల అభివృద్ధికి మా కట్టుబాటు",
        "app_subtitle": "రైతుల సేవలో | భారతదేశమంతటా లైవ్ మార్కెట్ ధరలు",
        "select_date": "📅 తేదీని ఎంచుకోండి:",
        "refresh_btn": "🔄 రిఫ్రెష్ (Refresh)",
        "share_wa": "📲 WhatsApp లో షేర్ చేయండి",
        "calc_title": "🧮 రైతు ఆదాయ అంచనా (అన్ని మార్కెట్ల పోలిక)",
        "calc_sub": "💰 అన్ని మార్కెట్లలో మీ అంచనా ఆదాయాన్ని పోల్చండి",
        "harvest_qty": "మీ పట్టు దిగుబడి బరువును ఎంటర్ చేయండి (Kg లలో):",
        "calc_info": "{date} ధరల ఆధారంగా {qty} Kg దిగుబడికి అంచనా ఆదాయం.",
        "top_mandis_title": "🏆 నేటి అత్యధిక ధర కలిగిన మార్కెట్లు",
        "top_bv": "⚪ టాప్ 3 BV మార్కెట్లు (అత్యధిక ధర)",
        "top_cb": "🟡 టాప్ 3 CB మార్కెట్లు (అత్యధిక ధర)",
        "search_label": "🔍 మార్కెట్ పేరును శోధించండి:",
        "sec1_title": "📋 విభాగం 1: లైవ్ మార్కెట్ పట్టికలు",
        "sec2_title": "📊 విభాగం 2: మార్కెట్ విశ్లేషణ మరియు ధరల ధోరణులు",
        "bv_header": "⚪ బై-వోల్టైన్ (BV) రకం",
        "cb_header": "🟡 క్రాస్-బ్రీడ్ (CB) రకం",
        "lowest": "కనీస ధర",
        "highest": "గరిష్ట ధర",
        "avg": "సగటు ధర",
        "download_btn": "📥 నేటి నివేదికను డౌన్‌లోడ్ చేయండి (CSV/Excel)",
        "bar_title": "📊 మార్కెట్ ధరల పోలిక (🔴 కనీస | 🟢 గరిష్ట | 🟡 సగటు)",
        "line_title": "📈 రోజువారీ ధరల మార్పు ట్రెండ్",
        "line_mandi_select": "🎯 ట్రెండ్ చూడటానికి మార్కెట్‌ను ఎంచుకోండి:",
        "exp_inc": "అంచనా ఆదాయం (సగటు)",
        "max_inc": "గరిష్ట సంభావ్య ఆదాయం",
        "avg_rate": "సగటు ధర",
        "mandi_col": "మార్కెట్ పేరు"
    },
    "Marathi (मराठी)": {
        "app_title": "🌾 सिल्क क्रिएटर्स - लाईव्ह रेशीम कोष बाजारभाव",
        "app_motto": "रेशीम उत्पादक शेतकऱ्यांच्या सेवेसाठी",
        "app_subtitle": "शेतकऱ्यांच्या सेवेसाठी | भारतातील थेट बाजारभाव",
        "select_date": "📅 दिनांक निवडा:",
        "refresh_btn": "🔄 ताजे करा (Refresh)",
        "share_wa": "📲 WhatsApp वर शेअर करा",
        "calc_title": "🧮 शेतकरी उत्पन्न कॅल्क्युलेटर (सर्व बाजार समिती तुलना)",
        "calc_sub": "💰 सर्व बाजारांमधील तुमचे अंदाजे उत्पन्न तपासा",
        "harvest_qty": "तुमचे एकूण उत्पन्न वजन प्रविष्ट करा (Kg मध्ये):",
        "calc_info": "{date} च्या दरांनुसार {qty} Kg उत्पन्नाची तुलना.",
        "top_mandis_title": "🏆 आजचे सर्वाधिक भाव देणारे बाजार",
        "top_bv": "⚪ टॉप 3 BV बाजार (सर्वाधिक भाव)",
        "top_cb": "🟡 टॉप 3 CB बाजार (सर्वाधिक भाव)",
        "search_label": "🔍 बाजार समिती नाव शोधा:",
        "sec1_title": "📋 विभाग १: लाईव्ह बाजारभाव तक्ता",
        "sec2_title": "📊 विभाग २: बाजारभाव चार्ट आणि ट्रेंड्स",
        "bv_header": "⚪ बाय-व्होल्टाईन (BV) रेशीम",
        "cb_header": "🟡 क्रॉस-ब्रीड (CB) रेशीम",
        "lowest": "किमान भाव",
        "highest": "कमाल भाव",
        "avg": "सरासरी भाव",
        "download_btn": "📥 आजचा अहवाल डाउनलोड करा (CSV/Excel)",
        "bar_title": "📊 बाजार समिती दर तुलना (🔴 किमान | 🟢 कमाल | 🟡 सरासरी)",
        "line_title": "📈 दैनिक दर बदल ट्रेंड",
        "line_mandi_select": "🎯 दर बदल पाहण्यासाठी बाजार समिती निवडा:",
        "exp_inc": "अंदाजे उत्पन्न (सरासरी)",
        "max_inc": "कमाल संभाव्य उत्पन्न",
        "avg_rate": "सरासरी भाव",
        "mandi_col": "बाजार समिती नाव"
    },
    "Tamil (தமிழ்)": {
        "app_title": "🌾 சில்க் கிரியேட்டர்ஸ் - நேரலை பட்டுக்கூடு சந்தை விலை",
        "app_motto": "பட்டு விவசாயிகளின் முன்னேற்றத்திற்காக",
        "app_subtitle": "விவசாயிகளின் சேவையில் | இந்தியா முழுவதுமான நேரலை விலை",
        "select_date": "📅 தேதியைத் தேர்ந்தெடுக்கவும்:",
        "refresh_btn": "🔄 புதுப்பி (Refresh)",
        "share_wa": "📲 WhatsApp இல் பகிரவும்",
        "calc_title": "🧮 விவசாயி வருமானக் கணக்கீடு (அனைத்து சந்தைகள் ஒப்பீடு)",
        "calc_sub": "💰 அனைத்து சந்தைகளிலும் உங்கள் எதிர்பார்க்கப்படும் வருமானத்தை ஒப்பிடுங்கள்",
        "harvest_qty": "உங்கள் மகசூல் எடையை உள்ளிடவும் (Kg):",
        "calc_info": "{date} தேதியின் விலைகளின் அடிப்படையில் {qty} Kg மகசூலுக்கான வருமான ஒப்பீடு.",
        "top_mandis_title": "🏆 இன்றைய அதிகபட்ச விலை சந்தைகள்",
        "top_bv": "⚪ டாப் 3 BV சந்தைகள் (அதிகபட்ச விலை)",
        "top_cb": "🟡 டாப் 3 CB சந்தைகள் (அதிகபட்ச விலை)",
        "search_label": "🔍 சந்தை பெயரைத் தேடுங்கள்:",
        "sec1_title": "📋 பிரிவு 1: நேரலை சந்தை அட்டவணை",
        "sec2_title": "📊 பிரிவு 2: சந்தை வரைபடங்கள் & விலை மாற்றங்கள்",
        "bv_header": "⚪ பை-வோல்டைன் (BV) ரகம்",
        "cb_header": "🟡 க்ராஸ்-பிரீட் (CB) ரகம்",
        "lowest": "குறைந்தபட்ச விலை",
        "highest": "அதிகபட்ச விலை",
        "avg": "சராசரி விலை",
        "download_btn": "📥 இன்றைய அறிக்கையைப் பதிவிறக்கவும் (CSV/Excel)",
        "bar_title": "📊 சந்தை விலை ஒப்பீடு (🔴 குறைந்தபட்சம் | 🟢 அதிகபட்சம் | 🟡 சராசரி)",
        "line_title": "📈 தினசரி விலை மாற்ற போக்கு",
        "line_mandi_select": "🎯 விலை போக்கைக் காண சந்தையைத் தேர்ந்தெடுக்கவும்:",
        "exp_inc": "எதிர்பார்க்கப்படும் வருமானம் (சராசரி)",
        "max_inc": "அதிகபட்ச சாத்தியமான வருமானம்",
        "avg_rate": "சராசரி விலை",
        "mandi_col": "சந்தை பெயர்"
    }
}

# 3. High-Contrast Readability Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    p, label, span, div {
        color: #0F172A;
        font-weight: 500;
    }

    .section-title {
        font-size: 20px;
        font-weight: 800;
        color: #0F172A !important;
        padding: 8px 12px;
        background: #FFFFFF !important;
        border-left: 5px solid #2563EB;
        border-radius: 4px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .top-mandi-card {
        background: white !important;
        color: #0F172A !important;
        padding: 12px;
        border-radius: 10px;
        border-left: 4px solid #10B981;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 8px;
    }

    div[data-testid="stDataFrame"] {
        background: white !important;
        border-radius: 12px;
        padding: 8px;
        border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Global Language Selection Engine
lang_list = ["English", "Kannada (ಕನ್ನಡ)", "Hindi (हिंदी)", "Telugu (తెలుగు)", "Marathi (मराठी)", "Tamil (தமிழ்)"]
lang_col1, lang_col2 = st.columns([3, 1])

with lang_col2:
    selected_lang = st.selectbox("🌐 Choose Language / ಭಾಷೆ:", lang_list, index=0, key="global_language_selector")

T = TEXTS.get(selected_lang, TEXTS["English"])

# 5. HIGH-CONTRAST EXECUTIVE BLUE HEADER BANNER (ORIGINAL RECTANGULAR PHOTO SHAPE)
header_html = f"""<div style="background: linear-gradient(135deg, #0F2B5C 0%, #1E40AF 50%, #2563EB 100%); padding: 22px; border-radius: 16px; margin-bottom: 25px; box-shadow: 0 8px 16px rgba(15, 43, 92, 0.3);">
<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 15px;">
<div style="display: flex; align-items: center; gap: 12px; background: rgba(255, 255, 255, 0.12); padding: 10px 14px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.25); min-width: 270px;">
<img src="{img_src}" style="height: 80px; width: auto; max-width: 90px; border-radius: 8px; object-fit: contain; border: 2px solid #60A5FA; flex-shrink: 0;" alt="Arun B. Magar" />
<div>
<h3 style="margin:0; font-size: 16px; font-weight: 800; color: #FFFFFF !important; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">ARUN B. MAGAR</h3>
<p style="margin:2px 0; font-size: 11px; color: #FDE047 !important; font-weight: 700;">Rtd. DySP, Maharashtra Police</p>
<p style="margin:1px 0; font-size: 11px; color: #93C5FD !important; font-weight: 600;">Founder, Silk Creators</p>
<p style="margin:2px 0; font-size: 12px;"><a href="https://wa.me/919637008151" target="_blank" style="color: #60A5FA !important; font-weight: 800; text-decoration: none;">📞 +91 9637008151</a></p>
<div style="display: flex; align-items: center; gap: 6px; margin-top: 3px;">
<img src="{wa_qr_url}" style="width: 30px; height: 30px; border-radius: 4px; border: 1px solid white;" alt="QR" />
<span style="font-size: 10px; color: #E0F2FE !important; font-weight: 600;">Scan WhatsApp QR</span>
</div>
</div>
</div>
<div style="text-align: center; flex: 1; min-width: 260px; padding: 4px;">
<h1 style="margin:0; font-size: 24px; font-weight: 900; color: #FFFFFF !important; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{T['app_title']}</h1>
<div style="font-size: 14px; color: #FDE047 !important; font-style: italic; font-weight: 700; margin: 3px 0; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">"{T['app_motto']}"</div>
<p style="margin:0; font-size: 12px; color: #E0F2FE !important; font-weight: 500;">{T['app_subtitle']}</p>
</div>
<div style="background: rgba(255, 255, 255, 0.12); padding: 10px 14px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.25); text-align: center; min-width: 240px;">
<h4 style="margin:0; font-size: 14px; font-weight: 800; color: #FDE047 !important; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">🗺️ All-India Silk Farmers Map</h4>
<div style="font-size: 12px; color: #FFFFFF !important; font-weight: 700; margin: 2px 0;">🌱 12,000+ Mapped Farmers</div>
<div style="font-size: 12px; color: #FFFFFF !important; font-weight: 700; margin-bottom: 4px;">👁️ 9,99,620+ Map Views</div>
<a href="https://www.google.com/maps/d/u/0/viewer?mid=1EvaJdvlAcQf3m4cjrKkwKuzSDoIK8r4&ll=24.84266843022882%2C95.18937613831109&z=3" target="_blank" style="background: #10B981; color: white !important; padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: 800; text-decoration: none; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">📍 Explore Live Farmers Map</a>
</div>
</div>
</div>"""

st.markdown(header_html, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/gviz/tq?tqx=out:csv&sheet=India%20Market%20Rate"

# 6. Data Loader
@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = [str(c).strip() for c in df.columns]
    
    numeric_cols = ['Min', 'Max', 'Avg', 'Lots', 'Qty (kg)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('₹', '').str.replace(',', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Variety' in df.columns:
        df['Variety_Clean'] = df['Variety'].apply(
            lambda x: 'Bi-Voltine (BV)' if any(k in str(x).lower() for k in ['bv', 'bivoltine', 'ದ್ವಿತಳಿ']) 
            else ('Cross-Breed (CB)' if any(k in str(x).lower() for k in ['cb', 'cross', 'ಮಿಶ್ರತಳಿ']) else 'General')
        )

    if 'Date' in df.columns:
        df['Date_Parsed'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        df = df.dropna(subset=['Date_Parsed'])
        df = df.sort_values(by='Date_Parsed', ascending=True)

    return df

try:
    df = load_data()

    # Top Control Bar
    ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])
    with ctrl1:
        available_dates = sorted(df['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox(T['select_date'], available_dates if available_dates else ["Latest"])
    
    with ctrl2:
        st.write("")
        if st.button(T['refresh_btn'], use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Filter Data by Selected Date
    if selected_date != "Latest" and 'Date' in df.columns:
        date_df = df[df['Date'] == selected_date].copy()
    else:
        date_df = df.copy()

    df_bv = date_df[date_df['Variety_Clean'] == 'Bi-Voltine (BV)'].copy()
    df_cb = date_df[date_df['Variety_Clean'] == 'Cross-Breed (CB)'].copy()

    # WhatsApp Sharing
    with ctrl3:
        st.write("")
        bv_avg_str = f"₹{df_bv['Avg'].mean():.0f}" if not df_bv.empty else "N/A"
        cb_avg_str = f"₹{df_cb['Avg'].mean():.0f}" if not df_cb.empty else "N/A"
        
        wa_text = f"🌾 *Silk Creators - Live Cocoon Rates ({selected_date})*\n\n⚪ *BV Avg Rate:* {bv_avg_str}/kg\n🟡 *CB Avg Rate:* {cb_avg_str}/kg\n\nCheck full mandi rates online:\nhttps://cocoon-prices.streamlit.app"
        encoded_wa_text = urllib.parse.quote(wa_text)
        wa_link = f"https://api.whatsapp.com/send?text={encoded_wa_text}"
        
        st.markdown(f"""
            <a href="{wa_link}" target="_blank" style="text-decoration:none;">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:9px; border-radius:8px; font-weight:bold; cursor:pointer;">
                    {T['share_wa']}
                </button>
            </a>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 🧮 FARMER INCOME ESTIMATOR CALCULATOR
    # -------------------------------------------------------------------------
    with st.expander(f"🧮 **{T['calc_title']}**", expanded=True):
        st.subheader(f"💰 {T['calc_sub']}")
        
        col_input, col_info = st.columns([1, 2])
        with col_input:
            farmer_qty = st.number_input(T['harvest_qty'], min_value=1, max_value=10000, value=100, step=10)
        
        with col_info:
            calc_info_text = T['calc_info'].format(qty=farmer_qty, date=selected_date)
            st.info(f"💡 {calc_info_text}")

        # Create Income Comparisons for all Mandis
        calc_df = date_df.copy()
        
        if not calc_df.empty:
            calc_df['Expected Income (Avg)'] = calc_df['Avg'] * farmer_qty
            calc_df['Max Potential Income'] = calc_df['Max'] * farmer_qty
            
            calc_bv = calc_df[calc_df['Variety_Clean'] == 'Bi-Voltine (BV)'].copy()
            calc_cb = calc_df[calc_df['Variety_Clean'] == 'Cross-Breed (CB)'].copy()

            col_calc_bv, col_calc_cb = st.columns(2)

            # BV INCOME TABLE
            with col_calc_bv:
                st.markdown(f"#### {T['bv_header']} ({farmer_qty} Kg)")
                if not calc_bv.empty:
                    disp_bv = calc_bv[['Market Name', 'Avg', 'Max', 'Expected Income (Avg)', 'Max Potential Income']].sort_values(by='Expected Income (Avg)', ascending=False).copy()
                    
                    disp_bv[T['avg_rate']] = disp_bv['Avg'].apply(lambda x: f"₹{x:.0f}/kg" if pd.notnull(x) else "-")
                    disp_bv[T['exp_inc']] = disp_bv['Expected Income (Avg)'].apply(lambda x: f"₹{x:,.0f}" if pd.notnull(x) else "-")
                    disp_bv[T['max_inc']] = disp_bv['Max Potential Income'].apply(lambda x: f"₹{x:,.0f}" if pd.notnull(x) else "-")
                    
                    disp_bv_renamed = disp_bv.rename(columns={'Market Name': T['mandi_col']})
                    st.dataframe(
                        disp_bv_renamed[[T['mandi_col'], T['avg_rate'], T['exp_inc'], T['max_inc']]],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.caption("No BV rate data available.")

            # CB INCOME TABLE
            with col_calc_cb:
                st.markdown(f"#### {T['cb_header']} ({farmer_qty} Kg)")
                if not calc_cb.empty:
                    disp_cb = calc_cb[['Market Name', 'Avg', 'Max', 'Expected Income (Avg)', 'Max Potential Income']].sort_values(by='Expected Income (Avg)', ascending=False).copy()
                    
                    disp_cb[T['avg_rate']] = disp_cb['Avg'].apply(lambda x: f"₹{x:.0f}/kg" if pd.notnull(x) else "-")
                    disp_cb[T['exp_inc']] = disp_cb['Expected Income (Avg)'].apply(lambda x: f"₹{x:,.0f}" if pd.notnull(x) else "-")
                    disp_cb[T['max_inc']] = disp_cb['Max Potential Income'].apply(lambda x: f"₹{x:,.0f}" if pd.notnull(x) else "-")
                    
                    disp_cb_renamed = disp_cb.rename(columns={'Market Name': T['mandi_col']})
                    st.dataframe(
                        disp_cb_renamed[[T['mandi_col'], T['avg_rate'], T['exp_inc'], T['max_inc']]],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.caption("No CB rate data available.")

    # 🏆 HIGHEST PAYING MANDIS TODAY
    st.markdown("---")
    st.markdown(f"### {T['top_mandis_title']}")
    top_col1, top_col2 = st.columns(2)

    with top_col1:
        st.markdown(f"**{T['top_bv']}**")
        if not df_bv.empty:
            top_bv = df_bv.sort_values(by='Max', ascending=False).head(3)
            for idx, row in top_bv.iterrows():
                st.markdown(f"<div class='top-mandi-card'>🥇 <b>{row['Market Name']}</b> — Max: <b>₹{row['Max']:.0f}/kg</b> (Avg: ₹{row['Avg']:.0f})</div>", unsafe_allow_html=True)
        else:
            st.caption("No BV data.")

    with top_col2:
        st.markdown(f"**{T['top_cb']}**")
        if not df_cb.empty:
            top_cb = df_cb.sort_values(by='Max', ascending=False).head(3)
            for idx, row in top_cb.iterrows():
                st.markdown(f"<div class='top-mandi-card'>🥇 <b>{row['Market Name']}</b> — Max: <b>₹{row['Max']:.0f}/kg</b> (Avg: ₹{row['Avg']:.0f})</div>", unsafe_allow_html=True)
        else:
            st.caption("No CB data.")

    # INSTANT MANDI SEARCH BAR
    st.markdown("---")
    search_mandi = st.text_input(T['search_label'], "").strip()

    if search_mandi:
        df_bv = df_bv[df_bv['Market Name'].str.contains(search_mandi, case=False, na=False)]
        df_cb = df_cb[df_cb['Market Name'].str.contains(search_mandi, case=False, na=False)]

    # =========================================================================
    # SECTION 1: LIVE MARKET TABLES (SIDE-BY-SIDE)
    # =========================================================================
    st.markdown(f"<div class='section-title'>{T['sec1_title']}</div>", unsafe_allow_html=True)

    col_tbl_bv, col_tbl_cb = st.columns(2)
    display_cols = ['Date', 'Market Name', 'Lots', 'Qty (kg)', 'Min', 'Max', 'Avg']
    display_cols = [c for c in display_cols if c in df.columns]

    # LEFT: BV TABLE
    with col_tbl_bv:
        st.markdown(f"### {T['bv_header']}")
        if not df_bv.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric(T['lowest'], f"₹{df_bv['Min'].min():.0f}")
            m2.metric(T['highest'], f"₹{df_bv['Max'].max():.0f}")
            m3.metric(T['avg'], f"₹{df_bv['Avg'].mean():.0f}")

            st.dataframe(
                df_bv[display_cols].sort_values(by='Date', ascending=False),
                use_container_width=True,
                hide_index=True,
                height=350
            )
        else:
            st.info("No BV entries found.")

    # RIGHT: CB TABLE
    with col_tbl_cb:
        st.markdown(f"### {T['cb_header']}")
        if not df_cb.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric(T['lowest'], f"₹{df_cb['Min'].min():.0f}")
            c2.metric(T['highest'], f"₹{df_cb['Max'].max():.0f}")
            c3.metric(T['avg'], f"₹{df_cb['Avg'].mean():.0f}")

            st.dataframe(
                df_cb[display_cols].sort_values(by='Date', ascending=False),
                use_container_width=True,
                hide_index=True,
                height=350
            )
        else:
            st.info("No CB entries found.")

    # CSV DOWNLOAD
    st.write("")
    csv_data = date_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=T['download_btn'],
        data=csv_data,
        file_name=f"Silk_Cocoon_Rates_{selected_date}.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown("---")

    # =========================================================================
    # SECTION 2: CHARTS & VISUAL ANALYTICS
    # =========================================================================
    st.markdown(f"<div class='section-title'>{T['sec2_title']}</div>", unsafe_allow_html=True)

    color_map = {'Min': '#EF4444', 'Max': '#10B981', 'Avg': '#F59E0B'}

    # SUB-SECTION 2A: SIDE-BY-SIDE BAR CHARTS
    st.markdown(f"#### {T['bar_title']}")
    col_bar_bv, col_bar_cb = st.columns(2)

    with col_bar_bv:
        if not df_bv.empty:
            melted_bv = pd.melt(df_bv, id_vars=['Market Name'], value_vars=['Min', 'Max', 'Avg'], var_name='Rate_Type', value_name='Price').dropna(subset=['Price'])
            fig_bv = px.bar(melted_bv, x='Market Name', y='Price', color='Rate_Type', barmode='group', text_auto='.0f', title=f"⚪ BV: {selected_date}", labels={'Market Name': 'Mandi', 'Price': 'Rate (₹/kg)'}, color_discrete_map=color_map)
            fig_bv.update_traces(textposition='outside')
            fig_bv.update_layout(xaxis_title="Mandi", yaxis_title="Rate (₹/kg)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=420, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig_bv, use_container_width=True)

    with col_bar_cb:
        if not df_cb.empty:
            melted_cb = pd.melt(df_cb, id_vars=['Market Name'], value_vars=['Min', 'Max', 'Avg'], var_name='Rate_Type', value_name='Price').dropna(subset=['Price'])
            fig_cb = px.bar(melted_cb, x='Market Name', y='Price', color='Rate_Type', barmode='group', text_auto='.0f', title=f"🟡 CB: {selected_date}", labels={'Market Name': 'Mandi', 'Price': 'Rate (₹/kg)'}, color_discrete_map=color_map)
            fig_cb.update_traces(textposition='outside')
            fig_cb.update_layout(xaxis_title="Mandi", yaxis_title="Rate (₹/kg)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=420, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig_cb, use_container_width=True)

    st.markdown("---")

    # SUB-SECTION 2B: DAY-WISE PRICE TREND TRAJECTORY
    st.markdown(f"#### {T['line_title']}")
    available_markets = ["All Mandis (Overall Trend)"] + sorted([str(m) for m in df['Market Name'].dropna().unique() if str(m).strip() != ''])
    selected_market = st.selectbox(T['line_mandi_select'], available_markets)

    if selected_market != "All Mandis (Overall Trend)":
        trend_df = df[df['Market Name'] == selected_market].copy()
    else:
        trend_df = df.copy()

    daily_trend = trend_df.groupby(['Date_Parsed', 'Variety_Clean'])['Avg'].mean().reset_index()
    daily_trend['Date_Formatted'] = daily_trend['Date_Parsed'].astype(str)

    if not daily_trend.empty:
        color_map_line = {'Bi-Voltine (BV)': '#1E3A8A', 'Cross-Breed (CB)': '#D97706', 'General': '#6B7280'}
        fig_line = px.line(daily_trend, x='Date_Formatted', y='Avg', color='Variety_Clean', title=f"Average Daily Rate Trend (₹/kg) — {selected_market}", markers=True, color_discrete_map=color_map_line)
        fig_line.update_xaxes(type='category')
        fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
        fig_line.update_layout(xaxis_title="Date", yaxis_title="Average Rate (₹/kg)", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=380, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")
    st.caption("✅ **Live Sync Active:** Connected to Google Sheets 'India Market Rate' tab.")

except Exception as e:
    st.error(f"⚠️ Error loading sheet data: {e}")
