import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# 제목
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("---")

# 데이터 불러오기 함수
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre 열 전처리: 안전하게 문자열로 변환 후 첫 번째 장르만 추출 (NaN 처리 강화)
    df['genre'] = df['genre'].apply(lambda x: str(x).split('|')[0] if pd.notna(x) and x != '' else '기타')
    
    # 숫자로 다뤄야 하는 열 형식 변환 및 예외 처리
    numeric_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    return df

try:
    df = load_data()
    
    # ---------------------------------------------------------
    # 1. 장르별 영화 편수 도넛 그래프
    # ---------------------------------------------------------
    st.subheader("1. 장르별 영화 편수 (도넛 그래프)")
    
    # 장르별 편수 집계
    genre_counts = df['genre'].value_counts().reset_index()
    genre_counts.columns = ['장르', '편수']
    
    # Plotly 도넛 차트 생성
    fig1 = px.pie(
        genre_counts, 
        values='편수', 
        names='장르', 
        hole=0.4,
        title="장르별 영화 편수 분포"
    )
    fig1.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate="<b>장르:</b> %{label}<br><b>편수:</b> %{value}편<br><b>비율:</b> %{percent}"
    )
    fig1.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 그래프 1 설명 및 인사이트 구역
    with st.container():
        st.info("💡 **이 그래프로 알 수 있는 것:** 1번 각 장르별 영화가 얼마나 나왔는지 알 수 있다.")
    
    st.markdown("---")
    
    # ---------------------------------------------------------
    # 2. 장르별 영화 총 관객수 트리맵
    # ---------------------------------------------------------
    st.subheader("2. 장르 및 영화별 총 관객수 (트리맵)")
    
    # Plotly 트리맵 생성
    fig2 = px.treemap(
        df,
        path=['genre', 'movieNm'],
        values='total_audi',
        title="장르 및 영화별 총 관객수 분포 (칸 크기 = 총 관객수)",
        hover_data={'total_audi': ':,d'}
    )
    
    fig2.update_traces(
        hovertemplate="<b>영화명:</b> %{label}<br><b>총 관객수:</b> %{value:,} 명"
    )
    fig2.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # 그래프 2 설명 및 인사이트 구역
    with st.container():
        st.info("💡 **이 그래프로 알 수 있는 것:** 2번 각 장르별 어떤 영화가 흥행했는지 한눈에 볼 수가 있다.")

    st.markdown("---")

    # ---------------------------------------------------------
    # 3. 총 관객수 히스토그램
    # ---------------------------------------------------------
    st.subheader("3. 영화별 총 관객수 분포 (히스토그램)")
    
    # Plotly 히스토그램 생성
    fig3 = px.histogram(
        df,
        x='total_audi',
        nbins=30,
        title="총 관객수 분포 히스토그램",
        labels={'total_audi': '총 관객수(명)', 'count': '영화 편수'},
        color_discrete_sequence=['#636EFA']
    )
    
    fig3.update_traces(
        hovertemplate="<b>관객수 구간:</b> %{x}명대<br><b>영화 수:</b> %{y}편"
    )
    fig3.update_layout(
        yaxis_title="영화 편수(개)",
        xaxis_title="총 관객수(명)",
        bargap=0.1,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig3, use_container_width=True)

    # 최고 흥행작 계산
    top_movie = df.loc[df['total_audi'].idxmax()]
    under_1m_pct = (df['total_audi'] < 1000000).mean() * 100

    # 동적 분석 문구 및 인사이트 구역
    st.markdown(f"📌 **관객수 구간 분석:** 박스오피스 상위권 영화 중에서도 **약 {under_1m_pct:.1f}%의 영화가 100만 명 미만 구간**에 집중되어 있습니다. 가장 많은 관객을 동원한 영화는 **'{top_movie['movieNm']}'**(약 {top_movie['total_audi']:,.0f}명)입니다.")
    
    with st.container():
        st.info("💡 **이 그래프로 알 수 있는 것:** 3번 어떤 영화가 많이 흥행하고 어떤 영화를 많이 안 흥행하는지 알 수가 있다.")

    st.markdown("---")

    # ---------------------------------------------------------
    # 4. 개봉일 스크린수 vs 총 관객수 (산점도)
    # ---------------------------------------------------------
    st.subheader("4. 개봉일 스크린수와 총 관객수의 관계 (산점도)")
    
    # Plotly 산점도 생성
    fig4 = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        color='genre',
        hover_name='movieNm',
        title="개봉일 스크린수 vs 총 관객수",
        labels={
            'first_scrn': '개봉일 스크린수(개)',
            'total_audi': '총 관객수(명)',
            'genre': '장르'
        },
        hover_data={
            'first_scrn': ':,d',
            'total_audi': ':,d',
            'genre': True
        }
    )
    
    fig4.update_traces(
        marker=dict(size=9, opacity=0.8),
        hovertemplate="<b>%{hovertext}</b><br>장르: %{customdata[2]}<br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명"
    )
    fig4.update_layout(
        xaxis_title="개봉일 스크린수(개)",
        yaxis_title="총 관객수(명)",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig4, use_container_width=True)

    # 그래프 4 설명 및 인사이트 구역
    with st.container():
        st.info("💡 **이 그래프로 알 수 있는 것:** 4번 장르별 색으로 어떤 영화가 개봉일 후 흥행했는지 알 수가 있다 위치별로")

    st.markdown("---")

    # ---------------------------------------------------------
    # 5. 영화 10편 이상 장르의 총 관객수 상자 그림 (박스플롯)
    # ---------------------------------------------------------
    st.subheader("5. 주요 장르별 총 관객수 분포 (박스플롯)")
    
    # 영화 수가 10편 이상인 장르 필터링
    genre_counts_series = df['genre'].value_counts()
    major_genres = genre_counts_series[genre_counts_series >= 10].index.tolist()
    df_filtered = df[df['genre'].isin(major_genres)]
    
    # Plotly 박스플롯 생성
    fig5 = px.box(
        df_filtered,
        x='genre',
        y='total_audi',
        color='genre',
        hover_name='movieNm',
        points='outliers',
        title="영화 10편 이상 장르별 총 관객수 박스플롯 (이상치 = 독보적 흥행작)",
        labels={
            'genre': '장르',
            'total_audi': '총 관객수(명)'
        }
    )
    
    fig5.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>총 관객수: %{y:,}명"
    )
    fig5.update_layout(
        xaxis_title="장르",
        yaxis_title="총 관객수(명)",
        showlegend=False,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig5, use_container_width=True)

    # 그래프 5 설명 및 인사이트 구역
    with st.container():
        st.info("💡 **이 그래프로 알 수 있는 것:** 5번 각 장르별 초대박 흥행작이 있는지 없는지 흥행했다면 얼마나 흥행했는지 알 수가 있다.")

    st.markdown("---")

    # ---------------------------------------------------------
    # 6. 개봉일 스크린수 vs 총 관객수 버블 차트 (점 크기 = 첫 주 관객수)
    # ---------------------------------------------------------
    st.subheader("6. 개봉일 스크린수와 총 관객수의 관계 (버블 차트)")
    
    # Plotly 버블 차트 생성
    fig6 = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        size='first_week_audi',
        color='genre',
        hover_name='movieNm',
        size_max=40,
        title="개봉일 스크린수 vs 총 관객수 (버블 크기 = 개봉 첫 주 관객수)",
        labels={
            'first_scrn': '개봉일 스크린수(개)',
            'total_audi': '총 관객수(명)',
            'first_week_audi': '개봉 첫 주 관객수(명)',
            'genre': '장르'
        },
        hover_data={
            'first_scrn': ':,d',
            'total_audi': ':,d',
            'first_week_audi': ':,d',
            'genre': True
        }
    )
    
    fig6.update_traces(
        marker=dict(opacity=0.7),
        hovertemplate="<b>%{hovertext}</b><br>장르: %{customdata[3]}<br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<br>첫 주 관객수: %{customdata[2]:,}명"
    )
    fig6.update_layout(
        xaxis_title="개봉일 스크린수(개)",
        yaxis_title="총 관객수(명)",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig6, use_container_width=True)

    # 그래프 6 설명 및 인사이트 구역
    with st.container():
        st.info("💡 **이 그래프로 알 수 있는 것:** 6번 버블의 크기로 각 장르별 영화가 얼마나 흥행했는지 알 수가 있다.")

    st.markdown("---")

    # ---------------------------------------------------------
    # 7. 제작 국가별-장르별 계층 구조 (선버스트 차트)
    # ---------------------------------------------------------
    st.subheader("7. 제작 국가 및 장르별 영화 편수 구조 (선버스트 차트)")
    
    # 국가(nation) -> 장르(genre) 계층 구조 집계
    sunburst_df = df.groupby(['nation', 'genre']).size().reset_index(name='편수')
    
    # Plotly 선버스트 차트 생성
    fig7 = px.sunburst(
        sunburst_df,
        path=['nation', 'genre'],
        values='편수',
        title="제작 국가 → 장르 계층별 영화 편수 (칸 크기 = 영화 편수)"
    )
    
    fig7.update_traces(
        hovertemplate="<b>구분:</b> %{label}<br><b>영화 편수:</b> %{value}편<br><b>비율:</b> %{percentParent:.1%}"
    )
    fig7.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    
    st.plotly_chart(fig7, use_container_width=True)

    # 그래프 7 설명 및 인사이트 구역
    with st.container():
        st.info("💡 **이 그래프로 알 수 있는 것:** 7번 각 장르별로 어떤 나라가 많이 냈는지 알 수가 있다.")

    st.markdown("---")

    # ---------------------------------------------------------
    # 8. 개봉 첫 주 관객수 구간별 평균 총 관객수 (막대 그래프)
    # ---------------------------------------------------------
    st.subheader("8. 개봉 첫 주 관객수 구간별 평균 총 관객수 (막대 그래프)")
    
    # 개봉 첫 주 관객수 구간(Bin) 생성
    bins = [0, 100000, 500000, 1000000, 3000000, 100000000]
    labels = ['10만 미만', '10만~50만', '50만~100만', '100만~300만', '300만 이상']
    
    df_first_week = df.copy()
    df_first_week['first_week_group'] = pd.cut(df_first_week['first_week_audi'], bins=bins, labels=labels, right=False)
    
    # 첫 주 관객수 구간별 평균 총 관객수 및 영화 수 집계
    first_week_summary = df_first_week.groupby('first_week_group', observed=False).agg(
        avg_total_audi=('total_audi', 'mean'),
        movie_count=('movieNm', 'count')
    ).reset_index()
    
    fig8 = px.bar(
        first_week_summary,
        x='first_week_group',
        y='avg_total_audi',
        color='first_week_group',
        text_auto='.2s',
        title="개봉 첫 주 관객수 구간별 평균 최종 총 관객수",
        labels={
            'first_week_group': '개봉 첫 주 관객수 구간',
            'avg_total_audi': '평균 총 관객수(명)',
            'movie_count': '영화 편수'
        },
        hover_data=['movie_count']
    )
    
    fig8.update_traces(
        hovertemplate="<b>첫 주 관객 구간:</b> %{x}<br><b>평균 총 관객수:</b> %{y:,.0f}명<br><b>영화 수:</b> %{customdata[0]}편"
    )
    fig8.update_layout(
        xaxis_title="개봉 첫 주 관객수 구간",
        yaxis_title="평균 총 관객수(명)",
        showlegend=False,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig8, use_container_width=True)

    # 그래프 8 설명 및 인사이트 구역
    with st.container():
        st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 첫 주에 들어온 관객 수 구간에 따라 최종 평균 총 관객수가 얼마나 차이나는지 직관적인 막대의 높이로 비교해 알 수가 있다.")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
