import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io
import time
from PIL import Image
import json
from src.utils.api import predict_image

def render_classification_tab(api_url, show_probabilities, show_top3, show_confidence_gauge):
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("""
            <div class="modern-card">
                <h2>📤 Telechargement d'Image</h2>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Glissez votre image ici ou cliquez pour parcourir",
            type=['jpg', 'jpeg', 'png'],
            help="Format accepte: JPG, PNG"
        )
        
        if uploaded_file is not None:
            # Afficher l'image
            image = Image.open(uploaded_file)
            st.image(image, caption="Image téléchargee", use_container_width=True)
            
            # Bouton d'analyse
            st.markdown("""
                <style>
                div.stButton > button p {
                    color: white !important;
                 }
                 </style>
             """, unsafe_allow_html=True)
            analyze_button = st.button("🚀 ANALYSER CETTE IMAGE", type="primary")
            
            if analyze_button:
                with col_right:
                    with st.spinner("🔄 Analyse en cours..."):
                        progress_bar = st.progress(0)
                        for percent in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(percent + 1)
                        
                        try:
                            result = predict_image(api_url, image)
                            
                            # Résultat principal
                            predicted_class = result['predicted_class']
                            confidence = result['confidence'] * 100
                            
                            # Déterminer l'emoji selon la confiance
                            if confidence >= 85:
                                emoji = "✅"
                            elif confidence >= 70:
                                emoji = "⚠️"
                            else:
                                emoji = "❓"
                            
                            # Affichage du résultat
                            st.markdown(f"""
                                <div class="result-card">
                                    <div style="font-size: 3.5rem; margin-bottom: 1rem;">{emoji}</div>
                                    <h3 style="color: #6B6B6B; font-family: 'Inter', sans-serif; font-weight: 600; margin-bottom: 0.5rem;">
                                        TYPE DÉTECTÉ
                                    </h3>
                                    <div class="result-title">{predicted_class}</div>
                                    <div style="color: #6B6B6B; margin: 1rem 0; font-weight: 500;">CONFIANCE</div>
                                    <div class="confidence-score">{confidence:.2f}%</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Jauge de confiance
                            if show_confidence_gauge:
                                fig_gauge = go.Figure(go.Indicator(
                                    mode="gauge+number",
                                    value=confidence,
                                    domain={'x': [0, 1], 'y': [0, 1]},
                                    title={'text': "Score de Confiance", 
                                           'font': {'size': 20, 'color': '#19124B', 'family': 'Inter'}},
                                    number={'font': {'size': 36, 'color': '#19124B', 'family': 'Playfair Display'}},
                                    gauge={
                                        'axis': {'range': [None, 100], 'tickcolor': "#19124B"},
                                        'bar': {'color': "#19124B"},
                                        'bgcolor': "#F8F9FA",
                                        'borderwidth': 2,
                                        'bordercolor': "#FEE2E7",
                                        'steps': [
                                            {'range': [0, 50], 'color': '#FEE2E7'},
                                            {'range': [50, 75], 'color': '#FED7E0'},
                                            {'range': [75, 100], 'color': '#FECDD6'}
                                        ],
                                        'threshold': {
                                            'line': {'color': "#19124B", 'width': 3},
                                            'thickness': 0.75,
                                            'value': 85
                                        }
                                    }
                                ))
                                
                                fig_gauge.update_layout(
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font={'color': "#2D2D2D", 'family': "Inter"},
                                    height=300
                                )
                                
                                st.plotly_chart(fig_gauge, use_container_width=True)
                            
                            # Top 3 prédictions
                            if show_top3:
                                st.markdown("""
                                    <div class="modern-card">
                                        <h3>🏆 Top 3 Predictions</h3>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                for i, pred in enumerate(result['top_3_predictions'], 1):
                                    conf_pct = pred['confidence'] * 100
                                    
                                    # Icône selon le rang
                                    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                                    medal = medals.get(i, "")
                                    
                                    st.markdown(f"""
                                        <div style="margin: 1rem 0;">
                                            <div style="color: #6B6B6B; font-size: 0.95rem; font-weight: 500; margin-bottom: 0.5rem;">
                                                {medal} {i}. {pred['class']}
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.progress(pred['confidence'], 
                                              text=f"{conf_pct:.2f}%")
                            
                            # Graphique de toutes les probabilités
                            if show_probabilities:
                                st.markdown("""
                                    <div class="modern-card">
                                        <h3>📊 Distribution des Probabilites</h3>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                probs_df = pd.DataFrame([
                                    {"Type": k, "Probabilite": v*100}
                                    for k, v in result['all_probabilities'].items()
                                ]).sort_values('Probabilite', ascending=False)
                                
                                fig_bar = px.bar(
                                    probs_df,
                                    x='Type',
                                    y='Probabilite',
                                    color='Probabilite',
                                    color_continuous_scale=['#FEE2E7', '#19124B'],
                                    text='Probabilite'
                                )
                                
                                fig_bar.update_traces(
                                    texttemplate='%{text:.2f}%',
                                    textposition='outside',
                                    marker_line_color='#19124B',
                                    marker_line_width=1.5
                                )
                                
                                fig_bar.update_layout(
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font={'color': "#2D2D2D", 'family': "Inter"},
                                    xaxis={'title': None, 'gridcolor': '#E5E5E5'},
                                    yaxis={'title': 'Probabilité (%)', 'gridcolor': '#E5E5E5'},
                                    showlegend=False,
                                    height=400
                                )
                                
                                st.plotly_chart(fig_bar, use_container_width=True)
                        
                        except requests.exceptions.RequestException as e:
                            st.error(f"Erreur de connexion à l'API: {e}")
                        except Exception as e:
                            st.error(f"Une erreur inattendue est survenue: {e}")
        
        else:
            with col_right:
                st.markdown("""
                    <div class="modern-card" style="text-align: center; padding: 3rem;">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">🌾</div>
                        <h3 style="color: #19124B;">
                            En Attente d'Image
                        </h3>
                        <p style="color: #6B6B6B; margin-top: 1rem;">
                            Téléchargez une image de grain de riz pour commencer l'analyse
                        </p>
                        <div class="info-box" style="margin-top: 2rem; text-align: left;">
                            <strong>📝 Instructions:</strong><br>
                            1. Cliquez sur "Browse files" ou glissez une image<br>
                            2. Sélectionnez une image de grain de riz<br>
                            3. Cliquez sur "ANALYSER LE TYPE DE RIZ"<br>
                            4. Consultez les resultats détailles<br><br>
                            <strong> Formats acceptes:</strong> JPG, PNG
                        </div>
                    </div>
                """, unsafe_allow_html=True)

def render_data_analysis_tab():
    with open('data/dataset_stats.json', 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    metrics = stats['metrics']
    class_dist = stats['class_distribution']

    st.markdown("""
        <div class="modern-card">
            <h2>📊 Apercu du Dataset</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🖼️ Total Images", metrics['total_images'])
    with col2:
        st.metric("📂 Classes", metrics['classes'])
    with col3:
        st.metric("🎯 Accuracy", metrics['accuracy'])
    with col4:
        st.metric("⚡ Temps/Image", metrics['time_per_image'])
    
    # Distribution des classes
    st.markdown("<br>", unsafe_allow_html=True)
    
    data_dist = pd.DataFrame(class_dist)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig_pie = px.pie(
            data_dist,
            values='Nombre',
            names='Type de Riz',
            title='Distribution des Classes',
            color_discrete_sequence=['#19124B', '#3D2E7E', '#5E4B9E', '#8168BE', '#FEE2E7']
        )
        
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#2D2D2D", 'family': "Inter"}
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_b:
        fig_bar2 = px.bar(
            data_dist,
            x='Type de Riz',
            y='Nombre',
            title='Nombre d\'Images par Classe',
            color='Nombre',
            color_continuous_scale=['#FEE2E7', '#19124B']
        )
        
        fig_bar2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#2D2D2D", 'family': "Inter"},
            showlegend=False
        )
        
        st.plotly_chart(fig_bar2, use_container_width=True)

def render_rice_types_tab():
    with open('data/rice_types.json', 'r', encoding='utf-8') as f:
        rice_types = json.load(f)
    
    for rice in rice_types:
        st.markdown(f"""
            <div class="modern-card">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 2.5rem;">{rice['emoji']}</div>
                    <h2 style="margin: 0;">{rice['name']}</h2>
                </div>
                <div style="color: #2D2D2D; line-height: 1.6;">
                    <p><strong style="color: #19124B;">Origine:</strong> {rice['origin']}</p>
                    <p><strong style="color: #19124B;">Caracteristiques:</strong> {rice['characteristics']}</p>
                    <p><strong style="color: #19124B;">Utilisation:</strong> {rice['usage']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

def render_documentation_tab():
    st.markdown("""
        <div class="modern-card">
            <h2>📚 Documentation Technique</h2>
        </div>
    """, unsafe_allow_html=True)
    
    doc_tabs = st.tabs(["🧠 Modèle", "🔌 API", "🐳 Docker", "🚀 Déploiement"])
    
    with doc_tabs[0]:
        st.markdown("""
            <div class="info-box">
                <h3 style="color: #19124B; margin-bottom: 1rem;">Architecture du Modèle</h3>
                <ul style="line-height: 1.8;">
                    <li><strong>Type:</strong> VGG16 Transfer Learning</li>
                    <li><strong>Input:</strong> 224x224x3</li>
                    <li><strong>Output:</strong> 5 classes (softmax)</li>
                    <li><strong>Framework:</strong> TensorFlow/Keras</li>
                    <li><strong>Accuracy:</strong> ~95%</li>
                    <li><strong>Paramètres:</strong> ~14M (trainable) + ~134M (frozen)</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with doc_tabs[1]:
        st.markdown("""
            <div class="info-box">
                <h3 style="color: #19124B; margin-bottom: 1rem;">Endpoints API</h3>
                <ul style="line-height: 1.8;">
                    <li><code>GET /</code> - Informations generales</li>
                    <li><code>GET /health</code> - Etat de l'API</li>
                    <li><code>POST /predict</code> - Classification</li>
                    <li><code>GET /classes</code> - Liste des classes</li>
                    <li><code>GET /model-info</code> - Infos modele</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.code("""
# Exemple Python
import requests

with open('rice.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/predict', files=files)
    print(response.json())
        """, language="python")
    
    with doc_tabs[2]:
        st.markdown("""
            <div class="info-box">
                <h3 style="color: #19124B; margin-bottom: 1rem;">Commandes Docker</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.code("""
# Build l'image
docker build -t rice-api .

# Lancer le conteneur
docker run -d -p 8000:8000 --name rice-api rice-api

# Docker Compose
docker-compose up -d
        """, language="bash")
    
    with doc_tabs[3]:
        st.markdown("""
            <div class="info-box">
                <h3 style="color: #19124B; margin-bottom: 1rem;">Deploiement avec ngrok</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.code("""
# Lancer ngrok
ngrok http 8000

# Vous obtiendrez une URL publique
# Exemple: https://xxxx.ngrok-free.app
        """, language="bash")

def render_tabs(api_url, show_probabilities, show_top3, show_confidence_gauge):
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Classification",
        "📊 Donnees & Analyse",
        "🎓 Types de Riz",
        "📚 Documentation"
    ])

    with tab1:
        render_classification_tab(api_url, show_probabilities, show_top3, show_confidence_gauge)
    
    with tab2:
        render_data_analysis_tab()

    with tab3:
        render_rice_types_tab()

    with tab4:
        render_documentation_tab()
