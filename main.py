import database
import operaciones

def menu_principal():
    # 1. Llamamos a la función del archivo database.py para conectarnos
    db = database.conectar_bd()
    
    if db is None:
        print("Error al inicializar la base de datos.")
        return

    # 2. Mostramos el menú iterativo
    while True:
        print("\n" + "="*45)
        print(" GESTIÓN DE EVENTOS E INVITADOS ")
        print("="*45)
        print("1. Listado general de eventos")
        print("2. Buscar invitados por nombre o correo")
        print("3. Validar acceso a evento")
        print("4. Top 3 eventos más populares")
        print("5. Salir")
        print("="*45)
        
        opcion = input("Selecciona una opción (1-5): ").strip()
        
        if opcion == '1':
            operaciones.listar_eventos(db)
        elif opcion == '2':
            operaciones.buscar_invitados_regex(db)
        elif opcion == '3':
            operaciones.validar_acceso_evento(db)
        elif opcion == '4':
            operaciones.top_eventos_confirmados(db)
        elif opcion == '5':
            print("\nCerrando el sistema. ¡Éxito en tu evaluación!")
            break
        else:
            print("\n Opción inválida. Intenta del 1 al 5.")

if __name__ == "__main__":
    menu_principal()