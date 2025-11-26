import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Wealth vs Education",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Wealth & Education: What's the Relationship?")
st.markdown("This interactive application analyzes the historical correlation between **GDP per Capita (PPP)** and **Mean Years of Schooling** across countries from 1990 to 2023.")
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

    df_pop = pd.read_csv('API_SP.POP.TOTL_DS2_en_csv_v2_246068.csv', skiprows=4)
    cols_existentes_pop = [c for c in cols_fixas + anos if c in df_pop.columns]
    df_pop = df_pop[cols_existentes_pop].melt(
        id_vars=['Country Code', 'Country Name'],
        var_name='year',
        value_name='population'
    )
    df_pop = df_pop.rename(columns={'Country Code': 'geo', 'Country Name': 'name'})
    df_pop['year'] = pd.to_numeric(df_pop['year'])
    df_pop['geo'] = df_pop['geo'].str.upper()
    df_pop['population'] = pd.to_numeric(df_pop['population'], errors='coerce')

    df_final = pd.merge(df_pib, df_edu_final, on=['geo', 'year'], how='inner')
    df_final = pd.merge(df_final, df_pop[['geo', 'year', 'population']], on=['geo', 'year'], how='left')
    # formatted population string with thousands separator (comma)
    df_final['population_str'] = df_final['population'].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) else "N/A"
    )
    return df_final

try:
    df = carregar_dados()
except Exception as e:
    st.error("Error loading data. Please check the required files are present in the folder.")
    st.stop()

st.sidebar.header("🎛️ Analysis Filters")

grupos = {
    'G20': ['ARG', 'AUS', 'BRA', 'CAN', 'CHN', 'FRA', 'DEU', 'IND', 'IDN', 'ITA', 'JPN', 'KOR', 'MEX', 'RUS', 'SAU', 'ZAF', 'TUR', 'GBR', 'USA', 'ESP'],
    'BRICS (Expanded)': ['BRA', 'RUS', 'IND', 'CHN', 'ZAF', 'EGY', 'ETH', 'IRN', 'ARE', 'SAU'],
    'G7': ['CAN', 'FRA', 'DEU', 'ITA', 'JPN', 'GBR', 'USA'],
    'South America': ['ARG', 'BOL', 'BRA', 'CHL', 'COL', 'ECU', 'GUY', 'PRY', 'PER', 'SUR', 'URY', 'VEN'],
    'Latin America & Caribbean': ['ARG', 'BHS', 'BRB', 'BLZ', 'BOL', 'BRA', 'CHL', 'COL', 'CRI', 'CUB', 'DOM', 'ECU', 'SLV', 'GTM', 'GUY', 'HTI', 'HND', 'JAM', 'MEX', 'NIC', 'PAN', 'PRY', 'PER', 'SUR', 'TTO', 'URY', 'VEN'],
    'Asia (Major)': ['CHN', 'JPN', 'IND', 'KOR', 'IDN', 'SAU', 'TUR', 'THA', 'MYS', 'VNM', 'PHL', 'SGP', 'BGD', 'PAK'],
    'Europe (European Union)': ['AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'],
    'Lusophone Countries': ['BRA', 'PRT', 'AGO', 'MOZ', 'CPV', 'GNB', 'STP', 'TLS'],
    'Asian Tigers (+ New)': ['KOR', 'SGP', 'HKG', 'TWN', 'MYS', 'THA', 'VNM', 'IDN'], 
    'OPEC + Others': ['SAU', 'ARE', 'KWT', 'QAT', 'OMN', 'NGA', 'VEN', 'DZA', 'AGO', 'IRN', 'IRQ', 'LBY', 'RUS', 'GUY']
}

grupos['World'] = list(df['geo'].unique())

grupo_selecionado = st.sidebar.selectbox("Choose a Group:", list(grupos.keys()))
lista_paises = grupos[grupo_selecionado]

st.sidebar.divider()
st.sidebar.markdown("### 🗂️ Data Sources")
st.sidebar.markdown(
    """
    1. **Wealth (GDP PPP):**
    🔗 [World Bank](https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD)
    
    2. **Education (Mean Years of Schooling):**
    🔗 [UNDP HDR](https://hdr.undp.org/data-center/documentation-and-downloads)
    """
)

st.sidebar.divider()
st.sidebar.markdown("### Author")
st.sidebar.info(
    """
    **Thiago Alcebiades Rodrigues**
    
    📧 [thiago.alcebiades@unifesp.br](mailto:thiago.alcebiades@unifesp.br)
    
    👔 [LinkedIn Profile](https://www.linkedin.com/in/thiago-alcebiades-rodrigues-95446621b/)
    """
)

st.sidebar.caption(
    """
    **💡 Inspiration:**
    This project was inspired by the work of [Hans Rosling](https://www.gapminder.org/) and the Gapminder foundation.
    """
)

df_filtrado = df[df['geo'].isin(lista_paises)].dropna(subset=['gdp_per_capita', 'years_schooling']).copy()
df_filtrado['population_for_size'] = df_filtrado['population'].fillna(1)

st.subheader(f"🌍 Historical Evolution: {grupo_selecionado}")

if df_filtrado.empty:
    st.warning("Insufficient data for this group.")
else:
    max_x = df_filtrado['gdp_per_capita'].max() * 1.3
    
    fig = px.scatter(
        df_filtrado, 
        x="gdp_per_capita", 
        y="years_schooling",
        animation_frame="year",      
        animation_group="name",     
        size="population_for_size",      
        color="name",                
        hover_name="name",  
        custom_data=["gdp_per_capita", "population", "population_str"],   
        log_x=True,                 
        size_max=60,
        range_x=[500, max_x],       
        range_y=[0, 16],
        labels={
            "gdp_per_capita": "GDP per Capita (US$ PPP)",
            "years_schooling": "Years of Schooling",
            "name": "Country",
            "year": "Year"
        }
    )
    
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b>\n"
            "GDP per Capita (US$ PPP): %{customdata[0]:,.2f}\n"
            "Population: %{customdata[2]}\n"
            "Years of Schooling: %{y:.2f}<extra></extra>"
        )
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)