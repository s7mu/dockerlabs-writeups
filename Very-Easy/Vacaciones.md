# DockerLabs — Vacaciones

![Plataforma](https://img.shields.io/badge/Plataforma-DockerLabs-21262d?style=flat)
![Dificultad](https://img.shields.io/badge/Dificultad-Very%20Easy-238636?style=flat)
![SO](https://img.shields.io/badge/SO-Linux-21262d?style=flat&logo=linux&logoColor=FCC624)
![Estado](https://img.shields.io/badge/Estado-Completada-238636?style=flat)

---

## Resumen

Laboratorio para practicar fuerza bruta contra SSH y escalada de privilegios en Linux.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p22,80 172.17.0.2
```

En este reconocimiento podemos ver que ambos servicios usan versiones vulnerables, pero no va por ahí el laboratorio.

---

## Enumeración

Primero, perdí bastante tiempo buscando PoC de las versiones vulnerables de ambos servicios, pero lo descarté. Me dió curiosidad la página web ya que era todo en blanco, así que decidí ver el código de la página y efectivamente, tenía un mensaje oculto que con él podemos obtener 2 posibles usuarios para SSH, Juan y Camilo.

![Pasted image 20260814003837](../images/Pasted%20image%2020260814003837.png)

Después de esto, quería ver si encontraba mas información de la web usando **Gobuster**, pero solo nos dió un directorio que es /javascript/ y es 301.
```bash
gobuster dir -u http://172.17.0.2/ -w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt
```

![Pasted image 20260814004038](../images/Pasted%20image%2020260814004038.png)

Después de perder bastante tiempo buscando recursos en el servidor web decidí hacer 2 ataques de fuerza bruta ssh a los dos usuarios que tenía, Pedro y Camilo.

```bash
hydra -l camilo -P /usr/share/wordlists/rockyou.txt ssh://172.17.0.2 -t 64
hydra -l pedro -P /usr/share/wordlists/rockyou.txt ssh://172.17.0.2 -t 64
```

Y nos encontró la contraseña del usuario pedro que es `password1`.

---

## Acceso inicial (Foothold)

Iniciamos sesión con la contraseña de camilo y era válida, conseguimos el primer acceso a la máquina. Probé `sudo -l` pero no tenía permisos para ejecutarlo, investigué los demás home pero no conseguí nada. También estuve un tiempo buscando otras vias de elevar privilegios a través de capabilities o mediante cron, sin éxito ninguno.

![Pasted image 20260814010322](../images/Pasted%20image%2020260814010322.png)

Hasta que me acuerdo del mensaje del index.html, hablaba algo de un correo así que fui al directorio `/var/mail/camilo`  y encontré un `correo.txt` que me daba una contraseña, según el contexto del mail era la de juan.

![Pasted image 20260814010739](../images/Pasted%20image%2020260814010739.png)

Inicié sesión con este usuario.

---

## Escalada de Privilegios

Al entrar con el usuario de Juan, lo primero que pruebo es `sudo -l` y tenemos una via bastante buena de elevar privilegios, ya que podiamos usar ruby como root.

```bash
sudo ruby -e 'exec "/bin/bash"'
```

Con este simple comando, conseguimos acceso al usuario root.

![Pasted image 20260814011037](../images/Pasted%20image%2020260814011037.png)
