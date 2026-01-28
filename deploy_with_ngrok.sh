#!/bin/bash

#Script pour deployer avec Docker + ngrok

echo "🐳 === Deploiement Rice Classification API ==="
echo ""

#Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

#Etape 1: Build Docker
echo -e "${BLUE}📦 Etape 1: Build de l'image Docker...${NC}"
docker build -t rice-classification-api .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors du build${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Image Docker créée avec succès${NC}"
echo ""

#Etape 2: Arreter les conteneurs existants
echo -e "${BLUE}🛑 Étape 2: Arret des conteneurs existants...${NC}"
docker stop rice-flask-api 2>/dev/null || true
docker rm rice-flask-api 2>/dev/null || true

echo ""

#Etape 3: Lancer le conteneur
echo -e "${BLUE}🚀 Étape 3: Lancement du conteneur...${NC}"
docker run -d \
    --name rice-flask-api \
    -p 5000:5000 \
    -v $(pwd)/modele:/app/modele \
    rice-classification-api

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors du lancement${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Conteneur lancé${NC}"
echo ""

#Attendre que l'API soit prête
echo -e "${BLUE}⏳ Attente du démarrage de l'API...${NC}"
sleep 5

#Tester l'API
echo -e "${BLUE}🧪 Test de l'API...${NC}"
response=$(curl -s http://localhost:5000/)
echo "$response"
echo ""

#Etape 4: Lancer ngrok
echo -e "${BLUE}🌐 Etape 4: Exposition via ngrok...${NC}"
echo -e "${YELLOW}Assurez-vous que ngrok est installe et configure${NC}"
echo ""

#Verifier si ngrok est installe
if ! command -v ngrok &> /dev/null; then
    echo -e "${YELLOW}⚠️  ngrok n'est pas installe${NC}"
    echo "Installez-le depuis: https://ngrok.com/download"
    echo ""
    echo -e "${GREEN}✅ API disponible localement sur: http://localhost:5000${NC}"
    exit 0
fi

echo "Lancement de ngrok..."
echo -e "${GREEN}➡️  Appuyez sur Ctrl+C dans une nouvelle fenêtre pour arrêter ngrok${NC}"
echo ""

#Lancer ngrok
ngrok http 5000