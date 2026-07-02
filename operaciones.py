def listar_eventos(db):
    """Cubre 3.1.1.I.2 y 3.1.1.I.3: Lista y permite filtrar eventos."""
    print("\n" + "="*40)
    print("        LISTADO GENERAL DE EVENTOS")
    print("="*40)
    
    filtro = {}
    categoria = input("Ingresa una categoría para filtrar (o presiona Enter para ver todos): ").strip()
    
    if categoria:
        filtro["categoria"] = {"$regex": categoria, "$options": "i"}

    try:
        coleccion = db['eventos']
        eventos = coleccion.find(filtro, {"_id": 0, "codigo": 1, "nombre": 1, "fecha": 1, "lugar": 1, "categoria": 1})
        
        cantidad = 0
        for evento in eventos:
            cantidad += 1
            print(f"\n Código: {evento.get('codigo')}")
            print(f"   Evento:    {evento.get('nombre')}")
            print(f"   Fecha:     {evento.get('fecha')}")
            print(f"   Lugar:     {evento.get('lugar')}")
            print(f"   Categoría: {evento.get('categoria')}")
        
        if cantidad == 0:
            print("No se encontraron eventos con esos criterios.")
    except Exception as e:
        print(f" Error al consultar la base de datos: {e}")


def buscar_invitados_regex(db):
    print("\n" + "="*40)
    print("       BÚSQUEDA FILTRADA DE INVITADOS")
    print("="*40)
    
    while True:
        termino = input("Ingresa parte del nombre o dominio de correo (ej: @empresa.cl): ").strip()
        if termino:
            break
        print(" Error: El término de búsqueda no puede estar vacío.")
        
    filtro = {
        "$or": [
            {"nombre": {"$regex": termino, "$options": "i"}},
            {"correo": {"$regex": termino, "$options": "i"}}
        ]
    }
    
    try:
        coleccion = db['invitados']
        resultados = coleccion.find(filtro)
        encontrados = False
        
        print(f"\n🔍 Resultados para '{termino}':")
        for res in resultados:
            encontrados = True
            print(f" {res.get('nombre')} | RUT: {res.get('rut')} | Correo: {res.get('correo')} | Estado: {res.get('estado')}")
            
        if not encontrados:
            print("No se encontraron invitados.")
    except Exception as e:
        print(f" Error al consultar la base de datos: {e}")


def validar_acceso_evento(db):
    """Cubre 3.1.3.I.6 y 3.1.4.I.8: Búsqueda en subdocumentos cruzando colecciones con $lookup."""
    print("\n" + "="*40)
    print("        VALIDACIÓN DE ACCESO ($lookup)")
    print("="*40)
    
    while True:
        correo_invitado = input("Ingresa el correo electrónico del invitado: ").strip()
        codigo_evento = input("Ingresa el código del evento (ej. EVT-2025-001): ").strip()
        if correo_invitado and codigo_evento:
            break
        print(" Error: Debes ingresar tanto el correo como el código del evento.")

    # Pipeline avanzado exigido por la rúbrica
    pipeline = [
        {"$match": {"codigo": codigo_evento}},
        {"$unwind": "$invitados"},
        {"$match": {"invitados.estado": "confirmado"}},
        {
            "$lookup": {
                "from": "invitados",
                "localField": "invitados.rut",
                "foreignField": "rut",
                "as": "datos_invitado"
            }
        },
        {"$unwind": "$datos_invitado"},
        {
            "$match": {
                "datos_invitado.correo": correo_invitado,
                "datos_invitado.estado": "activo"
            }
        }
    ]
    
    try:
        coleccion = db['eventos']
        resultados = list(coleccion.aggregate(pipeline))
        
        if resultados:
            datos_evento = resultados[0]
            invitado = datos_evento['datos_invitado']
            print(f"\n ACCESO PERMITIDO")
            print(f"   Invitado: {invitado.get('nombre')} (RUT: {invitado.get('rut')})")
            print(f"   Evento:   {datos_evento.get('nombre')} en {datos_evento.get('lugar')}")
        else:
            print("\n ACCESO DENEGADO: El invitado no existe, está inactivo o no está confirmado para este evento.")
    except Exception as e:
        print(f" Error al consultar la base de datos: {e}")


def top_eventos_confirmados(db):
    """Cubre 3.1.3.I.7: Top 3 mediante agregación de subdocumentos."""
    print("\n" + "="*40)
    print("          TOP 3 EVENTOS POPULARES")
    print("="*40)
    
    pipeline = [
        {"$unwind": "$invitados"},
        {"$match": {"invitados.estado": "confirmado"}},
        {
            "$group": {
                "_id": "$codigo",
                "nombre_evento": {"$first": "$nombre"},
                "lugar": {"$first": "$lugar"},
                "total_confirmados": {"$sum": 1}
            }
        },
        {"$sort": {"total_confirmados": -1}},
        {"$limit": 3}
    ]
    
    try:
        coleccion = db['eventos']
        resultados = list(coleccion.aggregate(pipeline))
        
        if not resultados:
            print("No hay registros de invitados confirmados.")
            return
            
        for puesto, res in enumerate(resultados, 1):
            print(f"\n Puesto #{puesto}")
            print(f"   Evento:       {res.get('nombre_evento')} (Código: {res.get('_id')})")
            print(f"   Lugar:        {res.get('lugar')}")
            print(f"   Confirmados:  {res.get('total_confirmados')} personas")
    except Exception as e:
        print(f" Error al ejecutar la agregación: {e}")