from fastapi import FastAPI

from api.prediccion import predecir
from api.schemas import (
    DatosPrestamo,
    ResultadoPrediccion
)
from logs.predicciones import guardar_prediccion


app = FastAPI(
    title="API Riesgo Crediticio",
    version="1.0"
)


@app.get("/")
def inicio():
    return {
        "mensaje": (
            "API de evaluación de riesgo "
            "funcionando correctamente."
        )
    }


@app.post(
    "/predict",
    response_model=ResultadoPrediccion
)
def predict(datos: DatosPrestamo):

    datos_diccionario = datos.model_dump()

    resultado = predecir(
        datos_diccionario
    )

    guardar_prediccion(
        datos_diccionario,
        resultado
    )

    return resultado

