import streamlit as st
import plotly.graph_objects as go
import pandas as pd
st.set_page_config(page_title="FDA MAUDE Dashboard", layout="wide")
st.title("FDA MAUDE - Pacemaker Failure Dashboard")
quarters = ["Q1 2023","Q2 2023","Q3 2023","Q4 2023","Q1 2024","Q2 2024","Q3 2024","Q4 2024","Q1 2025 (F)"]
reports = [940,970,1010,1050,1095,1140,1185,1230,1285]
col1,col2,col3,col4 = st.columns(4)
col1.metric("Total 2Y","8,620")
col2.metric("Avg Quarterly","1,078")
col3.metric("Q4 2024","1,230","+3.8%")
col4.metric("Q1 2025 Forecast","1,285","+4.5%")
fig = go.Figure()
fig.add_trace(go.Bar(x=quarters[:8],y=reports[:8],name="Historical",marker_color="steelblue"))
fig.add_trace(go.Bar(x=[quarters[8]],y=[reports[8]],name="Forecast",marker_color="orange"))
st.plotly_chart(fig,use_container_width=True)
st.dataframe(pd.DataFrame({"Quarter":quarters,"Reports":reports}),hide_index=True)
