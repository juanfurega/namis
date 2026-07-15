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
                        st.warning("Completa todos los campos correctamente")
            else:
                st.warning("No hay insumos disponibles. Primero crea un insumo.")
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
                    st.warning("Completa ambos campos")
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
                        "Selecciona el insumo a eliminar",
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
        st.subheader("👩‍🍳 Ver y Editar Receta")
        
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
    
    # Carrito de productos
    if "carrito_venta" not in st.session_state:
        st.session_state.carrito_venta = []
    
    # Formulario para registrar venta
    st.subheader("📝 Registrar Nueva Venta")
    
    with session_scope() as session:
        from namis.services import (
            actualizar_estado_deudor,
            registrar_venta,
            listar_ultimas_ventas,
            ItemVentaInput,
        )
        from namis.models.producto import Producto
        from namis.models.receta import Receta
        from sqlalchemy import select
        from decimal import Decimal
        from datetime import datetime
        
        # Obtener productos con receta
        productos_con_receta = session.scalars(
            select(Producto)
            .join(Receta, Receta.id_producto == Producto.id_producto)
            .where(Receta.id_producto_componente.is_(None))
            .distinct()
            .order_by(Producto.nombre_producto)
        ).all()
        
        with st.form("form_venta"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_cliente = st.text_input("Nombre del cliente *")
                medio_comunicacion = st.selectbox(
                    "Medio de comunicación",
                    options=["", "Wsp", "Ig", "Msn"],
                    key="medio_comunicacion"
                )
            
            with col2:
                medio_pago = st.selectbox(
                    "Medio de pago",
                    options=["", "Transferencia", "Efectivo"],
                    key="medio_pago"
                )
                costo_envio = st.number_input(
                    "Costo de envío",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=0.0
                )
            
            if productos_con_receta:
                st.subheader("📦 Productos")
                
                # Agregar productos al carrito
                col_prod, col_cant = st.columns([3, 1])
                
                with col_prod:
                    producto_seleccionado = st.selectbox(
                        "Seleccionar producto",
                        options=[""] + [f"{p.id_producto} - {p.nombre_producto}" for p in productos_con_receta],
                        key="producto_seleccionado"
                    )
                
                with col_cant:
                    cantidad = st.number_input("Cantidad", min_value=1, value=1, key="cantidad_producto")
                
                agregar = st.form_submit_button("Agregar al carrito", use_container_width=True)
                if agregar and producto_seleccionado:
                    id_producto = int(producto_seleccionado.split(" - ")[0])
                    st.session_state.carrito_venta.append(
                        {"id_producto": id_producto, "cantidad": cantidad}
                    )
                    st.rerun()
                
                # Mostrar carrito actual
                if st.session_state.carrito_venta:
                    st.write("🛒 Productos en el carrito:")
                    for i, item in enumerate(st.session_state.carrito_venta):
                        producto = session.get(Producto, item["id_producto"])
                        st.write(f"- {producto.nombre_producto} x {item['cantidad']}")
                else:
                    st.info("No hay productos en el carrito")
            else:
                st.warning("No hay productos con receta disponibles. Primero cree productos con recetas.")
            
            observaciones = st.text_area("Observaciones (opcional)", key="observaciones_venta")
            
            submitted = st.form_submit_button("Registrar Venta")
            
            if submitted:
                if not nombre_cliente:
                    st.error("El nombre del cliente es obligatorio")
                elif not st.session_state.carrito_venta:
                    st.error("Debe agregar al menos un producto al carrito")
                else:
                    try:
                        items = [
                            ItemVentaInput(
                                id_producto=item["id_producto"],
                                cantidad=item["cantidad"]
                            )
                            for item in st.session_state.carrito_venta
                        ]
                        
                        venta_registrada = registrar_venta(
                            session,
                            nombre_cliente=nombre_cliente,
                            items=items,
                            medio_pago=medio_pago.lower() if medio_pago else None,
                            red_social=medio_comunicacion.lower() if medio_comunicacion else None,
                            costo_envio=Decimal(str(costo_envio)),
                            observaciones=observaciones if observaciones else None,
                        )
                        
                        st.success(f"✅ Venta registrada exitosamente. ID: {venta_registrada.id_venta}")
                        st.session_state.carrito_venta = []
                        
                    except Exception as e:
                        st.error(f"Error al registrar venta: {e}")
                        import traceback
                        st.error(traceback.format_exc())
    
    # Botón para limpiar carrito (fuera del formulario)
    if st.session_state.carrito_venta:
        if st.button("🗑️ Limpiar carrito"):
            st.session_state.carrito_venta = []
            st.rerun()
    
    st.divider()
    
    # Lista de últimas 20 ventas (usando una nueva sesión)
    st.subheader("📋 Últimas 20 Ventas")
    
    with session_scope() as session:
        from namis.services import listar_ultimas_ventas, eliminar_venta
        
        try:
            ventas = listar_ultimas_ventas(session, limite=20)
            
            if ventas:
                # Preparar datos para mostrar
                dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                
                datos_ventas = []
                for venta in ventas:
                    if venta.fecha:
                        fecha = venta.fecha
                        dia_semana = dias_semana[fecha.weekday()]
                        fecha_formateada = fecha.strftime("%d/%m/%Y")
                    else:
                        dia_semana = "N/A"
                        fecha_formateada = "N/A"
                    
                    # Obtener productos de la venta (formato lista vertical con HTML)
                    productos_str = "<br>".join(
                        [f"• {d.producto.nombre_producto} x {d.cantidad}" for d in venta.detalles]
                    )
                    
                    promocion_str = f"${venta.monto_descontado}" if venta.monto_descontado > 0 else "No"
                    medio_pago_str = venta.medio_pago.capitalize() if venta.medio_pago else "N/A"
                    medio_com_str = venta.red_social.upper() if venta.red_social else "N/A"
                    envio_str = f"${venta.costo_envio}" if venta.costo_envio > 0 else "$0"
                    deudor_str = "✅" if venta.es_deudor else ""
                    
                    datos_ventas.append({
                        "ID": venta.id_venta,
                        "Día": dia_semana,
                        "Fecha": fecha_formateada,
                        "Cliente": venta.cliente.nombre,
                        "Medio Com.": medio_com_str,
                        "Medio Pago": medio_pago_str,
                        "Productos": productos_str,
                        "Envío": envio_str,
                        "Promoción": promocion_str,
                        "Total": f"${venta.total_cobrado}",
                        "Observaciones": venta.observaciones or "",
                        "Deudor": deudor_str,
                    })
                
                # Crear tabla HTML con colores para modo claro
                html_table = """
                <style>
                    .ventas-table {
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 14px;
                    }
                    .ventas-table th {
                        border: 1px solid #ddd;
                        padding: 10px;
                        text-align: left;
                        background-color: #f0f0f0;
                        color: #000;
                        font-weight: bold;
                    }
                    .ventas-table td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        color: #333;
                        vertical-align: top;
                    }
                    .ventas-table tr:hover {
                        background-color: #f5f5f5;
                    }
                </style>
                <table class='ventas-table'>
                """
                html_table += "<thead><tr>"
                for col in datos_ventas[0].keys():
                    html_table += f"<th>{col}</th>"
                html_table += "</tr></thead><tbody>"
                
                for row in datos_ventas:
                    html_table += "<tr>"
                    for col, val in row.items():
                        html_table += f"<td>{val}</td>"
                    html_table += "</tr>"
                
                html_table += "</tbody></table>"
                st.markdown(html_table, unsafe_allow_html=True)
                
                # Sección para marcar deudor
                st.subheader("📝 Marcar/Desmarcar Deudor")
                venta_seleccionada = st.selectbox(
                    "Seleccionar venta",
                    options=[""] + [f"{v.id_venta} - {v.cliente.nombre} - {v.fecha.strftime('%d/%m/%Y') if v.fecha else 'N/A'}" for v in ventas],
                    key="venta_deudor"
                )
                
                if venta_seleccionada:
                    id_venta = int(venta_seleccionada.split(" - ")[0])
                    venta_actual = next((v for v in ventas if v.id_venta == id_venta), None)
                    
                    if venta_actual:
                        col_deudor, col_accion = st.columns([1, 1])
                        with col_deudor:
                            nuevo_estado_deudor = st.checkbox(
                                "Marcar como Deudor",
                                value=venta_actual.es_deudor,
                                key=f"deudor_{id_venta}"
                            )
                        with col_accion:
                            if st.button("Actualizar Estado", key=f"btn_deudor_{id_venta}"):
                                try:
                                    actualizar_estado_deudor(session, id_venta, nuevo_estado_deudor)
                                    session.commit()
                                    st.success(f"✅ Estado de deudor actualizado para venta {id_venta}")
                                    st.rerun()
                                except Exception as e:
                                    session.rollback()
                                    st.error(f"Error al actualizar estado: {e}")
                                    import traceback
                                    st.error(traceback.format_exc())
                
                # Sección para eliminar venta
                st.subheader("🗑️ Eliminar Venta")
                venta_eliminar = st.selectbox(
                    "Seleccionar venta para eliminar",
                    options=[""] + [f"{v.id_venta} - {v.cliente.nombre} - {v.fecha.strftime('%d/%m/%Y') if v.fecha else 'N/A'} - ${v.total_cobrado}" for v in ventas],
                    key="venta_eliminar"
                )
                
                if venta_eliminar:
                    id_venta_eliminar = int(venta_eliminar.split(" - ")[0])
                    venta_eliminar_obj = next((v for v in ventas if v.id_venta == id_venta_eliminar), None)
                    
                    if venta_eliminar_obj:
                        st.warning(f"⚠️ Estás a punto de eliminar la venta {id_venta_eliminar} de {venta_eliminar_obj.cliente.nombre} por ${venta_eliminar_obj.total_cobrado}")
                        
                        if st.button("Confirmar Eliminación", key=f"btn_eliminar_{id_venta_eliminar}", type="primary"):
                            try:
                                eliminar_venta(session, id_venta_eliminar)
                                session.commit()
                                st.success(f"✅ Venta {id_venta_eliminar} eliminada exitosamente")
                                st.rerun()
                            except Exception as e:
                                session.rollback()
                                st.error(f"Error al eliminar venta: {e}")
                                import traceback
                                st.error(traceback.format_exc())
            else:
                st.info("No hay ventas registradas")
                
        except Exception as e:
            st.error(f"Error al cargar ventas: {e}")
            import traceback
            st.error(traceback.format_exc())

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
