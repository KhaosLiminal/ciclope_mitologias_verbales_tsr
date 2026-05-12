#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
restaurar_memoria.py
===================

Script de recuperación de memoria para el proyecto Cíclope.
Diagnostica y restaura la conexión con memoria remota devorada.

Uso:
    python scripts/restaurar_memoria.py --diagnosticar
    python scripts/restaurar_memoria.py --recuperar --origen <url>
    python scripts/restaurar_memoria.py --backup-automático
"""

import os
import sys
import json
import argparse
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class MemoryRestorer:
    """Sistema de recuperación de memoria del repositorio Cíclope"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.remotes_found = []
        self.dangling_blobs = 0
        self.diagnostico = {
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(self.repo_path),
            "estado": "aislado",
            "remotos": [],
            "vulnerabilidades": []
        }
    
    def diagnosticar_estado(self):
        """Diagnóstico completo del estado de memoria"""
        print("🔍 Iniciando diagnóstico de memoria...")
        
        # 1. Verificar remotos
        try:
            result = subprocess.run(['git', 'remote', '-v'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                self.remotes_found = result.stdout.strip().split('\n')
                print(f"✅ Remotos encontrados: {len(self.remotes_found)}")
                for remote in self.remotes_found:
                    print(f"   - {remote}")
            else:
                print("⚠️  No se encontraron remotos configurados")
        except Exception as e:
            print(f"❌ Error verificando remotos: {e}")
        
        # 2. Verificar blobs huérfanos
        try:
            result = subprocess.run(['git', 'fsck'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            if "dangling blob" in result.stdout:
                self.dangling_blobs = result.stdout.count("dangling blob")
                print(f"⚠️  Blobs huérfanos detectados: {self.dangling_blobs}")
            else:
                print("✅ No se detectaron blobs huérfanos")
        except Exception as e:
            print(f"❌ Error en fsck: {e}")
        
        # 3. Verificar estado del branch
        try:
            result = subprocess.run(['git', 'branch', '-a'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            if "HEAD detached" in result.stdout:
                print("⚠️  HEAD detached detectado")
            else:
                print("✅ Branch conectado correctamente")
        except Exception as e:
            print(f"❌ Error verificando branches: {e}")
        
        # 4. Actualizar diagnóstico
        self.diagnostico["remotos"] = self.remotes_found
        self.diagnostico["dangling_blobs"] = self.dangling_blobs
        self.diagnostico["estado"] = "diagnosticado"
        
        # 5. Identificar vulnerabilidades
        vulnerabilidades = []
        
        if not self.remotes_found:
            vulnerabilidades.append({
                "tipo": "crítica",
                "descripcion": "Sin conexión remota - pérdida total de memoria colectiva",
                "impacto": "extinción del proyecto",
                "accion": "recuperar_remoto"
            })
        
        if self.dangling_blobs > 50:
            vulnerabilidades.append({
                "tipo": "alta",
                "descripcion": f"Memoria fracturada - {self.dangling_blobs} objetos huérfanos",
                "impacto": "corrupción potencial del historial",
                "accion": "limpiar_blobs"
            })
        
        # Verificar .gitignore agresivo
        gitignore_path = self.repo_path / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "outputs/*_2026*" in content:
                    vulnerabilidades.append({
                        "tipo": "media",
                        "descripcion": ".gitignore previene archivado automático",
                        "impacto": "pérdida de capacidad de backup",
                        "accion": "ajustar_gitignore"
                    })
        
        self.diagnostico["vulnerabilidades"] = vulnerabilidades
        
        # Guardar diagnóstico
        output_path = self.repo_path / "diagnostico_memoria.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.diagnostico, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Diagnóstico guardado en: {output_path}")
        return self.diagnostico
    
    def buscar_origenes_posibles(self):
        """Busca posibles orígenes remotos del repositorio"""
        print("🔍 Buscando orígenes remotos posibles...")
        
        origenes = []
        
        # Verificar GitHub remotes
        try:
            result = subprocess.run(['git', 'remote', '-v'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if 'github.com' in line:
                        origenes.append({
                            "tipo": "GitHub",
                            "url": line.split()[1],
                            "confianza": "alta"
                        })
        except Exception as e:
            print(f"❌ Error buscando GitHub: {e}")
        
        # Verificar si hay configuración de GitHub Pages
        repo_name = self.repo_path.name
        possible_urls = [
            f"https://{repo_name}.github.io",
            f"https://github.com/{repo_name}",
            f"https://gitlab.com/{repo_name}",
            f"https://bitbucket.org/{repo_name}"
        ]
        
        for url in possible_urls:
            try:
                response = requests.get(f"{url}/{repo_name}", timeout=10)
                if response.status_code == 200:
                    origenes.append({
                        "tipo": "Web Detectada",
                        "url": url,
                        "confianza": "media"
                    })
                    print(f"✅ Posible origen encontrado: {url}")
            except:
                continue
        
        return origenes
    
    def recuperar_memoria(self, origen_url: str):
        """Intenta recuperar memoria desde un origen específico"""
        print(f"🔄 Iniciando recuperación desde: {origen_url}")
        
        try:
            # Agregar origen remoto
            result = subprocess.run(['git', 'remote', 'add', 'origin', origen_url], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Origen agregado: {origen_url}")
            else:
                print(f"❌ Error agregando origen: {result.stderr}")
                return False
            
            # Fetch para recuperar memoria
            print("📥 Recuperando memoria remota...")
            result = subprocess.run(['git', 'fetch', 'origin'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Memoria recuperada exitosamente")
            else:
                print(f"❌ Error en fetch: {result.stderr}")
                return False
            
            # Restaurar branch principal
            print("🌿 Restaurando branch principal...")
            result = subprocess.run(['git', 'checkout', 'main'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Branch principal restaurado")
            else:
                print(f"❌ Error en checkout: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error en recuperación: {e}")
            return False
    
    def limpiar_blobs_huerfanos(self):
        """Limpia blobs huérfanos para restaurar integridad"""
        print("🧹 Limpiando blobs huérfanos...")
        
        try:
            # Usar git prune para limpiar objetos inaccesibles
            result = subprocess.run(['git', 'prune', '--expire', 'now'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Blobs huérfanos limpiados")
            else:
                print(f"❌ Error en prune: {result.stderr}")
            
            # Corregir dangling commits si existen
            if self.dangling_blobs > 0:
                result = subprocess.run(['git', 'reflog', 'expire', '--expire=now', '--all'], 
                                      cwd=self.repo_path, 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Reflog limpiado")
                else:
                    print(f"❌ Error en reflog: {result.stderr}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error limpiando blobs: {e}")
            return False
    
    def implementar_backup_automatico(self):
        """Implementa sistema de backup automático"""
        print("🔄 Implementando sistema de backup automático...")
        
        # Crear script de backup
        backup_script = '''#!/bin/bash
# backup_automatico.sh
# Backup del proyecto Cíclope

REPO_DIR="{self.repo_path}"
BACKUP_DIR="$HOME/ciclope_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "🔄 Iniciando backup $TIMESTAMP..."

# Backup del código fuente
tar -czf "$BACKUP_DIR/ciclope_codigo_$TIMESTAMP.tar.gz" \\
    -C "$REPO_DIR" \\
    --exclude='.git' \\
    --exclude='outputs/*' \\
    --exclude='*.log' \\
    --exclude='__pycache__' \\
    --exclude='.venv' \\
    src/ docs/ scripts/ *.py *.md *.txt *.json

# Backup de datos generados
tar -czf "$BACKUP_DIR/ciclope_datos_$TIMESTAMP.tar.gz" \\
    -C "$REPO_DIR" \\
    capas/ outputs/ config/

# Backup de metadatos
cp "$REPO_DIR/STATUS.md" "$BACKUP_DIR/STATUS_$TIMESTAMP.md"

# Limpiar backups antiguos (mantener últimos 5)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completado: $TIMESTAMP"
echo "📁 Ubicación: $BACKUP_DIR"
echo "🔄 Siguiente backup en 24 horas"
'''
        
        backup_script_path = self.repo_path / "scripts" / "backup_automatico.sh"
        with open(backup_script_path, 'w', encoding='utf-8') as f:
            f.write(backup_script)
        
        # Hacer ejecutable
        os.chmod(backup_script_path, 0o755)
        
        print(f"✅ Script de backup creado: {backup_script_path}")
        
        # Crear tarea programada (Windows)
        try:
            result = subprocess.run(['schtasks', '/create', '/tn', 'Ciclope Backup', 
                                  '/tr', 'daily', 
                                  f'/sc', 'bash "{backup_script_path}"'],
                                  cwd=self.repo_path,
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Tarea de backup programada creada")
            else:
                print("⚠️  No se pudo crear tarea programada (requiere permisos de administrador)")
        except:
            print("⚠️  Sistema operativo no soporta tareas programadas")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Sistema de recuperación de memoria del proyecto Cíclope')
    parser.add_argument('--diagnosticar', action='store_true', 
                       help='Diagnosticar estado actual de memoria')
    parser.add_argument('--recuperar', type=str, 
                       help='Recuperar memoria desde URL específica')
    parser.add_argument('--origen', type=str, 
                       help='URL del origen remoto para recuperar')
    parser.add_argument('--limpiar-blobs', action='store_true', 
                       help='Limpiar blobs huérfanos')
    parser.add_argument('--backup-automatico', action='store_true', 
                       help='Implementar sistema de backup automático')
    
    args = parser.parse_args()
    
    # Determinar ruta del repositorio
    repo_path = os.getcwd()
    if 'cíclope_mitologías_verbales' in os.getcwd():
        repo_path = os.getcwd()
    else:
        repo_path = Path(__file__).parent.parent
    
    restorer = MemoryRestorer(repo_path)
    
    if args.diagnosticar:
        diagnostico = restorer.diagnosticar_estado()
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("📊 RESUMEN DEL DIAGNÓSTICO")
        print("="*60)
        
        print(f"Estado: {diagnostico['estado']}")
        print(f"Remotos: {len(diagnostico['remotos'])}")
        print(f"Blobs huérfanos: {diagnostico['dangling_blobs']}")
        print(f"Vulnerabilidades: {len(diagnostico['vulnerabilidades'])}")
        
        for vuln in diagnostico['vulnerabilidades']:
            print(f"  - {vuln['tipo']}: {vuln['descripcion']}")
        
        print("\n" + "="*60)
        
        # Si hay vulnerabilidades críticas, ofrecer soluciones
        criticas = [v for v in diagnostico['vulnerabilidades'] if v['tipo'] == 'crítica']
        if criticas:
            print("\n🚨 ACCIONES RECOMENDADAS:")
            for vuln in criticas:
                print(f"  • {vuln['accion']}: {vuln['descripcion']}")
            
            print("\n💡 EJECUTAR:")
            print("python scripts/restaurar_memoria.py --recuperar --origen <url>")
            print("python scripts/restaurar_memoria.py --backup-automatico")
    
    elif args.recuperar and args.origen:
        origenes = restorer.buscar_origenes_posibles()
        
        if not origenes:
            print("❌ No se encontraron orígenes posibles")
            return
        
        print("\n🔍 ORÍGENES DETECTADOS:")
        for i, origen in enumerate(origenes, 1):
            print(f"{i}. {origen['tipo']}: {origen['url']} (confianza: {origen['confianza']})")
        
        # Recuperar desde el origen especificado
        if restorer.recuperar_memoria(args.origen):
            print("\n✅ Memoria recuperada exitosamente")
        else:
            print("\n❌ Falló la recuperación de memoria")
    
    elif args.limpiar_blobs:
        if restorer.limpiar_blobs_huerfanos():
            print("\n✅ Limpieza completada")
        else:
            print("\n❌ Falló la limpieza")
    
    elif args.backup_automatico:
        if restorer.implementar_backup_automatico():
            print("\n✅ Sistema de backup implementado")
        else:
            print("\n❌ Falló la implementación")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
