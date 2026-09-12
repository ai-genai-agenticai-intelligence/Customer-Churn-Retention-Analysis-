import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "Churn_Modelling.csv"


# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df.drop(columns=["RowNumber", "CustomerId", "Surname"], errors="ignore")
    df = pd.get_dummies(df, columns=["Geography", "Gender"], drop_first=True)
    return df


df = load_data()

# -------------------------------
# Streamlit Layout
# -------------------------------
st.title("📊 Customer Churn & Retention Analysis")
st.markdown("Interactive EDA dashboard built with **Python + Streamlit**")

# Dataset preview
st.subheader("Dataset Preview")
st.dataframe(df.head())

# -------------------------------
# Churn Distribution
# -------------------------------
st.subheader("Churn Distribution")
fig, ax = plt.subplots()
sns.countplot(x="Exited", data=df, palette="Set2", ax=ax)
ax.set_title("Churn Distribution")
st.pyplot(fig)

# -------------------------------
# Age vs Churn
# -------------------------------
st.subheader("Age Distribution by Churn")
fig, ax = plt.subplots()
sns.histplot(
    df[df["Exited"] == 1]["Age"], bins=30, color="red", label="Churned", kde=True, ax=ax
)
sns.histplot(
    df[df["Exited"] == 0]["Age"],
    bins=30,
    color="green",
    label="Retained",
    kde=True,
    ax=ax,
)
ax.legend()
ax.set_title("Age Distribution by Churn")
st.pyplot(fig)

# -------------------------------
# Correlation Heatmap
# -------------------------------
st.subheader("Correlation Heatmap")
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(df.corr(), annot=False, cmap="coolwarm", ax=ax)
ax.set_title("Correlation Heatmap")
st.pyplot(fig)

# -------------------------------
# Churn Drivers
# -------------------------------
st.subheader("Churn Drivers")

# Active Member vs Churn
active_churn = df.groupby("IsActiveMember")["Exited"].mean()
st.write("**Churn Rate by Active Member:**")
st.bar_chart(active_churn)

# NumOfProducts vs Churn
product_churn = df.groupby("NumOfProducts")["Exited"].mean()
st.write("**Churn Rate by Number of Products:**")
st.bar_chart(product_churn)

# -------------------------------
# User Filters
# -------------------------------
st.subheader("Interactive Filters")
selected_age = st.slider(
    "Select Age Range", int(df["Age"].min()), int(df["Age"].max()), (20, 50)
)
filtered_df = df[(df["Age"] >= selected_age[0]) & (df["Age"] <= selected_age[1])]

st.write(
    f"Showing churn distribution for ages between {selected_age[0]} and {selected_age[1]}"
)
fig, ax = plt.subplots()
sns.countplot(x="Exited", data=filtered_df, palette="Set1", ax=ax)
st.pyplot(fig)
