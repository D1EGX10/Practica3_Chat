import socket
import threading
import base64
import os
IP = "0.0.0.0"
PORT = 5000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))
salas = {
    "sala1": set(),
    "sala2": set(),
    "sala3": set()
}
usuarios = {}  

print("Servidor iniciado en puerto", PORT)

def enviar(addr, mensaje):
    sock.sendto(mensaje.encode(), addr)

def enviar_sala(sala, mensaje):
    for u in salas[sala]:
        enviar(usuarios[u], mensaje)

def lista_usuarios(sala):
    if not salas[sala]:
        return "Nadie está en la sala."
    return "Usuarios actuales: " + ", ".join(salas[sala])

def manejar_mensaje(data, addr):
    try:
        texto = data.decode()
    except:
        return
    partes = texto.split(" ", 2)

    if len(partes) < 2:
        return
    comando = partes[0]
    usuario = partes[1]

    usuarios[usuario] = addr  

    if comando == "ENTER":
        sala = partes[2]

        if sala in salas:

            if usuario not in salas[sala]:
                salas[sala].add(usuario)

                enviar_sala(sala, f"[Servidor] {usuario} ha entrado a {sala}")

                enviar_sala(sala, f"[Servidor] {lista_usuarios(sala)}")

            enviar(addr, f"[Servidor] Entraste a {sala}")
        else:
            enviar(addr, "[Servidor] Esa sala no existe.")

    elif comando == "LEAVE":
        sala = partes[2]
        if sala in salas and usuario in salas[sala]:

            salas[sala].remove(usuario)

            enviar_sala(sala, f"[Servidor] {usuario} ha salido de {sala}")

            enviar_sala(sala, f"[Servidor] {lista_usuarios(sala)}")

            enviar(addr, f"[Servidor] Saliste de {sala}")
        else:
            enviar(addr, "[Servidor] No estás en esa sala.")

    elif comando == "LEAVEALL":
        for sala in salas:
            if usuario in salas[sala]:
                salas[sala].remove(usuario)
                enviar_sala(sala, f"[Servidor] {usuario} ha salido de {sala}")
                enviar_sala(sala, f"[Servidor] {lista_usuarios(sala)}")

        enviar(addr, "[Servidor] Saliste de todas las salas.")

    elif comando == "MSG":
        sala, mensaje = partes[2].split(" ", 1)

        if sala in salas and usuario in salas[sala]:
            for u in salas[sala]:
                enviar(usuarios[u], f"[{sala}] {usuario}: {mensaje}")
        else:
            enviar(addr, "[Servidor] No estás en esa sala.")

    elif comando == "PRIV":
        destino, mensaje = partes[2].split(" ", 1)
        if destino in usuarios:
            enviar(usuarios[destino], f"[Privado de {usuario}] {mensaje}")
        else:
            enviar(addr, "[Servidor] Ese usuario no existe.")

    elif comando == "AUDIO":
        destino, archivo_b64 = partes[2].split(" ", 1)
        if destino in usuarios:
            sock.sendto(data, usuarios[destino])
        else:
            enviar(addr, "[Servidor] Ese usuario no existe.")

def recibir():
    while True:
        data, addr = sock.recvfrom(65535)
        threading.Thread(target=manejar_mensaje, args=(data, addr)).start()
recibir()