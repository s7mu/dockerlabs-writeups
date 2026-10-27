---
tags:
  - ctf
  - writeup
platform: DockerLabs
machine: Obsession
difficulty: Very Easy
os: Linux
status: Completada
---

# DockerLabs — Obsession

## Resumen

Enumeración de rutas en web, y hacking de protocolos de red, principalmente SSH y FTP.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p21,22,80 172.17.0.2
```

Haciendo esto vemos que con FTP se puede entrar en anonymous y nos lista 2 archivos, chat-gonza.txt y pendientes.txt, más adelante veremos a ver que contienen. También nos encontramos con una versión de SSH vulnerable pero no vamos a atacar por ahí, ademas de una versión de Apache bastante desactualizada.

![Pasted image 20260813173813](../images/Pasted%20image%2020260813173813.png)

---

## Enumeración

Entramos al ftp de forma anónima y nos descargamos los 2 archivos, uno es un chat con un amigo con poca información relevante y otra es una lista de cosas pendientes. En esta lista nos encontramos que tiene pendiente cambiar algunas configuraciones de equipo porque comenta que tiene permisos habilitados no muy seguros.

![Pasted image 20260813174451](../images/Pasted%20image%2020260813174451.png)

Dejamos el FTP y nos centramos en la web, la web principal no tienen nada importante a simple vista, pero en el código fuente el usuario menciona que usa su mismo username en todos sus servicios.

![Pasted image 20260813175226](../images/Pasted%20image%2020260813175226.png)

Esto nos da una idea clara de el campo de username tanto en FTP como en SSH.

Con Feroxbuster escaneé posibles directorios con este comando:

```bash
feroxbuster -u http://172.17.0.2 \                      
-w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt
```

Y me dió /backup/ y /important/

En /backup/ había un fichero backup.txt que nos dice lo siguiente "Usuario para todos mis servicios: russoski (cambiar pronto!)" Esto nos proporciona ya el usuario. En /important/ solo hay un manifiesto hacker, nada relevante.

---

## Acceso inicial (Foothold)

Con todos los datos recogidos anteriormente, podemos empezar a hacer un ataque de fuerza bruta, en mi caso lo he hecho contra el SSH con la wordlist rockyou.txt

```bash
hydra -l russoski -P /usr/share/wordlists/rockyou.txt ssh://172.17.0.2 -t 64
```

Y me ha dado la contraseña iloveme

![Pasted image 20260813180729](../images/Pasted%20image%2020260813180729.png)

Iniciamos sesión a través de SSH y estamos dentro.

---

## Escalada de Privilegios

```bash
sudo -l
```

Hacemos un **sudo -l** y vemos que no somos root, pero que podemos ejecutar como root el binario *vim* 

![Pasted image 20260813181047](../images/Pasted%20image%2020260813181047.png)

Entonces simplemente hacemos sudo vim, escribimos :!/bin/bash, le damos a enter y ya tenemos una shell con root.

![Pasted image 20260813181245](../images/Pasted%20image%2020260813181245.png)
