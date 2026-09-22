
import os
import sys
import pandas as pd

CSV_PATH = "Sample_Purchase_Requests.csv"

_df_cache = None 

def load_pr_data(csv_path: str = CSV_PATH) -> pd.DataFrame:
    

    df = pd.read_csv(csv_path)
    df.columns =[c.strip() for c in df.columns]
    _df_cache=df
    return df


def get_pr_by_id(pr_id: str) -> dict | None:
    pr_id="PR-2026-"+pr_id
    df = load_pr_data()
    pr_id_clean = pr_id.strip().upper()

    match = df[df["PR_ID"].astype(str).str.strip().str.upper() == pr_id_clean]

    if match.empty:
        return None

    row = match.iloc[0]
    result = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
    return result


def format_pr_for_llm(pr_data: dict) -> str:
   
    lines = ["Purchase Request: "]
    for key, value in pr_data.items():
        display_value = value if value is not None else "Empty"
        lines.append(f"  - {key}: {display_value}")
    return "\n".join(lines)


def list_all_pr_ids() -> list[str]:
    df = load_pr_data()
    return df["PR_ID"].astype(str).str.strip().tolist()


if __name__ == "__main__":
    pr_id=input("please enter prid: ")
    result=get_pr_by_id(pr_id)
    format=format_pr_for_llm(result)
    print(format)