from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf
import json
import io
import os

#Initialisation de l'API
app = Flask(__name__)

#Autoriser Streamlit
CORS(app)

# Chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR, "modele", "classification_type_riz.keras"
)

LABELS_PATH = os.path.join(
    BASE_DIR, "modele", "class_names.json"
)

# Chargement du modele et labels
# Charge une seule fois au démarrage du serveur
try:
    model = tf.keras.models.load_model(MODEL_PATH)

    with open(LABELS_PATH, "r") as f:
        class_indices = json.load(f)

    class_names = {v: k for k, v in class_indices.items()}
    print("Modele et labels charges avec succes.")
except Exception as e:
    print(f"Erreur lors du chargement des ressources : {e}")


#Pretraitement image
IMG_SIZE = (224, 224)

def preprocess_image(image_content):
    """Prend les bytes de l'image, traite et retourne l'array prêt pour le modele"""
    image = Image.open(io.BytesIO(image_content)).convert("RGB")
    image = image.resize(IMG_SIZE)
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


#Routes API
@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Rice Classification API est en cours"})


@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier envoye"}), 400
    
    file = request.files['file']
    
    try:
        img_bytes = file.read()
        img_array = preprocess_image(img_bytes)

        #Prediction
        predictions = model.predict(img_array)[0]
        
        #Preparer toutes les probabilites pour le graphique
        all_probs = {class_names[i]: float(predictions[i]) for i in range(len(class_names))}
        
        #Trier pour obtenir le Top 3
        sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
        
        #Formatage
        return jsonify({
            "predicted_class": sorted_probs[0][0],
            "confidence": float(sorted_probs[0][1]),
            "top_3_predictions": [
                {"class": name, "confidence": conf} for name, conf in sorted_probs[:3]
            ],
            "all_probabilities": all_probs
        })

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la prediction : {str(e)}"}), 500


#Lancement app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)