import streamlit as st
import sys, io, re
from bulk_import import bulk_upload_orders

st.set_page_config(page_title="ZR Sync | مزامنة الطلبيات", page_icon="✚", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Arial:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="block-container"] {
    background: #F0F7F1 !important;
    padding: 0 !important;
}
[data-testid="block-container"] { padding: 0 0 40px !important; max-width: 560px !important; margin: 0 auto !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
header[data-testid="stHeader"] { display: none !important; }
footer, #MainMenu { visibility: hidden; }

/* Header bar — same green as app.py */
.header {
    background: #00A651;
    padding: 22px 20px;
    text-align: center;
    font-size: 1.25rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: 1px;
}

/* White card */
.card {
    background: #fff;
    border-radius: 18px;
    border: 1px solid #B2DFBF;
    margin: 24px 20px 0;
    padding: 28px 24px 24px;
    text-align: center;
}
.card .icon  { font-size: 3.2rem; margin-bottom: 8px; }
.card h2     { color: #1A3C2A; font-size: 1.25rem; font-weight: 800; margin: 0 0 6px; }
.card .sub   { color: #4A7A5A; font-size: 0.88rem; margin-bottom: 0; }
.divider     { border: none; border-top: 1px solid #D0EDD8; margin: 18px 0; }
.status-idle { color: #4A7A5A; font-size: 0.92rem; text-align: center; }

/* Button */
div.stButton { margin: 0 20px !important; }
div.stButton > button {
    width: 100% !important;
    background: #00A651 !important;
    color: #fff !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 26px !important;
    padding: 16px !important;
    box-shadow: 0 4px 18px rgba(0,166,81,0.35) !important;
    transition: background .2s !important;
}
div.stButton > button:hover  { background: #006B3A !important; }
div.stButton > button:active { transform: scale(0.98) !important; }

/* Processing spinner card */
.proc {
    background: #fff;
    border-radius: 18px;
    border: 1px solid #B2DFBF;
    margin: 16px 20px 0;
    padding: 32px 24px;
    text-align: center;
}
.spinner {
    width: 56px; height: 56px;
    border: 6px solid #C8E6C9;
    border-top: 6px solid #00A651;
    border-radius: 50%;
    margin: 0 auto 16px;
    animation: spin .9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.proc .cross { font-size: 1.6rem; color: #00A651; margin-bottom: 8px; }
.proc h3 { color: #00A651; font-size: 1rem; font-weight: 700; margin-bottom: 4px; }
.proc p  { color: #4A7A5A; font-size: 0.82rem; }

/* Result */
.result {
    background: #fff;
    border-radius: 18px;
    margin: 16px 20px 0;
    padding: 28px 24px;
    text-align: center;
}
.result.ok   { border: 1px solid #B2DFBF; }
.result.warn { border: 1px solid #FCD34D; }
.result.err  { border: 1px solid #FCA5A5; }
.result p { font-size: 1rem; font-weight: 700; margin: 0; }
.result p.ok-text   { color: #00A651; }
.result p.warn-text { color: #F59E0B; }
.result p.err-text  { color: #EF4444; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
st.markdown('<div class="header">✚&nbsp;&nbsp;ZR Express Sync&nbsp;&nbsp;✚</div>', unsafe_allow_html=True)

# ── Card ──────────────────────────────────────────────────────
st.markdown("""
<div class="card">
    <div class="icon">🏪</div>
    <h2>Branded Store Orders</h2>
    <p class="sub">مزامنة الطلبيات التلقائية مع شركة ZR Express</p>
    <hr class="divider">
    <p class="status-idle">النظام جاهز  •  اضغط لبدء المزامنة</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Button & Logic ────────────────────────────────────────────
result_area = st.empty()

if st.button("🚀   Upload Orders"):
    result_area.markdown("""
<div class="proc">
    <div class="spinner"></div>
    <div class="cross">✚</div>
    <h3>⏳ جاري معالجة الطلبيات...</h3>
    <p>يرجى الانتظار</p>
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
<div class="result ok">
    <p class="ok-text">✅ اكتملت المزامنة!  تم رفع {n} طلبيات بنجاح</p>
</div>""", unsafe_allow_html=True)
    elif "لا توجد طلبيات جديدة" in out:
        result_area.markdown("""
<div class="result ok">
    <p class="ok-text">✅ الشيت محدث  •  لا توجد طلبيات جديدة</p>
</div>""", unsafe_allow_html=True)
    elif m:
        result_area.markdown("""
<div class="result warn">
    <p class="warn-text">⚠️ لم يُرفع أي طلبية. راجع الشيت.</p>
</div>""", unsafe_allow_html=True)
    else:
        result_area.markdown("""
<div class="result err">
    <p class="err-text">❌ حدث خطأ. تحقق من الإنترنت أو إعدادات الشيت.</p>
</div>""", unsafe_allow_html=True)
