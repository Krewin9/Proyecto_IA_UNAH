from copy import deepcopy


VARIABLES_REQUERIDAS = [
    "loan_amnt",
    "term",
    "purpose",
    "annual_inc",
    "verification_status",
    "emp_length",
    "home_ownership",
    "dti",
    "fico_range_low",
    "inq_last_6mths",
    "total_acc",
    "mort_acc",
    "pub_rec",
    "delinq_2yrs",
    "pub_rec_bankruptcies"
]


PREGUNTAS = {

    "loan_amnt":
        "¿Qué monto desea solicitar para el préstamo?",

    "term":
        "¿En cuántos meses desea pagar el préstamo? (36 o 60 meses)",

    "purpose":
        (
            "¿Para qué utilizará el préstamo?\n"
            "Ejemplo: comprar un carro, comprar casa, "
            "tarjeta de credito, etc."
        ),

    "annual_inc":
        "¿Cuál es su ingreso anual aproximado?",

    "verification_status":
        (
            "¿Puede comprobar sus ingresos mediante "
            "documentos o constancias?\n"
            "Responda: Sí o No."
        ),

    "emp_length":
        "¿Cuántos años de experiencia laboral tiene en su empleo actual?",

    "home_ownership":
        (
            "¿Cuál es su situación de vivienda?\n"
            "Propia, Alquilada o Hipotecada."
        ),

    "dti":
        (
            "¿Qué porcentaje aproximado de sus ingresos "
            "mensuales utiliza para pagar deudas?"
        ),

    "fico_range_low":
        (
            "¿Conoce su puntaje o calificación crediticia?\n"
            "Si no lo conoce ingrese a este link \n"
            "https://www.cnbs.gob.hn/mi-reporte-crediticio/ "
        ),

    "inq_last_6mths":
        (
            "¿Cuántas consultas de crédito ha realizado "
            "durante los últimos seis meses?"
        ),

    "total_acc":
        "¿Cuántas tarjetas de crédito tiene actualmente?",

    "mort_acc":
        "¿Cuántos préstamos hipotecarios tiene actualmente?",

    "pub_rec":
        (
            "¿Tiene registros públicos negativos "
            "relacionados con asuntos financieros?\n"
            "Si es así, ¿cuántos?"
        ),

    "delinq_2yrs":
        (
            "¿Cuántas veces se ha atrasado en el pago "
            "de sus créditos durante los últimos dos años?"
        ),

    "pub_rec_bankruptcies":
        (
            "¿Cuántas declaraciones de bancarrota "
            "tiene registradas?"
        )
}


NOMBRES_AMIGABLES = {

    "loan_amnt":
        "Monto solicitado",

    "term":
        "Plazo del préstamo",

    "purpose":
        "Propósito del préstamo",

    "annual_inc":
        "Ingreso anual",

    "verification_status":
        "Ingresos verificados",

    "emp_length":
        "Experiencia laboral",

    "home_ownership":
        "Situación de vivienda",

    "dti":
        "Porcentaje destinado al pago de deudas",

    "fico_range_low":
        "Puntaje crediticio",

    "inq_last_6mths":
        "Consultas de crédito (últimos 6 meses)",

    "total_acc":
        "Tarjetas de crédito",

    "mort_acc":
        "Préstamos hipotecarios",

    "pub_rec":
        "Registros públicos negativos",

    "delinq_2yrs":
        "Atrasos en pagos (2 años)",

    "pub_rec_bankruptcies":
        "Bancarrotas registradas"
}


def crear_estado() -> dict:
    """
    Crea un estado vacío para una nueva conversación.
    """

    return {
        "datos": {},
        "confirmado": False,
        "finalizado": False
    }


def reiniciar_estado() -> dict:
    """
    Devuelve un estado nuevo y vacío.
    """

    return crear_estado()


def guardar_datos(
    estado: dict,
    datos_nuevos: dict
) -> dict:
    """
    Guarda únicamente variables válidas y valores
    que no sean None.
    """

    estado_actualizado = deepcopy(estado)

    for variable, valor in datos_nuevos.items():

        if variable not in VARIABLES_REQUERIDAS:
            continue

        if valor is None:
            continue

        estado_actualizado["datos"][variable] = valor

    return estado_actualizado


def obtener_variables_faltantes(
    estado: dict
) -> list[str]:
    """
    Devuelve las variables que todavía no han sido
    recolectadas.
    """

    datos = estado.get("datos", {})

    return [
        variable
        for variable in VARIABLES_REQUERIDAS
        if variable not in datos
    ]


def datos_completos(estado: dict) -> bool:
    """
    Indica si las 15 variables ya están disponibles.
    """

    return len(
        obtener_variables_faltantes(estado)
    ) == 0


def obtener_siguiente_pregunta(
    estado: dict
) -> str | None:
    """
    Devuelve la pregunta correspondiente al primer
    dato que todavía falta.
    """

    faltantes = obtener_variables_faltantes(estado)

    if not faltantes:
        return None

    siguiente_variable = faltantes[0]

    return PREGUNTAS[siguiente_variable]


def generar_resumen(estado: dict) -> str:
    """
    Genera un resumen legible de los datos recopilados.
    """

    datos = estado.get("datos", {})

    lineas = [
        "Resumen de la información proporcionada:",
        ""
    ]

    for variable in VARIABLES_REQUERIDAS:

        nombre = NOMBRES_AMIGABLES[variable]
        valor = datos.get(variable, "Pendiente")

        lineas.append(
            f"- {nombre}: {valor}"
        )

    return "\n".join(lineas)