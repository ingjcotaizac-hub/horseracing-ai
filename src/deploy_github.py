"""
Script de automatización para crear el repositorio en GitHub y hacer el push del proyecto.
"""

import os
import sys
import json
import subprocess
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def create_and_push_repo():
    # 1. Leer el token desde mcp_config.json
    mcp_path = r"C:\Users\Otaingenio\.gemini\config\mcp_config.json"
    token = None
    for enc in ['utf-8-sig', 'utf-8', 'utf-16']:
        try:
            cfg = json.load(open(mcp_path, encoding=enc))
            token = cfg['mcpServers']['github-mcp-server']['env']['GITHUB_PERSONAL_ACCESS_TOKEN']
            break
        except Exception:
            continue

    if not token:
        print("Error: No se pudo leer el token de mcp_config.json")
        return False

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 2. Verificar usuario
    u_res = requests.get("https://api.github.com/user", headers=headers)
    if u_res.status_code != 200:
        print(f"Error de autenticación en GitHub: {u_res.status_code} - {u_res.text}")
        return False
    
    username = u_res.json()["login"]
    repo_name = "horseracing-ai"
    print(f"Autenticado correctamente como: {username}")

    # 3. Crear repositorio en GitHub (o comprobar si ya existe)
    repo_url_api = f"https://api.github.com/repos/{username}/{repo_name}"
    check_repo = requests.get(repo_url_api, headers=headers)

    if check_repo.status_code == 404:
        print(f"Creando repositorio '{repo_name}' en GitHub...")
        payload = {
            "name": repo_name,
            "description": "Sistema de Pronósticos, Speed Figures y Past Performances Propias para Carreras USA",
            "private": False, # Público para despliegue directo e ilimitado en Streamlit Cloud
            "auto_init": False
        }
        create_res = requests.post("https://api.github.com/user/repos", headers=headers, json=payload)
        if create_res.status_code not in [200, 201]:
            print(f"Error al crear repositorio: {create_res.status_code} - {create_res.text}")
            return False
        print(f"Repositorio creado con éxito en GitHub: https://github.com/{username}/{repo_name}")
    else:
        print(f"El repositorio '{repo_name}' ya existía en tu cuenta de GitHub.")

    # 4. Configurar el control remoto de git y hacer push
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auth_remote_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    public_remote_url = f"https://github.com/{username}/{repo_name}.git"

    # Remover remote origin si ya existía
    subprocess.run(["git", "remote", "remove", "origin"], cwd=project_dir, capture_output=True)

    # Añadir remote con autenticación para el push
    add_rem = subprocess.run(["git", "remote", "add", "origin", auth_remote_url], cwd=project_dir, capture_output=True, text=True)
    if add_rem.returncode != 0:
        print(f"Aviso al configurar remote: {add_rem.stderr}")

    print("Subiendo código a la rama main de GitHub...")
    push_res = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=project_dir, capture_output=True, text=True)
    
    # Restaurar remote URL sin token en texto plano por seguridad
    subprocess.run(["git", "remote", "set-url", "origin", public_remote_url], cwd=project_dir, capture_output=True)

    if push_res.returncode == 0:
        print("\n¡SUBIDA COMPLETADA CON ÉXITO! 🚀")
        print(f"Tu repositorio está disponible en: {public_remote_url}")
        return True
    else:
        print(f"Error al hacer git push: {push_res.stderr}")
        return False

if __name__ == "__main__":
    create_and_push_repo()
