# DockerLabs — Injection

![Plataforma](https://img.shields.io/badge/Plataforma-DockerLabs-21262d?style=flat)
![Dificultad](https://img.shields.io/badge/Dificultad-Easy-e3b341?style=flat)
![SO](https://img.shields.io/badge/SO-Linux-21262d?style=flat&logo=linux&logoColor=FCC624)
![Estado](https://img.shields.io/badge/Estado-Completada-238636?style=flat)

---

## Resumen

Laboratorio para practicar la vulnerabilidad de inyección SQL para conseguir acceso al sistema y posterior escalada de privilegios en Linux.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p22,80
```

En este primer escaneo, vemos un servidor web y SSH, decidí echar un vistazo a la web y me encontré con un simple panel de login. 

![Pasted image 20260819182230](../images/Pasted%20image%2020260819182230.png)

---

## Enumeración

Al principio, me daba problemas de SQLi ya que la base de datos de MariaDB no estaba levantada, igual que otras cosas pero las he omitido en el writeup. Así que hice un escaneo de directorios y archivos ocultos pero encontré poca cosa:

![Pasted image 20260819182409](../images/Pasted%20image%2020260819182409.png)

El index.php que era el login, el archivo de config y el . que es el formulario de login.
Probé a ver si era vulnerable a una SQLi, en el campo de user puse `test´` con una comilla simple al final y en la contraseña test, era vulnerable a primera vista:

![Pasted image 20260819182819](../images/Pasted%20image%2020260819182819.png)

Luego, decidí abrir Burpsuite y ver que estaba pasando por detrás con la solicitud. Estuvie probando si era totalmente vulnerable y mandé este payload:

![Pasted image 20260819182859](../images/Pasted%20image%2020260819182859.png)

Que es `admin' OR '1'='1'-- -` pro codeado con URL, y vemos que sale un 302 Found y se nos redirige a `/acceso_valido_dylan.php`, decidí ver que era este recurso y nos dió la contraseña del usuario:

![Pasted image 20260819183103](../images/Pasted%20image%2020260819183103.png)

---

## Acceso inicial (Foothold)

Decidí reutilizar esta contraseña como clave del usuario dylan en ssh, y funcionó:

![Pasted image 20260819183152](../images/Pasted%20image%2020260819183152.png)

Nos faltaba ser el usuario root.

---

## Escalada de Privilegios

Hice `sudo -l`  pero no era por ahí, así que decidí buscar archivos con SUID:

```bash
find / -perm -u=s -type f 2>/dev/null
```

Me dió unos cuantos, pero me centré en `/usr/bin/env`:

Fui a gtfobins y busqué env, ví que había un apartado para SUID, copié, pegué y conseguí root:

<img src="../images/Pasted%20image%2020260817013510.png" width="591" alt="Pasted image 20260817013510" />
