import streamlit as st
from src.utils.helpers import load_css
from src.ui.sidebar import render_sidebar
from src.ui.tabs import render_tabs

def main():
    #Configuration de la page et chargement du CSS
    st.set_page_config(
        page_title="RiceVision AI",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    load_css("static/style.css")

    #Affichage de la sidebar et recuperation des configurations
    api_url, show_probabilities, show_top3, show_confidence_gauge = render_sidebar()

    #Header principal
    st.markdown("""
        <div class="main-header">
            🌾 RiceVision AI
        </div>
        <div class="subtitle">
            Intelligence Artificielle de Classification de Types de Riz
        </div>
    """, unsafe_allow_html=True)

    # Affichage des onglets
    render_tabs(api_url, show_probabilities, show_top3, show_confidence_gauge)

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 2rem; border-top: 2px solid #FEE2E7; margin-top: 3rem;">
            <p style="color: #6B6B6B; font-family: 'Inter', sans-serif; line-height: 1.8;">
                🎓 Projet realise dans le cadre du cours <strong style="color: #19124B;">Analyse des donnees massives</strong><br>
                Pr. Cheikh SARR - Université de Thies - 2025-2026<br><br>
                <strong style="color: #19124B;">Realise par:</strong> Bintou GUEYE, Abdallah TANDIA, Abdoulaye DIAGNE SAMB
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
