import json
import sqlite3
from collections import Counter
import textwrap

import pandas as pd
import numpy as np
import streamlit as st

import plotly.express as px
import plotly.graph_objects as go

DEFAULT_DB = "./artifacts/tasks.db"
EMBEDDINGS = "./data/interim/embeddings2d.npy"
CLUSTERS = "./data/interim/id_cluster.csv"
TOP_WORDS = "./data/interim/top_words_kmeans.json"

KMEANS_ACC = "./data/interim/kmeans_acc.json"
DBSCAN_ACC = "./data/interim/dbscan_acc.json"


def get_cmap(labels):
    default_colorscale = px.colors.cyclical.IceFire_r
    colors = px.colors.sample_colorscale(default_colorscale, len(labels))
    colors = {i: color for i, color in zip(labels, colors)}

    return colors


# Connect to the SQLite database
def wrap_text(text, max_length=50):
    # Replace \n with <br>
    text = text.replace("\n", "<br>")
    # Wrap text at word boundaries
    wrapped_lines = textwrap.wrap(text, width=max_length)
    return "<br>".join(wrapped_lines)


# Function to create the interactive plot
def create_interactive_plot(data, embeddings_2d, labels, most_common_words):
    unique_labels = np.unique(labels)

    if len(unique_labels) == 1:
        colors = {unique_labels[0]: "Blue"}
    else:
        colors = get_cmap(unique_labels)
        
    fig = go.Figure()
    fig.update_layout(width=1000, height=1000)

    # Add cluster centroids
    for label in unique_labels:
        cluster_points = embeddings_2d[labels == label]
        centroid = np.mean(cluster_points, axis=0)

        fig.add_trace(
            go.Scatter(
                x=[centroid[0]],
                y=[centroid[1]],
                mode="markers+text",
                text=f"C{label}",
                textposition="top center",
                marker=dict(size=10, color=colors[label], opacity=1),
                textfont=dict(color=colors[label]),
                name=f"C{label}",
            )
        )

        # Add cluster points (initially hidden)
        fig.add_trace(
            go.Scatter(
                x=cluster_points[:, 0],
                y=cluster_points[:, 1],
                mode="markers",
                hovertext=data[labels == label]["content"]
                .apply(wrap_text)
                .tolist(),
                marker=dict(
                    size=5,
                    color=colors[label],
                    opacity=0.2,
                    line=(
                        dict(width=2, color="DarkSlateGrey")
                        if label < 0
                        else None
                    ),
                ),
                name=f"C{label} Points",
                visible=True,  # Initially hidden
                # legend=False,
            )
        )

        # Add most common words (initially hidden)
        words = most_common_words.get(label, [])
        off_xs, off_ys = [], []

        for i in range(len(words)):
            angle = 2 * np.pi * i / len(words)
            offset_x = 10 * np.cos(angle)
            offset_y = 10 * np.sin(angle)
            off_xs.append(offset_x)
            off_ys.append(offset_y)

        fig.add_trace(
            go.Scatter(
                x=[centroid[0] + offset_x for offset_x in off_xs],
                y=[centroid[1] + offset_y for offset_y in off_ys],
                mode="text",
                text=words,
                textposition="middle center",
                name=f"C{label} words",
                visible="legendonly",  # Initially hidden
            )
        )

    # Update layout
    fig.update_layout(
        title="Interactive TSNE Cluster Visualization",
        showlegend=True,
        legend=dict(
            x=1,
            y=1,
            traceorder="normal",
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2,
        ),
    )

    # Add click event to show/hide cluster points and words
    fig.update_traces(selector=dict(mode="markers+text"))
    fig.update_layout(plot_bgcolor="white")

    return fig


def accuracy_plot(kmeans_accuracy: dict, dbscan_accuracy: dict):
    tags = list(kmeans_accuracy.keys())
    kmeans_values = list(kmeans_accuracy.values())
    dbscan_values = [dbscan_accuracy[tag] for tag in tags]

    # Create a bar chart
    fig = go.Figure()

    # Add KMeans accuracy bars
    fig.add_trace(
        go.Bar(
            x=tags,
            y=kmeans_values,
            name="KMeans Accuracy",
            marker_color="indianred",
        )
    )

    # Add DBSCAN accuracy bars
    fig.add_trace(
        go.Bar(
            x=tags,
            y=dbscan_values,
            name="DBSCAN Accuracy",
            marker_color="lightsalmon",
        )
    )

    # Update layout
    fig.update_layout(
        title="Clusterization Accuracy Comparison",
        xaxis_title="Tags",
        yaxis_title="Accuracy",
        barmode="group",
        legend_title="Algorithm",
    )

    return fig


def read_db(path: str, clusters_cache: str):
    conn = sqlite3.connect("./artifacts/tasks.db")

    # Query the data
    query = "SELECT * FROM tasks"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["tags"] = df["tags"].apply(json.loads)
    df["tags"] = df["tags"].apply(lambda x: [t[:5] for t in x[0]])

    df["content"] = df["task_text"].apply(lambda x: x + "\n")
    df["content"] = df["content"] + df["options"]

    clusters = pd.read_csv(clusters_cache)

    df = df.merge(
        right=clusters,
        how="left",
        left_on="id",
        right_on="id",
        suffixes=("", ""),
    )

    return df


def read_json(fp):
    with open(fp, "r") as f:
        d = json.load(f)

    return d


def main():
    df = read_db(DEFAULT_DB, CLUSTERS)

    # Sidebar for filtering
    st.sidebar.title("Filters")
    answer_type_filter = st.sidebar.multiselect(
        "Select Answer Types",
        options=df["answer_type"].unique(),
        default=df["answer_type"].unique(),
    )

    # Filter the dataframe based on the selected answer types
    filtered_index = df["answer_type"].isin(answer_type_filter)
    filtered_df = df[filtered_index]

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
        xaxis_title="Length",
        yaxis_title="Frequency",
        legend_title="Content Type",
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
            z=cooccurrence_df.pivot(
                index="Tag1", columns="Tag2", values="Count"
            ).fillna(0),
            x=cooccurrence_df["Tag2"].unique(),
            y=cooccurrence_df["Tag1"].unique(),
            colorscale="Viridis",
        )
    )

    fig_tag_cooccurrence.update_layout(title="Tag Co-occurrence")
    st.plotly_chart(fig_tag_cooccurrence)

    # Display the cluster plot
    st.header("Cluster Plot")
    embeddings_2d = np.load(EMBEDDINGS)[filtered_index]
    top_words = read_json(TOP_WORDS)
    cluster_plot = create_interactive_plot(
        filtered_df, embeddings_2d, filtered_df["cluster"], top_words
    )
    st.plotly_chart(cluster_plot)

    st.header("Cluster Accuracy")
    kmeans_acc = read_json(KMEANS_ACC)
    dbscan_acc = read_json(DBSCAN_ACC)
    acc_plot = accuracy_plot(kmeans_acc, dbscan_acc)
    st.plotly_chart(acc_plot)


if __name__ == "__main__":
    main()
