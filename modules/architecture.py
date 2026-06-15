import streamlit as st

def render():
    st.header("🏗️ 프로젝트 아키텍처 및 데이터 흐름")
    
    st.markdown("""
    본 프로젝트는 정기적인 데이터 수집, 클라우드 DB 동기화, 그리고 실시간 시각화를 위한 3단계 데이터 파이프라인으로 구성되어 있습니다.
    """)
    
    # 1. 아키텍처 흐름 시각화
    st.subheader("데이터 수집 및 동기화 파이프라인")
    st.info("Crawler(Raspberry Pi) → PostgreSQL(Local) → NEON DB(Cloud) → Streamlit(Visualization)")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("데이터 수집", "Selenium Crawler")
    col2.metric("데이터 저장", "PostgreSQL/NEON")
    col3.metric("시각화", "Streamlit")
    
    # 2. DB 구조 설명 (제공해주신 ERD 기반)
    st.subheader("데이터베이스 스키마 (ERD)")
    st.image("image_909ce6.png", caption="Job Opening 데이터베이스 관계도")
    
    # 3. 상세 프로세스
    with st.expander("기술적 구현 상세 보기"):
        st.write("""
        - **데이터 수집**: 잡플래닛의 무한 스크롤 방식을 처리하기 위해 `seleniarm/standalone-chromium` 이미지를 활용하여 크롬 드라이버를 원격 제어합니다.
        - **환경**: 라즈베리파이(ARM 아키텍처) 기반의 Docker Compose 환경에서 운영됩니다.
        - **동기화**: 로컬 PostgreSQL에 수집된 데이터는 NEON 클라우드 DB로 동기화되어 외부 접근성 및 대시보드 연결성을 확보합니다.
        """)
    
    # 4. 잡플래닛 크롤링 예시 (잡플래닛 이미지 추가)
    st.subheader("데이터 소스: 잡플래닛 채용 공고")
    # 여기에 잡플래닛 이미지 파일 경로를 넣어주세요
    # st.image("잡플래닛_이미지_경로.png", caption="데이터 수집 대상: 잡플래닛 채용 공고 페이지")