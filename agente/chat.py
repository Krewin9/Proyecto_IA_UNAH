import re
import unicodedata
from copy import deepcopy


import requests

from agente.estado import (
    datos_completos,
    generar_resumen,
    guardar_datos,
    obtener_siguiente_pregunta,
    obtener_variables_faltantes,
    reiniciar_estado,
    NOMBRES_AMIGABLES
)



URL_API = "http://127.0.0.1:8000/predict"

COMANDOS_REINICIO = {
    "reiniciar",
    "nuevo",
    "nueva evaluacion",
    "comenzar de nuevo",
    "volver a comenzar"
}

COMANDOS_CONFIRMACION = {
    "confirmar",
    "confirmo",
    "confirmado"
}




def normalizar_texto(texto: str) -> str:
    """
    Convierte el texto a minúsculas, elimina espacios
    innecesarios y quita las tildes.
    """

    texto = texto.lower().strip()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto_sin_tildes = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto_sin_tildes = re.sub(
        r"\s+",
        " ",
        texto_sin_tildes
    )

    return texto_sin_tildes.strip()


def convertir_numero(valor: str) -> float | None:
    """
    Convierte una cadena numérica a float.

    Acepta valores como:
    5000
    5,000
    18.5
    18,5
    """

    if not valor:
        return None

    valor = valor.strip()

    
    if "," in valor and "." in valor:
        valor = valor.replace(",", "")

    
    elif "," in valor:

        partes = valor.split(",")

        
        if (
            len(partes) == 2
            and len(partes[1]) == 3
        ):
            valor = valor.replace(",", "")

        
        else:
            valor = valor.replace(",", ".")

    try:
        return float(valor)

    except ValueError:
        return None


def extraer_numero(texto: str) -> float | None:
    """
    Extrae el primer número encontrado en un texto.
    """

    coincidencia = re.search(
        r"\d+(?:[.,]\d+)?",
        texto
    )

    if not coincidencia:
        return None

    return convertir_numero(
        coincidencia.group()
    )




def extraer_monto(texto: str) -> float | None:
    """
    Intenta identificar el monto solicitado.
    """

    patrones = [
        (
            r"(?:prestamo|solicitar|solicito|monto|"
            r"necesito|quiero|deseo)"
            r"\D{0,25}"
            r"(\d+(?:[.,]\d+)?)"
        ),
        (
            r"(\d+(?:[.,]\d+)?)"
            r"\s*(?:lempiras|dolares|usd|lps)"
        )
    ]

    for patron in patrones:

        coincidencia = re.search(
            patron,
            texto
        )

        if coincidencia:

            valor = convertir_numero(
                coincidencia.group(1)
            )

            if valor is not None and valor > 0:
                return valor

    return None



def extraer_plazo(texto: str) -> str | None:
    """
    Identifica si el préstamo será a 36 o 60 meses.
    """

    if re.search(
        r"\b36\s*(?:mes|meses|months)?\b",
        texto
    ):
        return "36 months"

    if re.search(
        r"\b60\s*(?:mes|meses|months)?\b",
        texto
    ):
        return "60 months"

    if any(
        frase in texto
        for frase in [
            "tres anos",
            "3 anos"
        ]
    ):
        return "36 months"

    if any(
        frase in texto
        for frase in [
            "cinco anos",
            "5 anos"
        ]
    ):
        return "60 months"

    return None


def extraer_proposito(texto: str) -> str | None:
    """
    Convierte el propósito escrito por el usuario
    a una categoría válida del modelo.
    """

    equivalencias = {
        "debt_consolidation": [
            "consolidar deudas",
            "consolidacion de deudas",
            "pagar mis deudas",
            "pagar deudas",
            "reunir deudas"
        ],

        "credit_card": [
            "tarjeta de credito",
            "pagar tarjetas",
            "pagar mi tarjeta",
            "deuda de tarjeta"
        ],

        "home_improvement": [
            "remodelar",
            "remodelacion",
            "mejorar mi casa",
            "mejorar la casa",
            "reparar mi casa",
            "reparar la casa",
            "reparaciones de casa",
            "mejoras del hogar"
        ],

        "small_business": [
            "negocio",
            "empresa",
            "emprendimiento",
            "capital de trabajo"
        ],

        "major_purchase": [
            "compra importante",
            "compra grande"
        ],

        "medical": [
            "gastos medicos",
            "tratamiento medico",
            "hospital",
            "medicina",
            "salud"
        ],

        "moving": [
            "mudanza",
            "mudarme",
            "traslado"
        ],

        "vacation": [
            "vacaciones",
            "viaje",
            "viajar"
        ],

        "house": [
            "comprar una casa",
            "comprarme una casa",
            "comprar casa",
            "comprarme casa",
            "comprar una vivienda",
            "comprarme una vivienda",
            "comprar vivienda",
            "adquirir una casa",
            "adquirir vivienda",
            "casa"
        ],

        "car": [
            "comprar un carro",
            "comprarme un carro",
            "comprar carro",
            "comprarme carro",
            "comprar un vehiculo",
            "comprarme un vehiculo",
            "comprar vehiculo",
            "automovil",
            "vehiculo",
            "carro",
            "auto"
        ],

        "renewable_energy": [
            "energia renovable",
            "paneles solares",
            "energia solar"
        ],

        "wedding": [
            "boda",
            "casamiento",
            "matrimonio"
        ],

        "education": [
            "universidad",
            "estudios",
            "estudiar",
            "educacion",
            "matricula"
        ],

        "other": [
            "otro proposito",
            "otros gastos"
        ]
    }

    for categoria, palabras in equivalencias.items():
        for palabra in palabras:
            if palabra in texto:
                return categoria

    return None





def extraer_ingreso_anual(
    texto: str
) -> float | None:
    """
    Identifica el ingreso anual aproximado.
    """

    patrones = [
        (
            r"(?:gano|ingreso|ingresos|salario|"
            r"devengo|recibo)"
            r"\D{0,25}"
            r"(\d+(?:[.,]\d+)?)"
            r"\s*(?:al ano|anuales|por ano)?"
        ),
        (
            r"(\d+(?:[.,]\d+)?)"
            r"\s*(?:al ano|anuales|por ano)"
        )
    ]

    for patron in patrones:

        coincidencia = re.search(
            patron,
            texto
        )

        if coincidencia:

            valor = convertir_numero(
                coincidencia.group(1)
            )

            if valor is not None and valor > 0:
                return valor

    return None



def extraer_verificacion(
    texto: str
) -> str | None:
    """
    Identifica el estado de verificación de ingresos.
    """

    if any(
        frase in texto
        for frase in [
            "no verificado",
            "no verificados",
            "sin verificar",
            "no estan verificados",
            "no esta verificado"
        ]
    ):
        return "Not Verified"

    if any(
        frase in texto
        for frase in [
            "verificado por la fuente",
            "verificados por la fuente",
            "source verified"
        ]
    ):
        return "Source Verified"

    if any(
        frase in texto
        for frase in [
            "verificado",
            "verificados",
            "si estan verificados",
            "si esta verificado"
        ]
    ):
        return "Verified"

    return None




def extraer_antiguedad(
    texto: str
) -> str | None:
    """
    Identifica la antigüedad laboral.
    """

    if any(
        frase in texto
        for frase in [
            "menos de un ano",
            "menos de 1 ano",
            "menos de un año"
        ]
    ):
        return "< 1 year"

    if any(
        frase in texto
        for frase in [
            "10 anos o mas",
            "10 años o mas",
            "mas de 10 anos",
            "mas de diez anos",
            "10+ anos"
        ]
    ):
        return "10+ years"

    patrones = [
        (
            r"(?:trabajo|trabajando|antiguedad|"
            r"experiencia|laborando|empleado)"
            r"\D{0,20}"
            r"(\d+)"
            r"\s*anos?"
        ),
        r"llevo\s*(\d+)\s*anos?",
        r"tengo\s*(\d+)\s*anos?\s*(?:trabajando|laborando)"
    ]

    for patron in patrones:

        coincidencia = re.search(
            patron,
            texto
        )

        if coincidencia:

            anos = int(
                coincidencia.group(1)
            )

            if anos >= 10:
                return "10+ years"

            if anos == 1:
                return "1 year"

            return f"{anos} years"

    return None




def extraer_vivienda(
    texto: str
) -> str | None:
    """
    Identifica si la vivienda es alquilada,
    propia o hipotecada.
    """

    if any(
        frase in texto
        for frase in [
            "vivo alquilado",
            "vivo alquilada",
            "casa alquilada",
            "vivienda alquilada",
            "alquilo",
            "rento",
            "rentada"
        ]
    ):
        return "RENT"

    if any(
        frase in texto
        for frase in [
            "casa hipotecada",
            "vivienda hipotecada",
            "tengo hipoteca",
            "pago hipoteca",
            "hipotecada"
        ]
    ):
        return "MORTGAGE"

    if any(
        frase in texto
        for frase in [
            "casa propia",
            "vivienda propia",
            "soy propietario",
            "soy propietaria",
            "la casa es mia",
            "propia"
        ]
    ):
        return "OWN"

    return None




def extraer_dti(texto: str) -> float | None:
    """
    Identifica la relación deuda-ingreso.
    """

    patrones = [
        (
            r"(?:dti|deuda.?ingreso|"
            r"relacion deuda ingreso)"
            r"\D{0,20}"
            r"(\d+(?:[.,]\d+)?)"
        ),
        (
            r"(\d+(?:[.,]\d+)?)"
            r"\s*%"
            r"\s*(?:de dti|de deuda)"
        )
    ]

    for patron in patrones:

        coincidencia = re.search(
            patron,
            texto
        )

        if coincidencia:

            valor = convertir_numero(
                coincidencia.group(1)
            )

            if valor is not None and valor >= 0:
                return valor

    return None




def extraer_fico(texto: str) -> float | None:
    """
    Extrae un puntaje crediticio entre 300 y 850.

    Si el usuario no conoce el puntaje, devuelve None.
    """

    if any(
        frase in texto
        for frase in [
            "no conozco mi puntaje",
            "no conozco el puntaje",
            "desconozco mi puntaje",
            "no se mi score",
            "no se mi fico"
        ]
    ):
        return None

    coincidencia = re.search(
        (
            r"(?:fico|puntaje|score|"
            r"calificacion crediticia)"
            r"\D{0,20}"
            r"(\d{3})"
        ),
        texto
    )

    if coincidencia:

        valor = float(
            coincidencia.group(1)
        )

        if 300 <= valor <= 850:
            return valor

    return None




def extraer_cantidad(
    texto: str,
    palabras_clave: list[str]
) -> float | None:
    """
    Busca un número después de una palabra o frase clave.
    """

    palabras_ordenadas = sorted(
        palabras_clave,
        key=len,
        reverse=True
    )

    expresion = "|".join(
        re.escape(palabra)
        for palabra in palabras_ordenadas
    )

    patrones = [
        (
            rf"(?:{expresion})"
            rf"\D{{0,20}}"
            rf"(\d+(?:[.,]\d+)?)"
        ),
        (
            rf"(\d+(?:[.,]\d+)?)"
            rf"\s*(?:{expresion})"
        )
    ]

    for patron in patrones:

        coincidencia = re.search(
            patron,
            texto
        )

        if coincidencia:

            valor = convertir_numero(
                coincidencia.group(1)
            )

            if valor is not None and valor >= 0:
                return valor

    return None




def extraer_datos(
    texto_original: str
) -> dict:
    """
    Extrae una o varias variables de un mismo mensaje.
    """

    texto = normalizar_texto(
        texto_original
    )

    datos: dict = {}

    monto = extraer_monto(texto)

    if monto is not None:
        datos["loan_amnt"] = monto

    plazo = extraer_plazo(texto)

    if plazo is not None:
        datos["term"] = plazo

    proposito = extraer_proposito(texto)

    if proposito is not None:
        datos["purpose"] = proposito

    ingreso = extraer_ingreso_anual(texto)

    if ingreso is not None:
        datos["annual_inc"] = ingreso

    verificacion = extraer_verificacion(texto)

    if verificacion is not None:
        datos["verification_status"] = verificacion

    antiguedad = extraer_antiguedad(texto)

    if antiguedad is not None:
        datos["emp_length"] = antiguedad

    vivienda = extraer_vivienda(texto)

    if vivienda is not None:
        datos["home_ownership"] = vivienda

    dti = extraer_dti(texto)

    if dti is not None:
        datos["dti"] = dti

    fico = extraer_fico(texto)

    if fico is not None:
        datos["fico_range_low"] = fico

    consultas = extraer_cantidad(
        texto,
        [
            "consultas crediticias",
            "consultas de credito",
            "consultas"
        ]
    )

    if consultas is not None:
        datos["inq_last_6mths"] = consultas

    cuentas_totales = extraer_cantidad(
        texto,
        [
            "cuentas de credito totales",
            "cuentas crediticias totales",
            "cuentas de credito",
            "cuentas crediticias",
            "cuentas totales"
        ]
    )

    if cuentas_totales is not None:
        datos["total_acc"] = cuentas_totales

    cuentas_hipotecarias = extraer_cantidad(
        texto,
        [
            "cuentas hipotecarias",
            "hipotecas"
        ]
    )

    if cuentas_hipotecarias is not None:
        datos["mort_acc"] = cuentas_hipotecarias

    registros_publicos = extraer_cantidad(
        texto,
        [
            "registros publicos negativos",
            "registros publicos",
            "registros negativos"
        ]
    )

    if registros_publicos is not None:
        datos["pub_rec"] = registros_publicos

    moras = extraer_cantidad(
        texto,
        [
            "moras en los ultimos dos anos",
            "moras durante los ultimos dos anos",
            "moras",
            "atrasos"
        ]
    )

    if moras is not None:
        datos["delinq_2yrs"] = moras

    bancarrotas = extraer_cantidad(
        texto,
        [
            "bancarrotas registradas",
            "bancarrotas",
            "quiebras"
        ]
    )

    if bancarrotas is not None:
        datos["pub_rec_bankruptcies"] = bancarrotas

    return datos



def solicitar_prediccion(
    datos: dict
) -> str:
    """
    Envía los datos recopilados a FastAPI y devuelve
    únicamente el nivel de riesgo.
    """

    try:
        respuesta = requests.post(
            URL_API,
            json=datos,
            timeout=30
        )

        respuesta.raise_for_status()

        resultado = respuesta.json()

        riesgo = resultado.get(
            "riesgo"
        )

        if not riesgo:
            return (
                "La API respondió, pero no devolvió "
                "un nivel de riesgo válido."
            )

        return riesgo

    except requests.exceptions.ConnectionError:
        return (
            "No fue posible conectar con la API. "
            "Verifique que FastAPI esté ejecutándose."
        )

    except requests.exceptions.Timeout:
        return (
            "La API tardó demasiado en responder."
        )

    except requests.exceptions.HTTPError as error:

        detalle = ""

        if error.response is not None:

            try:
                detalle = error.response.json()

            except ValueError:
                detalle = error.response.text

        return (
            "La API rechazó los datos enviados. "
            f"Detalle: {detalle}"
        )

    except requests.exceptions.RequestException as error:
        return (
            "Ocurrió un error al consultar la API: "
            f"{error}"
        )


def interpretar_respuesta_directa(
    mensaje: str,
    variable_esperada: str | None
) -> dict:
    """
    Interpreta respuestas breves según la variable
    que el agente está preguntando actualmente.
    """

    if variable_esperada is None:
        return {}

    texto = normalizar_texto(mensaje)
    numero = extraer_numero(texto)

    if variable_esperada == "loan_amnt":
        if numero is not None and numero > 0:
            return {"loan_amnt": numero}

    if variable_esperada == "annual_inc":
        if numero is not None and numero > 0:
            return {"annual_inc": numero}

    if variable_esperada == "term":
        plazo = extraer_plazo(texto)

        if plazo is not None:
            return {"term": plazo}

    if variable_esperada == "purpose":
        proposito = extraer_proposito(texto)

        if proposito is not None:
            return {"purpose": proposito}

    if variable_esperada == "verification_status":
        verificacion = extraer_verificacion(texto)

        if verificacion is not None:
            return {
                "verification_status": verificacion
            }

        if texto in {"si", "sí"}:
            return {
                "verification_status": "Verified"
            }

        if texto == "no":
            return {
                "verification_status": "Not Verified"
            }

    if variable_esperada == "emp_length":
        antiguedad = extraer_antiguedad(texto)

        if antiguedad is not None:
            return {"emp_length": antiguedad}

        if numero is not None:
            anos = int(numero)

            if anos >= 10:
                return {"emp_length": "10+ years"}

            if anos == 1:
                return {"emp_length": "1 year"}

            if anos >= 0:
                return {
                    "emp_length": f"{anos} years"
                }

    if variable_esperada == "home_ownership":
        vivienda = extraer_vivienda(texto)

        if vivienda is not None:
            return {"home_ownership": vivienda}

    if variable_esperada == "dti":
        if numero is not None and numero >= 0:
            return {"dti": numero}

    if variable_esperada == "fico_range_low":
        if texto in {
            "no lo se",
            "no se",
            "desconozco"
        }:
            return {"fico_range_low": None}

        if (
            numero is not None
            and 300 <= numero <= 850
        ):
            return {"fico_range_low": numero}

    variables_cantidad = {
        "inq_last_6mths",
        "total_acc",
        "mort_acc",
        "pub_rec",
        "delinq_2yrs",
        "pub_rec_bankruptcies"
    }

    if variable_esperada in variables_cantidad:
        if numero is not None and numero >= 0:
            return {
                variable_esperada: numero
            }

    return {}

def procesar_mensaje(
    mensaje: str,
    estado: dict
) -> tuple[str, dict]:
    """
    Procesa el mensaje del usuario, actualiza el estado
    y devuelve la respuesta del agente.
    """

    if not isinstance(mensaje, str):
        return (
            "El mensaje recibido no es válido.",
            estado
        )

    texto = normalizar_texto(mensaje)

    if not texto:
        return (
            "Por favor, escriba una respuesta.",
            estado
        )

    # =====================================================
    # Reiniciar conversación
    # =====================================================

    if texto in COMANDOS_REINICIO:

        nuevo_estado = reiniciar_estado()

        siguiente_pregunta = obtener_siguiente_pregunta(
            nuevo_estado
        )

        return (
            "Conversación reiniciada.\n\n"
            + siguiente_pregunta,
            nuevo_estado
        )

    # =====================================================
    # Evaluación ya finalizada
    # =====================================================

    if estado.get(
        "finalizado",
        False
    ):
        return (
            "La evaluación ya fue realizada.\n\n"
            "Escriba REINICIAR para comenzar "
            "una nueva evaluación.",
            estado
        )

    # =====================================================
    # Los 15 datos ya fueron recopilados
    # =====================================================

    if datos_completos(estado):

        if texto in COMANDOS_CONFIRMACION:

            riesgo = solicitar_prediccion(
                estado["datos"]
            )

            estado_actualizado = deepcopy(
                estado
            )

            estado_actualizado["confirmado"] = True
            estado_actualizado["finalizado"] = True

            return (
                "Resultado de la evaluación:\n\n"
                f"**{riesgo}**\n\n"
                "Escriba REINICIAR para realizar "
                "una nueva evaluación.",
                estado_actualizado
            )

        return (
            generar_resumen(estado)
            + "\n\nEscriba CONFIRMAR para realizar "
            "la evaluación.",
            estado
        )

    # =====================================================
    # Saber qué variable está esperando el agente
    # =====================================================

    variables_faltantes = obtener_variables_faltantes(
        estado
    )

    variable_esperada = (
        variables_faltantes[0]
        if variables_faltantes
        else None
    )

   

    datos_extraidos = extraer_datos(
        mensaje
    )

    # =====================================================
    # Interpretar respuestas cortas según la pregunta actual
    # =====================================================

    datos_directos = interpretar_respuesta_directa(
        mensaje,
        variable_esperada
    )

    datos_extraidos.update(
        datos_directos
    )


    estado_actualizado = guardar_datos(
        estado,
        datos_extraidos
    )

    

    if datos_completos(
        estado_actualizado
    ):
        return (
            generar_resumen(
                estado_actualizado
            )
            + "\n\nEscriba CONFIRMAR para realizar "
            "la evaluación.",
            estado_actualizado
        )

   

    siguiente_pregunta = obtener_siguiente_pregunta(
        estado_actualizado
    )

    if datos_extraidos:

        variables_detectadas = []

        for variable in datos_extraidos.keys():

            nombre = NOMBRES_AMIGABLES.get(
                variable,
                variable
            )

            variables_detectadas.append(
                f"✓ {nombre}"
            )

        texto_variables = "\n".join(
            variables_detectadas
        )

        respuesta = (
            "Perfecto.\n\n"
            "He registrado correctamente:\n\n"
            f"{texto_variables}\n\n"
            f"{siguiente_pregunta}"
        )

    else:

        respuesta = (
            "No pude identificar ese dato con claridad.\n\n"
            f"{siguiente_pregunta}"
        )

    return (
        respuesta,
        estado_actualizado
    )