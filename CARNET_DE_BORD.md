# 📘 Carnet de bord — Radar Dakal

**Projet :** Radar Dakal / Kamas Radar Dakal  
**Serveur ciblé :** DOFUS Unity, **Dakal**, monocompte  
**Site :** https://serialhornet.github.io/kamas-radar-dakal/  
**Dépôt :** https://github.com/Serialhornet/kamas-radar-dakal  
**Dernière synthèse :** 10 octobre 2026

> Document de référence du projet. Mettre cette page à jour après chaque grande évolution pour reprendre facilement le développement, même dans une nouvelle conversation.

## Les 7 outils réunis dans le même site

| Outil | Identité | Fonctionnalités principales |
|---|---|---|
| 🪙 Kamas Radar | Vert | Veille astuces kamas DOFUS Unity ; vidéos YouTube, Shorts, discussions communautaires, liens TikTok ajoutés manuellement ; filtres sources, pertinence monocompte, résultats peu vus |
| ⚒️ CraftRadar | Bleu glace | Catalogue objets/recettes, coûts de craft, prix HDV Dakal, recherche, récupération des prix depuis captures d'écran (OCR local), modification des lots |
| 🧭 RécolteRadar | Ambre | Routes indicatives de métiers de récolte par tranches de niveau, coordonnées et Zaaps conseillés |
| ⏱️ FarmRadar | Violet | Chronomètre, pause/reprise, minuteur, bilan ressources/kamas/heure, prix liés à CraftRadar, catalogue monstres, simulateur de drops manuels, alerte sonore à volume ajustable |
| 📜 QuêteRadar | Rose corail | Sélection de quêtes quotidiennes et hebdomadaires, liens guides, récompenses connues, cases à cocher, échéances, sauvegarde de progression |
| 💎 BrisageRadar | Rouge rubis | Calcul théorique du brisage, coût de craft et prix HDV depuis CraftRadar, jets personnalisables, exos, overs, prix des runes et coefficients modifiables |
| 🐣 ÉlevageRadar | Turquoise | Suivi Dragodindes/Muldos/Volkornes et jauges d'enclos, carburants, objectifs d'élevage, rappels sonores avec volume et test, comparaison coûts avec CraftRadar, croisements et fiches de montures |

## Partage des données

- **Prix Dakal** : les outils économiques concernés utilisent le stockage local de CraftRadar (clé `craftRadar_live_v2` dans le navigateur). Les changements synchronisés passent aussi par un canal `radar-dakal-prices`.
- **Sauvegarde personnelle** : plusieurs outils conservent leurs données via `localStorage` ou `IndexedDB`. Ces données ne suivent pas automatiquement l'utilisateur sur un autre navigateur/appareil et peuvent disparaître si les données du site sont effacées.
- **Aucun accès direct au client de jeu** : timers, jauges, rentabilités et probabilités peuvent nécessiter une saisie ou confirmation manuelle.

## Où se trouvent les fonctionnalités ?

- Point d'entrée : `docs/index.html`
- CraftRadar : `docs/craft-radar.html`
- RécolteRadar : `docs/recolte-radar.html`
- FarmRadar : `docs/farm-radar.html`
- QuêteRadar : `docs/quete-radar.html`, données `docs/quetes-data.json`
- BrisageRadar : `docs/brisage-radar.html`
- ÉlevageRadar : `docs/elevage-radar.html`
- Croisements : `docs/croisements-dragodindes.json` (66 variétés), `docs/croisements-muldos.json` (120), `docs/croisements-volkornes.json` (120)
- Fiches montures : `docs/monture-fiche.html`, via des données/images d'encyclopédie externes lorsqu'elles sont disponibles
- Veille Kamas : `scripts/collect.py`, `config/sources.json`, `config/liens-communautaires.json`, workflow dans `.github/workflows/veille.yml`

## Fonctionnalités remarquables réalisées

- Sept onglets dans le même site GitHub Pages.
- Raccourci Windows personnalisé pour ouvrir le site depuis le bureau (pack distribué dans la conversation, non stocké dans ce dépôt).
- Prix des objets et ressources partagés entre les outils compatibles.
- Alerte **FarmRadar** : trois bips graves, volume 0–100 %, test, coupure, volume enregistré.
- Alerte **ÉlevageRadar** : trois notes aiguës ascendantes, volume 0–100 %, test, coupure, rappel avant contrôle d'enclos.
- Croisements de montures avec recettes alternatives ; **certains jeux de données communautaires divergent ou sont incomplets** et sont signalés.
- Fiches illustrées de montures par lien externe : leur image et leurs caractéristiques dépendent des données accessibles.

## Limites connues et points à vérifier

1. **Ne pas promettre de taux de drop officiels** : FarmRadar utilise un simulateur simplifié, les taux renseignés par l'utilisateur n'étant pas automatiquement vérifiés.
2. **BrisageRadar** : son calcul est un modèle manuel indicatif, pas une réimplémentation validée de DoFocus. Comparer les estimations aux runes réellement obtenues.
3. **ÉlevageRadar** : les timers de jauge sont des estimations, pas une lecture temps réel du jeu ; vérifier les mécaniques à chaque mise à jour DOFUS (notamment 3.7 et versions suivantes).
4. **Volkornes** : la base répertorie 120 variantes, mais certains croisements multiples ne sont pas intégralement renseignés. Les divergences communautaires de Muldos sont signalées.
5. **QuêteRadar** : sélection initiale non exhaustive, récompenses parfois variables, guides parfois anciens, horaires de réinitialisation à confirmer selon chaque quête.
6. **Kamas Radar** : collecte YouTube/Shorts automatique via GitHub Actions ; TikTok ne fait pas l'objet d'une collecte automatisée complète. Les sources communautaires nécessitent une vérification.
7. **Illustrations externes** : fiches montures dépendantes des images et API externes, donc certaines images peuvent être absentes.
8. Les modifications de code ont été vérifiées syntaxiquement lors de leur ajout, **mais cela ne vaut pas test complet en navigateur** sur toutes les plateformes.

## Prochaines idées / backlog

- [ ] Tester les sept outils sur PC et mobile et corriger les problèmes remontés.
- [ ] Renforcer les exports/imports de sauvegarde, idéalement un export global de tous les outils.
- [ ] Compléter et vérifier les croisements multiples de Volkornes.
- [ ] Améliorer la précision des prédictions de brisage à partir de données réelles.
- [ ] Vérifier les sources des taux de drop et les mécanismes de prospection.
- [ ] Compléter les quêtes répétables et leurs récompenses.
- [ ] Valider la disponibilité des images et fiches de montures dans le navigateur.
- [ ] **Nouvelles idées à venir** — laisser cette ligne ouverte aux prochaines sessions !

## Reprendre le projet

Dans une nouvelle conversation, dire :

> « Reprends notre projet Radar Dakal dans GitHub `Serialhornet/kamas-radar-dakal`. Lis d'abord `CARNET_DE_BORD.md` pour retrouver les sept outils, les fonctionnalités, les limites et le backlog. Voici mon idée… »

---
**Maintenu ensemble, au fil des idées et des tests.** 🐉💰
