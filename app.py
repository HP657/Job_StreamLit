import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity

# =====================
# PostgreSQL 연결
# =====================


DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = st.secrets["DB_PORT"]
DB_NAME = st.secrets["DB_NAME"]

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
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

skills_df = pd.read_sql(skills_query, engine)

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

market_df = pd.read_sql(market_query, engine)

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

    market_vector.append(
        market_dict.get(skill, 0)
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

    st.metric(
        "매칭 점수",
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

growth_df = pd.read_sql(
    growth_query,
    engine
)

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