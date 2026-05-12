#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
limpiar_memoria_github.py
========================

Limpia toda la memoria de GitHub sobre el repositorio Cíclope
para poder subirlo como si fuera nuevo, preservando el código local.

Uso:
    python scripts/limpiar_memoria_github.py --auto
    python scripts/limpiar_memoria_github.py --limpiar-desktop
    python scripts/limpiar_memoria_github.py --limpiar-copilot
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List

class GitHubMemoryCleaner:
    """Limpia memoria de GitHub del repositorio Cíclope"""
    
    def __init__(self):
        self.user_home = Path.home()
        self.repo_path = Path(os.getcwd())
        
        # Rutas de caché en Windows
        self.github_desktop_cache = self.user_home / "AppData" / "Roaming" / "GitHub Desktop" / "repositories"
        self.github_desktop_cache_local = self.user_home / "AppData" / "Local" / "GitHub Desktop" / "cache"
        self.copilot_cache = self.user_home / ".copilot" / "cache"
        self.copilot_roaming = self.user_home / "AppData" / "Roaming" / "copilot"
        
    def limpiar_github_desktop(self):
        """Limpia caché de GitHub Desktop"""
        print("🧹 Limpiando caché de GitHub Desktop...")
        
        try:
            # Limpiar repositorio específico si existe
            repo_cache = self.github_desktop_cache / "ciclope_mitologias_verbales"
            if repo_cache.exists():
                shutil.rmtree(repo_cache)
                print(f"✅ Eliminado: {repo_cache}")
            
            # Limpiar caché general
            if self.github_desktop_cache_local.exists():
                for item in self.github_desktop_cache_local.iterdir():
                    if "ciclope" in item.name.lower():
                        shutil.rmtree(item)
                        print(f"✅ Eliminado: {item}")
            
            return True
        except Exception as e:
            print(f"❌ Error limpiando GitHub Desktop: {e}")
            return False
    
    def limpiar_copilot_cli(self):
        """Limpia caché de Copilot CLI"""
        print("🧹 Limpiando caché de Copilot CLI...")
        
        try:
            # Limpiar caché local
            if self.copilot_cache.exists():
                for item in self.copilot_cache.iterdir():
                    if "ciclope" in item.name.lower():
                        shutil.rmtree(item)
                        print(f"✅ Eliminado: {item}")
            
            # Limpiar caché roaming
            if self.copilot_roaming.exists():
                for item in self.copilot_roaming.iterdir():
                    if "ciclope" in item.name.lower():
                        shutil.rmtree(item)
                        print(f"✅ Eliminado: {item}")
            
            return True
        except Exception as e:
            print(f"❌ Error limpiando Copilot CLI: {e}")
            return False
    
    def limpiar_vscode_git(self):
        """Limpia caché de Git en VSCode"""
        print("🧹 Limpiando caché de VSCode Git...")
        
        try:
            vscode_cache = self.user_home / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "github.copilot"
            if vscode_cache.exists():
                shutil.rmtree(vscode_cache)
                print(f"✅ Eliminado: {vscode_cache}")
            
            return True
        except Exception as e:
            print(f"❌ Error limpiando VSCode Git: {e}")
            return False
    
    def preparar_nuevo_branch(self):
        """Prepara el repositorio para subir como nuevo"""
        print("🔄 Preparando repositorio para subida nueva...")
        
        try:
            # Crear branch principal
            result = subprocess.run(['git', 'checkout', '-b', 'main'], 
                                  cwd=self.repo_path,
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Branch 'main' creado")
            else:
                print(f"⚠️  Branch posiblemente ya existe: {result.stderr}")
            
            # Verificar estado
            result = subprocess.run(['git', 'status'], 
                                  cwd=self.repo_path,
                                  capture_output=True, text=True)
            print(f"\n📊 Estado actual:\n{result.stdout}")
            
            return True
        except Exception as e:
            print(f"❌ Error preparando branch: {e}")
            return False
    
    def generar_instrucciones(self):
        """Genera instrucciones para subida a GitHub"""
        print("\n" + "="*60)
        print("📋 INSTRUCCIONES PARA SUBIDA A GITHUB")
        print("="*60)
        
        print("""
1. **Eliminar repositorio existente en GitHub** (si aplica):
   - Ir a: https://github.com/KhaosLiminal/ciclope_mitologias_verbales
   - Settings → Delete repository
   - Confirmar eliminación

2. **Crear nuevo repositorio en GitHub**:
   - Nombre: ciclope_mitologias_verbales (o ciclope_mitologias_verbales_v2)
   - Marcar como privado o público según prefieras
   - ⚠️ NO inicializar con README, .gitignore o licencia

3. **Conectar repositorio local**:
   git remote add origin https://github.com/KhaosLiminal/ciclope_mitologias_verbales_v2.git

4. **Subir a GitHub**:
   git add .
   git commit -m "Subida inicial - Repositorio limpio"
   git push -u origin main

5. **Verificar subida**:
   - Visita el repositorio en GitHub
   - Verifica que todos los archivos estén presentes
   - Confirma que el historial se mantuvo intacto
        """)
        
        print("="*60)
        print("✅ Memoria remota eliminada - Repositorio listo para subida")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Limpia memoria de GitHub del repositorio Cíclope')
    parser.add_argument('--auto', action='store_true', 
                       help='Ejecuta limpieza completa automática')
    parser.add_argument('--limpiar-desktop', action='store_true', 
                       help='Limpia solo caché de GitHub Desktop')
    parser.add_argument('--limpiar-copilot', action='store_true', 
                       help='Limpia solo caché de Copilot CLI')
    parser.add_argument('--preparar-branch', action='store_true', 
                       help='Prepara branch principal para subida')
    
    args = parser.parse_args()
    
    cleaner = GitHubMemoryCleaner()
    
    if args.auto:
        print("🚀 Iniciando limpieza completa automática...")
        cleaner.limpiar_github_desktop()
        cleaner.limpiar_copilot_cli()
        cleaner.limpiar_vscode_git()
        cleaner.preparar_nuevo_branch()
        cleaner.generar_instrucciones()
    
    elif args.limpiar_desktop:
        cleaner.limpiar_github_desktop()
    
    elif args.limpiar_copilot:
        cleaner.limpiar_copilot_cli()
    
    elif args.preparar_branch:
        cleaner.preparar_nuevo_branch()
        cleaner.generar_instrucciones()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
