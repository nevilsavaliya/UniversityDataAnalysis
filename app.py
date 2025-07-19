import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.linear_model import LinearRegression
from flask_compress import Compress
app = Flask(__name__)
CORS(app)


@app.route("/analytics", methods=["GET"])
def get_analytics_summary():
    try:
        df = pd.read_csv("data/cleaned/university_data.csv")
        df = df.replace({True: 1, False: 0})

        # Calculate KPIs
        avg_student_staff_ratio = df["stats_student_staff_ratio"].mean(skipna=True)
        avg_international_students_pct = df["stats_pc_intl_students"].mean(skipna=True)

        universities_by_location = (
            df["location"].fillna("Unknown").value_counts().sort_index().to_dict()
        )

        teaching_score_by_year = (
            df.groupby("year")["scores_teaching"].mean().dropna().round(2).to_dict()
            if "year" in df.columns and "scores_teaching" in df.columns
            else {}
        )

        avg_number_of_students = pd.to_numeric(
            df["stats_number_students"]
            .astype(str)
            .str.replace(",", "", regex=False),
            errors="coerce"
        ).mean(skipna=True)

        avg_female_male_ratio = pd.to_numeric(
            df["stats_female_male_ratio"], errors="coerce"
        ).mean(skipna=True)

        avg_proportion_of_isr = df["stats_proportion_of_isr"].mean(skipna=True)

        # 📝 Only student stats + name
        student_stats_raw_data = (
            df[
                [
                    "name",
                    "stats_female_male_ratio",
                    "stats_proportion_of_isr",
                    "stats_number_students"
                ]
            ]
            .rename(columns={
                "name": "University Name",
                "stats_female_male_ratio": "Female:Male Ratio",
                "stats_proportion_of_isr": "Proportion of ISR",
                "stats_number_students": "Total Students"
            })
            .dropna(subset=["University Name"])
            .to_dict(orient="records")
        )

        return jsonify({
            "total_universities": len(df),
            "avg_student_staff_ratio": round(avg_student_staff_ratio, 2) if avg_student_staff_ratio else None,
            "avg_international_students_pct": round(avg_international_students_pct, 2) if avg_international_students_pct else None,
            "universities_by_location": universities_by_location,
            "teaching_score_by_year": teaching_score_by_year,
            "avg_number_of_students": round(avg_number_of_students, 2) if avg_number_of_students else None,
            "avg_female_male_ratio": round(avg_female_male_ratio, 2) if avg_female_male_ratio else None,
            "avg_proportion_of_isr": round(avg_proportion_of_isr * 100, 2) if avg_proportion_of_isr else None,
            "student_stats_raw_data": student_stats_raw_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/scatter_data", methods=["GET"])
def get_scatter_data():
    try:
        df = pd.read_csv("data/cleaned/university_data.csv")
        scatter_df = (
            df[["stats_student_staff_ratio", "scores_teaching", "location"]]
            .dropna()
            .rename(columns={
                "stats_student_staff_ratio": "Student-Staff Ratio",
                "scores_teaching": "Teaching Score",
                "location": "Location"
            })
        )
        if len(scatter_df) > 1000:
            scatter_df = scatter_df.sample(1000, random_state=42)

        return jsonify(scatter_df.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500



def predict_next_elements(sequence, n_predictions=4):
    sequence = np.array(sequence).flatten()
    n = len(sequence)
    X = np.arange(n).reshape(-1, 1)
    y = sequence
    model = LinearRegression()
    model.fit(X, y)
    next_indices = np.arange(n, n + n_predictions).reshape(-1, 1)
    predictions = model.predict(next_indices)

    return predictions.tolist()


label_encoders = joblib.load("models/label_encoders.pkl")
model = joblib.load("models/random_forest_model.pkl")
X_columns = joblib.load("models/X_columns.pkl")


@app.route("/predict_rank_by_name", methods=["POST"])
def predict_rank_by_name():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid request: JSON expected"}), 400

        input_data = request.get_json(force=True)
        university_name = input_data.get("university_name")

        if not university_name:
            return jsonify({"error": "University name missing"}), 400

        university_name = university_name.strip().lower()

        df = pd.read_csv("data/cleaned/university_data_rank.csv")
        df["name"] = df["name"].astype(str).str.strip().str.lower()
        df["location"] = df["location"].astype(str).str.strip().str.lower()
        df["aliases"] = df["aliases"].astype(str).str.strip().str.lower()

        uni_rows = df[df["name"] == university_name]
        if uni_rows.empty:
            return (
                jsonify(
                    {"error": "University not found", "university": university_name}
                ),
                404,
            )

        # Historical ranks
        historical_ranks = (
            uni_rows[["year", "rank"]]
            .dropna()
            .sort_values(by="year")
            .to_dict(orient="records")
        )

        # Prepare the latest row for one-year prediction
        latest_row = uni_rows.sort_values("year").iloc[-1:].copy()

        for col in ["location", "name"]:
            latest_row[col] = (
                latest_row[col].fillna("unknown").astype(str).str.strip().str.lower()
            )
            val = latest_row[col].iloc[0]
            if val not in label_encoders[col].classes_:
                label_encoders[col].classes_ = np.append(
                    label_encoders[col].classes_, val
                )
            latest_row[col] = label_encoders[col].transform(latest_row[col])

        latest_year = int(latest_row["year"].iloc[0])
        future_year = latest_year + 1
        latest_row["year"] = future_year

        X_input = latest_row[X_columns]
        predicted_rank = float(model.predict(X_input)[0])
        all_rank = [rank["rank"] for rank in historical_ranks]
        all_rank.append(int(predicted_rank))
        predicted_ranks = predict_next_elements(all_rank)
        ranks = [int(predicted_rank)]
        ranks.extend(predicted_ranks)
        result = {
            "all_ranks": ranks,
            "university": university_name,
            "historical_ranks": historical_ranks,
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict_rank_by_data", methods=["POST"])
def predict_rank_by_data():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid request: JSON expected"}), 400

        input_data = request.get_json(force=True)

        required_columns = [
            "name",
            "scores_overall",
            "scores_teaching",
            "scores_international_outlook",
            "scores_industry_income",
            "scores_research",
            "scores_citations",
            "location",
            "closed",
            "unaccredited",
            "year",
            "stats_number_students",
            "stats_student_staff_ratio",
            "stats_pc_intl_students",
            "stats_female_male_ratio",
            "stats_proportion_of_isr",
        ]

        subject_columns = [
            "subject_Accounting & Finance",
            "subject_Agriculture & Forestry",
            "subject_Archaeology",
            "subject_Architecture",
            "subject_Art",
            "subject_Biological Sciences",
            "subject_Business & Management",
            "subject_Chemical Engineering",
            "subject_Chemistry",
            "subject_Civil Engineering",
            "subject_Communication & Media Studies",
            "subject_Computer Science",
            "subject_Data Science",
            "subject_Earth & Marine Sciences",
            "subject_Economics & Econometrics",
            "subject_Education",
            "subject_Electrical & Electronic Engineering",
            "subject_Environmental",
            "subject_General Engineering",
            "subject_Geography",
            "subject_Geology",
            "subject_History",
            "subject_Languages",
            "subject_Law",
            "subject_Literature & Linguistics",
            "subject_Mathematics & Statistics",
            "subject_Mechanical & Aerospace Engineering",
            "subject_Medicine & Dentistry",
            "subject_Other Health",
            "subject_Performing Arts & Design",
            "subject_Philosophy",
            "subject_Philosophy & Theology",
            "subject_Physics & Astronomy",
            "subject_Politics & International Studies (incl Development Studies)",
            "subject_Psychology",
            "subject_Sociology",
            "subject_Sport Science",
            "subject_Veterinary Science",
        ]

        row_dict = {col: input_data.get(col, np.nan) for col in required_columns}

        studying_subjects = set(
            s.lower() for s in input_data.get("subjects_studying", [])
        )

        for subject in subject_columns:
            short_name = subject.replace("subject_", "").lower()
            row_dict[subject] = 1 if short_name in studying_subjects else 0

        input_df = pd.DataFrame([row_dict])

        for col in ["name", "location", "aliases"]:
            if col in input_df:
                val = str(input_df.at[0, col]).strip().lower()
                le = label_encoders[col]
                if val not in le.classes_:
                    le.classes_ = np.append(le.classes_, val)
                input_df[col] = le.transform([val])[0]

        input_df = input_df.fillna(0)

        X_input = input_df[X_columns].copy()
        start_year = int(input_data.get("year", 2024))
        predictions = []

        feature_importances = dict(zip(X_columns, model.feature_importances_))
        max_importance = max(feature_importances.values())

        base_improvement = 0.9993  # base factor for highest importance
        improvements = {}

        for col in ["scores_teaching", "scores_overall", "scores_research"]:
            importance = feature_importances.get(col, 0)
            weight = importance / max_importance if max_importance > 0 else 0
            # More important → closer to base_improvement; less important → closer to 1.0
            improvements[col] = 1.0 - ((1.0 - base_improvement) * weight)

        for i in range(4):
            current_year = start_year + i
            X_input.loc[:, "year"] = current_year
            predicted_rank = float(model.predict(X_input)[0])
            predictions.append(
                {
                    "year": current_year,
                    "predicted_rank": predicted_rank,
                    "university": input_data.get("name", ""),
                }
            )
            for col, factor in improvements.items():
                X_input[col] *= factor

        return jsonify({"predictions": predictions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
