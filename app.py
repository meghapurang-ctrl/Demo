from time import sleep

import plotly.express as px
import streamlit as st

from utils.agent import generate_creative
from utils.data import budget_recommendation, find_underperformers, load_campaign_data


st.set_page_config(page_title="Agentic Campaign Engine", page_icon="✦", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ink:#17242a; --muted:#617278; --mint:#c8f5df; --teal:#147d76; --orange:#ff8d5c; --line:#dce8e4; }
html, body, [class*="css"] { font-family:'DM Sans', sans-serif; color:var(--ink); }
h1, h2, h3 { font-family:'Space Grotesk', sans-serif; letter-spacing:0; }
[data-testid="stAppViewContainer"] { background:linear-gradient(135deg,#f7fbf9 0%,#edf7f3 52%,#fff8f1 100%); }
[data-testid="stSidebar"] { background:#17242a; }
[data-testid="stSidebar"] * { color:#eaf5f0; }
[data-testid="stMetric"] { background:#ffffffb8; border:1px solid var(--line); padding:16px; border-radius:8px; }
.block-container { padding-top:2.5rem; max-width:1240px; }
.hero { padding:26px 0 16px; border-bottom:1px solid var(--line); margin-bottom:24px; }
.eyebrow { color:var(--teal); font-size:.78rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
.hero h1 { font-size:clamp(2rem,4vw,3.4rem); margin:.25rem 0 .5rem; }
.hero p { color:var(--muted); max-width:680px; font-size:1.05rem; }
.agent-note { border-left:4px solid var(--orange); background:#fff4ed; padding:14px 18px; margin:14px 0 24px; border-radius:0 8px 8px 0; }
.step { color:var(--teal); font-size:.78rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em; }
.copy-card { background:white; border:1px solid var(--line); border-radius:8px; padding:18px; min-height:170px; }
.copy-card h4 { margin:6px 0; font-family:'Space Grotesk'; }
.small { color:var(--muted); font-size:.88rem; }
</style>
""", unsafe_allow_html=True)


data = load_campaign_data()
underperformers = find_underperformers(data)

with st.sidebar:
    st.markdown("## ✦ Agentic Engine")
    st.caption("Marketing intelligence lab")
    page = st.radio("Explore the workflow", [
        "Campaign Dashboard", "Anomaly Detection", "Creative Optimization", "Budget Reallocation",
    ], label_visibility="collapsed")
    st.divider()
    st.markdown("**Agent status**")
    st.success("Monitoring live dataset")
    st.caption(f"{len(data):,} campaigns indexed")
    st.caption("Thresholds: CPA > $50 · CTR < 0.5%")

st.markdown('<div class="hero"><div class="eyebrow">Agentic campaign optimization engine</div><h1>Make every marketing dollar work harder.</h1><p>A transparent four-step workflow for turning campaign signals into better creative and smarter allocation.</p></div>', unsafe_allow_html=True)

if page == "Campaign Dashboard":
    st.markdown('<div class="step">01 / Observe</div>', unsafe_allow_html=True)
    st.header("Campaign dashboard")
    st.markdown('<div class="agent-note"><b>What the agent sees:</b> A live performance surface across channels, audiences, and objectives. The agent starts here, looking for patterns that deserve attention.</div>', unsafe_allow_html=True)
    total_spend = data["Spend_USD"].sum()
    total_conversions = data["Conversions"].sum()
    cpa = total_spend / total_conversions
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total spend", f"${total_spend:,.0f}")
    m2.metric("Conversions", f"{total_conversions:,.0f}")
    m3.metric("Blended CPA", f"${cpa:,.2f}")
    m4.metric("Underperformers", f"{len(underperformers)}", delta=f"{len(underperformers) / len(data):.1%} of campaigns", delta_color="inverse")
    left, right = st.columns(2)
    with left:
        by_platform = data.groupby("Platform", as_index=False).agg(Spend_USD=("Spend_USD", "sum"), Conversions=("Conversions", "sum"))
        fig = px.scatter(by_platform, x="Spend_USD", y="Conversions", text="Platform", size="Spend_USD", color="Conversions", color_continuous_scale=["#ff8d5c", "#147d76"], template="simple_white", title="Spend vs conversions")
        fig.update_traces(textposition="top center")
        fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=45,b=0), xaxis_title="Spend (USD)", yaxis_title="Conversions")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        platform_cpa = data.groupby("Platform", as_index=False).apply(lambda x: x["Spend_USD"].sum() / x["Conversions"].sum(), include_groups=False).reset_index(name="CPA_USD")
        fig = px.bar(platform_cpa, x="Platform", y="CPA_USD", color="CPA_USD", color_continuous_scale=["#147d76", "#ff8d5c"], template="simple_white", title="CPA by platform")
        fig.update_layout(showlegend=False, coloraxis_showscale=False, margin=dict(l=0,r=0,t=45,b=0), yaxis_title="Blended CPA (USD)")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Anomaly Detection":
    st.markdown('<div class="step">02 / Diagnose</div>', unsafe_allow_html=True)
    st.header("Anomaly detection")
    st.markdown('<div class="agent-note"><b>Agent reasoning:</b> I am applying two plain-language health rules, then ranking the riskiest rows so a human can inspect the evidence before taking action.</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric("Rows flagged", len(underperformers))
    b.metric("Spend at risk", f"${underperformers['Spend_USD'].sum():,.0f}")
    c.metric("Worst CPA", f"${underperformers['CPA_USD'].max():,.2f}")
    table = underperformers[["Campaign_Name", "Platform", "Audience_Segment", "Issue", "Spend_USD", "CTR_Percent", "CPA_USD", "ROAS"]].copy()
    st.dataframe(table.style.format({"Spend_USD":"${:,.0f}", "CTR_Percent":"{:.2f}%", "CPA_USD":"${:,.2f}", "ROAS":"{:.2f}x"}).background_gradient(subset=["CPA_USD"], cmap="Oranges"), use_container_width=True, hide_index=True)

elif page == "Creative Optimization":
    st.markdown('<div class="step">03 / Create</div>', unsafe_allow_html=True)
    st.header("Agentic creative optimization")
    st.markdown('<div class="agent-note"><b>Human in the loop:</b> Choose a flagged segment. The simulated agent will explain the failure signal and draft three audience-specific alternatives for review.</div>', unsafe_allow_html=True)
    if underperformers.empty:
        st.success("No underperformers found. The agent has no creative brief to work on.")
    else:
        labels = underperformers["Campaign_Name"].tolist()
        selected_label = st.selectbox("Select an underperforming segment", labels)
        selected = underperformers[underperformers["Campaign_Name"] == selected_label].iloc[0].to_dict()
        x, y, z = st.columns(3)
        x.metric("Audience", selected["Audience_Segment"])
        y.metric("Current CPA", f"${selected['CPA_USD']:,.2f}")
        z.metric("CTR", f"{selected['CTR_Percent']:.2f}%")
        if st.button("✦ Run AI agent", type="primary", use_container_width=True):
            with st.status("Agent is analyzing the segment...", expanded=True) as status:
                st.write("Reading performance signals")
                sleep(.35)
                st.write("Mapping audience friction")
                sleep(.35)
                st.write("Drafting targeted variants")
                sleep(.35)
                result = generate_creative(selected)
                status.update(label="Agent analysis complete", state="complete")
            st.session_state["creative_result"] = result
        if "creative_result" in st.session_state:
            result = st.session_state["creative_result"]
            st.subheader("Agent readout")
            st.info(result["analysis"])
            st.subheader("Three variants for review")
            cards = st.columns(3)
            for card, variant in zip(cards, result["variants"]):
                with card:
                    st.markdown(f'<div class="copy-card"><div class="eyebrow">Variant {result["variants"].index(variant)+1}</div><h4>{variant["headline"]}</h4><p>{variant["text"]}</p></div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="step">04 / Reallocate</div>', unsafe_allow_html=True)
    st.header("Budget reallocation engine")
    st.markdown('<div class="agent-note"><b>Agent recommendation:</b> Protect the total budget, remove 20% from flagged campaigns, and route that pool toward the three strongest non-flagged campaigns by ROAS.</div>', unsafe_allow_html=True)
    recommendation, current, projected = budget_recommendation(data)
    lift = projected - current
    m1, m2, m3 = st.columns(3)
    m1.metric("Current conversions", f"{current:,.0f}")
    m2.metric("Projected conversions", f"{projected:,.0f}", delta=f"+{lift:,.0f}")
    m3.metric("Projected lift", f"{lift / current:.1%}")
    current_view = recommendation.nlargest(10, "Current_Budget")[["Audience_Segment", "Platform", "Current_Budget"]].rename(columns={"Current_Budget":"Budget"})
    next_view = recommendation.nlargest(10, "Recommended_Budget")[["Audience_Segment", "Platform", "Recommended_Budget"]].rename(columns={"Recommended_Budget":"Budget"})
    left, right = st.columns(2)
    with left:
        st.subheader("Current budget allocation")
        st.dataframe(current_view.style.format({"Budget":"${:,.0f}"}), use_container_width=True, hide_index=True)
    with right:
        st.subheader("Agent recommended allocation")
        st.dataframe(next_view.style.format({"Budget":"${:,.0f}"}), use_container_width=True, hide_index=True)
    st.caption("Recommendation is a simulation for workshop discussion. Validate incrementality and business constraints before activating budget changes.")
