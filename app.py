from flask import Flask, render_template, request, jsonify
import base64
import os
import json
import re
import requests

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

def analyze_images_with_gpt4(images_base64):
    """Analyse les images avec GPT-4 Vision - prompt ultra détaillé"""
    
    if not OPENAI_API_KEY:
        return {"error": "Clé API OpenAI non configurée"}
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Construire le contenu avec toutes les images
    content = [
        {
            "type": "text",
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

RÉPONDS UNIQUEMENT EN JSON VALIDE :
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
        
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img_base64}",
                "detail": "high"
            }
        })
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "max_tokens": 1500,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            return {"error": f"Erreur API OpenAI: {response.status_code}"}
        
        result = response.json()
        content_text = result['choices'][0]['message']['content']
        
        # Extraire le JSON de la réponse
        json_match = re.search(r'\{[\s\S]*\}', content_text)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Impossible de parser la réponse"}
            
    except requests.exceptions.Timeout:
        return {"error": "Timeout - L'analyse a pris trop de temps"}
    except json.JSONDecodeError:
        return {"error": "Erreur de parsing JSON"}
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

def search_vinted_prices(query):
    """Recherche les prix sur Vinted pour comparaison"""
    # Note: Vinted n'a pas d'API publique officielle
    # Cette fonction simule une recherche de prix basée sur des données moyennes
    # Dans une version production, tu pourrais utiliser du web scraping
    
    # Prix moyens par catégorie (données approximatives)
    price_data = {
        "maillot": {"min": 15, "max": 45, "avg": 25},
        "maillot authentique": {"min": 30, "max": 80, "avg": 50},
        "sneakers": {"min": 25, "max": 100, "avg": 50},
        "jean": {"min": 10, "max": 40, "avg": 20},
        "veste": {"min": 20, "max": 60, "avg": 35},
        "t-shirt": {"min": 5, "max": 20, "avg": 10},
        "sweat": {"min": 15, "max": 45, "avg": 25},
        "robe": {"min": 10, "max": 50, "avg": 25},
        "chaussures": {"min": 15, "max": 60, "avg": 30},
        "sac": {"min": 15, "max": 80, "avg": 35},
        "accessoire": {"min": 5, "max": 30, "avg": 15},
        "default": {"min": 10, "max": 40, "avg": 20}
    }
    
    query_lower = query.lower()
    
    for key, prices in price_data.items():
        if key in query_lower:
            return prices
    
    return price_data["default"]

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
        
        # Analyse avec GPT-4 Vision
        result = analyze_images_with_gpt4(images)
        
        if "error" in result:
            return jsonify(result), 500
        
        # Enrichir avec recherche de prix
        if result.get("type_produit"):
            market_prices = search_vinted_prices(result["type_produit"])
            result["market_data"] = market_prices
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
