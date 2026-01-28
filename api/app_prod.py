from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf
import json
import io
import os
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialisation de l'API
app = Flask(__name__)

# Configuration CORS plus sécurisée
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # En prod, mettre les domaines autorisés
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "modele", "classification_type_riz.keras")
LABELS_PATH = os.path.join(BASE_DIR, "modele", "class_names.json")

# Variables globales
model = None
class_names = None
IMG_SIZE = (224, 224)

# Chargement du modèle
def load_resources():
    """Charge le modele et les labels au demarrage"""
    global model, class_names
    
    try:
        logger.info(f"Chargement du modèle depuis: {MODEL_PATH}")
        model = tf.keras.models.load_model(MODEL_PATH)
        logger.info("Modele charg avec succes")

        logger.info(f"Chargement des labels depuis: {LABELS_PATH}")
        with open(LABELS_PATH, "r") as f:
            class_indices = json.load(f)
        
        # Inversion dictionnaire index → classe
        class_names = {v: k for k, v in class_indices.items()}
        logger.info(f"✅ Labels charges: {list(class_names.values())}")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors du chargement des ressources: {e}")
        return False

# Charger au démarrage
if not load_resources():
    logger.warning("L'API démarre sans modèle chargé")

# Prétraitement image
def preprocess_image(image_content):
    """Prend les bytes de l'image, traite et retourne l'array prêt pour le modèle"""
    try:
        image = Image.open(io.BytesIO(image_content)).convert("RGB")
        image = image.resize(IMG_SIZE)
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        logger.error(f"Erreur prétraitement: {e}")
        raise

# Routes API
@app.route("/", methods=["GET"])
def root():
    """Route racine - Informations sur l'API"""
    return jsonify({
        "message": "🌾 Rice Classification API",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": model is not None,
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "classes": "/classes",
            "info": "/info"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    """Healthcheck pour Docker"""
    if model is None:
        return jsonify({
            "status": "unhealthy",
            "model_loaded": False,
            "timestamp": datetime.now().isoformat()
        }), 503
    
    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "available_classes": list(class_names.values()) if class_names else [],
        "timestamp": datetime.now().isoformat()
    })

@app.route("/classes", methods=["GET"])
def get_classes():
    """Retourne la liste des classes disponibles"""
    if class_names is None:
        return jsonify({"error": "Classes non chargées"}), 503
    
    return jsonify({
        "classes": list(class_names.values()),
        "num_classes": len(class_names)
    })

@app.route("/info", methods=["GET"])
def get_info():
    """Informations sur le modele"""
    if model is None:
        return jsonify({"error": "Modèle non chargé"}), 503
    
    return jsonify({
        "model_type": "CNN Transfer Learning",
        "input_shape": [224, 224, 3],
        "num_classes": len(class_names) if class_names else 0,
        "classes": list(class_names.values()) if class_names else [],
        "framework": "TensorFlow/Keras"
    })

@app.route("/predict", methods=["POST"])
def predict():
    """Route de prédiction"""
    # Vérifier que le modèle est chargé
    if model is None:
        return jsonify({"error": "Modèle non chargé"}), 503
    
    # Vérifier la présence du fichier
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400
    
    file = request.files['file']
    
    # Vérifier que le fichier n'est pas vide
    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400
    
    try:
        logger.info(f"Réception d'une image: {file.filename}")
        
        # Lire et prétraiter l'image
        img_bytes = file.read()
        img_array = preprocess_image(img_bytes)

        # Prédiction
        logger.info("Prédiction en cours...")
        predictions = model.predict(img_array, verbose=0)[0]
        
        # 1. Préparer toutes les probabilités pour le graphique
        all_probs = {
            class_names[i]: float(predictions[i]) 
            for i in range(len(class_names))
        }
        
        # 2. Trier pour obtenir le Top 3
        sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
        
        # 3. Formatage final
        result = {
            "predicted_class": sorted_probs[0][0],
            "confidence": float(sorted_probs[0][1]),
            "top_3_predictions": [
                {"class": name, "confidence": float(conf)} 
                for name, conf in sorted_probs[:3]
            ],
            "all_probabilities": all_probs
        }
        
        logger.info(f"✅ Prédiction: {result['predicted_class']} ({result['confidence']:.2%})")
        
        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Erreur lors de la prédiction: {str(e)}")
        return jsonify({"error": f"Erreur lors de la prédiction: {str(e)}"}), 500

# Gestion des erreurs
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Route non trouvée"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Erreur serveur interne"}), 500

# Lancement
if __name__ == "__main__":
    logger.info("🚀 Démarrage de l'API Flask...")
    app.run(host="0.0.0.0", port=5000, debug=False)