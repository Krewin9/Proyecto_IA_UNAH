from pathlib import Path

import joblib
import pandas as pd


RUTA_MODELO = (
    Path(__file__).resolve().parent.parent
    / "modelo"
    / "modelo_riesgo_svc_smote.joblib"
)

RUTA_VARIABLES = (
    Path(__file__).resolve().parent.parent
    / "modelo"
    / "variables_modelo.joblib"
)

modelo = joblib.load(RUTA_MODELO)
variables = joblib.load(RUTA_VARIABLES)


MAPA_RIESGO = {
    0: "Riesgo Bajo",
    1: "Riesgo Medio",
    2: "Riesgo Alto"
}



def predecir(datos: dict):

    df = pd.DataFrame([datos])

    df = df[variables]

    codigo = int(modelo.predict(df)[0])

    return {
        "codigo_riesgo": codigo,
        "riesgo": MAPA_RIESGO[codigo]
    }