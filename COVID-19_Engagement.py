import streamlit as st
import pandas as pd
import altair as alt

# --------------------------
# Load data
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("covid_articles_matched_qids.csv")
    return df

df = load_data()
df["date"] = pd.to_datetime(df["date"])

st.title("Shifts in COVID-19 Global Public Interest")
st.write("How has public engagement in COVID-19 shifted during the post-pandemic period, as reflected in Wikipedia pageviews from 2023–2024?")

# --------------------------
# 1. Total Pageviews Over Time
# --------------------------
st.subheader("Total COVID-19 Pageviews Over Time")

# --------------------------
# Date range slider
# --------------------------
min_date = df["date"].min().to_pydatetime()
max_date = df["date"].max().to_pydatetime()

start_date, end_date = st.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

df_filtered = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

# Total daily pageviews
daily = df_filtered.groupby("date")["pageviews"].sum().reset_index()

line_chart = alt.Chart(daily).mark_line().encode(
    x=alt.X("date:T", title="Date", axis=alt.Axis(format="%b %Y")),
    y=alt.Y("pageviews:Q", title="Total Pageviews"),
    tooltip=["date:T", "pageviews:Q"]
).properties(height=350)

st.altair_chart(line_chart, use_container_width=True)

# --------------------------
# 2. Year Comparison
# --------------------------
st.subheader("2023 vs. 2024 — Total Pageviews")

df["year"] = df["date"].dt.year

yearly = df.groupby("year")["pageviews"].sum().reset_index()

bar_year = alt.Chart(yearly).mark_bar().encode(
    x=alt.X("year:N", title="Year"),
    y=alt.Y("pageviews:Q", title="Total Pageviews"),
    color=alt.Color("year:N", legend=None),
)

st.altair_chart(bar_year, use_container_width=True)

# --------------------------
# 3. Top Articles by Total Views
# --------------------------
st.subheader("Top 10 Most Popular COVID-19 Articles (2023–2024)")

top_articles = (
    df.groupby("article")["pageviews"]
    .sum()
    .reset_index()
    .sort_values("pageviews", ascending=False)
    .head(10)
)

bar = alt.Chart(top_articles).mark_bar().encode(
    x=alt.X("pageviews:Q", title="Total Pageviews"),
    y=alt.Y("article:N", sort='-x', title="Article"),
).properties(height=500)

st.altair_chart(bar, use_container_width=True)

# -------------------------------------------------------
# 4. Monthly Pageviews for Top 10 Articles 
# -------------------------------------------------------
st.subheader("Monthly Pageviews for Top 10 COVID-19 Articles by Year")

# select year from selectbox
year_selected = st.selectbox(
    "Select Year",
    options=[2023, 2024],
    index=0
)

st.write('The top COVID-19 article in 2023, "Coronavirus", has an extreme number of pageviews in February 2023 ' \
'that skews the data visualization. It can be excluded to better visualize trends for other articles.')
exclude_coronavirus = st.checkbox(
    'Exclude "Coronavirus" article', value=False
)

# Filter selected year
df_year = df[df["date"].dt.year == year_selected]
if exclude_coronavirus:
    df_year = df_year[df_year["article"] != "Coronavirus"]

# find top 10 articles for that year
top10_articles = (
    df_year.groupby("article")["pageviews"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .index.tolist()
)

df_top10 = df_year[df_year["article"].isin(top10_articles)]

df_top10["month"] = df_top10["date"].dt.to_period("M").dt.to_timestamp()

# sum monthly pageviews
monthly = (
    df_top10.groupby(["month", "article"])["pageviews"]
    .sum()
    .reset_index()
)

monthly_chart = (
    alt.Chart(monthly)
    .mark_line()
    .encode(
        x=alt.X("month:T", title="Month"),
        y=alt.Y("pageviews:Q", title="Total Pageviews"),
        color="article:N",
        tooltip=[
            alt.Tooltip("month:T", title="Month"),
            alt.Tooltip("article:N", title="Article"),
            alt.Tooltip("pageviews:Q", title="Pageviews")
        ]
    )
    .properties(height=400)
)

st.altair_chart(monthly_chart, use_container_width=True)

