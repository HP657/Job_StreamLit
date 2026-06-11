import streamlit as st
import plotly.graph_objects as go

from db import load_df
from utils.queries import TOP_SKILLS_RADAR, SKILL_NETWORK, SKILL_ID_MAP
from utils.recommendation import get_recommended_skills


def render(user_skills: list[str]) -> None:
    # ── 레이더 차트 ─────────────────────────────────────────
    st.header("🎯 역량 갭 분석")

    radar_df = load_df(TOP_SKILLS_RADAR)

    max_freq = radar_df["freq"].max() or 1
    # Market: 수요량을 0~100으로 정규화
    market_score = (radar_df["freq"] / max_freq * 100).tolist()
    # User: 보유 여부(0 or 100) — 같은 스케일로 갭 비교
    user_score = [
        100 if skill in user_skills else 0
        for skill in radar_df["name"]
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=user_score, theta=radar_df["name"],
        fill="toself", name="내 역량",
        line=dict(color="#636EFA"),
    ))
    fig.add_trace(go.Scatterpolar(
        r=market_score, theta=radar_df["name"],
        fill="toself", name="시장 수요",
        line=dict(color="#EF553B"),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        legend=dict(orientation="h", y=-0.15),
    )

    if user_skills:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("보유 기술을 선택하면 역량 갭 분석이 표시됩니다.")

    # ── 추천 기술 ───────────────────────────────────────────
    st.divider()
    st.header("📚 같이 배우면 좋은 기술")

    if not user_skills:
        st.info("보유 기술을 선택하면 추천 기술이 표시됩니다.")
        return

    network_df = load_df(SKILL_NETWORK)
    skill_map_df = load_df(SKILL_ID_MAP)
    id_to_name = dict(zip(skill_map_df["id"], skill_map_df["name"]))
    name_to_id = dict(zip(skill_map_df["name"], skill_map_df["id"]))

    recommend_skills = get_recommended_skills(user_skills, network_df, id_to_name, name_to_id)

    if recommend_skills.empty:
        st.info("추천 가능한 기술이 없습니다.")
        return

    st.dataframe(recommend_skills, use_container_width=True)
    st.success(f"가장 추천되는 기술: {recommend_skills.iloc[0]['기술']}")

    st.subheader("❌ 부족 기술 TOP 5")
    st.dataframe(
        recommend_skills.head(5).reset_index(drop=True),
        use_container_width=True,
    )