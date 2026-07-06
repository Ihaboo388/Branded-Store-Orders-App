import streamlit as st
import sys
import io
import re

from bulk_import import bulk_upload_orders

# ── Page Config ─────────────────────────────────────────────
st.set_page_config(
    page_title="ZR Sync | Upload Orders",
    page_icon="✚",
    layout="centered",
)

# ── Pharmacy Green CSS ───────────────────────────────────────
st.markdown("""
<style>
    :root {
        --green:  #00A651;
        --dark:   #006B3A;
        --light:  #E8F5E9;
        --bg:     #F0F7F1;
        --text:   #1A3C2A;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg) !important;
    }

    /* Header */
    .zr-header {
        background: var(--green);
        border-radius: 14px;
        padding: 20px 24px;
        text-align: center;
        margin-bottom: 24px;
    }
    .zr-header h1 {
        color: white !important;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 1px;
    }
    .zr-header p {
        color: #d0f0e0;
        margin: 6px 0 0;
        font-size: 0.95rem;
    }

    /* Card */
    .zr-card {
        background: white;
        border: 1px solid #B2DFBF;
        border-radius: 16px;
        padding: 32px 36px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,166,81,0.08);
    }

    .zr-icon { font-size: 3.5rem; margin-bottom: 8px; }

    .zr-card h2 {
        color: var(--text);
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 0 6px;
    }
    .zr-card .sub {
        color: #4A7A5A;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }

    /* Streamlit button override */
    div.stButton > button {
        background: var(--green) !important;
        color: white !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        border-radius: 30px !important;
        border: none !important;
        padding: 14px 50px !important;
        letter-spacing: 0.5px;
        transition: background 0.2s;
        width: 100%;
    }
    div.stButton > button:hover {
        background: var(--dark) !important;
    }

    /* Log box */
    .log-box {
        background: #0D1117;
        color: #58D68D;
        border-radius: 10px;
        padding: 16px 20px;
        font-family: monospace;
        font-size: 0.82rem;
        line-height: 1.7;
        max-height: 340px;
        overflow-y: auto;
        text-align: left;
        white-space: pre-wrap;
        word-break: break-all;
    }

    /* Success / Error banners */
    .banner {
        border-radius: 10px;
        padding: 16px 20px;
        font-size: 1rem;
        font-weight: 600;
        text-align: center;
        margin-top: 16px;
    }
    .banner.success { background:#E8F5E9; color:#1B5E20; border:1px solid #A5D6A7; }
    .banner.warning  { background:#FFFDE7; color:#F57F17; border:1px solid #FFF176; }
    .banner.error    { background:#FFEBEE; color:#B71C1C; border:1px solid #EF9A9A; }

    /* Hide Streamlit default footer */
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="zr-header">
    <h1>✚ &nbsp; ZR Express Sync &nbsp; ✚</h1>
    <p>مزامنة تلقائية للطلبيات مع شركة التوصيل</p>
</div>
""", unsafe_allow_html=True)

# ── Card ─────────────────────────────────────────────────────
st.markdown("""
<div class="zr-card">
    <div class="zr-icon">🏪</div>
    <h2>Branded Store Orders</h2>
    <p class="sub">يجلب الطلبيات بحالة <b>Confirmer</b> ويرفعها تلقائياً إلى ZR Express</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Button & Logic ───────────────────────────────────────────
if st.button("🚀   Upload Orders"):
    output_buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output_buf

    with st.spinner("⏳ جاري معالجة الطلبيات... يرجى الانتظار"):
        try:
            bulk_upload_orders("Branded Store Orders", "Orders")
        except Exception as e:
            print(f"[❌] خطأ غير متوقع: {e}")
        finally:
            sys.stdout = old_stdout

    output = output_buf.getvalue()

    # ── Results banner ──────────────────────────────────────
    match_success = re.search(r'\((\d+)\s*نجاح', output)
    if match_success:
        count = int(match_success.group(1))
        if count > 0:
            st.markdown(
                f'<div class="banner success">✅ اكتملت المزامنة بنجاح! تم رفع {count} طلبيات.</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="banner warning">⚠️ لم يُرفع أي طلبية. تحقق من الشيت.</div>',
                unsafe_allow_html=True
            )
    elif "لا توجد طلبيات جديدة" in output:
        st.markdown(
            '<div class="banner success">✅ الشيت محدث بالكامل — لا توجد طلبيات جديدة.</div>',
            unsafe_allow_html=True
        )
    elif output.strip():
        st.markdown(
            '<div class="banner error">❌ حدث خطأ. راجع السجل أدناه.</div>',
            unsafe_allow_html=True
        )

    # ── Log output ──────────────────────────────────────────
    if output.strip():
        st.markdown("<br><b>📋 سجل العمليات:</b>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="log-box">{output.replace("<","&lt;").replace(">","&gt;")}</div>',
            unsafe_allow_html=True
        )
