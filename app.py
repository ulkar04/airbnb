#NYC Airbnb Dashboard

# This project is a Streamlit dashboard backed by a SQLite database.
# It supports filtering, KPI cards, charts, and a map visualization.

# Run:  streamlit run app.py


import sqlite3
import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

pio.templates.default = "plotly_white"
st.set_page_config(page_title="NYC Airbnb Market Explorer", layout="wide")

DB_PATH = "airbnb.db"
TABLE_NAME = "airbnb"


def run_query(query, params=None):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=params or [])
    conn.close()
    return df


st.markdown("""
<style>
/* ---------- Base page ---------- */
.stApp {
    background-color: #f5f1ea;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1300px;
}

/* Default text */
html, body, p, label {
    color: black !important;
}

/* ---------- Header ---------- */
.hero-box {
    background: linear-gradient(135deg, #114b43, #1c6b5c);
    padding: 28px;
    border-radius: 20px;
    color: white !important;
    margin-bottom: 22px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}

.hero-title {
    font-size: 34px;
    font-weight: 800;
    margin: 0;
    color: white !important;
}

.hero-sub {
    font-size: 14px;
    margin-top: 6px;
    color: rgba(255,255,255,0.92) !important;
}

/* ---------- Cards ---------- */
.card {
    background: white;
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
    margin-bottom: 16px;
    color: black !important;
}

.section-title {
    color: black !important;
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 10px;
}

/* ---------- Metrics ---------- */
div[data-testid="stMetric"] {
    background: white;
    border-radius: 18px;
    padding: 18px 18px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
    border: none;
}

div[data-testid="stMetricLabel"] {
    color: black !important;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: black !important;
    font-weight: 800;
}

div[data-testid="stMetricDelta"] {
    color: black !important;
}

/* ---------- Dataframe ---------- */
div[data-testid="stDataFrame"] {
    background: white;
    border-radius: 16px;
    padding: 6px;
}

/* ---------- Closed multiselect input ---------- */
div[data-baseweb="select"] > div {
    background-color: white !important;
    color: black !important;
    border-radius: 12px !important;
    border: 1px solid #d1d5db !important;
}

div[data-baseweb="select"] input {
    color: black !important;
}

div[data-baseweb="select"] svg {
    fill: black !important;
}

div[data-baseweb="tag"] {
    background-color: #ff5757 !important;
    color: white !important;
    border-radius: 8px !important;
}

div[data-baseweb="tag"] span {
    color: white !important;
}

/* ---------- Dropdown popup ---------- */
div[role="listbox"] {
    background-color: #0f1720 !important;
    border: 1px solid #2b3540 !important;
}

div[role="option"] {
    background-color: #0f1720 !important;
    color: white !important;
}

div[role="option"] * {
    color: white !important;
}

div[role="option"]:hover {
    background-color: #25303b !important;
}

div[aria-selected="true"] {
    background-color: #334155 !important;
    color: white !important;
}

div[aria-selected="true"] * {
    color: white !important;
}

/* ---------- Slider ---------- */
div[data-baseweb="slider"] div[role="slider"] {
    background: white !important;
    border: 3px solid #8bd3ef !important;
    box-shadow: none !important;
}

div[data-baseweb="slider"] span {
    background: #8bd3ef !important;
}

div[data-baseweb="slider"] > div > div {
    background: #dddddd !important;
}

/* ---------- Plotly ---------- */
.js-plotly-plot, .plotly, .plot-container {
    border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-box">
    <div class="hero-title">NYC Airbnb Market Explorer</div>
    <div class="hero-sub">Dashboard backed by SQLite. Filters drive SQL queries in real time.</div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# LOAD FILTER OPTIONS FROM THE DATABASE
# We fetch the distinct borough names and room types directly from the DB
# so the filter dropdowns always reflect whatever data is actually in there —
# no hardcoding needed, and it stays in sync if the data changes.
# ──────────────────────────────────────────────
boroughs_df = run_query(f"""
    SELECT DISTINCT neighbourhood_group
    FROM {TABLE_NAME}
    WHERE neighbourhood_group IS NOT NULL
    ORDER BY neighbourhood_group
""")

room_types_df = run_query(f"""
    SELECT DISTINCT room_type
    FROM {TABLE_NAME}
    WHERE room_type IS NOT NULL
    ORDER BY room_type
""")



f1, f2, f3, f4 = st.columns([1.2, 1.2, 1.2, 1.0])

with f1:
    st.markdown('<div class="card"><div class="section-title">Boroughs</div>', unsafe_allow_html=True)
    boroughs = st.multiselect(
        "Boroughs",
        boroughs_df["neighbourhood_group"].tolist(),
        default=boroughs_df["neighbourhood_group"].tolist(),
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with f2:
    st.markdown('<div class="card"><div class="section-title">Room Types</div>', unsafe_allow_html=True)
    room_types = st.multiselect(
        "Room Types",
        room_types_df["room_type"].tolist(),
        default=room_types_df["room_type"].tolist(),
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with f3:
    st.markdown('<div class="card"><div class="section-title">Price Range</div>', unsafe_allow_html=True)
    price_range = st.slider(
        "Price Range",
        min_value=0,
        max_value=340,    # max price found in the dataset after removing outliers
        value=(50, 200),
        step=10,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with f4:
    st.markdown('<div class="card"><div class="section-title">Minimum Reviews</div>', unsafe_allow_html=True)
    min_reviews = st.slider(     # Lets users filter for listings with social proof — default 0 means show everything
        "Minimum Reviews",
        min_value=0,
        max_value=629,    # max reviews found in the dataset
        value=0,
        step=5,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)



# ──────────────────────────────────────────────
# BUILD THE SQL WHERE CLAUSE DYNAMICALLY
# Instead of fetching all data and filtering in Python, we push the filtering
# down to SQLite.We use parameterized queries (?) to safely inject user-selected values.
# ──────────────────────────────────────────────    
conditions = []
params = []

if boroughs:
    placeholders = ",".join(["?"] * len(boroughs))
    conditions.append(f"neighbourhood_group IN ({placeholders})")
    params.extend(boroughs)

if room_types:
    placeholders = ",".join(["?"] * len(room_types))
    conditions.append(f"room_type IN ({placeholders})")
    params.extend(room_types)

# price_range is a tuple (min, max) from the slider so we can directly use it for the BETWEEN clause
conditions.append("price BETWEEN ? AND ?")
params.extend(price_range)

# min_reviews is a single integer from the slider so we use a >= condition  
conditions.append("number_of_reviews >= ?")
params.append(min_reviews)

# assemble all conditions into a single WHERE clause string
where_clause = "WHERE " + " AND ".join(conditions)



# ──────────────────────────────────────────────
# KPI METRICS
# One SQL query aggregates the four headline numbers.
# occupancy_proxy_pct is derived from availability_365:
# fewer available days -> more likely it's being booked -> higher "occupancy"
# ──────────────────────────────────────────────
kpi_query = f"""
SELECT
    COUNT(*) AS total_listings,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(AVG(number_of_reviews), 1) AS avg_reviews,
    ROUND(AVG(availability_365) * 100.0 / 365, 1) AS occupancy_proxy_pct
FROM {TABLE_NAME}
{where_clause}
"""
kpi_df = run_query(kpi_query, params)
kpi = kpi_df.iloc[0]

# Render the four KPI tiles side by side
# pd.notna() guards against NaN values when the filter returns zero results
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Listings", int(kpi["total_listings"]) if pd.notna(kpi["total_listings"]) else 0)
k2.metric("Average Price", f"${int(kpi['avg_price'])}" if pd.notna(kpi["avg_price"]) else "$0")
k3.metric("Average Reviews", float(kpi["avg_reviews"]) if pd.notna(kpi["avg_reviews"]) else 0)
k4.metric("Occupancy Proxy", f"{kpi['occupancy_proxy_pct']}%" if pd.notna(kpi["occupancy_proxy_pct"]) else "0%")

st.write("")


# ──────────────────────────────────────────────
# CHART DATA QUERIES
# Each chart gets its own focused query — only pulling the columns it needs.
# All queries reuse the same where_clause and params built from the filters above.
# ──────────────────────────────────────────────


# Borough breakdown: listing count + avg price per borough (used in the bar chart)
borough_query = f"""
SELECT
    neighbourhood_group,
    COUNT(*) AS listings,
    ROUND(AVG(price), 0) AS avg_price
FROM {TABLE_NAME}
{where_clause}
GROUP BY neighbourhood_group
ORDER BY listings DESC
"""
borough_df = run_query(borough_query, params)

# Room type breakdown: just counts per room type (used in the donut chart)
room_query = f"""
SELECT
    room_type,
    COUNT(*) AS listings
FROM {TABLE_NAME}
{where_clause}
GROUP BY room_type
ORDER BY listings DESC
"""
room_df = run_query(room_query, params)

c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fig_bar = px.bar(
        borough_df,
        x="neighbourhood_group",
        y="listings",
        color="avg_price",
        title="Listings by Borough",
        text_auto=True,
        color_continuous_scale="Tealgrn"
    )
    fig_bar.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="black"),
    title_font=dict(color="black"),

    xaxis=dict(
        title_font=dict(color="black"),
        tickfont=dict(color="black")
    ),
    yaxis=dict(
        title_font=dict(color="black"),
        tickfont=dict(color="black")
    ),

    coloraxis_colorbar=dict(
        title_font=dict(color="black"),   
        tickfont=dict(color="black")      
    ),

    margin=dict(l=10, r=10, t=50, b=10)
)
    fig_bar.update_traces(textfont=dict(color="black"))
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fig_pie = px.pie(
        room_df,
        names="room_type",
        values="listings",
        hole=0.55,
        title="Room Type Mix",
        color_discrete_sequence=["#6272f3", "#f26b3a", "#44b8b1"]
    )
    fig_pie.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="black"),
        title_font=dict(color="black"),
        legend=dict(font=dict(color="black")),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    fig_pie.update_traces(textfont=dict(color="black"))
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# INTERACTIVE MAP
# We limit to 1000 rows for map performance — plotting tens of thousands of
# scatter points in the browser would be sluggish and hard to read anyway.
# Each dot is colored by room type and sized by price.
# ──────────────────────────────────────────────
map_query = f"""
SELECT
    neighbourhood_group,
    neighbourhood,
    room_type,
    price,
    latitude,
    longitude
FROM {TABLE_NAME}
{where_clause}
AND latitude IS NOT NULL
AND longitude IS NOT NULL
LIMIT 1000
"""
map_df = run_query(map_query, params)

st.markdown('<div class="card">', unsafe_allow_html=True)
fig_map = px.scatter_mapbox(
    map_df,
    lat="latitude",
    lon="longitude",
    color="room_type",
    size="price",
    hover_name="neighbourhood",
    hover_data=["neighbourhood_group", "price"],
    zoom=9.7,
    title="Interactive Listing Map",
    height=500,
    color_discrete_sequence=["#6272f3", "#f26b3a", "#44b8b1"]
)
fig_map.update_layout(
    mapbox_style="open-street-map",
    margin=dict(l=10, r=10, t=50, b=10),
    paper_bgcolor="white",
    font=dict(color="black"),
    title_font=dict(color="black"),
    legend=dict(font=dict(color="black"))
)
st.plotly_chart(fig_map, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)



# ──────────────────────────────────────────────
# DATA TABLE
# Shows the top 20 most expensive listings under the current filters —
# useful for exploring individual records after spotting something interesting
# in the charts above.
# ──────────────────────────────────────────────
table_query = f"""
SELECT
    neighbourhood_group,
    neighbourhood,
    room_type,
    price,
    minimum_nights,
    number_of_reviews,
    availability_365
FROM {TABLE_NAME}
{where_clause}
ORDER BY price DESC
LIMIT 20
"""
table_df = run_query(table_query, params)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Top Listings Under Current Filters</div>', unsafe_allow_html=True)
st.dataframe(table_df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)