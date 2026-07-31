import gradio as gr

from agente.chat import procesar_mensaje
from agente.estado import crear_estado




MENSAJE_INICIAL = (
    "👋 **¡Bienvenido!**\n\n"
    "Soy el asistente inteligente de evaluación "
    "de riesgo crediticio.\n\n"
    "Le realizaré una serie de preguntas para estimar "
    "el nivel de riesgo del solicitante.\n\n"
    "Puede proporcionar uno o varios datos "
    "en un mismo mensaje.\n\n"
    "### Comencemos\n\n"
    "¿Qué monto desea solicitar para el préstamo?"
)




CSS_PERSONALIZADO = """
/* Fondo general de la aplicación */
.gradio-container {
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 24px 24px 40px 24px !important;
}

/* Encabezado principal */
#encabezado-principal {
    text-align: center;
    padding: 28px 25px;
    margin-bottom: 20px;
    border-radius: 22px;
    background: linear-gradient(
        135deg,
        rgba(16, 185, 129, 0.14),
        rgba(20, 184, 166, 0.08)
    );
    border: 1px solid rgba(16, 185, 129, 0.25);
    box-shadow: 0 8px 25px rgba(15, 118, 110, 0.08);
}

#encabezado-principal h1 {
    margin-bottom: 10px;
    font-size: 2rem;
    font-weight: 750;
}

#encabezado-principal p {
    margin: 5px auto;
    max-width: 760px;
    font-size: 1rem;
    line-height: 1.6;
    opacity: 0.85;
}

/* Contenedor del chat */
#contenedor-chat {
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(15, 118, 110, 0.09);
}

/* Área de escritura */
#entrada-mensaje textarea {
    font-size: 1rem !important;
    line-height: 1.5 !important;
}

/* Botón enviar */
#boton-enviar {
    min-height: 48px;
    font-size: 1rem;
    font-weight: 700;
    border-radius: 14px;
}

/* Botón reiniciar */
#boton-reiniciar {
    min-height: 48px;
    font-size: 1rem;
    font-weight: 650;
    border-radius: 14px;
}

/* Texto inferior */
#pie-aplicacion {
    text-align: center;
    margin-top: 22px;
    opacity: 0.65;
    font-size: 0.85rem;
}

/* Ajustes para pantallas pequeñas */
@media (max-width: 768px) {
    .gradio-container {
        padding: 12px !important;
    }

    #encabezado-principal {
        padding: 20px 14px;
    }

    #encabezado-principal h1 {
        font-size: 1.5rem;
    }
}
"""



def responder(
    mensaje: str,
    historial: list,
    estado: dict
):
    """
    Procesa el mensaje del usuario, actualiza el historial
    visual y conserva la memoria de la conversación.
    """

    if historial is None:
        historial = []

    if estado is None:
        estado = crear_estado()

    if not isinstance(mensaje, str):
        return (
            "",
            historial,
            estado
        )

    mensaje = mensaje.strip()

    if not mensaje:
        return (
            "",
            historial,
            estado
        )

    respuesta, estado_actualizado = procesar_mensaje(
        mensaje,
        estado
    )

    historial_actualizado = historial + [
        {
            "role": "user",
            "content": mensaje
        },
        {
            "role": "assistant",
            "content": respuesta
        }
    ]

    return (
        "",
        historial_actualizado,
        estado_actualizado
    )




def reiniciar_conversacion():
    """
    Reinicia el historial visible y el estado interno.
    """

    historial_inicial = [
        {
            "role": "assistant",
            "content": MENSAJE_INICIAL
        }
    ]

    return (
        "",
        historial_inicial,
        crear_estado()
    )



with gr.Blocks(
    title="Sistema Inteligente de Riesgo Crediticio",
    theme="gradio/calm_seafoam",
    css=CSS_PERSONALIZADO
) as app:

    # Encabezado
    gr.Markdown(
        """
        # 🏦 Sistema Inteligente de Evaluación de Riesgo Crediticio

        Este asistente recopilará la información necesaria
        para estimar el nivel de riesgo crediticio del solicitante.

        **Puede responder una pregunta o proporcionar varios datos
        en un mismo mensaje.**
        """,
        elem_id="encabezado-principal"
    )

    # Chat
    with gr.Group(
        elem_id="contenedor-chat"
    ):

        chatbot = gr.Chatbot(
            value=[
                {
                    "role": "assistant",
                    "content": MENSAJE_INICIAL
                }
            ],
            height=560,
            label="💬 Conversación",
            show_label=True
        )

    # Estado interno
    estado = gr.State(
        crear_estado()
    )

    # Entrada de texto
    mensaje = gr.Textbox(
        label="✍️ Escriba su respuesta",
        placeholder=(
            "..."
        ),
        lines=2,
        max_lines=5,
        elem_id="entrada-mensaje"
    )

    # Botones
    with gr.Row():

        boton_enviar = gr.Button(
            "➤ Enviar respuesta",
            variant="primary",
            scale=2,
            elem_id="boton-enviar"
        )

        boton_reiniciar = gr.Button(
            "↻ Reiniciar conversación",
            variant="secondary",
            scale=1,
            elem_id="boton-reiniciar"
        )

    # Nota inferior
    gr.Markdown(
        """
        Los resultados generados corresponden a una estimación
        realizada mediante un modelo de aprendizaje automático.
        """,
        elem_id="pie-aplicacion"
    )



    # Enviar presionando Enter
    mensaje.submit(
        fn=responder,
        inputs=[
            mensaje,
            chatbot,
            estado
        ],
        outputs=[
            mensaje,
            chatbot,
            estado
        ]
    )

    # Enviar mediante el botón
    boton_enviar.click(
        fn=responder,
        inputs=[
            mensaje,
            chatbot,
            estado
        ],
        outputs=[
            mensaje,
            chatbot,
            estado
        ]
    )

    # Reiniciar conversación
    boton_reiniciar.click(
        fn=reiniciar_conversacion,
        inputs=[],
        outputs=[
            mensaje,
            chatbot,
            estado
        ]
    )




if __name__ == "__main__":

    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True
    )