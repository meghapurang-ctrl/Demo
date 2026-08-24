from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "synthetic_marketing_campaign_dataset.csv"


def load_campaign_data() -> pd.DataFrame:
    """Load and lightly normalize the workshop dataset."""
    data = pd.read_csv(DATA_PATH)
    numeric_columns = [
        "Spend_USD", "Impressions", "Clicks", "CTR_Percent", "CPC_USD",
        "Conversions", "Conversion_Rate_Percent", "CPA_USD", "Revenue_USD",
        "ROAS", "Engagement_Rate_Percent", "Video_Completion_Rate_Percent",
    ]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="coerce")
    return data


def find_underperformers(data: pd.DataFrame) -> pd.DataFrame:
    """Flag rows that breach either workshop health threshold."""
    flagged = data[(data["CPA_USD"] > 50) | (data["CTR_Percent"] < 0.5)].copy()
    flagged["Issue"] = flagged.apply(
        lambda row: "High CPA + low CTR"
        if row["CPA_USD"] > 50 and row["CTR_Percent"] < 0.5
        else "High CPA" if row["CPA_USD"] > 50 else "Low CTR",
        axis=1,
    )
    return flagged.sort_values(["CPA_USD", "CTR_Percent"], ascending=[False, True])


def budget_recommendation(data: pd.DataFrame) -> tuple[pd.DataFrame, float, float]:
    """Move 20% of underperformer spend, weighted toward the top three ROAS rows."""
    underperformers = find_underperformers(data)
    result = data[["Campaign_ID", "Campaign_Name", "Audience_Segment", "Platform", "Spend_USD", "Conversions", "CPA_USD", "ROAS"]].copy().set_index("Campaign_ID")
    result["Current_Budget"] = result["Spend_USD"]
    result["Recommended_Budget"] = result["Spend_USD"]
    pool = underperformers["Spend_USD"].sum() * 0.20
    under_ids = set(underperformers["Campaign_ID"])
    result.loc[result.index.isin(under_ids), "Recommended_Budget"] *= 0.80

    top_ids = data[~data["Campaign_ID"].isin(under_ids)].nlargest(3, "ROAS")["Campaign_ID"].tolist()
    weights = result.loc[result.index.isin(top_ids), "ROAS"]
    if not weights.empty and weights.sum() > 0:
        for campaign_id, weight in weights.items():
            result.loc[campaign_id, "Recommended_Budget"] += pool * weight / weights.sum()

    result["Projected_Conversions"] = result["Recommended_Budget"] / result["CPA_USD"]
    projected = result["Projected_Conversions"].sum()
    current = result["Conversions"].sum()
    return result, current, projected
