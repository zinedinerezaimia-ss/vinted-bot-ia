from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Base de données des produits avec prix réalistes
PRODUCTS = {
    # MAILLOTS
    "maillot_bayern": {"marque": "FC Bayern Munich / Adidas", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 25, "prix_max": 55, "prix": 35},
    "maillot_psg": {"marque": "Paris Saint-Germain / Nike", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 30, "prix_max": 60, "prix": 40},
    "maillot_real": {"marque": "Real Madrid / Adidas", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 30, "prix_max": 60, "prix": 40},
    "maillot_barca": {"marque": "FC Barcelona / Nike", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 30, "prix_max": 60, "prix": 40},
    "maillot_om": {"marque": "Olympique de Marseille / Puma", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 25, "prix_max": 50, "prix": 35},
    "maillot_ol": {"marque": "Olympique Lyonnais / Adidas", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 25, "prix_max": 50, "prix": 35},
    "maillot_juve": {"marque": "Juventus / Adidas", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 28, "prix_max": 55, "prix": 38},
    "maillot_manu": {"marque": "Manchester United / Adidas", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 30, "prix_max": 60, "prix": 40},
    "maillot_liverpool": {"marque": "Liverpool FC / Nike", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 30, "prix_max": 60, "prix": 40},
    "maillot_chelsea": {"marque": "Chelsea FC / Nike", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 30, "prix_max": 60, "prix": 40},
    "maillot_city": {"marque": "Manchester City / Puma", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 30, "prix_max": 60, "prix": 40},
    "maillot_dortmund": {"marque": "Borussia Dortmund / Puma", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 28, "prix_max": 55, "prix": 38},
    "maillot_inter": {"marque": "Inter Milan / Nike", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 28, "prix_max": 55, "prix": 38},
    "maillot_acmilan": {"marque": "AC Milan / Puma", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 28, "prix_max": 55, "prix": 38},
    "maillot_arsenal": {"marque": "Arsenal FC / Adidas", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 30, "prix_max": 60, "prix": 40},
    "maillot_france": {"marque": "Equipe de France / Nike", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 35, "prix_max": 70, "prix": 50},
    "maillot_autre": {"marque": "", "type": "Maillot de football", "cat": "Vetements de sport", "prix_min": 15, "prix_max": 40, "prix": 25},
    
    # SACS
    "sac_luxe": {"marque": "", "type": "Sac a main luxe", "cat": "Sacs", "prix_min": 80, "prix_max": 300, "prix": 150},
    "sac_cuir": {"marque": "", "type": "Sac en cuir", "cat": "Sacs", "prix_min": 35, "prix_max": 100, "prix": 60},
    "sac_main": {"marque": "", "type": "Sac a main", "cat": "Sacs", "prix_min": 18, "prix_max": 50, "prix": 30},
    "sac_bandouliere": {"marque": "", "type": "Sac bandouliere", "cat": "Sacs", "prix_min": 15, "prix_max": 45, "prix": 25},
    "sac_dos": {"marque": "", "type": "Sac a dos", "cat": "Sacs", "prix_min": 15, "prix_max": 50, "prix": 28},
    "pochette": {"marque": "", "type": "Pochette", "cat": "Sacs", "prix_min": 10, "prix_max": 35, "prix": 18},
    
    # HAUTS
    "tshirt": {"marque": "", "type": "T-shirt", "cat": "Hauts", "prix_min": 8, "prix_max": 25, "prix": 15},
    "polo": {"marque": "", "type": "Polo", "cat": "Hauts", "prix_min": 12, "prix_max": 35, "prix": 20},
    "chemise": {"marque": "", "type": "Chemise", "cat": "Hauts", "prix_min": 15, "prix_max": 40, "prix": 25},
    "pull": {"marque": "", "type": "Pull", "cat": "Hauts", "prix_min": 15, "prix_max": 45, "prix": 28},
    "sweat": {"marque": "", "type": "Sweat", "cat": "Hauts", "prix_min": 18, "prix_max": 50, "prix": 30},
    "hoodie": {"marque": "", "type": "Hoodie", "cat": "Hauts", "prix_min": 20, "prix_max": 55, "prix": 35},
    "debardeur": {"marque": "", "type": "Debardeur", "cat": "Hauts", "prix_min": 6, "prix_max": 18, "prix": 10},
    "crop_top": {"marque": "", "type": "Crop top", "cat": "Hauts", "prix_min": 8, "prix_max": 22, "prix": 14},
    
    # VESTES
    "veste_cuir": {"marque": "", "type": "Veste en cuir", "cat": "Vestes et manteaux", "prix_min": 45, "prix_max": 150, "prix": 80},
    "veste_jean": {"marque": "", "type": "Veste en jean", "cat": "Vestes et manteaux", "prix_min": 20, "prix_max": 55, "prix": 35},
    "blazer": {"marque": "", "type": "Blazer", "cat": "Vestes et manteaux", "prix_min": 25, "prix_max": 70, "prix": 40},
    "bomber": {"marque": "", "type": "Bomber", "cat": "Vestes et manteaux", "prix_min": 25, "prix_max": 65, "prix": 40},
    "doudoune": {"marque": "", "type": "Doudoune", "cat": "Vestes et manteaux", "prix_min": 30, "prix_max": 90, "prix": 50},
    "manteau": {"marque": "", "type": "Manteau", "cat": "Vestes et manteaux", "prix_min": 35, "prix_max": 100, "prix": 60},
    "parka": {"marque": "", "type": "Parka", "cat": "Vestes et manteaux", "prix_min": 35, "prix_max": 90, "prix": 55},
    "trench": {"marque": "", "type": "Trench", "cat": "Vestes et manteaux", "prix_min": 30, "prix_max": 80, "prix": 50},
    
    # PANTALONS
    "jean_slim": {"marque": "", "type": "Jean slim", "cat": "Pantalons", "prix_min": 15, "prix_max": 45, "prix": 25},
    "jean_droit": {"marque": "", "type": "Jean droit", "cat": "Pantalons", "prix_min": 15, "prix_max": 45, "prix": 25},
    "jean_mom": {"marque": "", "type": "Jean mom", "cat": "Pantalons", "prix_min": 18, "prix_max": 50, "prix": 30},
    "jean_flare": {"marque": "", "type": "Jean flare", "cat": "Pantalons", "prix_min": 18, "prix_max": 50, "prix": 30},
    "pantalon": {"marque": "", "type": "Pantalon", "cat": "Pantalons", "prix_min": 12, "prix_max": 40, "prix": 22},
    "jogging": {"marque": "", "type": "Jogging", "cat": "Pantalons", "prix_min": 12, "prix_max": 40, "prix": 22},
    "short": {"marque": "", "type": "Short", "cat": "Pantalons", "prix_min": 10, "prix_max": 30, "prix": 18},
    "bermuda": {"marque": "", "type": "Bermuda", "cat": "Pantalons", "prix_min": 12, "prix_max": 32, "prix": 20},
    
    # CHAUSSURES
    "sneakers": {"marque": "", "type": "Sneakers", "cat": "Chaussures", "prix_min": 25, "prix_max": 90, "prix": 45},
    "baskets": {"marque": "", "type": "Baskets", "cat": "Chaussures", "prix_min": 18, "prix_max": 50, "prix": 30},
    "bottes": {"marque": "", "type": "Bottes", "cat": "Chaussures", "prix_min": 25, "prix_max": 80, "prix": 45},
    "bottines": {"marque": "", "type": "Bottines", "cat": "Chaussures", "prix_min": 22, "prix_max": 70, "prix": 40},
    "escarpins": {"marque": "", "type": "Escarpins", "cat": "Chaussures", "prix_min": 20, "prix_max": 60, "prix": 35},
    "sandales": {"marque": "", "type": "Sandales", "cat": "Chaussures", "prix_min": 12, "prix_max": 40, "prix": 22},
    "mocassins": {"marque": "", "type": "Mocassins", "cat": "Chaussures", "prix_min": 18, "prix_max": 55, "prix": 32},
    "derbies": {"marque": "", "type": "Derbies", "cat": "Chaussures", "prix_min": 22, "prix_max": 65, "prix": 38},
    
    # ROBES & JUPES
    "robe_soiree": {"marque": "", "type": "Robe de soiree", "cat": "Robes", "prix_min": 25, "prix_max": 80, "prix": 45},
    "robe_ete": {"marque": "", "type": "Robe d'ete", "cat": "Robes", "prix_min": 15, "prix_max": 45, "prix": 25},
    "robe_pull": {"marque": "", "type": "Robe pull", "cat": "Robes", "prix_min": 18, "prix_max": 50, "prix": 30},
    "combinaison": {"marque": "", "type": "Combinaison", "cat": "Robes", "prix_min": 20, "prix_max": 55, "prix": 35},
    "jupe": {"marque": "", "type": "Jupe", "cat": "Jupes", "prix_min": 12, "prix_max": 38, "prix": 22},
    "jupe_longue": {"marque": "", "type": "Jupe longue", "cat": "Jupes", "prix_min": 15, "prix_max": 45, "prix": 28},
    
    # ACCESSOIRES
    "casquette": {"marque": "", "type": "Casquette", "cat": "Accessoires", "prix_min": 10, "prix_max": 35, "prix": 18},
    "bonnet": {"marque": "", "type": "Bonnet", "cat": "Accessoires", "prix_min": 8, "prix_max": 28, "prix": 15},
    "echarpe": {"marque": "", "type": "Echarpe", "cat": "Accessoires", "prix_min": 10, "prix_max": 40, "prix": 22},
    "ceinture": {"marque": "", "type": "Ceinture", "cat": "Accessoires", "prix_min": 10, "prix_max": 45, "prix": 22},
    "lunettes": {"marque": "", "type": "Lunettes de soleil", "cat": "Accessoires", "prix_min": 12, "prix_max": 50, "prix": 25},
    "montre": {"marque": "", "type": "Montre", "cat": "Accessoires", "prix_min": 20, "prix_max": 100, "prix": 45},
    "bijoux": {"marque": "", "type": "Bijoux", "cat": "Accessoires", "prix_min": 8, "prix_max": 40, "prix": 18},
    "foulard": {"marque": "", "type": "Foulard", "cat": "Accessoires", "prix_min": 8, "prix_max": 35, "prix": 18},
}

JOUEURS = ["Sans flocage", "Lewandowski #9", "Mbappe #7", "Messi #10", "Ronaldo #7", "Neymar #10", "Haaland #9", "Bellingham #5", "Vinicius Jr #7", "Griezmann #7", "Dembele #10", "Salah #11", "Benzema #9", "Autre"]
SAISONS = ["2024/2025", "2023/2024", "2022/2023", "2021/2022", "Retro/Vintage"]
COULEURS = ["Noir", "Blanc", "Bleu", "Rouge", "Vert", "Jaune", "Rose", "Gris", "Marron", "Beige", "Orange", "Violet", "Bleu marine", "Bordeaux", "Kaki", "Multicolore", "Dore", "Argent"]
TAILLES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL"]
POINTURES = ["35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47"]
ETATS = ["Neuf avec etiquette", "Neuf sans etiquette", "Tres bon etat", "Bon etat", "Satisfaisant"]


def generate_annonce(product_key, options):
    """Genere titre et description optimises"""
    
    if product_key not in PRODUCTS:
        return None
    
    p = PRODUCTS[product_key]
    
    marque = options.get('marque', p['marque']) or ""
    couleur = options.get('couleur', 'Noir')
    taille = options.get('taille', 'M')
    etat = options.get('etat', 'Tres bon etat')
    saison = options.get('saison', '')
    joueur = options.get('joueur', '')
    
    # Génération du titre
    if 'maillot' in product_key:
        if marque:
            titre = f"Maillot {marque.split('/')[0].strip()}"
        else:
            titre = "Maillot de football"
        if saison:
            titre += f" {saison}"
        if joueur and joueur != "Sans flocage":
            titre += f" {joueur}"
    elif marque:
        titre = f"{p['type']} {marque} {couleur}"
    else:
        titre = f"{p['type']} {couleur} - {etat}"
    
    titre = titre[:80]
    
    # Génération de la description
    if 'maillot' in product_key:
        if marque:
            desc = f"Maillot officiel {marque.split('/')[0].strip()}."
            if saison:
                desc += f" Saison {saison}."
            if joueur and joueur != "Sans flocage":
                desc += f" Flocage {joueur}."
            desc += f" {etat}. Authentique, parfait pour les fans et collectionneurs!"
        else:
            desc = f"Maillot de football en {etat.lower()}. N'hesitez pas a me contacter pour plus d'infos!"
    elif 'sac' in product_key or 'pochette' in product_key:
        desc = f"{p['type']} {couleur.lower()}. {etat}. "
        if 'luxe' in product_key or 'cuir' in product_key:
            desc += "Materiau de qualite, finitions soignees. Parfait pour toutes occasions!"
        else:
            desc += "Pratique et elegant. Envoi rapide et soigne!"
    elif 'chaussure' in product_key or 'sneakers' in product_key or 'bottes' in product_key or 'escarpins' in product_key or 'sandales' in product_key or 'baskets' in product_key or 'bottines' in product_key or 'mocassins' in product_key or 'derbies' in product_key:
        if marque:
            desc = f"{p['type']} {marque}. Pointure {taille}. {etat}. Confortables et stylees!"
        else:
            desc = f"{p['type']} {couleur.lower()}. Pointure {taille}. {etat}. Envoi rapide!"
    else:
        if marque:
            desc = f"{p['type']} {marque}. Taille {taille}, couleur {couleur.lower()}. {etat}. N'hesitez pas pour plus d'infos!"
        else:
            desc = f"{p['type']} {couleur.lower()}. Taille {taille}. {etat}. Envoi rapide et soigne!"
    
    return {
        "titre": titre,
        "description": desc,
        "marque": marque or "Sans marque",
        "type": p['type'],
        "categorie": p['cat'],
        "etat": etat,
        "taille": taille,
        "couleur": couleur,
        "prix_min": p['prix_min'],
        "prix_max": p['prix_max'],
        "prix": p['prix']
    }


@app.route('/')
def index():
    return render_template('index.html',
                          products=PRODUCTS,
                          joueurs=JOUEURS,
                          saisons=SAISONS,
                          couleurs=COULEURS,
                          tailles=TAILLES,
                          pointures=POINTURES,
                          etats=ETATS)


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        product_key = data.get('product')
        options = data.get('options', {})
        
        result = generate_annonce(product_key, options)
        if not result:
            return jsonify({"error": "Produit non trouve"}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
