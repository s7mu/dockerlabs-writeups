# DockerLabs — Tproot

![Plataforma](https://img.shields.io/badge/Plataforma-DockerLabs-21262d?style=flat)
![Dificultad](https://img.shields.io/badge/Dificultad-Very%20Easy-238636?style=flat)
![SO](https://img.shields.io/badge/SO-Linux-21262d?style=flat&logo=linux&logoColor=FCC624)
![Estado](https://img.shields.io/badge/Estado-Completada-238636?style=flat)

---

## Resumen

Laboratorio para practicar la explotación del backdoor de vsftpd 2.3.4 (CVE-2011-2523) para obtener acceso root.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
```

Nos ha dado el puerto 21 y 80

<img src="../images/Pasted%20image%2020260813153525.png" width="498" alt="Pasted image 20260813153525" />

```bash
nmap -sCV -p21,80 172.17.0.2
```

Este comando nos da algo bastante interesante, y es que FTP utiliza por detrás la versión vsftpd 2.3.4, que cuenta con un CVE con puntuación 9,8/10 (CVE-2011-2523). 

<img src="../images/Pasted%20image%2020260813153753.png" width="603" alt="Pasted image 20260813153753" />

---

## Enumeración

Con una rápida busqueda en Internet, encontramos la vulnerabilidad, esta se trata de que al conectarse a través de FTP con un usuario que termine en `:)` el servicio abre una shell con privilegios de root en el puerto TCP 6200

<img src="../images/Pasted%20image%2020260813154155.png" width="433" alt="Pasted image 20260813154155" />

## Acceso inicial (Foothold)

---
Nos conectamos por FTP a nuestra víctima e introducimos el usuario `kali:)` y cualquier contraseña.

![Pasted image 20260813154332](../images/Pasted%20image%2020260813154332.png)

Veremos que el servicio se queda congelado, esto significa que la shell está esperándonos.
En otra terminal, nos conectamos por netcat a ese puerto en específico:

```bash
nc -nv 172.17.0.2 6200
# El parámetro -n es para que no aplique DNS resolution, y -v es de verbose.
```

Y una vez conectados, si hacemos un `whoami` vemos que nos dice que somos root, teniendo total acceso a la máquina.

![Pasted image 20260813154711](../images/Pasted%20image%2020260813154711.png)
