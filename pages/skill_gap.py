import streamlit as st

from db import load_df
from utils.queries import SKILL_NETWORK, SKILL_ID_MAP
from utils.recommendation import get_recommended_skills


def render(user_skills: list[str]) -> None:
    # ── 추천 기술 ───────────────────────────────────────────
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