from flask import Flask, render_template, request, jsonify
import os
import json
import re
import requests
import random

app = Flask(__name__)


def get_api_keys():
    """Recupere les cles API depuis les variables d'environnement"""
    keys = []
    for i in range(1, 10):
        key = os.environ.get(f'GEMINI_API_KEY_{i}')
        if key:
            keys.append(key)
    return keys


def analyze_images_with_gemini(images_base64, key_index=0):
    """Analyse les images avec Gemini Vision API"""
    
    api_keys = get_api_keys()
    
    if not api_keys:
        return {"error": "Aucune cle API configuree. Ajoutez GEMINI_API_KEY_1 dans Render."}
    
    if key_index >= len(api_keys):
        return {"error": "Service temporairement indisponible. Reessaye dans 1 minute."}
    
    parts = [
        {
            "text": """Tu es un EXPERT en mode et vetements pour Vinted. Analyse ces images avec PRECISION.

IDENTIFIE :
1. MARQUE : Regarde les logos, etiquettes, motifs (Nike, Adidas, Bayern Munich, etc.)
2. TYPE : Maillot de foot, Jean, Sneakers, T-shirt, Veste...
3. DETAILS : Joueur, numero, saison, collection
4. COULEURS : Couleurs principales
5. ETAT : Neuf avec etiquette / Neuf sans etiquette / Tres bon etat / Bon etat / Satisfaisant
6. TAILLE : Si visible

Pour les MAILLOTS DE FOOT : identifie le CLUB (Bayern, PSG, Real...) et le JOUEUR si visible.

REPONDS EN JSON UNIQUEMENT :
{
    "marque": "Marque ou Club identifie",
    "type_produit": "Type precis",
    "details": "Details (joueur, numero, saison...)",
    "couleurs": ["couleur1", "couleur2"],
    "etat": "Bon etat",
    "taille": "Taille ou Non visible",
    "titre": "Titre accrocheur max 80 caracteres",
    "description": "Description vendeuse 100-150 caracteres",
    "prix_min": 15,
    "prix_max": 35,
    "prix_suggere": 25,
    "categorie_vinted": "Categorie",
    "mots_cles": ["mot1", "mot2", "mot3"],
    "confiance": 80
}"""
        }
    ]
    
    for img_base64 in images_base64:
        if ',' in img_base64:
            img_base64 = img_base64.split(',')[1]
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": img_base64
            }
        })
    
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.2,
            "topK": 32,
            "topP": 1,
            "maxOutputTokens": 1024
        }
    }
    
    api_key = api_keys[key_index]
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        # Si erreur, essayer la cle suivante
        if response.status_code in [400, 403, 429, 500, 503]:
            return analyze_images_with_gemini(images_base64, key_index + 1)
        
        if response.status_code != 200:
            return analyze_images_with_gemini(images_base64, key_index + 1)
        
        result = response.json()
        
        if 'candidates' not in result or len(result['candidates']) == 0:
            return analyze_images_with_gemini(images_base64, key_index + 1)
        
        content_text = result['candidates'][0]['content']['parts'][0]['text']
        content_text = content_text.strip()
        
        # Nettoyer le JSON
        if content_text.startswith('```json'):
            content_text = content_text[7:]
        if content_text.startswith('```'):
            content_text = content_text[3:]
        if content_text.endswith('```'):
            content_text = content_text[:-3]
        content_text = content_text.strip()
        
        json_match = re.search(r'\{[\s\S]*\}', content_text)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Erreur d'analyse. Reessaye."}
            
    except requests.exceptions.Timeout:
        return analyze_images_with_gemini(images_base64, key_index + 1)
    except Exception as e:
        if key_index < len(api_keys) - 1:
            return analyze_images_with_gemini(images_base64, key_index + 1)
        return {"error": f"Erreur: {str(e)}"}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        images = data.get('images', [])
        
        if not images:
            return jsonify({"error": "Aucune image recue"}), 400
        
        if len(images) > 5:
            return jsonify({"error": "Maximum 5 images"}), 400
        
        result = analyze_images_with_gemini(images)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500


@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
