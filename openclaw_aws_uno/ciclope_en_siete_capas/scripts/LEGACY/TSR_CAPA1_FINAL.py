"""
fusionar_tsr_final.py - Fusiona TSR_CAPA1_Completa.json con TSR_CAPA1_Reintentos.json
"""
import json
from pathlib import Path
from collections import defaultdict

def cargar_tsrs(archivo, es_reintentos=False):
    """Carga TSRs desde un archivo, manejando diferentes estructuras."""
    with open(archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    if 'clusters' in datos:
        # Si tiene estructura de clusters, extraer todos los TSRs
        tsrs = []
        for cluster in datos['clusters'].values():
            tsrs.extend(cluster)
        return tsrs, 'clusters'
    elif 'resultados' in datos:
        return datos['resultados'], 'resultados'
    elif isinstance(datos, list):
        return datos, 'lista'
    else:
        return [], 'desconocido'

def fusionar_tsrs(completos, reintentos):
    """Fusiona listas de TSRs, priorizando los reintentos."""
    # Crear índice de TSRs por número
    indice = {str(tsr.get('tsr', tsr.get('numero', ''))): tsr for tsr in completos}
    
    # Actualizar con reintentos
    for tsr in reintentos:
        num_tsr = str(tsr.get('tsr', tsr.get('numero', '')))
        indice[num_tsr] = tsr  # Sobrescribe con versión de reintentos
    
    return list(indice.values())

def guardar_final(tsrs, archivo_salida, estructura_original='clusters'):
    """Guarda los TSRs fusionados manteniendo la estructura original."""
    if estructura_original == 'clusters':
        # Reconstruir estructura de clusters
        clusters = defaultdict(list)
        for tsr in tsrs:
            cluster = tsr.get('cluster', 'Sin cluster')
            clusters[cluster].append(tsr)
        
        datos = {
            'metadata': {
                'version': '1.0',
                'fecha_fusion': '2026-02-11',
                'total_tsrs': len(tsrs),
                'total_clusters': len(clusters)
            },
            'clusters': dict(clusters)
        }
    else:
        datos = {
            'metadata': {
                'version': '1.0',
                'fecha_fusion': '2026-02-11',
                'total_tsrs': len(tsrs)
            },
            'resultados': tsrs
        }
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

def main():
    print("="*80)
    print("🔄 FUSIONANDO TSRs COMPLETOS CON REINTENTOS")
    print("="*80)
    
    # Configuración
    dir_actual = Path(__file__).parent
    archivo_completo = dir_actual / "TSR_CAPA1_Completa.json"
    archivo_reintentos = dir_actual / "TSR_CAPA1_Reintentos.json"
    archivo_salida = dir_actual / "TSR_CAPA1_FINAL.json"
    
    # Cargar datos
    print("\n📂 Cargando archivos...")
    tsrs_completos, estructura = cargar_tsrs(archivo_completo)
    tsrs_reintentos, _ = cargar_tsrs(archivo_reintentos, es_reintentos=True)
    
    print(f"   - TSRs en archivo completo: {len(tsrs_completos)}")
    print(f"   - TSRs en reintentos: {len(tsrs_reintentos)}")
    
    # Fusionar
    print("\n🔄 Fusionando TSRs...")
    tsrs_finales = fusionar_tsrs(tsrs_completos, tsrs_reintentos)
    print(f"   - TSRs únicos en archivo final: {len(tsrs_finales)}")
    
    # Guardar
    print(f"\n💾 Guardando archivo final: {archivo_salida}")
    guardar_final(tsrs_finales, archivo_salida, estructura)
    
    print("\n" + "="*80)
    print("✅ FUSIÓN COMPLETADA CON ÉXITO")
    print("="*80)
    print(f"📄 Archivo generado: {archivo_salida}")
    print(f"📊 Total TSRs: {len(tsrs_finales)}")
    print("="*80)

if __name__ == "__main__":
    main()