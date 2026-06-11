import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go

# =====================
# PostgreSQL 연결
# =====================


DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = st.secrets["DB_PORT"]
DB_NAME = st.secrets["DB_NAME"]

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require",
    pool_pre_ping=True
)

@st.cache_data(ttl=300)
def load_df(query, params=None):
    return pd.read_sql(
        query,
        engine,
        params=params
    )

st.set_page_config(page_title="시장 가치 분석", layout="wide")

st.title("📊 나의 시장 가치 분석")

# =====================
# 전체 스킬 조회
# =====================

skills_query = """
SELECT name
FROM skills
ORDER BY name
"""

skills_df = load_df(skills_query)

all_skills = skills_df["name"].tolist()

# =====================
# 사용자 입력
# =====================

user_skills = st.multiselect(
    "보유 기술 선택",
    all_skills
)

# =====================
# 시장 요구 역량
# =====================

market_query = """
SELECT
    s.name,
    COUNT(*) AS demand_count
FROM job_openings jo
JOIN job_opening_skills jos
    ON jo.id = jos.job_opening_id
JOIN skills s
    ON s.id = jos.skill_id
GROUP BY s.name
"""

market_df = load_df(market_query)

market_dict = {
    row["name"]: row["demand_count"]
    for _, row in market_df.iterrows()
}

# =====================
# 벡터 생성
# =====================

user_vector = []
market_vector = []

for skill in all_skills:

    if skill in user_skills:
        user_vector.append(1)
    else:
        user_vector.append(0)

    max_demand = max(
        market_dict.values()
    )

    market_vector.append(
        market_dict.get(skill, 0)
        / max_demand
    )

user_vector = np.array(user_vector)
market_vector = np.array(market_vector)

# =====================
# 시장 가치 점수
# =====================

if len(user_skills) > 0:

    score = cosine_similarity(
        [user_vector],
        [market_vector]
    )[0][0]

    match_score = round(score * 100, 2)

    st.subheader("🏆 나의 시장 가치")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "전체 기술 수",
            len(all_skills)
        )

    with col2:
        st.metric(
            "선택 기술 수",
            len(user_skills)
        )

    with col3:
        st.metric(
            "시장 매칭률",
            f"{match_score}%"
        )

    st.progress(match_score / 100)

# =====================
# 성장 가속도
# =====================

growth_query = """
SELECT
    s.name,

    SUM(
        CASE
            WHEN jo.created_at >= CURRENT_DATE - INTERVAL '30 days'
            THEN 1
            ELSE 0
        END
    ) AS recent_count,

    SUM(
        CASE
            WHEN jo.created_at >= CURRENT_DATE - INTERVAL '60 days'
             AND jo.created_at < CURRENT_DATE - INTERVAL '30 days'
            THEN 1
            ELSE 0
        END
    ) AS prev_count

FROM job_openings jo

JOIN job_opening_skills jos
ON jo.id = jos.job_opening_id

JOIN skills s
ON s.id = jos.skill_id

GROUP BY s.name
"""

growth_df = load_df(growth_query)

growth_df["growth_rate"] = (
    (
        growth_df["recent_count"]
        -
        growth_df["prev_count"]
    )
    /
    growth_df["prev_count"].replace(0, 1)
) * 100

# =====================
# 내가 가진 기술 성장률
# =====================

if user_skills:

    my_growth = growth_df[
        growth_df["name"].isin(user_skills)
    ]

    avg_growth = round(
        my_growth["growth_rate"].mean(),
        2
    )

    st.subheader("🚀 성장 가속도")

    st.metric(
        "최근 1개월 기술 성장률",
        f"{avg_growth}%"
    )

    st.dataframe(
        my_growth[
            [
                "name",
                "growth_rate"
            ]
        ]
        .sort_values(
            "growth_rate",
            ascending=False
        )
    )

st.divider()
st.header("🎯 역량 갭 분석")

radar_query = """
SELECT
    s.name,
    COUNT(*) freq
FROM job_openings jo
JOIN job_opening_skills jos
ON jo.id = jos.job_opening_id
JOIN skills s
ON s.id = jos.skill_id
GROUP BY s.name
ORDER BY freq DESC
LIMIT 6
"""

radar_df = load_df(radar_query)

market_score = radar_df["freq"].tolist()

user_score = []

for skill in radar_df["name"]:
    if skill in user_skills:
        user_score.append(
            market_dict.get(skill, 0)
        )
    else:
        user_score.append(0)

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=user_score,
        theta=radar_df["name"],
        fill="toself",
        name="User"
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=market_score,
        theta=radar_df["name"],
        fill="toself",
        name="Market"
    )
)

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True
        )
    )
)

if user_skills:
    st.plotly_chart(
        fig,
        use_container_width=True
    )
else:
    st.info(
        "보유 기술을 선택하면 역량 갭 분석이 표시됩니다."
    )


st.divider()
st.header("📚 같이 배우면 좋은 기술")

if user_skills:

    skill_network_query = """
    SELECT
        jo1.skill_id AS base_skill,
        jo2.skill_id AS related_skill,
        COUNT(*) AS freq
    FROM job_opening_skills jo1
    JOIN job_opening_skills jo2
        ON jo1.job_opening_id = jo2.job_opening_id
    WHERE jo1.skill_id <> jo2.skill_id
    GROUP BY
        jo1.skill_id,
        jo2.skill_id
    """

    network_df = load_df(skill_network_query)

    skill_map_query = """
    SELECT
        id,
        name
    FROM skills
    """

    skill_map_df = load_df(skill_map_query)

    id_to_name = dict(
        zip(
            skill_map_df["id"],
            skill_map_df["name"]
        )
    )

    name_to_id = dict(
        zip(
            skill_map_df["name"],
            skill_map_df["id"]
        )
    )

    selected_ids = [
        name_to_id[s]
        for s in user_skills
        if s in name_to_id
    ]

    recommend_scores = {}

    for skill_id in selected_ids:

        related = network_df[
            network_df["base_skill"] == skill_id
        ]

        for _, row in related.iterrows():

            related_skill = row["related_skill"]

            if related_skill in selected_ids:
                continue

            recommend_scores[
                related_skill
            ] = (
                recommend_scores.get(
                    related_skill,
                    0
                )
                + row["freq"]
            )

    recommend_skills = pd.DataFrame(
        [
            {
                "기술": id_to_name[k],
                "연관도": v
            }
            for k, v in recommend_scores.items()
        ]
    )

    if not recommend_skills.empty:

        recommend_skills = (
            recommend_skills
            .sort_values(
                "연관도",
                ascending=False
            )
            .head(10)
        )

        st.dataframe(
            recommend_skills,
            use_container_width=True
        )

        st.success(
            f"가장 추천되는 기술: "
            f"{recommend_skills.iloc[0]['기술']}"
        )
        st.subheader("❌ 부족 기술 TOP5")

        top5_skills = (
            recommend_skills
            .head(5)
        )

        for _, row in top5_skills.iterrows():

            st.metric(
                label=row["기술"],
                value=f"{row['연관도']:,}"
            )

    else:
        st.info(
            "추천 가능한 기술이 없습니다."
        )

st.divider()
st.header("🏢 추천 기업")

if user_skills:

    company_query = """
    SELECT
        jo.company_name,
        s.name
    FROM job_openings jo
    JOIN job_opening_skills jos
    ON jo.id = jos.job_opening_id
    JOIN skills s
    ON s.id = jos.skill_id
    """

    company_df = load_df(
        company_query
    )

    company_matrix = pd.crosstab(
        company_df["company_name"],
        company_df["name"]
    )

    if company_matrix.empty:
        st.warning("추천 가능한 기업 데이터가 없습니다.")
    else:

        user_company_vector = []

        for skill in company_matrix.columns:

            if skill in user_skills:
                user_company_vector.append(1)
            else:
                user_company_vector.append(0)

        scores = cosine_similarity(
            [user_company_vector],
            company_matrix.values
        )[0]

        recommend_df = pd.DataFrame({
            "회사": company_matrix.index,
            "매칭도": np.round(scores * 100, 2)
        })

        recommend_df = (
            recommend_df[
                recommend_df["매칭도"] > 10
            ]
            .sort_values(
                "매칭도",
                ascending=False
            )
            .head(10)
        )

        st.dataframe(
            recommend_df,
            use_container_width=True
        )

        if not recommend_df.empty:
            top_company = recommend_df.iloc[0]

            st.success(
                f"가장 적합한 기업: {top_company['회사']} "
                f"(매칭도 {top_company['매칭도']}%)"
            )

else:
    st.info(
        "보유 기술을 선택하면 추천 기업이 표시됩니다."
    )