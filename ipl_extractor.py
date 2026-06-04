import os
import json
import csv

def is_legal_ball(delivery):
    extras = delivery.get("extras", {})
    if "wides" in extras or "noballs" in extras:
        return False
    else:
        return True

def get_extra_runs(delivery, extra_type):
    extras = delivery.get("extras", {})
    if extra_type in extras:
        return extras[extra_type]
    else:
        return 0

# MAIN PROCESSING FUNCTION

def process_single_match(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    info = data.get("info", {})
    innings = data.get("innings", [])

    if not info or not innings:
        return []

    match_id = os.path.basename(filepath).replace(".json", "")
    
    teams = info.get("teams", [])
    if len(teams) == 2:
        team1 = teams[0]
        team2 = teams[1]
    else:
        team1 = ""
        team2 = ""


    outcome = info.get("outcome", {})
    if "winner" in outcome:
        match_winner = outcome["winner"]
    elif "result" in outcome:
        match_winner = outcome["result"]
    else:
        match_winner = "no result"

    first_innings_total = 0
    if len(innings) > 0:
        first_innings_data = innings[0]
        for over in first_innings_data.get("overs", []):
            for delivery in over.get("deliveries", []):
                runs_scored = delivery.get("runs", {}).get("total", 0)
                first_innings_total = first_innings_total + runs_scored
    
    target_score = first_innings_total + 1

    # Loop through the innings, overs, and balls
    all_rows_for_this_match = []

    for inning_index, inning_data in enumerate(innings):
        inning_number = inning_index + 1
        batting_team = inning_data.get("team", "")
        
        if batting_team == team1:
            bowling_team = team2
        else:
            bowling_team = team1

        cumulative_runs = 0
        cumulative_wickets = 0
        legal_balls_bowled = 0 

        for over in inning_data.get("overs", []):
            over_number = over.get("over", 0) + 1 

            # Loop through every ball in the over
            for ball_number, delivery in enumerate(over.get("deliveries", []), start=1):
                
                # Get Runs
                runs_info = delivery.get("runs", {})
                total_runs_this_ball = runs_info.get("total", 0)
                
                # Get Wickets
                wickets_list = delivery.get("wickets", [])
                if len(wickets_list) > 0:
                    is_wicket = 1
                else:
                    is_wicket = 0

                # Update the totals
                cumulative_runs = cumulative_runs + total_runs_this_ball
                cumulative_wickets = cumulative_wickets + is_wicket
                
                if is_legal_ball(delivery):
                    legal_balls_bowled = legal_balls_bowled + 1

                runs_required = ""
                balls_remaining = ""
                current_run_rate = ""
                required_run_rate = ""

                if inning_number == 2:
                    runs_required = target_score - cumulative_runs
                    if runs_required < 0:
                        runs_required = 0 
                    
                    balls_remaining = 120 - legal_balls_bowled
                    if balls_remaining < 0:
                        balls_remaining = 0

                    # Run Rate
                    if legal_balls_bowled > 0:
                        overs_bowled = legal_balls_bowled / 6
                        current_run_rate = round(cumulative_runs / overs_bowled, 2)
                    else:
                        current_run_rate = 0.0

                    # Required Run Rate
                    overs_left = balls_remaining / 6
                    if overs_left > 0:
                        required_run_rate = round(runs_required / overs_left, 2)
                    else:
                        required_run_rate = 999.99 # Prevent dividing by zero

                #  Create a dictionary 
                row = {
                    "match_id": match_id,
                    "date": info.get("dates", [""])[0],
                    "team1": team1,
                    "team2": team2,
                    "batting_team": batting_team,
                    "bowling_team": bowling_team,
                    "inning": inning_number,
                    "over": over_number,
                    "ball_in_over": ball_number,
                    "batter": delivery.get("batter", ""),
                    "bowler": delivery.get("bowler", ""),
                    "total_runs_ball": total_runs_this_ball,
                    "wides": get_extra_runs(delivery, "wides"),
                    "noballs": get_extra_runs(delivery, "noballs"),
                    "is_wicket": is_wicket,
                    "total_runs_so_far": cumulative_runs,
                    "wickets_so_far": cumulative_wickets,
                    "legal_balls_bowled": legal_balls_bowled,
                    "target": target_score if inning_number == 2 else "",
                    "runs_required": runs_required,
                    "balls_remaining": balls_remaining,
                    "current_run_rate": current_run_rate,
                    "required_run_rate": required_run_rate,
                    "match_winner": match_winner
                }
                
                all_rows_for_this_match.append(row)

    return all_rows_for_this_match


if __name__ == "__main__":
    input_directory = "./ipl_json"
    output_csv_file = "ipl_balls.csv"

    # List to hold every row from every match
    complete_data_list = []

    for filename in os.listdir(input_directory):
        if filename.endswith(".json"):
            full_path = os.path.join(input_directory, filename)
            
            print(f"Processing: {filename}")
            
            # Process the file and get its rows
            match_rows = process_single_match(full_path)
            
            # Add the rows to complete list
            complete_data_list.extend(match_rows)

    if len(complete_data_list) > 0:
        print(f"\nWriting {len(complete_data_list)} rows to {output_csv_file}...")
        
        with open(output_csv_file, "w", newline="", encoding="utf-8") as file:
            column_headers = list(complete_data_list[0].keys())
            
            writer = csv.DictWriter(file, fieldnames=column_headers)
            writer.writeheader()
            
            for row in complete_data_list:
                writer.writerow(row)
                
        print("✅ Success! CSV file created.")
    else:
        print("❌ No data was found. Please check your input folder.")