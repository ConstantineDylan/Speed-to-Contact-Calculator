import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import os
import base64
import mimetypes

# ---------------------------
#  CONFIG
# ---------------------------
st.set_page_config(page_title="Lead Decay Calculator", layout="wide", page_icon="⚡")

# Decay constant
DECAY_CONSTANT = 0.045
AI_RESPONSE_TIME_MIN = 0.5  # 30 seconds

# Colors
BG = "#0E1117"
CARD = "#121318"
TEXT = "#FFFFFF"
ACCENT = "#2EE6A6"
RED = "#B01212"
# RED = "#FF4B4B"
WHITE = "#F0F0F0"

# CTAs
form_link = "https://ldssxyfkwd9.typeform.com/to/x1P4Bgls"

# ---------------------------
#  STYLE
# ---------------------------
st.markdown(
    f"""
<style>
    .reportview-container .main {{
        background: {BG};
        color: {TEXT};
    }}
    .stApp {{
        background: {BG};
    }}
    .card {{
        background: {CARD};
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.6);
    }}

    .impact-row {{ display:flex; gap:12px; }}
    .impact-item {{ flex:1; background:#15181b; border-radius:8px; padding:10px; text-align:center; }}
    .card h2 {{ margin: 0 0 8px 0; }}
    .card hr {{ margin: 8px 0; opacity: 0.3; }}
    .card p {{ margin: 4px 0; }}
    h2 {{ margin: 0 0 6px 0; }}
    p {{ margin: 4px 0; }}
    
    /* New compact styles for funnel boxes and impact card */
    .funnel-box {{ padding: 12px 8px; background:#15181b; border-radius:8px; text-align:center; margin-bottom: 6px; }}
    .funnel-box-ai {{ padding: 12px 8px; background:#052914; border-radius:8px; text-align:center; color:{ACCENT}; margin-bottom: 6px; }}
    .impact-card {{ padding: 10px; margin-top: 6px; }}

    /* Keep metric pairs side-by-side even on phones */
    .funnel-row {{ display:flex; gap:12px; align-items:stretch; flex-wrap:nowrap; }}
    .funnel-col {{ flex:1 1 0; min-width:0; }}
    .muted {{ color: #9aa0a6; font-size:12px; }}
    .big-num {{ font-size:28px; font-weight:800; color:{ACCENT}; }}

    /* Quote cards above funnel */
    .quote-grid {{ display:flex; flex-wrap:wrap; gap:12px; margin: 8px 0 14px; }}
    .quote-card {{ display:flex; align-items:center; gap:12px; background:{CARD}; border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:12px; flex: 1 1 calc(50% - 12px); }}
    .quote-card.center {{ margin-left:auto; margin-right:auto; }}
    .quote-img {{ width:56px; height:56px; border-radius:8px; object-fit:contain; background:{BG}; }}
    .quote-body {{ flex:1; }}
    .quote-text {{ color:#d1d5db; font-size:14px; line-height:1.45; }}
    .quote-name {{ margin-top:6px; font-weight:700; }}

    .center-colored-subheader {{text-align: left; color: {RED}!important;}}

    /* Bottom CTA card */
    .cta-card {{
        background:#15181b;
        border-radius:12px;
        padding:24px;
        text-align:center;
        border:1px solid rgba(255,255,255,0.08);
        margin-top: 18px;
    }}
    .cta-title {{ font-size:35px; font-weight:800; margin-bottom:8px; }}
    .cta-sub {{ color:#9aa0a6; margin-bottom:10px; }}
    .cta-row {{
        display:flex;
        align-items:center;
        justify-content:center;
        gap:58px;
        flex-wrap:wrap;
        margin: 6px 0 10px;
    }}
    /* Tighter spacing on small screens */
    @media (max-width: 640px) {{
        .cta-row {{
            gap:12px;
        }}
    }}
    /* Bullet list with customizable left padding via --cta-pad */
    .cta-list {{
        list-style: none;
        padding-left: var(--cta-pad, 8px);
        margin: 0;
        display: inline-block;
        text-align: left;
    }}
    .cta-list li {{
        color:#9aa0a6;
        margin:4px 0;
        position: relative;
        padding-left: 16px;
    }}
    .cta-list li::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 9px;
        width: 6px;
        height: 6px;
        background: {ACCENT};
        border-radius: 50%;
    }}
    .cta-btn {{
        display:inline-block;
        background: {ACCENT};
        color:#0E1117;
        font-weight:700;
        # top-padding: 16px;
        padding:10px 16px;
        border-radius:8px;
        text-decoration:none;
        transition: background 0.2s ease-in-out;
    }}
    .cta-btn:hover {{
        background: #55F0BD;
    }}

    /* Chart legend styles */
    .chart-legend {{
        display:flex;
        justify-content:center;
        gap:14px;
        flex-wrap:wrap;
        margin-top:-20px;
    }}
    .legend-item {{
        display:flex;
        align-items:center;
        gap:6px;
        color:#9aa0a6;
        font-size:13px;
    }}
    .legend-swatch {{
        width:12px;
        height:12px;
        border-radius:2px;
        display:inline-block;
    }}
    .swatch-red {{ background: {RED}; }}
    .swatch-accent {{ background: {ACCENT}; }}
    .swatch-pink {{ background: {WHITE}; }}

    .paragraph {{
        # font-family: \'Times New Roman\';
        font-size: 15px;
        margin-bottom: 12px;
        text-align: justify;
    }}

</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------
#  HELPER FUNCTIONS
# ---------------------------
def effective_set_rate_fraction(base_frac, response_time):
    return base_frac * (1.0 / (1.0 + (np.array(response_time, dtype=float) / 5.0) ** 2))

def decay_factor_from_time(response_time):
    rt = np.array(response_time, dtype=float)
    return 1.0 / (1.0 + (rt / 5.0) ** 2)

def clamp01(x):
    return max(0.0, min(1.0, x))

# ---------------------------
#  HEADER
# ---------------------------
st.markdown("# ⚡ Lead Decay Calculator")
st.markdown("See how much revenue you're losing every minute your leads wait.")


st.markdown("---")


# Lead decay paragraph above the 3 quote cards
st.markdown("#### Lead Decay")

st.markdown("""
    <p class="paragraph">
        The biggest profit leak in your business, and most people don’t even know it’s happening. After five minutes, your chance of contacting a lead tanks, and by fifteen minutes, more than 80% of the money you could have made is already gone. You didn’t lose them because your offer sucks—you lost them because you were slow.\n
    </p>""", unsafe_allow_html=True)

st.markdown("""
    <p class="paragraph">
        Leads don’t “think about it”; they forget you exist while your team is still warming up the dialer. It doesn’t matter how good your ads, funnel, or closers are if your response speed is garbage. If you’re not responding instantly, you’re basically paying competitors to take your deals from you.
    </p>""", unsafe_allow_html=True)

# Resolve local Assets images to data URIs so HTML can render them
assets_dir = os.path.join(os.path.dirname(__file__), "Assets")

def image_data_uri(filename):
    path = os.path.join(assets_dir, filename)
    if not os.path.exists(path):
        # Fallback placeholder if file is missing
        return "https://placehold.co/56x56/png"
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"

# Quote cards section (two on top row, one centered below)
quote_cards = [
    {
        "img": image_data_uri("MIT_logo.png"),
        "text": "78% of deals go to the fastest first responder",
        "name": "Massachusetts Institute of Technology"
    },
    {
        "img": image_data_uri("Forbes_logo.png"),
        "text": "Lead value decays 80% in 15 minutes.",
        "name": "Forbes"
    },
    {
        "img": image_data_uri("AlexHormozi.jpg"),
        "text": "Their sales increased by 391% after they contact all their leads in under 1 minute, they close 55% of their leads.",
        "name": "Alex Hormozi - Acquisition.com",
        "center": True
    }
]

quotes_html = "<div class=\"quote-grid\">"
for qc in quote_cards:
    center_cls = " center" if qc.get("center") else ""
    quotes_html += f"""
        <div class='quote-card{center_cls}'>
        <img class='quote-img' src='{qc["img"]}' alt='{qc["name"]} logo'/>
        <div class='quote-body'>
            <div class='quote-text'>\"{qc["text"]}\"</div>
            <div class='quote-name'><strong>{qc["name"]}</strong></div>
        </div>
        </div>
        """
quotes_html += "</div>"

# Prefer Streamlit HTML renderer to avoid Markdown turning leading spaces into code blocks
try:
    st.html(quotes_html)
except Exception:
    st.markdown(quotes_html, unsafe_allow_html=True)

st.markdown("""
    <h3 class='center-colored-subheader' style='text-align:center; margin:6px 0; padding:0;'>
    \"The More You Wait, The More $$$ You'll Lose.\"
    </h3>
    """, unsafe_allow_html=True)

st.markdown("---")


# ---------------------------
#  INPUTS (LEFT COLUMN)
# ---------------------------
left_col, right_col = st.columns((1, 1.2))

with left_col:
    st.markdown("## Your Business Metrics")

    monthly_leads = int(st.number_input("Monthly Leads", 0, value=1000))
    avg_response_time = int(st.number_input("Current Average Response Time (minutes)", 0, value=30))
    current_set_rate_pct = int(st.number_input("Current Book Rate (%)", 0, 100, 25))
    show_rate_pct = int(st.number_input("Show Rate (%)", 0, 100, 60))
    close_rate_pct = int(st.number_input("Close Rate (%)", 0, 100, 20))
    deal_value = int(st.number_input("Average Deal Value ($)", 0, value=12500))
    max_potential_book_rate = int(st.number_input("Maxium Potential Book Rate (%)", 0, 100, 40)) / 100

# ---------------------------
#  CALCULATIONS
# ---------------------------
current_set_frac = current_set_rate_pct / 100
show_frac = show_rate_pct / 100
close_frac = close_rate_pct / 100

current_eff_set = effective_set_rate_fraction(current_set_frac, avg_response_time)
current_decay = decay_factor_from_time(avg_response_time)

baseline_potential_frac = clamp01(
    current_eff_set / current_decay if current_decay > 0 else current_eff_set
)

ai_eff_set = clamp01(
    baseline_potential_frac * np.exp(-DECAY_CONSTANT * AI_RESPONSE_TIME_MIN)
)

current_booked = int(monthly_leads * current_set_frac)
ai_booked = int(monthly_leads * max_potential_book_rate)

current_shows = int(current_booked * show_frac)
ai_shows = int(ai_booked * show_frac)

current_closed = int(current_shows * close_frac)
ai_closed = int(ai_shows * close_frac)

current_monthly_revenue = current_closed * deal_value
ai_monthly_revenue = ai_closed * deal_value

additional_appointments = ai_booked - current_booked
additional_closed = ai_closed - current_closed
additional_revenue_month = ai_monthly_revenue - current_monthly_revenue
annual_additional_revenue = additional_revenue_month * 12

# annual_savings = (setter_monthly_cost - ai_monthly_cost) * 12
# total_annual_impact = annual_additional_revenue + annual_savings

if current_monthly_revenue > 0:
    revenue_increase_pct = int((additional_revenue_month / current_monthly_revenue) * 100)
else:
    revenue_increase_pct = 0

# ---------------------------
#  RIGHT COLUMN — FUNNEL + IMPACT
# ---------------------------
with right_col:
    st.markdown("## Conversion Funnel")

    rows = {
        "Monthly Leads": (monthly_leads, None),
        "Booked Appointments": (current_booked, ai_booked),
        "Shows": (current_shows, ai_shows),
        "Closed Deals": (current_closed, ai_closed),
        "Monthly Revenue": (f"${current_monthly_revenue:,}", f"${ai_monthly_revenue:,}")
    }

    for label, (cur, ai) in rows.items():
        if label == "Monthly Leads":
            st.markdown(f"**{label}**")
            st.markdown(
                f"<div class='funnel-box' style='width:100%'>" + str(cur) + "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"**{label}**")
            row_html = f"""
<div class='funnel-row'>
  <div class='funnel-col'><div class='funnel-box'>{cur}</div></div>
  <div class='funnel-col'><div class='funnel-box-ai'>{ai}</div></div>
</div>
"""
            st.markdown(row_html, unsafe_allow_html=True)


    # IMPACT SUMMARY
    impact_html = f"""<div class="card impact-card">
<h2>Impact Summary</h2>

<div class="impact-row">
  <div class="impact-item">
    <div class="big-num">+{additional_appointments}</div>
    <div class="muted">calls/month</div>
  </div>

  <div class="impact-item">
    <div class="big-num">+${additional_revenue_month:,}</div>
    <div class="muted">/month</div>
  </div>

  <div class="impact-item">
    <div class="big-num">{revenue_increase_pct}%</div>
    <div class="muted">increase</div>
  </div>
</div>

<hr>

<p><strong>Annual Additional Revenue:</strong> ${annual_additional_revenue:,}</p>
<p><strong>Additional Closed Deals:</strong> +{additional_closed}/month</p>
</div>"""
    # Prefer Streamlit's HTML renderer to avoid Markdown interpreting leading spaces as code blocks
    try:
        st.html(impact_html)
    except Exception:
        # Fallback for older Streamlit versions
        st.markdown(impact_html, unsafe_allow_html=True)



# ---------------------------
#  DECAY CURVE — BOTTOM
# ---------------------------
st.markdown("### Number of Leads You'll Lose the More You Wait")

minutes = np.arange(0, 61)
# Compute expected leads captured as a function of response time
leads_captured = monthly_leads * decay_factor_from_time(minutes)

df = pd.DataFrame({"minutes": minutes, "leads_captured": leads_captured})

base = (
    alt.Chart(df)
    .mark_area(opacity=0.15, color=RED)
    .encode(
        x=alt.X("minutes:Q", title="Response Time (minutes)"),
        y=alt.Y("leads_captured:Q", title="Leads Captured")
    )
)

line = (
    alt.Chart(df)
    .mark_line(color=RED, strokeWidth=3)
    .encode(x="minutes:Q", y="leads_captured:Q")
)

current_marker = alt.Chart(pd.DataFrame({"t": [avg_response_time]})).mark_rule(
    color=WHITE, strokeWidth=2
).encode(x="t:Q")

ai_marker = alt.Chart(pd.DataFrame({"t": [AI_RESPONSE_TIME_MIN]})).mark_rule(
    color=ACCENT, strokeWidth=2
).encode(x="t:Q")

chart = (base + line + current_marker + ai_marker).properties(height=380)

st.altair_chart(chart, use_container_width=True)

# Bottom legend for chart lines
legend_html = f"""
<div class='chart-legend'>
  <div class='legend-item'><span class='legend-swatch swatch-red'></span><span>Leads captured curve</span></div>
  <div class='legend-item'><span class='legend-swatch swatch-pink'></span><span>Your avg response</span></div>
  <div class='legend-item'><span class='legend-swatch swatch-accent'></span><span>AI response (~30s)</span></div>
</div>
"""
try:
    st.html(legend_html)
except Exception:
    st.markdown(legend_html, unsafe_allow_html=True)

st.markdown("---")

# Subheader summarizing capture at current average response time
captured_at_avg = int(monthly_leads * decay_factor_from_time(avg_response_time))
st.markdown(
    f"""
    <h4 style='text-align: center;'>
    Out of {monthly_leads} leads, you only capture {captured_at_avg} high intent leads when responding in {avg_response_time} minutes.
    </h4>
    """,
    unsafe_allow_html=True,
)

# st.markdown(f"<div class='muted'>Your System ({avg_response_time}m): {current_eff_set*100:.2f}% effective set</div>", unsafe_allow_html=True)
# st.markdown(f"<div class='muted'>AI System ({AI_RESPONSE_TIME_MIN}m): {ai_eff_set*100:.2f}% effective set</div>", unsafe_allow_html=True)

# Bottom Call-To-Action card
cta_html = f"""
    <div class=\"card cta-card\">\n  
        <div class=\"cta-title\">Ready to Capture ALL of Your Leads?</div>\n  
        <div class=\"cta-sub\">If you're a Consulting / Coaching Business that is making between 100k-1M/month, get your schedule for our Free 30-Second Response Plan!</div>\n  
        <div class=\"cta-row\">\n
            <ul class=\"cta-list\" style=\"--cta-pad: 10px;\">\n
                <li>No obligation</li>\n
                <li>We plug your numbers in</li>\n
                <li>We show you ROI live</li>\n
                <li>Completely Free</li>\n
            </ul>\n
        <a class=\"cta-btn\" href=\"{form_link}\">Get My 30-Second Response Plan</a>\n        </div>\n
        <div style='text-align: center; font-style:italic; font-size: 15px;padding-top: 6px;'>*Only taking 2 new accounts this month so response quality stays high.*</div>\n  
    </div>
"""
try:
    st.html(cta_html)
except Exception:
    st.markdown(cta_html, unsafe_allow_html=True)

st.markdown(
    f"""
    <h5 style='text-align: center; font-weight:300; font-style:italic; margin-top: 20px;'>
    “If you could eliminate the delay and contact every lead within 60 seconds, your conversion rate would return to full potential instantly.”
    </h5>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

st.markdown("Built by SonicCRO")
