"""Create a second interactive dashboard with readable variable names.

Output:
- results/reports/M2_interactive_dashboard_v2.html
"""

from __future__ import annotations

import importlib
from pathlib import Path
import re

import numpy as np
import pandas as pd

from config_paths import FINAL_DATA_DIR, PROJECT_ROOT, REPORTS_DIR
from panel_format_utils import load_panel_as_wide


go = importlib.import_module("plotly.graph_objects")
sample_colorscale = importlib.import_module("plotly.colors").sample_colorscale


def parse_variable_dictionary(dict_path: Path) -> dict[str, dict[str, str]]:
    """Parse variable metadata from the markdown data dictionary table."""
    metadata: dict[str, dict[str, str]] = {}
    if not dict_path.exists():
        return metadata

    lines = dict_path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        if "Variable Name" in line or "---" in line:
            continue

        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 5:
            continue

        # Only parse rows from the variable-definition table where variable names are bolded.
        if "**" not in parts[0]:
            continue

        raw_var = re.sub(r"\*", "", parts[0]).strip()
        if not raw_var or raw_var == "Variable Name":
            continue

        metadata[raw_var] = {
            "description": parts[1],
            "type": parts[2],
            "source": parts[3],
            "units": parts[4],
            "notes": parts[5] if len(parts) > 5 else "",
        }

    return metadata


def friendly_label(var: str, meta: dict[str, dict[str, str]]) -> str:
    details = meta.get(var)
    if not details:
        return f"{var.replace('_', ' ').title()} ({var})"

    description = details.get("description", "").strip()
    units = details.get("units", "").strip()
    if units:
        return f"{description} ({var}) [{units}]"
    return f"{description} ({var})"


def create_time_series_figure(df: pd.DataFrame, numeric_cols: list[str], meta: dict[str, dict[str, str]]) -> go.Figure:
    fig = go.Figure()
    default_var = "mkt_ret" if "mkt_ret" in numeric_cols else numeric_cols[0]

    for col in numeric_cols:
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df[col],
                mode="lines",
                name=friendly_label(col, meta),
                visible=(col == default_var),
                hovertemplate="%{x|%Y-%m-%d}<br>%{y:.3f}<extra></extra>",
            )
        )

    buttons = []
    for i, col in enumerate(numeric_cols):
        visible = [False] * len(numeric_cols)
        visible[i] = True
        buttons.append(
            {
                "label": friendly_label(col, meta),
                "method": "update",
                "args": [
                    {"visible": visible},
                    {
                        "title": f"Time Series: {friendly_label(col, meta)}",
                        "yaxis": {"title": friendly_label(col, meta)},
                    },
                ],
            }
        )

    fig.update_layout(
        title=f"Time Series: {friendly_label(default_var, meta)}",
        xaxis_title="Date",
        yaxis_title=friendly_label(default_var, meta),
        updatemenus=[
            {
                "buttons": buttons,
                "x": 0.01,
                "y": 1.18,
                "xanchor": "left",
                "yanchor": "top",
                "direction": "down",
                "showactive": True,
            }
        ],
        height=500,
        margin={"l": 70, "r": 20, "t": 100, "b": 60},
        template="plotly_white",
    )
    return fig


def create_correlation_figure(df: pd.DataFrame, numeric_cols: list[str], meta: dict[str, dict[str, str]]) -> go.Figure:
    corr = df[numeric_cols].corr()
    labels = [friendly_label(c, meta) for c in numeric_cols]

    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=labels,
            y=labels,
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
            colorbar={"title": "Correlation"},
            hovertemplate="%{x}<br>%{y}<br>r = %{z:.3f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Correlation Heatmap with Human-Readable Variable Names",
        height=700,
        margin={"l": 180, "r": 30, "t": 80, "b": 180},
        template="plotly_white",
    )
    return fig


def create_scatter_figure(df: pd.DataFrame, numeric_cols: list[str], meta: dict[str, dict[str, str]]) -> go.Figure:
    target = "mkt_ret" if "mkt_ret" in numeric_cols else numeric_cols[0]
    candidates = [c for c in numeric_cols if c != target]

    fig = go.Figure()

    for i, col in enumerate(candidates):
        x = df[col]
        y = df[target]
        slope, intercept = np.polyfit(x, y, 1)
        y_fit = slope * x + intercept
        corr = x.corr(y)

        color = sample_colorscale("Viridis", [i / max(1, len(candidates) - 1)])[0]
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                marker={"color": color, "size": 7, "opacity": 0.72},
                name=friendly_label(col, meta),
                visible=(i == 0),
                hovertemplate=(
                    f"{friendly_label(col, meta)}: "
                    + "%{x:.3f}<br>"
                    + f"{friendly_label(target, meta)}: "
                    + "%{y:.3f}<extra></extra>"
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y_fit,
                mode="lines",
                line={"color": color, "width": 2},
                name=f"Trend: {friendly_label(col, meta)}",
                visible=(i == 0),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    buttons = []
    for i, col in enumerate(candidates):
        visible = [False] * (2 * len(candidates))
        visible[2 * i] = True
        visible[2 * i + 1] = True
        corr = df[col].corr(df[target])

        buttons.append(
            {
                "label": friendly_label(col, meta),
                "method": "update",
                "args": [
                    {"visible": visible},
                    {
                        "title": (
                            "Outcome vs Selected Variable "
                            f"(corr = {corr:.3f})"
                        ),
                        "xaxis": {"title": friendly_label(col, meta)},
                        "yaxis": {"title": friendly_label(target, meta)},
                    },
                ],
            }
        )

    fig.update_layout(
        title=f"Outcome vs Selected Variable (corr = {df[candidates[0]].corr(df[target]):.3f})",
        xaxis_title=friendly_label(candidates[0], meta),
        yaxis_title=friendly_label(target, meta),
        updatemenus=[
            {
                "buttons": buttons,
                "x": 0.01,
                "y": 1.18,
                "xanchor": "left",
                "yanchor": "top",
                "direction": "down",
                "showactive": True,
            }
        ],
        height=520,
        margin={"l": 70, "r": 20, "t": 100, "b": 60},
        template="plotly_white",
    )

    return fig


def build_glossary_table(numeric_cols: list[str], meta: dict[str, dict[str, str]]) -> str:
    rows = []
    for col in numeric_cols:
        details = meta.get(col, {})
        rows.append(
            "<tr>"
            f"<td><code>{col}</code></td>"
            f"<td>{details.get('description', 'N/A')}</td>"
            f"<td>{details.get('units', 'N/A')}</td>"
            f"<td>{details.get('source', 'N/A')}</td>"
            "</tr>"
        )

    return (
        "<table class='glossary'><thead><tr>"
        "<th>Variable Code</th><th>Readable Name</th><th>Units</th><th>Source</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def write_dashboard_html(time_fig: go.Figure, corr_fig: go.Figure, scatter_fig: go.Figure, glossary_html: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "M2_interactive_dashboard_v2.html"

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>M2 Interactive Dashboard v2</title>
  <style>
    body {{
      font-family: "Segoe UI", Tahoma, sans-serif;
      background: linear-gradient(180deg, #f7fafc 0%, #eef2f7 100%);
      color: #172033;
      margin: 0;
      padding: 24px;
    }}
    .wrap {{ max-width: 1280px; margin: 0 auto; }}
    h1 {{ margin-bottom: 8px; }}
    .sub {{ color: #3f4f6b; margin-top: 0; }}
    .card {{
      background: #ffffff;
      border-radius: 14px;
      padding: 16px;
      margin: 18px 0;
      box-shadow: 0 8px 24px rgba(21, 31, 56, 0.08);
    }}
    .hint {{ font-size: 0.95rem; color: #4d607f; }}
    .glossary {{ width: 100%; border-collapse: collapse; font-size: 0.95rem; }}
    .glossary th, .glossary td {{ border: 1px solid #d9e1ed; padding: 8px; text-align: left; }}
    .glossary th {{ background: #f2f6fc; }}
    code {{ background: #f4f7fc; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>M2 Interactive Dashboard v2</h1>
    <p class="sub">This dashboard uses readable variable names from your data dictionary so each graph is easier to interpret.</p>

    <div class="card">
      <h2>1) Variable Explorer (Time Series)</h2>
      <p class="hint">Use the dropdown to switch variables. Axis titles and legend labels update with readable names and units.</p>
      {time_fig.to_html(full_html=False, include_plotlyjs='cdn')}
    </div>

    <div class="card">
      <h2>2) Correlation Map</h2>
      <p class="hint">Hover over cells to see pairwise correlations with full variable descriptions.</p>
      {corr_fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>

    <div class="card">
      <h2>3) Outcome Relationship Explorer</h2>
      <p class="hint">Select a variable and view how it relates to market return with a fitted trend line.</p>
      {scatter_fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>

    <div class="card">
      <h2>4) Variable Glossary</h2>
      <p class="hint">Dictionary pulled from <code>data/final/data_dictionary.md</code>.</p>
      {glossary_html}
    </div>
  </div>
</body>
</html>
"""

    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    data_path = FINAL_DATA_DIR / "analysis_panel.csv"
    dict_path = PROJECT_ROOT / "data" / "final" / "data_dictionary.md"

    df = load_panel_as_wide(data_path)

    metadata = parse_variable_dictionary(dict_path)

    numeric_cols = [c for c in df.columns if c != "date" and pd.api.types.is_numeric_dtype(df[c])]

    time_fig = create_time_series_figure(df, numeric_cols, metadata)
    corr_fig = create_correlation_figure(df, numeric_cols, metadata)
    scatter_fig = create_scatter_figure(df, numeric_cols, metadata)
    glossary_html = build_glossary_table(numeric_cols, metadata)

    out_path = write_dashboard_html(time_fig, corr_fig, scatter_fig, glossary_html)
    print(f"Saved interactive dashboard: {out_path}")


if __name__ == "__main__":
    main()
