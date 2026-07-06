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

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"] {
    background: #F0F7F1 !important;
    font-family: 'Inter', sans-serif !important;
    padding-top: 0 !important;
}

/* Remove default Streamlit top padding */
[data-testid="block-container"] { padding: 0 !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
header[data-testid="stHeader"] { background: transparent; }

/* ── HEADER ── */
.zr-header {
    background: linear-gradient(135deg, #00A651 0%, #006B3A 100%);
    padding: 28px 20px 22px;
    text-align: center;
    border-radius: 0 0 28px 28px;
    box-shadow: 0 6px 24px rgba(0,166,81,0.25);
    margin-bottom: 24px;
}
.zr-header .cross { font-size: 2rem; letter-spacing: 8px; }
.zr-header h1 {
    color: #fff;
    font-size: clamp(1.3rem, 5vw, 1.8rem);
    font-weight: 800;
    letter-spacing: 0.5px;
    margin: 6px 0 4px;
}
.zr-header p { color: #b2f0ce; font-size: 0.88rem; }

/* ── CARD ── */
.zr-card {
    background: #fff;
    border-radius: 20px;
    border: 1px solid #c8ecd4;
    padding: 28px 20px 24px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,120,60,0.08);
    margin: 0 4px 20px;
}
.zr-card .store-icon { font-size: 3rem; margin-bottom: 10px; }
.zr-card h2 { color: #1A3C2A; font-size: 1.25rem; font-weight: 800; margin-bottom: 6px; }
.zr-card .desc { color: #4A7A5A; font-size: 0.85rem; line-height: 1.55; }
.zr-card .desc b { color: #00A651; }

/* Divider */
.divider { border: none; border-top: 1px solid #e0f0e8; margin: 18px 0; }

/* ── STATS ROW ── */
.stats-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-bottom: 18px;
}
.stat-chip {
    flex: 1;
    background: #F0FFF4;
    border: 1px solid #B2DFBF;
    border-radius: 12px;
    padding: 10px 8px;
    text-align: center;
}
.stat-chip .label { font-size: 0.72rem; color: #4A7A5A; margin-bottom: 2px; }
.stat-chip .val   { font-size: 1.1rem; font-weight: 800; color: #00A651; }

/* ── BUTTON ── */
div.stButton { margin: 0 !important; }
div.stButton > button {
    background: linear-gradient(135deg, #00A651, #006B3A) !important;
    color: #fff !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 16px 0 !important;
    width: 100% !important;
    letter-spacing: 0.4px;
    box-shadow: 0 6px 20px rgba(0,166,81,0.35) !important;
    transition: all 0.2s !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #00C060, #008B4A) !important;
    box-shadow: 0 8px 28px rgba(0,166,81,0.45) !important;
    transform: translateY(-1px);
}
div.stButton > button:active { transform: translateY(0); }

/* ── SPINNER ── */
[data-testid="stSpinner"] > div {
    border-color: #00A651 transparent #00A651 transparent !important;
}
.stSpinner p { color: #00A651 !important; font-weight: 600; }

/* ── BANNERS ── */
.banner {
    border-radius: 14px;
    padding: 16px 20px;
    font-size: 0.95rem;
    font-weight: 600;
    text-align: center;
    margin: 16px 4px 0;
    line-height: 1.5;
}
.banner.success { background:#E8F5E9; color:#1B5E20; border:1.5px solid #81C784; }
.banner.warning { background:#FFFDE7; color:#E65100; border:1.5px solid #FFD54F; }
.banner.error   { background:#FFEBEE; color:#B71C1C; border:1.5px solid #EF9A9A; }

/* ── LOG BOX ── */
.log-section { margin: 20px 4px 0; }
.log-title { color: #1A3C2A; font-weight: 700; font-size: 0.9rem; margin-bottom: 8px; }
.log-box {
    background: #0D1117;
    color: #58D68D;
    border-radius: 14px;
    padding: 16px;
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    line-height: 1.75;
    max-height: 320px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
    border: 1px solid #1E3A2A;
}

/* ── FOOTER ── */
.zr-footer {
    text-align: center;
    color: #8EAF98;
    font-size: 0.75rem;
    padding: 20px 0 32px;
}

footer, #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="zr-header">
    <div class="cross">✚ ✚ ✚</div>
    <h1>ZR Express Sync</h1>
    <p>مزامنة تلقائية للطلبيات مع شركة التوصيل</p>
</div>
""", unsafe_allow_html=True)

# ── Card ─────────────────────────────────────────────────────
st.markdown("""
<div class="zr-card">
    <div class="store-icon">🏪</div>
    <h2>Branded Store Orders</h2>
    <p class="desc">يجلب الطلبيات بحالة <b>Confirmer</b> ويرفعها تلقائياً<br>ويملأ <b>UUID · Tracking · Delivery Price · Return Price</b></p>
    <hr class="divider">
    <div class="stats-row">
        <div class="stat-chip">
            <div class="label">الحالة المستهدفة</div>
            <div class="val">Confirmer</div>
        </div>
        <div class="stat-chip">
            <div class="label">الحالة بعد الرفع</div>
            <div class="val">Action</div>
        </div>
        <div class="stat-chip">
            <div class="label">المنصة</div>
            <div class="val">ZR ✚</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Button ───────────────────────────────────────────────────
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

    # ── Banner ───────────────────────────────────────────────
    match_success = re.search(r'\((\d+)\s*نجاح', output)
    if match_success:
        count = int(match_success.group(1))
        if count > 0:
            st.markdown(
                f'<div class="banner success">✅ اكتملت المزامنة بنجاح!<br>تم رفع <b>{count}</b> طلبيات وتحديث الشيت.</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="banner warning">⚠️ لم يُرفع أي طلبية — تحقق من الشيت.</div>',
                unsafe_allow_html=True
            )
    elif "لا توجد طلبيات جديدة" in output:
        st.markdown(
            '<div class="banner success">✅ الشيت محدث بالكامل<br>لا توجد طلبيات جديدة.</div>',
            unsafe_allow_html=True
        )
    elif output.strip():
        st.markdown(
            '<div class="banner error">❌ حدث خطأ — راجع السجل أدناه.</div>',
            unsafe_allow_html=True
        )

    # ── Log ──────────────────────────────────────────────────
    if output.strip():
        safe_output = output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        st.markdown(f"""
<div class="log-section">
    <div class="log-title">📋 سجل العمليات</div>
    <div class="log-box">{safe_output}</div>
</div>
""", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────
st.markdown('<div class="zr-footer">ZR Express Sync © 2026 — Branded Store</div>', unsafe_allow_html=True)

