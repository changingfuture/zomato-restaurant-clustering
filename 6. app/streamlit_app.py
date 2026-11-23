# Importing StreamLIt
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page Configuration
st.set_page_config(
    page_title= "Zomato Restaurant Analytics",
    page_icon= "🍽️",
    layout= "wide"
)

# Dashboard Header
st.title("🍽️ Zomato Restaurant Analytics")
st.subheader("Restaurant Segmentation and Insights")
st.write(
    "Explore Restaurant Clusters, Pricing Patterns, Customer Ratings,"
    "Review Characteristics, and Customer Engagement using Machine Learning."
)
st.divider()

# Sidebar Navigation
st.sidebar.title("Navigation")
selected_page = st.sidebar.selectbox(
    "Select a Page",
    [
        "Overview", 
        "Cluster Analysis",
        "Restaurant Explorer",
        "Model Insights"
    ]
)
st.sidebar.divider()
st.sidebar.caption("Zomato Restaurant Analytics")

# Project Paths
project_root = Path(__file__).resolve().parents[1]
processed_data_path = project_root / "1. data" / "processed"

# Loading Final Clustered Dataset
final_results = pd.read_csv(
    processed_data_path / "final_restaurant_clusters.csv"
)

# Overview Metrics
if selected_page == "Overview":
    total_restaurants = len(final_results)
    total_clusters = final_results["Clusters"].nunique()
    avg_cost = final_results["Cost"].mean()
    average_rating = final_results["avg_rating"].mean()

    # KPI Cards
    st.subheader("Dataset Overview")
    col1, col2, col3,col4 = st.columns(4)
    with col1:
        st.metric(
            label= "Total Restaurants", 
            value= total_restaurants
        )
    with col2:
        st.metric(
            label= "Clusters Identified",
            value= total_clusters
        )
    with col3: 
        st.metric(
            label= "Average Cost (for 2 people)",
            value= f"₹{avg_cost:,.0f}"
        )
    with col4:
        st.metric(
            label= "Average Rating",
            value= f"{average_rating: .2f}/ 5"
        )

    # Restaurant Distribution by Cluster
    cluster_counts = (
        final_results["Clusters"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    cluster_counts.columns = ["Cluster", "Restaurants"]
    cluster_counts["Cluster"] = (
        "Cluster " + cluster_counts["Cluster"].astype(str)
    )

    # Cluster Distribution Chart
    st.subheader("Restaurant Distribution by Cluster")

    fig = px.bar(
        cluster_counts,
        x="Restaurants",
        y= "Cluster",
        orientation= "h",
        text= "Restaurants",
        color= "Cluster",
        color_discrete_sequence=["#2E8B57", "#81C784"],
        template="plotly_dark"
    )
    fig.update_layout(
        showlegend= False,
        xaxis_title="Number of Restaurants",
        yaxis_title ="",
        height= 350
    )
    fig.update_traces(textposition= "outside")
    st.plotly_chart(fig, use_container_width=True)

    # Average Rating by Cluster
    cluster_ratings = (
        final_results.groupby("Clusters")["avg_rating"]
        .mean()
        .reset_index()
    )
    cluster_ratings["Clusters"] = (
        "Cluster " + cluster_ratings["Clusters"].astype(str)
    )

    # Overview Comparison Charts
        # Average Cost Comparison Data
    cluster_costs = (
        final_results.groupby("Clusters")["Cost"]
        .mean()
        .reset_index()
    )
    cluster_costs["Clusters"] = (
        "Cluster " + cluster_costs["Clusters"].astype(str)
    )
    col1, col2 = st.columns(2)

    # Average Rating Comparison
    with col1: 
        st.subheader("Average Rating by Cluster")
        rating_fig = px.bar(
            cluster_ratings,
            x="Clusters",
            y="avg_rating",
            text= "avg_rating",
            color = "Clusters",
            color_discrete_sequence=["#2E8B57", "#81C784"],
            template= "plotly_dark"
        )
        rating_fig.update_layout(
            showlegend=False,
            xaxis_title= "",
            yaxis_title="Average Rating",
            yaxis_range= [0,5],
            height= 400
        )
        rating_fig.update_traces(
            texttemplate= "%{text:.2f}",
            textposition= "outside"
        )
        st.plotly_chart(rating_fig, use_container_width=True, key= "average_rating_chart")

    # Average Cost Comparison
    with col2: 
        st.subheader("Average Cost for Two")
        cost_fig = px.bar(
            cluster_costs,
            x = "Clusters",
            y = "Cost",
            text= "Cost",
            color= "Clusters",
            color_discrete_sequence=["#2E8B57", "#81C784"],
            template="plotly_dark"
        )
        cost_fig.update_layout(
            showlegend=False,
            xaxis_title ="",
            yaxis_title ="Average Cost (₹)",
            height= 400
        )
        cost_fig.update_traces(
            texttemplate= "₹%{text:,.0f}",
            textposition= "outside"
        )
        st.plotly_chart(cost_fig, use_container_width=True, key= "average_cost_chart")

    # Cluster Summary
    st.divider()
    st.subheader("Cluster Summary")

    col1, col2=st.columns(2)
    with col1: 
        st.subheader("Cluster 0 - Budget Friendly")
        st.write(
            """
            - Lower Average Cost
            - Average Rating of 3.33
            - Shorter Customer Reviews
            - Lower Photo Engagement
            - Higher Rating Variability
            """
        )
    with col2: 
        st.subheader("Cluster 1 - Premium Segment")
        st.write(
            """
            - Higher Average Cost
            - Average Rating of 3.88
            - Longer Customer Reviews
            - Higher Photo Engagement
            - More Consistent Ratings
            """
        )

# Cluster Analysis Page 
if selected_page == "Cluster Analysis": 

    st.title("Cluster Analysis")
    st.write(
        "Explore the characteristics, distributions, and differences "
        "between the Restaurant Clusters."
    )
    st.divider()

    # Cluster Profile Comparison
    st.subheader("Cluster Profile Comparison")
    cluster_profiles = (
        final_results.groupby("Clusters")[
            ["Cost", "avg_rating", "rating_std", "median_rl", "avg_pic"]
        ]
        .mean()
        .round(2)
    )

    cluster_profiles.index = [
        f"Cluster {cluster}" for cluster in cluster_profiles.index
    ]
    cluster_profiles = cluster_profiles.rename(
        columns= {
            "Cost" : "Average Cost (for Two)",
            "avg_rating" : "Average Rating",
            "rating_std" : "Rating Variability",
            "median_rl" : "Median Review Length",
            "avg_pic" : "Average Picture"
        }
    )
    st.dataframe(cluster_profiles, use_container_width=True)
    st.divider()

    # Cluster Comparison Charts
    st.subheader("Cluster Characteristics")

    # Chart Function
    def create_cluster_chart(data, metric, title, y_title, text_format):
        fig = px.bar(
            data, 
            x= "Clusters",
            y = metric,
            text= metric, 
            color = "Clusters",
            color_discrete_sequence=["#2E8B57", "#81C784"],
            template="plotly_dark"
        )
        fig.update_layout(
            title= title,
            showlegend = False,
            xaxis_title = "",
            yaxis_title= y_title,
            height= 400,
            margin=dict(t=60, b=40, l=40, r=20)    
        )
        fig.update_traces(
            texttemplate= text_format,
            textposition= "outside"
        )
        return fig
    # Prepare Cluster Labels
    chart_data = (
        final_results.groupby("Clusters")[
            ["Cost", "avg_rating", "rating_std", "median_rl", "avg_pic"]
        ]
        .mean()
        .reset_index()
    )
    chart_data["Clusters"] = (
        "Cluster " + chart_data["Clusters"].astype(str)
    )
    # Row 1 - Cost and Ratings
    col1, col2= st.columns(2)

    with col1: 
        cost_fig = create_cluster_chart(
            chart_data,
            "Cost",
            "Average Cost for Two",
            "Cost(₹)",
            "₹%{text:,.0f}"
        )
        st.plotly_chart(
            cost_fig,
            use_container_width=True,
            key= "analysis_cost_chart"
        )

    with col2:
        rating_fig = create_cluster_chart(
            chart_data,
            "avg_rating",
            "Average Restaurant Rating",
            "Rating (out of 5)",
            "%{text:.2f}"
        )
        rating_fig.update_layout(yaxis_range=[0, 5])
        st.plotly_chart(
            rating_fig,
            use_container_width=True,
            key="analysis_rating_chart"
        )

    # Row 2 - Rating Variability and Review Length
    col3, col4= st.columns(2)
    with col3:
        variability_fig = create_cluster_chart(
            chart_data,
            "rating_std",
            "Rating Variability",
            "Standard Deviation of Ratings",
            "%{text:.2f}"
        )
        st.plotly_chart(
            variability_fig,
            use_container_width=True,
            key="analysis_variability_chart"
        )
    with col4:
        review_fig = create_cluster_chart(
            chart_data,
            "median_rl",
            "Customer Review Length",
            "Median Words per Review",
            "%{text:.1f}"
        )
        st.plotly_chart(
            review_fig,
            use_container_width=True,
            key="analysis_review_chart"
        )

    # Row 3 - Photo Engagement
    st.subheader("Customer Photo Engagement")
    photo_fig = create_cluster_chart(
        chart_data,
        "avg_pic",
        "Average Photos per Review",
        "Average Number of Pictures",
        "%{text:.2f}"
    )
    st.plotly_chart(
        photo_fig,
        use_container_width=True,
        key="analysis_photo_chart"
    )

    # Cluster Interpretation
    st.divider()

    st.subheader("Cluster Interpretation")
    st.markdown(
        """
        **Cluster 0 - Budget-Friendly Segment**

        Restaurants in this segment generally exhibit lower average costs,
        comparatively lower ratings, greater rating variability, shorter
        customer reviews, and lower photo engagement.

        **Cluster 1 - Premium Segment**

        Restaurants in this segment generally exhibit higher average costs,
        higher ratings, more consistent ratings, longer customer reviews,
        and higher photo engagement.
        """
    )
    st.caption(
        "These clusters represent patterns identified by K-Means clustering. "
        "The segments are not absolute categories, and individual restaurants "
        "may exhibit characteristics that differ from their cluster profile."
    )

# Restaurant Explorer Page
# Restaurant Explorer Page
if selected_page == "Restaurant Explorer":

    st.title("Restaurant Explorer")

    st.write(
        "Search, filter, and explore individual restaurants "
        "within the identified clusters."
    )

    st.divider()

    # Restaurant Filters
    st.subheader("Filter Restaurants")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search_query = st.text_input(
            "Search Restaurant",
            placeholder="Enter restaurant name..."
        )

    with col2:
        selected_cluster = st.selectbox(
            "Select Cluster",
            ["All Clusters", 0, 1]
        )

    with col3:
        min_rating = st.slider(
            "Minimum Rating",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5
        )

    with col4:
        max_cost = st.slider(
            "Maximum Cost (for two)",
            min_value=0,
            max_value=int(final_results["Cost"].max()),
            value=int(final_results["Cost"].max()),
            step=100
        )

    # Apply Filters
    filtered_restaurants = final_results.copy()

    # Search Filter
    if search_query.strip():

        filtered_restaurants = filtered_restaurants[
            filtered_restaurants["Restaurant"]
            .str.contains(
                search_query.strip(),
                case=False,
                na=False,
                regex=False
            )
        ]

    # Cluster Filter
    if selected_cluster != "All Clusters":

        filtered_restaurants = filtered_restaurants[
            filtered_restaurants["Clusters"] == selected_cluster
        ]

    # Rating Filter
    if min_rating > 0:

        filtered_restaurants = filtered_restaurants[
            filtered_restaurants["avg_rating"] >= min_rating
        ]

    # Cost Filter
    filtered_restaurants = filtered_restaurants[
        filtered_restaurants["Cost"] <= max_cost
    ]

    st.divider()

    # Search Results
    st.subheader("Search Results")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Restaurants Found",
            len(filtered_restaurants)
        )

    with col2:

        valid_ratings = filtered_restaurants["avg_rating"].dropna()

        if not valid_ratings.empty:

            st.metric(
                "Average Rating",
                f"{valid_ratings.mean():.2f} / 5"
            )

        else:

            st.metric(
                "Average Rating",
                "N/A"
            )

    with col3:

        if not filtered_restaurants.empty:

            st.metric(
                "Average Cost (for two)",
                f"₹{filtered_restaurants['Cost'].mean():,.0f}"
            )

        else:

            st.metric(
                "Average Cost (for two)",
                "N/A"
            )

    # Restaurant Listings
    st.subheader("Restaurant Listings")

    if not filtered_restaurants.empty:

        display_columns = [
            "Restaurant",
            "Cost",
            "avg_rating",
            "Cuisines",
            "Clusters"
        ]

        restaurant_table = (
            filtered_restaurants[display_columns]
            .sort_values(
                "avg_rating",
                ascending=False,
                na_position="last"
            )
        )

        st.dataframe(
            restaurant_table,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No restaurants match the selected filters. "
            "Try adjusting your search criteria."
        )

    st.divider()

    # Individual Restaurant Profile
    st.subheader("Restaurant Profile")

    if not filtered_restaurants.empty:

        selected_restaurant_name = st.selectbox(
            "Choose a Restaurant",
            sorted(filtered_restaurants["Restaurant"].dropna().unique())
        )

        restaurant_profile = filtered_restaurants[
            filtered_restaurants["Restaurant"]
            == selected_restaurant_name
        ].iloc[0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Cost (for two)",
                f"₹{restaurant_profile['Cost']:,.0f}"
            )

        with col2:

            rating = restaurant_profile["avg_rating"]

            st.metric(
                "Average Rating",
                f"{rating:.2f} / 5" if pd.notna(rating)
                else "Not Rated"
            )

        with col3:

            variability = restaurant_profile["rating_std"]

            st.metric(
                "Rating Variability",
                f"{variability:.2f}" if pd.notna(variability)
                else "N/A"
            )

        with col4:

            st.metric(
                "Cluster",
                f"Cluster {int(restaurant_profile['Clusters'])}"
            )

        st.markdown("### Restaurant Details")

        st.write(
            f"**Cuisines:** {restaurant_profile['Cuisines']}"
        )

        review_length = restaurant_profile["median_rl"]

        st.write(
            f"**Median Review Length:** "
            f"{review_length:.1f} words"
            if pd.notna(review_length)
            else "**Median Review Length:** N/A"
        )

        photo_count = restaurant_profile["avg_pic"]

        st.write(
            f"**Average Pictures per Review:** "
            f"{photo_count:.2f}"
            if pd.notna(photo_count)
            else "**Average Pictures per Review:** N/A"
        )

# Model Insights Page
if selected_page == "Model Insights":
    st.title("Model Insights")
    st.write(
        "Understand the clustering methodology, model performance, "
        "evaluation metrics, and insights derived from the restaurant segments."
    )

    st.divider()

    # Model Overview
    st.subheader("Model Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.metric("Algorithm", "K-Means")
    with col2: 
        st.metric("Optimal Clusters (K)", "2")
    with col3: 
        st.metric("Restaurants","105")
    with col4:
        st.metric("Features","49")

    st.markdown(
        """
        The K-Means clustering algorithm was used to group restaurants
        based on similarities in their cost, rating behaviour,
        customer review characteristics, photo engagement, and cuisine
        representation.
        """
    )
    st.divider()

    # Model Configuration
    st.subheader("Model Configuration")
    model_configuration = pd.DataFrame(
        {
             "Parameter": [
                "Algorithm",
                "Number of Clusters",
                "Random State",
                "Number of Initializations",
                "Distance Measure"
            ],
            "Value": [
                "K-Means",
                "2",
                "42",
                "10",
                "Euclidean Distance"
            ]
        }
    )
    st.dataframe(
        model_configuration,
        use_container_width=True,
        hide_index=True
    )
    st.divider()

    # Evaluation Metrics
    st.subheader("Model Evaluation")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Inertia",
            "461.72"
        )
    with col2:
        st.metric(
            "Silhouette Score",
            "0.2073"
        )
    with col3:
        st.metric(
            "Davies-Bouldin Index",
            "1.7012"
        )
    with col4:
        st.metric(
            "Calinski-Harabasz Score",
            "34.0173"
        )

    metrics_data = pd.DataFrame(
        {
            "Metric": [
                "Inertia",
                "Silhouette Score",
                "Davies-Bouldin Index",
                "Calinski-Harabasz Score"
            ],
            "Value": [
                461.7208,
                0.2073,
                1.7012,
                34.0173
            ],
            "Interpretation": [
                "Within-cluster sum of squared distances",
                "Measures cluster separation and cohesion",
                "Evaluates separation between clusters",
                "Evaluates cluster dispersion and separation"
            ]
        }
    )
    st.dataframe(
        metrics_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Cluster Distribution
    st.subheader("Cluster Distribution")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Cluster 0",
            "55 Restaurants",
            "52.4% of dataset"
        )
    with col2:
        st.metric(
            "Cluster 1",
            "50 Restaurants",
            "47.6% of dataset"
        )

    st.markdown(
        """
        The dataset is distributed relatively evenly between the two
        identified clusters, with 55 restaurants in Cluster 0 and
        50 restaurants in Cluster 1.
        """
    )
    st.divider()

    # Key Findings
    st.subheader("Key Findings")

    st.markdown(
        """
        **Cluster 0 — Budget-Friendly Segment**
        - Lower average cost.
        - Lower average restaurant rating.
        - Greater rating variability.
        - Shorter customer reviews.
        - Lower photo engagement.

        **Cluster 1 — Premium Segment**
        - Higher average cost.
        - Higher average restaurant rating.
        - More consistent ratings.
        - Longer customer reviews.
        - Higher photo engagement.
        """
    )
    st.divider()

    # Model Limitations
    st.subheader("Model Limitations")

    st.markdown(
        """
        - The Silhouette Score indicates relatively weak separation
          between the identified clusters.
        - Some restaurants may share characteristics across both
          segments.
        - K-Means forms clusters based on feature-space distances,
          which may not represent every aspect of restaurant quality.
        - The results depend on the selected features, preprocessing
          methods, and clustering parameters.
        - Cluster labels represent groups of similar restaurants,
          not absolute rankings of restaurant quality.
        """
    )
    st.warning(
        "The identified clusters provide useful segmentation patterns, "
        "but the relatively low Silhouette Score suggests that the "
        "clusters overlap and should be interpreted with caution."
    )

    st.divider()

    # Conclusion
    st.subheader("Conclusion")
    st.markdown(
        """
        The clustering analysis identified two restaurant segments with
        different cost levels, rating behaviour, customer review
        characteristics, and photo engagement.

        Although the clusters provide meaningful descriptive insights,
        their separation is not particularly strong. The model is
        therefore best used as an exploratory segmentation tool rather
        than a definitive classification of restaurants.
        """
    )