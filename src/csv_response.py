
import os
import sys
import pandas as pd

CSV_PATH = r"data\Sample_Purchase_Requests.csv"

_df_cache = None 

# load data
def load_pr_data(csv_path: str = CSV_PATH) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.drop(columns=["Notes"],inplace=True)
    df.columns =[c.strip() for c in df.columns]
    _df_cache=df
    return df

def load_pr_data_sum(csv_path: str = CSV_PATH) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns =[c.strip() for c in df.columns]
    _df_cache=df
    return df

#       requester
#----------------------------

def get_requester_name(Name:str)->pd.DataFrame:
    df=load_pr_data()
    df.columns = df.columns.str.strip()
    requester_df=df.loc[df["Requester"]==Name]
    return requester_df

def prs_for_specfic_requester(requester_df):
    requester_df.columns = requester_df.columns.str.strip()
    return sorted(requester_df["PR_ID"].unique().tolist())

def get_known_requesters() -> list[str]:
    df=load_pr_data()
    return sorted(df["Requester"].dropna().unique().tolist())

def get_pr_by_id_requester(pr_id: str,requester_df:pd.DataFrame) -> dict | None:
    df=requester_df
    pr_id_clean = pr_id.strip().upper()
    match = df[df["PR_ID"].astype(str).str.strip().str.upper() == pr_id_clean]
    if match.empty:
        return None
    row = match.iloc[0]
    result = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
    return result

#          officer
#-----------------------------
def get_pr_by_id(pr_id: str) -> dict | None:
    df = load_pr_data()
    match = df[df["PR_ID"].astype(str).str.strip().str.upper() == pr_id]
    if match.empty:
        return {"error":f"there now pr with this value: {pr_id}"}
    row = match.iloc[0]
    result = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
    return result

def get_all_pr_codes():
    df=load_pr_data()
    return sorted(df["PR_ID"].dropna().unique().tolist())

def summarize():
    df=load_pr_data_sum()
    records=df.to_dict(orient="records")
    procurement_record={
        "Total Reqeusts":len(df),
        "Missing Info": int((df["Missing_Info_Flag"]=="Yes").sum()),
        "Status":df["Status"].value_counts().to_dict(),
        "Notes":df[df["Missing_Info_Flag"] == "Yes"]["Notes"].value_counts().to_dict()}
    
    return {"Records":records,"precomputed_stats":procurement_record}

#       message will send to LLM
#-----------------------------------------
def format_pr_for_llm(pr_data: dict) -> str:
   
    lines = ["Purchase Request: "]
    for key, value in pr_data.items():
        display_value = value if value is not None else "Empty"
        lines.append(f"  - {key}: {display_value}")
    return "\n".join(lines)



if __name__ == "__main__":
    p=summarize()
    print(p["precomputed_stats"])
    