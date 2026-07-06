import streamlit as st
import sys, io, re
from bulk_import import bulk_upload_orders

st.set_page_config(page_title="ZR Sync", page_icon="✚", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

* { font-family: 'Cairo', sans-serif !important; box-sizing: border-box; }

header[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stDecoration"], [data-testid="stToolbar"],
[data-testid="stStatusWidget"] { display: none !important; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #F0F7F1 !important;
    padding: 0 !important; margin: 0 !important;
}

[data-testid="block-container"] {
    padding: 0 0 40px 0 !important;
    max-width: 520px !important;
    margin: 0 auto !important;
}

/* Header bar */
.header-bar {
    background-color: #00A651;
    padding: 20px;
    text-align: center;
    color: #FFFFFF;
    font-size: 1.25rem;
    font-weight: 900;
    letter-spacing: 1px;
    margin-bottom: 20px;
}

/* Main card */
.main-card {
    background: #FFFFFF;
    border-radius: 18px;
    border: 1px solid #B2DFBF;
    padding: 28px 24px 28px;
    margin: 0 16px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,166,81,0.08);
}

.store-icon { font-size: 52px; display: block; margin-bottom: 8px; line-height: 1.2; }
.store-title { color: #1A3C2A; font-size: 1.35rem; font-weight: 900; margin: 0 0 6px; }
.store-sub   { color: #4A7A5A; font-size: 0.9rem; font-weight: 600; margin: 0; }
.divider     { height: 1px; background: #D0EDD8; margin: 18px 8px; }
.status-text { color: #4A7A5A; font-size: 0.9rem; font-weight: 600; margin: 0; }

/* Center the button */
div.stButton {
    display: flex !important;
    justify-content: center !important;
    margin-top: 20px !important;
    padding: 0 16px !important;
}
div.stButton > button {
    background-color: #00A651 !important;
    color: #FFFFFF !important;
    font-family: 'Cairo', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    padding: 14px 48px !important;
    border: none !important;
    border-radius: 30px !important;
    min-width: 220px !important;
    width: auto !important;
    box-shadow: 0 6px 20px rgba(0,166,81,0.4) !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
    letter-spacing: 0.5px !important;
}
div.stButton > button:hover {
    background-color: #006B3A !important;
    box-shadow: 0 8px 26px rgba(0,166,81,0.5) !important;
    transform: translateY(-2px) !important;
}
div.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 3px 10px rgba(0,166,81,0.3) !important;
}

/* Feedback cards */
.fb-card {
    border-radius: 14px;
    padding: 24px 20px;
    text-align: center;
    margin: 16px 16px 0;
    animation: fadeIn 0.4s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.fb-loader  { background: #F9FFF9; border: 1px solid #B2DFBF; }
.fb-success { background: #F0FFF4; border: 2px solid #00A651; }
.fb-warning { background: #FFFBF0; border: 2px solid #F59E0B; }
.fb-error   { background: #FFF5F5; border: 2px solid #EF4444; }

.spinner {
    width: 50px; height: 50px;
    border: 5px solid #C8E6C9;
    border-top: 5px solid #00A651;
    border-radius: 50%;
    margin: 0 auto 16px;
    animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.fb-title { font-size: 1rem; font-weight: 800; color: #1A3C2A; margin-bottom: 6px; }
.fb-text  { font-size: 0.88rem; color: #4A7A5A; font-weight: 600; margin: 0; }
.fb-count { font-size: 3rem; font-weight: 900; color: #00A651; line-height: 1.1; margin: 8px 0 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-bar">✚&nbsp;&nbsp;&nbsp;ZR Express Sync&nbsp;&nbsp;&nbsp;✚</div>
<div class="main-card">
    <span class="store-icon">🏪</span>
    <div class="store-title">Branded Store Orders</div>
    <div class="store-sub">مزامنة الطلبيات التلقائية مع شركة ZR Express</div>
    <div class="divider"></div>
    <div class="status-text">النظام جاهز &nbsp;•&nbsp; اضغط لبدء المزامنة</div>
</div>
""", unsafe_allow_html=True)

result_area = st.empty()

if st.button("🚀   Upload Orders"):
    result_area.markdown("""
    <div class="fb-card fb-loader">
        <div class="spinner"></div>
        <div class="fb-title">⏳ جاري معالجة الطلبيات...</div>
        <div class="fb-text">يرجى الانتظار، جاري مزامنة بياناتك بأمان.</div>
    </div>""", unsafe_allow_html=True)

    buf = io.StringIO()
    sys.stdout = buf
    try:
        bulk_upload_orders("Branded Store Orders", "Orders")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sys.stdout = sys.__stdout__

    out = buf.getvalue()
    m = re.search(r'\((\d+)\s*نجاح', out)

    if m and int(m.group(1)) > 0:
        n = int(m.group(1))
        result_area.markdown(f"""
        <div class="fb-card fb-success">
            <div class="fb-title">✅ اكتملت المزامنة!</div>
            <div class="fb-count">{n}</div>
            <div class="fb-text">طلبية تم رفعها وتحديث الشيت بالكامل.</div>
        </div>""", unsafe_allow_html=True)
    elif "لا توجد طلبيات جديدة" in out:
        result_area.markdown("""
        <div class="fb-card fb-success">
            <div class="fb-title">✅ الشيت محدث بالكامل</div>
            <div class="fb-text">لا توجد طلبيات جديدة تحتاج إلى المزامنة.</div>
        </div>""", unsafe_allow_html=True)
    elif m:
        result_area.markdown("""
        <div class="fb-card fb-warning">
            <div class="fb-title">⚠️ لم يتم رفع أي طلبية</div>
            <div class="fb-text">تأكد من وجود طلبيات بحالة Confirmer في الشيت.</div>
        </div>""", unsafe_allow_html=True)
    else:
        result_area.markdown("""
        <div class="fb-card fb-error">
            <div class="fb-title">❌ فشلت المزامنة</div>
            <div class="fb-text">حدث خطأ. تحقق من الاتصال بالإنترنت والإعدادات.</div>
        </div>""", unsafe_allow_html=True)
