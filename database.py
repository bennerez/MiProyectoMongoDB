from pymongo import MongoClient

def conectar_bd():
    """Establece la conexión con la base de datos MongoDB."""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['prueba3'] 
        return db
    except Exception as e:
        print(f"Error al conectar con MongoDB: {e}")
        return None