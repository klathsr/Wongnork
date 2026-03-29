"""
WONGNORK - My Location Page (PySide6)
Uses folium + QWebEngineView for an interactive map.
Install: pip install PySide6 folium

Falls back to a coordinate-picker UI if folium is not installed.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QApplication, QMainWindow
)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QFont, QColor, QPalette

from shared import (
    BG_DARK, BG_CARD, BG_CARD_HOV, ACCENT_ORANGE, ACCENT_GREEN,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, FONT_FAMILY,
    RESTAURANT_DATA
)

def _font(size: int, weight=QFont.Weight.Normal) -> QFont:
    return QFont(FONT_FAMILY, size, weight)

# Optional deps
try:
    import folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False


# ═══════════════════════════════════════════════════════════════════════════════
# Info bar
# ═══════════════════════════════════════════════════════════════════════════════
class _InfoBar(QFrame):
    def __init__(self, lat: float, lon: float):
        super().__init__()
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-radius: 10px;
                border-left: 3px solid {ACCENT_ORANGE};
            }}
        """)
        row = QHBoxLayout(self)
        row.setContentsMargins(20, 0, 20, 0)

        icon = QLabel("📍")
        icon.setFont(_font(22))
        icon.setStyleSheet("background: transparent;")

        self._coord_lbl = QLabel(self._fmt(lat, lon))
        self._coord_lbl.setFont(_font(13, QFont.Weight.Medium))
        self._coord_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")

        hint = QLabel("คลิกบนแผนที่เพื่อปักหมุดตำแหน่งของคุณ")
        hint.setFont(_font(11))
        hint.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")

        row.addWidget(icon)
        row.addSpacing(8)
        row.addWidget(self._coord_lbl)
        row.addStretch()
        row.addWidget(hint)

    def update_coords(self, lat: float, lon: float):
        self._coord_lbl.setText(self._fmt(lat, lon))

    @staticmethod
    def _fmt(lat, lon) -> str:
        return f"Lat {lat:.5f}  •  Lon {lon:.5f}"


# ═══════════════════════════════════════════════════════════════════════════════
# Map widget (folium + WebEngine)
# ═══════════════════════════════════════════════════════════════════════════════
class _FoliumMap(QWidget):
    location_changed = Signal(float, float)

    def __init__(self, lat: float, lon: float):
        super().__init__()
        self._lat = lat
        self._lon = lon

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._view = QWebEngineView()
        layout.addWidget(self._view)

        self._render_map()
        
        self._view.titleChanged.connect(self._on_title)

    def _render_map(self):
        m = folium.Map(location=[self._lat, self._lon], zoom_start=14,
                       tiles="CartoDB dark_matter")

        folium.Marker(
            [self._lat, self._lon],
            tooltip="📍 คุณอยู่ที่นี่",
            icon=folium.Icon(color="green", icon="home", prefix="fa")
        ).add_to(m)

        for name, data in RESTAURANT_DATA.items():
            lat, lon = data["coords"]
            folium.Marker(
                [lat, lon],
                tooltip=f"🍽 {name}\n⏰ {data['hours']}",
                popup=folium.Popup(
                    f"<b>{name}</b><br>{data['desc']}<br>⏰ {data['hours']}",
                    max_width=260
                ),
                icon=folium.Icon(color="orange", icon="cutlery", prefix="fa")
            ).add_to(m)

        click_js = """
        <script>
        function attachMapClick() {
            if (typeof window !== 'undefined' && typeof L !== 'undefined') {
                for (var key in window) {
                    if (key.startsWith("map_") && window[key] instanceof L.Map) {
                        window[key].on('click', function(e) {
                            document.title = e.latlng.lat + ',' + e.latlng.lng;
                        });
                        return; // Successfully attached
                    }
                }
            }
            // ถ้าเน็ตช้า แผนที่ยังไม่มา ให้วนลูปเช็คใหม่ทุก 100ms
            setTimeout(attachMapClick, 100);
        }
        attachMapClick();
        </script>
        """
        m.get_root().html.add_child(folium.Element(click_js))

        html_data = m.get_root().render()
        self._view.setHtml(html_data, QUrl("https://localhost"))

    def _on_title(self, title: str):
        try:
            lat, lon = map(float, title.split(","))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                self._lat = lat; self._lon = lon
                self.location_changed.emit(lat, lon)
        except Exception:
            pass

    def update_location(self, lat: float, lon: float):
        self._lat = lat
        self._lon = lon
        self._render_map()


# ═══════════════════════════════════════════════════════════════════════════════
# Fallback when folium/WebEngine is missing
# ═══════════════════════════════════════════════════════════════════════════════
class _FallbackMap(QWidget):
    location_changed = Signal(float, float)

    def __init__(self, lat: float, lon: float):
        super().__init__()
        self._lat = lat; self._lon = lon
        self.setStyleSheet(f"background: {BG_CARD}; border-radius: 10px;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        warn = QLabel("🗺️")
        warn.setFont(_font(52))
        warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warn.setStyleSheet("background: transparent;")

        msg = QLabel("Interactive map requires additional libraries.")
        msg.setFont(_font(14, QFont.Weight.Medium))
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")

        cmd = QLabel("pip install folium PySide6")
        cmd.setFont(_font(12))
        cmd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cmd.setStyleSheet(f"""
            background: {BG_DARK}; color: {ACCENT_ORANGE};
            border-radius: 8px; padding: 10px 20px;
            font-family: "Courier New";
        """)

        layout.addWidget(warn)
        layout.addSpacing(12)
        layout.addWidget(msg)
        layout.addSpacing(12)
        layout.addWidget(cmd)

    def update_location(self, lat: float, lon: float):
        self._lat = lat; self._lon = lon


# ═══════════════════════════════════════════════════════════════════════════════
# My Location Page
# ═══════════════════════════════════════════════════════════════════════════════
class MyLocationPage(QWidget):
    location_updated = Signal(float, float)   # emitted when user pins a new location

    def __init__(self, user_lat: float = 16.4550, user_lon: float = 102.8240, parent=None):
        super().__init__(parent)
        self._lat = user_lat
        self._lon = user_lon
        self.setStyleSheet(f"background: {BG_DARK};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(0)

        # Title
        title_row = QHBoxLayout()
        title = QLabel("My Location")
        title.setFont(_font(28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)
        layout.addSpacing(20)

        # Info bar
        self._info_bar = _InfoBar(user_lat, user_lon)
        layout.addWidget(self._info_bar)
        layout.addSpacing(16)

        # Map
        if HAS_FOLIUM and HAS_WEBENGINE:
            self._map = _FoliumMap(user_lat, user_lon)
        else:
            self._map = _FallbackMap(user_lat, user_lon)

        self._map.location_changed.connect(self._on_location_changed)
        layout.addWidget(self._map)

    def _on_location_changed(self, lat: float, lon: float):
        self._lat = lat; self._lon = lon
        self._info_bar.update_coords(lat, lon)
        self.location_updated.emit(lat, lon)
        
        self._map.update_location(lat, lon) 

    @property
    def lat(self): return self._lat

    @property
    def lon(self): return self._lon


# Dev preview
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT_FAMILY, 12))
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG_DARK))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    app.setPalette(palette)

    win = QMainWindow()
    win.setWindowTitle("My Location — Dev Preview")
    win.resize(1100, 720)
    win.setCentralWidget(MyLocationPage())
    win.show()
    sys.exit(app.exec())