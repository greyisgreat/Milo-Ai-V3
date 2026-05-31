"""
M.I.L.O — Machine Intelligence Liaison Operator
src/ui/visualizer.py

Visualization Engine — Diagrams & Interactive Maps
Renders inside a PySide6 glassmorphism panel using QWebEngineView.
All chart/diagram data is served as self-contained HTML (Plotly + Leaflet).
"""

from __future__ import annotations

import json
import textwrap
from typing import Any

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


# ──────────────────────────────────────────────────────────────────────────────
# HTML template helpers
# ──────────────────────────────────────────────────────────────────────────────

_BASE_HTML = textwrap.dedent("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: transparent;
    font-family: 'Rajdhani', 'Orbitron', monospace;
    color: #e0ffff;
    overflow: hidden;
  }}
  {extra_css}
</style>
{head_extras}
</head>
<body>
{body}
<script>
{script}
</script>
</body>
</html>
""")


def _wrap_html(body: str, script: str = "", extra_css: str = "", head_extras: str = "") -> str:
    return _BASE_HTML.format(
        body=body,
        script=script,
        extra_css=extra_css,
        head_extras=head_extras,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Diagram builder — Mermaid.js
# ──────────────────────────────────────────────────────────────────────────────

class DiagramBuilder:
    """
    Generates Mermaid.js diagrams (flowcharts, sequence, ER, Gantt, etc.)
    Returns a self-contained HTML string ready to load in QWebEngineView.
    """

    THEMES = {
        "milo": """
            %%{init: {'theme': 'base', 'themeVariables': {
              'primaryColor': '#0d1b2a',
              'primaryTextColor': '#00ffe7',
              'primaryBorderColor': '#00ffe7',
              'lineColor': '#00ffe7',
              'secondaryColor': '#0a0f1e',
              'tertiaryColor': '#001122',
              'background': '#0d1b2a',
              'mainBkg': '#0d1b2a',
              'nodeBorder': '#00ffe7',
              'clusterBkg': '#0a1628',
              'titleColor': '#00ffe7',
              'edgeLabelBackground': '#0d1b2a'
            }}}%%
        """
    }

    @staticmethod
    def build(mermaid_definition: str, title: str = "") -> str:
        """
        Args:
            mermaid_definition: A valid Mermaid diagram string.
            title: Optional diagram title shown above the visual.

        Returns:
            Self-contained HTML string.
        """
        theme_prefix = DiagramBuilder.THEMES["milo"]
        full_def = theme_prefix + "\n" + mermaid_definition

        title_html = f'<h2 class="diag-title">{title}</h2>' if title else ""

        body = f"""
        {title_html}
        <div class="mermaid-wrap">
          <pre class="mermaid">{full_def}</pre>
        </div>
        """

        head_extras = (
            '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>'
        )

        css = """
        .diag-title {
          text-align: center;
          font-size: 1.1rem;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: #00ffe7;
          padding: 12px 0 8px;
          text-shadow: 0 0 12px #00ffe7aa;
        }
        .mermaid-wrap {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 90vh;
          padding: 16px;
        }
        .mermaid svg { max-width: 100%; }
        """

        script = "mermaid.initialize({ startOnLoad: true, securityLevel: 'loose' });"

        return _wrap_html(body=body, script=script, extra_css=css, head_extras=head_extras)

    # ── Convenience presets ────────────────────────────────────────────────────

    @staticmethod
    def milo_architecture() -> str:
        """Pre-built M.I.L.O system architecture diagram."""
        definition = """
        flowchart TD
            USER([👤 User]):::user
            MIC[🎙️ SpeechRecognition<br/>Ears]:::io
            TTS[🔊 pyttsx3<br/>Voice]:::io
            BRAIN[🧠 Gemini API<br/>Brain]:::brain
            DISPATCH[⚡ Dispatcher<br/>system_ops.py]:::core
            HEALER[🔧 Self-Healer<br/>self_healer.py]:::heal
            VIZ[📊 Visualizer<br/>Diagrams & Maps]:::viz
            SYS[🖥️ System Ops<br/>Apps · Files · Shell]:::sys
            UI[🎨 PySide6 UI<br/>Glassmorphism]:::ui

            USER -->|speaks| MIC
            MIC -->|transcript| BRAIN
            BRAIN -->|intent + args| DISPATCH
            DISPATCH -->|action| SYS
            SYS -->|OperationResult| HEALER
            HEALER -- success --> UI
            HEALER -- failure + traceback --> BRAIN
            BRAIN -->|patch| HEALER
            BRAIN -->|diagram spec| VIZ
            BRAIN -->|speech| TTS
            TTS -->|audio| USER
            VIZ -->|HTML| UI
            UI -->|renders| USER

            classDef user fill:#001a33,stroke:#00ffe7,color:#e0ffff
            classDef io fill:#002244,stroke:#00ccbb,color:#e0ffff
            classDef brain fill:#003355,stroke:#00ffe7,color:#00ffe7,stroke-width:2px
            classDef core fill:#001a2e,stroke:#0088ff,color:#e0ffff
            classDef heal fill:#1a0022,stroke:#ff44ff,color:#ffaaff
            classDef viz fill:#001a0a,stroke:#00ff88,color:#aaffcc
            classDef sys fill:#1a1100,stroke:#ffaa00,color:#ffddaa
            classDef ui fill:#0a001a,stroke:#aa44ff,color:#ddaaff
        """
        return DiagramBuilder.build(definition, title="M.I.L.O System Architecture")

    @staticmethod
    def self_heal_flow() -> str:
        """Diagram of the self-healing loop."""
        definition = """
        sequenceDiagram
            participant U as 👤 User
            participant D as ⚡ Dispatcher
            participant SH as 🔧 Self-Healer
            participant G as 🧠 Gemini Brain

            U->>D: execute(action, **kwargs)
            D->>D: run operation
            alt Success
                D-->>U: OperationResult.ok()
            else Failure
                D->>SH: OperationResult.fail(error, traceback)
                SH->>G: diagnosis prompt + source code
                G-->>SH: {diagnosis, patch, safe_to_apply}
                alt Patch safe & auto_apply=True
                    SH->>SH: exec(patched_code)
                    SH->>D: retry with patched fn
                    D-->>U: OperationResult.ok()
                else Manual review needed
                    SH-->>U: diagnosis + proposed patch
                end
            end
        """
        return DiagramBuilder.build(definition, title="Self-Healing Loop")


# ──────────────────────────────────────────────────────────────────────────────
# Map builder — Leaflet.js
# ──────────────────────────────────────────────────────────────────────────────

class MapBuilder:
    """
    Generates interactive Leaflet.js maps.
    Supports markers, polylines, and heatmaps.
    """

    @staticmethod
    def build(
        center: tuple[float, float] = (20.0, 0.0),
        zoom: int = 2,
        markers: list[dict] | None = None,
        polylines: list[list[tuple[float, float]]] | None = None,
        title: str = "",
    ) -> str:
        """
        Args:
            center: (lat, lon) map centre.
            zoom: Initial zoom level.
            markers: List of {lat, lon, label, color?} dicts.
            polylines: List of coordinate sequences to draw as lines.
            title: Optional overlay title.

        Returns:
            Self-contained HTML string for QWebEngineView.
        """
        markers = markers or []
        polylines = polylines or []

        markers_js = json.dumps(markers)
        polylines_js = json.dumps(polylines)

        title_overlay = (
            f'<div class="map-title">{title}</div>' if title else ""
        )

        body = f"""
        {title_overlay}
        <div id="map"></div>
        """

        head_extras = """
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        """

        css = """
        #map { width: 100vw; height: 100vh; }
        .map-title {
          position: absolute;
          top: 12px; left: 50%;
          transform: translateX(-50%);
          z-index: 1000;
          background: rgba(0,20,40,0.75);
          border: 1px solid #00ffe7;
          padding: 6px 18px;
          border-radius: 20px;
          font-size: 0.9rem;
          letter-spacing: 0.15em;
          color: #00ffe7;
          text-transform: uppercase;
          backdrop-filter: blur(8px);
        }
        .leaflet-container { background: #0d1b2a; }
        """

        script = f"""
        const map = L.map('map', {{
          center: {list(center)},
          zoom: {zoom},
          zoomControl: true
        }});

        // Dark tile layer
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
          attribution: '&copy; OpenStreetMap &copy; CARTO',
          subdomains: 'abcd',
          maxZoom: 19
        }}).addTo(map);

        // Markers
        const markers = {markers_js};
        markers.forEach(m => {{
          const color = m.color || '#00ffe7';
          const icon = L.divIcon({{
            className: '',
            html: `<div style="
              width:14px;height:14px;border-radius:50%;
              background:${{color}};
              box-shadow:0 0 10px ${{color}},0 0 20px ${{color}}55;
              border:2px solid #fff2;
            "></div>`,
            iconSize: [14, 14],
            iconAnchor: [7, 7]
          }});
          L.marker([m.lat, m.lon], {{icon}})
            .bindPopup(`<b style="color:#00ffe7">${{m.label||''}}</b>`)
            .addTo(map);
        }});

        // Polylines
        const lines = {polylines_js};
        lines.forEach(coords => {{
          L.polyline(coords, {{
            color: '#00ffe7',
            weight: 2,
            opacity: 0.8,
            dashArray: '6 4'
          }}).addTo(map);
        }});
        """

        return _wrap_html(body=body, script=script, extra_css=css, head_extras=head_extras)


# ──────────────────────────────────────────────────────────────────────────────
# PySide6 Visualizer Widget
# ──────────────────────────────────────────────────────────────────────────────

class VisualizerWidget(QWidget):
    """
    A PySide6 widget that hosts a QWebEngineView for rendering
    diagrams and maps. Drop this into any glassmorphism panel.

    Usage:
        viz = VisualizerWidget()
        viz.show_diagram(DiagramBuilder.milo_architecture())
        viz.show_map(MapBuilder.build(center=(51.5, -0.1), zoom=10, markers=[...]))
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._view = QWebEngineView()
        self._view.setStyleSheet("background: transparent;")
        # Allow local resource access for embedded JS/CSS
        self._view.page().settings().setAttribute(
            self._view.page().settings().WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        layout.addWidget(self._view)

    def load_html(self, html: str):
        """Load any raw HTML string."""
        self._view.setHtml(html, QUrl("about:blank"))

    def show_diagram(self, mermaid_def: str, title: str = ""):
        """Render a Mermaid diagram."""
        html = DiagramBuilder.build(mermaid_def, title=title)
        self.load_html(html)

    def show_map(
        self,
        center: tuple[float, float] = (20.0, 0.0),
        zoom: int = 2,
        markers: list[dict] | None = None,
        polylines: list[list] | None = None,
        title: str = "",
    ):
        """Render a Leaflet interactive map."""
        html = MapBuilder.build(center=center, zoom=zoom, markers=markers, polylines=polylines, title=title)
        self.load_html(html)

    def show_architecture(self):
        """Shortcut: render the M.I.L.O architecture diagram."""
        self.load_html(DiagramBuilder.milo_architecture())

    def show_self_heal_flow(self):
        """Shortcut: render the self-healing sequence diagram."""
        self.load_html(DiagramBuilder.self_heal_flow())
