"""
M.I.L.O — Machine Intelligence Liaison Operator
src/ui/main_window.py

Main PySide6 Window — Neon-Cyan Glassmorphism shell.
Hosts: Chat panel · Visualizer panel · System status bar.
Voice commands are routed through VoiceEngine (no UI buttons for camera/screen).
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPalette, QFont, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QTextEdit, QLineEdit, QSplitter, QFrame, QGraphicsDropShadowEffect,
    QScrollArea, QSizePolicy,
)

from src.ui.visualizer import VisualizerWidget


# ──────────────────────────────────────────────────────────────────────────────
# Global stylesheet  (Neon-Cyan Glassmorphism)
# ──────────────────────────────────────────────────────────────────────────────

MILO_QSS = """
/* ── Root ─────────────────────────────────────────────────────── */
QMainWindow, QWidget#root {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #020c18,
        stop:0.5 #040d1f,
        stop:1 #010a14
    );
}

/* ── Glass panels ─────────────────────────────────────────────── */
QFrame#glassPanel {
    background: rgba(0, 200, 220, 0.04);
    border: 1px solid rgba(0, 255, 231, 0.18);
    border-radius: 16px;
}
QFrame#glassPanel:hover {
    border: 1px solid rgba(0, 255, 231, 0.35);
}

/* ── Chat output ──────────────────────────────────────────────── */
QTextEdit#chatLog {
    background: rgba(0, 15, 30, 0.60);
    border: 1px solid rgba(0, 255, 231, 0.12);
    border-radius: 12px;
    color: #cff8f4;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 13px;
    padding: 14px;
    selection-background-color: rgba(0, 255, 231, 0.25);
}

/* ── Input bar ────────────────────────────────────────────────── */
QLineEdit#chatInput {
    background: rgba(0, 255, 231, 0.05);
    border: 1px solid rgba(0, 255, 231, 0.30);
    border-radius: 24px;
    color: #e0ffff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    padding: 10px 20px;
    selection-background-color: rgba(0, 255, 231, 0.25);
}
QLineEdit#chatInput:focus {
    border: 1px solid rgba(0, 255, 231, 0.70);
    background: rgba(0, 255, 231, 0.08);
}
QLineEdit#chatInput::placeholder {
    color: rgba(0, 200, 200, 0.40);
}

/* ── Status bar ───────────────────────────────────────────────── */
QLabel#statusDot {
    color: #00ffe7;
    font-size: 10px;
}
QLabel#statusText {
    color: rgba(0, 255, 231, 0.60);
    font-family: 'Rajdhani', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
}

/* ── Section headers ──────────────────────────────────────────── */
QLabel#panelTitle {
    color: #00ffe7;
    font-family: 'Orbitron', 'Rajdhani', monospace;
    font-size: 11px;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    padding: 8px 14px 4px;
}

/* ── Scrollbars ───────────────────────────────────────────────── */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(0, 255, 231, 0.25);
    border-radius: 3px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(0, 255, 231, 0.50);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

/* ── Splitter ─────────────────────────────────────────────────── */
QSplitter::handle {
    background: rgba(0, 255, 231, 0.10);
    width: 2px;
}
QSplitter::handle:hover {
    background: rgba(0, 255, 231, 0.35);
}
"""


# ──────────────────────────────────────────────────────────────────────────────
# Glass panel factory
# ──────────────────────────────────────────────────────────────────────────────

def make_glass_panel() -> QFrame:
    panel = QFrame()
    panel.setObjectName("glassPanel")
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(40)
    shadow.setColor(QColor(0, 255, 231, 35))
    shadow.setOffset(0, 0)
    panel.setGraphicsEffect(shadow)
    return panel


# ──────────────────────────────────────────────────────────────────────────────
# Chat log widget
# ──────────────────────────────────────────────────────────────────────────────

class ChatLog(QTextEdit):
    """Read-only chat display with MILO-styled message formatting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatLog")
        self.setReadOnly(True)

    def append_user(self, text: str):
        self.append(
            f'<p style="color:#7dd3fc;margin:4px 0">'
            f'<span style="color:#0ea5e9;font-weight:bold">YOU &rsaquo;</span> {text}</p>'
        )

    def append_milo(self, text: str):
        self.append(
            f'<p style="color:#a7f3d0;margin:4px 0">'
            f'<span style="color:#00ffe7;font-weight:bold">M.I.L.O &rsaquo;</span> {text}</p>'
        )

    def append_system(self, text: str):
        self.append(
            f'<p style="color:rgba(0,200,180,0.5);font-size:11px;margin:2px 0">'
            f'[SYS] {text}</p>'
        )

    def append_error(self, text: str):
        self.append(
            f'<p style="color:#ff6b6b;margin:4px 0">'
            f'<span style="color:#ff4444;font-weight:bold">ERR &rsaquo;</span> {text}</p>'
        )


# ──────────────────────────────────────────────────────────────────────────────
# Main window
# ──────────────────────────────────────────────────────────────────────────────

class MiloWindow(QMainWindow):
    """
    M.I.L.O main application window.

    Layout:
      [Chat Panel | Visualizer Panel]
      [Status bar]

    Voice commands drive all AI features; no UI buttons trigger them.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("M.I.L.O  —  Machine Intelligence Liaison Operator")
        self.resize(1400, 860)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(MILO_QSS)
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(16, 16, 16, 10)
        main_layout.setSpacing(10)

        # ── Header
        header = self._build_header()
        main_layout.addWidget(header)

        # ── Content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)

        # Left: Chat panel
        chat_panel = self._build_chat_panel()
        splitter.addWidget(chat_panel)

        # Right: Visualizer panel
        viz_panel = self._build_viz_panel()
        splitter.addWidget(viz_panel)

        splitter.setSizes([480, 860])
        main_layout.addWidget(splitter, stretch=1)

        # ── Status bar
        status = self._build_status_bar()
        main_layout.addWidget(status)

    def _build_header(self) -> QWidget:
        frame = make_glass_panel()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 10, 20, 10)

        title = QLabel("M · I · L · O")
        title.setStyleSheet(
            "color: #00ffe7; font-family: 'Orbitron', monospace; "
            "font-size: 20px; letter-spacing: 0.4em; font-weight: 700;"
        )
        subtitle = QLabel("Machine Intelligence Liaison Operator")
        subtitle.setStyleSheet(
            "color: rgba(0,255,231,0.45); font-family: 'Rajdhani', monospace; "
            "font-size: 11px; letter-spacing: 0.2em;"
        )
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        # Pulse indicator (active state visual)
        self._pulse = QLabel("◉  ACTIVE")
        self._pulse.setStyleSheet(
            "color: #00ffe7; font-family: monospace; font-size: 11px; "
            "letter-spacing: 0.15em;"
        )
        layout.addWidget(self._pulse)
        return frame

    def _build_chat_panel(self) -> QFrame:
        panel = make_glass_panel()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        title = QLabel("CHAT INTERFACE")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        self.chat_log = ChatLog()
        layout.addWidget(self.chat_log, stretch=1)

        self.chat_input = QLineEdit()
        self.chat_input.setObjectName("chatInput")
        self.chat_input.setPlaceholderText("Type a command or speak to M.I.L.O…")
        self.chat_input.returnPressed.connect(self._on_text_submit)
        layout.addWidget(self.chat_input)

        return panel

    def _build_viz_panel(self) -> QFrame:
        panel = make_glass_panel()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        title = QLabel("VISUALIZER")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        self.visualizer = VisualizerWidget()
        layout.addWidget(self.visualizer, stretch=1)

        # Load default architecture diagram on startup
        self.visualizer.show_architecture()

        return panel

    def _build_status_bar(self) -> QWidget:
        frame = QWidget()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 2, 8, 2)

        dot = QLabel("●")
        dot.setObjectName("statusDot")
        self._status_label = QLabel("Systems nominal  ·  Voice engine ready  ·  Gemini connected")
        self._status_label.setObjectName("statusText")

        layout.addWidget(dot)
        layout.addWidget(self._status_label)
        layout.addStretch()

        version = QLabel("v0.1.0-alpha")
        version.setStyleSheet("color: rgba(0,255,231,0.25); font-size: 10px; font-family: monospace;")
        layout.addWidget(version)
        return frame

    # ── Slots / public API ────────────────────────────────────────────────────

    def _on_text_submit(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        self.chat_input.clear()
        self.chat_log.append_user(text)
        # Route to your Brain/Dispatcher here:
        # self.brain.process(text)

    def display_milo_response(self, text: str):
        self.chat_log.append_milo(text)

    def display_system_event(self, text: str):
        self.chat_log.append_system(text)

    def display_error(self, text: str):
        self.chat_log.append_error(text)

    def update_status(self, text: str):
        self._status_label.setText(text)

    def show_diagram(self, mermaid_def: str, title: str = ""):
        self.visualizer.show_diagram(mermaid_def, title)

    def show_map(self, center, zoom=10, markers=None, polylines=None, title=""):
        self.visualizer.show_map(center, zoom, markers, polylines, title)


# ──────────────────────────────────────────────────────────────────────────────
# Entry point (dev preview)
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MiloWindow()
    window.show()
    sys.exit(app.exec())
