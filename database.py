from pymongo import MongoClient

def conectar_bd():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['prueba3'] 
        return db
    except Exception as e:
        print(f"Error al conectar con MongoDB: {e}")
        return None