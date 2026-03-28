import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="E-Commerce Sales Dashboard", page_icon="🛒", layout="wide")

np.random.seed(99)

CATEGORIES = ["Electronics", "Clothing", "Home & Furniture", "Books", "Sports", "Beauty"]
SUB_CAT = {
    "Electronics":       ["Mobiles", "Laptops", "Headphones", "Cameras", "Tablets"],
    "Clothing":          ["Men", "Women", "Kids", "Footwear", "Accessories"],
    "Home & Furniture":  ["Sofa", "Bed", "Kitchen", "Decor", "Lighting"],
    "Books":             ["Fiction", "Non-Fiction", "Academic", "Comics", "Self-Help"],
    "Sports":            ["Cricket", "Football", "Gym", "Cycling", "Yoga"],
    "Beauty":            ["Skincare", "Makeup", "Haircare", "Perfume", "Grooming"],
}
REGIONS   = ["North", "South", "East", "West", "Central"]
SEGMENTS  = ["Consumer", "Corporate", "Home Office"]
MONTHS    = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
BASE_PX   = {"Electronics":450,"Clothing":85,"Home & Furniture":320,
             "Books":25,"Sports":110,"Beauty":60}

@st.cache_data
def generate_data():
    n = 5000
    cats     = np.random.choice(CATEGORIES, n, p=[0.25,0.20,0.18,0.10,0.15,0.12])
    sub_cats = [np.random.choice(SUB_CAT[c]) for c in cats]
    regions  = np.random.choice(REGIONS, n)
    segments = np.random.choice(SEGMENTS, n, p=[0.55,0.30,0.15])
    months   = np.random.randint(1, 13, n)
    years    = np.random.choice([2021,2022,2023], n, p=[0.28,0.35,0.37])
    prices   = np.array([max(10, np.random.normal(BASE_PX[c], BASE_PX[c]*0.3)) for c in cats])
    qty      = np.random.randint(1, 6, n)
    discount = np.random.choice([0,0,0,0.05,0.10,0.15,0.20,0.30], n)
    profit_m = np.where(discount > 0.20,
                        np.random.uniform(-0.10, 0.05, n),
                        np.random.uniform(0.05, 0.35, n))
    sales    = prices * qty * (1 - discount)
    profit   = sales * profit_m

    return pd.DataFrame({
        "Year": years, "Month": months,
        "Month_Name": [MONTHS[m-1] for m in months],
        "Category": cats, "Sub_Category": sub_cats,
        "Region": regions, "Segment": segments,
        "Quantity": qty, "Price": prices.round(2),
        "Discount": discount, "Sales": sales.round(2),
        "Profit": profit.round(2),
        "Profit_Margin": (profit / sales * 100).round(1),
    })

df = generate_data()

# Sidebar
st.sidebar.title("🛒 Filters")
yr  = st.sidebar.multiselect("Year",     sorted(df.Year.unique()),     default=sorted(df.Year.unique()))
reg = st.sidebar.multiselect("Region",   sorted(df.Region.unique()),   default=sorted(df.Region.unique()))
cat = st.sidebar.multiselect("Category", sorted(df.Category.unique()), default=sorted(df.Category.unique()))

fdf = df[df.Year.isin(yr) & df.Region.isin(reg) & df.Category.isin(cat)]

# Title
st.title("🛒 E-Commerce Sales Analytics Dashboard")
st.caption("Built with Python · Pandas · Plotly · Streamlit  |  By **Saumya Gupta**")
st.markdown("---")

# KPIs
k1,k2,k3,k4 = st.columns(4)
k1.metric("💰 Total Sales",  f"₹{fdf.Sales.sum():,.0f}")
k2.metric("📈 Total Profit", f"₹{fdf.Profit.sum():,.0f}")
k3.metric("📦 Orders",       f"{len(fdf):,}")
k4.metric("📊 Avg Margin",   f"{fdf.Profit_Margin.mean():.1f}%")
st.markdown("---")

# Row 1
c1, c2 = st.columns(2)
with c1:
    st.subheader("📅 Monthly Revenue Trend")
    monthly = (fdf.groupby(["Year","Month","Month_Name"])["Sales"]
               .sum().reset_index().sort_values(["Year","Month"]))
    monthly["Label"] = monthly["Month_Name"] + " " + monthly["Year"].astype(str)
    fig = px.line(monthly, x="Label", y="Sales", color="Year",
                  markers=True, template="plotly_white",
                  labels={"Sales":"Revenue (₹)","Label":""})
    fig.update_layout(height=310, margin=dict(l=5,r=5,t=5,b=70),
                      xaxis_tickangle=-45, legend_title="Year")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("🥧 Sales by Category")
    cat_s = fdf.groupby("Category")["Sales"].sum().reset_index()
    fig2  = px.pie(cat_s, values="Sales", names="Category", hole=0.4,
                   template="plotly_white",
                   color_discrete_sequence=px.colors.qualitative.Set2)
    fig2.update_layout(height=310, margin=dict(l=5,r=5,t=5,b=5))
    st.plotly_chart(fig2, use_container_width=True)

# Row 2
c3, c4 = st.columns(2)
with c3:
    st.subheader("🌍 Region-wise Profit")
    reg_p = fdf.groupby("Region")["Profit"].sum().reset_index().sort_values("Profit")
    clrs  = ["#ef4444" if x < 0 else "#22c55e" for x in reg_p.Profit]
    fig3  = go.Figure(go.Bar(x=reg_p.Profit, y=reg_p.Region,
                              orientation="h", marker_color=clrs))
    fig3.update_layout(height=290, template="plotly_white",
                       xaxis_title="Profit (₹)", margin=dict(l=5,r=5,t=5,b=5))
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.subheader("👥 Segment Sales vs Profit")
    seg = fdf.groupby("Segment")[["Sales","Profit"]].sum().reset_index()
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(name="Sales",  x=seg.Segment, y=seg.Sales,  marker_color="#3b82f6"))
    fig4.add_trace(go.Bar(name="Profit", x=seg.Segment, y=seg.Profit, marker_color="#22c55e"))
    fig4.update_layout(barmode="group", height=290,
                       template="plotly_white", margin=dict(l=5,r=5,t=5,b=5))
    st.plotly_chart(fig4, use_container_width=True)

# Row 3
c5, c6 = st.columns(2)
with c5:
    st.subheader("🔻 Discount vs Profit Margin")
    samp = fdf.sample(min(500, len(fdf)), random_state=1)
    fig5 = px.scatter(samp, x="Discount", y="Profit_Margin", color="Category",
                      opacity=0.65, template="plotly_white",
                      labels={"Discount":"Discount","Profit_Margin":"Profit Margin %"})
    fig5.update_layout(height=320, margin=dict(l=5,r=5,t=5,b=5))
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    st.subheader("🔥 Top 10 Sub-Categories by Sales")
    top_sub = fdf.groupby("Sub_Category")["Sales"].sum().nlargest(10).reset_index()
    fig6 = px.bar(top_sub, x="Sales", y="Sub_Category", orientation="h",
                  color="Sales", color_continuous_scale="Blues", template="plotly_white")
    fig6.update_layout(height=320, showlegend=False, margin=dict(l=5,r=5,t=5,b=5))
    st.plotly_chart(fig6, use_container_width=True)

# Loss alert
st.subheader("⚠️ Loss-Making Sub-Categories")
loss = fdf.groupby(["Category","Sub_Category"])["Profit"].sum().reset_index()
loss = loss[loss.Profit < 0].sort_values("Profit")
if len(loss):
    fig7 = px.bar(loss, x="Sub_Category", y="Profit", color="Category",
                  template="plotly_white")
    fig7.update_layout(height=260, margin=dict(l=5,r=5,t=5,b=60), xaxis_tickangle=-35)
    st.plotly_chart(fig7, use_container_width=True)
else:
    st.success("✅ No loss-making categories in selected filters!")

with st.expander("📊 View Raw Data"):
    st.dataframe(fdf.head(200).reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.caption("© Saumya Gupta | Data Analytics Portfolio | [LinkedIn](https://www.linkedin.com/in/collabs2saumya/)")
