# DockerLabs — HedgeHog

![Plataforma](https://img.shields.io/badge/Plataforma-DockerLabs-21262d?style=flat)
![Dificultad](https://img.shields.io/badge/Dificultad-Very%20Easy-238636?style=flat)
![SO](https://img.shields.io/badge/SO-Linux-21262d?style=flat&logo=linux&logoColor=FCC624)
![Estado](https://img.shields.io/badge/Estado-Completada-238636?style=flat)

---

## Resumen

Laboratorio para practicar fuerza bruta SSH y escalada de privilegios mediante movimiento entre usuarios.

---

## Reconocimiento

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
nmap -sCV -p22,80 172.17.0.2
```

Nos encontramos 2 servicios corriendo, un servidor web y SSH.

En la página nos encontramos todo en blanco y un nombre, tails, que en el contexto de la máquina pienso que es el usuario para hacer luego un ataque de fuerza bruta al ssh.

![Pasted image 20260814154016](../images/Pasted%20image%2020260814154016.png)

---

## Enumeración

Empezamos a hacer un ataque de fuerza bruta con este comando:

```bash
hydra -l tails -P rockyourev.txt -t 4 -f ssh://172.17.0.2
```

Para conseguir el `rockyourev.txt` hice este comando para invertir las líneas:

```bash
tac /usr/share/wordlists/rockyou.txt | tr -d ' ' > rockyourev.txt
```

donde el parámetro -f detendrá el proceso al encontrar el primer match:

![Pasted image 20260814155303](../images/Pasted%20image%2020260814155303.png)

Y nos encontramos una contraseña para entrar por SSH.

> [!NOTE]
> **Aclaración:** Antes de esto, estuve varios minutos intentando con el rockyou normal, pero al ver que no conseguía nada, pensé en invertirlo. Además, antes investigué toda la página web intentando encontrar otros directorios o archivos.

---

## Acceso inicial (Foothold)

Con las credenciales que tenía antes logré entrar.

![Pasted image 20260814155701](../images/Pasted%20image%2020260814155701.png)

Vi que en /home había otro usuario, sonic. 

---

## Escalada de Privilegios

```bash
sudo -l
```

Con este comando vi que podía ejecutar cualquier comando como sonic, así que me hice una bash con ese usuario:

```bash
sudo -u sonic bash
```

![Pasted image 20260814155914](../images/Pasted%20image%2020260814155914.png)

Siendo sonic, pude entrar a su home ya que antes no tenía permisos, en su home había un fichero llamado contraseña con este contenido: **perritos!** intenté hacer `su root` con esa contraseña pero fallé, así que hice `sudo -l` otra vez y vii que tenia via libre para hacer sudo su y convertirme en root.

![Pasted image 20260814160114](../images/Pasted%20image%2020260814160114.png)
