import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.analysis import render_sidebar_filters, safe_load_df


def render() -> None:
    st.header("📈 시장 기술 트렌드")
    _, _, top_n = render_sidebar_filters(default_top_n=5)

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

    trend_df = safe_load_df(query)
    if trend_df.empty:
        st.info("기술 트렌드 데이터를 불러올 수 없습니다.")
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
    month_df = trend_df.groupby(["month", "skill"], as_index=False)["demand_count"].sum()

    fig = go.Figure()
    for skill in top_skills:
        skill_df = month_df[month_df["skill"] == skill].sort_values("month")
        fig.add_trace(go.Scatter(x=skill_df["month"], y=skill_df["demand_count"], mode="lines", stackgroup="one", name=skill, hovertemplate="%{x}<br>%{fullData.name}: %{y}<extra></extra>"))

    fig.update_layout(title="월별 기술 점유율 변화", xaxis_title="월", yaxis_title="누적 공고 수", hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
