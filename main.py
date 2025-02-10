from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
import sqlite3
import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Conexión a la base de datos SQLite
conn = sqlite3.connect('fhsp.db', check_same_thread=False)
cursor = conn.cursor()

# Crear tablas si no existen
cursor.execute('''
    CREATE TABLE IF NOT EXISTS universidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        ciudad TEXT NOT NULL,
        contacto TEXT NOT NULL,
        email TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS documentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        universidad_id INTEGER NOT NULL,
        nombre_archivo TEXT NOT NULL,
        fecha_subida TEXT NOT NULL,
        estado_aprobacion TEXT NOT NULL,
        FOREIGN KEY (universidad_id) REFERENCES universidades (id)
    )
''')
conn.commit()

# Modelos Pydantic
class Universidad(BaseModel):
    nombre: str
    ciudad: str
    contacto: str
    email: str

class Documento(BaseModel):
    universidad_id: int
    nombre_archivo: str
    estado_aprobacion: str

# Endpoints
@app.post("/universidades/")
async def registrar_universidad(universidad: Universidad):
    cursor.execute('''
        INSERT INTO universidades (nombre, ciudad, contacto, email)
        VALUES (?, ?, ?, ?)
    ''', (universidad.nombre, universidad.ciudad, universidad.contacto, universidad.email))
    conn.commit()
    return {"mensaje": "Universidad registrada con éxito"}

@app.get("/universidades/")
async def listar_universidades():
    cursor.execute('SELECT * FROM universidades')
    universidades = cursor.fetchall()
    return {"universidades": universidades}

@app.post("/documentos/")
async def subir_documento(universidad_id: int, file: UploadFile = File(...)):
    fecha_subida = datetime.datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO documentos (universidad_id, nombre_archivo, fecha_subida, estado_aprobacion)
        VALUES (?, ?, ?, ?)
    ''', (universidad_id, file.filename, fecha_subida, "Pendiente"))
    conn.commit()
    return {"mensaje": "Documento subido con éxito"}

@app.get("/documentos/{id_universidad}")
async def consultar_documentos(id_universidad: int):
    cursor.execute('SELECT * FROM documentos WHERE universidad_id = ?', (id_universidad,))
    documentos = cursor.fetchall()
    return {"documentos": documentos}

@app.get("/")
async def root():
    return {"message": "Bienvenido al sistema de gestión de documentos de FHSP"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hs2-4k5j.vercel.app/"],  # Reemplaza con lac URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)