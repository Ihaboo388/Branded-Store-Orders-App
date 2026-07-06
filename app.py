import customtkinter as ctk
import tkinter as tk
import threading
import sys
import re
from bulk_import import bulk_upload_orders

PHARMACY_GREEN  = "#00A651"
DARK_GREEN      = "#006B3A"
LIGHT_GREEN     = "#E8F5E9"
BG_COLOR        = "#F0F7F1"
TEXT_DARK       = "#1A3C2A"
TEXT_MID        = "#4A7A5A"
WHITE           = "#FFFFFF"

class SilentRedirector:
    def __init__(self):
        self.output = ""
    def write(self, string):
        self.output += string
    def flush(self):
        pass
    def clear(self):
        self.output = ""

class PharmacyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ZR Sync | مزامنة الطلبيات")
        self.geometry("520x500")
        self.resizable(True, True)
        ctk.set_appearance_mode("light")
        self.configure(fg_color=BG_COLOR)
        self._build_ui()
        self.silent_out = SilentRedirector()
        self._loader_angle = 0
        self._loader_job = None
        self._msg_job = None

    def _build_ui(self):
        # ── Header Bar ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=PHARMACY_GREEN, corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header, text="✚   ZR Express Sync   ✚",
            font=("Arial", 20, "bold"), text_color=WHITE
        ).pack(expand=True)

        # ── Main Card ───────────────────────────────────────────
        self.card = ctk.CTkFrame(
            self, fg_color=WHITE, corner_radius=18,
            border_width=1, border_color="#B2DFBF"
        )
        self.card.pack(padx=32, pady=24, fill="both", expand=True)

        # Store icon
        ctk.CTkLabel(self.card, text="🏪", font=("Arial", 52)).pack(pady=(22, 4))

        ctk.CTkLabel(
            self.card, text="Branded Store Orders",
            font=("Arial", 21, "bold"), text_color=TEXT_DARK
        ).pack()

        ctk.CTkLabel(
            self.card, text="مزامنة الطلبيات التلقائية مع شركة ZR Express",
            font=("Arial", 12), text_color=TEXT_MID
        ).pack(pady=(4, 0))

        # Divider
        ctk.CTkFrame(self.card, height=1, fg_color="#D0EDD8").pack(fill="x", padx=28, pady=16)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.card, text="النظام جاهز  •  اضغط لبدء المزامنة",
            font=("Arial", 13), text_color=TEXT_MID
        )
        self.status_label.pack(pady=(0, 14))

        # ── Loader (hidden initially) ───────────────────────────
        self.loader_frame = ctk.CTkFrame(self.card, fg_color="transparent")

        self.loader_canvas = tk.Canvas(
            self.loader_frame, width=140, height=140,
            bg=WHITE, highlightthickness=0
        )
        self.loader_canvas.pack()

        self.loader_msg = ctk.CTkLabel(
            self.loader_frame, text="",
            font=("Arial", 12, "italic"), text_color=PHARMACY_GREEN
        )
        self.loader_msg.pack(pady=(6, 0))

        # ── Start button ────────────────────────────────────────
        self.btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.btn_frame.pack(pady=(0, 26))

        self.btn_start = ctk.CTkButton(
            self.btn_frame,
            text="🚀   Upload Orders",
            font=("Arial", 16, "bold"),
            command=self._on_start,
            height=52, width=230, corner_radius=26,
            fg_color=PHARMACY_GREEN, hover_color=DARK_GREEN, text_color=WHITE
        )
        self.btn_start.pack()

    # ── Events ─────────────────────────────────────────────────
    def _on_start(self):
        self.btn_frame.pack_forget()
        self.loader_frame.pack(pady=8)
        self._start_loader()
        self._start_msg_cycle()
        self.status_label.configure(
            text="⏳ جاري معالجة الطلبيات...",
            text_color=PHARMACY_GREEN, font=("Arial", 13, "bold")
        )
        self.silent_out.clear()
        self.old_stdout = sys.stdout
        sys.stdout = self.silent_out
        threading.Thread(
            target=self._run_upload,
            args=("Branded Store Orders", "Orders"),
            daemon=True
        ).start()

    def _run_upload(self, sheet_name, tab_name):
        try:
            bulk_upload_orders(sheet_name, tab_name)
        except Exception as e:
            self.silent_out.write(f"Error: {e}")
        sys.stdout = self.old_stdout
        self.after(0, self._show_results, self.silent_out.output)

    # ── Loader animation ────────────────────────────────────────
    def _start_loader(self):
        self._loader_angle = 0
        self._animate_loader()

    def _animate_loader(self):
        c = self.loader_canvas
        c.delete("all")
        cx, cy, r = 70, 70, 52

        # Track ring
        c.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#C8E6C9", width=11, fill=WHITE)

        # Spinning colored arc
        c.create_arc(
            cx-r, cy-r, cx+r, cy+r,
            start=self._loader_angle, extent=250,
            outline=PHARMACY_GREEN, width=11, style="arc"
        )

        # Inner circle
        ri = 36
        c.create_oval(cx-ri, cy-ri, cx+ri, cy+ri, fill="#F0FFF4", outline="#A5D6A7", width=1)

        # Pharmacy cross in center
        c.create_text(cx, cy, text="✚", font=("Arial", 24, "bold"), fill=PHARMACY_GREEN)

        self._loader_angle = (self._loader_angle + 7) % 360
        self._loader_job = self.after(22, self._animate_loader)

    _MESSAGES = [
        "🔍 فحص الطلبيات الجديدة...",
        "📦 تجهيز ملف الإكسل...",
        "🚀 إرسال إلى شركة التوصيل...",
        "⏳ انتظار استجابة السيرفر...",
        "📊 مزامنة الأسعار والتتبع...",
        "📝 تحديث الشيت...",
        "✅ التحقق من النتائج...",
    ]

    def _start_msg_cycle(self):
        self._msg_idx = 0
        self._cycle_message()

    def _cycle_message(self):
        self.loader_msg.configure(text=self._MESSAGES[self._msg_idx % len(self._MESSAGES)])
        self._msg_idx += 1
        self._msg_job = self.after(1700, self._cycle_message)

    def _stop_loader(self):
        if self._loader_job:
            self.after_cancel(self._loader_job)
            self._loader_job = None
        if self._msg_job:
            self.after_cancel(self._msg_job)
            self._msg_job = None

    # ── Results ─────────────────────────────────────────────────
    def _show_results(self, text):
        self._stop_loader()
        self.loader_frame.pack_forget()
        self.loader_msg.configure(text="")
        self.btn_frame.pack(pady=(0, 26))

        match_success = re.search(r'\((\d+)\s*نجاح', text)
        if match_success:
            count = int(match_success.group(1))
            if count > 0:
                self.status_label.configure(
                    text=f"✅ اكتملت المزامنة!  تم رفع {count} طلبيات بنجاح",
                    text_color=PHARMACY_GREEN, font=("Arial", 14, "bold")
                )
            else:
                self.status_label.configure(
                    text="⚠️ لم يُرفع أي طلبية. راجع الشيت.",
                    text_color="#F59E0B", font=("Arial", 13, "bold")
                )
        elif "لا توجد طلبيات جديدة" in text:
            self.status_label.configure(
                text="✅ الشيت محدث  •  لا توجد طلبيات جديدة",
                text_color=PHARMACY_GREEN, font=("Arial", 13, "bold")
            )
        else:
            self.status_label.configure(
                text="❌ حدث خطأ. تحقق من الإنترنت أو إعدادات الشيت.",
                text_color="#EF4444", font=("Arial", 13, "bold")
            )

if __name__ == "__main__":
    app = PharmacyApp()
    app.mainloop()
