import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd
import pickle
import requests
from io import BytesIO
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
SCRIPTS_DIR = BASE_DIR / "Scripts"

model1 = pickle.load(open(MODELS_DIR / "xgc_model1_depression.pkl", "rb"))
model2 = pickle.load(open(MODELS_DIR / "xgc_model1_anxiety.pkl", "rb"))
model3 = pickle.load(open(MODELS_DIR / "xgc_model1_stress.pkl", "rb"))

with open(SCRIPTS_DIR / "onehot_columns1.pkl", "rb") as f:
    onehot_columns = pickle.load(f)


def score(colname: str, data: pd.DataFrame) -> pd.DataFrame:
    for index, i in enumerate(data[colname]):
        if i <= 9:
            data.loc[index, colname] = 1
        elif 9 < i <= 13:
            data.loc[index, colname] = 2
        elif 13 < i <= 20:
            data.loc[index, colname] = 3
        elif 20 < i <= 27:
            data.loc[index, colname] = 4
        else:
            data.loc[index, colname] = 5
    return data[colname]

depression_questions = ["Q3A","Q5A","Q10A","Q13A","Q16A","Q17A","Q21A","Q24A","Q26A","Q31A","Q34A","Q37A","Q38A","Q42A"]
anxiety_questions = ["Q2A","Q4A","Q7A","Q9A","Q15A","Q19A","Q20A","Q23A","Q25A","Q28A","Q30A","Q36A","Q40A","Q41A"]
stress_questions = ["Q1A","Q6A","Q8A","Q11A","Q12A","Q14A","Q18A","Q22A","Q27A","Q29A","Q32A","Q33A","Q35A","Q39A"]

words = ["VCL1","VCL2","VCL3","VCL4","VCL5","VCL7","VCL8","VCL10","VCL11","VCL13","VCL14","VCL15","VCL16"]


def main():
    onedrive_url = "https://bennettu-my.sharepoint.com/personal/e23cseu0615_bennett_edu_in/_layouts/15/download.aspx?share=EQLLM6GDZKVHli4aSWFVGccB587D3Qpr40bJZlQA9NoxGA"
    response = requests.get(onedrive_url)

    if response.status_code != 200:
        raise Exception("Failed to load input data")

    data = pd.read_excel(BytesIO(response.content))

    qa = [c for c in data.columns if c.startswith("Q") and c.endswith("A")]
    for q in qa:
        data[q] = int(data[q][0][-1])

    reversed_dict = {
        "Disagree strongly": 1,
        "Disagree moderately": 2,
        "Disagree a little": 3,
        "Neither agree nor disagree": 4,
        "Agree a little": 5,
        "Agree moderately": 6,
        "Agree strongly": 7
    }

    for col in data.columns:
        if col.startswith("TIP"):
            data[col] = reversed_dict[data[col][0]]

    data["extraversion"] = data["TIPI1"] - data["TIPI6"]
    data["agreeableness"] = data["TIPI7"] - data["TIPI2"]
    data["conscientiousness"] = data["TIPI3"] - data["TIPI8"]
    data["emotional_stability"] = data["TIPI9"] - data["TIPI4"]
    data["openness"] = data["TIPI5"] - data["TIPI10"]

    encoded = pd.get_dummies(data)

# Force exact training columns
    encoded = pd.get_dummies(data)

    # 🔥 Ensure ALL training columns exist
    for col in onehot_columns:
        if col not in encoded.columns:
            encoded[col] = 0

    # 🔥 Remove extra columns (not seen in training)
    encoded = encoded[onehot_columns]

# 🔥 CRITICAL FIX: strip pandas metadata
    encoded_np = encoded.to_numpy()

    return encoded_np



def predict_depression():
    data = main()


    n_features = model1.n_features_in_
    data = data[:, :n_features]

    preds = model1.predict(data)
    return int(preds[-1])


def predict_anxiety():
    data = main()  # numpy array (shape: [1, 5396])

    

    
    n_features = model2.n_features_in_
    data = data[:, :n_features]

    preds = model2.predict(data)
    return int(preds[-1])



def predict_stress():
    data = main()

    

    n_features = model3.n_features_in_
    data = data[:, :n_features]

    preds = model3.predict(data)
    return int(preds[-1])

