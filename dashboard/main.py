import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import folium
import datetime

sns.set(style="dark")

all_df = pd.read_csv("./main_data.csv")

def create_daily_report_df(df, minDate, maxDate):
    df['Tanggal'] = pd.to_datetime(df[['year', 'month', 'day']], format='%Y-%m-%d')

    # Konversi minDate dan maxDate ke datetime64[ns]
    minDate = pd.to_datetime(minDate)
    maxDate = pd.to_datetime(maxDate)

    # Filter data berdasarkan rentang tanggal
    df_filtered = df[(df['Tanggal'] >= minDate) & (df['Tanggal'] <= maxDate)]

    # Menyimpan kolom yang akan digunakan dalam laporan harian
    columns_to_keep = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'wd', 'WSPM',
                       'station']

    # Membuat DataFrame baru dengan data harian
    daily_report = df_filtered.groupby(df['Tanggal'])[columns_to_keep].agg(
        {
         'PM2.5': 'mean',
         'PM10': 'mean',
         'SO2': 'mean',
         'NO2': 'mean',
         'CO': 'mean',
         'O3': 'mean',
         'TEMP': 'mean',
         'PRES': 'mean',
         'DEWP': 'mean',
         'RAIN': 'sum',
         'WSPM': 'mean',
         'station': 'first'})

    # Menampilkan laporan harian
    return daily_report

def draw_daily_temperature_chart(data):
    st.title('Grafik Suhu Harian Rata-rata')

    # Menggambar grafik suhu harian
    fig, ax = plt.subplots()
    ax.plot(data.index, data.values, marker='o', linestyle='-')
    ax.set_xlabel('Tanggal')
    ax.set_ylabel('Suhu (°C)')
    ax.set_title('Grafik Suhu Harian Rata-rata')
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)


st.title("Dashboard Air Quality")

# side bar
min_date = datetime.date(all_df["year"].min(), all_df["month"].min(), all_df["day"].min())
max_date = datetime.date(all_df["year"].max(), all_df["month"].max(), all_df["day"].max())

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://www.southportland.org/files/7515/6053/6591/air_2.png")

    # Mengambil start_date & end_date dari date_input
    start_date = ""
    end_date = ""
    try:
        start_date, end_date = st.date_input(
            label="Select Date",
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date],
        )
    except ValueError:
        st.error(
            "Invalid date input. Make sure you choose a suitable date."
        )

    try:
        main_df = all_df[
            (all_df["Tanggal"] >= str(start_date))
            & (all_df["Tanggal"] <= str(end_date))
        ]
    except ValueError:
        st.error("ups sorry!")


    # Daftar pilihan yang akan ditampilkan dalam dropdown
    options = all_df.groupby(by="station").agg({
        "station": "first"
    })

    # Menampilkan komponen selectbox
    selected_option = st.selectbox('Select Station:', options)

    # Menampilkan hasil pilihan
    st.write('You have chosen:', selected_option)

# all_df

daily_report_df = create_daily_report_df(all_df, min_date, max_date)
filtered_df = all_df[
    (all_df['Tanggal'] >= pd.to_datetime(start_date)) & (all_df['Tanggal'] <= pd.to_datetime(end_date)) & (
                all_df['station'] == selected_option)]



# Data stasiun dan koordinatnya (contoh data)
station_data = pd.DataFrame({
    'station': ['Aotizhongxin', 'Changping', 'Dingling', 'Dongsi', 'Guanyuan', 'Gucheng', 'Huairou', 'Nongzhanguan', 'Shunyi', 'Tiantan', 'Wanliu', 'Wanshouxigong'],
    'latitude': [39.9683, 40.2262, 40.2910, 39.9302, 39.9296, 39.9141, 40.3572, 39.9371, 40.1250, 39.8785, 39.9382, 39.8782],
    'longitude': [116.4081, 116.2156, 116.2201, 116.4163, 116.2951, 116.1868, 116.6262, 116.4640, 116.6468, 116.4132, 116.2927, 116.3279]
})

# Judul aplikasi
st.title('Peta Stasiun')

# Menampilkan peta dengan Folium
m = folium.Map(location=[39.938417, 116.2353522], zoom_start=8)  # Pusat peta dan level zoom awal

# Menambahkan marker untuk setiap stasiun
for index, row in station_data.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['station']
    ).add_to(m)

# Menampilkan peta dalam aplikasi Streamlit
st.components.v1.html(m._repr_html_(), width=700, height=500)


# tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["PM2.5 and PM10", "Station", "TEMP", "RAIN", "Time Series Plot suhu harian"])
with tab1:
    st.header("Report")
    # st.write(filtered_df)
    st.bar_chart(filtered_df[['PM2.5', 'PM10']])

    st.header("Average PM2.5 and PM10")

    # Menampilkan data yang sudah difilter
    # st.write(filtered_df)

    # Menghitung rata-rata dari kolom 'PM2.5' dan 'PM10'
    average_pm25 = filtered_df['PM2.5'].mean()
    average_pm10 = filtered_df['PM10'].mean()

    # Menampilkan rata-rata dalam diagram batang
    fig, ax = plt.subplots()
    ax.bar(['PM2.5', 'PM10'], [average_pm25, average_pm10])
    ax.set_ylabel('Rata-rata')
    ax.set_title('Rata-rata PM2.5 dan PM10')
    st.pyplot(fig)

    st.title("Perbandingan Rata-rata PM2.5 dan PM10 antara Stasiun")

    # Membuat dataframe dengan rata-rata PM2.5 dan PM10 per stasiun
    average_pm25_pm10 = filtered_df.groupby("station")[["PM2.5", "PM10"]].mean()

    # Membuat grafik bar
    st.bar_chart(average_pm25_pm10)

    # # Menampilkan data yang dipilih
    # st.write("Data yang dipilih:")
    # st.write(filtered_df)

with tab2:
    st.header("Rata-rata nilai Station")
    # Membuat DataFrame dengan rata-rata nilai variabel-variabel yang dipilih berdasarkan stasiun
    selected_columns = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN']
    average_values = filtered_df[selected_columns].mean().reset_index()
    average_values.columns = ['Variable', 'Average']

    # Membuat diagram batang interaktif dengan Plotly Express
    fig = px.bar(average_values, x='Variable', y='Average', title=f"Average Values by Station: {selected_option}")
    st.plotly_chart(fig)

with tab3:
    st.header("Temperatur")
    # Menghitung rata-rata dari kolom 'PM2.5' dan 'PM10'
    average_temp = filtered_df['TEMP'].mean()

    # Menampilkan rata-rata dalam diagram batang
    fig, ax = plt.subplots()
    ax.bar(['Temperatur'], [average_temp])
    ax.set_ylabel('Rata-rata')
    ax.set_title('Rata-rata Temperatur')
    st.pyplot(fig)

    # Menampilkan grafik suhu harian dalam aplikasi Streamlit
    # draw_daily_temperature_chart(filtered_df)

with tab4:
    st.header("MAX")
    max = filtered_df['RAIN'].max()
    # Menampilkan rata-rata dalam diagram batang
    fig, ax = plt.subplots()
    ax.bar(['RAIN'], [max])
    ax.set_ylabel('Rata-rata')
    ax.set_title('Max rain')
    st.pyplot(fig)

    st.header("MIN")
    min = filtered_df['RAIN'].min()
    # Menampilkan rata-rata dalam diagram batang
    fig, ax = plt.subplots()
    ax.bar(['RAIN'], [min])
    ax.set_ylabel('Rata-rata')
    ax.set_title('Min rain')
    st.pyplot(fig)

    st.header("AVERAGE")
    average_rain = filtered_df['RAIN'].mean()
    # Menampilkan rata-rata dalam diagram batang
    fig, ax = plt.subplots()
    ax.bar(['RAIN'], [average_rain])
    ax.set_ylabel('Rata-rata')
    ax.set_title('Rata-rata rain')
    st.pyplot(fig)

with tab5:
    # Menggambarkan diagram Time Series Plot suhu harian
    st.title("Diagram Time Series Suhu Harian")
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_df["Tanggal"], filtered_df["TEMP"], marker='o', linestyle='-', color='b')
    plt.xlabel('Tanggal')
    plt.ylabel('Suhu (°C)')
    plt.title('Grafik Suhu Harian Rata-rata')
    plt.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(plt)