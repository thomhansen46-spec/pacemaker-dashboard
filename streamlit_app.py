import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(page_title=“FDA MAUDE - Pacemaker Surveillance”, layout=“wide”)
st.title(“🫀 FDA MAUDE · Pacemaker Failure Dashboard”)
st.caption(“Surveillance analytics · Phase-Four Life Sciences”)

# ── DATA ──────────────────────────────────────────────────────────────────────

quarters_36 = [“Q1 2022”,“Q2 2022”,“Q3 2022”,“Q4 2022”,
“Q1 2023”,“Q2 2023”,“Q3 2023”,“Q4 2023”,
“Q1 2024”,“Q2 2024”,“Q3 2024”,“Q4 2024”,“Q1 2025 (F)”]
reports_36 = [820,845,860,890,940,970,1010,1050,1095,1140,1185,1230,1285]

failure_types = [“Battery Depletion”,“Lead Fracture”,“Sensing Failure”,
“Pacing Failure”,“Infection/Erosion”,“Software Anomaly”,
“Connector Issue”,“Other”]
failure_counts_36 = [2840,1920,1450,1230,980,760,640,800]
failure_counts_6 = [512,346,261,221,176,137,115,144]

companies = [“Medtronic”,“Abbott/St. Jude”,“Boston Scientific”,“Biotronik”,“Microport”]
company_totals = [3200,2100,1850,980,490]

medtronic_types = [980,650,520,410,320,240,200,280]
abbott_types = [620,480,340,290,210,180,140,190]
bsc_types = [540,410,290,250,180,160,120,200]

colors = [”#4C8BF5”,”#34A853”,”#F5A623”,”#EA4335”,”#9B59B6”,”#1ABC9C”,”#E67E22”,”#95A5A6”]
dark = dict(plot_bgcolor=”#0e1117”, paper_bgcolor=”#0e1117”, font_color=“white”)

# ── TABS ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
“📊 Overview”,
“📅 Last 36 Months”,
“🔍 Last 6 Months”,
“🏭 Top 5 Companies”,
“📈 Company Breakdown”
])

# ── TAB 1: Overview ── vertical bar + donut pie

with tab1:
col1,col2,col3,col4 = st.columns(4)
col1.metric(“Total 2Y Failures”,“8,620”)
col2.metric(“Avg Quarterly”,“~1,078”)
col3.metric(“Q4 2024”,“1,230”,”+3.8%”)
col4.metric(“Q1 2025 Forecast”,“1,285”,”+4.5%”)

```
st.subheader("Quarterly Trend · Vertical Bar Chart")
fig = go.Figure()
fig.add_trace(go.Bar(x=quarters_36[:12],y=reports_36[:12],name="Historical",marker_color="#4C8BF5"))
fig.add_trace(go.Bar(x=[quarters_36[12]],y=[reports_36[12]],name="Forecast",marker_color="#F5A623"))
fig.update_layout(height=400,**dark)
st.plotly_chart(fig,use_container_width=True)

st.subheader("Failure Type Distribution · Donut Pie Chart")
fig2 = go.Figure(go.Pie(labels=failure_types,values=failure_counts_36,
hole=0.45,marker_colors=colors))
fig2.update_layout(height=420,**dark)
st.plotly_chart(fig2,use_container_width=True)
```

# ── TAB 2: 36 Months ── line chart + horizontal bar

with tab2:
col1,col2,col3 = st.columns(3)
col1.metric(“36M Total”,“~13,100”)
col2.metric(“Annual Growth”,“~6.0%”)
col3.metric(“Peak”,“Q1 2025: 1,285”)

```
st.subheader("36-Month Trend · Line Chart")
fig = go.Figure()
fig.add_trace(go.Scatter(x=quarters_36[:12],y=reports_36[:12],
mode="lines+markers",name="Historical",
line=dict(color="#4C8BF5",width=3),
fill="tozeroy",fillcolor="rgba(76,139,245,0.15)"))
fig.add_trace(go.Scatter(x=[quarters_36[11],quarters_36[12]],
y=[reports_36[11],reports_36[12]],
mode="lines+markers",name="Forecast",
line=dict(color="#F5A623",width=3,dash="dash")))
fig.update_layout(height=420,**dark)
st.plotly_chart(fig,use_container_width=True)

st.subheader("Top 5 Failure Types · Horizontal Bar Chart")
top5 = sorted(zip(failure_types,failure_counts_36),key=lambda x:-x[1])[:5]
fig3 = go.Figure(go.Bar(x=[x[1] for x in top5],y=[x[0] for x in top5],
orientation='h',
marker_color=colors[:5]))
fig3.update_layout(height=380,**dark)
st.plotly_chart(fig3,use_container_width=True)
```

# ── TAB 3: Last 6 Months ── vertical bar + horizontal bar

with tab3:
col1,col2,col3 = st.columns(3)
col1.metric(“Q3 2024”,“1,185”)
col2.metric(“Q4 2024”,“1,230”,”+3.8%”)
col3.metric(“Q1 2025 (F)”,“1,285”,”+4.5%”)

```
st.subheader("Last 3 Quarters · Vertical Bar Chart")
fig = go.Figure()
fig.add_trace(go.Bar(x=["Q3 2024","Q4 2024"],y=[1185,1230],name="Historical",marker_color="#4C8BF5"))
fig.add_trace(go.Bar(x=["Q1 2025 (F)"],y=[1285],name="Forecast",marker_color="#F5A623"))
fig.update_layout(height=380,**dark)
st.plotly_chart(fig,use_container_width=True)

st.subheader("Top 5 Failure Types · Last 6 Months · Horizontal Bar")
top5_6 = sorted(zip(failure_types,failure_counts_6),key=lambda x:-x[1])[:5]
fig4 = go.Figure(go.Bar(x=[x[1] for x in top5_6],y=[x[0] for x in top5_6],
orientation='h',marker_color="#F5A623"))
fig4.update_layout(height=350,**dark)
st.plotly_chart(fig4,use_container_width=True)
```

# ── TAB 4: Top 5 Companies ── horizontal bar + pie

with tab4:
st.subheader(“Market Share by Failures · Pie Chart”)
fig = go.Figure(go.Pie(labels=companies,values=company_totals,marker_colors=colors[:5]))
fig.update_layout(height=400,**dark)
st.plotly_chart(fig,use_container_width=True)

```
st.subheader("Total Failures by Company · Horizontal Bar")
fig2 = go.Figure(go.Bar(x=company_totals,y=companies,orientation='h',
marker_color=colors[:5]))
fig2.update_layout(height=380,**dark)
st.plotly_chart(fig2,use_container_width=True)

df = pd.DataFrame({"Company":companies,"Failures":company_totals,
"Share":[f"{x/sum(company_totals)*100:.1f}%" for x in company_totals]})
st.dataframe(df,hide_index=True,use_container_width=True)
```

# ── TAB 5: Company Breakdown ── histogram + grouped bar

with tab5:
st.subheader(“Failure Type Histogram · Select Company”)
company_sel = st.selectbox(“Company”,[“Medtronic”,“Abbott/St. Jude”,“Boston Scientific”])
data = medtronic_types if company_sel==“Medtronic” else abbott_types if company_sel==“Abbott/St. Jude” else bsc_types
color = “#4C8BF5” if company_sel==“Medtronic” else “#34A853” if company_sel==“Abbott/St. Jude” else “#F5A623”

```
# Histogram — expand data into individual records for true histogram
expanded = []
for ft, cnt in zip(failure_types, data):
expanded.extend([ft]*cnt)
df_hist = pd.DataFrame({"Failure Type": expanded})

fig = px.histogram(df_hist, x="Failure Type", color_discrete_sequence=[color])
fig.update_layout(title=f"{company_sel} · Failure Type Histogram",
height=420,**dark, xaxis_tickangle=-30)
st.plotly_chart(fig,use_container_width=True)

st.subheader("All 3 Companies · Grouped Bar Chart")
fig2 = go.Figure()
fig2.add_trace(go.Bar(name="Medtronic",x=failure_types,y=medtronic_types,marker_color="#4C8BF5"))
fig2.add_trace(go.Bar(name="Abbott/St. Jude",x=failure_types,y=abbott_types,marker_color="#34A853"))
fig2.add_trace(go.Bar(name="Boston Scientific",x=failure_types,y=bsc_types,marker_color="#F5A623"))
fig2.update_layout(barmode='group',height=450,**dark,xaxis_tickangle=-30)
st.plotly_chart(fig2,use_container_width=True)
