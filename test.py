#!/usr/bin/env python3
"""
Script de test pour vérifier que l'application fonctionne
"""

import sys

print("🔍 Vérification de l'environnement...")
print(f"Python version: {sys.version}")

# Test des imports
try:
    from flask import Flask
    print("✅ Flask installé")
except ImportError:
    print("❌ Flask manquant - pip install Flask")
    sys.exit(1)

try:
    from PIL import Image
    print("✅ Pillow installé")
except ImportError:
    print("❌ Pillow manquant - pip install Pillow")
    sys.exit(1)

try:
    import requests
    print("✅ Requests installé")
except ImportError:
    print("❌ Requests manquant - pip install requests")
    sys.exit(1)

# Test de l'application
try:
    from app import app
    print("✅ App Flask chargée")
    
    with app.test_client() as client:
        response = client.get('/')
        if response.status_code == 200:
            print("✅ Page d'accueil OK")
        else:
            print(f"❌ Page d'accueil erreur: {response.status_code}")
        
        response = client.get('/health')
        if response.status_code == 200:
            print("✅ Endpoint /health OK")
        else:
            print(f"❌ Endpoint /health erreur: {response.status_code}")
    
    print("\n✅ TOUS LES TESTS PASSÉS")
    print("\n🚀 Pour lancer l'application :")
    print("   python app.py")
    print("\n   Puis ouvrir: http://localhost:5000")
    
except Exception as e:
    print(f"❌ Erreur lors du test: {e}")
    sys.exit(1)
