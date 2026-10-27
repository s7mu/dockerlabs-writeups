---
tags:
  - ctf
  - writeup
platform: DockerLabs
machine: BorazuwarahCTF
difficulty: Very Easy
os: Linnux
status: Completada
---

# 🏴 DockerLabs — BorazuwarahCTF

## Resumen

Laboratorio para practicar estaganografía y fuerza bruta contra protocolos de red.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p22,80 172.17.0.2
```

Nos encontramos 2 servicios corriendo, un servidor web y SSH.

![Pasted image 20260814134028](../images/Pasted%20image%2020260814134028.png)

---

## Enumeración

Decidí entrar a la página web y me encuentro un huevo Kinder sorpresa, tiene que tener una sorpresa obviamente, así que me descargo la imagen y uso **Exiftool** para ver los metadatos de la imagen a ver si hay algo interesante, y efectivamente, tenemos un usuario: borazuwarah

![Pasted image 20260814134226](../images/Pasted%20image%2020260814134226.png)

Pero nos falta la contraseña, así que antes de hacer un ataque de fuerza bruta, hice un gobuster para ver si encontraba algo más pero no encontré nada.

Así que decidí empezar un ataque de fuerza bruta usando **hydra**

```bash
hydra -l borazuwarah -P /usr/share/wordlists/rockyou.txt ssh://172.17.0.2 -t 64
```

Y me sacó la contraseña, **123456**

![Pasted image 20260814134425](../images/Pasted%20image%2020260814134425.png)

---

## Acceso inicial (Foothold)

Teniendo ya un usuario y contraseña, me conecto por SHH con las credenciales y entramos

![Pasted image 20260814134531](../images/Pasted%20image%2020260814134531.png)

Procedemos con la elevación de privilegios. 

---

## Escalada de Privilegios

```bash
sudo -l
```

Vemos que tenemos acceso a ejecutar `sudo /bin/bash` que nos va a hacer tener una bash como root, así que lo ejecutamos y ya conseguimos root.

![Pasted image 20260814134656](../images/Pasted%20image%2020260814134656.png)
