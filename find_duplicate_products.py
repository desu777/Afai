#!/usr/bin/env python3
"""
Skrypt do znajdowania duplikatów product_name w plikach JSON
"""

import json
import os
from collections import defaultdict
from pathlib import Path
import sys

def find_duplicate_products(folder_path):
    """
    Znajdź duplikaty product_name w folderze z plikami JSON
    
    Args:
        folder_path (str): Ścieżka do folderu z plikami JSON
    
    Returns:
        dict: Słownik z duplikatami - klucz to product_name, wartość to lista plików
    """
    product_files = defaultdict(list)
    error_files = []
    
    # Sprawdź czy folder istnieje
    if not os.path.exists(folder_path):
        print(f"❌ Folder {folder_path} nie istnieje!")
        return {}
    
    # Przejdź przez wszystkie pliki JSON w folderze
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    if not json_files:
        print(f"❌ Brak plików JSON w folderze {folder_path}")
        return {}
    
    print(f"🔍 Sprawdzanie {len(json_files)} plików JSON...")
    
    for filename in sorted(json_files):
        file_path = os.path.join(folder_path, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Sprawdź czy plik ma poprawną strukturę
            if 'metadata' in data and 'product_name' in data['metadata']:
                product_name = data['metadata']['product_name']
                file_id = data.get('id', 'unknown')
                
                product_files[product_name].append({
                    'filename': filename,
                    'id': file_id,
                    'file_path': file_path
                })
            else:
                error_files.append(filename)
                
        except (json.JSONDecodeError, KeyError, Exception) as e:
            error_files.append(f"{filename} (błąd: {str(e)})")
    
    # Pokaż pliki z błędami
    if error_files:
        print(f"\n⚠️  Pliki z błędami struktury ({len(error_files)}):")
        for error_file in error_files:
            print(f"   - {error_file}")
    
    # Znajdź duplikaty (produkty występujące w więcej niż jednym pliku)
    duplicates = {name: files for name, files in product_files.items() if len(files) > 1}
    
    return duplicates, product_files

def print_results(duplicates, all_products):
    """Wyświetl wyniki analizy"""
    
    print(f"\n📊 STATYSTYKI:")
    print(f"   - Łączna liczba produktów: {len(all_products)}")
    print(f"   - Unikalne nazwy produktów: {len(all_products)}")
    print(f"   - Duplikaty nazw: {len(duplicates)}")
    
    if duplicates:
        print(f"\n🔴 ZNALEZIONE DUPLIKATY ({len(duplicates)}):")
        print("=" * 80)
        
        for product_name, files in duplicates.items():
            print(f"\n📦 Product: '{product_name}'")
            print(f"   Liczba wystąpień: {len(files)}")
            print("   Pliki:")
            
            for file_info in files:
                print(f"     - {file_info['filename']} (ID: {file_info['id']})")
        
        print("\n" + "=" * 80)
        
        # Podsumowanie duplikatów
        total_duplicate_files = sum(len(files) for files in duplicates.values())
        print(f"📈 PODSUMOWANIE DUPLIKATÓW:")
        print(f"   - Nazw produktów z duplikatami: {len(duplicates)}")
        print(f"   - Łączna liczba plików z duplikatami: {total_duplicate_files}")
        print(f"   - Nadmiarowe pliki: {total_duplicate_files - len(duplicates)}")
        
    else:
        print(f"\n✅ Nie znaleziono duplikatów! Wszystkie product_name są unikalne.")

def save_results_to_file(duplicates, output_file="duplicate_products_report.txt"):
    """Zapisz wyniki do pliku"""
    
    if not duplicates:
        return
        
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("RAPORT DUPLIKATÓW PRODUCT_NAME\n")
            f.write("=" * 50 + "\n\n")
            
            for product_name, files in duplicates.items():
                f.write(f"Product: {product_name}\n")
                f.write(f"Liczba wystąpień: {len(files)}\n")
                f.write("Pliki:\n")
                
                for file_info in files:
                    f.write(f"  - {file_info['filename']} (ID: {file_info['id']})\n")
                f.write("\n")
            
            f.write(f"\nŁączna liczba duplikatów: {len(duplicates)}\n")
        
        print(f"\n💾 Raport zapisany do pliku: {output_file}")
        
    except Exception as e:
        print(f"❌ Błąd podczas zapisywania raportu: {str(e)}")

def main():
    # Domyślna ścieżka do folderu
    default_folder = "data/full — kopia"
    
    # Sprawdź argumenty linii poleceń
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = default_folder
    
    print(f"🚀 Analiza duplikatów product_name")
    print(f"📁 Folder: {folder_path}")
    print("-" * 50)
    
    # Znajdź duplikaty
    duplicates, all_products = find_duplicate_products(folder_path)
    
    # Wyświetl wyniki
    print_results(duplicates, all_products)
    
    # Zapisz do pliku jeśli są duplikaty
    if duplicates:
        save_results_to_file(duplicates)
    
    print(f"\n✨ Analiza zakończona!")

if __name__ == "__main__":
    main() 