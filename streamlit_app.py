import streamlit as st
import sys, io, re
from bulk_import import bulk_upload_orders

st.set_page_config(page_title="ZR Sync | Premium", page_icon="✨", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="block-container"] {
    background-color: #F8FAFC !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] { padding-top: 0 !important; }
[data-testid="block-container"] { padding: 1rem 1.2rem 3rem !important; max-width: 480px !important; margin: 0 auto !important; }
header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stDecoration"], [data-testid="stToolbar"] { display: none !important; }

.app-card {
    background: #FFFFFF; border-radius: 28px; padding: 40px 24px;
    box-shadow: 0 12px 40px -12px rgba(0,0,0,0.08); border: 1px solid #F1F5F9;
    text-align: center; margin-bottom: 12px;
}
.icon-wrapper {
    width: 72px; height: 72px; background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
    border-radius: 22px; display: flex; align-items: center; justify-content: center;
    font-size: 32px; margin: 0 auto 24px; box-shadow: 0 8px 16px -4px rgba(16, 185, 129, 0.2);
}
.title { color: #0F172A; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 10px; }
.subtitle { color: #64748B; font-size: 0.95rem; font-weight: 500; line-height: 1.6; margin-bottom: 28px; }
.badge {
    display: inline-flex; align-items: center; gap: 8px; background: #F8FAFC;
    padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; color: #475569;
    border: 1px solid #E2E8F0;
}
.badge .dot { width: 8px; height: 8px; background: #10B981; border-radius: 50%; box-shadow: 0 0 0 3px #D1FAE5; animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.4); } 70% { box-shadow: 0 0 0 6px rgba(16,185,129,0); } 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); } }

div.stButton { margin-top: 20px !important; }
div.stButton > button {
    width: 100% !important; background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    color: #FFFFFF !important; font-size: 1.1rem !important; font-weight: 700 !important;
    padding: 18px 20px !important; border: none !important; border-radius: 20px !important;
    box-shadow: 0 12px 24px -8px rgba(16, 185, 129, 0.5) !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    display: block !important; text-align: center !important;
}
div.stButton > button:hover { transform: translateY(-3px) !important; box-shadow: 0 16px 32px -8px rgba(16, 185, 129, 0.6) !important; }
div.stButton > button:active { transform: translateY(0) !important; box-shadow: 0 4px 12px -4px rgba(16, 185, 129, 0.5) !important; }

.fb-card { border-radius: 24px; padding: 32px 24px; text-align: center; animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; margin-top: 24px; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

.fb-loader { background: #FFFFFF; border: 1px solid #E2E8F0; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.05); }
.spinner { width: 56px; height: 56px; border: 4px solid #F1F5F9; border-top: 4px solid #10B981; border-radius: 50%; margin: 0 auto 24px; animation: spin 1s cubic-bezier(0.5, 0.1, 0.4, 0.9) infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.fb-success { background: #FFFFFF; border: 2px solid #10B981; box-shadow: 0 12px 32px -12px rgba(16,185,129,0.25); }
.fb-warning { background: #FFFFFF; border: 2px solid #F59E0B; box-shadow: 0 12px 32px -12px rgba(245,158,11,0.25); }
.fb-error { background: #FFFFFF; border: 2px solid #EF4444; box-shadow: 0 12px 32px -12px rgba(239,68,68,0.25); }

.fb-icon { font-size: 40px; margin-bottom: 16px; }
.fb-title { font-size: 1.2rem; font-weight: 800; margin-bottom: 8px; color: #0F172A; }
.fb-text { color: #64748B; font-size: 0.95rem; font-weight: 500; line-height: 1.5; }
.fb-count { font-size: 3.5rem; font-weight: 900; color: #10B981; line-height: 1; margin: 12px 0 16px; letter-spacing: -1.5px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-card">
    <div class="icon-wrapper">📦</div>
    <div class="title">Branded Store Orders</div>
    <div class="subtitle">مزامنة الطلبيات التلقائية مع شركة التوصيل. سريع، آمن، وموثوق.</div>
    <div class="badge">
        <div class="dot"></div>
        النظام جاهز
    </div>
</div>
""", unsafe_allow_html=True)

result_area = st.empty()

if st.button("🚀 بدء المزامنة الآن"):
    result_area.markdown("""
    <div class="fb-card fb-loader">
        <div class="spinner"></div>
        <div class="fb-title">جاري معالجة الطلبيات...</div>
        <div class="fb-text">يرجى الانتظار بينما نقوم بمزامنة بياناتك بأمان.</div>
    </div>
    """, unsafe_allow_html=True)

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
            <div class="fb-icon">✨</div>
            <div class="fb-title">تمت المزامنة بنجاح!</div>
            <div class="fb-count">{n}</div>
            <div class="fb-text">طلبية تم رفعها وتحديث الشيت بالكامل.</div>
        </div>""", unsafe_allow_html=True)
    elif "لا توجد طلبيات جديدة" in out:
        result_area.markdown("""
        <div class="fb-card fb-success">
            <div class="fb-icon">✅</div>
            <div class="fb-title">الشيت محدث بالكامل</div>
            <div class="fb-text">لا توجد طلبيات جديدة تحتاج إلى المزامنة.</div>
        </div>""", unsafe_allow_html=True)
    elif m:
        result_area.markdown("""
        <div class="fb-card fb-warning">
            <div class="fb-icon">⚠️</div>
            <div class="fb-title">لم يتم رفع أي طلبية</div>
            <div class="fb-text">يرجى التأكد من وجود طلبيات بحالة Confirmer في الشيت.</div>
        </div>""", unsafe_allow_html=True)
    else:
        result_area.markdown("""
        <div class="fb-card fb-error">
            <div class="fb-icon">❌</div>
            <div class="fb-title">فشلت المزامنة</div>
            <div class="fb-text">حدث خطأ ما. يرجى التحقق من اتصال الإنترنت والإعدادات.</div>
        </div>""", unsafe_allow_html=True)
