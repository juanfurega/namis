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
    st.header("🥄 Productos y Recetas")
    
    # Usar una sola sesión para toda la pestaña
    with session_scope() as session:
        from namis.services import (
            crear_producto,
            obtener_producto,
            actualizar_precios_producto,
            obtener_receta,
            agregar_insumo_a_receta,
            agregar_producto_a_receta,
            eliminar_linea_receta,
            eliminar_producto,
            listar_insumos_actuales,
        )
        from namis.models.producto import Producto
        from sqlalchemy import select
        
        # Listar productos
        with st.expander("📋 Lista de Productos", expanded=True):
            try:
                productos = session.scalars(
                    select(Producto).order_by(Producto.nombre_producto)
                ).all()
                
                if productos:
                    data = []
                    for prod in productos:
                        data.append({
                            "ID": prod.id_producto,
                            "Nombre": prod.nombre_producto,
                            "Precio Venta ($)": prod.precio_actual,
                            "Costo Actual ($)": prod.costo_actual,
                            "Tamaño (g)": prod.tamano_g if prod.tamano_g else "-"
                        })
                    
                    st.dataframe(data, width='stretch', hide_index=True)
                else:
                    st.warning("No hay productos registrados")
            except Exception as e:
                st.error(f"Error al listar productos: {e}")
                import traceback
                st.error(traceback.format_exc())
        
        st.divider()
        
        # Crear producto
        st.subheader("➕ Crear Producto")
        
        try:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                nombre_producto = st.text_input("Nombre del Producto", key="nombre_producto")
            
            with col2:
                precio_venta = st.number_input(
                    "Precio de Venta ($)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="precio_producto"
                )
            
            with col3:
                tamano = st.number_input(
                    "Tamaño (g) - Opcional",
                    min_value=0,
                    step=1,
                    value=None,
                    key="tamano_producto"
                )
            
            if st.button("Crear Producto", key="btn_crear_producto"):
                if nombre_producto and precio_venta >= 0:
                    try:
                        nuevo_producto = crear_producto(
                            session,
                            nombre_producto,
                            precio_venta,
                            tamano_g=tamano if tamano > 0 else None
                        )
                        session.commit()
                        st.success(f"✅ Producto '{nombre_producto}' creado correctamente (ID: {nuevo_producto.id_producto})")
                        st.rerun()
                    except Exception as e:
                        session.rollback()
                        st.error(f"Error al crear producto: {e}")
                        import traceback
                        st.error(traceback.format_exc())
                else:
                    st.warning("Complete el nombre y el precio")
        except Exception as e:
            st.error(f"Error al crear producto: {e}")
            import traceback
            st.error(traceback.format_exc())
        
        st.divider()
        
        # Ver y editar receta
        st.subheader("👨‍🍳 Ver y Editar Receta")
        
        try:
            productos = session.scalars(
                select(Producto).order_by(Producto.nombre_producto)
            ).all()
            
            if productos:
                opciones_productos = {f"{p.id_producto} - {p.nombre_producto}": p.id_producto for p in productos}
                producto_seleccionado = st.selectbox(
                    "Seleccionar Producto",
                    options=list(opciones_productos.keys()),
                    key="select_producto_receta"
                )
                
                if producto_seleccionado:
                    id_producto = opciones_productos[producto_seleccionado]
                    
                    # Mostrar receta actual
                    try:
                        receta = obtener_receta(session, id_producto)
                        
                        st.info(f"**Costo Total de Receta:** ${receta.costo_total}")
                        
                        if receta.lineas:
                            lineas_data = []
                            for linea in receta.lineas:
                                lineas_data.append({
                                    "ID Línea": linea.id_receta,
                                    "Tipo": linea.tipo,
                                    "Componente": linea.nombre_componente,
                                    "Cantidad Necesaria": linea.cantidad_necesaria,
                                    "Unidad": linea.unidad,
                                    "Costo": linea.costo_linea
                                })
                            
                            st.dataframe(lineas_data, width='stretch', hide_index=True)
                        else:
                            st.warning("Este producto no tiene receta definida")
                    except Exception as e:
                        st.error(f"Error al obtener receta: {e}")
                    
                    # Agregar componente a receta
                    st.divider()
                    st.subheader("➕ Agregar a Receta")
                    
                    tipo_componente = st.radio(
                        "Tipo",
                        options=["Insumo", "Producto"],
                        key="tipo_componente",
                        horizontal=True
                    )
                    
                    if tipo_componente == "Insumo":
                        insumos = listar_insumos_actuales(session)
                        if insumos:
                            opciones_insumos = {f"{i.id_insumo} - {i.nombre_insumo} ({i.unidad_medida})": i.id_insumo for i in insumos}
                            insumo_seleccionado = st.selectbox(
                                "Seleccionar Insumo",
                                options=list(opciones_insumos.keys()),
                                key="select_insumo_receta"
                            )
                            cantidad = st.number_input(
                                "Cantidad Necesaria",
                                min_value=0.01,
                                step=0.01,
                                format="%.2f",
                                key="cantidad_insumo_receta"
                            )
                            
                            if st.button("Agregar Insumo a Receta", key="btn_agregar_insumo"):
                                if insumo_seleccionado and cantidad > 0:
                                    try:
                                        from decimal import Decimal
                                        id_insumo = opciones_insumos[insumo_seleccionado]
                                        agregar_insumo_a_receta(session, id_producto, id_insumo, Decimal(str(cantidad)))
                                        session.commit()
                                        st.success("✅ Insumo agregado a la receta")
                                        st.rerun()
                                    except Exception as e:
                                        session.rollback()
                                        st.error(f"Error al agregar insumo: {e}")
                                        import traceback
                                        st.error(traceback.format_exc())
                                else:
                                    st.warning("Seleccione un insumo y cantidad")
                        else:
                            st.warning("No hay insumos disponibles")
                    
                    else:  # Producto
                        opciones_productos_componente = {f"{p.id_producto} - {p.nombre_producto}": p.id_producto for p in productos if p.id_producto != id_producto}
                        if opciones_productos_componente:
                            producto_componente = st.selectbox(
                                "Seleccionar Producto Componente",
                                options=list(opciones_productos_componente.keys()),
                                key="select_producto_componente"
                            )
                            cantidad = st.number_input(
                                "Cantidad Necesaria (unidades)",
                                min_value=1,
                                step=1,
                                value=1,
                                key="cantidad_producto_receta"
                            )
                            
                            if st.button("Agregar Producto a Receta", key="btn_agregar_producto"):
                                if producto_componente and cantidad > 0:
                                    try:
                                        from decimal import Decimal
                                        id_componente = opciones_productos_componente[producto_componente]
                                        agregar_producto_a_receta(session, id_producto, id_componente, Decimal(str(cantidad)))
                                        session.commit()
                                        st.success("✅ Producto agregado como componente")
                                        st.rerun()
                                    except Exception as e:
                                        session.rollback()
                                        st.error(f"Error al agregar producto: {e}")
                                        import traceback
                                        st.error(traceback.format_exc())
                                else:
                                    st.warning("Seleccione un producto y cantidad")
                        else:
                            st.warning("No hay otros productos disponibles como componentes")
                    
                    # Eliminar línea de receta
                    st.divider()
                    st.subheader("🗑️ Eliminar de Receta")
                    
                    try:
                        receta_actual = obtener_receta(session, id_producto)
                        if receta_actual.lineas:
                            opciones_lineas = {
                                f"{l.id_receta} - {l.tipo}: {l.nombre_componente} ({l.cantidad_necesaria} {l.unidad})": l.id_receta 
                                for l in receta_actual.lineas
                            }
                            linea_a_eliminar = st.selectbox(
                                "Selecciona la línea a eliminar",
                                options=[""] + list(opciones_lineas.keys()),
                                key="select_linea_eliminar"
                            )
                            
                            if linea_a_eliminar and st.button("Eliminar Línea", key="btn_eliminar_linea"):
                                try:
                                    id_linea = opciones_lineas[linea_a_eliminar]
                                    productos_actualizados = eliminar_linea_receta(session, id_linea)
                                    session.commit()
                                    st.success("✅ Línea eliminada correctamente")
                                    if productos_actualizados:
                                        st.info(f"Productos con costo actualizado: {len(productos_actualizados)}")
                                    st.rerun()
                                except Exception as e:
                                    session.rollback()
                                    st.error(f"Error al eliminar línea: {e}")
                                    import traceback
                                    st.error(traceback.format_exc())
                        else:
                            st.info("No hay líneas para eliminar")
                    except Exception as e:
                        st.error(f"Error al cargar líneas: {e}")
            
            else:
                st.warning("No hay productos disponibles. Primero cree un producto.")
        except Exception as e:
            st.error(f"Error al cargar productos: {e}")
            import traceback
            st.error(traceback.format_exc())
        
        st.divider()
        
        # Actualizar precio de producto
        st.subheader("💲 Actualizar Precio de Venta")
        
        try:
            productos = session.scalars(
                select(Producto).order_by(Producto.nombre_producto)
            ).all()
            
            if productos:
                opciones_productos = {f"{p.id_producto} - {p.nombre_producto} (Precio actual: ${p.precio_actual})": p.id_producto for p in productos}
                producto_precio = st.selectbox(
                    "Seleccionar Producto",
                    options=list(opciones_productos.keys()),
                    key="select_producto_precio"
                )
                
                nuevo_precio = st.number_input(
                    "Nuevo Precio de Venta ($)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="nuevo_precio"
                )
                
                if st.button("Actualizar Precio", key="btn_actualizar_precio"):
                    if producto_precio and nuevo_precio >= 0:
                        try:
                            id_producto = opciones_productos[producto_precio]
                            actualizar_precios_producto(session, id_producto, nuevo_precio)
                            session.commit()
                            st.success("✅ Precio actualizado correctamente")
                            st.rerun()
                        except Exception as e:
                            session.rollback()
                            st.error(f"Error al actualizar precio: {e}")
                            import traceback
                            st.error(traceback.format_exc())
                    else:
                        st.warning("Seleccione un producto y precio válido")
            else:
                st.warning("No hay productos disponibles")
        except Exception as e:
            st.error(f"Error al actualizar precio: {e}")
            import traceback
            st.error(traceback.format_exc())
        
        st.divider()
        
        # Eliminar producto completo (desplegable)
        with st.expander("❌ Eliminar Producto"):
            try:
                productos = session.scalars(
                    select(Producto).order_by(Producto.nombre_producto)
                ).all()
                
                if productos:
                    opciones_productos = {f"{p.id_producto} - {p.nombre_producto}": p.id_producto for p in productos}
                    producto_eliminar = st.selectbox(
                        "Seleccionar Producto a Eliminar",
                        options=[""] + list(opciones_productos.keys()),
                        key="select_producto_eliminar"
                    )
                    
                    if producto_eliminar:
                        try:
                            producto_actual = obtener_producto(session, opciones_productos[producto_eliminar])
                            st.warning(f"⚠️ Esto eliminará completamente el producto '{producto_actual.nombre_producto}' y su receta de la base de datos")
                            
                            if st.button("Eliminar Producto", key="btn_eliminar_producto"):
                                try:
                                    id_producto = opciones_productos[producto_eliminar]
                                    eliminar_producto(session, id_producto)
                                    session.commit()
                                    st.success(f"✅ Producto '{producto_actual.nombre_producto}' eliminado completamente")
                                    st.rerun()
                                except Exception as e:
                                    session.rollback()
                                    st.error(f"Error al eliminar producto: {e}")
                                    import traceback
                                    st.error(traceback.format_exc())
                        except Exception as e:
                            st.error(f"Error al cargar producto: {e}")
                else:
                    st.warning("No hay productos disponibles para eliminar")
            except Exception as e:
                st.error(f"Error al cargar productos: {e}")
                import traceback
                st.error(traceback.format_exc())

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
