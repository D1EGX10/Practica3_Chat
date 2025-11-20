import socket
import json
import threading

ip_servidor = "127.0.0.1"
puerto_servidor = 5500

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

nombre_usuario = input("Pon tu nombre en el chat: ")

salas_unidas = []

def mandar_json(data):
    mensaje = json.dumps(data).encode()
    sock.sendto(mensaje, (ip_servidor, puerto_servidor))

def recibir():
    """Hilo que recibe todo lo que diga el servidor."""
    while True:
        data, _ = sock.recvfrom(65535)
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

hilo = threading.Thread(target=recibir, daemon=True)
hilo.start()

print("""
Comandos:
  /entrar sala
  /salir sala
  /msg sala mensaje
  /privado usuario mensaje
  /salir
""")
while True:
    txt = input("> ")

    if txt.startswith("/entrar"):
        _, sala = txt.split(" ", 1)
        salas_unidas.append(sala)

        mandar_json({
            "tipo": "entrar_sala",
            "sala": sala,
            "nombre": nombre_usuario
        })

    elif txt.startswith("/salir "):
        _, sala = txt.split(" ", 1)
        mandar_json({
            "tipo": "salir_sala",
            "sala": sala,
            "nombre": nombre_usuario
        })

    elif txt.startswith("/msg"):
        _, sala, mensaje = txt.split(" ", 2)
        mandar_json({
            "tipo": "mensaje_sala",
            "sala": sala,
            "de": nombre_usuario,
            "contenido": mensaje
        })

    elif txt.startswith("/privado"):
        _, usuario_destino, mensaje = txt.split(" ", 2)
        mandar_json({
            "tipo": "privado",
            "para": usuario_destino,
            "de": nombre_usuario,
            "contenido": mensaje
        })

    elif txt == "/salir":
        print("Adiós.")
        break

    else:
        print("Comando no reconocido.")
