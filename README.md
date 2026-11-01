# 🎬 Movie Recommendation System

Content-based recommender (genre + year + runtime, cosine similarity) with a personalised
"for a user" mode, built from `Movie_Recommendation_System.xlsx` and served with Streamlit.

## Files
| File | Purpose |
|---|---|
| `Movie_Recommendation_System.ipynb` | Steps 1–12: load → clean → features → similarity → recommend → save |
| `Movie_Recommendation_System.xlsx` | Dataset (Movies, Users, Ratings sheets) |
| `movies.pkl`, `similarity.pkl`, `ratings.pkl` | Saved model/data produced by the notebook |
| `app.py` | Streamlit app (step 13) |
| `requirements.txt` | Dependencies |

## 14. Run locally
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook Movie_Recommendation_System.ipynb   # optional: re-run to regenerate the .pkl files
streamlit run app.py                                 # opens http://localhost:8501
```

## 15. Deploy on Streamlit Community Cloud
1. Create a GitHub repo and push: `app.py`, `requirements.txt`, `movies.pkl`, `similarity.pkl`, `ratings.pkl`
   (plus the notebook and xlsx if you like).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app** → choose the repo, branch `main`, main file `app.py`.
4. Click **Deploy**. Every `git push` redeploys automatically.

## How it works
- **By movie:** genre one-hot + scaled year/runtime → cosine similarity → top-N most similar movies.
- **For a user:** average similarity to the movies the user rated ≥ 4 (weighted by rating), blended 85/15
  with a Bayesian-weighted average rating; already-seen movies are removed.
- Director isn't used: all 100 movies have a different director, so it can't connect any two of them.
- Each user has only 2 ratings, so classic user-to-user collaborative filtering is too sparse here.
  With more ratings per user, add it as a third signal.
