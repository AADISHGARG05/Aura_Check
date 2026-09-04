import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
SCRIPTS_DIR = BASE_DIR / "Scripts"

SCHEMA_JSON = SCRIPTS_DIR / "onehot_columns_full.json"
SCHEMA_PKL = SCRIPTS_DIR / "onehot_columns.pkl"
TARGET_COLUMNS = {"depression_score", "anxiety_score", "stress_score"}

MODEL_PATHS = {
    "stress": MODELS_DIR / "xgc_model1_stress.pkl",
    "anxiety": MODELS_DIR / "xgc_model1_anxiety.pkl",
    "depression": MODELS_DIR / "xgc_model1_depression.pkl",
}

NUMERIC_FIELDS = (
    [f"Q{i}A" for i in range(1, 43)]
    + [f"TIPI{i}" for i in range(1, 11)]
    + [f"VCL{i}" for i in range(1, 17)]
    + ["education", "urban", "gender", "engnat", "age", "hand", "religion",
       "orientation", "race", "voted", "married", "familysize"]
)

DEFAULTS = {
    "education": 3, "urban": 2, "gender": 3, "engnat": 1, "age": 21,
    "hand": 1, "religion": 12, "orientation": 1, "race": 10,
    "voted": 2, "married": 1, "familysize": 4,
}


def _load_feature_columns():
    if SCHEMA_JSON.exists():
        payload = json.loads(SCHEMA_JSON.read_text(encoding="utf-8"))
        columns = payload["columns"]
    else:
        with open(SCHEMA_PKL, "rb") as file:
            columns = list(pickle.load(file))

    # The three score columns are training targets, not inference inputs.
    feature_columns = [column for column in columns if column not in TARGET_COLUMNS]
    if len(feature_columns) != 5393:
        raise ValueError(f"Expected 5393 model features, found {len(feature_columns)}")
    return feature_columns


FEATURE_COLUMNS = _load_feature_columns()


def _number(payload, field, minimum, maximum, default=None):
    raw = payload.get(field, default)
    if raw is None or str(raw).strip() == "":
        raise ValueError(f"Missing required field: {field}")
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid value for {field}") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")
    return value


def preprocess(payload):
    row = {}

    for i in range(1, 43):
        row[f"Q{i}A"] = _number(payload, f"Q{i}A", 1, 4)
    for i in range(1, 11):
        row[f"TIPI{i}"] = _number(payload, f"TIPI{i}", 1, 7)
    for i in range(1, 17):
        row[f"VCL{i}"] = _number(payload, f"VCL{i}", 0, 1)

    row["education"] = _number(payload, "education", 1, 4, DEFAULTS["education"])
    row["urban"] = _number(payload, "urban", 1, 3, DEFAULTS["urban"])
    row["gender"] = _number(payload, "gender", 1, 3, DEFAULTS["gender"])
    row["engnat"] = _number(payload, "engnat", 1, 2, DEFAULTS["engnat"])
    row["age"] = _number(payload, "age", 13, 100, DEFAULTS["age"])
    row["hand"] = _number(payload, "hand", 1, 3, DEFAULTS["hand"])
    row["religion"] = _number(payload, "religion", 1, 12, DEFAULTS["religion"])
    row["orientation"] = _number(payload, "orientation", 1, 5, DEFAULTS["orientation"])
    row["race"] = _number(payload, "race", 10, 70, DEFAULTS["race"])
    row["voted"] = _number(payload, "voted", 1, 2, DEFAULTS["voted"])
    row["married"] = _number(payload, "married", 1, 3, DEFAULTS["married"])
    row["familysize"] = _number(payload, "familysize", 1, 30, DEFAULTS["familysize"])

    row["extraversion"] = row["TIPI1"] - row["TIPI6"]
    row["agreeableness"] = row["TIPI7"] - row["TIPI2"]
    row["conscientiousness"] = row["TIPI3"] - row["TIPI8"]
    row["emotional_stability"] = row["TIPI9"] - row["TIPI4"]
    row["openness"] = row["TIPI5"] - row["TIPI10"]

    major = str(payload.get("major", "")).strip()
    frame = pd.DataFrame([row])
    encoded = pd.get_dummies(frame)

    major_column = f"major_{major}"
    if major and major_column in FEATURE_COLUMNS:
        encoded[major_column] = 1

    encoded = encoded.reindex(columns=FEATURE_COLUMNS, fill_value=0).astype(float)
    if encoded.shape != (1, 5393):
        raise ValueError(f"Invalid model input shape: {encoded.shape}")
    return encoded.to_numpy(dtype=np.float32)


def _label(value):
    value = int(value)
    if value <= 1:
        return "Low"
    if value == 2:
        return "Moderate"
    return "High"


def predict_all(payload):
    features = preprocess(payload)
    labels = {}

    for name, model_path in MODEL_PATHS.items():
        with open(model_path, "rb") as file:
            model = pickle.load(file)
        expected = int(model.n_features_in_)
        if expected != features.shape[1]:
            raise ValueError(
                f"{name.title()} model expects {expected} features, "
                f"but preprocessing produced {features.shape[1]}"
            )
        labels[name] = _label(model.predict(features)[0])

    severity_class = {
        "Low": "low", "Moderate": "moderate", "High": "high"
    }[labels["stress"]]
    return {**labels, "severity_class": severity_class}
