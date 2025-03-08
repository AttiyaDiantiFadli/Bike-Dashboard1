import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px

sns.set(style='dark')

# Load Data
file_path = "dashboard/all_data.csv"
bike_df = pd.read_csv(file_path)

# Ubah semua nama kolom menjadi lowercase
bike_df.columns = bike_df.columns.str.lower()

# Pastikan kolom yang benar digunakan
if "cnt_x" in bike_df.columns and "cnt_y" in bike_df.columns:
    cnt_column = "cnt_x"  # Pilih salah satu
elif "cnt_x" in bike_df.columns:
    cnt_column = "cnt_x"
elif "cnt_y" in bike_df.columns:
    cnt_column = "cnt_y"
else:
    st.error("Kolom 'cnt' tidak ditemukan dalam dataset.")
    st.stop()

# Ubah angka musim menjadi label musim
season_labels = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
bike_df["season"] = bike_df["season"].map(season_labels)

# Ubah angka cuaca menjadi label cuaca
weather_labels = {1: "Cerah", 2: "Mendung", 3: "Hujan", 4: "Salju"}
bike_df["weathersit"] = bike_df["weathersit"].map(weather_labels)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9033/9033633.png")
    st.subheader("📍 Kontak Kami:")
    st.write("📌 **Alamat:** Musi Rawas Utara")
    st.write("📞 **Telepon:** +62 857-4092-2279")
    st.write("✉️ **Email:** attiyadiantifadli@gmail.com")

    # Filter Interaktif
    st.subheader("🛠 Filter Data")
    
    # Filter Rentang Tanggal
    start_date, end_date = st.date_input(
        "Pilih Rentang Tanggal",
        [bike_df["dteday"].min(), bike_df["dteday"].max()],
        bike_df["dteday"].min(),
        bike_df["dteday"].max(),
    )

    # Filter Musim
    selected_seasons = st.multiselect("Pilih Musim", bike_df["season"].unique(), bike_df["season"].unique())

    # Filter Cuaca
    selected_weather = st.multiselect("Pilih Cuaca", bike_df["weathersit"].unique(), bike_df["weathersit"].unique())

    # Filter Jam dalam Sehari
    min_hour, max_hour = st.slider(
        "Pilih Rentang Jam", 
        min_value=0, 
        max_value=23, 
        value=(0, 23)
    )

# Terapkan Filter
filtered_df = bike_df[
    (bike_df["dteday"] >= pd.to_datetime(start_date)) &
    (bike_df["dteday"] <= pd.to_datetime(end_date)) &
    (bike_df["season"].isin(selected_seasons)) &
    (bike_df["weathersit"].isin(selected_weather)) &
    (bike_df["hr"] >= min_hour) &
    (bike_df["hr"] <= max_hour)
]

# Dashboard Header
st.header('Bike Rental Dashboard 🚴‍♂️')
st.write("Selamat datang di layanan penyewaan sepeda terbaik. Kami menawarkan berbagai jenis sepeda untuk berbagai kebutuhan Anda, mulai dari sepeda standar untuk perjalanan santai hingga sepeda listrik dan sepeda gunung untuk petualangan yang lebih menantang.")

# Harga Sewa
st.subheader("💰 Harga Sewa Sepeda")
st.write("🚲 **Sepeda Standar**: Rp. 15.000/jam")
st.write("⚡ **Sepeda Listrik**: Rp. 25.000/jam")
st.write("🏔️ **Sepeda Gunung**: Rp. 40.000/jam")

# Statistik Penyewaan
st.subheader('📊 Statistik Penyewaan')
col1, col2 = st.columns(2)
with col1:
    total_orders = filtered_df[cnt_column].sum()
    st.metric("Total Penyewaan", value=total_orders)
with col2:
    total_revenue = format_currency(total_orders * 15000, "IDR", locale='id_ID')  # Harga rata-rata Rp. 15.000
    st.metric("Total Revenue", value=total_revenue)

# Penyewaan Berdasarkan Musim
st.subheader("🌦️ Penyewaan Berdasarkan Musim")
byseason_df = filtered_df.groupby("season").agg({cnt_column: "sum"}).reset_index()

fig = px.bar(byseason_df, 
             x="season", 
             y=cnt_column, 
             title="Total Penyewaan per Musim", 
             labels={"season": "Musim", cnt_column: "Jumlah Penyewaan"},
             color="season",  
             color_discrete_sequence=px.colors.qualitative.Set1)
st.plotly_chart(fig)

# Penyewaan Sepeda: Hari Kerja vs Akhir Pekan
st.subheader("📆 Penyewaan: Hari Kerja vs Akhir Pekan")
workday_df = filtered_df.groupby("workingday").agg({cnt_column: "sum"}).reset_index()
workday_df["workingday"] = workday_df["workingday"].map({0: "Akhir Pekan", 1: "Hari Kerja"})
fig = px.pie(workday_df, names="workingday", values=cnt_column, title="Perbandingan Penyewaan")
st.plotly_chart(fig)

# Penyewaan Sepeda Berdasarkan Jam dalam Sehari dengan Filter Interaktif
st.subheader("⏰ Penyewaan Berdasarkan Jam")
hourly_df = filtered_df.groupby("hr").agg({cnt_column: "sum"}).reset_index()

fig = px.bar(hourly_df, 
             x="hr", 
             y=cnt_column, 
             title=f"Tren Penyewaan Sepeda Berdasarkan Jam {min_hour}:00 - {max_hour}:00", 
             labels={"hr": "Jam (24 Jam Format)", cnt_column: "Total Penyewaan"},
             color="hr",
             color_continuous_scale="Blues")

st.plotly_chart(fig)

st.caption('Copyright © Attiya Dianti Fadli 2025')
