import streamlit as st
import pandas as pd
import joblib

# Load the trained model
model = joblib.load('ipl_win_model.pkl')

st.title('IPL Win Probability Predictor')
st.markdown("Enter the current match situation to get real-time win probabilities.")

# User Inputs
col1, col2 = st.columns(2)

with col1:
    target = st.number_input('Target Score', min_value=1, max_value=300, value=160)
    current_score = st.number_input('Current Score', min_value=0, max_value=target, value=75)
    wickets_so_far = st.slider('Wickets Fallen', min_value=0, max_value=9, value=2)

with col2:
    total_match_overs = st.number_input('Total Match Overs (Adjust for rain)', min_value=1, max_value=20, value=20)
    overs_done = st.number_input('Overs Completed', min_value=0.0, max_value=float(total_match_overs), value=8.0, step=0.1)

# Predict Button & Background Calculations
if st.button('Predict Win Probability'):
    
    # Calculate Runs Required
    runs_required = target - current_score
    if runs_required < 0:
        runs_required = 0

    # Calculate Balls Bowled from cricket over notation 
    completed_overs = int(overs_done)
    balls_in_current_over = int(round((overs_done - completed_overs) * 10))
    balls_bowled = (completed_overs * 6) + balls_in_current_over
    
    # Calculate Balls Remaining
    total_match_balls = total_match_overs * 6
    balls_remaining = total_match_balls - balls_bowled
    if balls_remaining < 0:
        balls_remaining = 0

    # Calculate Run Rates
    # Protect against divide-by-zero errors on the very first ball or last ball
    overs_bowled_math = balls_bowled / 6
    overs_remaining_math = balls_remaining / 6
    
    current_run_rate = (current_score / overs_bowled_math) if overs_bowled_math > 0 else 0
    required_run_rate = (runs_required / overs_remaining_math) if overs_remaining_math > 0 else 0
    run_rate_diff = current_run_rate - required_run_rate
    
    # Model Prediction

    input_data = pd.DataFrame([{
        'total_runs_so_far': current_score,
        'wickets_so_far': wickets_so_far,  # Change to 'wickets_in_hand' and pass (10 - wickets_so_far) if you kept that change!
        'balls_remaining': balls_remaining,
        'runs_required': runs_required,
        'current_run_rate': current_run_rate,
        'required_run_rate': required_run_rate,
        'run_rate_diff': run_rate_diff
    }])
    
    # Get probability for Class 1 (Win)
    win_prob = model.predict_proba(input_data)[0][1]
    loss_prob = 1 - win_prob
    
    # Display Results
    st.markdown("---")
    st.subheader("Match Projections")
    
    # Display the derived stats so the user can verify them
    st.write(f"**Runs Required:** {runs_required} off {balls_remaining} balls")
    st.write(f"**CRR:** {current_run_rate:.2f} | **RRR:** {required_run_rate:.2f}")
    st.write("")
    
    # Display Probabilities
    st.write(f"**Chasing Team Win Probability:** {win_prob * 100:.1f}%")
    st.write(f"**Defending Team Win Probability:** {loss_prob * 100:.1f}%")
    st.progress(float(win_prob))