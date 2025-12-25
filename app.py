from flask import Flask, request, render_template_string, jsonify
import base64
from io import BytesIO
from PIL import Image
import json
import os
import requests

app = Flask(__name__)

# Traductions
TRANSLATIONS = {
    'fr': {
        'title': 'Bot Vinted IA',
        'subtitle': 'Analyse automatique de vos articles avec l\'intelligence artificielle',
        'language': 'Langue',
        'upload_zone': 'Glissez vos photos ici ou cliquez pour sélectionner',
        'upload_hint': 'Jusqu\'à 5 photos • JPG, PNG',
        'analyze_btn': '🚀 Analyser avec l\'IA',
        'analyzing': 'Analyse en cours...',
        'results_title': '✨ Résultats de l\'analyse',
        'edit_hint': 'Cliquez pour modifier',
        'copy_all': '📋 Tout copier',
        'product_type': 'Type de produit',
        'brand': 'Marque',
        'color': 'Couleur',
        'condition': 'État',
        'price': 'Prix suggéré',
        'title_field': 'Titre',
        'description': 'Description',
        'copied': '✓ Copié !',
        'error': 'Erreur',
        'select_photos': 'Sélectionnez au moins une photo',
        'reset': '🔄 Nouvelle analyse'
    },
    'en': {
        'title': 'Vinted AI Bot',
        'subtitle': 'Automatic analysis of your items with artificial intelligence',
        'language': 'Language',
        'upload_zone': 'Drop your photos here or click to select',
        'upload_hint': 'Up to 5 photos • JPG, PNG',
        'analyze_btn': '🚀 Analyze with AI',
        'analyzing': 'Analyzing...',
        'results_title': '✨ Analysis Results',
        'edit_hint': 'Click to edit',
        'copy_all': '📋 Copy all',
        'product_type': 'Product type',
        'brand': 'Brand',
        'color': 'Color',
        'condition': 'Condition',
        'price': 'Suggested price',
        'title_field': 'Title',
        'description': 'Description',
        'copied': '✓ Copied!',
        'error': 'Error',
        'select_photos': 'Select at least one photo',
        'reset': '🔄 New analysis'
    },
    'es': {
        'title': 'Bot Vinted IA',
        'subtitle': 'Análisis automático de tus artículos con inteligencia artificial',
        'language': 'Idioma',
        'upload_zone': 'Arrastra tus fotos aquí o haz clic para seleccionar',
        'upload_hint': 'Hasta 5 fotos • JPG, PNG',
        'analyze_btn': '🚀 Analizar con IA',
        'analyzing': 'Analizando...',
        'results_title': '✨ Resultados del análisis',
        'edit_hint': 'Haz clic para editar',
        'copy_all': '📋 Copiar todo',
        'product_type': 'Tipo de producto',
        'brand': 'Marca',
        'color': 'Color',
        'condition': 'Estado',
        'price': 'Precio sugerido',
        'title_field': 'Título',
        'description': 'Descripción',
        'copied': '✓ ¡Copiado!',
        'error': 'Error',
        'select_photos': 'Selecciona al menos una foto',
        'reset': '🔄 Nuevo análisis'
    },
    'de': {
        'title': 'Vinted KI-Bot',
        'subtitle': 'Automatische Analyse Ihrer Artikel mit künstlicher Intelligenz',
        'language': 'Sprache',
        'upload_zone': 'Ziehen Sie Ihre Fotos hierher oder klicken Sie zum Auswählen',
        'upload_hint': 'Bis zu 5 Fotos • JPG, PNG',
        'analyze_btn': '🚀 Mit KI analysieren',
        'analyzing': 'Analysieren...',
        'results_title': '✨ Analyseergebnisse',
        'edit_hint': 'Zum Bearbeiten klicken',
        'copy_all': '📋 Alles kopieren',
        'product_type': 'Produkttyp',
        'brand': 'Marke',
        'color': 'Farbe',
        'condition': 'Zustand',
        'price': 'Vorgeschlagener Preis',
        'title_field': 'Titel',
        'description': 'Beschreibung',
        'copied': '✓ Kopiert!',
        'error': 'Fehler',
        'select_photos': 'Wählen Sie mindestens ein Foto',
        'reset': '🔄 Neue Analyse'
    }
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{lang}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{t.title}}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Animated background particles */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(255,255,255,0.05) 0%, transparent 50%);
            animation: float 20s ease-in-out infinite;
            pointer-events: none;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            animation: slideDown 0.6s ease;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .logo {
            font-size: 4em;
            margin-bottom: 15px;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
            animation: bounce 2s ease infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        h1 {
            color: white;
            font-size: 2.5em;
            font-weight: 800;
            margin-bottom: 10px;
            text-shadow: 0 2px 20px rgba(0,0,0,0.2);
        }
        
        .subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 1.1em;
            font-weight: 500;
        }
        
        .language-selector {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 100;
        }
        
        .language-selector select {
            padding: 12px 20px;
            font-size: 1em;
            font-weight: 600;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 12px;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .language-selector select:hover {
            background: white;
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .glass-card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 
                0 8px 32px rgba(0,0,0,0.1),
                0 0 0 1px rgba(255,255,255,0.5) inset;
            animation: fadeIn 0.6s ease;
            margin-bottom: 30px;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .upload-zone {
            border: 3px dashed #cbd5e0;
            border-radius: 20px;
            padding: 60px 40px;
            text-align: center;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            transition: all 0.3s;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .upload-zone::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(102,126,234,0.1), transparent);
            transition: left 0.5s;
        }
        
        .upload-zone:hover::before {
            left: 100%;
        }
        
        .upload-zone:hover {
            border-color: #667eea;
            background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
            transform: scale(1.02);
        }
        
        .upload-zone.dragover {
            border-color: #667eea;
            background: linear-gradient(135deg, #e6f2ff 0%, #d4e9ff 100%);
            transform: scale(1.05);
        }
        
        .upload-icon {
            font-size: 4em;
            margin-bottom: 20px;
            animation: pulse 2s ease infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .upload-text {
            font-size: 1.3em;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 10px;
        }
        
        .upload-hint {
            color: #718096;
            font-size: 0.95em;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .preview-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .preview-item {
            position: relative;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s;
            animation: scaleIn 0.4s ease;
        }
        
        @keyframes scaleIn {
            from {
                opacity: 0;
                transform: scale(0.8);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        .preview-item:hover {
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .preview-item img {
            width: 100%;
            height: 180px;
            object-fit: cover;
        }
        
        .remove-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 30px;
            height: 30px;
            background: rgba(239,68,68,0.95);
            border: none;
            border-radius: 50%;
            color: white;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .remove-btn:hover {
            background: #dc2626;
            transform: rotate(90deg) scale(1.1);
        }
        
        .analyze-btn {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 1.2em;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 20px rgba(102,126,234,0.4);
            position: relative;
            overflow: hidden;
        }
        
        .analyze-btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .analyze-btn:hover::before {
            width: 300px;
            height: 300px;
        }
        
        .analyze-btn:hover:not(:disabled) {
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(102,126,234,0.6);
        }
        
        .analyze-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            text-align: center;
            padding: 60px;
            display: none;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            width: 60px;
            height: 60px;
            margin: 0 auto 30px;
            border: 4px solid rgba(102,126,234,0.2);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            font-size: 1.2em;
            font-weight: 600;
            color: #667eea;
        }
        
        .results {
            display: none;
        }
        
        .results.show {
            display: block;
            animation: fadeIn 0.6s ease;
        }
        
        .results-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .results-header h2 {
            font-size: 2em;
            color: #2d3748;
            margin-bottom: 15px;
        }
        
        .copy-all-btn {
            padding: 12px 30px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(16,185,129,0.3);
        }
        
        .copy-all-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16,185,129,0.4);
        }
        
        .result-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .result-item {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.3s;
            position: relative;
            border: 2px solid transparent;
        }
        
        .result-item:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border-color: #667eea;
            transform: translateY(-2px);
        }
        
        .result-label {
            font-size: 0.85em;
            font-weight: 700;
            color: #667eea;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .copy-icon {
            cursor: pointer;
            opacity: 0.6;
            transition: all 0.3s;
            font-size: 1.2em;
        }
        
        .copy-icon:hover {
            opacity: 1;
            transform: scale(1.2);
        }
        
        .result-value {
            font-size: 1.1em;
            color: #2d3748;
            font-weight: 500;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 10px;
            min-height: 50px;
            cursor: text;
            transition: all 0.3s;
        }
        
        .result-value:focus {
            outline: none;
            background: white;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.2);
        }
        
        .result-item.large {
            grid-column: 1 / -1;
        }
        
        .result-item.large .result-value {
            min-height: 120px;
        }
        
        .reset-btn {
            width: 100%;
            padding: 16px;
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
            border-radius: 12px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
        }
        
        .reset-btn:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102,126,234,0.3);
        }
        
        .error {
            background: linear-gradient(135deg, #fee 0%, #fdd 100%);
            color: #c53030;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            display: none;
            font-weight: 600;
            border-left: 4px solid #e53e3e;
            animation: shake 0.5s ease;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        .error.show {
            display: block;
        }
        
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            font-weight: 600;
            box-shadow: 0 4px 20px rgba(16,185,129,0.4);
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.4s;
            z-index: 1000;
        }
        
        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }
            .glass-card {
                padding: 25px;
            }
            .result-grid {
                grid-template-columns: 1fr;
            }
            .language-selector {
                position: static;
                text-align: center;
                margin-bottom: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="language-selector">
        <select id="language" onchange="changeLanguage()">
            <option value="fr" {{'selected' if lang == 'fr' else ''}}>🇫🇷 Français</option>
            <option value="en" {{'selected' if lang == 'en' else ''}}>🇬🇧 English</option>
            <option value="es" {{'selected' if lang == 'es' else ''}}>🇪🇸 Español</option>
            <option value="de" {{'selected' if lang == 'de' else ''}}>🇩🇪 Deutsch</option>
        </select>
    </div>

    <div class="container">
        <div class="header">
            <div class="logo">🤖</div>
            <h1>{{t.title}}</h1>
            <p class="subtitle">{{t.subtitle}}</p>
        </div>

        <div class="glass-card">
            <div class="upload-zone" id="uploadZone" onclick="document.getElementById('photos').click()">
                <div class="upload-icon">📸</div>
                <div class="upload-text">{{t.upload_zone}}</div>
                <div class="upload-hint">{{t.upload_hint}}</div>
                <input type="file" id="photos" accept="image/*" multiple onchange="previewImages()">
            </div>

            <div class="preview-container" id="preview"></div>

            <button class="analyze-btn" onclick="analyzePhotos()" id="analyzeBtn" disabled>
                <span style="position: relative; z-index: 1;">{{t.analyze_btn}}</span>
            </button>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div class="loading-text">{{t.analyzing}}</div>
            </div>

            <div class="error" id="error"></div>
        </div>

        <div class="glass-card results" id="results">
            <div class="results-header">
                <h2>{{t.results_title}}</h2>
                <button class="copy-all-btn" onclick="copyAll()">{{t.copy_all}}</button>
            </div>

            <div class="result-grid">
                <div class="result-item">
                    <div class="result-label">
                        {{t.product_type}}
                        <span class="copy-icon" onclick="copyField('type')" title="Copier">📋</span>
                    </div>
                    <div class="result-value" contenteditable="true" id="type"></div>
                </div>

                <div class="result-item">
                    <div class="result-label">
                        {{t.brand}}
                        <span class="copy-icon" onclick="copyField('brand')" title="Copier">📋</span>
                    </div>
                    <div class="result-value" contenteditable="true" id="brand"></div>
                </div>

                <div class="result-item">
                    <div class="result-label">
                        {{t.color}}
                        <span class="copy-icon" onclick="copyField('color')" title="Copier">📋</span>
                    </div>
                    <div class="result-value" contenteditable="true" id="color"></div>
                </div>

                <div class="result-item">
                    <div class="result-label">
                        {{t.condition}}
                        <span class="copy-icon" onclick="copyField('condition')" title="Copier">📋</span>
                    </div>
                    <div class="result-value" contenteditable="true" id="condition"></div>
                </div>

                <div class="result-item">
                    <div class="result-label">
                        {{t.price}}
                        <span class="copy-icon" onclick="copyField('price')" title="Copier">📋</span>
                    </div>
                    <div class="result-value" contenteditable="true" id="price"></div>
                </div>

                <div class="result-item large">
                    <div class="result-label">
                        {{t.title_field}}
                        <span class="copy-icon" onclick="copyField('listingTitle')" title="Copier">📋</span>
                    </div>
                    <div class="result-value" contenteditable="true" id="listingTitle"></div>
                </div>

                <div class="result-item large">
                    <div class="result-label">
                        {{t.description}}
                        <span class="copy-icon" onclick="copyField('description')" title="Copier">📋</span>
                    </div>
                    <div class="result-value" contenteditable="true" id="description"></div>
                </div>
            </div>

            <button class="reset-btn" onclick="reset()">{{t.reset}}</button>
        </div>
    </div>

    <div class="toast" id="toast">{{t.copied}}</div>

    <script>
        let selectedFiles = [];
        const currentLang = '{{lang}}';
        const translations = {{translations_json | safe}};

        function changeLanguage() {
            const lang = document.getElementById('language').value;
            window.location.href = '/?lang=' + lang;
        }

        // Drag and drop
        const uploadZone = document.getElementById('uploadZone');
        
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            document.getElementById('photos').files = files;
            previewImages();
        });

        function previewImages() {
            const files = document.getElementById('photos').files;
            const preview = document.getElementById('preview');
            const analyzeBtn = document.getElementById('analyzeBtn');
            
            selectedFiles = Array.from(files).slice(0, 5);
            preview.innerHTML = '';
            
            if (selectedFiles.length > 0) {
                analyzeBtn.disabled = false;
                selectedFiles.forEach((file, index) => {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        const div = document.createElement('div');
                        div.className = 'preview-item';
                        div.innerHTML = `
                            <img src="${e.target.result}" alt="Photo ${index + 1}">
                            <button class="remove-btn" onclick="removeImage(${index})" type="button">×</button>
                        `;
                        preview.appendChild(div);
                    };
                    reader.readAsDataURL(file);
                });
            } else {
                analyzeBtn.disabled = true;
            }
        }

        function removeImage(index) {
            selectedFiles.splice(index, 1);
            const dataTransfer = new DataTransfer();
            selectedFiles.forEach(file => dataTransfer.items.add(file));
            document.getElementById('photos').files = dataTransfer.files;
            previewImages();
        }

        async function analyzePhotos() {
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const error = document.getElementById('error');
            const analyzeBtn = document.getElementById('analyzeBtn');
            
            if (selectedFiles.length === 0) {
                showError(translations[currentLang].select_photos);
                return;
            }

            loading.classList.add('show');
            results.classList.remove('show');
            error.classList.remove('show');
            analyzeBtn.disabled = true;

            const formData = new FormData();
            selectedFiles.forEach(file => formData.append('photos', file));
            formData.append('language', currentLang);

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.error) {
                    showError(data.error);
                } else {
                    document.getElementById('type').textContent = data.type;
                    document.getElementById('brand').textContent = data.brand;
                    document.getElementById('color').textContent = data.color;
                    document.getElementById('condition').textContent = data.condition;
                    document.getElementById('price').textContent = data.price;
                    document.getElementById('listingTitle').textContent = data.title;
                    document.getElementById('description').textContent = data.description;
                    results.classList.add('show');
                }
            } catch (err) {
                showError(translations[currentLang].error + ': ' + err.message);
            } finally {
                loading.classList.remove('show');
                analyzeBtn.disabled = false;
            }
        }

        function showError(message) {
            const error = document.getElementById('error');
            error.textContent = message;
            error.classList.add('show');
        }

        function copyField(fieldId) {
            const field = document.getElementById(fieldId);
            const text = field.textContent;
            navigator.clipboard.writeText(text).then(() => {
                showToast();
            });
        }

        function copyAll() {
            const fields = ['type', 'brand', 'color', 'condition', 'price', 'listingTitle', 'description'];
            const labels = {
                'type': translations[currentLang].product_type,
                'brand': translations[currentLang].brand,
                'color': translations[currentLang].color,
                'condition': translations[currentLang].condition,
                'price': translations[currentLang].price,
                'listingTitle': translations[currentLang].title_field,
                'description': translations[currentLang].description
            };
            
            let allText = '';
            fields.forEach(field => {
                const value = document.getElementById(field).textContent;
                allText += `${labels[field]}: ${value}\n\n`;
            });
            
            navigator.clipboard.writeText(allText).then(() => {
                showToast();
            });
        }

        function showToast() {
            const toast = document.getElementById('toast');
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 2000);
        }

        function reset() {
            document.getElementById('results').classList.remove('show');
            document.getElementById('preview').innerHTML = '';
            document.getElementById('photos').value = '';
            selectedFiles = [];
            document.getElementById('analyzeBtn').disabled = true;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    lang = request.args.get('lang', 'fr')
    if lang not in TRANSLATIONS:
        lang = 'fr'
    
    translations_json = json.dumps(TRANSLATIONS)
    return render_template_string(HTML_TEMPLATE, t=TRANSLATIONS[lang], lang=lang, translations_json=translations_json)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        files = request.files.getlist('photos')
        language = request.form.get('language', 'fr')
        
        if not files or len(files) == 0:
            return jsonify({'error': 'Aucune photo fournie'}), 400

        # Convertir images en base64
        images_base64 = []
        for file in files[:5]:
            img = Image.open(file.stream)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Redimensionner pour optimiser
            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=90)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            images_base64.append(img_base64)

        # Appel à l'API Claude pour analyse
        result = analyze_with_claude(images_base64, language)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_with_claude(images_base64, language):
    """Analyse les images avec l'API Claude Sonnet 4"""
    
    # Prompts optimisés selon la langue
    prompts = {
        'fr': """Tu es un expert en analyse de vêtements et accessoires pour Vinted. Analyse ces photos avec PRÉCISION MAXIMALE.

INSTRUCTIONS CRITIQUES :
1. TYPE : Identifie le type EXACT (maillot de foot, t-shirt, pull, sweat, pantalon, chaussures, sac, etc.)
   - Si c'est un maillot d'équipe sportive, dis "Maillot [équipe]" (ex: "Maillot Bayern Munich")
   - Si incertain, choisis le type le plus proche mais PRÉCIS

2. MARQUE : Détecte la marque VISIBLE sur les photos
   - Cherche logos, étiquettes, inscriptions
   - Pour les équipes : Bayern Munich, Real Madrid, FC Barcelona, PSG, etc.
   - Pour marques sport : Nike, Adidas, Puma, etc.
   - Si AUCUNE marque visible, écris "Non identifiée"

3. COULEUR : Identifie la couleur DOMINANTE exacte (Rouge, Bleu, Noir, Blanc, Gris, Vert, etc.)

4. ÉTAT : Estime l'état (Neuf avec étiquette, Très bon état, Bon état, Satisfaisant)

5. PRIX : Suggère un prix réaliste basé sur :
   - Type de produit
   - Marque (équipes pro = 25-40€, marques sport = 15-30€, basique = 8-15€)
   - État

6. TITRE : Crée un titre accrocheur et précis (ex: "Maillot officiel Bayern Munich - Lewandowski #9 - Saison 2021/22")

7. DESCRIPTION : Rédige une description attrayante, honnête et détaillée en 3-4 phrases.

Réponds UNIQUEMENT en JSON :
{
    "type": "type exact du produit",
    "brand": "marque détectée ou 'Non identifiée'",
    "color": "couleur dominante",
    "condition": "état estimé",
    "price": "XX",
    "title": "titre accrocheur",
    "description": "description détaillée"
}

SOIS ULTRA-PRÉCIS. Analyse VRAIMENT les images.""",

        'en': """You are an expert in analyzing clothing and accessories for Vinted. Analyze these photos with MAXIMUM PRECISION.

CRITICAL INSTRUCTIONS:
1. TYPE: Identify the EXACT type (football jersey, t-shirt, sweater, sweatshirt, pants, shoes, bag, etc.)
   - If it's a sports team jersey, say "Jersey [team]" (e.g., "Bayern Munich Jersey")
   - If uncertain, choose the closest but PRECISE type

2. BRAND: Detect VISIBLE brand in photos
   - Look for logos, labels, inscriptions
   - For teams: Bayern Munich, Real Madrid, FC Barcelona, PSG, etc.
   - For sport brands: Nike, Adidas, Puma, etc.
   - If NO visible brand, write "Unidentified"

3. COLOR: Identify exact DOMINANT color (Red, Blue, Black, White, Gray, Green, etc.)

4. CONDITION: Estimate condition (New with tags, Very good, Good, Fair)

5. PRICE: Suggest realistic price based on:
   - Product type
   - Brand (pro teams = €25-40, sport brands = €15-30, basic = €8-15)
   - Condition

6. TITLE: Create catchy and precise title (e.g., "Official Bayern Munich Jersey - Lewandowski #9 - 2021/22 Season")

7. DESCRIPTION: Write attractive, honest and detailed description in 3-4 sentences.

Respond ONLY in JSON:
{
    "type": "exact product type",
    "brand": "detected brand or 'Unidentified'",
    "color": "dominant color",
    "condition": "estimated condition",
    "price": "XX",
    "title": "catchy title",
    "description": "detailed description"
}

BE ULTRA-PRECISE. REALLY analyze the images.""",

        'es': """Eres un experto en análisis de ropa y accesorios para Vinted. Analiza estas fotos con MÁXIMA PRECISIÓN.

INSTRUCCIONES CRÍTICAS:
1. TIPO: Identifica el tipo EXACTO (camiseta de fútbol, camiseta, jersey, sudadera, pantalón, zapatos, bolso, etc.)
   - Si es una camiseta de equipo deportivo, di "Camiseta [equipo]" (ej: "Camiseta Bayern Munich")
   - Si no estás seguro, elige el tipo más cercano pero PRECISO

2. MARCA: Detecta marca VISIBLE en fotos
   - Busca logos, etiquetas, inscripciones
   - Para equipos: Bayern Munich, Real Madrid, FC Barcelona, PSG, etc.
   - Para marcas deportivas: Nike, Adidas, Puma, etc.
   - Si NO hay marca visible, escribe "No identificada"

3. COLOR: Identifica color DOMINANTE exacto (Rojo, Azul, Negro, Blanco, Gris, Verde, etc.)

4. ESTADO: Estima el estado (Nuevo con etiqueta, Muy buen estado, Buen estado, Aceptable)

5. PRECIO: Sugiere precio realista basado en:
   - Tipo de producto
   - Marca (equipos pro = €25-40, marcas deportivas = €15-30, básico = €8-15)
   - Estado

6. TÍTULO: Crea título atractivo y preciso (ej: "Camiseta oficial Bayern Munich - Lewandowski #9 - Temporada 2021/22")

7. DESCRIPCIÓN: Redacta descripción atractiva, honesta y detallada en 3-4 frases.

Responde SOLO en JSON:
{
    "type": "tipo exacto de producto",
    "brand": "marca detectada o 'No identificada'",
    "color": "color dominante",
    "condition": "estado estimado",
    "price": "XX",
    "title": "título atractivo",
    "description": "descripción detallada"
}

SÉ ULTRA-PRECISO. Analiza REALMENTE las imágenes.""",

        'de': """Du bist Experte für die Analyse von Kleidung und Accessoires für Vinted. Analysiere diese Fotos mit MAXIMALER PRÄZISION.

KRITISCHE ANWEISUNGEN:
1. TYP: Identifiziere den GENAUEN Typ (Fußballtrikot, T-Shirt, Pullover, Sweatshirt, Hose, Schuhe, Tasche, etc.)
   - Wenn es ein Sportteam-Trikot ist, sage "Trikot [Team]" (z.B. "Bayern München Trikot")
   - Wenn unsicher, wähle den nächsten aber PRÄZISEN Typ

2. MARKE: Erkenne SICHTBARE Marke auf Fotos
   - Suche nach Logos, Etiketten, Aufschriften
   - Für Teams: Bayern München, Real Madrid, FC Barcelona, PSG, etc.
   - Für Sportmarken: Nike, Adidas, Puma, etc.
   - Wenn KEINE sichtbare Marke, schreibe "Nicht identifiziert"

3. FARBE: Identifiziere genaue DOMINANTE Farbe (Rot, Blau, Schwarz, Weiß, Grau, Grün, etc.)

4. ZUSTAND: Schätze Zustand (Neu mit Etikett, Sehr gut, Gut, Akzeptabel)

5. PREIS: Schlage realistischen Preis vor basierend auf:
   - Produkttyp
   - Marke (Profi-Teams = €25-40, Sportmarken = €15-30, Basis = €8-15)
   - Zustand

6. TITEL: Erstelle ansprechenden und präzisen Titel (z.B. "Offizielles Bayern München Trikot - Lewandowski #9 - Saison 2021/22")

7. BESCHREIBUNG: Verfasse attraktive, ehrliche und detaillierte Beschreibung in 3-4 Sätzen.

Antworte NUR in JSON:
{
    "type": "genauer Produkttyp",
    "brand": "erkannte Marke oder 'Nicht identifiziert'",
    "color": "dominante Farbe",
    "condition": "geschätzter Zustand",
    "price": "XX",
    "title": "ansprechender Titel",
    "description": "detaillierte Beschreibung"
}

SEI ULTRA-PRÄZISE. Analysiere die Bilder WIRKLICH."""
    }
    
    # Construction du contenu avec les images
    content = [{"type": "text", "text": prompts.get(language, prompts['fr'])}]
    
    for img_base64 in images_base64:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": img_base64
            }
        })
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2048,
                "temperature": 0.3,  # Plus bas pour plus de précision
                "messages": [{
                    "role": "user",
                    "content": content
                }]
            },
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            text_content = data['content'][0]['text']
            
            # Extraire le JSON de la réponse
            if '```json' in text_content:
                text_content = text_content.split('```json')[1].split('```')[0].strip()
            elif '```' in text_content:
                text_content = text_content.split('```')[1].split('```')[0].strip()
            
            result = json.loads(text_content)
            
            # Formater le prix
            if 'price' in result and result['price']:
                price_value = str(result['price']).replace('€', '').replace('EUR', '').strip()
                result['price'] = f"{price_value}€"
            
            return result
        else:
            print(f"Erreur API: {response.status_code} - {response.text}")
            return get_fallback_analysis(language)
            
    except Exception as e:
        print(f"Erreur API Claude: {e}")
        return get_fallback_analysis(language)

def get_fallback_analysis(language):
    """Analyse de secours si l'API échoue"""
    fallbacks = {
        'fr': {
            'type': 'Vêtement',
            'brand': 'À préciser',
            'color': 'À préciser',
            'condition': 'Bon état',
            'price': '15€',
            'title': 'Article de qualité à vendre',
            'description': 'Article en bon état. Consultez les photos pour plus de détails. N\'hésitez pas à poser vos questions !'
        },
        'en': {
            'type': 'Clothing',
            'brand': 'To be specified',
            'color': 'To be specified',
            'condition': 'Good condition',
            'price': '15€',
            'title': 'Quality item for sale',
            'description': 'Item in good condition. Check the photos for more details. Feel free to ask questions!'
        },
        'es': {
            'type': 'Ropa',
            'brand': 'Por especificar',
            'color': 'Por especificar',
            'condition': 'Buen estado',
            'price': '15€',
            'title': 'Artículo de calidad en venta',
            'description': 'Artículo en buen estado. Consulta las fotos para más detalles. ¡No dudes en hacer preguntas!'
        },
        'de': {
            'type': 'Kleidung',
            'brand': 'Anzugeben',
            'color': 'Anzugeben',
            'condition': 'Guter Zustand',
            'price': '15€',
            'title': 'Qualitätsartikel zu verkaufen',
            'description': 'Artikel in gutem Zustand. Siehe Fotos für weitere Details. Fragen Sie gerne!'
        }
    }
    return fallbacks.get(language, fallbacks['fr'])

@app.route('/health')
def health():
    """Endpoint pour keep-alive"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
