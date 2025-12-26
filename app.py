from flask import Flask, render_template, request, jsonify
import os
import json
import requests
import base64
import re

app = Flask(__name__)

HF_TOKEN = os.environ.get('HF_TOKEN', '')

def analyze_with_llava(images_base64):
    """Analyse avec LLaVA - modele vision gratuit et puissant"""
    
    # Prendre la premiere image
    img_base64 = images_base64[0]
    if ',' in img_base64:
        img_base64 = img_base64.split(',')[1]
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    
    # Essayer plusieurs modeles dans l'ordre
    models = [
        "llava-hf/llava-1.5-7b-hf",
        "Salesforce/blip2-opt-2.7b",
        "Salesforce/blip-image-captioning-large"
    ]
    
    prompt = """Describe this clothing item in detail. Include:
- Brand name if visible (Nike, Adidas, Puma, etc.)
- Type of clothing (jersey, t-shirt, jacket, pants, shoes, etc.)
- For sports jerseys: team name, player name, number
- Colors
- Any text or logos visible
Be specific and detailed."""

    description = ""
    
    for model in models:
        try:
            if "blip" in model.lower():
                # BLIP models - send image directly
                url = f"https://api-inference.huggingface.co/models/{model}"
                image_bytes = base64.b64decode(img_base64)
                response = requests.post(url, headers=headers, data=image_bytes, timeout=30)
            else:
                # LLaVA and other models
                url = f"https://api-inference.huggingface.co/models/{model}"
                payload = {
                    "inputs": {
                        "image": img_base64,
                        "text": prompt
                    }
                }
                response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict):
                        description = result[0].get('generated_text', '') or result[0].get('text', '')
                    else:
                        description = str(result[0])
                elif isinstance(result, dict):
                    description = result.get('generated_text', '') or result.get('text', '')
                
                if description:
                    break
        except Exception as e:
            continue
    
    # Analyser la description pour extraire les infos
    return parse_description(description, img_base64)


def parse_description(description, img_base64):
    """Parse la description et genere les infos pour Vinted"""
    
    desc_lower = description.lower() if description else ""
    
    # Detection marque
    brands = {
        'nike': 'Nike', 'adidas': 'Adidas', 'puma': 'Puma', 'reebok': 'Reebok',
        'jordan': 'Jordan', 'new balance': 'New Balance', 'vans': 'Vans',
        'converse': 'Converse', 'fila': 'Fila', 'champion': 'Champion',
        'lacoste': 'Lacoste', 'ralph lauren': 'Ralph Lauren', 'tommy': 'Tommy Hilfiger',
        'levis': "Levi's", 'zara': 'Zara', 'h&m': 'H&M', 'uniqlo': 'Uniqlo',
        'gucci': 'Gucci', 'louis vuitton': 'Louis Vuitton', 'supreme': 'Supreme',
        'bayern': 'FC Bayern Munich', 'munich': 'FC Bayern Munich',
        'psg': 'Paris Saint-Germain', 'real madrid': 'Real Madrid',
        'barcelona': 'FC Barcelona', 'manchester': 'Manchester United',
        'liverpool': 'Liverpool FC', 'chelsea': 'Chelsea FC',
        'juventus': 'Juventus', 'inter': 'Inter Milan', 'milan': 'AC Milan'
    }
    
    marque = "Non identifiee"
    for key, val in brands.items():
        if key in desc_lower:
            marque = val
            break
    
    # Detection joueur (maillots)
    players = {
        'lewandowski': 'Lewandowski #9', 'mbappe': 'Mbappe #7', 'messi': 'Messi #10',
        'ronaldo': 'Ronaldo #7', 'neymar': 'Neymar #10', 'haaland': 'Haaland #9',
        'benzema': 'Benzema #9', 'salah': 'Salah #11', 'de bruyne': 'De Bruyne #17'
    }
    
    details = ""
    for key, val in players.items():
        if key in desc_lower:
            details = val
            break
    
    # Detection type
    type_produit = "Vetement"
    types = {
        'jersey': 'Maillot de football', 'soccer': 'Maillot de football',
        'football': 'Maillot de football', 'shirt': 'T-shirt', 't-shirt': 'T-shirt',
        'jacket': 'Veste', 'hoodie': 'Sweat a capuche', 'sweatshirt': 'Sweat',
        'pants': 'Pantalon', 'jeans': 'Jean', 'shorts': 'Short',
        'sneakers': 'Sneakers', 'shoes': 'Chaussures', 'boots': 'Bottes',
        'dress': 'Robe', 'skirt': 'Jupe', 'coat': 'Manteau'
    }
    
    for key, val in types.items():
        if key in desc_lower:
            type_produit = val
            break
    
    # Detection couleur
    couleurs = []
    colors = {
        'red': 'Rouge', 'blue': 'Bleu', 'black': 'Noir', 'white': 'Blanc',
        'green': 'Vert', 'yellow': 'Jaune', 'orange': 'Orange', 'pink': 'Rose',
        'purple': 'Violet', 'grey': 'Gris', 'gray': 'Gris', 'brown': 'Marron',
        'navy': 'Bleu marine', 'beige': 'Beige'
    }
    
    for key, val in colors.items():
        if key in desc_lower and val not in couleurs:
            couleurs.append(val)
    
    if not couleurs:
        couleurs = ["Non identifiee"]
    
    # Generer titre et description
    if 'Maillot' in type_produit and marque != "Non identifiee":
        titre = f"Maillot {marque}"
        if details:
            titre += f" {details}"
        titre = titre[:80]
        desc_vinted = f"Maillot officiel {marque}. {details}. Parfait pour les fans! Envoi rapide et soigne."
    elif marque != "Non identifiee":
        titre = f"{type_produit} {marque} {couleurs[0]}"[:80]
        desc_vinted = f"{type_produit} {marque} en {couleurs[0].lower()}. Tres bon etat. N'hesitez pas a me contacter!"
    else:
        titre = f"{type_produit} {couleurs[0]} - Bon etat"[:80]
        desc_vinted = f"{type_produit} en {couleurs[0].lower()}. Bon etat general. Envoi rapide!"
    
    # Prix selon le type et la marque
    if marque in ['Gucci', 'Louis Vuitton', 'Supreme']:
        prix_min, prix_max, prix = 80, 200, 120
    elif marque in ['Nike', 'Adidas', 'Jordan', 'FC Bayern Munich', 'Paris Saint-Germain', 'Real Madrid']:
        prix_min, prix_max, prix = 25, 60, 40
    elif marque != "Non identifiee":
        prix_min, prix_max, prix = 15, 40, 25
    else:
        prix_min, prix_max, prix = 10, 25, 15
    
    # Categorie
    if 'Maillot' in type_produit:
        categorie = "Sport - Football"
    elif 'Chaussures' in type_produit or 'Sneakers' in type_produit:
        categorie = "Chaussures"
    elif 'Pantalon' in type_produit or 'Jean' in type_produit:
        categorie = "Pantalons"
    else:
        categorie = "Hauts"
    
    # Confiance
    confiance = 85 if marque != "Non identifiee" else 65
    
    return {
        "marque": marque,
        "type_produit": type_produit,
        "details": details or "Aucun detail specifique",
        "couleurs": couleurs,
        "etat": "Bon etat",
        "taille": "Non visible",
        "titre": titre,
        "description": desc_vinted,
        "prix_min": prix_min,
        "prix_max": prix_max,
        "prix_suggere": prix,
        "categorie_vinted": categorie,
        "mots_cles": [type_produit.lower(), marque.lower() if marque != "Non identifiee" else "occasion", couleurs[0].lower()],
        "confiance": confiance,
        "raw_description": description
    }


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
        
        result = analyze_with_llava(images)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500


@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
