# Kamas Radar Dakal — installation sans programmation

1. Crée un compte GitHub : https://github.com/.
2. Crée un dépôt **public** nommé `kamas-radar-dakal` sans initialisation (ne coche pas « Add a README file »).
3. Sur la page vide du dépôt, choisis **uploading an existing file**. Dépose **le contenu du dossier** `kamas-radar-dakal` décompressé, y compris `.github/workflows/veille.yml`, puis valide avec **Commit changes**. Si l'interface n'accepte pas le dossier caché `.github`, crée ce fichier via **Add file > Create new file**, avec comme nom `.github/workflows/veille.yml`, et colle son contenu.
4. Dans Google Cloud Console (https://console.cloud.google.com/), crée un projet, active **YouTube Data API v3** et crée une clé API. Restreins-la à cette API. Vérifie les quotas gratuits et n'active pas de facturation payante.
5. Dans ton dépôt : **Settings > Secrets and variables > Actions > New repository secret**. Nom `YOUTUBE_API_KEY`, valeur = ta clé. Ne la publie jamais dans les fichiers.
6. Dans **Settings > Actions > General**, autorise les workflows et les permissions d'écriture si nécessaire. Le fichier de workflow demande `contents: write`.
7. Dans **Actions > Kamas Radar - Veille automatique > Run workflow**, lance une première collecte. Vérifie qu'elle est verte et que `docs/data.json` contient des résultats.
8. Dans **Settings > Pages > Build and deployment**, choisis **Deploy from a branch**, branche `main`, dossier `/docs`, puis **Save**.
9. Ouvre `https://TON-PSEUDO.github.io/kamas-radar-dakal/` (remplace TON-PSEUDO par ton pseudo GitHub).

La veille tourne 4 fois par jour à 02:17, 08:17, 14:17 et 20:17 UTC, avec retards possibles côté GitHub. Quatre recherches YouTube par exécution, soit 16 recherches/jour hors tests manuels. Les fiches en français sont des modèles automatiques et ne constituent pas une analyse de rentabilité réelle.

**DoFocus :** aucune collecte automatique. N'importe quel export DoFocus doit être expressément autorisé avant import. Pour cette version, tu peux consulter https://dofocus.fr/Dakal manuellement. Aucun import DoFocus automatique n'est fourni.

**Sources additionnelles :** cette première version ne surveille que YouTube. Les forums/RSS pourront être ajoutés dans une version ultérieure uniquement si les conditions d'accès le permettent.

**Budget :** GitHub Pages et Actions sont gratuits pour les dépôts publics selon les conditions de GitHub. L'API YouTube dispose d'un quota gratuit, sous réserve des conditions Google. Le site est public ; n'y stocke aucune donnée privée.
