import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

df = pd.read_csv('streamlit/data/AtropellosGS2015.csv')

st.set_page_config(
    page_title="Santiago de Chile Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded")
alt.theme.enable("dark")

with st.sidebar:
    st.title('Santiago de Chile Car Crashes')
    street_list = df['Ubicacion']
    single_street = st.selectbox('Select a street:', street_list)
    multi_street = st.multiselect('Select multiple streets:', street_list)

col = st.columns((2.5, 4, 2), gap='medium')

def make_donut_chart(df, single_street, total_accidents_single):
    total_accidents_all = df['Accidentes'].sum()
    percent = 0 if total_accidents_all == 0 else round((total_accidents_single / total_accidents_all) * 100, 2)
    
    data = pd.DataFrame({
        'Category': [single_street, 'Other Streets'],
        'Accidents': [total_accidents_single, total_accidents_all - total_accidents_single]
    })
    
    chart_colors = ["#00EA42", '#BDC3C7']
    
    donut = alt.Chart(data).mark_arc(innerRadius=60, cornerRadius=10).encode(
        theta='Accidents',
        color=alt.Color('Category:N',
                        scale=alt.Scale(domain=[single_street, 'Other Streets'],
                                        range=chart_colors),
                        legend=None),
        tooltip=['Category', 'Accidents']
    ).properties(
        width='container',
        height=250
    )

    text = alt.Chart(pd.DataFrame({'text': [f'{percent}%']})).mark_text(
        align='center',
        baseline='middle',
        fontSize=36,
        fontWeight=700,
        color='#00EA42'
    ).encode(text='text:N')

    return donut + text

with col[0]:
    st.markdown('#### Total Crashes')
    clean_street = single_street.split(',')[0].strip()
    if '&' in clean_street:
        clean_street = clean_street.split('&')[0].strip()
    mask_single = df['Ubicacion'].str.contains(clean_street, case=False, na=False)
    total_accidents_single = df.loc[mask_single, 'Accidentes'].sum()

    st.metric(label=f'Crashes on {clean_street}:', value=int(total_accidents_single))
    
    st.markdown('#### Total Crashes')
    total_accidents_multi = 0
    unique_clean_streets = set()

    for s in multi_street:
        clean = s.split(',')[0].strip()
        if '&' in clean:
            clean = clean.split('&')[0].strip()

        if clean.lower() not in unique_clean_streets:
            mask = df['Ubicacion'].str.contains(clean, case=False, na=False)
            total_accidents_multi += df.loc[mask, 'Accidentes'].sum()
            unique_clean_streets.add(clean.lower())
    st.metric(label='Crashes on multiple streets:', value=int(total_accidents_multi))
    st.altair_chart(make_donut_chart(df, single_street, total_accidents_single), use_container_width=True)


def make_map():
    if multi_street:
        street_df = df[df['Ubicacion'].isin(multi_street)]
    else:
        street_df = df[df['Ubicacion'] == single_street]
    map = px.scatter_map(street_df,
                        lat='X',
                        lon='Y',
                        hover_name='Ubicacion',
                        hover_data='Accidentes',
                        zoom=9)
    return map

def make_heatmap():
    corr = df[['Fallecidos', 'Graves', 'MenosGrave', 'Leve', 'Accidentes']].corr()
    map = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale='Reds',
        title='Correlation Heatmap of Accident Severity'
    )

    return map

with col[1]:
    st.markdown('#### Crashes at point on street')
    st.plotly_chart(make_map(), use_container_width=True)
    st.plotly_chart(make_heatmap(), use_container_width=True)

with col[2]:
    with st.expander('Summary', expanded=True):
        st.write(f'''
            - Total Accidents: {df['Accidentes'].sum()}
            - Total Fatalities: {df['Fallecidos'].sum()}
            - Total Seriously Injured: {df['Graves'].sum()}
            - Total Moderatly Injured: {df['MenosGrave'].sum()}
            - Total Minorly Injured: {df['Leve'].sum()}
            - Average Injured Per Crash: {round((df['Fallecidos'] + df['Graves'] + 
                                           df['MenosGrave'] + df['Leve']).sum() / 
                                           df['Accidentes'].sum())}
            - Data: [Kaggle Car Accidents (Santiago de Chile)](<https://www.kaggle.com/datasets/sandorabad/georeferenced-car-accidents-santiago-de-chile>).
        ''')
    st.write("#### Insights:\n" +
            "The dashboard was able to show hotspot locations of each accident.\n" +
            "The most deadly areas were streets that had the highest amount of crashes.\n" +
            "There were correlations between severity of accidents and total amount of accidents.")
