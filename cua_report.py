#!/usr/bin/env python3
"""
CUA Report Generator
=====================
Reads cua_trajectory.json and generates a beautiful HTML report
showing every step the agent took, with screenshots as evidence.

This is exactly what a CUA annotator produces — a structured
record of every action with verification.

Usage:
    python3 cua_report.py
    open cua_report.html
"""

import json
import os
import sys
import base64
from datetime import datetime

TRAJECTORY_FILE = "cua_trajectory.json"
OUTPUT_HTML     = "cua_report.html"


def load_trajectory():
    if not os.path.exists(TRAJECTORY_FILE):
        print(f"Error: {TRAJECTORY_FILE} not found.")
        print("Run python3 cua_agent.py first.")
        sys.exit(1)
    with open(TRAJECTORY_FILE) as f:
        return json.load(f)


def img_to_base64(path):
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def action_color(action_type):
    colors = {
        "LAUNCH":   "#2e86c1",
        "NAVIGATE": "#1e8449",
        "EXTRACT":  "#7d3c98",
        "VALIDATE": "#d35400",
        "CLICK":    "#c0392b",
        "TYPE":     "#117a65",
        "CLOSE":    "#626567",
        "ERROR":    "#e74c3c",
    }
    return colors.get(action_type, "#555")


def generate_html(data):
    steps = data["trajectory"]
    total = data["total_steps"]
    errors = data["total_errors"]
    success = total - errors

    rows = ""
    for step in steps:
        color  = action_color(step["action_type"])
        status = step["status"]
        icon   = "✓" if status == "success" else "✗"
        icon_color = "#27ae60" if status == "success" else "#e74c3c"

        # Screenshot
        img_html = ""
        if step.get("screenshot"):
            b64 = img_to_base64(step["screenshot"])
            if b64:
                img_html = f'''
                <div style="margin-top:10px;">
                  <img src="data:image/png;base64,{b64}"
                       style="max-width:100%;border:1px solid #ddd;border-radius:6px;cursor:pointer;"
                       onclick="this.style.maxWidth=this.style.maxWidth==='100%'?'none':'100%'"
                       title="Click to toggle full size"/>
                  <div style="font-size:10px;color:#888;margin-top:3px;">
                    📸 {step["screenshot"]} — click to expand
                  </div>
                </div>'''

        rows += f"""
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:12px 8px;text-align:center;font-weight:bold;color:#333;vertical-align:top;">
            {step["step"]:02d}
          </td>
          <td style="padding:12px 8px;vertical-align:top;">
            <span style="background:{color};color:white;padding:3px 8px;border-radius:4px;
                         font-size:10px;font-weight:bold;letter-spacing:0.5px;">
              {step["action_type"]}
            </span>
          </td>
          <td style="padding:12px 8px;vertical-align:top;">
            <div style="font-weight:bold;color:#1a1a1a;font-size:12px;">{step["action"]}</div>
            <div style="color:#555;font-size:11px;margin-top:4px;">{step["description"]}</div>
            {img_html}
          </td>
          <td style="padding:12px 8px;vertical-align:top;font-size:11px;color:#2c3e50;">
            {step["verification"]}
          </td>
          <td style="padding:12px 8px;text-align:center;vertical-align:top;">
            <span style="color:{icon_color};font-size:16px;font-weight:bold;">{icon}</span>
          </td>
          <td style="padding:12px 8px;vertical-align:top;font-size:10px;color:#888;">
            {step["timestamp"][11:19]}
          </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CUA Trajectory Report</title>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:Arial,sans-serif; background:#f4f6f9; padding:30px; }}
  .header {{ background:linear-gradient(135deg,#1e3a5f,#2e86c1);
             color:white; padding:28px 32px; border-radius:12px; margin-bottom:24px; }}
  .header h1 {{ font-size:22px; margin-bottom:6px; }}
  .header p {{ font-size:13px; opacity:0.85; }}
  .stats {{ display:flex; gap:16px; margin-bottom:24px; flex-wrap:wrap; }}
  .stat {{ background:white; border-radius:10px; padding:16px 24px; flex:1; min-width:140px;
           box-shadow:0 2px 8px rgba(0,0,0,0.07); text-align:center; }}
  .stat .num {{ font-size:28px; font-weight:bold; }}
  .stat .lbl {{ font-size:11px; color:#888; margin-top:4px; }}
  .card {{ background:white; border-radius:12px; padding:0;
           box-shadow:0 2px 10px rgba(0,0,0,0.07); overflow:hidden; }}
  table {{ width:100%; border-collapse:collapse; }}
  thead tr {{ background:#1e3a5f; color:white; }}
  thead th {{ padding:12px 8px; text-align:left; font-size:11px; font-weight:bold; }}
  tbody tr:hover {{ background:#f8f9ff; }}
  .legend {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:16px; font-size:11px; }}
  .leg {{ display:flex; align-items:center; gap:5px; }}
  .dot {{ width:10px; height:10px; border-radius:2px; }}
  .footer {{ text-align:center; color:#aaa; font-size:11px; margin-top:20px; }}
</style>
</head>
<body>

<div class="header">
  <h1>CUA Trajectory Report</h1>
  <p>Agent: {data["agent"]} &nbsp;|&nbsp;
     Task: {data["task"]} &nbsp;|&nbsp;
     Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
</div>

<div class="stats">
  <div class="stat">
    <div class="num" style="color:#2e86c1">{total}</div>
    <div class="lbl">Total Steps</div>
  </div>
  <div class="stat">
    <div class="num" style="color:#27ae60">{success}</div>
    <div class="lbl">Successful</div>
  </div>
  <div class="stat">
    <div class="num" style="color:#e74c3c">{errors}</div>
    <div class="lbl">Errors</div>
  </div>
  <div class="stat">
    <div class="num" style="color:#7d3c98">
      {round((success/total)*100) if total else 0}%
    </div>
    <div class="lbl">Success Rate</div>
  </div>
  <div class="stat">
    <div class="num" style="color:#d35400" style="font-size:18px;">
      {data["started_at"][11:19]}
    </div>
    <div class="lbl">Start Time</div>
  </div>
</div>

<div class="card">
  <table>
    <thead>
      <tr>
        <th style="width:40px">#</th>
        <th style="width:100px">Action Type</th>
        <th>Action & Description</th>
        <th style="width:260px">Verification</th>
        <th style="width:50px">Status</th>
        <th style="width:70px">Time</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</div>

<div class="legend">
  <strong>Action Types:</strong>
  <div class="leg"><div class="dot" style="background:#2e86c1"></div> LAUNCH</div>
  <div class="leg"><div class="dot" style="background:#1e8449"></div> NAVIGATE</div>
  <div class="leg"><div class="dot" style="background:#7d3c98"></div> EXTRACT</div>
  <div class="leg"><div class="dot" style="background:#d35400"></div> VALIDATE</div>
  <div class="leg"><div class="dot" style="background:#c0392b"></div> CLICK</div>
  <div class="leg"><div class="dot" style="background:#117a65"></div> TYPE</div>
  <div class="leg"><div class="dot" style="background:#626567"></div> CLOSE</div>
  <div class="leg"><div class="dot" style="background:#e74c3c"></div> ERROR</div>
</div>

<div class="footer">
  CUA Trajectory Report &nbsp;|&nbsp; Vijayendra Singh &nbsp;|&nbsp;
  {datetime.now().strftime("%Y-%m-%d")}
</div>

</body>
</html>"""
    return html


def main():
    data = load_trajectory()
    html = generate_html(data)
    with open(OUTPUT_HTML, "w") as f:
        f.write(html)

    steps = data["total_steps"]
    errors = data["total_errors"]
    print(f"\n  CUA Report generated!")
    print(f"  Steps    : {steps}")
    print(f"  Errors   : {errors}")
    print(f"  Report   : {OUTPUT_HTML}")
    print(f"\n  Open it: open {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
