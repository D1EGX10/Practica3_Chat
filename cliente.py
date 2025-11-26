import socket
import json
import threading

ip_servidor = "127.0.0.1"
puerto_servidor = 5500

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 0)) 

nombre_usuario = input("Pon tu nombre en el chat: ").strip()
if not nombre_usuario:
    nombre_usuario = "anonimo"

salas_unidas = [] 

def mandar_json(data):
    try:
        mensaje = json.dumps(data).encode()
        sock.sendto(mensaje, (ip_servidor, puerto_servidor))
    except Exception as e:
        print("Error al mandar:", e)

def recibir():
    """Hilo que recibe todo lo que diga el servidor."""
    while True:
        try:
            data, _ = sock.recvfrom(65535)
        except Exception as e:
            print("Error en recv:", e)
            break

        try:
            info = json.loads(data.decode())
        except:
            print("Mensaje raro:", data)
            continue

        tipo = info.get("tipo")

        if tipo == "lista_usuarios":
            print(f"\n--- Usuarios en sala {info['sala']} ---")
            print(", ".join(info["contenido"]))
            print("-------------------------\n")

        elif tipo == "mensaje_sala":
            print(f"[{info['sala']}] {info['de']}: {info['contenido']}")

        elif tipo == "privado":
            print(f"[PRIVADO] {info['de']}: {info['contenido']}")

        elif tipo == "error":
            print(f"[SERVIDOR] {info.get('contenido')}")

        else:
            print("RECIBIDO:", info)

hilo = threading.Thread(target=recibir, daemon=True)
hilo.start()
print("""
Comandos (cortos y humanos):
  e sala       -> entrar a sala
  s sala       -> salir de sala
  m sala texto -> mandar mensaje a sala
  p usuario texto -> mandar privado
  x            -> salir del programa (sale de todas las salas)""")
while True:
    try:
        txt = input("> ").strip()
    except (KeyboardInterrupt, EOFError):
        txt = "x"

    if not txt:
        continue

    partes = txt.split(" ", 2) 

    cmd = partes[0]

    if cmd == "e" or cmd == "/entrar" or cmd == "entrar":
        if len(partes) < 2:
            print("Usa: e sala")
            continue
        sala = partes[1].strip()
        if sala in salas_unidas:
            print("Ya estás en", sala)
            continue
        salas_unidas.append(sala)
        mandar_json({
            "tipo": "entrar_sala",
            "sala": sala,
            "nombre": nombre_usuario
        })
        print(f"Entrando a {sala}...")
    elif cmd == "s" and len(partes) >= 2 or (cmd == "/salir" and len(partes) >= 2):
        sala = partes[1].strip()
        if sala not in salas_unidas:
            print("No estás en esa sala:", sala)
            continue
        try:
            salas_unidas.remove(sala)
        except:
            pass
        mandar_json({
            "tipo": "salir_sala",
            "sala": sala,
            "nombre": nombre_usuario
        })
        print(f"Saliendo de {sala}...")
    elif cmd == "m" or cmd == "/msg" or cmd == "msg":
        if len(partes) < 3:
            print("Usa: m sala mensaje")
            continue
        sala = partes[1].strip()
        mensaje = partes[2].strip()
        if sala not in salas_unidas:
            print("No estás en esa sala. Entra primero con: e", sala)
            continue
        mandar_json({
            "tipo": "mensaje_sala",
            "sala": sala,
            "de": nombre_usuario,
            "contenido": mensaje
        })
    elif cmd == "p" or cmd == "/privado" or cmd == "privado":
        if len(partes) < 3:
            print("Usa: p usuario mensaje")
            continue
        destino = partes[1].strip()
        mensaje = partes[2].strip()
        mandar_json({
            "tipo": "privado",
            "para": destino,
            "de": nombre_usuario,
            "contenido": mensaje
        })
        print(f"(privado a {destino}) {mensaje}")
    elif cmd == "x" or (cmd == "/salir" and len(partes) == 1):
        for sala in list(salas_unidas):
            mandar_json({
                "tipo": "salir_sala",
                "sala": sala,
                "nombre": nombre_usuario
            })
        print("Saliendo del chat. Nos vemos.")
        break
    elif cmd == "/salir" and len(partes) >= 2:
        sala = partes[1].strip()
        if sala in salas_unidas:
            salas_unidas.remove(sala)
        mandar_json({
            "tipo": "salir_sala",
            "sala": sala,
            "nombre": nombre_usuario
        })

    else:
        print("Comando no reconocido. Usa 'e,s,m,p,x' o /entrar /salir /msg /privado /salir")
