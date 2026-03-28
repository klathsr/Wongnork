"""
WONGNORK Authentication & Queue Management UI  —  Redesigned Dark Theme
=======================================================================
Run:  python wongnork_new.py
Needs: Python 3  (+ tkintermapview for the map page)
Install map lib:  pip install tkintermapview

Demo account: demo@wongnork.com / demo123
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re, json, os, threading, math, datetime

# ─────────────────────────────────────────────
#  MAP LIBRARY
# ─────────────────────────────────────────────
try:
    import tkintermapview
    HAS_MAP = True
except ImportError:
    HAS_MAP = False

# ─────────────────────────────────────────────
#  DARK THEME PALETTE
# ─────────────────────────────────────────────
C = {
    "bg":        "#0d0f14",
    "surface":   "#13161d",
    "surface2":  "#1a1e28",
    "border":    "#1f2433",
    "border2":   "#2a3040",
    "accent":    "#e8855a",
    "accent2":   "#f0a882",
    "accent_dk": "#c0613a",
    "green":     "#3dd68c",
    "green2":    "#2ab87a",
    "green_dim": "#1a3d2b",
    "red":       "#ff6b6b",
    "red_dim":   "#3d1a1a",
    "gold":      "#f5c842",
    "gold_dim":  "#3d3010",
    "text":      "#f0f0f0",
    "muted":     "#6b7280",
    "soft":      "#9ca3af",
    "navy":      "#23364A",   # kept for compatibility
    "white":     "#13161d",   # remapped to surface
    "inp_bg":    "#1a1e28",
    "error":     "#ff6b6b",
    "shadow":    "#08090c",
}

# ─────────────────────────────────────────────
#  RESTAURANT DATA
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
    R = 6371.0
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# ─────────────────────────────────────────────
#  USER DATABASE
# ─────────────────────────────────────────────
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
_DEFAULT_USERS = [{"first":"Demo","last":"User","email":"demo@wongnork.com","password":"demo123"}]

def _load_db():
    if not os.path.exists(DB_FILE): _save_db(_DEFAULT_USERS); return list(_DEFAULT_USERS)
    try:
        with open(DB_FILE,"r",encoding="utf-8") as f:
            d = json.load(f); return d if isinstance(d,list) else list(_DEFAULT_USERS)
    except: return list(_DEFAULT_USERS)

def _save_db(u):
    try:
        with open(DB_FILE,"w",encoding="utf-8") as f: json.dump(u,f,indent=2,ensure_ascii=False)
    except: pass

USER_DB = _load_db()

def valid_email(e): return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", e.strip()))
def find_user(email): return next((u for u in USER_DB if u["email"].lower()==email.strip().lower()), None)
def add_user(first,last,email,password):
    user={"first":first,"last":last,"email":email.lower(),"password":password}
    USER_DB.append(user); _save_db(USER_DB); return user

# ─────────────────────────────────────────────
#  RESERVATIONS DATABASE
# ─────────────────────────────────────────────
RES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reservations.json")

def _load_res():
    if not os.path.exists(RES_FILE): return []
    try:
        with open(RES_FILE,"r",encoding="utf-8") as f:
            d=json.load(f); return d if isinstance(d,list) else []
    except: return []

def _save_res(r):
    try:
        with open(RES_FILE,"w",encoding="utf-8") as f: json.dump(r,f,indent=2,ensure_ascii=False)
    except: pass

RESERVATIONS = _load_res()

def add_reservation(user_email,name,restaurant,date,time,guests,note):
    rest_res = [r for r in RESERVATIONS if r.get("restaurant")==restaurant]
    queue_number = f"A{len(rest_res)+1:03d}"
    res = {"id":len(RESERVATIONS)+1,"email":user_email.lower(),"name":name,
           "restaurant":restaurant,"date":date,"time":time,"guests":guests,
           "note":note,"queue_number":queue_number,
           "created":str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
           "status":"Waiting in Line","rating":0,"feedback":""}
    RESERVATIONS.append(res); _save_res(RESERVATIONS); return res

def get_user_reservations(email): return [r for r in RESERVATIONS if r["email"]==email.lower()]

def cancel_reservation(res_id):
    for r in RESERVATIONS:
        if r["id"]==res_id: r["status"]="Cancelled"
    _save_res(RESERVATIONS)

def submit_feedback(res_id,rating,comment):
    for r in RESERVATIONS:
        if r["id"]==res_id: r["status"]="Completed"; r["rating"]=rating; r["feedback"]=comment
    _save_res(RESERVATIONS)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def darken(hex_color, amt=20):
    try:
        r,g,b = int(hex_color[1:3],16),int(hex_color[3:5],16),int(hex_color[5:7],16)
        return "#{:02x}{:02x}{:02x}".format(max(0,r-amt),max(0,g-amt),max(0,b-amt))
    except: return hex_color

def lighten(hex_color, amt=15):
    try:
        r,g,b = int(hex_color[1:3],16),int(hex_color[3:5],16),int(hex_color[5:7],16)
        return "#{:02x}{:02x}{:02x}".format(min(255,r+amt),min(255,g+amt),min(255,b+amt))
    except: return hex_color

def alpha_mix(hex_bg, ratio):
    r,g,b = int(hex_bg[1:3],16),int(hex_bg[3:5],16),int(hex_bg[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(int(r+(255-r)*ratio),int(g+(255-g)*ratio),int(b+(255-b)*ratio))

# ─────────────────────────────────────────────
#  SCROLLABLE FRAME
# ─────────────────────────────────────────────
class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=None, **kw):
        bg = bg or C["bg"]
        super().__init__(parent, bg=bg, **kw)
        self._cv = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self._sb = ttk.Scrollbar(self, orient="vertical", command=self._cv.yview)
        self._cv.configure(yscrollcommand=self._sb.set)
        self._sb.pack(side="right", fill="y")
        self._cv.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self._cv, bg=bg)
        self._win  = self._cv.create_window((0,0), window=self.inner, anchor="nw")
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
        if event.num==4: self._cv.yview_scroll(-1,"units")
        elif event.num==5: self._cv.yview_scroll(1,"units")
        else: self._cv.yview_scroll(int(-1*(event.delta/120)),"units")


# ═════════════════════════════════════════════
#  STYLED WIDGETS
# ═════════════════════════════════════════════

def _style_ttk():
    """Apply dark theme to ttk widgets globally."""
    s = ttk.Style()
    try: s.theme_use("clam")
    except: pass
    s.configure("TCombobox",
                fieldbackground=C["surface2"], background=C["surface2"],
                foreground=C["text"], selectbackground=C["surface2"],
                selectforeground=C["text"], bordercolor=C["border2"],
                arrowcolor=C["soft"], lightcolor=C["surface2"], darkcolor=C["surface2"],
                insertcolor=C["text"])
    s.map("TCombobox",
          fieldbackground=[("readonly", C["surface2"]), ("focus", C["surface2"])],
          foreground=[("readonly", C["text"])],
          bordercolor=[("focus", C["accent"])])
    s.configure("Vertical.TScrollbar",
                background=C["surface2"], troughcolor=C["surface"],
                arrowcolor=C["muted"], bordercolor=C["border"])


class DarkEntry(tk.Frame):
    """Styled dark-theme entry with focus highlight."""
    def __init__(self, parent, textvariable=None, show="", placeholder="", **kw):
        super().__init__(parent, bg=C["border2"], padx=1, pady=1)
        self._inner = tk.Frame(self, bg=C["surface2"])
        self._inner.pack(fill="x")
        self._var = textvariable or tk.StringVar()
        self._placeholder = placeholder
        self._showing_ph = False

        self.entry = tk.Entry(self._inner, textvariable=self._var, show=show,
                              bg=C["surface2"], fg=C["text"], font=("Segoe UI", 11),
                              relief="flat", bd=8, insertbackground=C["accent"],
                              highlightthickness=0)
        self.entry.pack(fill="x")

        if placeholder and not self._var.get():
            self._show_placeholder()

        self.entry.bind("<FocusIn>",  self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)

    def _show_placeholder(self):
        self._showing_ph = True
        self.entry.config(fg=C["muted"])
        self.entry.insert(0, self._placeholder)

    def _focus_in(self, _=None):
        self.config(bg=C["accent"])
        self._inner.config(bg=lighten(C["surface2"], 5))
        self.entry.config(bg=lighten(C["surface2"], 5))
        if self._showing_ph:
            self.entry.delete(0, "end")
            self.entry.config(fg=C["text"])
            self._showing_ph = False

    def _focus_out(self, _=None):
        self.config(bg=C["border2"])
        self._inner.config(bg=C["surface2"])
        self.entry.config(bg=C["surface2"])
        if not self._var.get() and self._placeholder:
            self._show_placeholder()

    def get(self):
        if self._showing_ph: return ""
        return self._var.get()

    def set(self, v): self._var.set(v)


class DarkButton(tk.Label):
    """Hover-animated button."""
    def __init__(self, parent, text, command=None, bg=None, fg="white",
                 font=("Segoe UI", 11, "bold"), padx=0, pady=11, **kw):
        bg = bg or C["accent"]
        super().__init__(parent, text=text, font=font, fg=fg, bg=bg,
                         padx=padx, pady=pady, cursor="hand2", **kw)
        self._bg = bg
        self._hover = darken(bg, 18)
        self._cmd = command
        self.bind("<Enter>",    lambda e: self.config(bg=self._hover))
        self.bind("<Leave>",    lambda e: self.config(bg=self._bg))
        self.bind("<Button-1>", lambda e: command() if command else None)


# ═════════════════════════════════════════════
#  MAIN APPLICATION
# ═════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WONGNORK")
        self.configure(bg=C["bg"])
        self.minsize(900, 650)
        self.resizable(True, True)
        self._center(1080, 760)

        self.user_lat = 16.4550
        self.user_lon = 102.8240
        self.dropdown_mapping = {}
        self._current_user = None
        self._toast_id = None
        self._shadow_frame = None
        self._card_frame = None

        _style_ttk()
        self._build_body()
        self._build_toast()
        self.show_login()
        self.bind("<Configure>", self._on_resize)

    def _center(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── BODY ─────────────────────────────────────────────────────────────────
    def _build_body(self):
        self._body = tk.Frame(self, bg=C["bg"])
        self._body.pack(fill="both", expand=True)
        self._outer = tk.Frame(self._body, bg=C["bg"])
        self._outer.place(relx=0.5, rely=0.5, anchor="center",
                          relwidth=0.94, relheight=0.92)

    def _on_resize(self, _=None):
        if hasattr(self,"_toast_frame") and self._toast_frame.winfo_ismapped():
            self._toast_frame.place(x=self.winfo_width()-20, y=20, anchor="ne")

    # ── TOAST ────────────────────────────────────────────────────────────────
    def _build_toast(self):
        self._toast_var   = tk.StringVar()
        self._toast_frame = tk.Frame(self, bg=C["surface2"],
                                     highlightbackground=C["green"],
                                     highlightthickness=1, padx=20, pady=12)
        self._toast_lbl   = tk.Label(self._toast_frame, textvariable=self._toast_var,
                                      bg=C["surface2"], fg=C["text"],
                                      font=("Segoe UI", 11, "bold"))
        self._toast_lbl.pack()

    def show_toast(self, msg, kind="success"):
        icon  = "✓  " if kind=="success" else "✕  "
        color = C["green"] if kind=="success" else C["red"]
        self._toast_var.set(icon + msg)
        self._toast_frame.config(highlightbackground=color)
        self._toast_lbl.config(fg=color)
        self._toast_frame.place(x=self.winfo_width()-20, y=20, anchor="ne")
        self._toast_frame.lift()
        if self._toast_id: self.after_cancel(self._toast_id)
        self._toast_id = self.after(3200, lambda: self._toast_frame.place_forget())

    # ── CARD LAYOUT (LOGIN / REGISTER) ───────────────────────────────────────
    def _clear(self):
        for attr in ("_shadow_frame","_card_frame"):
            w = getattr(self, attr, None)
            if w and w.winfo_exists(): w.destroy()
            setattr(self, attr, None)

    def _make_card(self):
        self._clear()
        shadow = tk.Frame(self._outer, bg=C["shadow"])
        shadow.place(relx=0.5, rely=0.5, anchor="center",
                     relwidth=1.0, relheight=1.0, x=4, y=4)
        self._shadow_frame = shadow
        card = tk.Frame(self._outer, bg=C["surface"])
        card.place(relx=0.5, rely=0.5, anchor="center",
                   relwidth=1.0, relheight=1.0)
        self._card_frame = card
        return card

    def _left_panel(self, card, title, subtitle, accent=C["accent"]):
        """Dark gradient left panel."""
        pnl = tk.Frame(card, bg=C["surface2"], width=300)
        pnl.pack(side="left", fill="y"); pnl.pack_propagate(False)

        # Decorative canvas
        cv = tk.Canvas(pnl, bg=C["surface2"], highlightthickness=0)
        cv.place(relwidth=1, relheight=1)
        def _redraw(_, c=cv):
            c.delete("all")
            w, h = max(c.winfo_width(),1), max(c.winfo_height(),1)
            c.create_oval(w*.3,-h*.1,w*1.6,h*.55, fill=darken(C["surface2"],6), outline="")
            c.create_oval(-w*.2,h*.55,w*.7,h*1.2, fill=darken(C["surface2"],6), outline="")
        cv.bind("<Configure>", _redraw)

        # Avatar
        av = tk.Canvas(pnl, width=88, height=88, bg=C["surface2"], highlightthickness=0)
        av.pack(pady=(64, 16))
        av.create_oval(2,2,86,86, outline=accent, width=2)
        av.create_oval(20,10,68,54, fill=C["border2"], outline="")
        av.create_arc(12,46,76,86, start=0, extent=180, fill=C["border2"], outline="")

        tk.Label(pnl, text=title, bg=C["surface2"], fg=C["text"],
                 font=("Segoe UI", 22, "bold"), justify="center").pack(padx=16, pady=(0,8))
        tk.Label(pnl, text=subtitle, bg=C["surface2"], fg=C["muted"],
                 font=("Segoe UI", 10), wraplength=240, justify="center").pack(padx=14)

        # Bottom accent bar
        tk.Frame(pnl, bg=accent, height=3).pack(side="bottom", fill="x")

    def _right_panel(self, card):
        sf  = ScrollFrame(card, bg=C["surface"])
        sf.pack(side="left", fill="both", expand=True)
        pad = tk.Frame(sf.inner, bg=C["surface"])
        pad.pack(fill="both", expand=True, padx=52, pady=44)
        return pad

    # ── FORM HELPERS ─────────────────────────────────────────────────────────
    def _lbl(self, p, text, size=10, weight="bold", fg=None):
        tk.Label(p, text=text, bg=C["surface"], fg=fg or C["text"],
                 font=("Segoe UI", size, weight), anchor="w").pack(fill="x")

    def _field(self, parent, label_text, show=""):
        tk.Label(parent, text=label_text.upper(), bg=C["surface"], fg=C["muted"],
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", pady=(12,3))
        var = tk.StringVar()
        ent = DarkEntry(parent, textvariable=var, show=show)
        ent.pack(fill="x")
        err = tk.Label(parent, text="", bg=C["surface"], fg=C["red"],
                       font=("Segoe UI", 9), anchor="w")
        err.pack(fill="x", padx=2)
        return var, ent.entry, err

    def _field_pair(self, parent, l1, l2):
        row = tk.Frame(parent, bg=C["surface"]); row.pack(fill="x")
        def _half(container, lbl):
            tk.Label(container, text=lbl.upper(), bg=C["surface"], fg=C["muted"],
                     font=("Segoe UI",8,"bold"), anchor="w").pack(fill="x", pady=(12,3))
            var = tk.StringVar()
            ent = DarkEntry(container, textvariable=var)
            ent.pack(fill="x")
            err = tk.Label(container, text="", bg=C["surface"], fg=C["red"],
                           font=("Segoe UI",9), anchor="w")
            err.pack(fill="x", padx=2)
            return var, ent.entry, err
        lf = tk.Frame(row, bg=C["surface"]); lf.pack(side="left",fill="x",expand=True,padx=(0,8))
        rf = tk.Frame(row, bg=C["surface"]); rf.pack(side="left",fill="x",expand=True,padx=(8,0))
        return _half(lf, l1), _half(rf, l2)

    def _btn(self, parent, text, color, fg="white", cmd=None, outline=False):
        bg = color
        b = DarkButton(parent, text=text, command=cmd, bg=bg, fg=fg,
                       font=("Segoe UI",12,"bold"), padx=0, pady=12)
        if outline:
            b.config(highlightbackground=C["border2"], highlightthickness=1)
        b.pack(fill="x", pady=(6,0))
        return b

    def _divider(self, parent):
        f = tk.Frame(parent, bg=C["surface"]); f.pack(fill="x", pady=14)
        tk.Frame(f, bg=C["border2"], height=1).pack(side="left",fill="x",expand=True,pady=8)
        tk.Label(f, text=" or ", bg=C["surface"], fg=C["muted"], font=("Segoe UI",9)).pack(side="left")
        tk.Frame(f, bg=C["border2"], height=1).pack(side="left",fill="x",expand=True,pady=8)

    def _fade(self, callback, alpha=1.0, direction="out"):
        if direction=="out":
            if alpha>0.05:
                try: self.attributes("-alpha", alpha)
                except: pass
                self.after(16, lambda: self._fade(callback, alpha-0.09,"out"))
            else:
                self.attributes("-alpha",0); callback(); self._fade(None,0.0,"in")
        else:
            if alpha<1.0:
                try: self.attributes("-alpha", alpha)
                except: pass
                self.after(16, lambda: self._fade(None, alpha+0.09,"in"))
            else:
                self.attributes("-alpha",1.0)

    # ═════════════════════════════════════════
    #  LOGIN
    # ═════════════════════════════════════════
    def show_login(self):
        self._login_attempts = 0
        card  = self._make_card()
        self._left_panel(card, "Welcome\nBack",
                         "Sign in to manage your\nqueue & reservations")
        inner = self._right_panel(card)

        self._lbl(inner, "Sign In", 24, "bold")
        self._lbl(inner, "Enter your credentials to continue", 10, "normal", fg=C["muted"])
        tk.Frame(inner, bg=C["surface"], height=10).pack()

        self._le_v, self._le_e, self._le_err = self._field(inner, "Email Address")
        self._lp_v, self._lp_e, self._lp_err = self._field(inner, "Password", show="•")

        fl = tk.Frame(inner, bg=C["surface"]); fl.pack(fill="x", pady=(4,0))
        tk.Button(fl, text="Forgot password?", bg=C["surface"], fg=C["accent"],
                  relief="flat", bd=0, cursor="hand2",
                  font=("Segoe UI",9,"bold")).pack(side="right")

        self._btn(inner, "Sign In", C["accent"], cmd=self._do_login)
        self._divider(inner)
        self._btn(inner, "Create an Account", C["surface2"], fg=C["text"],
                  cmd=lambda: self._fade(self.show_register), outline=True)

    def _do_login(self):
        email, pw = self._le_v.get().strip(), self._lp_v.get()
        self._le_err.config(text=""); self._lp_err.config(text="")
        if not email or not pw: return
        user = find_user(email)
        if user and user["password"]==pw:
            self.show_toast(f"Welcome back, {user['first']}! 🎉", "success")
            self._current_user = user
            self.after(600, lambda: self._fade(self.show_reservation))
        else:
            self._le_err.config(text="⚠  Invalid email or password.")

    # ═════════════════════════════════════════
    #  REGISTER
    # ═════════════════════════════════════════
    def show_register(self):
        card  = self._make_card()
        self._left_panel(card, "Join\nUs Today",
                         "Create your WONGNORK account", accent=C["green"])
        inner = self._right_panel(card)

        self._lbl(inner, "Create Account", 22, "bold")
        tk.Frame(inner, bg=C["surface"], height=8).pack()

        (self._rf_v,self._rf_e,self._rf_err),(self._rl_v,self._rl_e,self._rl_err) = \
            self._field_pair(inner, "First Name", "Last Name")
        self._re_v,  self._re_e,  self._re_err  = self._field(inner, "Email Address")
        self._rp_v,  self._rp_e,  self._rp_err  = self._field(inner, "Password", show="•")
        self._rrp_v, self._rrp_e, self._rrp_err = self._field(inner, "Confirm Password", show="•")

        self._btn(inner, "Create Account", C["green"], cmd=self._do_register)
        self._divider(inner)
        self._btn(inner, "Back to Sign In", C["surface2"], fg=C["text"],
                  cmd=lambda: self._fade(self.show_login), outline=True)

    def _do_register(self):
        first = self._rf_v.get().strip()
        last  = self._rl_v.get().strip()
        email = self._re_v.get().strip()
        pw    = self._rp_v.get()
        repw  = self._rrp_v.get()
        if not email or pw!=repw: return
        add_user(first, last, email, pw)
        self.show_toast("Account created! 🎉", "success")
        self.after(1000, lambda: self._fade(self.show_login))

    # ═════════════════════════════════════════
    #  DASHBOARD SHELL
    # ═════════════════════════════════════════
    def show_reservation(self):
        self._clear()
        self._outer.place_forget()

        self._res_root = tk.Frame(self._body, bg=C["bg"])
        self._res_root.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_sidebar(self._res_root)

        main = tk.Frame(self._res_root, bg=C["bg"])
        main.pack(side="left", fill="both", expand=True)

        # Top bar
        topbar = tk.Frame(main, bg=C["surface"], height=64)
        topbar.pack(fill="x"); topbar.pack_propagate(False)
        tk.Frame(topbar, bg=C["border"], height=1).pack(side="bottom", fill="x")
        self._topbar_title = tk.Label(topbar, text="Dashboard", bg=C["surface"],
                                       fg=C["text"], font=("Segoe UI", 17, "bold"))
        self._topbar_title.pack(side="left", padx=36, pady=18)

        # User pill top-right
        user = self._current_user or {}
        name_str = f"{user.get('first','')} {user.get('last','')}".strip()
        tk.Label(topbar, text=f"👤  {name_str}", bg=C["surface"], fg=C["soft"],
                 font=("Segoe UI",10)).pack(side="right", padx=24)

        self._content_area = tk.Frame(main, bg=C["bg"])
        self._content_area.pack(fill="both", expand=True)
        self._show_reservations_content()

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=C["surface"], width=240)
        sb.pack(side="left", fill="y"); sb.pack_propagate(False)
        tk.Frame(sb, bg=C["border"], width=1).pack(side="right", fill="y")

        # Logo area
        logo_pad = tk.Frame(sb, bg=C["surface"])
        logo_pad.pack(fill="x", pady=(28,0), padx=22)

        cv = tk.Canvas(logo_pad, bg=C["surface"], highlightthickness=0, height=26, width=180)
        cv.pack(anchor="w")
        cv.create_text(0,13,text="WONG",font=("Segoe UI",15,"bold"),fill=C["text"],anchor="w")
        cv.create_text(58,13,text="NORK",font=("Segoe UI",15,"bold"),fill=C["accent"],anchor="w")

        tk.Label(logo_pad, text="SMART QUEUE PLATFORM", bg=C["surface"], fg=C["muted"],
                 font=("Segoe UI",7,"bold"), letterSpacing=4).pack(anchor="w", pady=(3,0))
        tk.Frame(sb, bg=C["border"], height=1).pack(fill="x", padx=18, pady=18)

        # Nav
        nav_defs = [
            ("📊", "All Queues",   False),
            ("🍽️", "Reservations", True),
            ("📍", "My Location",  False),
        ]
        self._nav_frames, self._nav_labels = {}, {}
        for icon, label, active in nav_defs:
            bg = C["accent_dk"] if active else C["surface"]
            nf = tk.Frame(sb, bg=bg, cursor="hand2")
            nf.pack(fill="x", padx=12, pady=2)

            inner = tk.Frame(nf, bg=bg, pady=11, padx=14)
            inner.pack(fill="x")

            icon_f = tk.Frame(inner, bg=lighten(bg,8) if active else C["surface2"],
                              width=30, height=30)
            icon_f.pack(side="left"); icon_f.pack_propagate(False)
            tk.Label(icon_f, text=icon, font=("Segoe UI",13),
                     bg=icon_f["bg"]).place(relx=.5,rely=.5,anchor="center")

            lbl_w = tk.Label(inner, text=label, bg=bg,
                             fg=C["text"] if active else C["soft"],
                             font=("Segoe UI",11,"bold" if active else "normal"),
                             anchor="w")
            lbl_w.pack(side="left", padx=10)

            self._nav_frames[label]  = (nf, inner, icon_f)
            self._nav_labels[label]  = lbl_w

            for w in [nf, inner, icon_f, lbl_w]:
                w.bind("<Button-1>", lambda e, l=label: self._nav_click(l))
                w.bind("<Enter>",    lambda e, n=nf, i=inner, _f=icon_f, l=lbl_w, a=active:
                       self._nav_hover(n, i, _f, l, True, a))
                w.bind("<Leave>",    lambda e, n=nf, i=inner, _f=icon_f, l=lbl_w, a=active:
                       self._nav_hover(n, i, _f, l, False, a))

        # Logout
        tk.Frame(sb, bg=C["border"], height=1).pack(side="bottom",fill="x",padx=18,pady=(0,4))
        logout_f = tk.Frame(sb, bg=C["surface"], cursor="hand2")
        logout_f.pack(side="bottom", fill="x", padx=12, pady=8)
        inner_l  = tk.Frame(logout_f, bg=C["surface"], pady=10, padx=14)
        inner_l.pack(fill="x")
        lo_lbl = tk.Label(inner_l, text="🚪  Log Out", bg=C["surface"], fg=C["muted"],
                          font=("Segoe UI",11))
        lo_lbl.pack(anchor="w")
        for w in [logout_f, inner_l, lo_lbl]:
            w.bind("<Button-1>", lambda _: self._logout())
            w.bind("<Enter>",    lambda e, ll=lo_lbl: ll.config(fg=C["red"]))
            w.bind("<Leave>",    lambda e, ll=lo_lbl: ll.config(fg=C["muted"]))

    def _nav_hover(self, nf, inner, icon_f, lbl, entering, active):
        if active: return
        if entering:
            nf.config(bg=C["surface2"]); inner.config(bg=C["surface2"])
            icon_f.config(bg=lighten(C["surface2"],4))
            lbl.config(bg=C["surface2"], fg=C["text"])
        else:
            nf.config(bg=C["surface"]); inner.config(bg=C["surface"])
            icon_f.config(bg=C["surface2"])
            lbl.config(bg=C["surface"], fg=C["soft"])

    def _nav_click(self, clicked_label):
        # Reset all
        for label, (nf, inner, icon_f) in self._nav_frames.items():
            is_active = (label == clicked_label)
            bg = C["accent_dk"] if is_active else C["surface"]
            nf.config(bg=bg); inner.config(bg=bg)
            icon_f.config(bg=lighten(bg,8) if is_active else C["surface2"])
            self._nav_labels[label].config(
                bg=bg, fg=C["text"] if is_active else C["soft"],
                font=("Segoe UI",11,"bold" if is_active else "normal"))
            for child in icon_f.winfo_children():
                child.config(bg=icon_f["bg"])

        if   clicked_label == "My Location":  self._show_gps_page()
        elif clicked_label == "Reservations": self._show_reservations_content()
        elif clicked_label == "All Queues":   self._show_all_queues_content()

    def _get_sorted_restaurants(self):
        distances = [(r, calculate_distance(self.user_lat, self.user_lon,
                                            d["coords"][0], d["coords"][1]))
                     for r, d in RESTAURANT_DATA.items()]
        distances.sort(key=lambda x: x[1])
        return distances

    # ═════════════════════════════════════════
    #  ALL QUEUES PAGE
    # ═════════════════════════════════════════
    def _show_all_queues_content(self):
        for w in self._content_area.winfo_children(): w.destroy()
        self._topbar_title.config(text="Live Restaurant Queues")

        sf  = ScrollFrame(self._content_area, bg=C["bg"])
        sf.pack(fill="both", expand=True)
        pad = tk.Frame(sf.inner, bg=C["bg"])
        pad.pack(fill="both", expand=True, padx=36, pady=28)

        # Section header
        sh = tk.Frame(pad, bg=C["bg"]); sh.pack(fill="x", pady=(0,16))
        tk.Label(sh, text="📊  สถานะคิวปัจจุบันของทุกร้าน",
                 bg=C["bg"], fg=C["text"], font=("Segoe UI",14,"bold")).pack(side="left")
        tk.Label(sh, text="  เรียงตามระยะทางจากจุดที่คุณอยู่",
                 bg=C["bg"], fg=C["muted"], font=("Segoe UI",10)).pack(side="left",pady=(4,0))

        for rest, dist in self._get_sorted_restaurants():
            waiting = len([r for r in RESERVATIONS
                           if r.get("restaurant")==rest and r.get("status")=="Waiting in Line"])
            self._queue_row(pad, rest, dist, waiting)

    def _queue_row(self, parent, rest, dist, waiting):
        card = tk.Frame(parent, bg=C["surface"], cursor="hand2")
        card.pack(fill="x", pady=(0,8))

        # Left accent bar
        bar_color = C["red"] if waiting > 0 else C["border2"]
        tk.Frame(card, bg=bar_color, width=3).pack(side="left", fill="y")

        inner = tk.Frame(card, bg=C["surface"])
        inner.pack(side="left", fill="both", expand=True, padx=20, pady=14)

        lf = tk.Frame(inner, bg=C["surface"]); lf.pack(side="left", fill="both", expand=True)
        tk.Label(lf, text=f"🏢  {rest}", bg=C["surface"], fg=C["text"],
                 font=("Segoe UI",12,"bold"), anchor="w").pack(anchor="w")
        tk.Label(lf, text=f"📍  ห่างจากคุณ {dist:.2f} km",
                 bg=C["surface"], fg=C["muted"], font=("Segoe UI",9)).pack(anchor="w", pady=(3,0))

        rf = tk.Frame(inner, bg=C["surface"]); rf.pack(side="right")
        color = C["red"] if waiting > 0 else C["green"]
        tk.Label(rf, text=f"กำลังรออยู่ {waiting} คิว",
                 bg=C["surface"], fg=color, font=("Segoe UI",12,"bold")).pack(anchor="e")

        # Hover
        def _on(e):
            card.config(bg=C["surface2"]); inner.config(bg=C["surface2"])
            lf.config(bg=C["surface2"]); rf.config(bg=C["surface2"])
            for ch in lf.winfo_children(): ch.config(bg=C["surface2"])
            for ch in rf.winfo_children(): ch.config(bg=C["surface2"])
        def _off(e):
            card.config(bg=C["surface"]); inner.config(bg=C["surface"])
            lf.config(bg=C["surface"]); rf.config(bg=C["surface"])
            for ch in lf.winfo_children(): ch.config(bg=C["surface"])
            for ch in rf.winfo_children(): ch.config(bg=C["surface"])
        for w in [card, inner, lf, rf]:
            w.bind("<Enter>", _on); w.bind("<Leave>", _off)

    # ═════════════════════════════════════════
    #  RESERVATIONS PAGE
    # ═════════════════════════════════════════
    def _show_reservations_content(self):
        for w in self._content_area.winfo_children(): w.destroy()
        self._topbar_title.config(text="Find & Book a Table")

        sf  = ScrollFrame(self._content_area, bg=C["bg"])
        sf.pack(fill="both", expand=True)
        pad = tk.Frame(sf.inner, bg=C["bg"])
        pad.pack(fill="both", expand=True, padx=36, pady=28)

        cols = tk.Frame(pad, bg=C["bg"]); cols.pack(fill="both", expand=True)
        left_col  = tk.Frame(cols, bg=C["bg"])
        left_col.pack(side="left", fill="both", expand=True, padx=(0,14))
        right_col = tk.Frame(cols, bg=C["bg"])
        right_col.pack(side="left", fill="both", expand=True, padx=(14,0))

        self._build_booking_form(left_col)
        self._build_bookings_list(right_col)

    def _card_section(self, parent, icon, title, accent=C["accent"]):
        """Create a styled card with header, return the body frame."""
        card = tk.Frame(parent, bg=C["surface"])
        card.pack(fill="x", pady=(0,16))

        # Header
        hdr = tk.Frame(card, bg=C["surface2"])
        hdr.pack(fill="x")
        icon_f = tk.Frame(hdr, bg=darken(accent,30), width=36, height=36)
        icon_f.pack(side="left", padx=18, pady=14); icon_f.pack_propagate(False)
        tk.Label(icon_f, text=icon, font=("Segoe UI",14),
                 bg=icon_f["bg"]).place(relx=.5,rely=.5,anchor="center")
        tk.Label(hdr, text=title, bg=C["surface2"], fg=C["text"],
                 font=("Segoe UI",13,"bold")).pack(side="left")
        tk.Frame(card, bg=C["border"], height=1).pack(fill="x")

        body = tk.Frame(card, bg=C["surface"])
        body.pack(fill="both", expand=True, padx=22, pady=18)
        return body

    def _build_booking_form(self, left_col):
        body = self._card_section(left_col, "📝", "New Booking")

        # Guest name
        self._res_name_v = tk.StringVar()
        self._form_label(body, "GUEST NAME")
        ent = DarkEntry(body, textvariable=self._res_name_v, placeholder="Enter your name…")
        ent.pack(fill="x", pady=(0,14))

        # Restaurant
        self._form_label(body, "SELECT RESTAURANT")
        sorted_rests = self._get_sorted_restaurants()
        self.dropdown_mapping = {f"{r} ({d:.1f} km)": r for r, d in sorted_rests}
        display_opts = list(self.dropdown_mapping.keys())
        self._res_restaurant_v = tk.StringVar(value=display_opts[0])
        cb = ttk.Combobox(body, textvariable=self._res_restaurant_v,
                          values=display_opts, state="readonly", font=("Segoe UI",11))
        cb.pack(fill="x", ipady=6, pady=(0,14))

        # Date + Time
        dr = tk.Frame(body, bg=C["surface"]); dr.pack(fill="x", pady=(0,14))
        lf = tk.Frame(dr, bg=C["surface"]); lf.pack(side="left",fill="x",expand=True,padx=(0,8))
        rf = tk.Frame(dr, bg=C["surface"]); rf.pack(side="left",fill="x",expand=True,padx=(8,0))

        self._form_label(lf, "DATE")
        df = tk.Frame(lf, bg=C["surface"]); df.pack(fill="x")
        now = datetime.datetime.now()
        self._res_day_v   = tk.StringVar(value=now.strftime("%d"))
        self._res_month_v = tk.StringVar(value=now.strftime("%m"))
        self._res_year_v  = tk.StringVar(value=now.strftime("%Y"))
        days   = [f"{i:02d}" for i in range(1,32)]
        months = [f"{i:02d}" for i in range(1,13)]
        years  = [str(now.year), str(now.year+1)]
        for var, vals, w in [(self._res_day_v,days,3),
                              (self._res_month_v,months,3),
                              (self._res_year_v,years,5)]:
            ttk.Combobox(df, textvariable=var, values=vals,
                         state="readonly", width=w, font=("Segoe UI",11)).pack(side="left",padx=(0,4))

        self._form_label(rf, "TIME")
        self._res_time_v = tk.StringVar(value=now.strftime("%H:00"))
        times = [f"{h:02d}:{m:02d}" for h in range(0,24) for m in (0,30)]
        ttk.Combobox(rf, textvariable=self._res_time_v, values=times,
                     state="readonly", font=("Segoe UI",11)).pack(fill="x", ipady=4)

        # Guests
        self._form_label(body, "GUESTS")
        self._res_guests_v = tk.StringVar(value="2")
        ttk.Combobox(body, textvariable=self._res_guests_v,
                     values=[str(i) for i in range(1,11)],
                     state="readonly", font=("Segoe UI",11)).pack(fill="x", ipady=6, pady=(0,20))

        # Button
        DarkButton(body, "✓   Confirm & Join Queue",
                   command=self._do_reserve, bg=C["accent"],
                   font=("Segoe UI",12,"bold"), pady=13).pack(fill="x")

    def _form_label(self, parent, text):
        tk.Label(parent, text=text, bg=C["surface"], fg=C["muted"],
                 font=("Segoe UI",8,"bold"), anchor="w").pack(fill="x", pady=(0,4))

    def _do_reserve(self):
        user = self._current_user or {}
        name = self._res_name_v.get().strip() or user.get("first","")
        selected_display = self._res_restaurant_v.get()
        rest = self.dropdown_mapping.get(selected_display, selected_display.split(" (")[0])
        try:
            year, month, day = int(self._res_year_v.get()), int(self._res_month_v.get()), int(self._res_day_v.get())
            hh, mm = map(int, self._res_time_v.get().split(":"))
            selected_dt = datetime.datetime(year, month, day, hh, mm)
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please check the date format.")
            return
        if selected_dt < datetime.datetime.now():
            messagebox.showwarning("Invalid Time", "Cannot book a time in the past.")
            return
        date_str = f"{year}-{month:02d}-{day:02d}"
        add_reservation(user.get("email",""), name, rest, date_str,
                        self._res_time_v.get(), self._res_guests_v.get(), "")
        self.show_toast(f"Joined queue at {rest}! 🎉", "success")
        self._refresh_bookings()

    def _build_bookings_list(self, right_col):
        body = self._card_section(right_col, "📋", "Live Queue & History", accent=C["green"])
        self._bookings_frame = body
        self._refresh_bookings()

    def _refresh_bookings(self):
        if not hasattr(self, "_bookings_frame"): return
        for w in self._bookings_frame.winfo_children(): w.destroy()
        user     = self._current_user or {}
        bookings = get_user_reservations(user.get("email",""))

        if not bookings:
            tk.Label(self._bookings_frame, text="No queues yet.  🍽️",
                     bg=C["surface"], fg=C["muted"],
                     font=("Segoe UI",11)).pack(pady=40)
            return

        for res in reversed(bookings):
            status = res.get("status","Waiting in Line")
            self._booking_row(self._bookings_frame, res, status)

    def _booking_row(self, parent, res, status):
        row = tk.Frame(parent, bg=C["surface2"])
        row.pack(fill="x", pady=(0,10))
        # Accent top strip
        strip_color = C["accent"] if "Waiting" in status else (C["green"] if status=="Completed" else C["border2"])
        tk.Frame(row, bg=strip_color, height=2).pack(fill="x")

        inner = tk.Frame(row, bg=C["surface2"], pady=12, padx=16)
        inner.pack(fill="x")

        lf = tk.Frame(inner, bg=C["surface2"]); lf.pack(side="left", fill="x", expand=True)
        rest_name = res.get("restaurant","Unknown")
        tk.Label(lf, text=f"🏢  {rest_name}", bg=C["surface2"], fg=C["text"],
                 font=("Segoe UI",12,"bold"), anchor="w").pack(anchor="w")

        if status in ("Waiting in Line","Confirmed"):
            ahead = sum(1 for r in RESERVATIONS
                        if r.get("restaurant")==rest_name
                        and r.get("status")=="Waiting in Line"
                        and r["id"] < res["id"])
            color = C["red"] if ahead > 0 else C["green"]
            tk.Label(lf, text=f"🎫  Queue: {res.get('queue_number','N/A')}   |   ⏳  {ahead} ahead",
                     bg=C["surface2"], fg=color,
                     font=("Segoe UI",10,"bold"), anchor="w").pack(anchor="w", pady=(3,5))

        tk.Label(lf, text=f"📅  {res['date']}   🕐  {res['time']}   👥  {res['guests']} pax",
                 bg=C["surface2"], fg=C["muted"],
                 font=("Segoe UI",9), anchor="w").pack(anchor="w")

        rf = tk.Frame(inner, bg=C["surface2"])
        rf.pack(side="right", fill="y", padx=(12,0))

        if status == "Completed":
            rating = res.get("rating",0)
            stars  = "★"*rating + "☆"*(5-rating)
            tk.Label(rf, text="Completed", bg=C["surface2"], fg=C["green"],
                     font=("Segoe UI",10,"bold")).pack(anchor="e")
            tk.Label(rf, text=stars, bg=C["surface2"], fg=C["gold"],
                     font=("Segoe UI",15)).pack(anchor="e")
        elif status == "Cancelled":
            tk.Label(rf, text="Cancelled", bg=C["surface2"], fg=C["muted"],
                     font=("Segoe UI",10,"bold")).pack(anchor="e")
        else:
            tk.Label(rf, text="● Waiting", bg=C["surface2"], fg=C["gold"],
                     font=("Segoe UI",9,"bold")).pack(anchor="e", pady=(0,8))
            bf = tk.Frame(rf, bg=C["surface2"]); bf.pack(anchor="e")
            DarkButton(bf, "⭐  Finish & Rate",
                       command=lambda rid=res["id"], rn=rest_name: self._show_feedback_popup(rid, rn),
                       bg=C["green"], fg="#0d1a12", font=("Segoe UI",9,"bold"),
                       pady=6, padx=10).pack(side="left", padx=(0,8))
            DarkButton(bf, "Cancel",
                       command=lambda rid=res["id"]: self._cancel_res(rid),
                       bg=C["surface"], fg=C["red"],
                       font=("Segoe UI",9), pady=6, padx=8).pack(side="left")

    def _cancel_res(self, res_id):
        cancel_reservation(res_id)
        self.show_toast("Queue cancelled.", "success")
        self._refresh_bookings()

    # ═════════════════════════════════════════
    #  FEEDBACK POPUP
    # ═════════════════════════════════════════
    def _show_feedback_popup(self, res_id, rest_name):
        top = tk.Toplevel(self)
        top.title("Rate your experience")
        top.geometry("420x400")
        top.configure(bg=C["surface"])
        top.resizable(False, False)
        top.transient(self); top.grab_set()
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - 420) // 2
        y = self.winfo_y() + (self.winfo_height() - 400) // 2
        top.geometry(f"+{x}+{y}")

        # Header strip
        hdr = tk.Frame(top, bg=C["accent"], height=4)
        hdr.pack(fill="x")

        tk.Label(top, text="How was your experience?", bg=C["surface"], fg=C["text"],
                 font=("Segoe UI",15,"bold")).pack(pady=(24,4))
        tk.Label(top, text=f"at {rest_name}", bg=C["surface"], fg=C["muted"],
                 font=("Segoe UI",10)).pack(pady=(0,20))

        star_frame = tk.Frame(top, bg=C["surface"]); star_frame.pack()
        self._current_rating = 0
        star_labels = []

        def _set(idx):
            self._current_rating = idx
            for i, lbl in enumerate(star_labels, 1):
                lbl.config(text="★" if i<=idx else "☆",
                           fg=C["gold"] if i<=idx else C["border2"])

        for i in range(1,6):
            lbl = tk.Label(star_frame, text="☆", bg=C["surface"], fg=C["border2"],
                           font=("Segoe UI",28), cursor="hand2")
            lbl.pack(side="left", padx=4)
            lbl.bind("<Button-1>", lambda e, idx=i: _set(idx))
            star_labels.append(lbl)

        tk.Label(top, text="Comment (optional)", bg=C["surface"], fg=C["muted"],
                 font=("Segoe UI",9,"bold"), anchor="w").pack(anchor="w", padx=32, pady=(18,4))
        comment_box = tk.Text(top, height=3, bg=C["surface2"], fg=C["text"],
                              insertbackground=C["accent"],
                              font=("Segoe UI",11), relief="flat", bd=8)
        comment_box.pack(fill="x", padx=32)

        def _submit():
            if self._current_rating == 0:
                messagebox.showwarning("Rating Required","Please select a star rating.", parent=top)
                return
            submit_feedback(res_id, self._current_rating,
                            comment_box.get("1.0","end-1c").strip())
            top.destroy()
            self.show_toast("Thanks for your feedback! 🙏", "success")
            self._refresh_bookings()

        DarkButton(top, "Submit Feedback", command=_submit,
                   bg=C["accent"], font=("Segoe UI",11,"bold"),
                   pady=12, padx=0).pack(fill="x", padx=32, pady=24)

    # ═════════════════════════════════════════
    #  GPS / MAP PAGE
    # ═════════════════════════════════════════
    def _show_gps_page(self):
        for w in self._content_area.winfo_children(): w.destroy()
        self._topbar_title.config(text="📍 My Location")

        if not HAS_MAP:
            ef = tk.Frame(self._content_area, bg=C["bg"])
            ef.pack(expand=True)
            tk.Label(ef, text="⚠️  Map Library Missing", bg=C["bg"], fg=C["red"],
                     font=("Segoe UI",18,"bold")).pack(pady=14)
            tk.Label(ef, text="Install it with:", bg=C["bg"], fg=C["text"],
                     font=("Segoe UI",12)).pack(pady=4)
            tk.Label(ef, text="pip install tkintermapview", bg=C["surface2"],
                     fg=C["accent"], font=("Courier",14,"bold"),
                     padx=12, pady=8).pack(pady=10)
            return

        outer = tk.Frame(self._content_area, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=36, pady=24)

        # Info card
        info_card = tk.Frame(outer, bg=C["surface"])
        info_card.pack(fill="x", pady=(0,16))
        tk.Frame(info_card, bg=C["accent"], height=3).pack(fill="x")
        ic_inner = tk.Frame(info_card, bg=C["surface"])
        ic_inner.pack(fill="x", padx=22, pady=14)
        tk.Label(ic_inner,
                 text="📍  คลิกบนแผนที่เพื่อปักหมุดตำแหน่งของคุณ  |  คลิกร้านเพื่อดูข้อมูล",
                 bg=C["surface"], fg=C["soft"], font=("Segoe UI",10)).pack(side="left")
        self._coords_lbl = tk.Label(ic_inner,
                                     text=f"Lat {self.user_lat:.5f}  ·  Lon {self.user_lon:.5f}",
                                     bg=C["surface"], fg=C["accent"],
                                     font=("Segoe UI",10,"bold"))
        self._coords_lbl.pack(side="right")

        map_frame = tk.Frame(outer, bg=C["border"], bd=1)
        map_frame.pack(fill="both", expand=True)
        self.map_widget = tkintermapview.TkinterMapView(map_frame, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_position(self.user_lat, self.user_lon)
        self.map_widget.set_zoom(13)

        for rest, data in RESTAURANT_DATA.items():
            lat, lon = data["coords"]
            marker = self.map_widget.set_marker(lat, lon, text=rest,
                                                 marker_color_circle=C["accent"],
                                                 marker_color_outside=C["accent_dk"],
                                                 command=self._on_restaurant_click)
            marker.rest_name = rest

        self.current_marker = self.map_widget.set_marker(
            self.user_lat, self.user_lon, text="📍 คุณอยู่ที่นี่",
            marker_color_circle=C["green"], marker_color_outside=C["green2"])
        self.map_widget.add_left_click_map_command(self._on_map_click)

    def _on_restaurant_click(self, marker):
        rest_name = getattr(marker, "rest_name", marker.text)
        if rest_name not in RESTAURANT_DATA: return
        data = RESTAURANT_DATA[rest_name]

        top = tk.Toplevel(self)
        top.title("Restaurant Info")
        top.geometry("400x260")
        top.configure(bg=C["surface"])
        top.resizable(False,False)
        top.transient(self); top.grab_set()
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()-400)//2
        y = self.winfo_y() + (self.winfo_height()-260)//2
        top.geometry(f"+{x}+{y}")

        tk.Frame(top, bg=C["accent"], height=3).pack(fill="x")
        tk.Label(top, text=f"🏢  {rest_name}", bg=C["surface"], fg=C["text"],
                 font=("Segoe UI",14,"bold")).pack(pady=(20,12))

        info = tk.Frame(top, bg=C["surface2"], padx=16, pady=14)
        info.pack(fill="x", padx=24)
        tk.Label(info, text=f"🍽️  {data['desc']}", bg=C["surface2"], fg=C["soft"],
                 font=("Segoe UI",10), wraplength=320, justify="left").pack(anchor="w", pady=(0,8))
        tk.Label(info, text=f"⏰  {data['hours']}", bg=C["surface2"], fg=C["accent"],
                 font=("Segoe UI",10,"bold")).pack(anchor="w")

        DarkButton(top, "Close", command=top.destroy, bg=C["surface2"],
                   fg=C["soft"], font=("Segoe UI",10,"bold"),
                   pady=9, padx=20).pack(pady=16)

    def _on_map_click(self, coords):
        lat, lon = coords
        self.user_lat, self.user_lon = lat, lon
        if hasattr(self,"current_marker") and self.current_marker:
            self.current_marker.delete()
        self.current_marker = self.map_widget.set_marker(
            lat, lon, text="📍 คุณอยู่ที่นี่",
            marker_color_circle=C["green"], marker_color_outside=C["green2"])
        self._coords_lbl.config(text=f"Lat {lat:.5f}  ·  Lon {lon:.5f}")
        self.show_toast("📌 อัปเดตตำแหน่งของคุณแล้ว!", "success")

    # ═════════════════════════════════════════
    #  LOGOUT
    # ═════════════════════════════════════════
    def _logout(self):
        self._current_user = None
        if hasattr(self,"_res_root") and self._res_root.winfo_exists():
            self._res_root.destroy()
        self._outer.place(relx=0.5, rely=0.5, anchor="center",
                          relwidth=0.94, relheight=0.92)
        self._fade(self.show_login)


if __name__ == "__main__":
    app = App()
    app.mainloop()