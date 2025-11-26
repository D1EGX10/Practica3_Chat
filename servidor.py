import socket
import json
import threading
salas = {}
usuarios = {}

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
        print("Error mandando JSON a", direccion, e)
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
    """Procesa paquetes entrantes del cliente."""
    try:
        info = json.loads(data.decode())
    except Exception as e:
        print("Mensaje no entendible:", data, e)
        return

    tipo = info.get("tipo")

    if tipo == "entrar_sala":
        sala = info["sala"]
        usuario = info["nombre"]

        if sala not in salas:
            salas[sala] = {}

        salas[sala][usuario] = direccion
        usuarios[usuario] = direccion 
        print(f"[{sala}] ENTRA {usuario} desde {direccion}")

        avisar_lista_usuarios(sala)

    elif tipo == "salir_sala":
        sala = info["sala"]
        usuario = info["nombre"]

        if sala in salas and usuario in salas[sala]:
            del salas[sala][usuario]
            print(f"[{sala}] SALE {usuario}")
            esta_en_otra = any(usuario in s for s in salas.values())
            if not esta_en_otra and usuario in usuarios:
                del usuarios[usuario]

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

        if destino in usuarios:
            mandar_json(usuarios[destino], info)
            mandar_json(direccion, {"tipo": "error", "contenido": f"Privado enviado a {destino}"})
        else:
            mandar_json(direccion, {"tipo": "error", "contenido": f"Usuario {destino} no conectado"})

    else:
        print("Tipo no reconocido:", tipo, "de", direccion)

def escuchar():
    """Hilo principal que recibe datagramas UDP."""
    while True:
        data, direccion = sock.recvfrom(65535)
        # procesar cada paquete en un hilo para no bloquear
        threading.Thread(target=procesar_paquete, args=(data, direccion), daemon=True).start()

hilo = threading.Thread(target=escuchar, daemon=True)
hilo.start()
while True:
    try:
        pass
    except KeyboardInterrupt:
        print("Servidor detenido.")
        break
