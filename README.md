# Namis - Sistema de Gestión de Yogurtería

Sistema de gestión integral para una yogurtería (PyME), con interfaz web construida en Streamlit. Permite administrar insumos, productos, recetas, ventas, promociones y balance financiero desde un mismo lugar, reemplazando planillas manuales por una base de datos relacional con lógica de negocio centralizada.

El proyecto nació como una solución real para el negocio y fue evolucionando hacia una arquitectura más ordenada (modelos, servicios y capa de presentación separados) pensando tanto en mantenibilidad como en mostrar el proceso de diseño como parte de mi portfolio.

## Características

- **Gestión de Insumos**: Registrar materia prima con historial de precios, permitiendo trackear variaciones de costos a lo largo del tiempo.
- **Productos y Recetas**: Crear productos con recetas que pueden usar insumos directos o sub-recetas (recetas anidadas), calculando costos de forma jerárquica.
- **Ventas**: Registrar ventas con clientes, medios de pago, promociones aplicadas y envíos, con detalle de productos por venta.
- **Promociones**: Configurar promociones con descuentos basados en requisitos de productos (combos, cantidades mínimas, etc.).
- **Balance**: Visualizar el balance financiero del negocio a partir de ventas, costos de insumos y otros movimientos.

## Tecnologías

- **Python 3.14**
- **Streamlit** — interfaz web
- **SQLAlchemy 2.0** — ORM
- **MySQL 8.0** — base de datos
- **Docker / Docker Compose** — contenedorización del entorno de base de datos

## Arquitectura

El proyecto sigue una separación simple en capas dentro de `src/namis/`:

- **`database.py`**: configuración del engine de SQLAlchemy y manejo de sesiones.
- **`models.py`**: modelos ORM que representan las tablas de la base de datos (clientes, productos, ventas, insumos, recetas, promociones, etc.).
- **`services.py`**: lógica de negocio (cálculo de costos de recetas, aplicación de promociones, registro de ventas, historial de precios).
- **`streamlit_app.py`**: capa de presentación, consume los servicios y expone la interfaz de usuario.

Esta separación busca que la lógica de negocio no dependa de Streamlit, facilitando testing y una eventual migración de interfaz (por ejemplo, a una API REST) sin reescribir la lógica central.

## Instalación

### Prerrequisitos

- Python 3.8 o superior
- Docker y Docker Compose

### Configuración

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/juanfurega/namis.git
   cd namis
   ```
2. Copiar el archivo de variables de entorno:
   ```bash
   cp .env.example .env
   ```
3. Editar `.env` con las credenciales de la base de datos (usar las credenciales de `docker-compose.yml` para desarrollo).

### Instalar dependencias

Se recomienda usar un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Iniciar la base de datos

```bash
docker-compose up -d
```

Esto iniciará MySQL 8.0 en el puerto 3307 y ejecutará automáticamente el `schema.sql` para crear las tablas.

Para verificar que el contenedor está corriendo correctamente:

```bash
docker-compose ps
docker-compose logs -f mysql
```

## Uso

Ejecutar la aplicación Streamlit:

```bash
streamlit run streamlit_app.py
```

La interfaz estará disponible en `http://localhost:8501`

### Flujo de trabajo típico

1. Cargar insumos y sus precios iniciales.
2. Crear recetas asociando insumos (o sub-recetas ya existentes).
3. Crear productos a partir de esas recetas.
4. Configurar promociones si aplica.
5. Registrar ventas a medida que ocurren.
6. Consultar el balance para ver el estado financiero del negocio.

## Estructura del Proyecto

```
Namis/
├── src/namis/           # Código fuente del proyecto
│   ├── database.py      # Configuración de base de datos
│   ├── models.py        # Modelos SQLAlchemy
│   └── services.py      # Lógica de negocio
├── streamlit_app.py     # Interfaz principal Streamlit
├── schema.sql           # Esquema de base de datos
├── docker-compose.yml   # Configuración Docker
├── requirements.txt     # Dependencias Python
└── .env.example         # Ejemplo de variables de entorno
```

## Estructura de la Base de Datos

| Tabla | Descripción |
|---|---|
| `clientes` | Información de clientes |
| `productos` | Productos finales (yogurt) |
| `promociones` | Configuración de descuentos |
| `promocion_requisitos` | Requisitos para aplicar promociones |
| `ventas` | Registro de ventas |
| `detalle_ventas` | Detalle de productos en cada venta |
| `insumos` | Materia prima |
| `insumos_historial_precios` | Historial de precios de insumos |
| `recetas` | Recetas de productos (pueden usar insumos o sub-recetas) |

Un aspecto particular del modelo es que las **recetas pueden componerse de otras recetas** (sub-recetas), lo que permite representar productos compuestos (por ejemplo, un yogurt con topping que a su vez tiene su propia receta) sin duplicar información de costos.

## Variables de Entorno

- `DATABASE_URL`: URL de conexión a MySQL (formato: `mysql+pymysql://usuario:contraseña@host:puerto/nombre_bd?charset=utf8mb4`)

Para desarrollo con Docker:
```
DATABASE_URL=mysql+pymysql://namis:namis_secret@127.0.0.1:3307/namis_yogur?charset=utf8mb4
```

## Comandos útiles

```bash
# Detener y eliminar los contenedores
docker-compose down

# Detener y eliminar contenedores + volúmenes (borra los datos)
docker-compose down -v

# Reiniciar la base de datos desde cero
docker-compose down -v && docker-compose up -d
```

## Roadmap / Mejoras futuras

- [ ] Reportes exportables (PDF/Excel) del balance financiero
- [ ] Control de stock de insumos con alertas de reposición
- [ ] Autenticación de usuarios y roles (admin / vendedor)

## Notas de desarrollo

Este proyecto fue desarrollado con asistencia de herramientas de generación de código basadas en IA (Cursor), utilizadas como acelerador dentro de un proceso de diseño e iteración propio: definición del modelo de datos, revisión de la lógica de negocio y validación funcional contra las necesidades reales del negocio.
