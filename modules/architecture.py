import streamlit as st
import os

def render():
    st.header("🏗️ 프로젝트 아키텍처 및 데이터 흐름")
    
    st.markdown("본 프로젝트는 데이터 수집, 클라우드 DB 동기화, 시각화를 위한 파이프라인으로 구성되어 있습니다.")
    
    # 1. 아키텍처 요약
    c1, c2, c3 = st.columns(3)
    c1.markdown("### 🔍 데이터 수집")
    c1.write("Selenium Crawler")
    c2.markdown("### 💾 데이터 저장")
    c2.write("PostgreSQL / NEON")
    c3.markdown("### 📊 시각화")
    c3.write("Streamlit")
    
    st.divider()

    # 2. DB 스키마를 텍스트/표로 표현 (사진 대신 사용)
    st.subheader("데이터베이스 스키마 (ERD 정보)")
    
    # DB 구조를 표로 상세히 정의
    erd_data = {
        "테이블명": ["job_openings", "skills", "job_opening_skills"],
        "주요 컬럼": ["id, company_name, experience, title", "id, name", "id, job_opening_id, skill_id"],
        "설명": ["채용 공고 기본 정보", "기술 스택 마스터 데이터", "공고와 기술의 매핑(M:N)"]
    }
    st.table(erd_data)
    
    st.divider()

    # 3. 이미지 업로드 공간 (없으면 준비중 메시지 출력)
    st.subheader("데이터 소스: 잡플래닛 채용 공고")
    image_path = "jobplanet_screenshot.png" # 나중에 이 이름으로 파일을 올리세요
    
    if os.path.exists(image_path):
        st.image(image_path, caption="데이터 수집 대상: 잡플래닛 채용 페이지", use_column_width=True)
    else:
        st.info("💡 채용 사이트 스크린샷 이미지를 추가할 공간입니다. 'jobplanet_screenshot.png' 파일을 업로드하면 여기에 표시됩니다.")

    # 4. 상세 프로세스
    with st.expander("기술적 구현 상세 보기"):
        st.write("""
        - **데이터 수집**: 잡플래닛 무한 스크롤 처리를 위해 Selenium WebDriver를 원격 제어합니다.
        - **배포 환경**: 라즈베리파이(ARM) 기반 Docker Compose 환경에서 컨테이너화하여 운영 중입니다.
        - **데이터 동기화**: 로컬 DB에서 NEON 클라우드 DB로 실시간 동기화하여 시각화 안정성을 확보했습니다.
        """)