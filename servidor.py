import socket
import json
import threading
salas = {}

ip_servidor = "0.0.0.0"
puerto_servidor = 5500

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip_servidor, puerto_servidor))

print("SERVIDOR LISTO en puerto", puerto_servidor)

def mandar_json(direccion, data):
    """Envia diccionario como JSON a un cliente."""
    try:
        mensaje = json.dumps(data).encode()
        sock.sendto(mensaje, direccion)
    except Exception as e:
        print("Error mandando JSON:", e)

def avisar_lista_usuarios(nombre_sala):
    """Cada que alguien entra o sale, avisamos a todos en esa sala."""
    if nombre_sala not in salas:
        return

    lista_usuarios = list(salas[nombre_sala].keys())

    aviso = {
        "tipo": "lista_usuarios",
        "sala": nombre_sala,
        "contenido": lista_usuarios
    }
    for usuario, direccion in salas[nombre_sala].items():
        mandar_json(direccion, aviso)


def procesar_paquete(data, direccion):
    """Aquí cae TODO lo que manden los clientes."""
    try:
        info = json.loads(data.decode())
    except:
        print("Mensaje no entendible:", data)
        return

    tipo = info.get("tipo")

    if tipo == "entrar_sala":
        sala = info["sala"]
        usuario = info["nombre"]

        if sala not in salas:
            salas[sala] = {}

        salas[sala][usuario] = direccion
        print(f"[{sala}] ENTRA {usuario}")

        avisar_lista_usuarios(sala)


    elif tipo == "salir_sala":
        sala = info["sala"]
        usuario = info["nombre"]

        if sala in salas and usuario in salas[sala]:
            del salas[sala][usuario]
            print(f"[{sala}] SALE {usuario}")

            avisar_lista_usuarios(sala)

    elif tipo == "mensaje_sala":
        sala = info["sala"]
        usuario = info["de"]
        texto = info["contenido"]

        print(f"[{sala}] {usuario} dice: {texto}")

        if sala in salas:
            for otro, direccion_otro in salas[sala].items():
                if otro != usuario:
                    mandar_json(direccion_otro, info)

    elif tipo == "privado":
        destino = info["para"]
        texto = info["contenido"]
        usuario = info["de"]

        print(f"[PRIVADO] {usuario} -> {destino}: {texto}")

        for s in salas.values():
            if destino in s:
                mandar_json(s[destino], info)
                break

def escuchar():
    """Hilo principal que recibe datagramas UDP."""
    while True:
        data, direccion = sock.recvfrom(65535)
        procesar_paquete(data, direccion)

hilo = threading.Thread(target=escuchar, daemon=True)
hilo.start()


while True:
    pass
