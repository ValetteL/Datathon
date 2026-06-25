# Frontend — Datathon CNC × Ultia

Interface de démonstration du pipeline multi-agents d'analyse de crise virale.

## Stack

- React 18
- Vite
- TailwindCSS
- Axios

## Installation

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install axios tailwindcss @tailwindcss/vite
npm run dev
```

## Configuration

```bash
# .env
VITE_API_URL=http://localhost:8000
```

---

## Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── VeilleResult.jsx
│   │   ├── HumanGate.jsx
│   │   ├── StrategeResult.jsx
│   │   ├── RedacteurResult.jsx
│   │   ├── MockBadge.jsx
│   │   ├── AlertBadge.jsx
│   │   ├── PeaksTable.jsx
│   │   ├── StepIndicator.jsx
│   │   └── Loader.jsx
│   ├── pages/
│   │   └── Pipeline.jsx
│   ├── api/
│   │   └── client.js
│   ├── hooks/
│   │   └── usePipeline.js
│   └── App.jsx
├── public/
├── .env
├── package.json
└── README.md
```

---

## États globaux du pipeline

```
idle
  → loading_veille
    → veille_done
      → awaiting_human
        → loading_stratege
          → stratege_done
            → loading_redacteur
              → complete
        → rejected
```

---

## User Stories

---

### US-01 — Lancer l'analyse

**En tant qu'** opérateur de la cellule de crise,
**je veux** lancer l'analyse du corpus en un clic,
**afin de** déclencher le pipeline sans manipuler le code.

**Tâches**

- Créer la page `Pipeline.jsx` avec un bouton "Lancer l'analyse"
- Appeler `POST /analyse/veille` au clic
- Passer l'état global à `loading_veille` pendant l'appel
- Stocker le `run_id` retourné dans le state global
- Passer à `veille_done` à la réception de la réponse

**Critères d'acceptance**

- Le bouton est désactivé pendant le chargement
- Un loader s'affiche pendant l'appel API
- Le `run_id` est bien stocké pour les appels suivants
- En cas d'erreur API, un message d'erreur s'affiche

**DOD**

- [ ] Bouton fonctionnel et désactivé pendant le loading
- [ ] Loader visible
- [ ] `run_id` stocké dans le state
- [ ] Gestion d'erreur affichée à l'utilisateur
- [ ] Pas de double appel si on clique deux fois

---

### US-02 — Afficher les résultats de la Veille

**En tant qu'** opérateur,
**je veux** voir les résultats de l'AgentVeille clairement présentés,
**afin de** comprendre l'état de la crise avant de décider.

**Tâches**

- Créer `VeilleResult.jsx` qui reçoit les données de la Veille en props
- Créer `AlertBadge.jsx` : badge coloré selon le niveau d'alerte
  - `low` → vert
  - `medium` → jaune
  - `high` → orange
  - `critical` → rouge
- Afficher le résumé textuel de la Veille
- Créer `PeaksTable.jsx` : tableau des pics (date, volume, top shares)
- Afficher les métriques clés : tweets viraux, pic journalier, pic horaire

**Critères d'acceptance**

- Le badge de niveau est bien coloré selon la valeur
- Le tableau des pics est trié par volume décroissant
- Les métriques clés sont lisibles en un coup d'œil
- Le composant s'affiche uniquement quand `veille_done`

**DOD**

- [ ] `AlertBadge` affiche la bonne couleur pour chaque niveau
- [ ] `PeaksTable` affiche toutes les colonnes avec les bonnes valeurs
- [ ] Métriques clés visibles (tweets viraux, pic journalier)
- [ ] Résumé textuel affiché
- [ ] Composant invisible tant que la Veille n'a pas répondu

---

### US-03 — Afficher le badge Mock

**En tant qu'** opérateur,
**je veux** savoir si les narratifs sont simulés ou réels,
**afin de** ne pas interpréter des résultats non fiables comme définitifs.

**Tâches**

- Créer `MockBadge.jsx` : bandeau jaune avec icône ⚠
- L'afficher si `narratives` est mocké (flag retourné par le backend)
- L'afficher en haut de page, avant les résultats

**Critères d'acceptance**

- Le badge est visible et non ambigu
- Il disparaît si les narratifs sont réels

**DOD**

- [ ] Badge affiché si `is_mock: true` dans la réponse backend
- [ ] Badge absent si `is_mock: false`
- [ ] Texte clair : "Narratifs simulés — AgentAnalyste non branché"

---

### US-04 — Valider ou rejeter au HumanGate

**En tant qu'** opérateur,
**je veux** valider ou rejeter l'analyse avant la génération de réponses,
**afin de** garder le contrôle humain sur le pipeline.

**Tâches**

- Créer `HumanGate.jsx` avec deux boutons : Valider (vert) / Rejeter (rouge)
- Au clic Valider : appeler `POST /analyse/stratege` avec `human_approved: true`
- Au clic Rejeter : passer l'état à `rejected`, afficher un message de fin
- Désactiver les deux boutons pendant le chargement

**Critères d'acceptance**

- Les deux boutons sont clairement différenciés visuellement
- Le pipeline s'arrête proprement si rejeté
- Un message de confirmation s'affiche après rejet
- Les boutons sont désactivés après le choix

**DOD**

- [ ] Bouton Valider déclenche `POST /analyse/stratege`
- [ ] Bouton Rejeter arrête le pipeline et affiche un message
- [ ] Les boutons sont disabled après le choix
- [ ] Le composant n'est visible qu'à l'état `awaiting_human`

---

### US-05 — Afficher les options du Stratège

**En tant qu'** opérateur,
**je veux** voir les 3 options de réponse proposées par l'AgentStratège,
**afin de** choisir la bonne stratégie de communication.

**Tâches**

- Créer `StrategeResult.jsx` qui affiche 3 cards
- Chaque card affiche : titre, tonalité, description, liste des risques
- Badge ⭐ sur la card recommandée
- Couleur de la card selon la tonalité :
  - `prudent` → bleu
  - `equilibre` → jaune
  - `assertif` → rouge

**Critères d'acceptance**

- Les 3 cards sont affichées côte à côte sur desktop
- La card recommandée est visuellement mise en avant
- Les risques sont lisibles (liste à puces)
- Le composant s'affiche uniquement à `stratege_done`

**DOD**

- [ ] 3 cards affichées avec les bonnes couleurs
- [ ] Badge ⭐ sur `option_recommandee`
- [ ] Risques affichés en liste
- [ ] Justification de la recommandation affichée en bas
- [ ] Composant invisible tant que `stratege_done` non atteint

---

### US-06 — Afficher les drafts du Rédacteur

**En tant qu'** opérateur,
**je veux** voir les 3 versions de communiqué rédigées par l'AgentRédacteur,
**afin de** choisir et adapter le message à publier.

**Tâches**

- Créer `RedacteurResult.jsx` qui affiche 3 cards de draft
- Chaque card affiche : titre, tonalité, corps du texte, call to action
- Badge ⭐ sur la version recommandée
- Bouton "Copier" sur chaque card

**Critères d'acceptance**

- Les 3 versions sont lisibles et bien structurées
- Le bouton "Copier" copie le corps du texte dans le presse-papier
- La version recommandée est mise en avant
- Le composant s'affiche uniquement à `complete`

**DOD**

- [ ] 3 cards affichées avec titre, corps, call to action
- [ ] Bouton "Copier" fonctionnel (clipboard API)
- [ ] Badge ⭐ sur la version recommandée
- [ ] Composant invisible tant que `complete` non atteint

---

### US-07 — Suivre la progression du pipeline

**En tant qu'** opérateur,
**je veux** voir où en est le pipeline à tout moment,
**afin de** comprendre ce qui s'est passé et ce qui reste à faire.

**Tâches**

- Créer `StepIndicator.jsx` : barre de progression avec 4 étapes
  - Veille / HumanGate / Stratège / Rédacteur
- Chaque étape a 3 états : en attente (gris) / en cours (bleu animé) / terminé (vert)
- La barre est sticky en haut de page

**Critères d'acceptance**

- La barre est toujours visible pendant le pipeline
- L'étape en cours est clairement indiquée
- Les étapes terminées sont marquées ✓

**DOD**

- [ ] 4 étapes affichées dans l'ordre
- [ ] État de chaque étape synchronisé avec l'état global
- [ ] Animation sur l'étape en cours
- [ ] Sticky en haut de page

---

### US-08 — Gestion des erreurs API

**En tant qu'** opérateur,
**je veux** être informé quand une étape du pipeline échoue,
**afin de** comprendre ce qui s'est passé sans que l'interface se bloque.

**Tâches**

- Intercepter les erreurs Axios dans `client.js`
- Afficher un message d'erreur contextuel (quelle étape a échoué)
- Proposer un bouton "Réessayer" sur l'étape en erreur

**Critères d'acceptance**

- L'interface ne se bloque pas sur une erreur
- Le message d'erreur indique quelle étape a échoué
- Le bouton Réessayer relance uniquement l'étape en erreur

**DOD**

- [ ] Erreurs Axios interceptées globalement
- [ ] Message d'erreur affiché avec le contexte
- [ ] Bouton Réessayer fonctionnel
- [ ] L'état global revient à l'étape précédente en cas d'erreur

---

### US-09 — Reprendre une session existante

**En tant qu'** opérateur,
**je veux** voir la liste des sessions précédentes et en sélectionner une,
**afin de** revoir les résultats sans relancer le pipeline.

**Tâches**

- Appeler `GET /sessions` au chargement de la page
- Afficher la liste sous le bouton "Lancer l'analyse"
- Chaque item affiche : run_id (court), status, alert_level, created_at
- Au clic sur une session : appeler `GET /sessions/{run_id}`
- Restaurer l'état du front depuis la réponse

**Critères d'acceptance**

- La liste est visible dès le chargement
- Le statut est lisible (badge coloré)
- Au clic, le pipeline reprend au bon état

**DOD**

- [ ] `GET /sessions` appelé au montage du composant
- [ ] Liste affichée avec status coloré
- [ ] Clic sur une session restaure l'état global
- [ ] Pipeline reprend à la bonne étape selon le status
- [ ] Liste vide si aucune session disponible

---

## Ordre d'implémentation recommandé

1. `client.js` — appels API
2. `usePipeline.js` — state machine et logique
3. `StepIndicator.jsx` — navigation visuelle
4. `Loader.jsx` — composant réutilisable
5. `Pipeline.jsx` + bouton de lancement (US-01)
6. `AlertBadge.jsx` + `PeaksTable.jsx` + `VeilleResult.jsx` (US-02)
7. `MockBadge.jsx` (US-03)
8. `HumanGate.jsx` (US-04)
9. `StrategeResult.jsx` (US-05)
10. `RedacteurResult.jsx` (US-06)
11. Gestion des erreurs (US-08)
