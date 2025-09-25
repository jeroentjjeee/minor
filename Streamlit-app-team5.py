import streamlit as st
import requests
import pandas as pd
import plotly.express as px


url1 = 'https://opendata.cbs.nl/ODataApi/odata/80345eng/TypedDataSet'
url2 = 'https://opendata.cbs.nl/ODataApi/odata/70187eng/TypedDataSet'


headers = {
    "Accept": "application/json"
}

response1 = requests.get(url1, headers=headers)

if response1.status_code == 200:
    data = response1.json()
    records = data.get('value', [])
    
    # Zet lijst van dicts om in DataFrame
    df1 = pd.DataFrame(records)
    
    
else:
    print(f"Fout bij ophalen data: {response1.status_code}")

response2 = requests.get(url2, headers=headers)

if response2.status_code == 200:
    data = response2.json()
    records = data.get('value', [])
    
    # Zet lijst van dicts om in DataFrame
    df2 = pd.DataFrame(records)
    
    
else:
    print(f"Fout bij ophalen data: {response2.status_code}")

df1['Year'] = df1["Periods"].str[:4].astype(int)
df2["Year"] = df2["Periods"].str[:4].astype(int)

cprijs = df1.bfill()
inkomen = df2.bfill()


j1990 = cprijs['Year'] >= 1990
j2000 = cprijs['Year'] <= 2000
cprijs = cprijs[j1990 & j2000]
df = cprijs.merge(inkomen, on = 'Year')
df = df.drop(['ID_x', 'Periods_x', 'ID_y', 'Periods_y','CompositionOfTheHousehold', 'OtherHouseholdCharacteristics', 'NumberOfHouseholds_1', 'PersonsPerHousehold_2', 'PersonsWithAnIncomePerHousehold_3' ], axis = 1).drop_duplicates()
df = df.groupby('Year').mean()
df.columns = df.columns.str.replace(r'_\d+$', '', regex=True)
df['Year'] = df.index
df = df.reset_index(drop = True)
cols = ['Year'] + [c for c in df.columns if c != 'Year']
df = df[cols]
df['Year'] = pd.to_datetime(df['Year'], format = '%Y').dt.year



# Streamlit
keuze = st.sidebar.radio('Choose a page', ['Data','Visualisations 1990-2000','Visualistion 1900-2018' ])



if keuze == 'Data':

    st.header('Consumer prices and income over the years')

    st.write(
     "We are working with 2 datasets from Statistics Netherlands (CBS).\n"
    "These datasets contain information on product prices between 1980 and 2018, "
    "an on different types of income between 1990 and 2000.\n"
    "For the income variables, the averages have been chosen."
    )

    st.write(
    "Below you can see our dataset. In the dropdown menu, you can select which variables are displayed.\n"
    "Under the table, the units of the variables are shown."
    )
    df = df.set_index('Year').astype(str)
    kolom = df.columns.unique().tolist()
    select = st.multiselect('Choose the variables:', kolom, default = kolom[0:10] )
    df = df.astype(str).replace('.', ',').astype(float).round(2)
    df.index = df.index.astype(str)
    dfshow = df[select]
    st.dataframe(dfshow)

    st.write('The income variables **GrossIncome**, **SpendableIncome**, and **StandardisedIncome** are measured in thousands.')

    st.markdown(
        """
        The consumer price variables are measured in different units:  

        - **Sugar, StewingSteak, Rice, Potatoes, PorkSteak, and Cheese**: euros per kilogram  
        - **Beer and Milk**: euros per liter  
        - **Bread**: euros per loaf  
        - **Butter**: euros per 250 grams  
        - **Coffee**:  
            - Before 2000: euros per 500 grams  
             After 2000: euros per kilogram  
        - **Eggs**:  
            - Before 2000: euros per egg  
            - After 2000: euros per 10 eggs  
        - **Margarine**:  
            - Before 2000: euros per 500 grams  
            - After 2000: euros per 250 grams  
        - **Tea**:  
            - Before 2000: euros per 80 grams  
            - After 2000: euros per 50 grams  
        """
    )

    
elif keuze == 'Visualisations 1990-2000':
    st.header('Visualisations of income and consumerprices between 1990 and 2000')
    st.write('First there is a lineplot of the growth of income through the years.  \n' \
    'In the checkboxes are options to show the different kinds of income.'
    )
    dfi = df.set_index('Year')
    opties = ['GrossIncome', 'SpendableIncome', 'StandardisedIncome']
    gekozen = []
    for i,optie in enumerate(opties):
        if st.checkbox(optie,value =(i==0), key=optie):
            gekozen.append(optie)
    dfg = dfi[gekozen]

    graf = px.line(dfg, x = dfg.index, y = gekozen, markers = True  )
    graf.update_layout(title = 'Consumerprices of the selected year')
    st.plotly_chart(graf)

    st.write('Then there is a barplot of the consumer prices.  \n' \
    'In the slider you can choose the year which you want to see the prices of.')
    jaar = st.slider("Choose the year", 1990, 2000)
    df1 = df[df['Year']== jaar]
    df1 = df1.melt(id_vars=['Year'],
    value_vars = [c for c in df1.columns if c not in ['GrossIncome', 'SpendableIncome', 'StandardisedIncome']], 
    var_name='product', 
    value_name='waarde').sort_values('waarde',ascending = False)
    fig = px.bar(df1, x= 'product', y = 'waarde', color = 'product')
    fig.update_layout(title = 'Consumerprices of the selected year')
    st.plotly_chart(fig)

    st.write('The last graph is a lineplot of the annual growth rate based on percentages.  \n' \
    'In the top dropdown menu you can choose the products and in th bottom dropdown menu you can choose the kinds of income. ')
    df_per = df.pct_change( )* 100
    selected_colc = st.multiselect('Kies consument:',
                                  options = [c for c in df.columns if c not in ['Year','GrossIncome', 'SpendableIncome', 'StandardisedIncome']] ,
                                  default = ['Cheese'])
    selected_coli = st.multiselect('Choose types of income',
                                   options = ['GrossIncome', 'SpendableIncome', 'StandardisedIncome'],
                                   default = 'GrossIncome')
    selected_col = selected_colc + selected_coli
    dfg = df_per[selected_col]
    cor = px.line(dfg, x = df['Year'], y = selected_col)
    cor.update_layout(title = 'Annual growth rate over the years', xaxis_title = 'Year', yaxis_title = 'Percentage')
    st.plotly_chart(cor)


    
elif keuze == 'Visualistion 1900-2018':
    st.header('Growth consumerprices through the years')
    st.write('In the checkboxes you can choose which products you want to see the price growth of.')

    infla = df1.bfill()
    infla = infla[infla['Year'] >= 1900]
    infla = infla.drop(['ID', 'Periods'], axis = 1)
    inflatie = ['Year'] + [c for c in infla.columns if c != 'Year']
    inflatie = infla[inflatie]
    inflatie.columns = inflatie.columns.str.replace(r'_\d+$', '', regex=True)
    col1, col2 = st.columns(2)
    with col1:
        opties = [c for c in inflatie.columns if c != 'Year']
        gekozen = []
        for i,optie in enumerate(opties):
            if st.checkbox(optie,value =(i==0), key=optie):
                gekozen.append(optie)
    inflatieg = inflatie[gekozen]
    with col2:
        lijn =  px.line(inflatie, x = 'Year',y = gekozen)
        lijn.update_layout(title = 'Consumerprices over the years')
        st.plotly_chart(lijn)



