import streamlit as st
import requests

def render_sidebar():
    with st.sidebar:
        st.markdown("# ⚙️ Configuration")
        
        api_url = st.text_input(
            "🔗 URL de l'API",
            value="http://localhost:5000",
            help="0.0.0.0"
        )
        
        st.markdown("---")
        
        st.markdown("## 🔬 Mode d'Analyse")
        st.radio(
            "",
            ["🎯 Analyse Rapide", "📊 Analyse Detaillee", "🔄 Analyse Comparative"],
            index=0,
            key="analysis_mode"
        )
        
        st.markdown("---")
        
        st.markdown("## 📈 Visualisations")
        show_probabilities = st.checkbox("Graphique des probabilites", value=True)
        show_top3 = st.checkbox("Top 3 predictions", value=True)
        show_confidence_gauge = st.checkbox("Jauge de confiance", value=True)
        
        st.markdown("---")
        
        st.markdown("## 🔌 Etat de l'API")
        try:
            response = requests.get(f"{api_url}/", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                st.markdown("""
                    <div class="success-box" style="padding:10px; border-radius:5px;">
                        <strong style="color: black !important;">API Connectée</strong>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📋 Détails"):
                    st.json(health_data)
            else:
                st.markdown("""
                    <div class="warning-box" style="padding:10px; border-radius:5px;">
                        <strong style="color: black !important;">⚠️ API Inaccessible</strong>
                    </div>
                """, unsafe_allow_html=True)
        except:
            # Pour l'erreur, on garde le rouge pour le contraste
            st.markdown("""
                <div class="error-box" style="padding:10px; border-radius:5px;">
                    <strong style="color: #EF4444 !important;">Connexion Impossible</strong>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("##### 📜 Historique")
        if st.button("🗑️ Effacer l'historique"):
            st.session_state.clear()
            st.rerun()
        
        st.markdown("---")
        


    return api_url, show_probabilities, show_top3, show_confidence_gauge
