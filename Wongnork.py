"""
WONGNORK Authentication & Queue Management UI
=============================================
Run:  python wongnork.py
Needs: Python 3 and tkintermapview
Install: pip install tkintermapview

Demo account: demo@wongnork.com / demo123
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
import json
import os
import threading
import math
import datetime

# ─────────────────────────────────────────────
#  IMPORT MAP LIBRARY
# ─────────────────────────────────────────────
try:
    import tkintermapview
    HAS_MAP = True
except ImportError:
    HAS_MAP = False

# ─────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────
C = {
    "bg":      "#ECECEC",
    "navy":    "#23364A",
    "brown":   "#A46A4A",
    "green":   "#1FA97A",
    "green2":  "#156b50",
    "white":   "#FFFFFF",
    "inp_bg":  "#F3F4F6",
    "border":  "#E0E2E8",
    "muted":   "#8A93A2",
    "error":   "#E05555",
    "shadow":  "#C8CDD5",
    "gold":    "#FFD700" 
}

# ─────────────────────────────────────────────
#  RESTAURANT DATA (EXACT Coordinates in Khon Kaen)
# ─────────────────────────────────────────────
RESTAURANT_DATA = {
    "สุกี้ตี๋น้อย (สาขาตลาดอู้ฟู่)": {
        "coords": (16.412581835185925, 102.8156580139527), 
        "desc": "บุฟเฟต์สุกี้ยากี้ / ชาบู ยอดฮิต (ตั้งอยู่ในตลาดอู้ฟู่ ริมถนนมิตรภาพ)", 
        "hours": "11:00 - 05:00"
    },
    "สุกี้ตี๋น้อย (สาขาโลตัส ขอนแก่น 2)": {
        "coords": (16.494814100794112, 102.83182515120313), 
        "desc": "บุฟเฟต์สุกี้ยากี้ / ชาบู (ตั้งอยู่ในโลตัส ศิลา)", 
        "hours": "11:00 - 05:00"
    },
    "สุกี้ตี๋น้อย (สาขาศรีจันทร์)": {
        "coords": (16.43501227281179, 102.8572306522941), 
        "desc": "บุฟเฟต์สุกี้ยากี้ / ชาบู (ตั้งอยู่โครงการตึกศรีจันทร์สแควร์ ในเมือง)", 
        "hours": "11:00 - 05:00"
    },
    "โบนัสสุกี้ (สาขาแฟรี่พลาซ่า)": {
        "coords": (16.43192580309003, 102.83258394753588), 
        "desc": "บุฟเฟต์ชาบู-สุกี้ยากี้ เจ้าดังขวัญใจชาวขอนแก่น (ชั้น 2 ห้างแฟรี่พลาซ่า)", 
        "hours": "10:30 - 21:00"
    },
    "หมูกระทะเฮียเปียว (กังสดาล)": {
        "coords": (16.460612551887007, 102.8272372935368), 
        "desc": "หมูกระทะแบบชั่งกิโลในตำนาน น้ำจิ้มสูตรเด็ด (โซนกังสดาล มข.)", 
        "hours": "16:00 - 23:00"
    },
    "Style Soup ซุปหม่าล่า (กังสดาล)": {
        "coords": (16.457412807112917, 102.8241600627709), 
        "desc": "หม่าล่าทั่งแบบตักขีด ซุปกระดูกวัว ซุปนมเข้มข้น (โซนกังสดาล มข.)", 
        "hours": "11:00 - 22:00"
    },
    "เฟิงฟู่ หมูกระทะ Fengfu Mookata (หลังมอ)": {
        "coords": (16.4824476065446, 102.81224826095774), 
        "desc": "หมูกระทะ น้ำจิ้มสูตรเด็ด กุ้งหมึกจัดเต็ม (โซนหลังมอ มข.)", 
        "hours": "16:30 - 00:00"
    },
    "หมีกะหมู ชาบู&ปิ้งย่าง (หลังมอ)": {
        "coords": (16.489822806304286, 102.82004481481545), 
        "desc": "หมูกระทะบุฟเฟต์ราคาประหยัด ขวัญใจวัยรุ่นหลังมอ (โซนหลังมอ มข.)", 
        "hours": "16:30 - 22:00"
    },
    "แจ่วฮ้อนอภิรมย์ สาขา มข.": {
        "coords": (16.460328616609143, 102.83063009116643), 
        "desc": "แจ่วฮ้อนรสเด็ด น้ำซุปสมุนไพรเข้มข้น เนื้อคุณภาพดี (โซน มข.)", 
        "hours": "11:00 - 22:00"
    },
    "โต้งปลาเผา (โซนในเมือง)": {
        "coords": (16.42255541255355, 102.83728596841723), 
        "desc": "ร้านอาหารอีสาน รสแซ่บ ปลาช่อนเผาเกลือ (ริมถนนศรีนวล)", 
        "hours": "12:00 - 22:00"
    },
    "Riburs BBQ": {
        "coords": (16.46285789361636, 102.84449397411916), 
        "desc": "ภัตตาคารอาหารอเมริกัน", 
        "hours": "18:00 - 23:00"
    },
    "เอมโอช (โซนในเมือง)": {
        "coords": (16.435859552566374, 102.83621939299617), 
        "desc": "ร้านอาหารเช้าชื่อดัง ไข่กระทะ กวยจั๊บญวน (ถนนกลางเมือง)", 
        "hours": "04:00 - 13:00"
    },
    "ฮาลองเบย์ อาหารเวียดนาม (โซนในเมือง)": {
        "coords": (16.424158982736248, 102.84022958957652), 
        "desc": "ภัตตาคารอาหารเวียดนาม", 
        "hours": "09:30 - 21:30"
    },
    "VT แหนมเนือง ขอนแก่น": {
        "coords": (16.444298003901313, 102.79633422554072), 
        "desc": "อาหารเวียดนาม แหนมเนืองชุดใหญ่ ผักสดสะอาด (ถนนหน้าเมือง)", 
        "hours": "08:00 - 19:30"
    },
    "ประสิทธิ์โภชนา": {
        "coords": (16.43433725837038, 102.83336809242859), 
        "desc": "เนื้อย่างระดับตำนานของเมืองขอนแก่น (ถนนอำมาตย์)", 
        "hours": "09:30 - 14:00"
    }
}

RESTAURANT_LIST = list(RESTAURANT_DATA.keys())

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth surface."""
    R = 6371.0 # Earth radius in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ─────────────────────────────────────────────
#  PERSISTENT USER DATABASE
# ─────────────────────────────────────────────
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")

_DEFAULT_USERS = [
    {"first": "Demo", "last": "User", "email": "demo@wongnork.com", "password": "demo123"},
]

def _load_db():
    if not os.path.exists(DB_FILE):
        _save_db(_DEFAULT_USERS)
        return list(_DEFAULT_USERS)
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else list(_DEFAULT_USERS)
    except Exception:
        return list(_DEFAULT_USERS)

def _save_db(users):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

USER_DB = _load_db()

def valid_email(e):
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", e.strip()))

def find_user(email):
    return next((u for u in USER_DB if u["email"].lower() == email.strip().lower()), None)

def add_user(first, last, email, password):
    user = {"first": first, "last": last, "email": email.lower(), "password": password}
    USER_DB.append(user)
    _save_db(USER_DB)
    return user

# ─────────────────────────────────────────────
#  PERSISTENT RESERVATIONS
# ─────────────────────────────────────────────
RES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reservations.json")

def _load_res():
    if not os.path.exists(RES_FILE): return []
    try:
        with open(RES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception: return []

def _save_res(reservations):
    try:
        with open(RES_FILE, "w", encoding="utf-8") as f:
            json.dump(reservations, f, indent=2, ensure_ascii=False)
    except Exception: pass

RESERVATIONS = _load_res()

def add_reservation(user_email, name, restaurant, date, time, guests, note):
    rest_reservations = [r for r in RESERVATIONS if r.get("restaurant") == restaurant]
    next_q_num = len(rest_reservations) + 1
    queue_number = f"A{next_q_num:03d}"

    res = {
        "id":    len(RESERVATIONS) + 1,
        "email": user_email.lower(),
        "name":  name,
        "restaurant": restaurant,
        "date":  date,
        "time":  time,
        "guests":guests,
        "note":  note,
        "queue_number": queue_number,
        "created": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
        "status": "Waiting in Line", 
        "rating": 0,
        "feedback": ""
    }
    RESERVATIONS.append(res)
    _save_res(RESERVATIONS)
    return res

def get_user_reservations(user_email):
    return [r for r in RESERVATIONS if r["email"] == user_email.lower()]

def cancel_reservation(res_id):
    for r in RESERVATIONS:
        if r["id"] == res_id: r["status"] = "Cancelled"
    _save_res(RESERVATIONS)

def submit_feedback(res_id, rating, comment):
    for r in RESERVATIONS:
        if r["id"] == res_id:
            r["status"] = "Completed"
            r["rating"] = rating
            r["feedback"] = comment
    _save_res(RESERVATIONS)

# ─────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────
def alpha_mix(hex_bg, ratio):
    r, g, b = int(hex_bg[1:3],16), int(hex_bg[3:5],16), int(hex_bg[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(int(r+(255-r)*ratio), int(g+(255-g)*ratio), int(b+(255-b)*ratio))

def darken(hex_color, amt=22):
    try:
        r,g,b = int(hex_color[1:3],16),int(hex_color[3:5],16),int(hex_color[5:7],16)
        return "#{:02x}{:02x}{:02x}".format(max(0,r-amt), max(0,g-amt), max(0,b-amt))
    except: return hex_color

# ═════════════════════════════════════════════
#  SCROLLABLE FRAME
# ═════════════════════════════════════════════
class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=C["white"], **kw):
        super().__init__(parent, bg=bg, **kw)
        self._cv  = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self._sb  = ttk.Scrollbar(self, orient="vertical", command=self._cv.yview)
        self._cv.configure(yscrollcommand=self._sb.set)
        self._sb.pack(side="right", fill="y")
        self._cv.pack(side="left",  fill="both", expand=True)
        self.inner  = tk.Frame(self._cv, bg=bg)
        self._win   = self._cv.create_window((0,0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._update)
        self._cv.bind("<Configure>",   self._on_canvas_resize)
        self._cv.bind("<Enter>",  lambda _: self._bind_wheel())
        self._cv.bind("<Leave>",  lambda _: self._unbind_wheel())

    def _update(self, _=None):
        self._cv.configure(scrollregion=self._cv.bbox("all"))
        if self.inner.winfo_reqheight() <= self._cv.winfo_height(): self._sb.pack_forget()
        else: self._sb.pack(side="right", fill="y")

    def _on_canvas_resize(self, event):
        self._cv.itemconfig(self._win, width=event.width)
        self._update()

    def _bind_wheel(self):
        self._cv.bind_all("<MouseWheel>", self._scroll)
        self._cv.bind_all("<Button-4>",   self._scroll)
        self._cv.bind_all("<Button-5>",   self._scroll)

    def _unbind_wheel(self):
        self._cv.unbind_all("<MouseWheel>")
        self._cv.unbind_all("<Button-4>")
        self._cv.unbind_all("<Button-5>")

    def _scroll(self, event):
        if event.num == 4: self._cv.yview_scroll(-1, "units")
        elif event.num == 5: self._cv.yview_scroll( 1, "units")
        else: self._cv.yview_scroll(int(-1*(event.delta/120)), "units")

# ═════════════════════════════════════════════
#  MAIN APP
# ═════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WONGNORK")
        self.configure(bg=C["bg"])
        self.minsize(850, 650)
        self.resizable(True, True)
        self._center(1050, 750)
        
        # จุดเริ่มต้นตั้งไว้ที่ กังสดาล มข. 
        self.user_lat = 16.4550
        self.user_lon = 102.8240
        self.dropdown_mapping = {}

        self._build_navbar()
        self._build_body()
        self._build_toast()
        self._toast_id      = None
        self._shadow_frame  = None
        self._card_frame    = None

        self.show_login()
        self.bind("<Configure>", self._on_resize)

    def _center(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_navbar(self):
        nav = tk.Frame(self, bg=C["navy"], height=52)
        nav.pack(side="top", fill="x"); nav.pack_propagate(False)
        tk.Label(nav, text="W O N G N O R K", bg=C["navy"], fg=C["white"], font=("Helvetica", 14, "bold")).pack(side="left", padx=26)
        tk.Label(nav, text="●", bg=C["navy"], fg=C["brown"], font=("Helvetica", 8)).pack(side="left", padx=(0,4))
        tk.Label(nav, text="Smart Queue Management Platform", bg=C["navy"], fg="#5a7a99", font=("Helvetica", 9)).pack(side="left")

    def _build_body(self):
        self._body = tk.Frame(self, bg=C["bg"])
        self._body.pack(fill="both", expand=True)
        self._bg_cv = tk.Canvas(self._body, bg=C["bg"], highlightthickness=0)
        self._bg_cv.place(relwidth=1, relheight=1)
        self._body.bind("<Configure>", lambda _: self._draw_blobs())
        self._outer = tk.Frame(self._body, bg=C["bg"])
        self._outer.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.94, relheight=0.92)

    def _draw_blobs(self):
        self._bg_cv.delete("all")
        w, h = max(self._body.winfo_width(), 1), max(self._body.winfo_height(), 1)
        self._bg_cv.create_oval(-80, -40, w*0.42, h*0.7, fill="#e5dbd5", outline="", stipple="gray25")
        self._bg_cv.create_oval(w*0.62, h*0.42, w+80, h+60, fill="#d5e8e0", outline="", stipple="gray25")

    def _on_resize(self, _=None):
        self._draw_blobs()
        if hasattr(self, "_toast_frame") and self._toast_frame.winfo_ismapped():
            self._toast_frame.place(x=self.winfo_width()-20, y=60, anchor="ne")

    def _build_toast(self):
        self._toast_var   = tk.StringVar()
        self._toast_frame = tk.Frame(self, bg=C["green"], padx=18, pady=10)
        self._toast_lbl   = tk.Label(self._toast_frame, textvariable=self._toast_var, bg=C["green"], fg="white", font=("Helvetica", 11, "bold"))
        self._toast_lbl.pack()

    def show_toast(self, msg, kind="success"):
        bg   = C["green"] if kind == "success" else C["error"]
        icon = "✓  "      if kind == "success" else "✕  "
        self._toast_var.set(icon + msg)
        self._toast_frame.config(bg=bg)
        self._toast_lbl.config(bg=bg)
        self._toast_frame.place(x=self.winfo_width()-20, y=60, anchor="ne")
        self._toast_frame.lift()
        if self._toast_id: self.after_cancel(self._toast_id)
        self._toast_id = self.after(3200, lambda: self._toast_frame.place_forget())

    def _clear(self):
        for attr in ("_shadow_frame", "_card_frame"):
            w = getattr(self, attr, None)
            if w and w.winfo_exists(): w.destroy()
            setattr(self, attr, None)

    def _make_card(self):
        self._clear()
        shadow = tk.Frame(self._outer, bg=C["shadow"])
        shadow.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0, x=4, y=4)
        self._shadow_frame = shadow
        card = tk.Frame(self._outer, bg=C["white"])
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0)
        self._card_frame = card
        return card

    def _left_panel(self, card, title, subtitle, bg=None):
        bg = bg or C["navy"]
        pnl = tk.Frame(card, bg=bg, width=280)
        pnl.pack(side="left", fill="y"); pnl.pack_propagate(False)
        bc = tk.Canvas(pnl, bg=bg, highlightthickness=0)
        bc.place(relwidth=1, relheight=1)
        def _redraw(_, cv=bc, b=bg):
            cv.delete("all")
            w, h = max(cv.winfo_width(), 1), max(cv.winfo_height(), 1)
            lt = alpha_mix(b, 0.07)
            cv.create_oval(w*.4, -h*.15, w*1.9, h*.5,  fill=lt, outline="")
            cv.create_oval(-w*.3, h*.6, w*.65, h*1.3,  fill=lt, outline="")
        bc.bind("<Configure>", _redraw)
        av = tk.Canvas(pnl, width=96, height=96, bg=bg, highlightthickness=0)
        av.pack(pady=(60, 12))
        av.create_oval(2, 2, 94, 94, outline="white", width=2, fill="")
        av.create_oval(14, 14, 82, 82, fill=alpha_mix(bg, 0.13), outline="")
        av.create_oval(30, 16, 66, 52, fill="white", outline="")
        av.create_arc(14, 50, 82, 88, start=0, extent=180, fill="white", outline="")
        tk.Label(pnl, text=title, bg=bg, fg="white", font=("Helvetica", 22, "bold"), justify="center").pack(padx=16, pady=(0,6))
        tk.Label(pnl, text=subtitle, bg=bg, fg=alpha_mix(bg, 0.60), font=("Helvetica", 10), wraplength=220, justify="center").pack(padx=14)

    def _right_panel(self, card):
        sf = ScrollFrame(card, bg=C["white"])
        sf.pack(side="left", fill="both", expand=True)
        pad = tk.Frame(sf.inner, bg=C["white"])
        pad.pack(fill="both", expand=True, padx=50, pady=40)
        return pad

    def _lbl(self, p, text, size=10, weight="bold", fg=None):
        tk.Label(p, text=text, bg=C["white"], fg=fg or C["navy"], font=("Helvetica", size, weight), anchor="w").pack(fill="x")

    def _field(self, parent, label, show=""):
        tk.Label(parent, text=label.upper(), bg=C["white"], fg=C["navy"], font=("Helvetica", 9, "bold"), anchor="w").pack(fill="x", pady=(10,2))
        border = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        border.pack(fill="x")
        inner  = tk.Frame(border, bg=C["inp_bg"])
        inner.pack(fill="x")
        var   = tk.StringVar()
        entry = tk.Entry(inner, textvariable=var, show=show, bg=C["inp_bg"], fg=C["navy"], font=("Helvetica", 11), relief="flat", bd=8, insertbackground=C["navy"])
        entry.pack(side="left", fill="x", expand=True)
        def _in(_): border.config(bg=C["brown"]); inner.config(bg=C["white"]); entry.config(bg=C["white"])
        def _out(_): border.config(bg=C["border"]); inner.config(bg=C["inp_bg"]); entry.config(bg=C["inp_bg"])
        entry.bind("<FocusIn>",  _in); entry.bind("<FocusOut>", _out)
        err = tk.Label(parent, text="", bg=C["white"], fg=C["error"], font=("Helvetica", 9), anchor="w")
        err.pack(fill="x", padx=2)
        return var, entry, err

    def _field_pair(self, parent, l1, l2):
        row = tk.Frame(parent, bg=C["white"])
        row.pack(fill="x")
        def _half(container, label):
            tk.Label(container, text=label.upper(), bg=C["white"], fg=C["navy"], font=("Helvetica", 9, "bold"), anchor="w").pack(fill="x", pady=(10,2))
            border = tk.Frame(container, bg=C["border"], padx=1, pady=1)
            border.pack(fill="x")
            inner  = tk.Frame(border, bg=C["inp_bg"])
            inner.pack(fill="x")
            var   = tk.StringVar()
            entry = tk.Entry(inner, textvariable=var, bg=C["inp_bg"], fg=C["navy"], font=("Helvetica", 11), relief="flat", bd=8, insertbackground=C["navy"])
            entry.pack(fill="x")
            def _i(_): border.config(bg=C["brown"]); inner.config(bg=C["white"]); entry.config(bg=C["white"])
            def _o(_): border.config(bg=C["border"]); inner.config(bg=C["inp_bg"]); entry.config(bg=C["inp_bg"])
            entry.bind("<FocusIn>",  _i); entry.bind("<FocusOut>", _o)
            err = tk.Label(container, text="", bg=C["white"], fg=C["error"], font=("Helvetica", 9), anchor="w")
            err.pack(fill="x", padx=2)
            return var, entry, err
        lf = tk.Frame(row, bg=C["white"]); lf.pack(side="left", fill="x", expand=True, padx=(0,6))
        rf = tk.Frame(row, bg=C["white"]); rf.pack(side="left", fill="x", expand=True, padx=(6,0))
        return _half(lf, l1), _half(rf, l2)

    def _btn(self, parent, text, color, fg="white", cmd=None, outline=False):
        btn = tk.Button(parent, text=text, bg=color, fg=fg, font=("Helvetica", 12, "bold"), relief="flat", bd=0, cursor="hand2", pady=11, activeforeground=fg, command=cmd)
        if outline: btn.config(highlightbackground=C["border"], highlightthickness=1)
        btn.pack(fill="x", pady=(4,0))
        dk = darken(color)
        btn.bind("<Enter>", lambda _: btn.config(bg=dk)); btn.bind("<Leave>", lambda _: btn.config(bg=color))
        return btn

    def _divider(self, parent):
        f = tk.Frame(parent, bg=C["white"]); f.pack(fill="x", pady=12)
        tk.Frame(f, bg=C["border"], height=1).pack(side="left", fill="x", expand=True, pady=8)
        tk.Label(f, text=" or ", bg=C["white"], fg=C["muted"], font=("Helvetica", 9)).pack(side="left")
        tk.Frame(f, bg=C["border"], height=1).pack(side="left", fill="x", expand=True, pady=8)

    def _fade(self, callback, alpha=1.0, direction="out"):
        if direction == "out":
            if alpha > 0.05:
                try: self.attributes("-alpha", alpha)
                except: pass
                self.after(16, lambda: self._fade(callback, alpha-0.09, "out"))
            else:
                self.attributes("-alpha", 0); callback(); self._fade(None, 0.0, "in")
        else:
            if alpha < 1.0:
                try: self.attributes("-alpha", alpha)
                except: pass
                self.after(16, lambda: self._fade(None, alpha+0.09, "in"))
            else:
                self.attributes("-alpha", 1.0)

    # ═════════════════════════════════════
    #  LOGIN & REGISTER
    # ═════════════════════════════════════
    def show_login(self):
        self._login_attempts, self._lockout_active = 0, False
        card  = self._make_card()
        self._left_panel(card, "Welcome\nBack", "Sign in to manage your\nrestaurant operations")
        inner = self._right_panel(card)
        self._lbl(inner, "Sign In", 24, "bold")
        self._lbl(inner, "Enter your credentials to continue", 10, "normal", fg=C["muted"])
        tk.Frame(inner, bg=C["white"], height=12).pack()
        self._le_v, self._le_e, self._le_err = self._field(inner, "Email Address")
        self._lp_v, self._lp_e, self._lp_err = self._field(inner, "Password", show="•")
        self._lp_v.trace_add("write", lambda *_: self._lp_err.config(text="", fg=C["error"]))
        fl = tk.Frame(inner, bg=C["white"]); fl.pack(fill="x", pady=(0,8))
        tk.Button(fl, text="Forgot password?", bg=C["white"], fg=C["brown"], relief="flat", bd=0, cursor="hand2", font=("Helvetica", 9, "bold")).pack(side="right")
        self._sign_in_btn = self._btn(inner, "Sign In", C["brown"], cmd=self._do_login)
        self._divider(inner)
        self._btn(inner, "Create an Account", C["white"], fg=C["navy"], cmd=lambda: self._fade(self.show_register), outline=True)

    def _do_login(self):
        email, pw = self._le_v.get().strip(), self._lp_v.get()
        self._le_err.config(text=""); self._lp_err.config(text="")
        if not email or not pw: return
        user = find_user(email)
        if user and user["password"] == pw:
            self.show_toast(f"Welcome back, {user['first']}! 🎉", "success")
            self._current_user = user
            self.after(600, lambda: self._fade(self.show_reservation))
        else:
            self._le_err.config(text="⚠ Invalid email or password.")

    def show_register(self):
        card  = self._make_card()
        self._left_panel(card, "Join\nUs Today", "Create your account", bg=C["green2"])
        inner = self._right_panel(card)
        self._lbl(inner, "Create Account", 22, "bold")
        tk.Frame(inner, bg=C["white"], height=8).pack()
        (self._rf_v, self._rf_e, self._rf_err), (self._rl_v, self._rl_e, self._rl_err) = self._field_pair(inner, "First Name", "Last Name")
        self._re_v,  self._re_e,  self._re_err  = self._field(inner, "Email Address")
        self._rp_v,  self._rp_e,  self._rp_err  = self._field(inner, "Password", show="•")
        self._rrp_v, self._rrp_e, self._rrp_err = self._field(inner, "Confirm Password", show="•")
        self._btn(inner, "Create Account", C["green"], cmd=self._do_register)
        self._divider(inner)
        self._btn(inner, "Back to Sign In", C["white"], fg=C["navy"], cmd=lambda: self._fade(self.show_login), outline=True)

    def _do_register(self):
        first, last, email, pw, repw = self._rf_v.get().strip(), self._rl_v.get().strip(), self._re_v.get().strip(), self._rp_v.get(), self._rrp_v.get()
        if not email or pw != repw: return
        add_user(first, last, email, pw)
        self.show_toast("Account created!", "success")
        self.after(1000, lambda: self._fade(self.show_login))

    # ═════════════════════════════════════
    #  RESERVATION PAGE & DASHBOARD
    # ═════════════════════════════════════
    def show_reservation(self):
        self._clear()
        self._outer.place_forget()
        self._res_root = tk.Frame(self._body, bg=C["bg"])
        self._res_root.place(relx=0, rely=0, relwidth=1, relheight=1)

        sidebar = tk.Frame(self._res_root, bg=C["navy"], width=240)
        sidebar.pack(side="left", fill="y"); sidebar.pack_propagate(False)
        tk.Label(sidebar, text="W O N G N O R K", bg=C["navy"], fg=C["white"], font=("Helvetica", 13, "bold")).pack(pady=(36,2), padx=24, anchor="w")
        tk.Label(sidebar, text="Smart Queue Platform", bg=C["navy"], fg=alpha_mix(C["navy"], 0.5), font=("Helvetica", 9)).pack(padx=24, anchor="w")
        tk.Frame(sidebar, bg=alpha_mix(C["navy"], 0.15), height=1).pack(fill="x", padx=20, pady=20)
        
        # ─── NAVIGATION ───
        nav_items = [
            ("📊", "All Queues", False), 
            ("🍽️", "Reservations", True), 
            ("📍", "My Location", False)
        ]
        
        self._nav_frames, self._nav_labels = {}, {}
        for icon, label, active in nav_items:
            bg  = C["brown"] if active else C["navy"]
            nf  = tk.Frame(sidebar, bg=bg, padx=16, pady=12, cursor="hand2")
            nf.pack(fill="x", padx=16, pady=4)
            lbl_w = tk.Label(nf, text=f"{icon}  {label}", bg=bg, fg="white", font=("Helvetica", 11, "bold" if active else "normal"), anchor="w")
            lbl_w.pack(fill="x")
            self._nav_frames[label], self._nav_labels[label] = nf, lbl_w
            nf.bind("<Button-1>", lambda e, l=label: self._nav_click(l))
            lbl_w.bind("<Button-1>", lambda e, l=label: self._nav_click(l))

        logout_f = tk.Frame(sidebar, bg=C["navy"], padx=16, pady=12, cursor="hand2")
        logout_f.pack(side="bottom", fill="x", padx=16, pady=20)
        tk.Label(logout_f, text="🚪  Log Out", bg=C["navy"], fg="white", font=("Helvetica", 11)).pack(fill="x")
        logout_f.bind("<Button-1>", lambda _: self._logout())

        main = tk.Frame(self._res_root, bg=C["bg"])
        main.pack(side="left", fill="both", expand=True)
        topbar = tk.Frame(main, bg=C["white"], height=70)
        topbar.pack(fill="x"); topbar.pack_propagate(False)
        self._topbar_title = tk.Label(topbar, text="Dashboard", bg=C["white"], fg=C["navy"], font=("Helvetica", 18, "bold"))
        self._topbar_title.pack(side="left", padx=32, pady=20)
        self._content_area = tk.Frame(main, bg=C["bg"])
        self._content_area.pack(fill="both", expand=True)
        
        self._show_reservations_content()

    def _nav_click(self, label):
        for lbl, frm in self._nav_frames.items():
            frm.config(bg=C["navy"]); self._nav_labels[lbl].config(bg=C["navy"], font=("Helvetica",11,"normal"))
        self._nav_frames[label].config(bg=C["brown"])
        self._nav_labels[label].config(bg=C["brown"], font=("Helvetica",11,"bold"))
        
        if label == "My Location": self._show_gps_page()
        elif label == "Reservations": self._show_reservations_content()
        elif label == "All Queues": self._show_all_queues_content()

    def _get_sorted_restaurants(self):
        distances = []
        for rest, data in RESTAURANT_DATA.items():
            dist = calculate_distance(self.user_lat, self.user_lon, data["coords"][0], data["coords"][1])
            distances.append((rest, dist))
        distances.sort(key=lambda x: x[1])
        return distances

    # ═════════════════════════════════════
    #  ALL QUEUES PAGE 
    # ═════════════════════════════════════
    def _show_all_queues_content(self):
        for w in self._content_area.winfo_children(): w.destroy()
        self._topbar_title.config(text="Live Restaurant Queues")
        
        sf = ScrollFrame(self._content_area, bg=C["bg"])
        sf.pack(fill="both", expand=True)
        pad = tk.Frame(sf.inner, bg=C["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=24)
        
        tk.Label(pad, text="📊 สถานะคิวปัจจุบันของทุกร้าน (เรียงตามระยะทางจากจุดที่คุณอยู่)", bg=C["bg"], fg=C["navy"], font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(0, 16))
        
        grid_frame = tk.Frame(pad, bg=C["bg"])
        grid_frame.pack(fill="x")
        
        sorted_rests = self._get_sorted_restaurants()
        
        for rest, dist in sorted_rests:
            waiting_count = len([r for r in RESERVATIONS if r.get("restaurant") == rest and r.get("status") == "Waiting in Line"])
            
            card = tk.Frame(grid_frame, bg=C["white"], padx=20, pady=16)
            card.pack(fill="x", pady=(0, 12))
            
            lf = tk.Frame(card, bg=C["white"])
            lf.pack(side="left")
            
            tk.Label(lf, text=f"🏢 {rest}", bg=C["white"], fg=C["navy"], font=("Helvetica", 12, "bold")).pack(anchor="w")
            tk.Label(lf, text=f"📍 ห่างจากคุณ {dist:.2f} km", bg=C["white"], fg=C["muted"], font=("Helvetica", 9)).pack(anchor="w", pady=(2,0))
            
            rf = tk.Frame(card, bg=C["white"])
            rf.pack(side="right")
            
            status_color = C["error"] if waiting_count > 0 else C["green"]
            tk.Label(rf, text=f"กำลังรออยู่ {waiting_count} คิว", bg=C["white"], fg=status_color, font=("Helvetica", 12, "bold")).pack(anchor="e")

    # ═════════════════════════════════════
    #  RESERVATIONS TAB
    # ═════════════════════════════════════
    def _show_reservations_content(self):
        for w in self._content_area.winfo_children(): w.destroy()
        self._topbar_title.config(text="Find & Book a Table")
        sf = ScrollFrame(self._content_area, bg=C["bg"])
        sf.pack(fill="both", expand=True)
        pad = tk.Frame(sf.inner, bg=C["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=24)
        cols = tk.Frame(pad, bg=C["bg"])
        cols.pack(fill="both", expand=True)
        left_col  = tk.Frame(cols, bg=C["bg"])
        left_col.pack(side="left", fill="both", expand=True, padx=(0,16))
        right_col = tk.Frame(cols, bg=C["bg"])
        right_col.pack(side="left", fill="both", expand=True, padx=(16,0))
        self._build_booking_form(left_col)
        self._build_bookings_list(right_col)

    def _build_booking_form(self, left_col):
        form_card = tk.Frame(left_col, bg=C["white"])
        form_card.pack(fill="x", pady=(0,16))
        hdr = tk.Frame(form_card, bg=C["navy"], pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🗓️  New Booking", bg=C["navy"], fg="white", font=("Helvetica", 13, "bold")).pack(side="left", padx=24)
        fpad = tk.Frame(form_card, bg=C["white"])
        fpad.pack(fill="x", padx=24, pady=20)

        self._res_name_v = tk.StringVar()
        tk.Label(fpad, text="GUEST NAME", bg=C["white"], fg=C["navy"], font=("Helvetica", 9, "bold")).pack(anchor="w", pady=(0,4))
        tk.Entry(fpad, textvariable=self._res_name_v, font=("Helvetica", 12), bg=C["inp_bg"], relief="flat").pack(fill="x", ipady=4, pady=(0,12))

        tk.Label(fpad, text="SELECT RESTAURANT", bg=C["white"], fg=C["navy"], font=("Helvetica", 9, "bold")).pack(anchor="w", pady=(0,4))
        
        sorted_rests = self._get_sorted_restaurants()
        self.dropdown_mapping = {f"{r[0]} ({r[1]:.1f} km)": r[0] for r in sorted_rests}
        display_options = list(self.dropdown_mapping.keys())
        
        self._res_restaurant_v = tk.StringVar(value=display_options[0])
        ttk.Combobox(fpad, textvariable=self._res_restaurant_v, values=display_options, state="readonly", font=("Helvetica", 11)).pack(fill="x", ipady=5, pady=(0,12))

        dr = tk.Frame(fpad, bg=C["white"]); dr.pack(fill="x", pady=(0,12))
        lf = tk.Frame(dr, bg=C["white"]); lf.pack(side="left", fill="x", expand=True, padx=(0,6))
        rf = tk.Frame(dr, bg=C["white"]); rf.pack(side="left", fill="x", expand=True, padx=(6,0))
        
        tk.Label(lf, text="DATE (DD/MM/YYYY)", bg=C["white"], fg=C["navy"], font=("Helvetica", 9, "bold")).pack(anchor="w", pady=(0,4))
        date_frame = tk.Frame(lf, bg=C["white"])
        date_frame.pack(fill="x")
        
        now = datetime.datetime.now()
        self._res_day_v = tk.StringVar(value=now.strftime("%d"))
        self._res_month_v = tk.StringVar(value=now.strftime("%m"))
        self._res_year_v = tk.StringVar(value=now.strftime("%Y"))
        
        days = [f"{i:02d}" for i in range(1, 32)]
        months = [f"{i:02d}" for i in range(1, 13)]
        years = [str(now.year), str(now.year + 1)]
        
        ttk.Combobox(date_frame, textvariable=self._res_day_v, values=days, state="readonly", width=3, font=("Helvetica", 11)).pack(side="left", padx=(0,4))
        tk.Label(date_frame, text="/", bg=C["white"], fg=C["muted"]).pack(side="left")
        ttk.Combobox(date_frame, textvariable=self._res_month_v, values=months, state="readonly", width=3, font=("Helvetica", 11)).pack(side="left", padx=4)
        tk.Label(date_frame, text="/", bg=C["white"], fg=C["muted"]).pack(side="left")
        ttk.Combobox(date_frame, textvariable=self._res_year_v, values=years, state="readonly", width=5, font=("Helvetica", 11)).pack(side="left", padx=(4,0))

        tk.Label(rf, text="TIME", bg=C["white"], fg=C["navy"], font=("Helvetica", 9, "bold")).pack(anchor="w", pady=(0,4))
        self._res_time_v = tk.StringVar(value=now.strftime("%H:00"))
        times = [f"{h:02d}:{m:02d}" for h in range(0, 24) for m in (0, 30)]
        ttk.Combobox(rf, textvariable=self._res_time_v, values=times, state="readonly", font=("Helvetica", 11)).pack(fill="x", ipady=3)

        tk.Label(fpad, text="GUESTS", bg=C["white"], fg=C["navy"], font=("Helvetica", 9, "bold")).pack(anchor="w", pady=(12,4))
        self._res_guests_v = tk.StringVar(value="2")
        ttk.Combobox(fpad, textvariable=self._res_guests_v, values=[str(i) for i in range(1,11)], state="readonly", font=("Helvetica", 11)).pack(fill="x", ipady=5, pady=(0,20))

        tk.Button(fpad, text="✓ Confirm & Join Queue", bg=C["brown"], fg="white", font=("Helvetica", 12, "bold"), relief="flat", cursor="hand2", pady=12, command=self._do_reserve).pack(fill="x")

    def _do_reserve(self):
        user = getattr(self, "_current_user", {})
        name = self._res_name_v.get().strip() or user.get("first")
        
        selected_display = self._res_restaurant_v.get()
        rest = self.dropdown_mapping.get(selected_display, selected_display.split(" (")[0])
        
        try:
            year = int(self._res_year_v.get())
            month = int(self._res_month_v.get())
            day = int(self._res_day_v.get())
            time_str = self._res_time_v.get()
            hh, mm = map(int, time_str.split(':'))
            
            selected_dt = datetime.datetime(year, month, day, hh, mm)
        except ValueError:
            messagebox.showwarning("รูปแบบวันที่ไม่ถูกต้อง", "กรุณาตรวจสอบวันที่ใหม่อีกครั้ง")
            return
            
        if selected_dt < datetime.datetime.now():
            messagebox.showwarning("ไม่สามารถจองได้", "ไม่สามารถจองคิวในวันและเวลาที่ผ่านไปแล้วได้ กรุณาเลือกเวลาใหม่")
            return

        date_str = f"{year}-{month:02d}-{day:02d}"
        
        add_reservation(user.get("email",""), name, rest, date_str, self._res_time_v.get(), self._res_guests_v.get(), "")
        self.show_toast(f"Joined queue at {rest}!", "success")
        self._refresh_bookings()

    def _build_bookings_list(self, right_col):
        bk_card = tk.Frame(right_col, bg=C["white"])
        bk_card.pack(fill="both", expand=True)
        bk_hdr = tk.Frame(bk_card, bg=C["navy"], pady=16)
        bk_hdr.pack(fill="x")
        tk.Label(bk_hdr, text="📋  Live Queue & History", bg=C["navy"], fg="white", font=("Helvetica", 13, "bold")).pack(side="left", padx=24)
        self._bookings_frame = tk.Frame(bk_card, bg=C["white"])
        self._bookings_frame.pack(fill="both", expand=True, padx=20, pady=16)
        self._refresh_bookings()

    def _refresh_bookings(self):
        for w in self._bookings_frame.winfo_children(): w.destroy()
        user  = getattr(self, "_current_user", {})
        bookings = get_user_reservations(user.get("email",""))

        if not bookings:
            tk.Label(self._bookings_frame, text="No queues or reservations yet. 🍽️", bg=C["white"], fg=C["muted"], font=("Helvetica", 11)).pack(pady=40)
            return

        for res in reversed(bookings):
            status = res.get("status", "Waiting in Line")
            bg_color = C["inp_bg"]
            row = tk.Frame(self._bookings_frame, bg=bg_color, pady=12, padx=16)
            row.pack(fill="x", pady=(0,10))

            lf = tk.Frame(row, bg=bg_color)
            lf.pack(side="left", fill="x", expand=True)

            rest_name = res.get("restaurant", "Unknown Restaurant")
            tk.Label(lf, text=f"🏢 {rest_name}", bg=bg_color, fg=C["navy"], font=("Helvetica", 12, "bold"), anchor="w").pack(anchor="w")

            if status in ["Waiting in Line", "Confirmed"]:
                live_queues_ahead = sum(
                    1 for r in RESERVATIONS 
                    if r.get("restaurant") == rest_name 
                    and r.get("status") == "Waiting in Line" 
                    and r["id"] < res["id"]
                )
                
                queue_info = f"🎫 Queue: {res.get('queue_number', 'N/A')}   |   ⏳ {live_queues_ahead} queues ahead"
                tk.Label(lf, text=queue_info, bg=bg_color, fg=C["error"] if live_queues_ahead>0 else C["green"], font=("Helvetica", 10, "bold"), anchor="w").pack(anchor="w", pady=(2,4))
            
            tk.Label(lf, text=f"📅 {res['date']} • 🕐 {res['time']} • 👥 {res['guests']} pax", bg=bg_color, fg=C["muted"], font=("Helvetica", 9), anchor="w").pack(anchor="w")

            rf = tk.Frame(row, bg=bg_color)
            rf.pack(side="right", fill="y", padx=(10,0))
            
            if status == "Completed":
                rating = res.get("rating", 0)
                stars = "★" * rating + "☆" * (5 - rating)
                tk.Label(rf, text="Completed", bg=bg_color, fg=C["green"], font=("Helvetica", 10, "bold")).pack(anchor="e", pady=(0,2))
                tk.Label(rf, text=stars, bg=bg_color, fg=C["gold"], font=("Helvetica", 16)).pack(anchor="e")
            elif status == "Cancelled":
                tk.Label(rf, text="Cancelled", bg=bg_color, fg=C["muted"], font=("Helvetica", 10, "bold")).pack(anchor="e")
            else:
                tk.Label(rf, text="Status: Waiting", bg=bg_color, fg=C["brown"], font=("Helvetica", 9, "bold")).pack(anchor="e", pady=(0,8))
                
                btn_frame = tk.Frame(rf, bg=bg_color)
                btn_frame.pack(anchor="e")
                
                rate_btn = tk.Button(btn_frame, text="🍽️ Finish & Rate", bg=C["green"], fg="white", font=("Helvetica", 9, "bold"), relief="flat", cursor="hand2", padx=12, pady=4, command=lambda rid=res["id"], rname=rest_name: self._show_feedback_popup(rid, rname))
                rate_btn.pack(side="left", padx=(0,8))
                
                cancel_btn = tk.Button(btn_frame, text="Cancel", bg=bg_color, fg=C["error"], font=("Helvetica", 9, "underline"), relief="flat", cursor="hand2", command=lambda rid=res["id"]: self._cancel_res(rid))
                cancel_btn.pack(side="left")

    def _cancel_res(self, res_id):
        cancel_reservation(res_id)
        self.show_toast("Queue cancelled.", "success")
        self._refresh_bookings()

    # ═════════════════════════════════════
    #  FEEDBACK SYSTEM
    # ═════════════════════════════════════
    def _show_feedback_popup(self, res_id, rest_name):
        top = tk.Toplevel(self)
        top.title("Post-Service Evaluation")
        top.geometry("400x380")
        top.configure(bg=C["white"])
        top.transient(self)
        top.grab_set()
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 380) // 2
        top.geometry(f"+{x}+{y}")

        tk.Label(top, text="How was your experience?", bg=C["white"], fg=C["navy"], font=("Helvetica", 14, "bold")).pack(pady=(24,4))
        tk.Label(top, text=f"at {rest_name}", bg=C["white"], fg=C["muted"], font=("Helvetica", 10)).pack(pady=(0,20))

        star_frame = tk.Frame(top, bg=C["white"]); star_frame.pack(pady=10)
        self._current_rating = 0
        star_labels = []

        def _set_rating(idx):
            self._current_rating = idx
            for i, lbl in enumerate(star_labels, 1):
                lbl.config(text="★" if i <= idx else "☆", fg=C["gold"] if i <= idx else C["border"])

        for i in range(1, 6):
            lbl = tk.Label(star_frame, text="☆", bg=C["white"], fg=C["border"], font=("Helvetica", 28), cursor="hand2")
            lbl.pack(side="left", padx=4)
            lbl.bind("<Button-1>", lambda e, idx=i: _set_rating(idx))
            star_labels.append(lbl)

        tk.Label(top, text="Leave a comment (optional)", bg=C["white"], fg=C["navy"], font=("Helvetica", 9, "bold")).pack(anchor="w", padx=30, pady=(16,4))
        comment_box = tk.Text(top, height=3, bg=C["inp_bg"], font=("Helvetica", 11), relief="flat", bd=8)
        comment_box.pack(fill="x", padx=30)

        def _submit():
            if self._current_rating == 0:
                messagebox.showwarning("Rating Required", "Please select a star rating.", parent=top)
                return
            submit_feedback(res_id, self._current_rating, comment_box.get("1.0", "end-1c").strip())
            top.destroy()
            self.show_toast("Thanks for your feedback!", "success")
            self._refresh_bookings()

        tk.Button(top, text="Submit Feedback", bg=C["brown"], fg="white", font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2", pady=10, command=_submit).pack(fill="x", padx=30, pady=24)

    # ═════════════════════════════════════
    #  GPS LOCATION PAGE (INTERACTIVE MAP)
    # ═════════════════════════════════════
    def _show_gps_page(self):
        for w in self._content_area.winfo_children(): w.destroy()
        self._topbar_title.config(text="📍 My Location (Pin on Map)")

        if not HAS_MAP:
            err_frame = tk.Frame(self._content_area, bg=C["bg"])
            err_frame.pack(expand=True)
            tk.Label(err_frame, text="⚠️ Required Library Missing ⚠️", bg=C["bg"], fg=C["error"], font=("Helvetica", 18, "bold")).pack(pady=10)
            tk.Label(err_frame, text="Please install the map library by running this in your terminal:", bg=C["bg"], fg=C["navy"], font=("Helvetica", 12)).pack(pady=4)
            tk.Label(err_frame, text="pip install tkintermapview", bg=C["inp_bg"], fg=C["brown"], font=("Courier", 14, "bold"), padx=10, pady=5).pack(pady=10)
            return

        outer = tk.Frame(self._content_area, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=32, pady=24)

        info_card = tk.Frame(outer, bg=C["white"])
        info_card.pack(fill="x", pady=(0, 16))
        
        hdr = tk.Frame(info_card, bg=C["navy"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📍 คลิกซ้ายบนแผนที่เพื่อปักหมุดตำแหน่งของคุณ หรือคลิกที่ร้านเพื่อดูข้อมูล", bg=C["navy"], fg="white", font=("Helvetica", 11, "bold")).pack(pady=4)

        self._coords_lbl = tk.Label(info_card, text=f"พิกัดปัจจุบัน: Lat {self.user_lat:.5f}, Lon {self.user_lon:.5f}", bg=C["white"], fg=C["navy"], font=("Helvetica", 11, "bold"))
        self._coords_lbl.pack(pady=10)

        # ── MAP FRAME ──
        map_frame = tk.Frame(outer, bg=C["border"], bd=2)
        map_frame.pack(fill="both", expand=True)

        self.map_widget = tkintermapview.TkinterMapView(map_frame, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)

        self.map_widget.set_position(self.user_lat, self.user_lon)
        self.map_widget.set_zoom(13)

        for rest, data in RESTAURANT_DATA.items():
            lat, lon = data["coords"]
            marker = self.map_widget.set_marker(
                lat, lon, 
                text=rest, 
                marker_color_circle=C["brown"],
                marker_color_outside=C["navy"],
                command=self._on_restaurant_click
            )
            marker.rest_name = rest

        self.current_marker = self.map_widget.set_marker(
            self.user_lat, self.user_lon, 
            text="📍 คุณอยู่ที่นี่", 
            marker_color_circle=C["green"], 
            marker_color_outside=C["green2"]
        )

        self.map_widget.add_left_click_map_command(self._on_map_click)

    def _on_restaurant_click(self, marker):
        rest_name = getattr(marker, "rest_name", marker.text)
        if rest_name not in RESTAURANT_DATA: return
        data = RESTAURANT_DATA[rest_name]
        
        top = tk.Toplevel(self)
        top.title("Restaurant Details")
        top.geometry("380x240")
        top.configure(bg=C["white"])
        top.transient(self)
        top.grab_set()
        
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 240) // 2
        top.geometry(f"+{x}+{y}")
        
        tk.Label(top, text=f"🏢 {rest_name}", bg=C["white"], fg=C["navy"], font=("Helvetica", 14, "bold")).pack(pady=(20, 10))
        
        info_frame = tk.Frame(top, bg=C["inp_bg"], padx=15, pady=15)
        info_frame.pack(fill="x", padx=20)
        
        tk.Label(info_frame, text=f"🍽️ รายละเอียด: {data['desc']}", bg=C["inp_bg"], fg=C["navy"], font=("Helvetica", 10), wraplength=310, justify="left").pack(anchor="w", pady=(0, 6))
        tk.Label(info_frame, text=f"⏰ เวลาเปิด-ปิด: {data['hours']}", bg=C["inp_bg"], fg=C["brown"], font=("Helvetica", 10, "bold")).pack(anchor="w")
        
        tk.Button(top, text="ปิดหน้าต่าง", bg=C["navy"], fg="white", font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=top.destroy).pack(pady=15, ipadx=20)

    def _on_map_click(self, coords):
        lat, lon = coords
        self.user_lat = lat
        self.user_lon = lon

        if hasattr(self, "current_marker") and self.current_marker:
            self.current_marker.delete()
        self.current_marker = self.map_widget.set_marker(
            lat, lon, 
            text="📍 คุณอยู่ที่นี่", 
            marker_color_circle=C["green"], 
            marker_color_outside=C["green2"]
        )

        self._coords_lbl.config(text=f"พิกัดปัจจุบัน: Lat {lat:.5f}, Lon {lon:.5f}")
        self.show_toast("📌 อัปเดตตำแหน่งของคุณแล้ว!", "success")

    def _logout(self):
        self._current_user = None
        if hasattr(self, "_res_root") and self._res_root.winfo_exists(): self._res_root.destroy()
        self._outer.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.94, relheight=0.92)
        self._fade(self.show_login)

if __name__ == "__main__":
    app = App()
    app.mainloop()