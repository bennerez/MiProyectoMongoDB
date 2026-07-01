
def listar_eventos(db):
    print("\n" + "="*40)
    print("        LISTADO GENERAL DE EVENTOS")
    print("="*40)
    
    coleccion = db['eventos']
    eventos = coleccion.find({}, {"_id": 0, "codigo": 1, "nombre": 1, "fecha": 1, "lugar": 1, "categoria": 1})
    
    cantidad = 0
    for evento in eventos:
        cantidad += 1
        print(f"\n Código: {evento.get('codigo')}")
        print(f"   Evento:    {evento.get('nombre')}")
        print(f"   Fecha:     {evento.get('fecha')}")
        print(f"   Lugar:     {evento.get('lugar')}")
        print(f"   Categoría: {evento.get('categoria')}")
    
    if cantidad == 0:
        print("No se encontraron eventos.")

def buscar_invitados_regex(db):
    print("\n" + "="*40)
    print("       BÚSQUEDA FILTRADA DE INVITADOS")
    print("="*40)
    
    termino = input("Ingresa parte del nombre o correo a buscar: ").strip()
    if not termino:
        print("El término de búsqueda no puede estar vacío.")
        return
        
    coleccion = db['invitados']
    filtro = {
        "$or": [
            {"nombre": {"$regex": termino, "$options": "i"}},
            {"correo": {"$regex": termino, "$options": "i"}}
        ]
    }
    
    resultados = coleccion.find(filtro)
    encontrados = False
    
    print(f"\n Resultados para '{termino}':")
    for res in resultados:
        encontrados = True
        print(f" {res.get('nombre')} | RUT: {res.get('rut')} | Correo: {res.get('correo')} | Estado: {res.get('estado')}")
        
    if not encontrados:
        print("No se encontraron invitados.")

def validar_acceso_evento(db):
    print("\n" + "="*40)
    print("        VALIDACIÓN DE ACCESO")
    print("="*40)
    
    correo_invitado = input("Ingresa el correo electrónico del invitado: ").strip()
    codigo_evento = input("Ingresa el código del evento (ej. EVT-2025-001): ").strip()
    
    invitado_doc = db['invitados'].find_one({"correo": correo_invitado})
    
    if not invitado_doc:
        print("\n ACCESO DENEGADO: El correo ingresado no está registrado.")
        return
        
    if invitado_doc.get("estado") != "activo":
        print(f"\n ACCESO DENEGADO: El invitado está '{invitado_doc.get('estado')}' en el sistema (Debe ser activo).")
        return

    rut_invitado = invitado_doc.get("rut")
    evento_doc = db['eventos'].find_one({
        "codigo": codigo_evento,
        "invitados": {
            "$elemMatch": {
                "rut": rut_invitado,
                "estado": "confirmado"
            }
        }
    })
    
    if evento_doc:
        print(f"\n ACCESO PERMITIDO")
        print(f"   Invitado: {invitado_doc.get('nombre')} (RUT: {rut_invitado})")
        print(f"   Evento:   {evento_doc.get('nombre')} en {evento_doc.get('lugar')}")
    else:
        existe_evento = db['eventos'].find_one({"codigo": codigo_evento})
        if not existe_evento:
            print("\n ERROR: El código del evento ingresado no existe.")
        else:
            print("\n ACCESO DENEGADO: El invitado no se encuentra 'confirmado' para este evento.")

def top_eventos_confirmados(db):
    print("\n" + "="*40)
    print("          TOP 3 EVENTOS POPULARES")
    print("="*40)
    
    coleccion = db['eventos']
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
        print(f"Error al ejecutar la agregación: {e}")