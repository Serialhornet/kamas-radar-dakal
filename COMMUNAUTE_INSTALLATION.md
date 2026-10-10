# Radar Dakal — installation de l'espace communautaire

> **État du projet : socle créé, non activé.** Le site actuel et ses sept outils continuent de fonctionner tant qu'aucune connexion Supabase opérationnelle n'est configurée. Ne pas annoncer un espace privé actif avant validation de toutes les étapes.

## Ce qui est déjà dans le dépôt

- `supabase/migrations/20261010_radar_community.sql` : base, profils, état personnel par outil, prix HDV communs, votes, commentaires et règles RLS.
- `supabase/functions/radar-admin/index.ts` : API administrateur pour créer/suspendre/réactiver des joueurs et renouveler leurs clés.
- `docs/community-client.js` : connexion par clé, actions base commune (prix, votes, commentaires, états personnels).
- `docs/community-config.js` : configuration **publique** du client, **disabled** par défaut.
- `docs/communaute.html` : écran de connexion, profil, gestion des invitations, saisie simple de prix partagés.
- `docs/index.html` : lien vers la nouvelle page, mais **pas encore de verrouillage de l'application**.

### Important : fonctionnalité encore à terminer

La gestion des membres et une base commune sont préparées, mais **les outils individuels utilisent toujours leur stockage local**. Les prix affichés par CraftRadar ne se synchronisent PAS encore avec la table commune. Les votes/commentaires ne sont PAS encore visibles dans les cartes Kamas Radar. Le site public n'est pas privé tant qu'une barrière d'accès et une politique de protection n'ont pas été déployées et vérifiées. Ne jamais considérer un simple masque JavaScript comme une protection des fichiers statiques accessibles sur GitHub Pages.

## Étapes pour activer le serveur (administrateur)

1. Créer un projet Supabase sur https://supabase.com/dashboard (compte personnel).
2. Dans Supabase > SQL Editor, exécuter **tout** le contenu de `supabase/migrations/20261010_radar_community.sql`. Vérifier les cinq tables et les règles RLS.
3. Dans **Authentication > Users**, créer un utilisateur initial avec :
   - e-mail : `radar-admin@radar-dakal.example.com` (e-mail technique non routable)
   - un **mot de passe fort et aléatoire composé de caractères hexadécimaux MAJUSCULES**, au moins 32 caractères ;
   - « Auto Confirm User / confirmation de l'e-mail » activé.
   - Noter son identifiant UUID.
4. Dans SQL Editor, exécuter avec l'UUID réel :
   `insert into public.radar_profiles(id,pseudo,role) values ('UUID_REEL_DU_COMPTE','Serialhornet','admin');`
5. Le premier accès utilisera la clé **`RD-ADMIN-VOTRE_MOT_DE_PASSE_ADMIN`**. Garder cette clé privée et ne JAMAIS la coller dans GitHub ni dans cette conversation. La clé est un mot de passe d'authentification, pas un simple identifiant. Si vous utilisez l'adresse fictive `.example.com`, ne comptez pas sur la récupération par e-mail ; seuls les administrateurs Supabase peuvent restaurer le compte initial.
6. Installer ou utiliser Supabase CLI et déployer la fonction :
   `supabase login`
   `supabase link --project-ref VOTRE_PROJECT_REF`
   `supabase functions deploy radar-admin`
   La fonction utilise les variables secrètes `SUPABASE_URL` et `SUPABASE_SERVICE_ROLE_KEY` dans **l'environnement Supabase uniquement**. Vérifier le support de ces variables et les définir via Supabase secrets si nécessaire.
7. Dans Supabase **Project Settings > API**, relever **Project URL** et **anon / publishable key** (clé publique UNIQUEMENT).
8. Dans `docs/community-config.js`, régler :
   ```js
   window.RADAR_COMMUNITY_CONFIG = Object.freeze({
     enabled: true,
     url: "https://VOTRE_PROJECT_REF.supabase.co",
     anonKey: "VOTRE_ANON_OU_PUBLISHABLE_KEY"
   });
   ```
9. Ouvrir `https://serialhornet.github.io/kamas-radar-dakal/communaute.html`, entrer la clé admin, puis tester l'ajout d'un **profil de test**. Un code `RD-...` nominatif apparaît. Copier et transmettre uniquement au joueur concerné.
10. Vérifier que le profil test ne peut pas lire les données personnelles d'autres profils, qu'il ne peut pas appeler l'API administrateur et qu'un compte suspendu ne peut plus agir sur les données (RLS).

## Confidentialité et gestion des accès

- Aucun `service_role` ni `sb_secret_...` dans `docs/`, sur le front-end ou dans le dépôt public.
- La clé publique `anon/publishable` peut être exposée : la protection repose sur Supabase Auth + RLS.
- Les clés utilisateurs sont des secrets de connexion individuels et ne doivent pas être stockées en clair dans une base commune.
- Seul un compte admin actif peut appeler la fonction `radar-admin` après authentification. Ne pas supprimer l'étape de vérification JWT.
- Les profils suspendus sont bloqués par RLS. **Le renouvellement d'un mot de passe ne suffit pas, à lui seul, à invalider immédiatement toutes les sessions JWT existantes** : exiger une vérification du comportement de révocation Supabase avant de promettre une coupure instantanée lors d'un reset.
- Chaque membre peut obtenir ses propres données depuis `radar_personal_state`, tandis que `radar_shared_prices`, `radar_votes` et `radar_comments` sont collectifs.
- Le premier navigateur disposant déjà des données personnelles de l'ancien Radar n'est **pas encore migré** ; ne pas vider son cache ni supprimer les données de son site.
- L'application GitHub Pages et ses fichiers HTML/JS restent publics ; l'accès aux **données protégées** dépend de Supabase, pas d'une page HTML cachée.

## Suite du développement avant de déclarer le site prêt

- [ ] Activer et tester le serveur Supabase, l'authentification et l'admin.
- [ ] Ajouter le contrôle de session au démarrage du site (navigation non autorisée vers les données privées) ; documenter que les fichiers statiques restent publics.
- [ ] Mettre en place une migration non destructive des données existantes vers `radar_personal_state` pour les outils utilisant localStorage et IndexedDB.
- [ ] Relier les prix CraftRadar / FarmRadar / BrisageRadar / ÉlevageRadar à `radar_shared_prices`, avec contrôle des conflits et des prix.
- [ ] Ajouter l'interface et les badges de votes/commentaires sur les cartes KamasRadar, avec pseudo auteur et modération.
- [ ] Tester les règles d'accès et les données partagées entre deux comptes réels, y compris deux navigateurs et appareils.
- [ ] Sauvegardes/export/import pour les profils, prévention des pertes de données et rollback.

## Reprise après une pause

Lire ce fichier et les migrations avant de modifier les outils. Si les identifiants Supabase ne sont pas encore configurés, **ne jamais activer de pseudo-connexion locale non sécurisée** comme remplacement de l'authentification.
