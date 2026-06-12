import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from db import load_df
from utils.analysis import filter_period, limit_top_n, render_sidebar_filters


def render() -> None:
    st.header("📈 시장 기술 트렌드")
    category, period, top_n = render_sidebar_filters(default_top_n=5)

    query = """
    SELECT
        DATE_TRUNC('month', jo.created_at) AS month,
        s.name AS skill,
        COUNT(*) AS demand_count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY 1, 2
    ORDER BY 1, 2
    """

    trend_df = load_df(query)
    if trend_df.empty:
        st.info("기술 트렌드 데이터를 불러올 수 없습니다.")
        return

    trend_df = filter_period(trend_df, "month", period)
    if trend_df.empty:
        st.info("선택한 기간에 해당하는 데이터가 없습니다.")
        return

    top_skills = (
        trend_df.groupby("skill", as_index=False)["demand_count"]
        .sum()
        .sort_values("demand_count", ascending=False)
        .head(top_n)["skill"]
        .tolist()
    )
    if not top_skills:
        st.info("표시할 기술이 없습니다.")
        return

    trend_df = trend_df[trend_df["skill"].isin(top_skills)].copy()
    other_df = (
        trend_df.groupby("month", as_index=False)["demand_count"]
        .sum()
        .rename(columns={"demand_count": "기타"})
    )
    other_df["기타"] = 0

    fig = go.Figure()
    for skill in top_skills:
        skill_df = trend_df[trend_df["skill"] == skill].groupby("month", as_index=False)["demand_count"].sum()
        fig.add_trace(go.Scatter(x=skill_df["month"], y=skill_df["demand_count"], mode="lines", stackgroup="one", name=skill, hovertemplate="%{x}<br>%{fullData.name}: %{y}<extra></extra>"))

    fig.add_trace(go.Scatter(x=other_df["month"], y=other_df["기타"], mode="lines", stackgroup="one", name="기타", line=dict(dash="dot"), hovertemplate="%{x}<br>기타: %{y}<extra></extra>"))

    fig.update_layout(title="월별 기술 점유율 변화", xaxis_title="월", yaxis_title="누적 공고 수", hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.caption("※ 상위 N개 기술만 누적하여 표시하고, 나머지는 '기타'로 묶어 데이터 과부하를 줄였습니다.")
