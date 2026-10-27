#!/usr/bin/env python3
"""
sync.py - Sincroniza writeups de DockerLabs desde el vault de Obsidian al repositorio.
Lee en modo de solo lectura desde /home/samu/obsidian-vault sin modificar el vault.
"""

import os
import glob
import re
import shutil
import urllib.parse

VAULT_DIR = os.path.expanduser('~/obsidian-vault')
SRC_BASE = os.path.join(VAULT_DIR, 'CyberSec/09 - CTF/DockerLabs')
IMG_SRC_DIR = os.path.join(VAULT_DIR, 'Imágenes')
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    if not os.path.exists(SRC_BASE):
        print(f"Error: No se encuentra la ruta origen en {SRC_BASE}")
        return

    os.makedirs(os.path.join(REPO_DIR, 'Very-Easy'), exist_ok=True)
    os.makedirs(os.path.join(REPO_DIR, 'Easy'), exist_ok=True)
    os.makedirs(os.path.join(REPO_DIR, 'images'), exist_ok=True)

    files = glob.glob(f'{SRC_BASE}/**/*.md', recursive=True)
    copied_images = set()
    processed_count = 0

    for f in sorted(files):
        with open(f, 'r', encoding='utf-8') as fp:
            content = fp.read()

        rel = os.path.relpath(f, SRC_BASE)
        folder = rel.split('/')[0]
        target_folder = 'Very-Easy' if 'Very' in folder else 'Easy'
        base_name = os.path.basename(f).replace('DL-', '')

        # Extraer metadatos y eliminar el bloque YAML frontmatter
        diff = 'Very Easy' if 'Very' in folder else 'Easy'
        fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            content = content[fm_match.end():]
            diff_match = re.search(r'difficulty:\s*([^\n]+)', fm_text)
            if diff_match:
                diff = diff_match.group(1).strip()

        # Eliminar las secciones '## Técnicas usadas' y '## Qué aprendí'
        if '## Técnicas usadas' in content:
            content = content.split('## Técnicas usadas')[0]
        elif '## Tecnicas usadas' in content:
            content = content.split('## Tecnicas usadas')[0]

        if '## Qué aprendí' in content:
            content = content.split('## Qué aprendí')[0]
        elif '## Que aprendi' in content:
            content = content.split('## Que aprendi')[0]

        content = content.rstrip()
        while content.endswith('---'):
            content = content[:-3].rstrip()
        content += '\n'

        # Limpiar emoji y placeholder en encabezado si existiera
        content = content.replace('# 🏴 DockerLabs', '# DockerLabs')
        content = content.replace('# 🏴 Dockerlabs', '# DockerLabs')
        content = content.replace('# DockerLabs — <Nombre Máquina>', f'# DockerLabs — {base_name.replace(".md", "")}')

        # Reemplazar wikilinks [[Tool]] -> **Tool**
        content = re.sub(r'(?<!\!)\[\[(.*?)\]\]', lambda m: f'**{m.group(1).split("|")[-1]}**', content)

        # Formatear callouts/alerts de GitHub Flavored Markdown (GFM)
        content = re.sub(
            r'>\s*\[!NOTE\]\s+([A-Za-z0-9_¿¡].*?)\n>\s*',
            r'> [!NOTE]\n> **\1:** ',
            content
        )
        content = re.sub(
            r'>\s*\[!NOTE\]\s*¿Por qué\?\s*\n([^>\n][^\n]*)',
            r'> [!NOTE]\n> **¿Por qué?** \1',
            content
        )

        # Reemplazar imágenes ![[img.png|size]] -> standard markdown / img
        def replace_img(m):
            parts = m.group(1).split('|')
            img_name = parts[0].strip()
            width = parts[1].strip() if len(parts) > 1 else None

            src_img = os.path.join(IMG_SRC_DIR, img_name)
            dst_img = os.path.join(REPO_DIR, 'images', img_name)
            if os.path.exists(src_img):
                shutil.copy2(src_img, dst_img)
                copied_images.add(img_name)

            enc_url = f'../images/{urllib.parse.quote(img_name)}'
            alt = img_name.replace('.png', '').replace('.jpg', '')
            if width and width.isdigit():
                return f'<img src="{enc_url}" width="{width}" alt="{alt}" />'
            return f'![{alt}]({enc_url})'

        content = re.sub(r'!\[\[(.*?)\]\]', replace_img, content)

        # Separar múltiples imágenes en una misma línea
        content = re.sub(r'(<img[^>]+>)\s*(<img[^>]+>)', r'\1\n\n\2', content)

        # Asegurar salto de línea antes y después de cada imagen
        lines = content.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            is_img = ('<img ' in line) or (re.search(r'^!\[.*?\]\(.*?\)$', line.strip()) is not None)
            if is_img:
                if new_lines and new_lines[-1].strip() != '':
                    new_lines.append('')
                new_lines.append(line.strip())
                if i + 1 < len(lines) and lines[i+1].strip() != '':
                    new_lines.append('')
            else:
                new_lines.append(line)

        cleaned = '\n'.join(new_lines)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip() + '\n'

        # Generar badges de metadatos estéticos
        diff_badge_text = 'Very%20Easy' if 'very' in diff.lower() else 'Easy'
        diff_color = '238636' if 'very' in diff.lower() else 'e3b341'
        badges = (
            f'![Plataforma](https://img.shields.io/badge/Plataforma-DockerLabs-21262d?style=flat)\n'
            f'![Dificultad](https://img.shields.io/badge/Dificultad-{diff_badge_text}-{diff_color}?style=flat)\n'
            f'![SO](https://img.shields.io/badge/SO-Linux-21262d?style=flat&logo=linux&logoColor=FCC624)\n'
            f'![Estado](https://img.shields.io/badge/Estado-Completada-238636?style=flat)'
        )

        # Insertar badges tras el título
        h1_match = re.search(r'^(# [^\n]+)\n+', cleaned)
        if h1_match:
            h1 = h1_match.group(1)
            rest = cleaned[h1_match.end():].lstrip()
            if rest.startswith('## Resumen'):
                final_content = f'{h1}\n\n{badges}\n\n---\n\n{rest}'
            else:
                final_content = f'{h1}\n\n{badges}\n\n{rest}'
        else:
            final_content = f'{badges}\n\n{cleaned}'

        target_file = os.path.join(REPO_DIR, target_folder, base_name)
        with open(target_file, 'w', encoding='utf-8') as fp:
            fp.write(final_content)

        processed_count += 1

    print(f"Sincronización completada con éxito.")
    print(f"- Writeups procesados: {processed_count}")
    print(f"- Imágenes vinculadas y copiadas: {len(copied_images)}")

if __name__ == '__main__':
    main()
