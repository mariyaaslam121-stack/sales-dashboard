import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("Sales Data Analysis Dashboard")
st.write("Electronics Store Sales Data Analysis - 2019")


@st.cache_data
def load_data():
    data = pd.read_csv("Sales Data.csv")
    total_rows = len(data)

    data = data.drop(columns=["Unnamed: 0"], errors="ignore")

    data["Order Date"] = pd.to_datetime(data["Order Date"], errors="coerce")
    data["Quantity Ordered"] = pd.to_numeric(data["Quantity Ordered"], errors="coerce")
    data["Price Each"] = pd.to_numeric(data["Price Each"], errors="coerce")

    data = data.dropna(subset=[
        "Order ID", "Product", "Quantity Ordered",
        "Price Each", "Order Date", "Purchase Address"
    ])

    rows_after_missing = len(data)

    data = data.drop_duplicates()
    rows_after_duplicates = len(data)

    data = data[data["Order Date"].dt.year == 2019].copy()
    rows_after_year = len(data)

    data["Sales"] = data["Quantity Ordered"] * data["Price Each"]
    data["Month"] = data["Order Date"].dt.month_name()
    data["Hour"] = data["Order Date"].dt.hour
    data["Day"] = data["Order Date"].dt.day_name()

    address = data["Purchase Address"].str.split(",", expand=True)
    data["City"] = address[1].str.strip()
    data["State"] = address[2].str.strip().str[:2]
    data["City"] = data["City"] + " (" + data["State"] + ")"

    report = {
        "Original Rows": total_rows,
        "Rows After Missing Values": rows_after_missing,
        "Rows After Duplicates": rows_after_duplicates,
        "Final Rows": rows_after_year,
        "Missing Rows Removed": total_rows - rows_after_missing,
        "Duplicates Removed": rows_after_missing - rows_after_duplicates,
        "Rows Outside 2019": rows_after_duplicates - rows_after_year
    }

    return data, report


try:
    df, report = load_data()
except FileNotFoundError:
    st.error("Sales Data.csv file not found. Keep it in the same folder as app.py.")
    st.stop()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()


st.sidebar.header("Filters")

month_list = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

months = ["All"] + [m for m in month_list if m in df["Month"].unique()]
cities = ["All"] + sorted(df["City"].unique())
products = ["All"] + sorted(df["Product"].unique())

month = st.sidebar.selectbox("Select Month", months)
city = st.sidebar.selectbox("Select City", cities)
product = st.sidebar.selectbox("Select Product", products)

data = df.copy()

if month != "All":
    data = data[data["Month"] == month]

if city != "All":
    data = data[data["City"] == city]

if product != "All":
    data = data[data["Product"] == product]

if data.empty:
    st.warning("No data found. Please change the filters.")
    st.stop()


total_sales = data["Sales"].sum()
total_orders = data["Order ID"].nunique()
total_items = data["Quantity Ordered"].sum()

order_total = data.groupby("Order ID")["Sales"].sum()
average_order = order_total.mean()

tab1, tab2 = st.tabs(["Dashboard", "Data Cleaning"])


with tab1:

    st.header("Sales Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Sales", f"${total_sales:,.2f}")
    c2.metric("Number of Orders", total_orders)
    c3.metric("Items Sold", total_items)
    c4.metric("Average Order Value", f"${average_order:,.2f}")

    st.divider()

    st.header("1. Univariate Analysis")

    st.subheader("1. Quantity Ordered")

    fig = px.histogram(data, x="Quantity Ordered",
                       title="Distribution of Quantity Ordered")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Observation: This graph shows the frequency of different order quantities.")

    st.subheader("2. Price Each")

    fig = px.histogram(data, x="Price Each",
                       title="Distribution of Product Prices")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Observation: This graph shows the price distribution of products.")

    st.subheader("3. Sales")

    fig = px.histogram(data, x="Sales",
                       title="Distribution of Sales")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Observation: This graph shows the distribution of sales amounts.")

    st.subheader("4. Product")

    product_count = data["Product"].value_counts().reset_index()
    product_count.columns = ["Product", "Count"]

    fig = px.bar(product_count, x="Product", y="Count",
                 title="Number of Records by Product")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Observation: This graph compares the number of records for each product.")

    st.subheader("5. City")

    city_count = data["City"].value_counts().reset_index()
    city_count.columns = ["City", "Count"]

    fig = px.bar(city_count, x="City", y="Count",
                 title="Number of Records by City")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Observation: This graph shows the number of sales records in each city.")

    st.subheader("6. Month")

    month_count = data["Month"].value_counts()
    month_count = month_count.reindex(month_list, fill_value=0)
    month_count = month_count.reset_index()
    month_count.columns = ["Month", "Count"]

    fig = px.bar(month_count, x="Month", y="Count",
                 title="Number of Records by Month")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Observation: This graph shows the monthly distribution of sales records.")

    st.subheader("7. Hour")

    hour_count = data["Hour"].value_counts().sort_index().reset_index()
    hour_count.columns = ["Hour", "Count"]

    fig = px.bar(hour_count, x="Hour", y="Count",
                 title="Number of Records by Hour")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Observation: This graph shows when orders were recorded during the day.")

    st.divider()

    st.header("2. Bivariate Analysis")

    st.subheader("1. Average Sales per Order by City")

    city_orders = data.groupby(["City", "Order ID"])["Sales"].sum().reset_index()
    city_average = city_orders.groupby("City")["Sales"].mean().reset_index()
    city_average.columns = ["City", "Average Sales"]

    fig = px.bar(city_average, x="City", y="Average Sales",
                 title="Average Sales per Order by City")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("2. Quantity Ordered by Product")

    product_quantity = data.groupby("Product")["Quantity Ordered"].sum().reset_index()

    fig = px.bar(product_quantity, x="Product", y="Quantity Ordered",
                 title="Quantity Ordered by Product")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("3. Total Sales by Month and Hour")

    month_hour = data.groupby(["Month", "Hour"])["Sales"].sum().reset_index()

    month_hour["Month"] = pd.Categorical(
        month_hour["Month"], categories=month_list, ordered=True)
    month_hour = month_hour.sort_values("Month")

    fig = px.density_heatmap(
        month_hour, x="Hour", y="Month", z="Sales",
        title="Total Sales by Month and Hour")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("4. Product Price and Quantity Relationship")

    price_quantity = data.groupby("Product").agg({
        "Price Each": "mean",
        "Quantity Ordered": "sum"
    }).reset_index()

    fig = px.scatter(
        price_quantity, x="Price Each", y="Quantity Ordered",
        hover_name="Product",
        title="Product Price vs Quantity Sold")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.header("3. Additional Research Questions")

    st.subheader("Question 1: Which day of the week has the highest sales?")

    day_list = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"]

    day_sales = data.groupby("Day")["Sales"].sum()
    day_sales = day_sales.reindex(day_list, fill_value=0)
    day_sales = day_sales.reset_index()
    day_sales.columns = ["Day", "Sales"]

    fig = px.bar(day_sales, x="Day", y="Sales",
                 title="Sales by Day of the Week")
    st.plotly_chart(fig, use_container_width=True)

    best_day = day_sales.loc[day_sales["Sales"].idxmax()]
    st.write(
        f"Insight: {best_day['Day']} has the highest sales "
        f"with ${best_day['Sales']:,.2f}.")

    st.subheader("Question 2: Which state generates the highest sales?")

    state_sales = data.groupby("State")["Sales"].sum().reset_index()
    state_sales = state_sales.sort_values("Sales", ascending=False)

    fig = px.bar(state_sales, x="State", y="Sales",
                 title="Sales by State")
    st.plotly_chart(fig, use_container_width=True)

    best_state = state_sales.iloc[0]
    st.write(
        f"Insight: State {best_state['State']} has the highest sales "
        f"with ${best_state['Sales']:,.2f}.")

    st.divider()

    st.header("4. Conclusion")

    best_product = data.groupby("Product")["Quantity Ordered"].sum().idxmax()
    best_city = data.groupby("City")["Sales"].sum().idxmax()
    best_month = data.groupby("Month")["Sales"].sum().idxmax()
    best_hour = data.groupby("Hour")["Sales"].sum().idxmax()

    st.write(f"1. Total sales are ${total_sales:,.2f}.")
    st.write(f"2. The most sold product is {best_product}.")
    st.write(f"3. The city with highest sales is {best_city}.")
    st.write(f"4. The month with highest sales is {best_month}.")
    st.write(f"5. The busiest sales hour is {best_hour}:00.")

    csv_file = data.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Filtered Data",
        csv_file,
        "filtered_sales_data.csv",
        "text/csv")


with tab2:

    st.header("Data Cleaning Report")

    report_data = pd.DataFrame(
        list(report.items()),
        columns=["Cleaning Step", "Rows"])

    st.dataframe(report_data, use_container_width=True)

    st.subheader("Sales Outlier Detection")

    fig = px.box(df, y="Sales", title="Sales Box Plot")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Quantity Outlier Detection")

    fig = px.box(df, y="Quantity Ordered",
                 title="Quantity Ordered Box Plot")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Outlier Decision")

    st.write("High sales and quantities may be genuine purchases. "
             "These values are kept unless they are confirmed as errors.")

    st.subheader("Cleaned Dataset Preview")

    st.dataframe(df.head(100), use_container_width=True)

    st.write("Total Cleaned Rows:", len(df))
    st.write("Total Columns:", len(df.columns))
