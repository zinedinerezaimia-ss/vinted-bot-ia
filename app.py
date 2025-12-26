from flask import Flask, render_template, request, jsonify
import base64
import os
import json
import re
import requests
import random

app = Flask(__name__)

GEMINI_API_KEYS = [
    'AIzaSyDn-oQvj7F411s3H5jzuOX8367e6w0SESE',
    'AIzaSyCn-del02fs_kGf10rEkX9FCC3jat3f5ss',
    'AIzaSyBpzc77QhdU345ydW74LBkGQ9U7ftiFIqY',
    'AIzaSyBM0G1mIE_WgUL_3nGK86ZRBOInJTmnRPQ',
    'AIzaSyAbCxhcS4WRkR3hPjh52rsLpFDk83Ow_M0'
]

def get_random_api_key():
    return random.choice(GEMINI_API_KEYS)

def analyze_images_with_gemini(images_base64, retry_count=0):
    if retry_count >= len(GEMINI_API_KEYS):
        return {"error": "Toutes les cles API sont saturees. Reessaye dans quelques minutes."}
    
    headers = {
        "Content-Type": "application/json"
    }
    
    parts = [
        {
            "text": """Tu es un EXPERT en mode, vetements, chaussures et accessoires. Tu travailles pour une application qui aide les vendeurs Vinted.

ANALYSE CES IMAGES AVEC UNE EXTREME PRECISION.

IDENTIFICATION OBLIGATOIRE :
1. MARQUE : Identifie la marque EXACTE (logos, etiquettes, motifs signatures)
   - Pour les maillots de foot : identifie le CLUB et l'EQUIPEMENTIER
   
2. TYPE DE PRODUIT : Sois PRECIS (Maillot de football, Jean slim, Sneakers, etc.)
   - Pour les maillots : precise domicile/exterieur/third, la saison si visible
   
3. DETAILS SPECIFIQUES : Nom du joueur, numero, saison, collection, edition limitee
   
4. COULEURS : Les couleurs PRINCIPALES

5. ETAT : Neuf avec etiquette / Neuf sans etiquette / Tres bon etat / Bon etat / Satisfaisant

6. TAILLE : Si visible

7. MATIERE : Si identifiable

GENERE UN TITRE VENDEUR (max 80 caracteres)
GENERE UNE DESCRIPTION VENDEUSE (150-200 caracteres)

REPONDS UNIQUEMENT EN JSON VALIDE :
{
    "marque": "Marque exacte",
    "type_produit": "Type precis",
    "details": "Details specifiques",
    "couleurs": ["couleur1", "couleur2"],
    "etat": "Etat estime",
    "taille": "Taille ou Non visible",
    "matiere": "Matiere ou Non identifiable",
    "titre": "Titre optimise pour Vinted",
    "description": "Description vendeuse optimisee",
    "prix_min": 10,
    "prix_max": 20,
    "prix_suggere": 15,
    "categorie_vinted": "Categorie Vinted",
    "mots_cles": ["mot1", "mot2", "mot3"],
    "confiance": 85
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
            "temperature": 0.3,
            "topK": 32,
            "topP": 1,
            "maxOutputTokens": 2048
        }
    }
    
    api_key = GEMINI_API_KEYS[retry_count] if retry_count > 0 else get_random_api_key()
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 429:
            return analyze_images_with_gemini(images_base64, retry_count + 1)
        
        if response.status_code != 200:
            return {"error": f"Erreur API Gemini: {response.status_code}"}
        
        result = response.json()
        
        if 'candidates' not in result or len(result['candidates']) == 0:
            return {"error": "Pas de reponse de Gemini"}
        
        content_text = result['candidates'][0]['content']['parts'][0]['text']
        content_text = content_text.strip()
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
            return {"error": "Impossible de parser la reponse"}
            
    except Exception as e:
        if retry_count < len(GEMINI_API_KEYS) - 1:
            return analyze_images_with_gemini(images_base64, retry_count + 1)
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
