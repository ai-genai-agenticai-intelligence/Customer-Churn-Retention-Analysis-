from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).resolve().parent / "Churn_Modelling.csv"
NAVY = "#18243B"
BLUE = "#536DFE"
TEAL = "#11A89A"
CORAL = "#F17468"
MUTED = "#718096"
GRID = "#E8EDF4"

st.set_page_config(
    page_title="Customer Churn | Retention Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_data():
    data = pd.read_csv(DATA_PATH)
    return data.drop(columns=["RowNumber", "CustomerId", "Surname"], errors="ignore")


def apply_filters(data, geography, age_range, membership, products):
    filtered = data[
        data["Age"].between(age_range[0], age_range[1])
        & data["NumOfProducts"].isin(products)
    ]
    if geography != "All regions":
        filtered = filtered[filtered["Geography"] == geography]
    if membership != "All customers":
        active = membership == "Active members"
        filtered = filtered[filtered["IsActiveMember"] == int(active)]
    return filtered


def churn_rate(data):
    return data["Exited"].mean() if not data.empty else 0


def segment_stats(data, column):
    return data.groupby(column, observed=True)["Exited"].agg(
        customers="size",
        churned="sum",
        churn_rate="mean",
    )


def age_groups(data):
    return pd.cut(
        data["Age"],
        bins=[age_min - 1, 25, 35, 45, 55, 65, age_max + 1],
        labels=["18–25", "26–35", "36–45", "46–55", "56–65", "66+"],
        include_lowest=True,
    )


def style_axes(ax):
    ax.set_facecolor("white")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", colors=MUTED, labelsize=9, length=0, pad=8)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot_churn_split(data):
    counts = data["Exited"].value_counts().reindex([0, 1], fill_value=0)
    fig, ax = plt.subplots(figsize=(5.5, 3.3), facecolor="white")
    wedges, _, _ = ax.pie(
        counts,
        colors=[TEAL, CORAL],
        startangle=90,
        counterclock=False,
        autopct=lambda pct: f"{pct:.1f}%" if pct else "",
        pctdistance=0.8,
        textprops={"color": NAVY, "fontsize": 10, "weight": "bold"},
        wedgeprops={"width": 0.32, "edgecolor": "white", "linewidth": 3},
    )
    ax.text(
        0,
        0.06,
        f"{len(data):,}",
        ha="center",
        va="center",
        color=NAVY,
        fontsize=20,
        fontweight="bold",
    )
    ax.text(0, -0.17, "customers", ha="center", color=MUTED, fontsize=9)
    ax.legend(
        wedges,
        ["Retained", "Churned"],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=2,
        frameon=False,
        labelcolor=MUTED,
        fontsize=9,
    )
    ax.set(aspect="equal")
    fig.tight_layout()
    return fig


def plot_age_distribution(data):
    fig, ax = plt.subplots(figsize=(7, 3.3), facecolor="white")
    for exited, label, color in [(0, "Retained", TEAL), (1, "Churned", CORAL)]:
        ages = data.loc[data["Exited"] == exited, "Age"]
        if not ages.empty:
            ax.hist(
                ages,
                bins=18,
                color=color,
                alpha=0.66,
                label=label,
                edgecolor="white",
                linewidth=0.5,
            )
    style_axes(ax)
    ax.set_xlabel("Customer age", color=MUTED, labelpad=10)
    ax.set_ylabel("Customers", color=MUTED, labelpad=10)
    ax.legend(frameon=False, labelcolor=MUTED, fontsize=9)
    fig.tight_layout()
    return fig


def plot_churn_by(data, column, title, labels=None):
    grouped = data.groupby(column, observed=True)["Exited"].mean().mul(100)
    counts = data.groupby(column, observed=True)["Exited"].size().reindex(grouped.index)
    if labels:
        grouped.index = [labels.get(value, value) for value in grouped.index]
    tick_labels = [
        f"{category}\n(n={count:,})"
        for category, count in zip(grouped.index, counts.values)
    ]
    fig, ax = plt.subplots(figsize=(6, 3.2), facecolor="white")
    bars = ax.bar(
        tick_labels,
        grouped.values,
        color=[CORAL if value == grouped.max() else BLUE for value in grouped.values],
        width=0.58,
        zorder=3,
    )
    style_axes(ax)
    ax.set_title(title, loc="left", color=NAVY, fontsize=11, fontweight="bold", pad=14)
    ax.set_ylabel("Churn rate (%)", color=MUTED, labelpad=10)
    ax.set_ylim(0, max(10, float(grouped.max()) * 1.3) if not grouped.empty else 10)
    for bar, value in zip(bars, grouped.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            color=NAVY,
            fontsize=9,
            fontweight="bold",
        )
    fig.tight_layout()
    return fig


def show_figure(fig):
    st.pyplot(fig, width="stretch")
    plt.close(fig)


st.markdown(
    """
    <style>
    .stApp {
        background: #F5F7FB;
        color: #18243B;
        font-family: 'Aptos', 'Segoe UI', sans-serif;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: #18243B;
        border-right: 1px solid rgba(255,255,255,.08);
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #E7ECF5;
    }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #A8B4C8;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] > div {
        background: #24334F;
        border-color: #3B4B68;
    }
    [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
        background: #AAB7FF;
    }
    .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3 {
        color: #18243B;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
        letter-spacing: -.025em;
    }
    h1 { font-size: 2rem !important; }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E8EDF4;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 3px 14px rgba(24,36,59,.035);
    }
    [data-testid="stMetricLabel"] { color: #718096; }
    [data-testid="stMetricValue"] { color: #18243B; }
    [data-testid="stTabs"] button {
        font-weight: 600;
        color: #718096;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #536DFE;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #E8EDF4;
        border-radius: 12px;
        overflow: hidden;
    }
    .eyebrow {
        color: #536DFE;
        font-size: .73rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin: 0 0 .45rem;
    }
    .page-subtitle {
        color: #718096;
        font-size: 1rem;
        margin-top: -.5rem;
        margin-bottom: 1.5rem;
    }
    .section-note {
        color: #718096;
        font-size: .9rem;
        margin-top: -.6rem;
        margin-bottom: 1.2rem;
    }
    .insight-card {
        background: #EEF1FF;
        border: 1px solid #DFE4FF;
        border-left: 4px solid #536DFE;
        border-radius: 12px;
        color: #34415E;
        padding: 14px 17px;
        margin: .25rem 0 1.2rem;
        font-size: .92rem;
    }
    .finding-card {
        height: 100%;
        background: #FFFFFF;
        border: 1px solid #E8EDF4;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 3px 14px rgba(24,36,59,.035);
    }
    .finding-label {
        color: #718096;
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .06em;
        text-transform: uppercase;
    }
    .finding-value {
        color: #18243B;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
        font-size: 1.65rem;
        font-weight: 700;
        margin: .35rem 0;
    }
    .finding-detail {
        color: #718096;
        font-size: .85rem;
        line-height: 1.45;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

data = load_data()
regions = ["All regions"] + sorted(data["Geography"].dropna().unique().tolist())
product_options = sorted(data["NumOfProducts"].dropna().unique().tolist())
age_min, age_max = int(data["Age"].min()), int(data["Age"].max())

with st.sidebar:
    st.markdown("## ✦ Retainly")
    st.caption("CUSTOMER INTELLIGENCE")
    st.markdown("---")
    st.markdown("### Refine your view")
    geography_filter = st.selectbox("Region", regions)
    age_filter = st.slider(
        "Customer age",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max),
        help="Limit the analysis to customers in this age range.",
    )
    membership_filter = st.selectbox(
        "Membership status",
        ["All customers", "Active members", "Inactive members"],
    )
    product_filter = st.multiselect(
        "Number of products",
        options=product_options,
        default=product_options,
    )
    st.markdown("---")
    st.caption("Filters update every metric and visualization.")

filtered_data = apply_filters(
    data,
    geography_filter,
    age_filter,
    membership_filter,
    product_filter,
)

st.markdown('<p class="eyebrow">CUSTOMER SUCCESS • ANALYTICS</p>', unsafe_allow_html=True)
st.title("Churn & Retention Overview")
st.markdown(
    '<p class="page-subtitle">Understand who is leaving, what puts them at risk, and where retention efforts can make a difference.</p>',
    unsafe_allow_html=True,
)

churned_count = int(filtered_data["Exited"].sum())
retained_count = len(filtered_data) - churned_count
current_churn_rate = churn_rate(filtered_data)
overall_rate = churn_rate(data)

metric_columns = st.columns(4)
metric_columns[0].metric("Customers in view", f"{len(filtered_data):,}")
metric_columns[1].metric(
    "Churn rate",
    f"{current_churn_rate:.1%}",
    f"{(current_churn_rate - overall_rate) * 100:+.1f} pp vs overall",
    delta_color="inverse",
)
metric_columns[2].metric("Customers retained", f"{retained_count:,}")
metric_columns[3].metric("Customers churned", f"{churned_count:,}")

st.markdown("")
overview_tab, drivers_tab, data_tab = st.tabs(
    ["Overview", "Churn drivers", "Data & quality"]
)

with overview_tab:
    st.subheader("What stands out")
    st.markdown(
        '<p class="section-note">Largest observed churn signals across the full dataset (10,000 customers).</p>',
        unsafe_allow_html=True,
    )
    geography_stats = segment_stats(data, "Geography")
    member_stats = segment_stats(data, "IsActiveMember")
    age_profile = data.assign(AgeGroup=age_groups(data))
    age_stats = segment_stats(age_profile, "AgeGroup").dropna()
    age_stats = age_stats[age_stats["customers"] >= 100]

    standout_columns = st.columns(3, gap="medium")
    standout_findings = [
        (
            "Highest-churn age group",
            str(age_stats["churn_rate"].idxmax()),
            age_stats["churn_rate"].max(),
            int(age_stats.loc[age_stats["churn_rate"].idxmax(), "customers"]),
        ),
        (
            "Highest-churn region",
            str(geography_stats["churn_rate"].idxmax()),
            geography_stats["churn_rate"].max(),
            int(geography_stats.loc[geography_stats["churn_rate"].idxmax(), "customers"]),
        ),
        (
            "Inactive members",
            "Higher churn",
            member_stats.loc[0, "churn_rate"],
            int(member_stats.loc[0, "customers"]),
        ),
    ]
    for column, (label, value, rate, customers) in zip(
        standout_columns, standout_findings
    ):
        with column:
            st.markdown(
                f'<div class="finding-card"><div class="finding-label">{label}</div>'
                f'<div class="finding-value">{value} · {rate:.1%}</div>'
                f'<div class="finding-detail">Churn among {customers:,} customers in this segment.</div></div>',
                unsafe_allow_html=True,
            )
    st.caption(
        "Segment comparisons are descriptive, not causal. Churn rates can vary with customer mix."
    )

    if filtered_data.empty:
        st.info("No customers match these filters. Broaden your selection to see the analysis.")
    else:
        left, right = st.columns([0.85, 1.5], gap="large")
        with left:
            st.subheader("Retention snapshot")
            st.markdown(
                '<p class="section-note">The balance between customers who stay and those who leave.</p>',
                unsafe_allow_html=True,
            )
            show_figure(plot_churn_split(filtered_data))
        with right:
            st.subheader("Churn profile by age")
            st.markdown(
                '<p class="section-note">Compare the age distribution of retained and churned customers.</p>',
                unsafe_allow_html=True,
            )
            show_figure(plot_age_distribution(filtered_data))

        st.markdown(
            f'<div class="insight-card"><strong>At a glance</strong> &nbsp; '
            f'{current_churn_rate:.1%} of customers in this view have churned. '
            f'The dashboard is currently showing {len(filtered_data):,} of {len(data):,} customers.</div>',
            unsafe_allow_html=True,
        )

        region_column, member_column = st.columns(2, gap="large")
        with region_column:
            show_figure(plot_churn_by(filtered_data, "Geography", "Churn by region"))
        with member_column:
            show_figure(
                plot_churn_by(
                    filtered_data,
                    "IsActiveMember",
                    "Churn by membership",
                    {0: "Inactive", 1: "Active"},
                )
            )
        product_column, gender_column = st.columns(2, gap="large")
        with product_column:
            show_figure(
                plot_churn_by(filtered_data, "NumOfProducts", "Churn by products")
            )
        with gender_column:
            show_figure(
                plot_churn_by(filtered_data, "Gender", "Churn by gender")
            )

with drivers_tab:
    st.subheader("Where churn risk concentrates")
    st.markdown(
        '<p class="section-note">Compare churn rates across customer segments in your current selection.</p>',
        unsafe_allow_html=True,
    )
    if filtered_data.empty:
        st.info("No customers match these filters. Broaden your selection to explore churn drivers.")
    else:
        driver_data = filtered_data.assign(AgeGroup=age_groups(filtered_data))
        age_column, region_column = st.columns(2, gap="large")
        with age_column:
            show_figure(plot_churn_by(driver_data, "AgeGroup", "Churn by age group"))
        with region_column:
            show_figure(plot_churn_by(filtered_data, "Geography", "Churn by region"))

        member_column, product_column = st.columns(2, gap="large")
        with member_column:
            show_figure(
                plot_churn_by(
                    filtered_data,
                    "IsActiveMember",
                    "Churn by membership status",
                    {0: "Inactive", 1: "Active"},
                )
            )
        with product_column:
            show_figure(
                plot_churn_by(
                    filtered_data, "NumOfProducts", "Churn by product count"
                )
            )
        gender_column, balance_column = st.columns(2, gap="large")
        with gender_column:
            show_figure(plot_churn_by(filtered_data, "Gender", "Churn by gender"))
        with balance_column:
            balance_data = filtered_data.assign(
                BalanceGroup=filtered_data["Balance"].gt(0).map(
                    {False: "Zero balance", True: "Has balance"}
                )
            )
            show_figure(
                plot_churn_by(balance_data, "BalanceGroup", "Churn by balance status")
            )

with data_tab:
    st.subheader("Explore customer records")
    st.markdown(
        '<p class="section-note">Review the filtered dataset and check the source data quality.</p>',
        unsafe_allow_html=True,
    )
    quality_columns = st.columns(3)
    quality_columns[0].metric("Source records", f"{len(data):,}")
    quality_columns[1].metric(
        "Missing values", f"{int(data.isna().sum().sum()):,}"
    )
    quality_columns[2].metric("Duplicate rows", f"{int(data.duplicated().sum()):,}")
    st.caption(
        "Churn is the observed Exited outcome, not a model prediction. "
        "The notebook's optional logistic-regression experiment is not used by this dashboard."
    )
    st.download_button(
        "Download filtered data",
        data=filtered_data.to_csv(index=False).encode("utf-8"),
        file_name="customer_churn_filtered.csv",
        mime="text/csv",
        disabled=filtered_data.empty,
    )
    st.dataframe(
        filtered_data,
        width="stretch",
        hide_index=True,
        height=440,
    )
    st.caption(f"Showing {len(filtered_data):,} filtered customer records.")
