import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Configuración de página ---
st.set_page_config(page_title="Lavandería", page_icon="🧺", layout="centered")

# --- Lista de servicios con precios ---
servicios = {
    "Lavadora 16 kg": 140,
    "Lavadora 9 kg": 85,
    "Lavadora 4 kg": 50,
    "Secadora 9 kg (15 minutos)": 30,
    "Secadora 9 kg (30 minutos)": 60,
    "1 medida de jabón": 10,
    "1 medida de suavizante": 10,
    "1 medida de desmugrante": 15,
    "1 bolsa chica": 5,
    "1 bolsa mediana": 6,
    "1 bolsa grande": 7,
}

# --- Título de la app ---
st.markdown("<h1 style='color:#A3C4F3'>🧺 Sistema de Lavandería</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#C9A3F3'>Seleccione los servicios y cantidades:</h3>", unsafe_allow_html=True)

# Carrito de compra
pedido = []
total_general = 0

# --- SECCIÓN 1: Lavadoras y Secadoras ---
st.markdown("<h3 style='color:#C9A3F3'>🧺 Lavadoras y Secadoras</h3>", unsafe_allow_html=True)
for servicio in ["Lavadora 16 kg", "Lavadora 9 kg", "Lavadora 4 kg",
                 "Secadora 9 kg (15 minutos)", "Secadora 9 kg (30 minutos)"]:
    precio = servicios[servicio]
    cantidad = st.number_input(f"{servicio} (${precio})", min_value=0, step=1, key=servicio)
    if cantidad > 0:
        subtotal = cantidad * precio
        pedido.append((servicio, cantidad, precio, subtotal))
        total_general += subtotal

# --- SECCIÓN 2: Detergentes y Bolsas ---
st.markdown("<h3 style='color:#C9A3F3'>🧴 Detergentes, Suavizantes, Desmugrantes y Bolsas</h3>", unsafe_allow_html=True)
for servicio in ["1 medida de jabón", "1 medida de suavizante", "1 medida de desmugrante",
                 "1 bolsa chica", "1 bolsa mediana", "1 bolsa grande"]:
    precio = servicios[servicio]
    cantidad = st.number_input(f"{servicio} (${precio})", min_value=0, step=1, key=servicio+"_extra")
    if cantidad > 0:
        subtotal = cantidad * precio
        pedido.append((servicio, cantidad, precio, subtotal))
        total_general += subtotal

# Guardar total en sesión
st.session_state["total_general"] = total_general

# --- Emoji de dinero ajustado al tamaño de los títulos ---
st.markdown("<h3 style='color:#C9A3F3'>💵 Dinero entregado:</h3>", unsafe_allow_html=True)
dinero_entregado = st.number_input("", min_value=0, step=1, key="dinero")

# Botón para generar ticket
if st.button("🧾 Generar Ticket"):
    if pedido:
        st.markdown("<h3 style='color:#C9A3F3'>Ticket de compra</h3>", unsafe_allow_html=True)

        # Mostrar en formato tabla
        st.table(
            {
                "Servicio": [p[0] for p in pedido],
                "Cantidad": [p[1] for p in pedido],
                "Precio c/u": [p[2] for p in pedido],
                "Subtotal": [p[3] for p in pedido],
            }
        )

        # Total con azul pastel
        st.markdown(f"<h3 style='color:#89CFF0'>💰 TOTAL GENERAL: ${total_general}</h3>", unsafe_allow_html=True)

        # Validar pago y mostrar cambio
        if dinero_entregado >= total_general:
            cambio = dinero_entregado - total_general
            st.markdown(f"<h3 style='color:#B3E6B3'>✅ Cambio a devolver: ${cambio}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='color:#F5A3A3'>⚠️ El dinero entregado no es suficiente.</h3>", unsafe_allow_html=True)

        # --- Guardar ticket en Excel ---
        filas = []
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for p in pedido:
            filas.append({
                "Fecha": fecha_actual,
                "Servicio": p[0],
                "Cantidad": p[1],
                "Precio Unitario": p[2],
                "Subtotal": p[3],
                "Total": total_general,
                "Dinero Entregado": dinero_entregado,
                "Cambio": dinero_entregado - total_general if dinero_entregado >= total_general else 0
            })

        df_ticket = pd.DataFrame(filas)

        # Guardar o anexar a archivo existente
        try:
            df_existente = pd.read_excel("ventas_lavanderia.xlsx")
            df_final = pd.concat([df_existente, df_ticket], ignore_index=True)
        except FileNotFoundError:
            df_final = df_ticket

        df_final.to_excel("ventas_lavanderia.xlsx", index=False)
        st.success("📄 Ticket guardado correctamente en ventas_lavanderia.xlsx")
    else:
        st.markdown("<h3 style='color:#F5A3A3'>⚠️ No seleccionaste ningún servicio.</h3>", unsafe_allow_html=True)

# --- Mostrar resumen diario ---
st.markdown("<h3 style='color:#C9A3F3'>📊 Resumen de ventas del día</h3>", unsafe_allow_html=True)
try:
    df_ventas = pd.read_excel("ventas_lavanderia.xlsx")
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    df_hoy = df_ventas[df_ventas['Fecha'].str.contains(fecha_hoy)]
    if not df_hoy.empty:
        st.table(df_hoy)
        # --- SUMA CORRECTA DEL TOTAL DEL DÍA ---
        df_totales_ticket = df_hoy.groupby('Fecha')['Total'].first().reset_index()
        total_dia = df_totales_ticket['Total'].sum()
        st.markdown(f"<h3 style='color:#89CFF0'>💰 TOTAL DEL DÍA: ${total_dia}</h3>", unsafe_allow_html=True)

        # --- RESUMEN DE CANTIDADES USADAS CON SECCIONES ESTÉTICAS ---
        servicios_diarios = {
            "Lavadoras 16 kg": "Lavadora 16 kg",
            "Lavadoras 9 kg": "Lavadora 9 kg",
            "Lavadoras 4 kg": "Lavadora 4 kg",
            "Secadoras 9 kg (15 minutos)": "Secadora 9 kg (15 minutos)",
            "Secadoras 9 kg (30 minutos)": "Secadora 9 kg (30 minutos)",
            "Detergentes": "1 medida de jabón",
            "Suavizantes": "1 medida de suavizante",
            "Desmugrantes": "1 medida de desmugrante",
            "Bolsas chicas": "1 bolsa chica",
            "Bolsas medianas": "1 bolsa mediana",
            "Bolsas grandes": "1 bolsa grande"
        }

        # Sección Lavadoras y Secadoras
        st.markdown("<h3 style='color:#C9A3F3'>🧺 Lavadoras y Secadoras usadas hoy</h3>", unsafe_allow_html=True)
        for nombre, servicio_columna in servicios_diarios.items():
            if servicio_columna in ["Lavadora 16 kg", "Lavadora 9 kg", "Lavadora 4 kg",
                                    "Secadora 9 kg (15 minutos)", "Secadora 9 kg (30 minutos)"]:
                total = df_hoy[df_hoy['Servicio'] == servicio_columna]['Cantidad'].sum() if servicio_columna in df_hoy['Servicio'].values else 0
                st.markdown(f"- {nombre}: {total}")

        # Sección Detergentes y Bolsas
        st.markdown("<h3 style='color:#C9A3F3'>🧴 Detergentes, Suavizantes, Desmugrantes y Bolsas usadas hoy</h3>", unsafe_allow_html=True)
        for nombre, servicio_columna in servicios_diarios.items():
            if servicio_columna in ["1 medida de jabón", "1 medida de suavizante", "1 medida de desmugrante",
                                    "1 bolsa chica", "1 bolsa mediana", "1 bolsa grande"]:
                total = df_hoy[df_hoy['Servicio'] == servicio_columna]['Cantidad'].sum() if servicio_columna in df_hoy['Servicio'].values else 0
                st.markdown(f"- {nombre}: {total}")

    else:
        st.info("No hay ventas registradas para hoy.")
except FileNotFoundError:
    st.info("No hay registros de ventas aún.")

# --- Botón para reiniciar todo ---
st.markdown("<h3 style='color:#C9A3F3'>⚠️ Reiniciar ventas</h3>", unsafe_allow_html=True)
if st.button("🔄 Reiniciar todo"):
    if os.path.exists("ventas_lavanderia.xlsx"):
        os.remove("ventas_lavanderia.xlsx")
        st.success("✅ Todas las ventas han sido eliminadas. Sistema reiniciado.")
    else:
        st.info("No hay registros previos para eliminar.")