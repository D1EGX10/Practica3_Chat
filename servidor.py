import socket
import json
import base64
ip = "0.0.0.0"
puerto = 5500
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, puerto))
print(f"Servidor listo en puerto {puerto}")
usuarios = {}        
salas = {}          
def mandar(dest, data):
    mensaje = json.dumps(data).encode()
    sock.sendto(mensaje, dest)

def mandar_a_sala(sala, data):
    if sala not in salas:
        return

    mensaje = json.dumps(data).encode()

    for usuario in salas[sala]:
        destino = usuarios.get(usuario)
        if destino:
            sock.sendto(mensaje, destino)

while True:
    data, cliente = sock.recvfrom(65535)

    try:
        info = json.loads(data.decode())
    except:
        continue

    tipo = info.get("tipo")

    if tipo == "registrar":
        nombre = info["nombre"]
        usuarios[nombre] = cliente
        continue

    if tipo == "entrar_sala":
        sala = info["sala"]
        nombre = info["nombre"]

        if sala not in salas:
            salas[sala] = []

        if nombre not in salas[sala]:
            salas[sala].append(nombre)

        mandar(cliente, {
            "tipo": "ok",
            "msg": f"Entraste a {sala}"
        })

        mandar_a_sala(sala, {
            "tipo": "mensaje_sala",
            "sala": sala,
            "de": "SERVIDOR",
            "contenido": f"{nombre} entró a la sala"
        })

        mandar(cliente, {
            "tipo": "lista_usuarios",
            "sala": sala,
            "contenido": salas[sala]
        })

    elif tipo == "salir_sala":
        sala = info["sala"]
        nombre = info["nombre"]

        if sala in salas and nombre in salas[sala]:
            salas[sala].remove(nombre)

            mandar_a_sala(sala, {
                "tipo": "mensaje_sala",
                "sala": sala,
                "de": "SERVIDOR",
                "contenido": f"{nombre} salió de la sala"
            })

    elif tipo == "mensaje_sala":
        sala = info["sala"]
        mandar_a_sala(sala, info)

    elif tipo == "privado":
        destino = info["para"]

        if destino not in usuarios:
            mandar(cliente, {
                "tipo": "privado",
                "de": "SERVIDOR",
                "contenido": f"Usuario {destino} no existe"
            })
            continue

        mandar(usuarios[destino], info)
    elif tipo == "audio":
        destino = info["para"]

        if destino not in usuarios:
            mandar(cliente, {
                "tipo": "privado",
                "de": "SERVIDOR",
                "contenido": f"Usuario {destino} no existe"
            })
            continue
        mandar(usuarios[destino], info)
