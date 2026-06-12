import plotly.graph_objects as go
import streamlit as st

<<<<<<< Updated upstream
from utils.analysis import safe_load_df
from utils.queries import SKILL_NETWORK, SKILL_ID_MAP
from utils.recommendation import get_recommended_skills
from utils.graphs import build_network_graph
=======
from db import load_df
from utils.analysis import render_sidebar_filters
from utils.queries import MARKET_DEMAND
import pages.skill_network as skill_network_page
>>>>>>> Stashed changes


def render(user_skills: list[str]) -> None:
    st.header("📚 역량 갭 분석")
    _, _, top_n = render_sidebar_filters(default_top_n=8)

    if not user_skills:
        st.info("보유 기술을 선택하면 역량 갭 분석이 표시됩니다.")
        return

    network_df = safe_load_df(SKILL_NETWORK)
    skill_map_df = safe_load_df(SKILL_ID_MAP)
    id_to_name = dict(zip(skill_map_df["id"], skill_map_df["name"]))
    name_to_id = dict(zip(skill_map_df["name"], skill_map_df["id"]))

    market_df = market_df.rename(columns={"name": "skill", "demand_count": "market_demand"})
    market_df = market_df[market_df["skill"].isin(user_skills)].copy()
    market_df["user_score"] = 5
    market_df["market_avg"] = market_df["market_demand"].rank(pct=True) * 5
    market_df = market_df.sort_values("market_demand", ascending=False).head(top_n)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=market_df["user_score"].tolist(), theta=market_df["skill"].tolist(), fill="toself", name="보유 역량", marker=dict(color="rgba(31,119,180,0.75)"), hovertemplate="%{theta}: %{r}점<extra></extra>"))
    fig.add_trace(go.Scatterpolar(r=market_df["market_avg"].tolist(), theta=market_df["skill"].tolist(), fill="toself", name="시장 평균", marker=dict(color="rgba(255,127,14,0.75)"), hovertemplate="%{theta}: %{r:.1f}점<extra></extra>"))

    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), title="목표 기술 대비 역량 갭", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🕸️ 기술 연관성 네트워크")
    skill_network_page.render()

    st.caption("※ 상위 N개 기술만 레이더 차트에 표시해 보유 역량과 시장 평균을 한눈에 비교합니다.")