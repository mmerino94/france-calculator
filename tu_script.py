import pandas as pd
import numpy as np

# ============================================
# FUNCIÓN 1
# ============================================

def procesar_archivo(filepath):

    df = pd.read_excel(filepath)

    filas_vacias = df.isna().all(axis=1)
    indices_vacios = np.where(filas_vacias)[0]

    bloques = []
    inicio = 0

    for fin in indices_vacios:
        if fin > inicio:
            bloques.append(df.iloc[inicio:fin].copy())
        inicio = fin + 1

    if inicio < len(df):
        bloques.append(df.iloc[inicio:].copy())

    bloques1 = bloques[0].copy()

    bloques1.columns = bloques1.iloc[0]
    bloques1 = bloques1.iloc[1:]
    bloques1.reset_index(drop=True, inplace=True)

    bloques1.columns.values[18] = "Games Played area average"

    bloques1["CI"] = bloques1["Coin In per machine per day"] * bloques1["Days on Floor"]
    bloques1["NW"] = bloques1["Net Win per machine per day"] * bloques1["Days on Floor"]
    bloques1["TH"] = bloques1["Theoretical Win per machine per day"] * bloques1["Days on Floor"]
    bloques1["GP"] = bloques1["Games Played per machine per day"] * bloques1["Days on Floor"]

    bloques2 = bloques[1].copy()

    bloques2.columns = bloques2.iloc[0]
    bloques2 = bloques2.iloc[1:]
    bloques2.reset_index(drop=True, inplace=True)

    bloques2.columns = bloques2.iloc[0]
    bloques2 = bloques2.iloc[1:]
    bloques2.reset_index(drop=True, inplace=True)

    bloques2 = bloques2.iloc[:, 0:6]

    bloques2["Month"] = bloques1["Month"].iloc[0]
    bloques2["CasinoName"] = bloques1["CasinoName"].iloc[0]
    bloques2["Casino Group"] = bloques1["Casino Group"].iloc[0]

    return bloques1, bloques2


# ============================================
# FUNCIÓN 2
# ============================================

def convertir_a_plantilla(bloques1_final):

    plantilla_cols = [
        "MonthOfYear INPUT","CasinoName INPUT","Area","Section","PositionInBank",
        "Vendor INPUT","SerialNumber","EGM No","Game Title INPUT","Cabinet INPUT",
        "Lines","MaxBet","thRTP","Additional Info","GameType INPUT","Denom Input",
        "Currency","DenomValue","Coin In","CIPUPD","Net Win","NWPUPD","Th Win",
        "ThWinPUPD","Games Played","GPPUPD","DaysOnFloor","CI Floor Av",
        "CI Area Av","CIvsFA%","CIvsArea%","CIvsDenomArea%","theoNW Floor Av",
        "theoNW Area Av","theoNWvsFA%","theoNWvsArea%","NW Floor Av","NW Area AV",
        "NWvsFA%","NWvsArea%","GP Floor Av","GP Area Av","GPvsFA%","GPvs.Area%",
        "USB Extract MG Game Count","DailyLeaseFee","Lease Type Input",
        "VenueSize","VenueType","Field Trial","Rating Month ALT!",
        "MG Ratio CIPUPD","MG Ratio GPPUPD","MG Ratio ThWinPUPD"
    ]

    mapeo1 = {
        "Month": "MonthOfYear INPUT",
        "CasinoName": "CasinoName INPUT",
        "Machine#": "EGM No",
        "SerialNumber": "SerialNumber",
        "GameTitle": "Game Title INPUT",
        "Cabinet": "Cabinet INPUT",
        "CI": "Coin In",
        "Coin In per machine per day": "CIPUPD",
        "NW": "Net Win",
        "Net Win per machine per day": "NWPUPD",
        "TH": "Th Win",
        "Theoretical Win per machine per day": "ThWinPUPD",
        "GP": "Games Played",
        "Games Played per machine per day": "GPPUPD",
        "Days on Floor": "DaysOnFloor",
        "Coin In area average": "CI Area Av",
        "Net Win area average": "NW Area AV",
        "Theoretical Win area average": "theoNW Area Av",
        "Games Played area average": "GP Area Av",
        "Coin In Index vs Area": "CIvsArea%",
        "ThNW Index vs Area": "theoNWvsArea%",
        "Net Win Index vs Area": "NWvsArea%",
        "Games Played Index vs Area": "GPvs.Area%"
    }

    df_out = bloques1_final.rename(columns=mapeo1)

    df_out["GameType INPUT"] = "Video"
    df_out["Vendor INPUT"] = "IGT"
    df_out["Currency"] = "EUR"
    df_out["Denom Input"] = 0.01
    df_out["Field Trial"] = "Field Trial"

    for col in plantilla_cols:
        if col not in df_out.columns:
            df_out[col] = np.nan

    df_out = df_out[plantilla_cols]

    df_out["MonthOfYear INPUT"] = pd.to_datetime(
        df_out["MonthOfYear INPUT"]
    ).dt.strftime("%Y-%m")

    df_out = df_out.sort_values(
        by=["MonthOfYear INPUT","CasinoName INPUT","Area","Section","SerialNumber"]
    )

    df_out.reset_index(drop=True, inplace=True)

    return df_out
