import pickle
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")


@st.cache_data
def load():
    movies = pickle.load(open("movies.pkl", "rb"))
    sim = pickle.load(open("similarity.pkl", "rb"))
    ratings = pickle.load(open("ratings.pkl", "rb"))
    return movies, sim, ratings


movies, similarity, ratings = load()
COLS = {"avg_rating": "Avg ★", "n_ratings": "# Ratings", "Duration": "Min"}


def recommend_by_movie(title, n=5, genre=None):
    i = movies.index[movies["Title"] == title][0]
    s = pd.Series(similarity[i], index=movies.index).drop(i)
    if genre:
        s = s[movies.loc[s.index, "Genre"] == genre]
    wr = movies.loc[s.index, "weighted_rating"]
    order = pd.DataFrame({"sim": s, "wr": wr}).sort_values(["sim", "wr"], ascending=False).head(n)
    out = movies.loc[order.index, ["Title", "Genre", "Year", "Duration", "avg_rating", "n_ratings"]].copy()
    out.insert(1, "Match %", (order["sim"] * 100).round(1).values)
    return out.rename(columns=COLS).reset_index(drop=True)


def recommend_for_user(user_id, n=5, liked_min=4, alpha=0.85):
    mine = ratings[ratings["UserID"] == user_id]
    liked = mine[mine["Rating"] >= liked_min]
    if liked.empty:
        liked = mine[mine["Rating"] == mine["Rating"].max()]
    rows = movies.index[movies["MovieID"].isin(liked["MovieID"])]
    w = liked.set_index("MovieID").loc[movies.loc[rows, "MovieID"], "Rating"].values
    content = (similarity[rows] * w[:, None]).sum(axis=0) / w.sum()
    score = alpha * content + (1 - alpha) * movies["weighted_rating"].values / 5
    score = pd.Series(score, index=movies.index).drop(movies.index[movies["MovieID"].isin(mine["MovieID"])])
    top = score.sort_values(ascending=False).index[:n]
    out = movies.loc[top, ["Title", "Genre", "Year", "avg_rating", "n_ratings"]].copy()
    out.insert(1, "Score", (score[top] * 100).round(1).values)
    return out.rename(columns=COLS).reset_index(drop=True)


st.title("🎬 Movie Recommendation System")
st.caption("Content-based (genre, year, runtime) with a rating-quality boost for personalised picks.")

tab1, tab2, tab3 = st.tabs(["🎞️ By movie", "👤 For a user", "📊 Explore"])

with tab1:
    c1, c2, c3 = st.columns([3, 1, 2])
    title = c1.selectbox("Pick a movie you like", sorted(movies["Title"]))
    n = c2.slider("How many?", 3, 15, 5, key="n1")
    genre = c3.selectbox("Limit to genre", ["Any"] + sorted(movies["Genre"].unique()))
    row = movies[movies["Title"] == title].iloc[0]
    st.write(f"**{row.Title}** · {row.Genre} · {row.Year} · {row.Duration} min · directed by {row.Director}")
    if st.button("Recommend", type="primary"):
        res = recommend_by_movie(title, n, None if genre == "Any" else genre)
        if res.empty:
            st.warning("No other movies match that genre filter.")
        else:
            st.dataframe(res, hide_index=True, width='stretch')

with tab2:
    uid = st.selectbox("User ID", sorted(ratings["UserID"].unique()))
    n2 = st.slider("How many?", 3, 15, 5, key="n2")
    seen = ratings[ratings["UserID"] == uid].merge(movies[["MovieID", "Title", "Genre"]], on="MovieID")
    st.write("**Rated so far**")
    st.dataframe(seen[["Title", "Genre", "Rating"]], hide_index=True, width='stretch')
    st.write("**Recommended for this user**")
    st.dataframe(recommend_for_user(uid, n2), hide_index=True, width='stretch')

with tab3:
    a, b = st.columns(2)
    a.write("**Movies per genre**")
    a.bar_chart(movies["Genre"].value_counts())
    b.write("**Ratings distribution**")
    b.bar_chart(ratings["Rating"].value_counts().sort_index())
    st.write("**Top rated** (weighted, so one lucky 5★ doesn't win)")
    top = movies.sort_values("weighted_rating", ascending=False).head(10)
    st.dataframe(top[["Title", "Genre", "Year", "avg_rating", "n_ratings"]].rename(columns=COLS), hide_index=True, width='stretch')
