import pandas as pd
import pickle

import requests
import pandas as pd
from io import BytesIO



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



depression_questions = ["Q3A", "Q5A", "Q10A", "Q13A", "Q16A", "Q17A", "Q21A", "Q24A", "Q26A", "Q31A", "Q34A","Q37A", "Q38A", "Q42A"]
anxiety_questions = ["Q2A", "Q4A", "Q7A", "Q9A", "Q15A", "Q19A", "Q20A", "Q23A", "Q25A", "Q28A", "Q30A", "Q36A", "Q40A", "Q41A"]
stress_questions = ["Q1A", "Q6A", "Q8A", "Q11A", "Q12A", "Q14A", "Q18A", "Q22A", "Q27A", "Q29A", "Q32A", "Q33A", "Q35A", "Q39A"]

words = ["VCL1", "VCL2", "VCL3", "VCL4","VCL5", "VCL7", "VCL8", "VCL10", "VCL11", "VCL13", "VCL14", "VCL15", "VCL16"]

def main():
    onedrive_url = "https://bennettu-my.sharepoint.com/personal/e23cseu0615_bennett_edu_in/_layouts/15/download.aspx?share=EQLLM6GDZKVHli4aSWFVGccB587D3Qpr40bJZlQA9NoxGA"

    response = requests.get(onedrive_url)

    if response.status_code == 200:
        data = pd.read_excel(BytesIO(response.content))
    else:
        print(f"❌ Error: {response.status_code}")

    qa = []
    for i in data.columns:
        if i.startswith("Q") and i.endswith("A"):
            qa.append(i)

    for i in qa:
        data[i] = int(data[i][0][-1])

    reversed_dict = {
        "Disagree strongly": 1,
        "Disagree moderately": 2,
        "Disagree a little": 3,
        "Neither agree nor disagree": 4,
        "Agree a little": 5,
        "Agree moderately": 6,
        "Agree strongly": 7
    }

    ls = []

    for i in data.columns:
        if i[:3] == "TIP":
            ls.append(i)

    for i in ls:
        data[i] = reversed_dict[data[i][0]]
        
    data["extraversion"] = data["TIPI1"] - data["TIPI6"]
    data["agreeableness"] = data["TIPI7"] - data["TIPI2"]
    data["conscientiousness"] = data["TIPI3"] - data["TIPI8"]
    data["emotional_stability"] = data["TIPI9"] - data["TIPI4"]
    data["openness"] = data["TIPI5"] - data["TIPI10"]

    with open('/Users/aryanmanchanda/Projects/aura-check/Scripts/onehot_columns.pkl', 'rb') as f:
        onehot_columns = pickle.load(f)

    # One-hot encode input
    data.fillna("Unknown", inplace=True)

    input_encoded = pd.get_dummies(data)

    # Align input with training columns, filling missing columns with 0
    input_encoded = input_encoded.reindex(columns=onehot_columns, fill_value=0)
    data.fillna(False, inplace=True)
    input_encoded.to_csv("csv.csv")


def predict_depression():
    main()
    data = pd.read_csv("csv.csv", index_col=0)
    dropped_questions = ["anxiety_score", "stress_score", "depression_score"]
    for i in data.columns:
        if i.startswith("Q") and (i.endswith("I") or i.endswith("E")):
            dropped_questions.append(i)

    data = data.drop(dropped_questions, axis=1)
    model = pickle.load(open("/Users/aryanmanchanda/Projects/aura-check/models/xgc_model1_depression.pkl", "rb"))
    preds = model.predict(data)
    print(preds)

def predict_anxiety():
    main()
    data = pd.read_csv("csv.csv", index_col=0)
    dropped_questions = ["anxiety_score", "stress_score", "depression_score"]
    for i in data.columns:
        if i.startswith("Q") and (i.endswith("I") or i.endswith("E")):
            dropped_questions.append(i)

    data = data.drop(dropped_questions, axis=1)
    model = pickle.load(open("/Users/aryanmanchanda/Projects/aura-check/models/xgc_model1_anxiety.pkl", "rb"))
    preds = model.predict(data)
    print(preds)

def predict_stress():
    main()
    data = pd.read_csv("csv.csv", index_col=0)
    dropped_questions = ["anxiety_score", "stress_score", "depression_score"]
    for i in data.columns:
        if i.startswith("Q") and (i.endswith("I") or i.endswith("E")):
            dropped_questions.append(i)

    data = data.drop(dropped_questions, axis=1)
    model = pickle.load(open("/Users/aryanmanchanda/Projects/aura-check/models/xgc_model1_stress.pkl", "rb"))
    preds = model.predict(data)
    return preds[-1]


predict_anxiety()
predict_depression()
predict_stress()