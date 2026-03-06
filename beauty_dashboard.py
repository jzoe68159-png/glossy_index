import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import re


# Page configuration –  pink theme

st.set_page_config(
    page_title="✨ The Glossy Index – Beauty Product Analyzer",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make it visually pleasing
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fce4e8 0%, #f8d7e3 100%);
    }
    .css-1aumxhk {
        background-color: rgba(255,255,255,0.9);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #b34180;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton>button {
        background-color: #d96c9e;
        color: white;
        border-radius: 25px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #b34180;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.stApp {
    background: linear-gradient(-45deg, #fce4e8, #f8d7e3, #ffd9e8, #ffc0cb);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
</style>
""", unsafe_allow_html=True)

st.title("💖 **The Glossy Index** – Beauty Product Analyzer")
st.markdown("Uncover the **real value** behind beauty products. Do expensive products really have better ingredients? Let's find out!")


# Load and cache data

@st.cache_data
def load_data():
    df = pd.read_csv('product_info.csv')
    # Keep only necessary columns (avoid large data)
    keep_cols = ['product_id', 'product_name', 'brand_name', 'price_usd', 'rating',
                 'ingredients', 'primary_category', 'secondary_category', 'loves_count']
    df = df[[c for c in keep_cols if c in df.columns]]
    return df

df = load_data()


# Ingredient scoring (same as before)

ingredient_scores = {
    # High-quality
    'Sodium Hyaluronate': 3, 'Hyaluronic Acid': 3, 'Tocopherol': 3,
    'Niacinamide': 3, 'Retinol': 3, 'Vitamin C': 3, 'Ascorbic Acid': 3,
    'Peptides': 3, 'Ceramides': 3, 'Shea Butter': 3,
    # Moderate
    'Glycerin': 2, 'Aloe Barbadensis': 2, 'Aloe Vera': 2,
    'Green Tea': 2, 'Salicylic Acid': 2, 'Lactic Acid': 2,
    'Glycolic Acid': 2, 'Honey': 2,
    # Low/controversial
    'Fragrance': 1, 'Parfum': 1, 'Alcohol Denat.': 1,
    'Denatured Alcohol': 1, 'Phenoxyethanol': 1,
    'Sodium Lauryl Sulfate': 1, 'SLS': 1, 'Sulfates': 1,
    # Common perfume ingredients
    'Limonene': 1, 'D-Limonene': 1, 'Linalool': 1,
    'Citronellol': 1, 'Geraniol': 1, 'Eugenol': 1,
    'Coumarin': 1, 'Benzyl Alcohol': 1, 'Benzyl Benzoate': 1,
    'Benzyl Salicylate': 1, 'Citral': 1, 'Farnesol': 1,
    'Isoeugenol': 1, 'Cinnamal': 1, 'Hexyl Cinnamal': 1,
    'Alpha-Isomethyl Ionone': 1, 'Octoxynol-10': 1,
    'Ethylhexyl Methoxycinnamate': 1,
    'Butyl Methoxydibenzoylmethane': 1,
    'Ethylhexyl Salicylate': 1,
}

@st.cache_data
def compute_scores(df):
    def score_ingredients(text):
        if pd.isna(text):
            return 0
        text = str(text).lower()
        total = 0
        for ing, score in ingredient_scores.items():
            if re.search(r'\b' + re.escape(ing.lower()) + r'\b', text):
                total += score
        return total

    df = df.copy()
    df['ingredient_score'] = df['ingredients'].apply(score_ingredients)
    return df

df = compute_scores(df)


# Sidebar filters 
st.sidebar.header("🎀 **Filter your products**")

# Brand multi-select
brands = sorted(df['brand_name'].dropna().unique())
selected_brands = st.sidebar.multiselect("Brand", brands, default=[])

# Price range
price_min = float(df['price_usd'].min())
price_max = float(df['price_usd'].max())
price_range = st.sidebar.slider("Price ($)", price_min, price_max, (price_min, price_max))

# Rating
rating_min = float(df['rating'].min())
rating_max = float(df['rating'].max())
rating_range = st.sidebar.slider("Rating", rating_min, rating_max, (rating_min, rating_max))

# Category
categories = sorted(df['primary_category'].dropna().unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=[])

# Apply filters
mask = (df['price_usd'].between(price_range[0], price_range[1])) & \
       (df['rating'].between(rating_range[0], rating_range[1]))
if selected_brands:
    mask &= df['brand_name'].isin(selected_brands)
if selected_categories:
    mask &= df['primary_category'].isin(selected_categories)

df_filtered = df[mask].copy()

st.sidebar.markdown(f"**✨ {len(df_filtered)} products match your vibe.**")

# Main content – two columns

col1, col2 = st.columns(2)

with col1:
    st.subheader("💎 **Price vs. Ingredient Quality**")
    fig = px.scatter(df_filtered, x='ingredient_score', y='price_usd',
                     color='rating', hover_name='product_name',
                     hover_data={'brand_name': True, 'price_usd': ':.2f'},
                     color_continuous_scale='plasma',  # brighter scale
                     size='rating', size_max=15,        # bigger points
                     title="Is there a relationship?")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#b34180'
    )
    # Add darker grid lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💰 **Top 10 Most Expensive Brands**")
    brand_avg = df_filtered.groupby('brand_name')['price_usd'].mean().sort_values(ascending=False).head(10)
    fig2 = px.bar(brand_avg, x=brand_avg.values, y=brand_avg.index,
                  orientation='h', color=brand_avg.values,
                  color_continuous_scale='pinkyl')
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#b34180',
        xaxis_title="Average Price (USD)",
        yaxis_title=""
    )
    st.plotly_chart(fig2, use_container_width=True)

# Second row – two columns
col3, col4 = st.columns(2)

with col3:
    st.subheader("📊 **Ingredient Score by Price Category**")
    df_filtered['price_category'] = pd.cut(df_filtered['price_usd'],
                                           bins=[0, 25, 50, 100, 500, 2000],
                                           labels=['Budget (<$25)', 'Mid ($25-50)',
                                                   'Premium ($50-100)', 'Luxury ($100-500)',
                                                   'Ultra-Luxury ($500+)'])
    cat_score = df_filtered.groupby('price_category')['ingredient_score'].mean().dropna()
    fig3 = px.bar(cat_score, x=cat_score.index, y=cat_score.values,
                  color=cat_score.values, color_continuous_scale='peach')
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#b34180',
        xaxis_title="",
        yaxis_title="Average Ingredient Score"
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("💖 **Brand Love**")
    # Show brands with most products in filtered set
    top_brands = df_filtered['brand_name'].value_counts().head(10)
    fig4 = px.bar(top_brands, x=top_brands.values, y=top_brands.index,
                  orientation='h', color=top_brands.values,
                  color_continuous_scale='magenta')
    fig4.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#b34180',
        xaxis_title="Number of Products",
        yaxis_title=""
    )
    st.plotly_chart(fig4, use_container_width=True)


# Best Value Gems table


st.markdown("""
<style>
    .dataframe {
        background-color: #fff0f5 !important;
        border-radius: 15px;
    }
    .dataframe th {
        background-color: #d96c9e !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)
st.header("✨ **Best Value Gems**")
st.markdown("High ingredient score, affordable price, and top‑rated by customers.")

gems = df_filtered[(df_filtered['ingredient_score'] > 10) & (df_filtered['price_usd'] < 50) & (df_filtered['rating'] >= 4.5)]
gems = gems.sort_values('rating', ascending=False).drop_duplicates('product_name').head(20)

if not gems.empty:
    st.dataframe(
        gems[['product_name', 'brand_name', 'price_usd', 'ingredient_score', 'rating']],
        use_container_width=True,
        hide_index=True,
        column_config={
            'price_usd': st.column_config.NumberColumn(format="$%.2f"),
            'rating': st.column_config.NumberColumn(format="%.1f ⭐"),
        }
    )
else:
    st.info("No gems match your filters – try expanding your criteria!")


# Surprise Me Button 
st.markdown("---")
col_surprise1, col_surprise2 = st.columns([1, 3])
with col_surprise1:
    if st.button("🎁 **Surprise Me!**", use_container_width=True):
        # Get all gems (high score, low price, good rating)
        gems_all = df_filtered[(df_filtered['ingredient_score'] > 10) & 
                                (df_filtered['price_usd'] < 50) & 
                                (df_filtered['rating'] >= 4.5)].copy()
        if not gems_all.empty:
            surprise = gems_all.sample(1).iloc[0]
            st.balloons()   # 🎈 Celebration!
            with col_surprise2:
                st.success(f"**✨ Your surprise product: {surprise['product_name']}**")
                st.write(f"**Brand:** {surprise['brand_name']}")
                st.write(f"**Price:** ${surprise['price_usd']:.2f}")
                st.write(f"**Ingredient Score:** {surprise['ingredient_score']}")
                st.write(f"**Rating:** {surprise['rating']} ⭐")
        else:
            st.warning("No gems found with current filters – expand your criteria!")


# Brand comparison tool

st.header("⚖️ **Brand Battle**")
col5, col6 = st.columns(2)
with col5:
    brand_a = st.selectbox("Choose first brand", brands, index=0)
with col6:
    brand_b = st.selectbox("Choose second brand", brands, index=min(1, len(brands)-1))

if brand_a and brand_b:
    comp_df = df[df['brand_name'].isin([brand_a, brand_b])]
    comp_summary = comp_df.groupby('brand_name').agg({
        'price_usd': 'mean',
        'ingredient_score': 'mean',
        'rating': 'mean'
    }).round(2)
    st.dataframe(
        comp_summary,
        use_container_width=True,
        column_config={
            'price_usd': st.column_config.NumberColumn("Avg Price", format="$%.2f"),
            'ingredient_score': st.column_config.NumberColumn("Avg Ingredient Score"),
            'rating': st.column_config.NumberColumn("Avg Rating", format="%.1f ⭐"),
        }
    )

