# DockerLabs Writeups

> Colección personal de writeups y metodologías detalladas paso a paso para la resolución de laboratorios vulnerables de la plataforma **[DockerLabs](https://dockerlabs.es/)**.

[![Platform](https://img.shields.io/badge/Platform-DockerLabs-blue.svg)](https://dockerlabs.es/)
[![Machines](https://img.shields.io/badge/Completed-14%20Machines-brightgreen.svg)](#índice-de-máquinas)
[![Difficulty](https://img.shields.io/badge/Difficulty-Very%20Easy%20%7C%20Easy-orange.svg)](#índice-de-máquinas)
[![Author](https://img.shields.io/badge/Author-s7mu-blueviolet.svg)](https://github.com/s7mu)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## Descripción

Este repositorio documenta el proceso de auditoría y explotación (*walkthroughs*) de diferentes entornos de **DockerLabs**, abarcando desde la fase de reconocimiento inicial hasta la obtención de privilegios de administrador (`root`).

Cada writeup sigue una metodología estructurada:
1. **Reconocimiento y escaneo**: Identificación de puertos abiertos, versiones y servicios (`nmap`, `netcat`, scripts NSE).
2. **Enumeración web y de servicios**: Descubrimiento de rutas ocultas, CMS, parámetros vulnerables y credenciales débiles.
3. **Acceso inicial (Foothold)**: Explotación de vulnerabilidades web (LFI, SQLi, wrappers PHP, backdoors, fuerza bruta SSH/FTP).
4. **Escalada de privilegios**: Análisis del sistema, abusos de permisos (`sudo -l`), secuestro de scripts, tareas programadas o binarios con capacidades especiales.

---

## Estadísticas

| Dificultad | Máquinas resueltas | Sistema Operativo |
| :--- | :---: | :---: |
| 🟢 **Very Easy** | 7 | Linux |
| 🟡 **Easy** | 7 | Linux |
| **Total** | **14** | **100% Linux** |

---

## Índice de Máquinas

### 🟢 Very Easy

| Máquina | Dificultad | SO | Vector de Ataque / Técnicas | Writeup |
| :--- | :---: | :---: | :--- | :---: |
| **BreakMySSH** | `Very Easy` | Linux | Fuerza bruta SSH con Hydra, credenciales débiles, root directo | [Leer](Very-Easy/BreakMySSH.md) |
| **BorazuwarahCTF** | `Very Easy` | Linux | Esteganografía (`steghide`), extracción de datos, fuerza bruta SSH | [Leer](Very-Easy/BorazuwarahCTF.md) |
| **HedgeHog** | `Very Easy` | Linux | Fuerza bruta SSH, escalada de privilegios | [Leer](Very-Easy/HedgeHog.md) |
| **Obsession** | `Very Easy` | Linux | Fuzzing web de rutas, enumeración de servicios y protocolos de red | [Leer](Very-Easy/Obsession.md) |
| **Tproot** | `Very Easy` | Linux | Explotación de backdoor vsftpd 2.3.4 (CVE-2011-2523), root shell | [Leer](Very-Easy/Tproot.md) |
| **Trust** | `Very Easy` | Linux | Enumeración Apache, SSH, escalada mediante `sudo` | [Leer](Very-Easy/Trust.md) |
| **Vacaciones** | `Very Easy` | Linux | Fuerza bruta contra servicio SSH, escalada de privilegios vía `sudo` | [Leer](Very-Easy/Vacaciones.md) |

---

### 🟡 Easy

| Máquina | Dificultad | SO | Vector de Ataque / Técnicas | Writeup |
| :--- | :---: | :---: | :--- | :---: |
| **Duque** | `Easy` | Linux | Inyección SQL (SQLi), volcado de hashes, John the Ripper, escalada | [Leer](Easy/Duque.md) |
| **ForbiddenHack** | `Easy` | Linux | Bypass de código 403 Forbidden, LFI con PHP Filters / Wrappers, escalada | [Leer](Easy/ForbiddenHack.md) |
| **hannah_coffee** | `Easy` | Linux | Enumeración web, extracción de credenciales, Reverse Shell en Bash | [Leer](Easy/hannah_coffee.md) |
| **Injection** | `Easy` | Linux | Inyección SQL manual y automatizada con SQLMap, escalada | [Leer](Easy/Injection.md) |
| **PequeñasMentirosas** | `Easy` | Linux | Fuzzing con Gobuster, credenciales SSH, permisos de lectura y escritura | [Leer](Easy/PequeñasMentirosas.md) |
| **Psycho** | `Easy` | Linux | LFI, lectura de claves SSH privadas (`id_rsa`), escalada con Python y `sudo -l` | [Leer](Easy/Psycho.md) |
| **WalkingCMS** | `Easy` | Linux | Enumeración WordPress (`wpscan`), plugin malicioso, Reverse Shell, sudoers | [Leer](Easy/WalkingCMS.md) |

---

## Herramientas Principales

- **Reconocimiento & Escaneo:** `nmap`, `netcat`, `whatweb`
- **Fuzzing & Enumeración Web:** `gobuster`, `ffuf`, `wfuzz`, `wpscan`
- **Fuerza Bruta & Cracking:** `hydra`, `john`, `rockyou.txt`, `seclists`
- **Explotación & Análisis:** `sqlmap`, `steghide`, `exiftool`, PHP filters

---

## Disclaimer

La información y writeups contenidos en este repositorio tienen fines estrictamente **educativos y de aprendizaje** en entornos de laboratorio controlados. El autor no se hace responsable del uso indebido de las técnicas y herramientas descritas.

---

## Licencia

Distribuido bajo la Licencia MIT. Consulta [LICENSE](LICENSE) para más información.

Creado por [s7mu](https://github.com/s7mu).
