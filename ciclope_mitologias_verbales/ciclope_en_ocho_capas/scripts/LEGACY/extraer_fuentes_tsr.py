"""
extraer_fuentes_tsr.py - Extrae TODAS las fuentes de los archivos TSR
"""
import json
import os
from pathlib import Path
from collections import defaultdict

def extraer_todas_las_fuentes(archivo_json):
    """Extrae todas las fuentes de un archivo JSON, sin importar la estructura."""
    with open(archivo_json, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    fuentes_por_tsr = defaultdict(list)
    
    # Función recursiva para buscar fuentes
    def buscar_fuentes(objeto, ruta=[]):
        if isinstance(objeto, dict):
            # Si encontramos una fuente (tiene 'titulo' y 'autor')
            if 'titulo' in objeto and 'autor' in objeto:
                return [objeto]
            
            # Buscar en todos los valores del diccionario
            fuentes = []
            for valor in objeto.values():
                fuentes.extend(buscar_fuentes(valor, ruta + [str(valor)[:50]]))
            return fuentes
            
        elif isinstance(objeto, list):
            # Buscar en todos los elementos de la lista
            fuentes = []
            for item in objeto:
                fuentes.extend(buscar_fuentes(item, ruta + ['item']))
            return fuentes
            
        return []

    # Buscar TSRs en diferentes estructuras posibles
    posibles_tsrs = []
    if 'clusters' in datos:
        for cluster in datos['clusters'].values():
            posibles_tsrs.extend(cluster)
    if 'resultados' in datos:
        posibles_tsrs.extend(datos['resultados'])
    if not posibles_tsrs:
        posibles_tsrs = [datos]  # Intentar con el objeto raíz

    # Procesar cada TSR encontrado
    for tsr in posibles_tsrs:
        if not isinstance(tsr, dict):
            continue
            
        # Obtener número de TSR
        numero_tsr = tsr.get('tsr') or tsr.get('numero') or 'DESCONOCIDO'
        
        # Buscar fuentes en el TSR
        fuentes = buscar_fuentes(tsr)
        
        # Si no se encontraron fuentes, buscar en otros campos comunes
        if not fuentes and 'fuentes' in tsr:
            fuentes = tsr['fuentes']
        
        if fuentes:
            fuentes_por_tsr[numero_tsr].extend(fuentes)
    
    return dict(fuentes_por_tsr)

def guardar_informe(fuentes_por_tsr, archivo_salida):
    """Guarda un informe detallado de las fuentes encontradas."""
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("INFORME DE FUENTES POR TSR\n")
        f.write("="*80 + "\n\n")
        
        total_fuentes = 0
        
        for tsr, fuentes in sorted(fuentes_por_tsr.items()):
            f.write(f"TSR-{tsr}: {len(fuentes)} fuentes\n")
            f.write("-"*40 + "\n")
            
            for i, fuente in enumerate(fuentes, 1):
                f.write(f"{i}. {fuente.get('titulo', 'Sin título')}\n")
                if 'autor' in fuente:
                    f.write(f"   Autor: {fuente['autor']}\n")
                if 'año' in fuente:
                    f.write(f"   Año: {fuente['año']}\n")
                if 'url' in fuente:
                    f.write(f"   URL: {fuente['url']}\n")
                f.write("\n")
            
            total_fuentes += len(fuentes)
            f.write("\n")
        
        f.write("="*80 + "\n")
        f.write(f"TOTAL DE TSRs: {len(fuentes_por_tsr)}\n")
        f.write(f"TOTAL DE FUENTES: {total_fuentes}\n")
        f.write("="*80 + "\n")

def main():
    print("="*80)
    print("🔍 EXTRAER TODAS LAS FUENTES DE TSRs")
    print("="*80)
    
    # Configuración
    archivo_json = input("Ruta del archivo JSON de TSRs: ").strip('"')
    if not os.path.exists(archivo_json):
        print(f"❌ Error: El archivo {archivo_json} no existe")
        return
    
    # Extraer fuentes
    print("\n🔍 Buscando fuentes...")
    fuentes_por_tsr = extraer_todas_las_fuentes(archivo_json)
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE FUENTES ENCONTRADAS")
    print("="*80)
    for tsr, fuentes in sorted(fuentes_por_tsr.items()):
        print(f"TSR-{tsr}: {len(fuentes)} fuentes")
    
    total_fuentes = sum(len(fuentes) for fuentes in fuentes_por_tsr.values())
    print(f"\nTOTAL: {total_fuentes} fuentes en {len(fuentes_por_tsr)} TSRs")
    
    # Guardar informe
    carpeta_salida = "informe_fuentes"
    os.makedirs(carpeta_salida, exist_ok=True)
    
    nombre_archivo = os.path.basename(archivo_json)
    archivo_salida = os.path.join(carpeta_salida, f"fuentes_{nombre_archivo}.txt")
    
    guardar_informe(fuentes_por_tsr, archivo_salida)
    print(f"\n📄 Informe guardado en: {os.path.abspath(archivo_salida)}")
    print("="*80)

if __name__ == "__main__":
    main()