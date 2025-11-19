import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Riqueza vs Educação",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 A Riqueza Traz Educação?")
st.markdown("Esta aplicação interativa analisa a correlação histórica entre o **PIB per Capita (PPP)** e a **Média de Anos de Estudo** em diversos países entre 1990 e 2023.")
st.divider()

@st.cache_data
def carregar_dados():
    df_wb = pd.read_csv('API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_216039.csv', skiprows=4)
    cols_fixas = ['Country Code', 'Country Name']
    anos = [str(ano) for ano in range(1990, 2024)]
    cols_existentes = [c for c in cols_fixas + anos if c in df_wb.columns]
    
    df_pib = df_wb[cols_existentes].melt(
        id_vars=['Country Code', 'Country Name'], 
        var_name='year', 
        value_name='gdp_per_capita'
    )
    df_pib = df_pib.rename(columns={'Country Code': 'geo', 'Country Name': 'name'})
    df_pib['year'] = pd.to_numeric(df_pib['year'])
    df_pib['geo'] = df_pib['geo'].str.upper()

    df_edu = pd.read_excel('hdr-data.xlsx')
    df_edu.columns = df_edu.columns.str.strip()
    df_edu['year'] = pd.to_numeric(df_edu['year'], errors='coerce')
    df_edu = df_edu[(df_edu['year'] >= 1990) & (df_edu['year'] <= 2023)]
    
    df_edu_final = df_edu[['countryIsoCode', 'year', 'value']].copy()
    df_edu_final = df_edu_final.rename(columns={'countryIsoCode': 'geo', 'value': 'years_schooling'})
    df_edu_final['geo'] = df_edu_final['geo'].str.upper()
    df_edu_final['years_schooling'] = pd.to_numeric(df_edu_final['years_schooling'], errors='coerce')

    df_final = pd.merge(df_pib, df_edu_final, on=['geo', 'year'], how='inner')
    return df_final

try:
    df = carregar_dados()
except Exception as e:
    st.error("Erro ao carregar dados. Verifique os arquivos na pasta.")
    st.stop()

st.sidebar.header("🎛️ Filtros de Análise")

grupos = {
    'G20': ['ARG', 'AUS', 'BRA', 'CAN', 'CHN', 'FRA', 'DEU', 'IND', 'IDN', 'ITA', 'JPN', 'KOR', 'MEX', 'RUS', 'SAU', 'ZAF', 'TUR', 'GBR', 'USA'],
    'BRICS': ['BRA', 'RUS', 'IND', 'CHN', 'ZAF', 'EGY', 'ETH', 'IRN', 'ARE'],
    'G7': ['CAN', 'FRA', 'DEU', 'ITA', 'JPN', 'GBR', 'USA'],
    'Tigres Asiáticos': ['KOR', 'SGP', 'HKG', 'MYS', 'THA', 'VNM', 'IDN', 'PHL', 'CHN'],
    'OCDE': ['USA', 'GBR', 'DEU', 'FRA', 'JPN', 'KOR', 'AUS', 'CAN', 'ESP', 'ITA', 'NLD', 'SWE', 'CHE', 'NOR', 'DNK', 'FIN', 'PRT', 'CHL', 'ISR', 'TUR'],
    'OPEP/Petróleo': ['SAU', 'ARE', 'KWT', 'QAT', 'OMN', 'NGA', 'VEN', 'DZA', 'AGO', 'IRN', 'IRQ', 'LBY'],
    'União Europeia': ['AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'],
    'América Latina': ['ARG', 'BOL', 'BRA', 'CHL', 'COL', 'CRI', 'CUB', 'DOM', 'ECU', 'SLV', 'GTM', 'HND', 'MEX', 'NIC', 'PAN', 'PRY', 'PER', 'URY', 'VEN']
}


grupos['Mundial'] = list(df['geo'].unique())

grupo_selecionado = st.sidebar.selectbox("Escolha um Grupo:", list(grupos.keys()))
lista_paises = grupos[grupo_selecionado]

st.sidebar.divider()
st.sidebar.markdown("### 🗂️ Fontes de Dados")
st.sidebar.markdown(
    """
    1. **Riqueza (PIB PPP):**
    🔗 [Banco Mundial](https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD)
    
    2. **Educação (Anos de Estudo):**
    🔗 [UNDP HDR](https://hdr.undp.org/data-center/documentation-and-downloads)
    """
)

st.sidebar.divider()
st.sidebar.markdown("### Autor")
st.sidebar.info(
    """
    **Thiago Alcebiades Rodrigues**
    
    📧 [thiago.alcebiades@unifesp.br](mailto:thiago.alcebiades@unifesp.br)
    
    👔 [Perfil no LinkedIn](https://www.linkedin.com/in/thiago-alcebiades-rodrigues-95446621b/)
    """
)

st.sidebar.caption(
    """
    **💡 Inspiração:**
    Este projeto foi inspirado no trabalho visionário de [Hans Rosling](https://www.gapminder.org/) e na fundação Gapminder.
    """
)

df_filtrado = df[df['geo'].isin(lista_paises)].dropna()

st.subheader(f"🌍 Evolução Histórica: {grupo_selecionado}")

if df_filtrado.empty:
    st.warning("Dados insuficientes para este grupo.")
else:
    max_x = df_filtrado['gdp_per_capita'].max() * 1.1
    
    fig = px.scatter(
        df_filtrado, 
        x="gdp_per_capita", 
        y="years_schooling",
        animation_frame="year",      
        animation_group="name",     
        size="gdp_per_capita",      
        color="name",                
        hover_name="name",           
        log_x=True,                 
        size_max=60,
        range_x=[500, max_x],       
        range_y=[0, 14],
        labels={
            "gdp_per_capita": "PIB per Capita (US$ PPP)",
            "years_schooling": "Anos de Estudo",
            "name": "País",
            "year": "Ano"
        }
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)