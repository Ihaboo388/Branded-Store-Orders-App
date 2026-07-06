import streamlit as st
import sys
import io
import re

from bulk_import import bulk_upload_orders

st.set_page_config(page_title="ZR Sync", page_icon="✚", layout="centered")

# ════════════════════════════════════════════════════════════
#  CSS — Dark Premium Pharmacy Theme
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

@property --angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"] {
    background: #060e08 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0 !important;
    color: #e0f0e8 !important;
}
[data-testid="stVerticalBlock"] { gap: 0 !important; }
header[data-testid="stHeader"]  { background: transparent !important; }
footer, #MainMenu                { visibility: hidden; }
section[data-testid="stSidebar"]{ display: none; }

/* ── HEADER ─────────────────────────────────────────────── */
.zr-header {
    background: linear-gradient(160deg, #00A651 0%, #003D20 100%);
    padding: 32px 20px 28px;
    text-align: center;
    border-radius: 0 0 36px 36px;
    box-shadow: 0 12px 40px rgba(0,166,81,0.35), 0 0 0 1px rgba(0,255,136,0.1);
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.zr-header::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% -20%, rgba(0,255,136,0.18) 0%, transparent 65%);
    pointer-events: none;
}
.zr-header .cross {
    font-size: 1.5rem;
    letter-spacing: 10px;
    color: rgba(255,255,255,0.55);
    margin-bottom: 8px;
}
.zr-header h1 {
    color: #fff !important;
    font-size: clamp(1.4rem, 6vw, 2rem);
    font-weight: 900;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 16px rgba(0,255,136,0.35);
    margin-bottom: 6px;
}
.zr-header p { color: rgba(255,255,255,0.65); font-size: 0.88rem; font-weight: 300; }

/* ── GLASS CARD ─────────────────────────────────────────── */
.zr-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0,166,81,0.25);
    border-radius: 24px;
    padding: 28px 20px 24px;
    text-align: center;
    margin: 0 6px 24px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.07);
}
.zr-card .store-icon { font-size: 3.2rem; margin-bottom: 12px; filter: drop-shadow(0 0 12px rgba(0,255,136,0.5)); }
.zr-card h2 {
    color: #fff;
    font-size: 1.3rem;
    font-weight: 800;
    margin-bottom: 8px;
    letter-spacing: -0.3px;
}
.zr-card .desc { color: rgba(180,220,195,0.8); font-size: 0.84rem; line-height: 1.6; }
.zr-card .desc b { color: #00ff88; }

/* Divider */
.divider { border: none; border-top: 1px solid rgba(0,166,81,0.2); margin: 18px 0; }

/* Stats chips */
.stats-row { display: flex; gap: 8px; justify-content: center; margin-bottom: 4px; }
.stat-chip {
    flex: 1;
    background: rgba(0,166,81,0.1);
    border: 1px solid rgba(0,166,81,0.2);
    border-radius: 14px;
    padding: 10px 6px;
}
.stat-chip .label { font-size: 0.68rem; color: rgba(150,200,170,0.7); margin-bottom: 3px; }
.stat-chip .val   { font-size: 0.95rem; font-weight: 800; color: #00ff88; }

/* ── BUTTON ─────────────────────────────────────────────── */
div.stButton { margin: 0 6px !important; }
div.stButton > button {
    background: linear-gradient(135deg, #00A651 0%, #00CC66 50%, #00A651 100%) !important;
    background-size: 200% 200% !important;
    color: #fff !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 18px 0 !important;
    width: 100% !important;
    letter-spacing: 0.3px;
    box-shadow:
        0 0 0 0 rgba(0,255,136,0),
        0 8px 30px rgba(0,166,81,0.5),
        inset 0 1px 0 rgba(255,255,255,0.25) !important;
    transition: all 0.3s ease !important;
    animation: btn-breathe 3s ease-in-out infinite;
    position: relative !important;
}
@keyframes btn-breathe {
    0%, 100% { box-shadow: 0 0 20px rgba(0,166,81,0.4), 0 8px 30px rgba(0,166,81,0.3), inset 0 1px 0 rgba(255,255,255,0.2); }
    50%       { box-shadow: 0 0 40px rgba(0,255,136,0.6), 0 8px 40px rgba(0,166,81,0.5), inset 0 1px 0 rgba(255,255,255,0.2); }
}
div.stButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 0 50px rgba(0,255,136,0.7), 0 12px 40px rgba(0,166,81,0.6) !important;
    animation: none !important;
}
div.stButton > button:active { transform: translateY(0) scale(0.99) !important; }

/* ── PROCESSING BOX ─────────────────────────────────────── */
.proc-wrapper {
    position: relative;
    border-radius: 24px;
    padding: 3px;
    margin: 8px 6px;
    background: conic-gradient(from var(--angle), #003D20, #00ff88, #00A651, #00ff88, #003D20);
    animation: spin-border 2s linear infinite;
}
@keyframes spin-border { to { --angle: 360deg; } }

.proc-inner {
    background: #0a1a10;
    border-radius: 22px;
    padding: 32px 20px;
    text-align: center;
}
.proc-spinner {
    width: 56px; height: 56px;
    border-radius: 50%;
    margin: 0 auto 16px;
    background: conic-gradient(from var(--angle), transparent 60%, #00ff88 100%);
    animation: spin-border 1s linear infinite;
    position: relative;
}
.proc-spinner::after {
    content: '';
    position: absolute;
    inset: 6px;
    background: #0a1a10;
    border-radius: 50%;
}
.proc-title { color: #00ff88; font-size: 1.05rem; font-weight: 700; margin-bottom: 6px; }
.proc-sub   { color: rgba(150,200,170,0.6); font-size: 0.82rem; }

/* ── RESULT CARDS ─────────────────────────────────────────── */
.result-card {
    border-radius: 24px;
    padding: 32px 20px;
    text-align: center;
    margin: 8px 6px 0;
    position: relative;
    overflow: hidden;
}
.result-card::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(0,255,136,0.15), transparent 65%);
    pointer-events: none;
}
.result-card.success {
    background: rgba(0,166,81,0.12);
    border: 1px solid rgba(0,255,136,0.3);
    box-shadow: 0 0 40px rgba(0,166,81,0.2);
}
.result-card.warning {
    background: rgba(255,160,0,0.1);
    border: 1px solid rgba(255,200,0,0.3);
}
.result-card.error {
    background: rgba(200,30,30,0.1);
    border: 1px solid rgba(255,80,80,0.25);
}
.result-icon  { font-size: 2.8rem; margin-bottom: 10px; }
.result-title { font-size: 1.1rem; font-weight: 800; color: #fff; margin-bottom: 10px; }
.result-count {
    font-size: 5rem;
    font-weight: 900;
    color: #00ff88;
    line-height: 1;
    margin: 6px 0 4px;
    text-shadow: 0 0 30px rgba(0,255,136,0.6);
}
.result-label { font-size: 0.85rem; color: rgba(150,200,170,0.7); }

/* ── FOOTER ─────────────────────────────────────────────── */
.zr-footer {
    text-align: center;
    color: rgba(100,150,120,0.4);
    font-size: 0.72rem;
    padding: 24px 0 36px;
}
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
    <p class="desc">يجلب الطلبيات بحالة <b>Confirmer</b> ويرفعها تلقائياً<br>مع تحديث <b>UUID · Tracking · Delivery · Return</b></p>
    <hr class="divider">
    <div class="stats-row">
        <div class="stat-chip"><div class="label">تبحث عن</div><div class="val">Confirmer</div></div>
        <div class="stat-chip"><div class="label">تحوّل إلى</div><div class="val">Action</div></div>
        <div class="stat-chip"><div class="label">المنصة</div><div class="val">ZR ✚</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Button & Logic ───────────────────────────────────────────
result_area = st.empty()

if st.button("🚀   Upload Orders"):
    result_area.markdown("""
<div class="proc-wrapper">
    <div class="proc-inner">
        <div class="proc-spinner"></div>
        <div class="proc-title">⏳ جاري معالجة الطلبيات...</div>
        <div class="proc-sub">يرجى الانتظار، قد تستغرق العملية بضع دقائق</div>
    </div>
</div>
""", unsafe_allow_html=True)

    output_buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output_buf
    try:
        bulk_upload_orders("Branded Store Orders", "Orders")
    except Exception as e:
        print(f"ERROR:{e}")
    finally:
        sys.stdout = old_stdout

    output = output_buf.getvalue()
    match_success = re.search(r'\((\d+)\s*نجاح', output)

    if match_success:
        count = int(match_success.group(1))
        if count > 0:
            result_area.markdown(f"""
<div class="result-card success">
    <div class="result-icon">✅</div>
    <div class="result-title">تمت العملية بنجاح!</div>
    <div class="result-count">{count}</div>
    <div class="result-label">طلبية تم رفعها وتحديث الشيت بالكامل</div>
</div>""", unsafe_allow_html=True)
        else:
            result_area.markdown("""
<div class="result-card warning">
    <div class="result-icon">⚠️</div>
    <div class="result-title">لم يُرفع أي طلبية</div>
    <div class="result-label">تحقق من وجود طلبيات بحالة Confirmer</div>
</div>""", unsafe_allow_html=True)
    elif "لا توجد طلبيات جديدة" in output:
        result_area.markdown("""
<div class="result-card success">
    <div class="result-icon">✅</div>
    <div class="result-title">الشيت محدث بالكامل</div>
    <div class="result-label">لا توجد طلبيات جديدة للرفع</div>
</div>""", unsafe_allow_html=True)
    else:
        result_area.markdown("""
<div class="result-card error">
    <div class="result-icon">❌</div>
    <div class="result-title">حدث خطأ</div>
    <div class="result-label">تحقق من اتصال الإنترنت أو إعدادات الشيت</div>
</div>""", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────
st.markdown('<div class="zr-footer">ZR Express Sync © 2026 — Branded Store</div>', unsafe_allow_html=True)

