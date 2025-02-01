from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import numpy as np
import matplotlib.pyplot as plt
import os

# Configuración de FastAPI y Jinja2
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Carpeta para guardar el gráfico generado
OUTPUT_FOLDER = "static"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "fractal.png")

# Función para calcular el fractal con mucho detalle
def calcular_fractal(x_min, x_max, y_min, y_max, ancho, alto, iteraciones_max):
    # Crear el plano complejo
    x = np.linspace(x_min, x_max, ancho)
    y = np.linspace(y_min, y_max, alto)
    X, Y = np.meshgrid(x, y)
    c = X + 1j * Y

    # Inicializar z y el contador de iteraciones
    z = np.zeros(c.shape, dtype=complex)
    iteraciones = np.zeros(c.shape, dtype=int)

    # Calcular el fractal con iteraciones máximas dinámicas
    for i in range(iteraciones_max):
        mascara = np.abs(z) <= 2
        z[mascara] = z[mascara] ** 2 + c[mascara]
        iteraciones[mascara] += 1

    # Normalizar las iteraciones para suavizar el color
    iteraciones = np.log(iteraciones + 1) / np.log(iteraciones_max)
    return iteraciones

# Función para guardar el fractal como imagen
def guardar_fractal(iteraciones, x_min, x_max, y_min, y_max, output_path):
    plt.figure(figsize=(12, 12), dpi=150)  # Aumentar resolución
    plt.imshow(iteraciones, extent=(x_min, x_max, y_min, y_max), cmap="inferno", origin="lower")
    plt.colorbar(label="Profundidad de iteración", orientation="vertical")
    plt.title("Fractal de Mandelbrot (Zoom detallado)", fontsize=14, color="white")
    plt.xlabel("Re(c)", fontsize=12, color="white")
    plt.ylabel("Im(c)", fontsize=12, color="white")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

# Ruta principal para el formulario
@app.get("/", response_class=HTMLResponse)
async def formulario(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta para generar el fractal
@app.post("/generar", response_class=HTMLResponse)
async def generar_fractal(
    request: Request,
    x_min: float = Form(),
    x_max: float = Form(),
    y_min: float = Form(),
    y_max: float = Form(),
    ancho: int = Form(),
    alto: int = Form(),
    iteraciones_max: int = Form(),
):
    # Calcular el fractal
    iteraciones = calcular_fractal(x_min, x_max, y_min, y_max, ancho, alto, iteraciones_max)
    guardar_fractal(iteraciones, x_min, x_max, y_min, y_max, OUTPUT_FILE)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "imagen_url": "/static/fractal.png",
            "x_min": x_min,
            "x_max": x_max,
            "y_min": y_min,
            "y_max": y_max,
        },
    )

# Ruta para servir el archivo generado
@app.get("/static/fractal.png", response_class=FileResponse)
async def servir_fractal():
    return FileResponse(OUTPUT_FILE)
