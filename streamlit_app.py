"""
Interfaz Streamlit para Namis - Sistema de gestión de yogurtería
"""

import streamlit as st
from namis.database import session_scope

st.set_page_config(
    page_title="Namis - Gestión Yogurtería",
    page_icon="⭐",
    layout="wide"
)

st.title("Nami's")

# Barra lateral con información de conexión
with st.sidebar:
    st.header("Información")
    try:
        with session_scope() as session:
            st.success("✅ Conectado a la base de datos")
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")

# Pestañas principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Insumos",
    "Productos y Recetas",
    "Ventas",
    "Promociones",
    "Balance"
])

with tab1:
    st.header("📦 Gestión de Insumos")
    
    # Usar una sola sesión para toda la pestaña
    with session_scope() as session:
        from namis.services import listar_insumos_actuales, crear_insumo, registrar_compra_insumo, eliminar_insumo
        
        # Listar insumos actuales
        with st.expander("📋 Lista de Insumos", expanded=True):
            try:
                insumos = listar_insumos_actuales(session)
                
                if insumos:
                    data = []
                    for insumo in insumos:
                        if insumo.precio_vigente:
                            cantidad_paquete = insumo.precio_vigente.cantidad_paquete
                            precio_pagado = insumo.precio_vigente.precio_paquete
                            fecha_precio = insumo.precio_vigente.fecha_registro.strftime("%d/%m/%Y")
                        else:
                            cantidad_paquete = "-"
                            precio_pagado = "-"
                            fecha_precio = "-"
                        
                        data.append({
                            "ID": insumo.id_insumo,
                            "Nombre": insumo.nombre_insumo,
                            "Cantidad Paquete": cantidad_paquete,
                            "Unidad": insumo.unidad_medida,
                            "Precio Pagado ($)": precio_pagado,
                            "Última Actualización": fecha_precio
                        })
                    
                    st.dataframe(data, width='stretch', hide_index=True)
                else:
                    st.warning("No hay insumos registrados")
            except Exception as e:
                st.error(f"Error al listar insumos: {e}")
                import traceback
                st.error(traceback.format_exc())
        
        st.divider()
        
        # Registrar compra de insumo
        st.subheader("🛒 Registrar Compra de Insumo")
        
        try:
            insumos = listar_insumos_actuales(session)
            
            if insumos:
                opciones_insumos = {f"{i.nombre_insumo} ({i.unidad_medida})": i.id_insumo for i in insumos}
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    insumo_seleccionado = st.selectbox(
                        "Seleccionar Insumo",
                        options=list(opciones_insumos.keys()),
                        key="select_insumo_compra"
                    )
                
                with col2:
                    cantidad = st.number_input(
                        "Cantidad del Paquete",
                        min_value=0.01,
                        step=0.1,
                        format="%.2f",
                        key="cantidad_compra"
                    )
                
                with col3:
                    precio_pagado = st.number_input(
                        "Precio Pagado ($)",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        key="precio_compra"
                    )
                
                if st.button("Registrar Compra", key="btn_registrar_compra"):
                    if insumo_seleccionado and cantidad > 0 and precio_pagado >= 0:
                        try:
                            id_insumo = opciones_insumos[insumo_seleccionado]
                            resultado = registrar_compra_insumo(
                                session,
                                id_insumo,
                                cantidad,
                                precio_pagado
                            )
                            session.commit()
                            st.success(f"✅ Compra registrada correctamente")
                            st.info(f"ID Historial: {resultado.id_historial}")
                            if resultado.productos_costo_actualizado:
                                st.info(f"Productos con costo actualizado: {len(resultado.productos_costo_actualizado)}")
                            st.rerun()
                        except Exception as e:
                            session.rollback()
                            st.error(f"Error al registrar compra: {e}")
                            import traceback
                            st.error(traceback.format_exc())
                    else:
                        st.warning("Complete todos los campos correctamente")
            else:
                st.warning("No hay insumos disponibles. Primero cree un insumo.")
        except Exception as e:
            st.error(f"Error al cargar insumos: {e}")
            import traceback
            st.error(traceback.format_exc())
        
        st.divider()
        
        # Crear nuevo insumo (no desplegable)
        st.subheader("➕ Crear Insumo")
        
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_nuevo = st.text_input("Nombre del Insumo", key="nombre_nuevo_insumo")
            
            with col2:
                unidad_medida = st.text_input("Unidad de Medida (ej: kg, l, un)", key="unidad_nuevo_insumo")
            
            if st.button("Crear Insumo", key="btn_crear_insumo"):
                if nombre_nuevo and unidad_medida:
                    try:
                        nuevo_insumo = crear_insumo(session, nombre_nuevo, unidad_medida)
                        session.commit()
                        st.success(f"✅ Insumo '{nombre_nuevo}' creado correctamente (ID: {nuevo_insumo.id_insumo})")
                        st.rerun()
                    except Exception as e:
                        session.rollback()
                        st.error(f"Error al crear insumo: {e}")
                        import traceback
                        st.error(traceback.format_exc())
                else:
                    st.warning("Complete ambos campos")
        except Exception as e:
            st.error(f"Error al crear insumo: {e}")
            import traceback
            st.error(traceback.format_exc())
        
        st.divider()
        
        # Eliminar insumo (desplegable)
        with st.expander("🗑️ Eliminar Insumo"):
            try:
                insumos = listar_insumos_actuales(session)
                
                if insumos:
                    opciones_eliminar = {f"{i.id_insumo} - {i.nombre_insumo}": i.id_insumo for i in insumos}
                    insumo_a_eliminar = st.selectbox(
                        "Seleccionar insumo a eliminar",
                        options=[""] + list(opciones_eliminar.keys()),
                        key="select_eliminar_insumo"
                    )
                    
                    if insumo_a_eliminar and st.button("Eliminar Insumo", key="btn_eliminar_insumo"):
                        try:
                            id_insumo = opciones_eliminar[insumo_a_eliminar]
                            eliminar_insumo(session, id_insumo)
                            session.commit()
                            st.success(f"✅ Insumo eliminado correctamente")
                            st.rerun()
                        except Exception as e:
                            session.rollback()
                            st.error(f"Error al eliminar insumo: {e}")
                            import traceback
                            st.error(traceback.format_exc())
                else:
                    st.warning("No hay insumos para eliminar")
            except Exception as e:
                st.error(f"Error al cargar insumos: {e}")
                import traceback
                st.error(traceback.format_exc())

with tab2:
    st.header("🍦 Productos y Recetas")
    st.info("Módulo de productos y recetas en desarrollo")
    # TODO: Implementar gestión de productos y recetas
    # - Listar productos
    # - Crear/actualizar producto
    # - Ver y editar recetas
    # - Agregar insumos o sub-recetas
    # - Calcular costos

with tab3:
    st.header("💰 Ventas")
    st.info("Módulo de ventas en desarrollo")
    # TODO: Implementar gestión de ventas
    # - Calcular presupuesto
    # - Registrar venta
    # - Ver historial de ventas
    # - Selección de cliente
    # - Aplicación automática de promociones

with tab4:
    st.header("🏷️ Promociones")
    st.info("Módulo de promociones en desarrollo")
    # TODO: Implementar gestión de promociones
    # - Listar promociones
    # - Crear nueva promoción
    # - Editar requisitos
    # - Activar/desactivar promociones

with tab5:
    st.header("📊 Balance")
    st.info("Módulo de balance en desarrollo")
    # TODO: Implementar balance
    # - Resumen del día
    # - Calendario mensual
    # - Historial por cliente
    # - Detalle de venta específica
