from flask import Flask, render_template, request, jsonify
import base64
import os
import json
import re
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDn-oQvj7F411s3H5jzuOX8367e6w0SESE')

def analyze_images_with_gemini(images_base64):
    """Analyse les images avec Google Gemini Vision"""
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Construire les parties avec les images
    parts = [
        {
            "text": """Tu es un EXPERT en mode, vêtements, chaussures et accessoires. Tu travailles pour une application qui aide les vendeurs Vinted.

ANALYSE CES IMAGES AVEC UNE EXTRÊME PRÉCISION.

🔍 IDENTIFICATION OBLIGATOIRE :
1. **MARQUE** : Identifie la marque EXACTE. Regarde :
   - Les logos (même petits ou partiels)
   - Les étiquettes visibles
   - Le style caractéristique de certaines marques
   - Les motifs signatures (ex: virgule Nike, 3 bandes Adidas, crocodile Lacoste)
   - Pour les maillots de foot : identifie le CLUB et l'ÉQUIPEMENTIER
   
2. **TYPE DE PRODUIT** : Sois PRÉCIS
   - Pas juste "vêtement" mais "Maillot de football", "Jean slim", "Sneakers montantes", etc.
   - Pour les maillots : précise si c'est domicile/extérieur/third, la saison si visible
   
3. **DÉTAILS SPÉCIFIQUES** :
   - Nom du joueur flocké (dos du maillot)
   - Numéro du joueur
   - Saison/année si identifiable
   - Collection spéciale
   - Édition limitée
   
4. **COULEUR(S)** : Les couleurs PRINCIPALES visibles

5. **ÉTAT** : Analyse visuelle
   - Neuf avec étiquette
   - Neuf sans étiquette  
   - Très bon état
   - Bon état
   - Satisfaisant

6. **TAILLE** : Si visible sur étiquette ou déductible

7. **MATIÈRE** : Si identifiable (coton, polyester, cuir, etc.)

📝 GÉNÈRE UN TITRE VENDEUR (max 80 caractères) :
Format optimal : [Marque] [Type] [Détail unique] [Taille si connue]
Exemples :
- "Maillot Bayern Munich Lewandowski #9 Domicile 2021-2022 Taille M"
- "Nike Air Force 1 Low Blanches Taille 42"
- "Jean Levi's 501 Original Bleu Délavé W32 L32"

📝 GÉNÈRE UNE DESCRIPTION VENDEUSE (150-200 caractères) :
- Mentionne les points forts
- Précise l'état
- Ajoute des mots-clés recherchés
- Ton professionnel mais chaleureux

💰 ESTIMATION DE PRIX :
Estime une fourchette de prix réaliste pour Vinted France basée sur :
- La marque et sa cote
- L'état du produit
- La rareté/demande
- Le type d'article

RÉPONDS UNIQUEMENT EN JSON VALIDE (sans markdown, sans ```json```, juste le JSON) :
{
    "marque": "Marque exacte ou 'Non identifiée'",
    "type_produit": "Type précis du produit",
    "details": "Tous les détails spécifiques (joueur, numéro, collection, etc.)",
    "couleurs": ["couleur1", "couleur2"],
    "etat": "État estimé",
    "taille": "Taille si visible ou 'Non visible'",
    "matiere": "Matière si identifiable ou 'Non identifiable'",
    "titre": "Titre optimisé pour Vinted",
    "description": "Description vendeuse optimisée",
    "prix_min": 10,
    "prix_max": 20,
    "prix_suggere": 15,
    "categorie_vinted": "Catégorie Vinted appropriée",
    "mots_cles": ["mot1", "mot2", "mot3"],
    "confiance": 85
}"""
        }
    ]
    
    # Ajouter chaque image
    for img_base64 in images_base64:
        # Nettoyer le base64 si nécessaire
        if ',' in img_base64:
            img_base64 = img_base64.split(',')[1]
        
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": img_base64
            }
        })
    
    payload = {
        "contents": [
            {
                "parts": parts
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "topK": 32,
            "topP": 1,
            "maxOutputTokens": 2048
        }
    }
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            error_detail = response.json() if response.text else "Pas de détails"
            return {"error": f"Erreur API Gemini: {response.status_code} - {error_detail}"}
        
        result = response.json()
        
        # Extraire le texte de la réponse Gemini
        if 'candidates' not in result or len(result['candidates']) == 0:
            return {"error": "Pas de réponse de Gemini"}
        
        content_text = result['candidates'][0]['content']['parts'][0]['text']
        
        # Nettoyer le JSON (enlever les backticks markdown si présents)
        content_text = content_text.strip()
        if content_text.startswith('```json'):
            content_text = content_text[7:]
        if content_text.startswith('```'):
            content_text = content_text[3:]
        if content_text.endswith('```'):
            content_text = content_text[:-3]
        content_text = content_text.strip()
        
        # Extraire le JSON de la réponse
        json_match = re.search(r'\{[\s\S]*\}', content_text)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Impossible de parser la réponse JSON"}
            
    except requests.exceptions.Timeout:
        return {"error": "Timeout - L'analyse a pris trop de temps"}
    except json.JSONDecodeError as e:
        return {"error": f"Erreur de parsing JSON: {str(e)}"}
    except Exception as e:
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
            return jsonify({"error": "Aucune image reçue"}), 400
        
        if len(images) > 5:
            return jsonify({"error": "Maximum 5 images autorisées"}), 400
        
        # Analyse avec Gemini Vision
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
