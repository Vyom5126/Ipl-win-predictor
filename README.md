# IPL Win Probability Predictor

A ball-by-ball win probability model for IPL second innings chases - deployed as a live Streamlit web app. Enter the current match situation and get an instant win probability for the chasing team, similar to what Cricbuzz and Hotstar show during a live match.

*[Live App →](https://vd-ipl-win-predictor.streamlit.app/)* 

---

## What It Does

Given a mid-game match situation in the second innings - current score, wickets fallen, overs completed, and target - the model predicts the probability that the chasing team wins. Two models were trained and compared; the better-performing one was selected for deployment.

Sample output:
```
CSK chasing 180 | 120/3 after 14 overs
→ Chasing Team Win Probability: 62%
```

---

## Project Structure

```
ipl-win-probability/
│
├── ipl_json/                  # Raw ball-by-ball JSON files from Cricsheet (not tracked in git)
├── ipl_extractor.py           # Parses JSON files → flat CSV
├── ipl_balls.csv              # Processed ball-by-ball dataset (not tracked in git)
├── ipl_predictor.ipynb        # Full ML pipeline: EDA, feature engineering, training, evaluation
├── ipl_win_model.pkl          # Saved trained model (Logistic Regression)
├── app.py                     # Streamlit web app
├── requirements.txt           # Python dependencies
└── README.md
```

---

## How It Was Built

### Phase 1 — Data
Ball-by-ball IPL match data was downloaded from [Cricsheet.org](https://cricsheet.org) in JSON format, covering IPL seasons from 2008 onwards (~900+ matches).

### Phase 2 — Parsing
`ipl_extractor.py` parses each JSON match file and outputs a flat CSV with one row per ball, including cumulative match state fields like running score, wickets fallen, balls bowled, and target.

### Phase 3 — Feature Engineering
Only second innings rows were retained (chasing scenario). A binary target column `batting_team_won` was created. The following features were engineered:

| Feature | Description |
|---|---|
| `total_runs_so_far` | Runs scored by chasing team so far |
| `wickets_so_far` | Wickets lost so far |
| `balls_remaining` | Legal balls left in the innings |
| `runs_required` | Runs still needed to win |
| `current_run_rate` | Runs per over scored so far |
| `required_run_rate` | Runs per over needed from here |
| `run_rate_diff` | CRR minus RRR (positive = advantage chasing) |

### Phase 4 — Model Training
Train/test split was done at the **match level** (not row level) to prevent data leakage - entire matches are assigned to either train or test, never split across both.

Two models were trained and compared:

| Model | Accuracy | Log Loss |
|---|---|---|
| Logistic Regression | 76.70% | 0.4786 |
| XGBoost | 75.06% | 0.4971 |

**Logistic Regression was selected for deployment** - it outperformed XGBoost on both metrics, which is expected given the features are largely linear in nature (run rate differential, resources remaining).

### Phase 5 — Deployment
Model serialized with `joblib` and deployed via Streamlit Community Cloud.

---

## Win Probability Progression (Sample Match)

The chart below shows how win probability evolved ball-by-ball for a sample match from the test set. Probability dips on wickets and rises with boundaries - exactly like live broadcast overlays.


---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/Vyom5126/Ipl-win-probability.git
cd ipl-win-probability

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

To retrain the model from scratch, download the IPL JSON dataset from [Cricsheet.org](https://cricsheet.org/downloads/), place the files in an `ipl_json/` folder, run `ipl_extractor.py` to generate `ipl_balls.csv`, and then run `ipl_predictor.ipynb` top to bottom.

---

## Dependencies

```
streamlit
pandas
numpy
scikit-learn
xgboost
joblib
matplotlib
```

---

## Planned Improvements

- Add head-to-head historical win % between the two teams as a feature
- Add venue-level mean encoding (some grounds heavily favour chasing)
- Extend to first innings with a projected score model
- Probability calibration using Platt scaling to reduce overconfidence

---

## Data Source

[Cricsheet.org](https://cricsheet.org) — free, open ball-by-ball cricket data. No scraping required.

---

