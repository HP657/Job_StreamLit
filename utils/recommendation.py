import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def build_user_market_vectors(
    all_skills: list[str],
    user_skills: list[str],
    market_dict: dict,
) -> tuple[np.ndarray, np.ndarray]:
    """사용자 벡터와 시장 수요 벡터를 생성합니다."""
    max_demand = max(market_dict.values()) if market_dict else 1

    user_vector = np.array([
        1 if skill in user_skills else 0
        for skill in all_skills
    ])
    market_vector = np.array([
        market_dict.get(skill, 0) / max_demand
        for skill in all_skills
    ])

    return user_vector, market_vector


def calc_market_match_score(
    user_vector: np.ndarray,
    market_vector: np.ndarray,
) -> float:
    """코사인 유사도 기반 시장 매칭률(0~100)을 반환합니다."""
    score = cosine_similarity([user_vector], [market_vector])[0][0]
    return round(score * 100, 2)


def calc_growth_rate(growth_df: pd.DataFrame) -> pd.DataFrame:
    """최근/이전 기간 비교로 성장률 컬럼을 추가합니다."""
    df = growth_df.copy()
    df["growth_rate"] = (
        (df["recent_count"] - df["prev_count"])
        / df["prev_count"].replace(0, 1)
    ) * 100
    return df


def get_recommended_skills(
    user_skills: list[str],
    network_df: pd.DataFrame,
    id_to_name: dict,
    name_to_id: dict,
    top_n: int = 10,
) -> pd.DataFrame:
    """연관 기술 네트워크에서 추천 기술을 계산합니다."""
    selected_ids = [name_to_id[s] for s in user_skills if s in name_to_id]
    recommend_scores: dict = {}

    for skill_id in selected_ids:
        related = network_df[network_df["base_skill"] == skill_id]
        for _, row in related.iterrows():
            related_skill = row["related_skill"]
            if related_skill in selected_ids:
                continue
            recommend_scores[related_skill] = (
                recommend_scores.get(related_skill, 0) + row["freq"]
            )

    if not recommend_scores:
        return pd.DataFrame(columns=["기술", "연관도"])

    return (
        pd.DataFrame([
            {"기술": id_to_name[k], "연관도": v}
            for k, v in recommend_scores.items()
        ])
        .sort_values("연관도", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def get_recommended_companies(
    user_skills: list[str],
    company_df: pd.DataFrame,
    top_n: int = 10,
    min_match: float = 10.0,
) -> pd.DataFrame:
    """사용자 스킬과 기업 요구 스킬의 코사인 유사도로 추천 기업을 반환합니다."""
    company_matrix = pd.crosstab(company_df["company_name"], company_df["name"])

    if company_matrix.empty:
        return pd.DataFrame(columns=["회사", "매칭도"])

    user_vector = np.array([
        1 if skill in user_skills else 0
        for skill in company_matrix.columns
    ])
    scores = cosine_similarity([user_vector], company_matrix.values)[0]

    return (
        pd.DataFrame({"회사": company_matrix.index, "매칭도": np.round(scores * 100, 2)})
        .query(f"매칭도 > {min_match}")
        .sort_values("매칭도", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )