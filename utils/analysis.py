import pandas as pd
import streamlit as st


def render_sidebar_filters(default_top_n: int = 10) -> tuple[str, str, int]:
    """공통 필터 UI를 렌더링합니다."""
    st.sidebar.header("🔎 분석 필터")
    category = st.sidebar.selectbox("기술 카테고리", ["전체", "백엔드", "프론트엔드", "데이터", "클라우드", "DevOps", "AI"], key="category")
    period = st.sidebar.selectbox("분석 기간", ["최근 30일", "최근 90일", "최근 180일", "전체"], key="period")
    top_n = st.sidebar.slider("상위 N개 표시", 5, 30, default_top_n, key="top_n")
    return category, period, top_n


def filter_period(df: pd.DataFrame, date_col: str, period: str) -> pd.DataFrame:
    """기간 필터를 적용합니다."""
    if df.empty or date_col not in df.columns or period == "전체":
        return df.copy()

    days_map = {"최근 30일": 30, "최근 90일": 90, "최근 180일": 180}
    days = days_map.get(period, 30)

    try:
        date_series = pd.to_datetime(df[date_col], errors="coerce", utc=True)
        if date_series.isna().all():
            return df.copy()

        cutoff = pd.Timestamp.utcnow().normalize().tz_localize("UTC") - pd.Timedelta(days=days)
        return df[date_series >= cutoff].copy()
    except Exception:
        return df.copy()


def limit_top_n(df: pd.DataFrame, count_col: str, top_n: int) -> pd.DataFrame:
    """데이터 과부하 방지를 위해 상위 N개만 유지합니다."""
    if df.empty or count_col not in df.columns:
        return df.copy()
    return df.sort_values(count_col, ascending=False).head(top_n).reset_index(drop=True)


def safe_load_df(query: str, params=None) -> pd.DataFrame:
    """DB 오류가 있어도 빈 DataFrame을 반환해 페이지가 깨지지 않도록 합니다."""
    try:
        from db import load_df

        return load_df(query, params=params)
    except Exception:
        return pd.DataFrame()
