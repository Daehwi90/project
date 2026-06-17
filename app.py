import streamlit as st
import pandas as pd
import folium
import streamlit.components.v1 as components

# 1. 페이지 기본 설정 (넓은 레이아웃)
st.set_page_config(page_title="따릉이 주말 대여소 대시보드", layout="wide")

st.title("🚲 서울시 따릉이 인기 대여소 대시보드 (Top 50)")

# 2. 데이터 불러오기 및 캐싱
# 캐싱(@st.cache_data)을 사용하면 데이터를 한 번만 불러와서 앱 속도가 빨라집니다.
@st.cache_data
def load_data():
    return pd.read_csv('top50_weekend_stations.csv')

df = load_data()

# 3. 상단 요약 지표 (Metrics)
st.markdown("### 📌 요약 지표")
col1, col2, col3 = st.columns(3)
col1.metric(label="Top 50 대여소 갯수", value=f"{len(df)} 개")
col2.metric(label="Top 50 주말 누적 대여건수", value=f"{df['주말'].sum():,} 건")
col3.metric(label="가장 인기있는 대여소", value=df.iloc[0]['대여 대여소명'], delta=f"주말 {df.iloc[0]['주말']:,}건")

st.divider()

# 4. 레이아웃 2분할 (지도 좌측, 차트 우측)
col_map, col_chart = st.columns([1, 1])

with col_map:
    st.markdown("### 📍 주말 인기 대여소 위치")
    
    center_lat = df['대여점위도'].mean()
    center_lon = df['대여점경도'].mean()
    
    # Folium 지도 생성
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
    
    for _, row in df.iterrows():
        popup_txt = f"{row['대여 대여소명']} (주말: {row['주말']}건)"
        # 이용 건수에 따라 마커 크기(radius)를 약간씩 다르게 설정
        folium.CircleMarker(
            location=[row['대여점위도'], row['대여점경도']],
            radius=5 + (row['주말'] / 1000), 
            popup=popup_txt,
            tooltip=row['대여 대여소명'],
            color='crimson',
            fill=True,
            fill_opacity=0.7
        ).add_to(m)
        
    # 생성된 Folium 지도를 Streamlit HTML 컴포넌트로 변환하여 렌더링
    components.html(m._repr_html_(), height=500)

with col_chart:
    st.markdown("### 📊 상위 15개 대여소 주말/평일 비교")
    # 상위 15개만 추출 후 인덱스를 대여소명으로 지정해야 차트의 X축으로 사용됩니다.
    chart_data = df.head(15).set_index('대여 대여소명')[['주말', '평일']]
    st.bar_chart(chart_data)

st.divider()

# 5. 하단 데이터프레임 원본
st.markdown("### 📋 Top 50 상세 데이터")
st.dataframe(df, use_container_width=True)