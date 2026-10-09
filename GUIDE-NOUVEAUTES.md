# Kamas Radar — sources communautaires et capture HDV

## CraftRadar
Page : https://serialhornet.github.io/kamas-radar-dakal/craft-radar.html

Cette page reprend le CraftRadar HTML fourni par l'utilisateur, avec :
- catalogue DofusDude et recettes, si leur API est disponible ;
- serveur Dakal sélectionné par défaut pour les nouveaux visiteurs ;
- saisie/import CSV de prix, calcul de crafts ;
- import expérimental de capture HDV (PNG/JPG/WEBP).

Pour importer une capture : CraftRadar > Prix HDV > Capture HDV > Analyser la capture.
Le navigateur charge Tesseract.js (moteur OCR gratuit) depuis un CDN.
Le programme tente de retrouver le nom dans le catalogue et, uniquement lorsqu'un nombre clairement identifiable se trouve sur la même ligne, suggère un prix.
TOUJOURS corriger le prix proposé, sélectionner le lot x1/x10/x100 et confirmer manuellement.
Aucune image n'est envoyée à Kamas Radar ; pour charger le moteur et ses données linguistiques, une connexion aux CDN est nécessaire.
Le navigateur conserve les prix localement : ils ne sont pas synchronisés entre PC et téléphone.

## Communautés et autres sources
La collecte RSS/Atom est disponible dans scripts/collect.py, **mais aucune source extérieure n'est active par défaut**.
Il faut trouver une URL RSS/Atom HTTPS officielle, publique, et autorisant cet usage.
Il n'y a pas de scraping automatique de sites, forums ni de DoFocus.

Dans config/sources.json, ajouter à rss_feeds une entrée par source autorisée :
```json
{
  "name": "Nom du flux",
  "url": "https://adresse-du-flux-public-existante.example/rss.xml",
  "authorized": true
}
```
L'exemple ci-dessus est un **format fictif**, pas une URL utilisable.
Vérifier les conditions du site et la disponibilité de son flux avant d'entrer son adresse.
Les entrées RSS sont filtrées pour écarter Retro/Touch, Songes et multicompte explicites, tout en recherchant Unity/Dakal et les méthodes de kamas.
Elles seront visibles après la prochaine collecte GitHub Actions.

## Limites
- La description d'une vidéo n'est pas sa transcription ; aucune véritable traduction automatique des vidéos n'est activée.
- Les commentaires sont des retours de joueurs et non des preuves.
- Le filtrage automatique peut rejeter une vidéo valide ou en retenir une douteuse.
- La reconnaissance OCR n'est pas fiable à 100 % ; aucun prix n'est enregistré sans validation.
- La collecte RSS d'une source autorisée n'est pas équivalente à une analyse du texte intégral des articles.
- Les calculs restent dépendants de prix saisis par l'utilisateur.
