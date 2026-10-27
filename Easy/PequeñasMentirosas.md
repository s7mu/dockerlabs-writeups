---
tags:
  - ctf
  - writeup
platform: DockerLabs
machine: PequeñasMentirosas
difficulty: Easy
os: Linux
status: Completada
---

# 🏴 DockerLabs — PequeñasMentirosas

## Resumen

El reto consiste en enumerar los servicios expuestos, obtener acceso inicial mediante unas credenciales débiles y posteriormente realizar movimiento lateral mediante el descubrimiento y crackeo de un hash. Finalmente, una configuración insegura de sudo permite ejecutar Python como root y conseguir una shell privilegiada.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p22,80 172.17.0.2
```

Hacemos un escaneo y vemos que tiene SSH corriendo junto con un servidor web. En la web no parece haber nada de primeras solo un texto que contiene `# Pista: Encuentra la clave para A en los archivos.` 

---

## Enumeración

Decido escanear directorios y archivos con Gobuster, probé un par de veces pero no encontré nada, así que decidí tomar otra dirección y dejar la web a un lado.

Realicé un ataque de fuerza bruta con el usuario `a` que nos habían mencionado anteriormente en la web con Hydra:

```bash
hydra -l a -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt ssh://172.17.0.2 -t 64
```

Usamos la wordlist de las 10.000 contraseñas más comunes y conseguimos sacar la contraseña siendo `secret`.

![Pasted image 20260825235556](../images/Pasted%20image%2020260825235556.png)

---

## Acceso inicial (Foothold)

Inicié en SSH como el usuario `a` y con la contraseña que habíamos visto antes. Veo que hay otro usuario llamado `spencer`, puede ser interesante para después. 

![Pasted image 20260825235724](../images/Pasted%20image%2020260825235724.png)

---

## Post-Explotación

Realicé lo típico, buscar binarios con SUID, `sudo -l`, buscar capabilities, pero no encontré nada, así que decidí investigar un poco los ficheros de la máquina. Encontré un par de carpetas en `/opt` pero no parecía ser nada interesante, así que llegué a `/srv/ftp` donde nos encontramos bastante contenido.

![Pasted image 20260825235930](../images/Pasted%20image%2020260825235930.png)

Entre todos los ficheros, encontramos uno llamado `hash_spencer.txt` con el siguiente contenido `7c6a180b36896a0a8c02787eeafb0e4c`. También había otro fichero que decía que teníamos que aplicar fuerza bruta contra el hash de `spencer`, así que es lo que hice con John The Ripper:

```bash
john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt hash_spencer.txt
```

En el que especificamos el formato usando `--format=raw-md5`, ya que es lo que mas pinta tenía según su estructura.

Nos encontró la contraseña rapidamente. `password1`:
![Pasted image 20260826000813](../images/Pasted%20image%2020260826000813.png)

---

## Escalada de Privilegios


Con lo anterior, inicié sesión por SSH con el usuario `spencer`, haciendo `sudo -l` viendo que podemos ejecutar python3 como root. Así que con este comando logré invocarme una shell como root. 

```bash
ssh spencer@172.17.0.2
sudo python3 -c 'import os; os.execl("/bin/sh", "sh")'
```

![Pasted image 20260826001006](../images/Pasted%20image%2020260826001006.png)
