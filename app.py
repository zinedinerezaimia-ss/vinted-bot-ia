from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Base de données des produits avec prix réalistes Vinted
PRODUCTS_DB = {
    # MAILLOTS DE FOOT
    "maillot_bayern": {
        "marque": "FC Bayern Munich / Adidas",
        "type": "Maillot de football",
        "categorie": "Vetements de sport",
        "prix_min": 25, "prix_max": 55, "prix": 35,
        "titre": "Maillot Bayern Munich {saison} {joueur}",
        "description": "Maillot officiel FC Bayern Munich. {joueur_desc}Authentique, excellent etat. Parfait pour les fans du Bayern!"
    },
    "maillot_psg": {
        "marque": "Paris Saint-Germain / Nike",
        "type": "Maillot de football",
        "categorie": "Vetements de sport",
        "prix_min": 30, "prix_max": 60, "prix": 40,
        "titre": "Maillot PSG {saison} {joueur}",
        "description": "Maillot officiel Paris Saint-Germain. {joueur_desc}Authentique Nike, tres bon etat. Allez Paris!"
    },
    "maillot_real": {
        "marque": "Real Madrid / Adidas",
        "type": "Maillot de football",
        "categorie": "Vetements de sport",
        "prix_min": 30, "prix_max": 60, "prix": 40,
        "titre": "Maillot Real Madrid {saison} {joueur}",
        "description": "Maillot officiel Real Madrid. {joueur_desc}Authentique Adidas. Hala Madrid!"
    },
    "maillot_barca": {
        "marque": "FC Barcelona / Nike",
        "type": "Maillot de football",
        "categorie": "Vetements de sport",
        "prix_min": 30, "prix_max": 60, "prix": 40,
        "titre": "Maillot FC Barcelona {saison} {joueur}",
        "description": "Maillot officiel FC Barcelona. {joueur_desc}Authentique Nike, excellent etat. Visca Barca!"
    },
    "maillot_om": {
        "marque": "Olympique de Marseille / Puma",
        "type": "Maillot de football",
        "categorie": "Vetements de sport",
        "prix_min": 25, "prix_max": 50, "prix": 35,
        "titre": "Maillot OM Marseille {saison} {joueur}",
        "description": "Maillot officiel Olympique de Marseille. {joueur_desc}Authentique, tres bon etat. Allez l'OM!"
    },
    "maillot_autre": {
        "marque": "A preciser",
        "type": "Maillot de football",
        "categorie": "Vetements de sport",
        "prix_min": 15, "prix_max": 40, "prix": 25,
        "titre": "Maillot de football {saison}",
        "description": "Maillot de football en bon etat. N'hesitez pas a me contacter pour plus d'infos!"
    },
    
    # SACS
    "sac_luxe": {
        "marque": "A preciser (luxe)",
        "type": "Sac a main",
        "categorie": "Sacs et pochettes",
        "prix_min": 80, "prix_max": 300, "prix": 150,
        "titre": "Sac a main {marque} {couleur}",
        "description": "Magnifique sac a main de marque. Excellent etat, peu utilise. Accessoire elegant pour toutes occasions!"
    },
    "sac_moyen": {
        "marque": "A preciser",
        "type": "Sac a main",
        "categorie": "Sacs et pochettes",
        "prix_min": 20, "prix_max": 60, "prix": 35,
        "titre": "Sac a main {couleur} - Bon etat",
        "description": "Joli sac a main pratique et elegant. Bon etat general. Parfait pour le quotidien!"
    },
    "sac_bandouliere": {
        "marque": "A preciser",
        "type": "Sac bandouliere",
        "categorie": "Sacs et pochettes",
        "prix_min": 15, "prix_max": 45, "prix": 25,
        "titre": "Sac bandouliere {couleur}",
        "description": "Sac bandouliere pratique et leger. Tres bon etat. Ideal pour sortir les mains libres!"
    },
    
    # HAUTS
    "tshirt_marque": {
        "marque": "A preciser",
        "type": "T-shirt",
        "categorie": "Hauts et t-shirts",
        "prix_min": 10, "prix_max": 30, "prix": 18,
        "titre": "T-shirt {marque} {couleur} - {taille}",
        "description": "T-shirt de marque en tres bon etat. Peu porte, couleurs vives. Confortable et stylé!"
    },
    "tshirt_basic": {
        "marque": "Sans marque",
        "type": "T-shirt",
        "categorie": "Hauts et t-shirts",
        "prix_min": 5, "prix_max": 15, "prix": 8,
        "titre": "T-shirt {couleur} - {taille}",
        "description": "T-shirt basique en bon etat. Confortable, ideal pour le quotidien!"
    },
    "pull_sweat": {
        "marque": "A preciser",
        "type": "Pull / Sweat",
        "categorie": "Hauts et t-shirts",
        "prix_min": 15, "prix_max": 45, "prix": 25,
        "titre": "Pull {marque} {couleur} - {taille}",
        "description": "Pull/sweat confortable et chaud. Tres bon etat, parfait pour l'hiver!"
    },
    "hoodie": {
        "marque": "A preciser",
        "type": "Sweat a capuche",
        "categorie": "Hauts et t-shirts",
        "prix_min": 18, "prix_max": 50, "prix": 30,
        "titre": "Hoodie {marque} {couleur} - {taille}",
        "description": "Sweat a capuche tres confortable. Bon etat, capuche et poche kangourou. Style streetwear!"
    },
    
    # VESTES
    "veste_cuir": {
        "marque": "A preciser",
        "type": "Veste en cuir",
        "categorie": "Vestes et manteaux",
        "prix_min": 40, "prix_max": 120, "prix": 70,
        "titre": "Veste en cuir {couleur} - {taille}",
        "description": "Belle veste en cuir veritable. Style indemodable, tres bon etat. Un must-have!"
    },
    "veste_jean": {
        "marque": "A preciser",
        "type": "Veste en jean",
        "categorie": "Vestes et manteaux",
        "prix_min": 20, "prix_max": 50, "prix": 30,
        "titre": "Veste en jean {couleur} - {taille}",
        "description": "Veste en jean classique et intemporelle. Bon etat, parfaite pour la mi-saison!"
    },
    "manteau": {
        "marque": "A preciser",
        "type": "Manteau",
        "categorie": "Vestes et manteaux",
        "prix_min": 30, "prix_max": 80, "prix": 50,
        "titre": "Manteau {couleur} - {taille}",
        "description": "Manteau chaud et elegant. Tres bon etat, parfait pour l'hiver!"
    },
    "doudoune": {
        "marque": "A preciser",
        "type": "Doudoune",
        "categorie": "Vestes et manteaux",
        "prix_min": 25, "prix_max": 70, "prix": 40,
        "titre": "Doudoune {couleur} - {taille}",
        "description": "Doudoune chaude et legere. Tres bon etat, ideale pour l'hiver!"
    },
    
    # PANTALONS
    "jean": {
        "marque": "A preciser",
        "type": "Jean",
        "categorie": "Pantalons et shorts",
        "prix_min": 15, "prix_max": 40, "prix": 22,
        "titre": "Jean {coupe} {couleur} - {taille}",
        "description": "Jean en tres bon etat. Coupe {coupe}, confortable. Incontournable du dressing!"
    },
    "pantalon": {
        "marque": "A preciser",
        "type": "Pantalon",
        "categorie": "Pantalons et shorts",
        "prix_min": 12, "prix_max": 35, "prix": 20,
        "titre": "Pantalon {couleur} - {taille}",
        "description": "Pantalon en bon etat. Confortable et polyvalent!"
    },
    "short": {
        "marque": "A preciser",
        "type": "Short",
        "categorie": "Pantalons et shorts",
        "prix_min": 8, "prix_max": 25, "prix": 15,
        "titre": "Short {couleur} - {taille}",
        "description": "Short en bon etat. Parfait pour l'ete!"
    },
    
    # CHAUSSURES
    "sneakers_marque": {
        "marque": "A preciser (Nike, Adidas...)",
        "type": "Sneakers",
        "categorie": "Chaussures",
        "prix_min": 35, "prix_max": 100, "prix": 55,
        "titre": "Sneakers {marque} - Pointure {taille}",
        "description": "Sneakers de marque en bon etat. Confortables et stylees. Pointure {taille}."
    },
    "sneakers_basic": {
        "marque": "Sans marque",
        "type": "Sneakers",
        "categorie": "Chaussures",
        "prix_min": 15, "prix_max": 35, "prix": 22,
        "titre": "Baskets {couleur} - Pointure {taille}",
        "description": "Baskets en bon etat. Confortables pour le quotidien. Pointure {taille}."
    },
    "bottes": {
        "marque": "A preciser",
        "type": "Bottes",
        "categorie": "Chaussures",
        "prix_min": 25, "prix_max": 70, "prix": 40,
        "titre": "Bottes {couleur} - Pointure {taille}",
        "description": "Bottes en bon etat. Elegantes et confortables. Pointure {taille}."
    },
    "talons": {
        "marque": "A preciser",
        "type": "Chaussures a talons",
        "categorie": "Chaussures",
        "prix_min": 20, "prix_max": 60, "prix": 35,
        "titre": "Escarpins {couleur} - Pointure {taille}",
        "description": "Escarpins elegants en bon etat. Parfaits pour les soirees! Pointure {taille}."
    },
    
    # ROBES
    "robe_soiree": {
        "marque": "A preciser",
        "type": "Robe de soiree",
        "categorie": "Robes",
        "prix_min": 25, "prix_max": 70, "prix": 40,
        "titre": "Robe de soiree {couleur} - {taille}",
        "description": "Magnifique robe de soiree. Elegante, parfaite pour vos evenements!"
    },
    "robe_ete": {
        "marque": "A preciser",
        "type": "Robe d'ete",
        "categorie": "Robes",
        "prix_min": 12, "prix_max": 35, "prix": 20,
        "titre": "Robe d'ete {couleur} - {taille}",
        "description": "Jolie robe legere pour l'ete. Fraiche et feminine!"
    },
    
    # ACCESSOIRES
    "casquette": {
        "marque": "A preciser",
        "type": "Casquette",
        "categorie": "Accessoires",
        "prix_min": 10, "prix_max": 30, "prix": 18,
        "titre": "Casquette {marque} {couleur}",
        "description": "Casquette en bon etat. Style streetwear, parfaite pour l'ete!"
    },
    "bonnet": {
        "marque": "A preciser",
        "type": "Bonnet",
        "categorie": "Accessoires",
        "prix_min": 8, "prix_max": 25, "prix": 15,
        "titre": "Bonnet {couleur}",
        "description": "Bonnet chaud et confortable. Parfait pour l'hiver!"
    },
    "ceinture": {
        "marque": "A preciser",
        "type": "Ceinture",
        "categorie": "Accessoires",
        "prix_min": 10, "prix_max": 40, "prix": 20,
        "titre": "Ceinture {couleur}",
        "description": "Ceinture en bon etat. Accessoire indispensable!"
    },
    "echarpe": {
        "marque": "A preciser",
        "type": "Echarpe",
        "categorie": "Accessoires",
        "prix_min": 10, "prix_max": 35, "prix": 18,
        "titre": "Echarpe {couleur}",
        "description": "Echarpe douce et chaude. Parfaite pour l'hiver!"
    },
    "lunettes": {
        "marque": "A preciser",
        "type": "Lunettes de soleil",
        "categorie": "Accessoires",
        "prix_min": 12, "prix_max": 50, "prix": 25,
        "titre": "Lunettes de soleil {marque}",
        "description": "Lunettes de soleil en bon etat. Style et protection UV!"
    },
    "montre": {
        "marque": "A preciser",
        "type": "Montre",
        "categorie": "Accessoires",
        "prix_min": 20, "prix_max": 80, "prix": 40,
        "titre": "Montre {marque} {couleur}",
        "description": "Montre en bon etat de fonctionnement. Elegante et pratique!"
    }
}

JOUEURS = {
    "lewandowski": "Lewandowski #9",
    "mbappe": "Mbappe #7",
    "messi": "Messi #10",
    "ronaldo": "Ronaldo #7",
    "neymar": "Neymar #10",
    "haaland": "Haaland #9",
    "benzema": "Benzema #9",
    "vinicius": "Vinicius Jr #7",
    "bellingham": "Bellingham #5",
    "griezmann": "Griezmann #7",
    "dembele": "Dembele #10",
    "salah": "Salah #11",
    "autre": "",
    "sans": ""
}

COULEURS = ["Noir", "Blanc", "Bleu", "Rouge", "Vert", "Jaune", "Rose", "Gris", "Marron", "Beige", "Orange", "Violet", "Bleu marine", "Bordeaux", "Kaki", "Multicolore"]
TAILLES = ["XS", "S", "M", "L", "XL", "XXL", "34", "36", "38", "40", "42", "44", "46"]
POINTURES = ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46"]
COUPES_JEAN = ["Slim", "Skinny", "Regular", "Droit", "Mom", "Bootcut", "Flare"]
SAISONS = ["2024/2025", "2023/2024", "2022/2023", "2021/2022", "Vintage"]
ETATS = ["Neuf avec etiquette", "Neuf sans etiquette", "Tres bon etat", "Bon etat", "Satisfaisant"]


@app.route('/')
def index():
    return render_template('index.html', 
                          products=PRODUCTS_DB,
                          couleurs=COULEURS,
                          tailles=TAILLES,
                          pointures=POINTURES,
                          coupes=COUPES_JEAN,
                          saisons=SAISONS,
                          joueurs=JOUEURS,
                          etats=ETATS)


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        product_key = data.get('product')
        options = data.get('options', {})
        
        if product_key not in PRODUCTS_DB:
            return jsonify({"error": "Produit non trouve"}), 400
        
        product = PRODUCTS_DB[product_key].copy()
        
        # Remplacer les variables dans le titre et la description
        titre = product['titre']
        description = product['description']
        
        # Couleur
        couleur = options.get('couleur', 'Noir')
        titre = titre.replace('{couleur}', couleur)
        description = description.replace('{couleur}', couleur)
        
        # Taille
        taille = options.get('taille', 'M')
        titre = titre.replace('{taille}', taille)
        description = description.replace('{taille}', taille)
        
        # Marque personnalisee
        marque = options.get('marque', '')
        if marque:
            titre = titre.replace('{marque}', marque)
            description = description.replace('{marque}', marque)
            product['marque'] = marque
        else:
            titre = titre.replace('{marque} ', '').replace('{marque}', '')
            description = description.replace('{marque} ', '').replace('{marque}', '')
        
        # Saison (maillots)
        saison = options.get('saison', '')
        titre = titre.replace('{saison}', saison).replace('  ', ' ')
        
        # Joueur (maillots)
        joueur_key = options.get('joueur', '')
        joueur = JOUEURS.get(joueur_key, '')
        titre = titre.replace('{joueur}', joueur).replace('  ', ' ')
        if joueur:
            description = description.replace('{joueur_desc}', f'Flocage {joueur}. ')
        else:
            description = description.replace('{joueur_desc}', '')
        
        # Coupe jean
        coupe = options.get('coupe', 'Slim')
        titre = titre.replace('{coupe}', coupe)
        description = description.replace('{coupe}', coupe)
        
        # Etat
        etat = options.get('etat', 'Tres bon etat')
        
        # Nettoyer les espaces doubles
        titre = ' '.join(titre.split())
        description = ' '.join(description.split())
        
        return jsonify({
            "titre": titre[:80],
            "description": description,
            "marque": product['marque'],
            "type": product['type'],
            "categorie": product['categorie'],
            "etat": etat,
            "taille": taille,
            "couleur": couleur,
            "prix_min": product['prix_min'],
            "prix_max": product['prix_max'],
            "prix": product['prix']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
