from csv import DictWriter
from datetime import datetime
from pathlib import Path


RUTA_LOG = (
    Path(__file__).resolve().parent
    / "predicciones.csv"
)


def guardar_prediccion(datos: dict, resultado: dict) -> None:
    registro = {
        "fecha_hora": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        **datos,
        **resultado
    }

    archivo_existe = RUTA_LOG.exists()

    with RUTA_LOG.open(
        mode="a",
        newline="",
        encoding="utf-8"
    ) as archivo:
        escritor = DictWriter(
            archivo,
            fieldnames=registro.keys()
        )

        if not archivo_existe:
            escritor.writeheader()

        escritor.writerow(registro)