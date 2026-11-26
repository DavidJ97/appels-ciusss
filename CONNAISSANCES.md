# Appels CIUSSS : base de connaissances complète

> Document de référence pour une IA (ChatGPT, Claude, etc.) qui doit travailler sur ce projet. Lisez-le en entier avant toute modification.

## 1. En bref

| | |
|---|---|
| **Nom** | Appels CIUSSS : guides de prise de RDV |
| **Auteur** | David Jules (Jupiterre), agent administratif classe 3, CIUSSS du Centre-Ouest-de-l'Île-de-Montréal (Santé Québec) |
| **But** | Transformer les protocoles d'appel papier en guides interactifs pour prendre des rendez-vous au téléphone sans rien oublier |
| **Format** | Un seul fichier `index.html` autonome (~2,8 Mo), sans serveur ni build |
| **App en ligne** | https://claude.ai/artifact/RFbdbPH49HBJugvwjh2Ez4 (version complète, avec numéros internes) |
| **Dépôt public** | https://github.com/DavidJ97/appels-ciusss (numéros internes retirés) |
| **Langue** | Français (quelques phrases à dire aussi en anglais) |

### Ce que fait l'app pendant un appel
1. Pose les questions du protocole, dans l'ordre.
2. Affiche un **verdict** à chaque étape : `go` (prendre RDV), `hold` (attendre ou vérifier), `stop` (pas admissible ou référer), `done` (appel terminé).
3. Donne les **phrases exactes à dire** au patient (bouton Copier).
4. Indique le **module, le service et l'accès Clic Santé** à utiliser.
5. Produit un **résumé copiable** pour le dossier (avec la durée de l'appel).

---

## 2. Règles de travail (à respecter absolument)

1. **Ne jamais inventer une règle de protocole.** Si une information manque ou est ambiguë, l'app dit « Vérifiez auprès de votre chef d'équipe ».
2. **Vérifier les infos qui changent** (âges d'admissibilité, horaires, numéros) sur des sources officielles : Québec.ca, le Répertoire santé (sante.gouv.qc.ca), le site du CIUSSS (ciussscentreouest.ca).
3. **Simple et direct** : pas de complexité inutile.
4. **Réutiliser avant de créer** : chercher d'abord un dépôt GitHub ou un asset libre qui fait déjà la chose (donner le lien et la licence).
5. **Un commit à chaque changement**, puis pousser sur GitHub et redonner le lien de l'app en ligne.
6. **Version publique** : les entrées du répertoire marquées « Ne pas donner aux usagers » (`w:1`) sont retirées par `sanitize.py` avant chaque push.
7. Ne jamais mentionner Desjardins (sans rapport avec le projet).

---

## 3. Architecture technique

### 3.1 Fichier unique
Tout est intégré dans `index.html` : CSS, JavaScript, librairies et modèles 3D en base64. Ordre des blocs :
1. `<head>` : CSS (verre, optique, protocole, cadran, thèmes, monde 3D, panneaux).
2. `<body>` : rail du haut (`#pgrp`, `#ptitle`, `#worldBtn`, `#to3d`, `#palBtn`), sections d'étapes, tiroir, répertoire (`#dirDrawer`), palette de recherche (`#pal`), monde 3D (`#world`), `#qsrc`, `#toast`.
3. Scripts : three.js, données GLB (`window.__GLB`), MiniSearch, script principal (moteur + cadran + monde 3D), `<svg id="lo-defs">`, script d'optique (**toujours en dernier**).

### 3.2 Librairies intégrées
| Librairie | Usage | Licence |
|---|---|---|
| three.js r170 (sous-ensemble bundlé avec esbuild en IIFE, global `THREE`) + GLTFLoader, SkeletonUtils, décodeur meshopt | Monde 3D | MIT |
| MiniSearch 7.2.0 | Recherche dans les protocoles et le répertoire | MIT |
| Quaternius « Ultimate Animated Character Pack » | Personnages 3D animés | CC0 |

Personnages utilisés (allégés avec gltf-transform : prune, resample, meshopt) :
- `agent` = Doctor_Male_Young (le joueur, en blouse)
- `nurse` = Doctor_Female_Young (l'infirmière)
- `patient` = Casual_Female (patients et parents)

Animations conservées : Idle, Walk, Run, Jump, Victory, Defeat, Shoot_OneHanded, RecieveHit.

Inspirations d'animation : The Aviator (yakudoo, mer animée, style low-poly), CrossRoad (hexianWeb, MIT, sauts), folio de Bruno Simon (sons).

### 3.3 Moteur de protocoles (le cœur, à ne pas casser)
- **État global** : `st` (réponses), `cur` (étape courante), `P` (code du chapitre courant).
- **Registre** : `META{g,l,h,d,hr}` (groupe, libellé, hash, description, angle du cadran), `REG{dc:DC, sa:SA, …}` (un objet par chapitre), `THEME[p]=[encre, accent, saturation]`.
- Chaque objet de chapitre expose `upd()`, `verdict()`, `summary()`, `grid()`, `state(i)`, `answer(i)`, `blocked(i)`, `label()`.
- Rougeole (`rg`) et Maladies chroniques (`ch`) sont gérés directement dans `stepVerdict()`.
- Fonctions communes : `upd()` (recalcule tout depuis le DOM ; finit par `__World.sync()`), `go()`, `reset()`, `setProto(p)`, `summary()`, `fmt()`, `toast()`, `copy()`.
- Contrôles du DOM : boutons segmentés `.seg[data-k] [data-v]` avec `aria-pressed`, cases à cocher, champs `input`/`select` dans `main`.
- Navigation : chaque chapitre a des sections `<section data-p="xx" data-s="n">` ; le bouton Suivant est désactivé par `blocked(cur)`.

### 3.4 Interface classique (2D)
- Style « verre » (glassmorphism) avec effets d'optique.
- **Cadran rotatif** (porté de l'app IDoM) pour changer de chapitre ; chaque chapitre a son thème de couleur.
- Palette de recherche (MiniSearch), répertoire téléphonique en tiroir.
- Le choix 3D ou classique est mémorisé dans `localStorage['ciusss:vue']`.

### 3.5 Monde 3D (`window.__World`)
Le jeu lit le **vrai DOM** du protocole, donc la logique est toujours identique à celle de la vue 2D :
- `collect()` : lit les éléments visibles de l'étape (choix, cases, champs, phrases, infos, boutons, résumé).
- `todo()` : éléments restant à faire (clé `ikey()`, ensemble `GB.done`).
- `isEnd()` : fin du parcours (`st.e.end`, verdict stop avec Suivant désactivé, ou libellé Fin/Référer/Transférer/Aviser).
- `ask({who,text,field,copy,then})` : dialogue `#qdlg` (style RPG), dont le champ se synchronise avec le vrai champ.

**Modes** :
| Mode | Utilisé par | Description |
|---|---|---|
| `campus` | accueil | On marche entre des pavillons, un par chapitre |
| `board2` | 13 chapitres | Plateau générique, un style visuel par chapitre (`STY`) |
| `board` | Zona | Serpents et échelles fait à la main (graphe `ZN`) |
| `gallery` | Rougeole | Stand de tir à l'arc forain (cibles sur rails, prix si verdict `done`) |

**Styles des plateaux (`STY`)** :
- Route et ville : Rougeole, Adultes.
- Pelouse en spirale avec arbres : Maladies chroniques.
- Pelouse fleurie avec femme enceinte : dcaT.
- Eau avec rochers (mer animée) : Strep A, COVID, Colorectal, VPH.
- Aire de jeu avec ballons : Enfants, Pédiatrie, VRS bébés.
- Damier avec livres : TCT.
- Neige : Campagne.
- Laboratoire avec tubes : Prélèvements.

**Mécaniques des plateaux** :
- Jusqu'à 4 réponses : des voies directionnelles (gauche, haut, droite, bas).
- Plus de 4 réponses ou des cases à cocher : éventail de panneaux numérotés (touches 1 à 9).
- Échelle quand une réponse fait sauter des questions ; serpent vers une maison de fin quand `isEnd()`.
- Portail vers l'étape suivante ; « Mission accomplie » avec feux d'artifice à la fin.
- Les champs sont demandés par l'infirmière, les phrases à dire par un personnage du chapitre.
- Une réponse manquante est redemandée jusqu'à 3 fois (`GB.retry`).

**Accessibilité et commandes** :
- **Panneau de réponses** `#chpanel` : gros boutons HTML (texte foncé sur blanc, pastille de couleur avec flèche ou numéro), utilisables au doigt, à la souris et au clavier (Tab, Entrée, chiffres). À droite sur ordinateur, en bas sur téléphone, sur une ligne compacte en mode paysage. Les étiquettes 3D des panneaux sont masquées (`nolab`).
- **« ↩ Corriger le choix précédent »** `#undoBtn`, tout en bas de l'écran (touche Retour arrière aussi) :
  - un instantané est pris à chaque question posée (`hPush`) : DOM, `st`, `cur`, `GB.done`, chemin, position du joueur, nombre d'objets de la scène ;
  - le retour restaure l'état précédent **sans recommencer le plateau** : le joueur revient sur la case précédente et les objets ajoutés depuis sont retirés ;
  - les boutons segmentés sont restaurés par clé `data-k=valeur#occurrence`, et la comparaison se fait sur `cur` + `st`.
- **Caméra** (`CAM`) :
  - ordinateur : glisser avec le clic droit (ou Ctrl), molette pour zoomer ;
  - téléphone : bouton 🎥 puis glisser ; deux doigts = pincer pour zoomer, tourner pour pivoter, glisser pour incliner.
- **Barre d'outils du bas** : Campus (changer de chapitre), Rechercher, Répertoire, Aide-mémoire, Caméra, Son, Rejouer, Vue classique.

**Rendu** : ciel en dégradé (dôme), contre-jour, ombres 2048, brouillard, vignette, particules (`burst`, `ring`), secousse de caméra, sons WebAudio (coupés par défaut, bouton ♪), personnages qui respirent et clignent.

### 3.6 Tests
- Playwright sans écran avec swiftshader (`--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`).
- Un robot joue chaque chapitre 3D jusqu'au bout et vérifie qu'il n'y a pas d'erreur.
- Les tests de régression de la logique forcent la vue classique (`localStorage.setItem('ciusss:vue','classique')`).
- Crochets de test : `__World._g()`, `_ga()`, `_board()`, `_go(p)`, `_items()`, `_tiles()`, `_find(txt)`.

---

## 4. Les 15 chapitres

| Code | Hash | Chapitre | Groupe | Jeu 3D |
|---|---|---|---|---|
| rg | `#rougeole` | Rougeole | Vaccination | Stand de tir |
| dc | `#dcat` | dcaT grossesse | Vaccination | Plateau fleuri |
| ve | `#enfants` | Enfants 2 ans + | Vaccination | Aire de jeu |
| va | `#adultes` | Adultes | Vaccination | Ville |
| tc | `#tct` | Stagiaires et TCT | Vaccination | Damier |
| cm | `#campagne` | Grippe, COVID, VRS | Vaccination | Neige |
| vb | `#vrs-bebes` | VRS bébés | Vaccination | Aire de jeu |
| zo | `#zona` | Zona | Vaccination | Serpents et échelles |
| pr | `#prelevements` | Prélèvements | Dépistage et prélèvements | Laboratoire |
| sa | `#strep` | Strep A | Dépistage et prélèvements | Îles |
| cv | `#covid` | Dépistage COVID | Dépistage et prélèvements | Îles |
| cr | `#colorectal` | Cancer colorectal | Dépistage et prélèvements | Rivière |
| vp | `#vph` | Dépistage VPH | Dépistage et prélèvements | Îlot du mardi |
| ch | `#chroniques` | Maladies chroniques | Suivi | Spirale |
| tp | `#pediatrie` | Trajectoire pédiatrique | Suivi | Aire de jeu |

### 4.1 Rougeole (`rg`, 5 étapes)
1. **Admissibilité** (Panorama Production / SI-PMI) :
   - moins de 12 mois : pas de vaccin ; la DRSP a contacté la famille, et si le parent reste inquiet → 811 ;
   - née avant 1970 : protégée ;
   - née entre 1970 et 1979 : 2 doses pour un stagiaire ou travailleur de la santé, un voyageur ou une recrue militaire ; 1 dose pour garderie, école ou autre ;
   - née en 1980 ou après : 2 doses ;
   - preuves d'immunité, sans RDV : attestation médicale (rougeole avant le 1er janvier 1996) ou sérologie positive ;
   - aucune dose au profil : vaccinée à l'étranger ? Carnet bleu du Québec → RDV de validation ; carnet étranger en français ou en anglais → RDV, validé sur place ; autre langue → pas de RDV, le carnet doit d'abord être évalué.
2. **Profil RAMQ** apparié ? Valider nom, nom de jeune fille de la mère, adresse, date de naissance, téléphone, NAM, courriel. Un écart se saisit dans « Profils NON appariés_Rougeole.xlsx » (ne pas modifier le profil).
3. **Symptômes et contact**, obligatoire : fièvre, éruption, toux, nez qui coule, conjonctivite, taches de Koplik, contact soupçonné. S'il y en a un → pas de RDV, 811.
4. **RDV Clic Santé** : module 80036 (Vaccination générale), service « Vaccination contre la rougeole 4 ans et plus », Gestion #2 ; Côte-Saint-Luc (6900 Décarie) ou Parc-Extension (7101 av. du Parc), du lundi au samedi, 10 h à 17 h 45.
5. **Consignes** : évaluation par l'infirmière, arriver 5 min avant, masque obligatoire, carte RAMQ, PFSI ou pièce d'identité.

### 4.2 dcaT grossesse (`dc`, 5 étapes)
1. Raison : dcaT pour une femme enceinte ? Sinon appel hors sujet → CLSC du quartier (recherche par code postal), inscrire dans « Appels Hors-Sujet v2 ».
2. Semaines de grossesse (saisies, ou calculées depuis les dernières menstruations) :
   - déjà vaccinée pendant cette grossesse → aucune autre dose ;
   - 26 à 32 semaines → RDV ;
   - moins de 26 semaines → RDV à partir de la date des 26 semaines (calculée par l'app). Si elle insiste pour avant, expliquer ; si elle insiste encore → chef d'équipe ;
   - 33 semaines et plus → chef d'équipe.
3. Programme « Ma grossesse » : vérifier l'inscription, recommander l'inscription en ligne (11 langues).
4. RDV : service « Vaccination femmes enceintes », Gestion #2, site de masse ou CLSC.
5. Conclure : arriver 15 min avant, carte RAMQ ou PFSI.

### 4.3 Vaccination enfants 2 ans et plus (`ve`, 2 étapes)
- Valider l'identité de l'enfant et ouvrir son profil SI-PMI.
  - moins de 2 ans → chef d'équipe ;
  - registre complet → pas de RDV ;
  - un vaccin manque → RDV ;
  - aucun vaccin au registre et vacciné hors Québec → les parents apportent les preuves (en français ou en anglais) sans RDV ;
  - jamais vacciné → RDV.
- RDV : module 80036, PSL Côte-Saint-Luc ou Parc-Extension.

### 4.4 Vaccination adultes (`va`, 3 étapes)
- 18 ans et plus ayant manqué des vaccins du calendrier régulier du PIQ. Demander le NAM et ouvrir SI-PMI.
- Redirections : moins de 18 ans → Enfants ; COVID → vaccination de masse ; femme enceinte → dcaT ; rougeole → Rougeole.
- RDV : module 80036, « Vaccination générale adulte », Parc-Extension ou Côte-Saint-Luc.
- Dire que le RDV ne garantit pas une injection (évaluation de l'infirmière). Envoyer la confirmation par courriel et vérifier qu'elle est reçue.

### 4.5 Stagiaires et TCT (`tc`, 3 étapes)
- Motif : vaccination, TCT (test cutané à la tuberculine) ou les deux. Aucune restriction de territoire ; la centrale ne réserve que le 1er RDV.
- Clientèle admise : travailleurs de la santé, stagiaires et bénévoles en contact avec les patients ; refuges pour personnes itinérantes ; labos de mycobactériologie ; contacts d'un cas de tuberculose ou personnes référées par la santé publique. Sinon → guide Adultes.
- Symptômes de tuberculose (toux de 2 semaines, fièvre, crachats sanglants, sueurs nocturnes, perte d'appétit ou de poids, fatigue) → pas de RDV, 811 option 3.
- RDV : module 80036, « Vaccination – Étudiants et stagiaires du secteur de la santé ». **Jamais** « Lecture du TCT ».
  - Côte-Saint-Luc le mardi, Parc-Extension le lundi (le mardi si le lundi est férié) ;
  - lecture du TCT 48 h plus tard, RDV pris sur place.
- Apporter ses preuves vaccinales et le formulaire de l'école ou de l'employeur.

### 4.6 Campagne grippe / COVID / VRS (`cm`, 3 étapes, saison 2026-2027)
- Vaccin demandé : grippe, COVID, les deux, VRS adulte, VRS bébé (→ guide VRS bébés), pneumocoque ou zona (→ à demander à l'infirmière sur place).
- Critères déclarés : 65 ans et plus, CHSLD ou RI-SAPA, RPA, maladie chronique du PIQ, immunodéprimé ou dialysé, enceinte, personnel de la santé, région éloignée, vit avec une personne à risque ou est proche aidant (grippe seulement). VRS adulte : âge (18-59, 60-74, 75+), milieu de vie, greffe, dose antérieure.
- L'agent n'interprète pas la situation clinique : en cas de doute → infirmière.
- Admissible → RDV en PSL (module 12022, Vaccination de masse). Hors critères → pharmacie (payant).
- Toujours dire : « Un rendez-vous ne garantit pas la vaccination ; l'infirmière validera les critères de gratuité. »

### 4.7 Trajectoire pédiatrique (`tp`, 2 étapes)
L'app donne le lieu, le module, le service et la durée :

| Situation | Lieu | Module / service | Durée |
|---|---|---|---|
| Vaccin acheté en pharmacie (Bexsero, Prevnar-20…) | PSL seulement, jamais en CLSC | 80036 | 20 min |
| 2 mois | CLSC, toujours | 5031 ABCDaire – 2 mois (avec suivi de santé mentale parentale) | 1 h |
| Entre 2 et 6 mois, après l'ABCDaire 2 mois | PSL | 80036 Vaccination enfant – autre | 20 min |
| 4 ou 12 mois sans médecin de famille | CLSC | 5031 ABCDaire | 1 h |
| 4 ou 12 mois avec médecin de famille | PSL | 80036 | 20 min |
| 6 mois sans médecin de famille | CLSC | 5031 ABCDaire | 1 h |
| 6 mois **avec** médecin de famille | **non précisé : chef d'équipe** | | |
| Rougeole 6 à 11 mois (risque ou voyage) | PSL, vacciner dans les 72 h | 80036 | 20 min |
| Rattrapage 6-12 mois ou 12-18 mois | PSL | 80036 | 20 min |
| 18 mois et plus | CLSC | 5031 ABCDaire 18 mois + | 1 h |

Pour changer un RDV existant : garder le même module et le même service.

### 4.8 VRS bébés (`vb`, nirsévimab / Beyfortus, 3 étapes)
- Âge calculé **toujours au 30 septembre 2026**. Vérifier la date de naissance, le poids (5 kg ou plus) et les doses dans SI-PMI : aucune dose pour la saison ni entre le 1er avril et le 18 mai 2026. Certains bébés sont enregistrés sous le nom de la mère (« BB de … ») : chercher par NAM.
  - dose déjà reçue → aucune autre ;
  - moins de 6 mois → RDV en PSL ou CLSC ;
  - 6 à 8 mois → RDV seulement si prématuré (moins de 37 semaines), communauté éloignée ou condition de vulnérabilité ; sinon pas admissible ;
  - 8 à 19 mois → RDV seulement si 5 kg ou plus avec une condition (dysplasie bronchopulmonaire, maladie pulmonaire chronique, cardiopathie, hypertension pulmonaire, trisomie 21, fibrose kystique, trouble d'évacuation des sécrétions, greffe) ; prématurité seule → pas admissible.
- L'agent ne pose pas de diagnostic. Parent incertain ou SI-PMI discordant → chef d'équipe.
- RDV : Gestion #2 ; PSL (aucune restriction de territoire) ou CLSC (territoire du Centre-Ouest seulement). Commentaires obligatoires.

### 4.9 Zona (`zo`, Shingrix, 2 étapes)
- **Gratuit : 71 ans et plus** (Québec.ca, élargissement aux 71-74 ans en janvier 2026), ou 18 ans et plus immunodéprimé.
  - 50 à 70 ans non immunodéprimé → recommandé mais payant, en pharmacie ;
  - moins de 18 ans → pas admissible.
- Ne pas questionner le client sur sa santé. S'il hésite sur l'immunodépression → prendre le RDV, il sera évalué sur place.
- Intervalles :
  - 2e dose de Shingrix : 10 mois après la 1re (2 mois si immunodéprimé) ;
  - après le Zostavax ou un épisode de zona : 12 mois. Trop tôt → l'app calcule la date de rappel.
- RDV : module 12022 « Vaccin contre Zona », Gestion 2, sans NAM, jamais sans rendez-vous. Carré Décarie ou Parc-Extension. Ne pas prendre les plages à cadenas rouge.

### 4.10 Prélèvements (`pr`, 3 étapes)
- Raison de l'appel :
  - résultats → nous n'y avons pas accès, voir le médecin ou le prescripteur ;
  - question clinique → infirmière ou médecin ;
  - STAT ou urgent → transférer au chef d'équipe (RDV dans les 24 à 72 h) ;
  - test génétique → non offert.
- Conditions pour un RDV :
  - carte RAMQ ou PFSI (sinon hôpital ou clinique privée via Clic Santé) ;
  - 14 ans et plus (13 ans et moins → CHU Sainte-Justine, Hôpital de Montréal pour enfants, CUSM, Cité de la Santé de Laval) ;
  - ambulatoire (sinon programme SAPA, par son médecin) ;
  - requête papier émise au Québec, avec les coordonnées du patient et la signature du prescripteur.
- RDV : module 8088 (ou 8137), un seul RDV pour tous les tests, aucune restriction de territoire.
  - à jeun, cortisol, hyperglycémie provoquée chez la femme enceinte : avant 9 h ;
  - **jamais** « Prélèvement Interne-Urgent » ni « Corridor de service GMF ».
- Horaires des sites :

  | Site | Horaire |
  |---|---|
  | Benny Farm | lundi au vendredi, 7 h 30 – 11 h |
  | René-Cassin | mardi et jeudi, 7 h 30 – 15 h |
  | CLSC Métro | lundi au vendredi, 7 h 30 – 15 h 30 (confirmé sur le site du CIUSSS) |
  | PSL Côte-Saint-Luc | lundi au vendredi, 8 h – 15 h, et samedi, 9 h – 16 h |
  | PSL Parc-Extension | lundi au vendredi, 8 h 30 – 16 h |
- Situations : patient frustré → proposer un autre centre ; très en colère → chef d'équipe ; inquiet ou sujet aux chocs vagaux → le dire à l'infirmière ; Coumadin → le mentionner à l'infirmière.
- Règles : requêtes papier seulement, aucun échantillon de clinique externe, plus de 15 min de retard = nouveau RDV, cartes d'autres provinces refusées en CLSC (acceptées dans les hôpitaux).

### 4.11 Strep A (`sa`, 3 étapes)
- Âge dans Panorama. Moins de 3 ans → pas admissible. **Mal de gorge obligatoire.**
- Autres symptômes : douleur en avalant, fièvre, ganglions, dépôts blanchâtres, nausées, ou personne référée par le 811.
- RDV : module 10174 DLM, « Dépistage streptocoque A ». Un seul centre : centre de dépistage de Parc-Extension, 7085 Hutchison (entrée par l'avenue du Parc, derrière le CLSC). Du lundi au samedi, 8 h 30 à 16 h 30.
- Consignes en français et en anglais. Un enfant de moins de 14 ans doit être accompagné d'un parent ou tuteur.

### 4.12 Dépistage COVID (`cv`, 3 étapes)
- Triage :
  - employé du CIUSSS Centre-Ouest → Santé et Sécurité du Travail, 514 731-7343 ;
  - travailleur de la santé d'un autre établissement → RDV ;
  - procédure à l'HGJ → pas de RDV, transférer au chef d'équipe ;
  - sinon, clientèles prioritaires du MSSS. Pas admissible → test rapide en pharmacie.
- RDV : module 10174, « Dépistage COVID – Clientèles prioritaires », centre de Parc-Extension, tous les jours de 8 h 30 à 16 h 30. **Jamais** à Légaré ni à l'HGJ.
- Informations identiques à Panorama. Résultat par courriel ou par téléphone. Accès : métro Parc, autobus 80 et 93.

### 4.13 Cancer colorectal (`cr`, 3 étapes)
- Admissible : 50 à 74 ans, ou 49 ans et moins avec un cancer colorectal dans la famille.
  - dernier RSOSi (FIT) il y a moins de 2 ans → pas admissible ;
  - dernière coloscopie il y a moins de 5 ans → pas admissible.
- RDV : module 10174, « Dépistage du cancer colorectal », Côte-Saint-Luc ou Parc-Extension, du lundi au samedi, 10 h à 17 h.

### 4.14 Dépistage VPH (`vp`, 2 étapes)
- 25 à 65 ans, et personne qui a un col de l'utérus, peu importe l'identité de genre (rester inclusif).
- RDV : module 10174, CLSC Métro au 3e étage, **le mardi seulement**. Sans RDV possible, mais insister sur le RDV. Numéro dédié : 514 734-9911.
- Case « CLSC Métro fermé (incendie) » → service relocalisé au PSL Côte-Saint-Luc, au rez-de-chaussée.

### 4.15 Maladies chroniques (`ch`, 4 étapes)
- Dépistage gratuit du diabète de type 2 et évaluation cardiovasculaire, pour les patients d'un GMF : Novomed, Cité Médicale ou Queen Elizabeth. Autre GMF → vérifier avec la coordination.
- Tous les critères doivent être respectés :
  - 18 à 75 ans ;
  - aucun diagnostic (prédiabète, diabète, cholestérol, maladie cardiovasculaire, hypertension, insuffisance rénale sévère) ;
  - aucun médicament pour ces conditions ;
  - pas enceinte, ni accouchée il y a moins de 6 semaines.
- Lieu selon l'adresse : CSL, NDG, Montréal-Ouest → PSL Côte-Saint-Luc ; CDN, Métro, Parc-Extension → PSL Parc-Extension. Priorité aux plages du jour même ou du lendemain.
- Clic Santé : module 10174 DLM, « Dépistage diabète type 2 et évaluation cardiovasculaire » ; le GMF va dans les commentaires.
- RDV d'une heure avec une infirmière, qui peut mener à une prise de sang. Pas besoin d'être à jeun.

---

## 5. Répertoire téléphonique
- Groupes : lignes principales du CIUSSS Centre-Ouest (DLM 514 731-8531 et ses options), adresses des CLSC, CVD, dépistage VPH, centres pédiatriques de prélèvement, PDS d'autres régions, etc.
- Chaque entrée : `{n: nom, t: téléphone, d: détails, a: adresse, w: 1 si « Ne pas donner aux usagers », m: 1 si noté à la main}`.
- Les entrées `w:1` (5 entrées, dont le guichet d'accès SAPA-SAD) existent dans l'app en ligne, mais sont retirées du dépôt public par `sanitize.py`.
- Numéros vérifiés en ligne : 514 852-7780 (centrale de RDV, vaccins tétanos, dcaT et 0-17 ans) ; 1-844-448-6826 (prélèvements, Montérégie).

---

## 6. Glossaire
| Terme | Sens |
|---|---|
| CIUSSS | Centre intégré universitaire de santé et de services sociaux |
| CLSC | Centre local de services communautaires |
| PSL | Point de service local (Côte-Saint-Luc, Parc-Extension) |
| GMF | Groupe de médecine familiale |
| DLM | Direction (module Clic Santé 10174) |
| SI-PMI / Panorama | Registre de vaccination du Québec |
| RAMQ / NAM | Régie de l'assurance maladie / numéro d'assurance maladie |
| PFSI | Programme fédéral de santé intérimaire |
| PIQ | Protocole d'immunisation du Québec |
| Clic Santé | Système de prise de RDV (modules, services, accès « Gestion #2 ») |
| ABCDaire | Suivi pédiatrique en CLSC |
| TCT | Test cutané à la tuberculine |
| RSOSi | Recherche de sang occulte dans les selles (test FIT) |
| SAPA / SAD | Soutien à l'autonomie des personnes âgées / soutien à domicile |
| DRSP | Direction régionale de santé publique |
| HGJ | Hôpital général juif |

---

## 7. Points ouverts
- « 6 mois avec médecin de famille » (Trajectoire pédiatrique) : service non précisé sur la feuille → à faire confirmer par le chef d'équipe.
- Dépistage VPH le mardi au CLSC Métro, 3e étage : non confirmé en ligne depuis l'incendie.
- Lignes PDS manuscrites de Laval, Lanaudière et Montérégie-Ouest : non trouvées en ligne.
- Le jeu 3D est mieux adapté à la **formation** des nouveaux agents ; la vue classique est plus rapide en plein appel.
- Idées non commencées : jeux sur mesure par chapitre (train miniature avec aiguillages pour la pédiatrie, tape-taupe des mardis pour le VPH, balance de pouponnière pour le VRS bébés, etc.) et un mode Entraînement avec des cas simulés et un score.

---

## 8. Comment demander une modification
```
Demande : [ce que je veux]
- Ne touche pas à la logique (REG, st, upd, verdict) sauf si ma demande porte sur une règle ; dans ce cas, cite la source officielle avec le lien.
- Garde le fichier unique et autonome.
- Utilise une librairie ou un asset libre existant si possible (lien et licence).
- Donne seulement les modifications précises (chercher/remplacer).
- Explique comment tester sur téléphone et sur ordinateur.
- Termine par un message de commit en français.
```
