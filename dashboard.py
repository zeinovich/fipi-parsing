import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import pandas as pd
from collections import Counter
import json

# Connect to the SQLite database
conn = sqlite3.connect("./artifacts/tasks.db")

# Query the data
query = "SELECT * FROM tasks"
df = pd.read_sql_query(query, conn)

# Convert tags from JSON string to list
df["tags"] = df["tags"].apply(json.loads)
df["tags"] = df["tags"].apply(lambda x: [t[:5] for t in x[0]])

# Sidebar for filtering
st.sidebar.title("Filters")
answer_type_filter = st.sidebar.multiselect(
    "Select Answer Types",
    options=df["answer_type"].unique(),
    default=df["answer_type"].unique(),
)

# Filter the dataframe based on the selected answer types
filtered_df = df[df["answer_type"].isin(answer_type_filter)]

# Tag Distribution
st.title("Task Data Dashboard")
st.header("Tag Distribution")

# Flatten the tags list
all_tags = [tag for sublist in filtered_df["tags"] for tag in sublist]
tag_counts = Counter(all_tags)

# Create a bar chart for tag distribution
tag_df = pd.DataFrame(tag_counts.items(), columns=["Tag", "Count"])
fig_tag_distribution = px.bar(
    tag_df, x="Tag", y="Count", title="Tag Distribution"
)
st.plotly_chart(fig_tag_distribution)

# Answer Type Distribution
st.header("Answer Type Distribution")
answer_type_counts = filtered_df["answer_type"].value_counts()
fig_answer_type_distribution = px.pie(
    answer_type_counts,
    values=answer_type_counts.values,
    names=answer_type_counts.index,
    title="Answer Type Distribution",
)
st.plotly_chart(fig_answer_type_distribution)

# Task Content Length Distribution
st.header("Task Content Length Distribution")
filtered_df["task_text_length"] = filtered_df["task_text"].apply(len)
filtered_df["options_length"] = filtered_df["options"].apply(len)

# Create a histogram for task_text and options length distribution
fig_content_length_distribution = px.histogram(
    filtered_df,
    x=["task_text_length", "options_length"],
    barmode="overlay",
    title="Task Content Length Distribution",
    labels={"value": "Length", "variable": "Content Type"},
)

# Update layout for better readability
fig_content_length_distribution.update_layout(
    xaxis_title="Length", yaxis_title="Frequency", legend_title="Content Type"
)
st.plotly_chart(fig_content_length_distribution)

# Tag Co-occurrence
st.header("Tag Co-occurrence")
tag_cooccurrence = Counter()
for tags in filtered_df["tags"]:
    for i in range(len(tags)):
        for j in range(i + 1, len(tags)):
            tag_cooccurrence[(tags[i], tags[j])] += 1

cooccurrence_df = pd.DataFrame(
    tag_cooccurrence.items(), columns=["Tags", "Count"]
)
cooccurrence_df[["Tag1", "Tag2"]] = pd.DataFrame(
    cooccurrence_df["Tags"].tolist(), index=cooccurrence_df.index
)

fig_tag_cooccurrence = go.Figure(
    data=go.Heatmap(
        z=cooccurrence_df.pivot(index="Tag1", columns="Tag2", values="Count").fillna(0),
        x=cooccurrence_df["Tag2"].unique(),
        y=cooccurrence_df["Tag1"].unique(),
        colorscale="Viridis",
    )
)

fig_tag_cooccurrence.update_layout(title="Tag Co-occurrence")
st.plotly_chart(fig_tag_cooccurrence)

# Display the cluster plot
st.header("Cluster Plot")
st.components.v1.html(open("./artifacts/clusters_kmeans.html").read(), height=1000, width=1000)

# Close the database connection
conn.close()
