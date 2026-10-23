# Version française du site : style et glossaire

Les pages françaises sont dans `fr/`, avec les mêmes noms que les pages anglaises
(`fr/index.html`, `fr/projects/foehn.html`…). Elles sont créées par `tools/i18n_skeleton.py`
avec le texte anglais en place ; on remplace ce texte par le français, rien d'autre.
Après chaque page : `python3 tools/i18n_skeleton.py check` (balises, liens, ancres, scripts).

## Ton

- Français naturel, écrit par un Français : on traduit le sens, pas les mots. Phrases courtes.
- Humble et factuel : pas de superlatifs ni de formules promotionnelles qui ne sont pas dans
  l'anglais. Quand l'anglais en contient une, on la rend fidèlement, sans l'amplifier.
- Même personne que l'anglais : « je » pour l'auteur (« I »), « nous » pour le travail d'équipe (« we »).
  Le lecteur est vouvoyé (« l'air que vous respirez »).
- Mêmes faits, mêmes chiffres, mêmes liens, même ordre : rien n'est ajouté, rien n'est retiré.
  Aucun projet, produit ou prototype qui n'est pas nommé sur la page anglaise.
- La bio garde ses liens vers AMC-Lahti, Michael Boy et Zhi-Song Liu.
- Les co-auteurs restent cités comme dans l'anglais.

## Ce qu'on traduit

Le texte visible, et aussi : `<title>`, `meta description`, `og:title`, `og:description`,
`og:image:alt`, les `alt`, `aria-label`, `title`, `figcaption`, légendes de galerie, le lien
d'évitement (`skip-link`), et dans le JSON-LD les valeurs de texte `jobTitle`, `name` et
`description` des vidéos.

## Ce qui reste tel quel

- Noms de personnes, de modèles et de logiciels : Foehn, FLEXGREEN, TopoFlow, CRAN-PM, CranPM Studio,
  AQ-Net, cDESP, LingoRob, NAO, CAMS, ERA5, GHAP, OpenAQ, CAQRA, Aurora, LUMI, LSTM, ViT, CUDA, ROCm,
  PyTorch, TensorFlow, Flask, Django, Jinja2, Gradio, Excel, VBA, Voggt…
- Titres d'articles (`.pub-title`, `headline` du JSON-LD, titres cités dans les actualités), noms de
  revues et de conférences (*npj Climate and Atmospheric Science*, SCIA, Springer LNCS, arXiv,
  IAC 2026, EAC, Boya Forum on Environmental Research), intitulés officiels des cours
  (`BM40A1601 · Foundations of Artificial Intelligence and Machine Learning`) et de l'école d'été
  (*Application of AI / ML techniques in Atmospheric Science*).
- Les blocs BibTeX (`<pre>`) en entier, les URL, l'adresse e-mail, les numéros arXiv, les DOI,
  les codes de cours, `og:site_name`, les noms d'organisations du JSON-LD.
- Le balisage : balises, classes, `id`, ancres (`#about`, `#y2026`, `#series`…), `href`, `src`,
  attributs `data-*` (identifiants YouTube, `data-doi`, `data-until`).
- Les lignes gérées par le script, à ne pas modifier à la main : le sélecteur de langue
  (`<span class="lang-switch">`), `canonical`, `og:url`, `og:locale`, les `hreflang`, et `url` /
  `inLanguage` du JSON-LD. `site.js` et `citations.js` suivent déjà `<html lang>`.
- Quand un élément entier reste en anglais (titre d'article, intitulé de cours), lui ajouter
  `lang="en"` (par ex. `<p class="pub-title" lang="en">`) ; inutile pour un simple nom propre.

## Noms d'institutions et de lieux

| Anglais | Français |
|---|---|
| LUT University | LUT University |
| Atmospheric Modelling Centre (AMC-Lahti) | Atmospheric Modelling Centre (AMC-Lahti) |
| INAR, University of Helsinki | INAR, Université d'Helsinki |
| University of Helsinki, Lahti campus | Université d'Helsinki, campus de Lahti |
| INRIA Bordeaux, Mnemosyne team | INRIA Bordeaux, équipe Mnemosyne |
| ARCHES team at Inria | équipe ARCHES d'Inria |
| Technical University of Munich (TUM) | Université technique de Munich (TUM) |
| Peking University | Université de Pékin |
| Istanbul Technical University | Université technique d'Istanbul |
| École Polytechnique | École polytechnique |
| Cabinet of the French Presidency | cabinet de la présidence de la République |
| EEA (European Environment Agency) | AEE (Agence européenne pour l'environnement) |
| Finland / west France | Finlande / ouest de la France |
| Beijing, Xi'an, Reykjavík, Lecce | Pékin, Xi'an, Reykjavík, Lecce |
| Sichuan Basin, Po Valley, Indo-Gangetic Plain, Northern China | bassin du Sichuan, plaine du Pô, plaine indo-gangétique, nord de la Chine |

## Interface (identique sur toutes les pages)

| Anglais | Français |
|---|---|
| About · Research · Videos · Publications · Contact (menu) | À propos · Recherche · Vidéos · Publications · Contact |
| Skip to main content | Aller au contenu principal |
| `aria-label="Main"` (menu) · `"Menu"` | `"Menu principal"` · `"Menu"` |
| Explore · Elsewhere · Contact (pied de page) | Explorer · Ailleurs · Contact |
| Teaching neural networks how the atmosphere flows. | Apprendre aux réseaux de neurones comment circule l'atmosphère. |
| © 2026 Ammar Kheder · LUT University · Atmospheric Modelling Centre · Lahti, Finland | © 2026 Ammar Kheder · LUT University · Atmospheric Modelling Centre · Lahti, Finlande |
| X, by Ammar Kheder (titres) | X, par Ammar Kheder |
| Ammar Kheder, forecasting air pollution · LUT University | Ammar Kheder, prévision de la pollution de l'air · LUT University |
| Research and projects · News archive · Teaching · Videos | Recherche et projets · Archives des actualités · Enseignement · Vidéos |
| Page not found · Error · 404 | Page introuvable · Erreur · 404 |
| This address does not exist, or the page has moved. | Cette adresse n'existe pas, ou la page a été déplacée. |
| Where to go next · Home · Projects · News archive | Pour continuer · Accueil · Projets · Archives des actualités |
| ← Back to home · ← All projects · ← Back to all projects | ← Retour à l'accueil · ← Tous les projets · ← Retour à tous les projets |
| Next: X → · ← Previous: X | Suivant : X → · ← Précédent : X |
| `aria-label="Other projects"` · `"Years"` · `"Videos"` | `"Autres projets"` · `"Années"` · `"Vidéos"` |
| This page has moved to videos.html. (talks.html) | Cette page a été déplacée vers videos.html. |

## Accueil

| Anglais | Français |
|---|---|
| Doctoral Researcher in Computational Engineering | Doctorant en ingénierie computationnelle |
| PhD student working on air-quality forecasting with physics and machine learning. | Doctorant, je travaille sur la prévision de la qualité de l'air, à l'aide de la physique et de l'apprentissage automatique. |
| Read the Foehn preprint → · Watch the series | Lire la prépublication de Foehn → · Voir la série |
| Tap: my portrait, illustrated by Mitsuhiro Arita | Touchez : mon portrait, illustré par Mitsuhiro Arita |
| Tap or hover to reveal the Arita illustration. Tap again to flip back. | Touchez ou survolez l'image pour voir l'illustration d'Arita. Touchez à nouveau pour revenir. |
| About · Experience · Education · Talks and visits | À propos · Expérience · Formation · Exposés et visites |
| supervised by Prof. Michael Boy and Assoc. Prof. Zhi-Song Liu | sous la direction du Pr Michael Boy et de Zhi-Song Liu, professeur associé |
| Topics: · Beyond research: · Languages: | Thèmes : · En dehors de la recherche : · Langues : |
| French and Arabic (native), English (fluent). | français et arabe (langues maternelles), anglais (courant). |
| Junior Researcher & Teaching Assistant | Chercheur junior et assistant d'enseignement |
| CEO, Wabel Group · AI services and web development | CEO, Wabel Group · services d'IA et développement web |
| Research Engineer (Apprenticeship) | Ingénieur de recherche (alternance) |
| Volunteer Firefighter | Sapeur-pompier volontaire |
| Ph.D. Computational Engineering | Doctorat en ingénierie computationnelle |
| MSc Engineering, Big Data & AI · with apprenticeship at INRIA Bordeaux | Diplôme d'ingénieur, Big Data et IA · en alternance à l'INRIA Bordeaux |
| Bachelor, Data Science · Statistics, Big Data, Business Intelligence | Bachelor, science des données · statistique, big data, informatique décisionnelle |
| aeronautics initiation (BIA) | brevet d'initiation aéronautique (BIA) |
| Latest preprint · October 2026 · with … | Dernière prépublication · octobre 2026 · avec … |
| Explore the 1 km forecasts · Case study · Code | Explorer les prévisions à 1 km · Étude de cas · Code |
| Where was the air you breathe? Try it → | Où était l'air que vous respirez ? Essayez → |
| Watch (section) · All videos → | À voir · Toutes les vidéos → |
| Research · Read the case study → · All research and projects → | Recherche · Lire l'étude de cas → · Toute la recherche et les projets → |
| Publications · Cite · All publications on Google Scholar → | Publications · Citer · Toutes les publications sur Google Scholar → |
| Preprint · Journal · Conference (type) · Lead author | Prépublication · Revue · Conférence · Premier auteur |
| News · New (badge) · Earlier in 2026 (3) · All news → | Actualités · Nouveau · Plus tôt en 2026 (3) · Toutes les actualités → |

## Projets, vidéos, actualités

| Anglais | Français |
|---|---|
| Key ideas · Visualisations · Figures · Gallery · Demo | Idées clés · Visualisations · Figures · Galerie · Démo |
| Resources · Credits · Read more · Repository | Ressources · Crédits · Pour aller plus loin · Dépôt |
| Authors · Venue · Compute · Affiliation · Status · Period · Role · Supervision | Auteurs · Publication · Calcul · Affiliation · Statut · Période · Rôle · Encadrement |
| Code on GitHub · Project website · arXiv preprint · Nature paper | Code sur GitHub · Site du projet · Prépublication arXiv · Article (Nature) |
| Live demo · Open the live demo → · Interactive forecasts | Démo en ligne · Ouvrir la démo en ligne → · Prévisions interactives |
| Galton Board in Excel | Planche de Galton sous Excel |
| Pokémon Card Detection · Pokémon Robot Auction | Détection de cartes Pokémon · Enchères Pokémon avec un robot |
| BIA Aeronautical Initiation / Programme | Brevet d'initiation aéronautique (BIA) |
| Foehn in 8 minutes · Foehn from A to Z · What's in the air? | Foehn en 8 minutes · Foehn de A à Z · Qu'y a-t-il dans l'air ? |
| Playlist on YouTube · Full film, 43:58 · Playlist · 12 episodes + full film | Playlist sur YouTube · Film complet, 43:58 · Playlist · 12 épisodes + film complet |
| Audio in 31 languages · subtitles in 33 (Settings > Audio track) | Audio en 31 langues · sous-titres en 33 (Paramètres > Piste audio) |
| `aria-label="Play: TITLE (7:46)"` | `aria-label="Lire : TITRE (7:46)"` |
| Archive · chronological · Jump to | Archives · ordre chronologique · Aller à |
| #PUB #TALK #VISIT #TEACH #EVENT #PROJECT #MILESTONE | #PUB #EXPOSÉ #VISITE #ENSEIGNEMENT #ÉVÉNEMENT #PROJET #ÉTAPE |

## Vocabulaire scientifique

| Anglais | Français |
|---|---|
| air quality · air pollution | qualité de l'air · pollution de l'air |
| forecast (n.) · to forecast · forecasting | prévision · prévoir · prévision |
| the operational forecast | la prévision opérationnelle |
| probabilistic forecast · ensemble · calibrated | prévision probabiliste · ensemble · calibré |
| one day ahead · up to a week ahead · lead time | à un jour d'échéance (J+1) · jusqu'à une semaine à l'avance · échéance |
| retrospective forecasts (of 2022) | prévisions rétrospectives (sur 2022) |
| reanalysis · station(s) | réanalyse · station(s) de mesure |
| fine particles · PM<sub>2.5</sub> | particules fines · PM<sub>2.5</sub> (inchangé) |
| all inhabited land | toutes les terres habitées |
| machine learning · deep learning | apprentissage automatique · apprentissage profond |
| generative model · generator | modèle génératif · générateur |
| flow matching · Vision Transformer · attention · patch | flow matching · Vision Transformer · attention · patch |
| physics-informed neural networks · physics-aware / physics-guided | réseaux de neurones informés par la physique · guidé par la physique |
| Lagrangian transport · the air traced backwards | transport lagrangien · l'air remonté dans le temps |
| terrain · elevation · topographic blocking | relief · altitude · blocage par le relief |
| zero-shot transfer | transfert zero-shot (sans réentraînement) |
| high-performance computing · supercomputer · GPUs | calcul haute performance · supercalculateur · GPU (invariable) |
| large-scale distributed training | entraînement distribué à grande échelle |
| dataset · baseline · benchmark | jeu de données · modèle de référence · comparaison |
| haze (Beijing) · wildfire smoke · Saharan dust | épisode de pollution · fumées d'incendies · poussières sahariennes |
| preprint · paper · journal · lead author | prépublication · article · revue · premier auteur |
| talk · invited talk · speed talk · poster | exposé · exposé invité · présentation éclair · poster |
| research visit / stay | séjour de recherche |
| teaching assistant · lab sessions · summer school | assistant d'enseignement · travaux pratiques · école d'été |
| case study (page de projet) | étude de cas |

## Nombres, dates, typographie

- Virgule décimale : 9,71 µg/m³ ; 1,8 s. Milliers séparés par une espace insécable : 1 024 GPU ;
  5 954 stations ; 6 324 stations ; 29 millions de pixels. Pourcentages : −17 % ; 71–80 %.
- « 3 in 4 » → « 3 sur 4 » ; « three stations in four » → « trois stations sur quatre » ;
  « 487× faster » → « 487 fois plus rapide » ; « 2y 8mo » → « 2 ans et 8 mois ».
- Inchangés : années, numéros de version (v1.0, Python 3.7+), numéros arXiv (2610.25941), DOI,
  codes de cours, durées de vidéo (7:46, 43:58, 3 h 22), le signe moins −, les unités (µg/m³, km).
- Dates : « 23 oct. 2026 », « oct. 2026 », « 1er sept. » ; en toutes lettres dans le texte courant
  (« le 24 avril 2026 », « du 7 janvier au 17 avril 2026 »). Abréviations : janv., févr., mars,
  avr., mai, juin, juil., août, sept., oct., nov., déc. Mois en minuscule, sauf en début de titre
  (« Octobre 2026 »). Intervalles : « 5–6 mai », « 11–15 août 2025 ».
  « 2024 – now » → « depuis 2024 » ; « October 2024 to present » → « depuis octobre 2024 » ;
  « Fall 2024 » → « automne 2024 » ; « 5 PM → 8 PM Paris » → « 17 h → 20 h, heure de Paris ».
- Espaces : une espace insécable `&nbsp;` avant `: ; ! ?` et `%`, à l'intérieur des guillemets
  « », entre un nombre et son unité (1&nbsp;km, 7&nbsp;jours) et dans les milliers (5&nbsp;954).
  Toujours `&nbsp;` (U+00A0), jamais l'espace fine U+202F ni `&thinsp;` : les polices dessinées du
  site (Cabin Sketch, Neucha) n'ont pas ce caractère, il serait dessiné avec une autre police.
- Apostrophe typographique ’ ; guillemets « » (et “ ” à l'intérieur) ; tiret demi-cadratin –
  pour les intervalles, sans espaces ; majuscules accentuées (À propos, État).
- Titres : majuscule au premier mot et aux noms propres seulement (« Idées clés »).
- Les accents et « œ » sont dans les polices du site ; « Ÿ » n'y est pas (inutile ici).
