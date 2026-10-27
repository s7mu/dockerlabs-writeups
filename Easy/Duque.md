# DockerLabs — Duque

![Plataforma](https://img.shields.io/badge/Plataforma-DockerLabs-21262d?style=flat)
![Dificultad](https://img.shields.io/badge/Dificultad-Easy-e3b341?style=flat)
![SO](https://img.shields.io/badge/SO-Linux-21262d?style=flat&logo=linux&logoColor=FCC624)
![Estado](https://img.shields.io/badge/Estado-Completada-238636?style=flat)

---

## Resumen

Laboratorio de dificultad Easy centrado principalmente en SQL Injection, enumeración de recursos y escalada de privilegios mediante un binario SUID.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p22,80 172.17.0.2
```

Vemos que tiene un servidor web y ssh corriendo, lo que nos da una idea de que tenemos que recolectar información en la web y luego ver si podemos entrar por ssh.

![Pasted image 20260824163629](../images/Pasted%20image%2020260824163629.png)

---

## Enumeración

Una vez que nos metemos a la web vemos que se trata de una web empresarial con varios apartados, inicio, empleados, normativa, intranet y proveedores. De estos no podemos entrar ni en Intranet ni en empleados, pero decido buscar otras cosas antes de intentar ver el contenido de alguna de los 2 sitios dichos antes.

Así que hago un escaneo con Gobuster con este comando:

```bash
gobuster dir -u http://172.17.0.2/ -w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt
```

Y nos encuentra /bills/

![Pasted image 20260824163949](../images/Pasted%20image%2020260824163949.png)

Y nos encontramos un panel de login, pruebo a ver si es vulnerable con SQLi poniendo una comilla simple ' y nos da Error 500:

<img src="../images/Pasted%20image%2020260824164056.png" width="383" alt="Pasted image 20260824164056" />

<img src="../images/Pasted%20image%2020260824164109.png" width="313" alt="Pasted image 20260824164109" />

Así que empiezo a probar payloads, primero hago `admin'-- -` para entrar directamente como Admin y conseguimos acceso:

<img src="../images/Pasted%20image%2020260824164400.png" width="364" alt="Pasted image 20260824164400" />

Además si pruebo `' OR '1'='1'-- -` en vez de `admin'-- -`  nos encontramos con otro usuario llamado Mario pero que no tiene acceso a este panel de administración.

En esta situación me quedé un poco atascado, tenía una idea de como seguir pero decidí probar otras cosas, como investigar los directorios donde no me dejaba meterme antes para ver si podía hacer algún tipo de bypass o en el panel de login. Es cuando decidí utilizar sqlmap para sacar credenciales.

```bash
sqlmap -r req.txt --batch --dbs
```

Utilizo `-r` para que SQLmap reproduzca la petición HTTP capturada por Burp Suite, incluyendo método, parámetros, cookies y demás cabeceras necesarias para mantener el contexto de la aplicación. Este comando me dió bastante información, como el DBMS y enumeró cinco bases de datos, entre ellas `register`.

![Pasted image 20260824164753](../images/Pasted%20image%2020260824164753.png)

Procedemos a ver las tablas de la base de datos `register`:

```bash
sqlmap -r req.txt -D register --tables
```

![Pasted image 20260824164853](../images/Pasted%20image%2020260824164853.png)

Solo tenía una, que era users, vemos las columnas que tiene con:

```bash
sqlmap -r req.txt -D register -T users --columns
```

![Pasted image 20260824164952](../images/Pasted%20image%2020260824164952.png)

3 Columnas, el id, la contraseña y el username. Procedemos a ver el contenido con:

```bash
sqlmap -r req.txt -D register -T users -C id,passwd,username --dump
```

![Pasted image 20260824165057](../images/Pasted%20image%2020260824165057.png)

Y nos dió esto, las probé en SSH, pero no funcionaban, así que deduje que esto había que hacerlo antes de entrar a `/bills/` como administrador, pero yo me adelanté usando `admin'-- -`.

Así que volví al panel de facturas y vi que tenía 2 facturas disponibles, una se llamaba `xya456` y otra `xyu597`. Vemos una estructura clara, empieza por xy, luego una letra y luego 3 números, podemos ver si hay alguna factura escondida.
Veo que esta solicitud se hace con esta URL `http://172.17.0.2/bills/panel.php?id=xyu597` así que decido usar ffuf y otra herramienta para automatizar este proceso.

```bash
crunch 4 4 -t @%%% | ffuf -c -w - -b "PHPSESSID=hvurh7b97lmbi7pc2l0vbv53md" -u "http://172.17.0.2/bills/panel.php?id=xyFUZZ" --fw 2616,2715
```

Estos son 2 comandos en uno, primero generamos una wordlist usando crunch, especificándole con el 4 4 el mínimo y máximo de carácteres, y con -t @%%%% la estrucutra, siendo @ la letra y % un número. Luego usamos ffuf para coger esta wordlist y usarla para escanear en esa URL dada, esto lo hacemos usando el parámetro -w - que dice que la wordlist viene de stdin. Además le damos la Cookie con -b para que pueda acceder al panel y filtramos falsos positivos con --fw:

![Pasted image 20260824165822](../images/Pasted%20image%2020260824165822.png)

Nos encuentra esta factura, la buscamos y encontramos credenciales del usuario duque.

![Pasted image 20260824170133](../images/Pasted%20image%2020260824170133.png)

---

## Acceso inicial (Foothold)

Inicié sesión por SSH con las credenciales encontradas anteriormente:

<img src="../images/Pasted%20image%2020260824170204.png" width="421" alt="Pasted image 20260824170204" />

---

## Escalada de Privilegios

Usé sudo -l y find y encontré un binario que puedo ejecutar con root, siendo este `/usr/bin/env/`, así que decido irme a GTFObins, buscar el binario, copiar el payload y pegarlo:

![Pasted image 20260824170406](../images/Pasted%20image%2020260824170406.png)

Así nos convertimos en root.
