import socket
import json
import threading
import base64
import os

ip_servidor = "127.0.0.1"
puerto_servidor = 5500

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 0)) 

nombre = input("Nombre: ")

sock.sendto(json.dumps({"tipo": "registrar", "nombre": nombre}).encode(),
            (ip_servidor, puerto_servidor))

def enviar(data):
    mensaje = json.dumps(data).encode()
    sock.sendto(mensaje, (ip_servidor, puerto_servidor))


def recibir():
    while True:
        data, _ = sock.recvfrom(65535)
        try:
            info = json.loads(data.decode())
        except:
            continue

        tipo = info.get("tipo")

        if tipo == "mensaje_sala":
            print(f"[{info['sala']}] {info['de']}: {info['contenido']}")

        elif tipo == "privado":
            print(f"(privado) {info['de']}: {info['contenido']}")

        elif tipo == "lista_usuarios":
            print(f"Usuarios en {info['sala']}: {', '.join(info['contenido'])}")

        elif tipo == "audio":
            nombre_archivo = f"audio_recibido_{info['de']}.wav"
            with open(nombre_archivo, "wb") as f:
                f.write(base64.b64decode(info["contenido"]))
            print(f"(audio de {info['de']}) guardado como {nombre_archivo}")

hilo = threading.Thread(target=recibir, daemon=True)
hilo.start()

print("""
Comandos:
e sala
s sala
m sala mensaje
p usuario mensaje
a usuario archivo.wav
x
""")

while True:
    t = input("> ")

    if t == "x":
        break

    if t.startswith("e "):
        _, sala = t.split(" ", 1)
        enviar({"tipo": "entrar_sala", "sala": sala, "nombre": nombre})
        continue

    if t.startswith("s "):
        _, sala = t.split(" ", 1)
        enviar({"tipo": "salir_sala", "sala": sala, "nombre": nombre})
        continue

    if t.startswith("m "):
        try:
            _, sala, msg = t.split(" ", 2)
            enviar({
                "tipo": "mensaje_sala",
                "sala": sala,
                "de": nombre,
                "contenido": msg
            })
        except:
            print("Usa: m sala mensaje")
        continue
    if t.startswith("p "):
        try:
            _, dest, msg = t.split(" ", 2)
            enviar({
                "tipo": "privado",
                "para": dest,
                "de": nombre,
                "contenido": msg
            })
        except:
            print("Usa: p usuario mensaje")
        continue
    if t.startswith("a "):
        try:
            _, dest, archivo = t.split(" ", 2)
            if not os.path.isfile(archivo):
                print("No existe el archivo")
                continue

            with open(archivo, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()

            enviar({
                "tipo": "audio",
                "para": dest,
                "de": nombre,
                "contenido": b64
            })
            print(f"(audio enviado a {dest})")

        except:
            print("Usa: a usuario archivo.wav")

        continue

    print("Comando no válido.")
