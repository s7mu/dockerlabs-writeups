# DockerLabs — Psycho

![Plataforma](https://img.shields.io/badge/Plataforma-DockerLabs-21262d?style=flat)
![Dificultad](https://img.shields.io/badge/Dificultad-Easy-e3b341?style=flat)
![SO](https://img.shields.io/badge/SO-Linux-21262d?style=flat&logo=linux&logoColor=FCC624)
![Estado](https://img.shields.io/badge/Estado-Completada-238636?style=flat)

---

## Resumen

El laboratorio Psycho de DockerLabs es un entorno vulnerable en Linux donde se practican técnicas básicas de hacking ético. Incluye enumeración de servicios, explotación de una vulnerabilidad LFI, acceso mediante clave SSH filtrada y escalada de privilegios usando sudo.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p22,80 172.17.0.2
```

Vemos que tiene una página web y SSH corriendo, no encontramos mucha mas información por ahora así que el siguiente paso es ver la página web.

<img src="../images/Pasted%20image%2020260825172049.png" width="586" alt="Pasted image 20260825172049" />

---

## Enumeración

Dentro de la página web no tiene pinta de haber mucha en un primer vistazo, no tiene otros directorios visibles desde el propio sitio, en el código fuente no hay nada importante y no me da muchas pistas.
Así que decido hacer un escaneo de directorios:

```bash
gobuster dir -u http://172.17.0.2 -w /usr/share/dirb/wordlists/common.txt
```

Y nos encuentra el directorio `/assets`, dentro tiene una archivo llamado `background.jpg`. Decido usar la herramienta `exiftool` para ver si tiene algo oculto, pero vemos que no, así que continuamos con la enumeración.

<img src="../images/Pasted%20image%2020260825172342.png" width="391" alt="Pasted image 20260825172342" />

Me puse a buscar párametros interesantes con `ffuf` con este comando, ya que `index.php` parecía procesar algún parámetro pero no sabíamos cual era:

```bash
ffuf -u 'http://172.17.0.2/index.php?FUZZ=test' \
-w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
-fs 2596
```

Y nos encuentra el parámetro `secret`:

![Pasted image 20260825172944](../images/Pasted%20image%2020260825172944.png)

Así que decido usar ese parámetro para ver si puedo leer el archivo `/etc/passwd` usando path traversal, usando `http://172.17.0.2/index.php?secret=../../../../../../../../etc/passwd` y vemos que nos sale el archivo con éxito.

![Pasted image 20260825173108](../images/Pasted%20image%2020260825173108.png)

Decido usar Burpsuite para ver el contenido mejor y vemos 2 usuarios, `vaxei` y `luisillo`.
Una vez que tengo estos 2 usuarios, vemos si puedo robar su clave privada de SSH para poder iniciar sesión con ella. El usuario `luisillo` no cuenta con ella pero el usuario `vaxei` sí, lo pude saber con esta URL:
`http://172.17.0.2/index.php?secret=../../../../../../../../home/vaxei/.ssh/id_rsa` 

Y viendo el contenido:

![Pasted image 20260825173617](../images/Pasted%20image%2020260825173617.png)

---

## Acceso inicial (Foothold)

Una vez que tenemos esto, copiamos la clave ya que nos permite autenticarnos por SSH, así que la copiamos en un fichero llamado `id_rsa`, le damos los permisos necessarios con `chmod 600 id_rsa` e iniciamos sesión con `ssh -i id_rsa vaxei@172.17.0.2`. Logrando entrar al sistema como el usuario `vaxei` .

![Pasted image 20260825173903](../images/Pasted%20image%2020260825173903.png)

En su home tiene un fichero que parece texto sin sentido como `asdasdasd` y similares, pero no encontré nada más. Así que empecé a ver posibles caminos para elevar mis privilegios.

---

## Escalada de Privilegios

```bash
sudo -l
```

Con este comando vemos que podemos ejecutar como el usuario `luisillo` el binario `/usr/bin/perl` así que con este comando: `sudo -u luisillo perl -e 'exec "/bin/sh"'` Nos da una shell como el usuario luisillo. Además, hacemos TTY Upgrade con:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

![Pasted image 20260825174207](../images/Pasted%20image%2020260825174207.png)

Ahora tenemos acceso al usuario luisillo, hacemos `sudo -l` y vemos que podemos ejecutar como `root` el siguiente archivo: `/usr/bin/python3 /opt/paw.py`. Me pongo a investigar el archivo y parece humo, el script por sí solo no hace nada importante, pero si nos fijamos en sus permisos vemos que no lo podemos editar directamente, pero sí tenemos permiso de escritura en el directorio `/opt/`:

![Pasted image 20260825174725](../images/Pasted%20image%2020260825174725.png)

Ya que si hacemos un `ls -la /opt/` vemos que nos permite escribir. Así que es tan fácil como borrar `paw.py`, crear una archivo en `/opt/` con el mismo nombre y generarnos una shell, yo lo he hecho con esto:

```python
import os
os.system("/bin/bash")
```

Así que guardamos el archivo, lo ejecutamos con sudo, y nos dará una shell como usuario root.

![Pasted image 20260825174947](../images/Pasted%20image%2020260825174947.png)
