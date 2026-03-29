"""
WONGNORK - Shared constants, restaurant data, and database helpers.
Import this in every page file.
"""

import re, json, os, math, datetime

# ── Colour Palette ────────────────────────────────────────────────────────────
BG_DARK        = "#0f1117"
BG_SIDEBAR     = "#13151e"
BG_CARD        = "#1a1d27"
BG_CARD_HOV    = "#1f2235"
BG_ACTIVE      = "#2a1f14"
ACCENT_ORANGE  = "#e8712a"
ACCENT_GREEN   = "#22c55e"
ACCENT_GREEN2  = "#16a34a"
ACCENT_RED     = "#ef4444"
ACCENT_BLUE    = "#3b82f6"
ACCENT_GOLD    = "#f59e0b"
TEXT_PRIMARY   = "#f0f2f8"
TEXT_SECONDARY = "#8b90a7"
TEXT_MUTED     = "#555a72"
BORDER         = "#252839"
INPUT_BG       = "#1e2235"

FONT_FAMILY = "Segoe UI"

# ── Restaurant Data ───────────────────────────────────────────────────────────
RESTAURANT_DATA = {
    "สุกี้ตี๋น้อย (สาขาตลาดอู้ฟู่)": {
        "coords": (16.412581835185925, 102.8156580139527),
        "desc":   "บุฟเฟต์สุกี้ยากี้ / ชาบู ยอดฮิต (ตั้งอยู่ในตลาดอู้ฟู่ ริมถนนมิตรภาพ)",
        "hours":  "11:00 - 05:00", "emoji": "🍲",
    },
    "สุกี้ตี๋น้อย (สาขาโลตัส ขอนแก่น 2)": {
        "coords": (16.494814100794112, 102.83182515120313),
        "desc":   "บุฟเฟต์สุกี้ยากี้ / ชาบู (ตั้งอยู่ในโลตัส ศิลา)",
        "hours":  "11:00 - 05:00", "emoji": "🍲",
    },
    "สุกี้ตี๋น้อย (สาขาศรีจันทร์)": {
        "coords": (16.43501227281179, 102.8572306522941),
        "desc":   "บุฟเฟต์สุกี้ยากี้ / ชาบู (ตั้งอยู่โครงการตึกศรีจันทร์สแควร์ ในเมือง)",
        "hours":  "11:00 - 05:00", "emoji": "🍲",
    },
    "โบนัสสุกี้ (สาขาแฟรี่พลาซ่า)": {
        "coords": (16.43192580309003, 102.83258394753588),
        "desc":   "บุฟเฟต์ชาบู-สุกี้ยากี้ เจ้าดังขวัญใจชาวขอนแก่น (ชั้น 2 ห้างแฟรี่พลาซ่า)",
        "hours":  "10:30 - 21:00", "emoji": "🥘",
    },
    "หมูกระทะเฮียเปียว (กังสดาล)": {
        "coords": (16.460612551887007, 102.8272372935368),
        "desc":   "หมูกระทะแบบชั่งกิโลในตำนาน น้ำจิ้มสูตรเด็ด (โซนกังสดาล มข.)",
        "hours":  "16:00 - 23:00", "emoji": "🥩",
    },
    "Style Soup ซุปหม่าล่า (กังสดาล)": {
        "coords": (16.457412807112917, 102.8241600627709),
        "desc":   "หม่าล่าทั่งแบบตักขีด ซุปกระดูกวัว ซุปนมเข้มข้น (โซนกังสดาล มข.)",
        "hours":  "11:00 - 22:00", "emoji": "🍜",
    },
    "เฟิงฟู่ หมูกระทะ Fengfu Mookata (หลังมอ)": {
        "coords": (16.4824476065446, 102.81224826095774),
        "desc":   "หมูกระทะ น้ำจิ้มสูตรเด็ด กุ้งหมึกจัดเต็ม (โซนหลังมอ มข.)",
        "hours":  "16:30 - 00:00", "emoji": "🍖",
    },
    "หมีกะหมู ชาบู&ปิ้งย่าง (หลังมอ)": {
        "coords": (16.489822806304286, 102.82004481481545),
        "desc":   "หมูกระทะบุฟเฟต์ราคาประหยัด ขวัญใจวัยรุ่นหลังมอ (โซนหลังมอ มข.)",
        "hours":  "16:30 - 22:00", "emoji": "🐷",
    },
    "แจ่วฮ้อนอภิรมย์ สาขา มข.": {
        "coords": (16.460328616609143, 102.83063009116643),
        "desc":   "แจ่วฮ้อนรสเด็ด น้ำซุปสมุนไพรเข้มข้น เนื้อคุณภาพดี (โซน มข.)",
        "hours":  "11:00 - 22:00", "emoji": "🍜",
    },
    "โต้งปลาเผา (โซนในเมือง)": {
        "coords": (16.42255541255355, 102.83728596841723),
        "desc":   "ร้านอาหารอีสาน รสแซ่บ ปลาช่อนเผาเกลือ (ริมถนนศรีนวล)",
        "hours":  "12:00 - 22:00", "emoji": "🐟",
    },
    "Riburs BBQ": {
        "coords": (16.46285789361636, 102.84449397411916),
        "desc":   "ภัตตาคารอาหารอเมริกัน",
        "hours":  "18:00 - 23:00", "emoji": "🥩",
    },
    "เอมโอช (โซนในเมือง)": {
        "coords": (16.435859552566374, 102.83621939299617),
        "desc":   "ร้านอาหารเช้าชื่อดัง ไข่กระทะ กวยจั๊บญวน (ถนนกลางเมือง)",
        "hours":  "04:00 - 13:00", "emoji": "🍳",
    },
    "ฮาลองเบย์ อาหารเวียดนาม (โซนในเมือง)": {
        "coords": (16.424158982736248, 102.84022958957652),
        "desc":   "ภัตตาคารอาหารเวียดนาม",
        "hours":  "09:30 - 21:30", "emoji": "🍱",
    },
    "VT แหนมเนือง ขอนแก่น": {
        "coords": (16.444298003901313, 102.79633422554072),
        "desc":   "อาหารเวียดนาม แหนมเนืองชุดใหญ่ ผักสดสะอาด (ถนนหน้าเมือง)",
        "hours":  "08:00 - 19:30", "emoji": "🥗",
    },
    "ประสิทธิ์โภชนา": {
        "coords": (16.43433725837038, 102.83336809242859),
        "desc":   "เนื้อย่างระดับตำนานของเมืองขอนแก่น (ถนนอำมาตย์)",
        "hours":  "09:30 - 14:00", "emoji": "🍽",
    },
}

RESTAURANT_LIST = list(RESTAURANT_DATA.keys())

def calculate_distance(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dLon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_sorted_restaurants(user_lat: float, user_lon: float):
    """Return list of (name, dist_km) sorted by distance."""
    result = []
    for rest, data in RESTAURANT_DATA.items():
        dist = calculate_distance(user_lat, user_lon, *data["coords"])
        result.append((rest, dist))
    result.sort(key=lambda x: x[1])
    return result

# ── User Database ─────────────────────────────────────────────────────────────
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
_DEFAULT_USERS = [
    {"first": "Demo", "last": "User", "email": "demo@wongnork.com", "password": "demo123"},
]

def _load_db():
    if not os.path.exists(DB_FILE):
        _save_db(_DEFAULT_USERS); return list(_DEFAULT_USERS)
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

def valid_email(e: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", e.strip()))

def find_user(email: str):
    return next((u for u in USER_DB if u["email"].lower() == email.strip().lower()), None)

def add_user(first, last, email, password):
    user = {"first": first, "last": last, "email": email.lower(), "password": password}
    USER_DB.append(user)
    _save_db(USER_DB)
    return user

# ── Reservation Database ──────────────────────────────────────────────────────
RES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reservations.json")

def _load_res():
    if not os.path.exists(RES_FILE): return []
    try:
        with open(RES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def _save_res(reservations):
    try:
        with open(RES_FILE, "w", encoding="utf-8") as f:
            json.dump(reservations, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

RESERVATIONS = _load_res()

def add_reservation(user_email, name, restaurant, date, time, guests, note):
    rest_reservations = [r for r in RESERVATIONS if r.get("restaurant") == restaurant]
    queue_number = f"A{len(rest_reservations) + 1:03d}"
    res = {
        "id":           len(RESERVATIONS) + 1,
        "email":        user_email.lower(),
        "name":         name,
        "restaurant":   restaurant,
        "date":         date,
        "time":         time,
        "guests":       guests,
        "note":         note,
        "queue_number": queue_number,
        "created":      datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status":       "Waiting in Line",
        "rating":       0,
        "feedback":     "",
    }
    RESERVATIONS.append(res)
    _save_res(RESERVATIONS)
    return res

def get_user_reservations(user_email: str):
    return [r for r in RESERVATIONS if r["email"] == user_email.lower()]

def cancel_reservation(res_id: int):
    for r in RESERVATIONS:
        if r["id"] == res_id:
            r["status"] = "Cancelled"
    _save_res(RESERVATIONS)

def submit_feedback(res_id: int, rating: int, comment: str):
    for r in RESERVATIONS:
        if r["id"] == res_id:
            r["status"]   = "Completed"
            r["rating"]   = rating
            r["feedback"] = comment
    _save_res(RESERVATIONS)

def get_waiting_count(restaurant: str) -> int:
    return sum(1 for r in RESERVATIONS
               if r.get("restaurant") == restaurant
               and r.get("status") == "Waiting in Line")
