import socket
import threading
import base64
import os
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
username = input("Ingresa tu Nombre de usuario: ")
print("""
Salas disponibles:
  sala1
  sala2
  sala3

Comandos:
e salaX            -> entrar a sala
s salaX            -> salir de sala
s                  -> salir de TODAS
m salaX texto      -> mensaje a sala
p usuario texto    -> privado
a usuario archivo  -> enviar audio
x                  -> salir
""")

def recibir():
    while True:
        try:
            data, _ = sock.recvfrom(65535)
            if data.startswith(b"AUDIO "):
                partes = data.split(b" ", 3)
                origen = partes[1].decode()
                nombre = partes[2].decode()
                b64 = partes[3]

                with open("REC_" + nombre, "wb") as f:
                    f.write(base64.b64decode(b64))

                print(f"\n(Audio recibido de {origen}, guardado como REC_{nombre})\n> ", end="")
                continue

            print("\n" + data.decode() + "\n> ", end="")
        except:
            pass

threading.Thread(target=recibir, daemon=True).start()
def enviar(texto):
    sock.sendto(texto.encode(), (SERVER_IP, SERVER_PORT))

while True:
    msg = input("> ")
    if msg == "":
        continue
    if msg == "x":
        enviar(f"LEAVEALL {username}")
        break
    partes = msg.split(" ", 2)

    cmd = partes[0]

    if cmd == "e": 
        sala = partes[1]
        enviar(f"ENTER {username} {sala}")

    elif cmd == "s" and len(partes) == 1:
        enviar(f"LEAVEALL {username}")

    elif cmd == "s":  
        sala = partes[1]
        enviar(f"LEAVE {username} {sala}")

    elif cmd == "m":  
        sala = partes[1]
        texto = partes[2]
        enviar(f"MSG {username} {sala} {texto}")

    elif cmd == "p":  
        dest = partes[1]
        texto = partes[2]
        enviar(f"PRIV {username} {dest} {texto}")

    elif cmd == "a":  
        dest = partes[1]
        archivo = partes[2]

        if not os.path.exists(archivo):
            print("No existe el archivo.")
            continue

        b64 = base64.b64encode(open(archivo, "rb").read()).decode()
        enviar(f"AUDIO {username} {dest} {archivo} {b64}")

    else:
        print("Comando no válido.")
