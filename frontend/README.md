# Frontend — Datathon CNC × Ultia

Interface de démonstration du pipeline multi-agents d'analyse de crise virale.

## Stack

React 19 · TypeScript · Vite · TailwindCSS v4 · Axios · pnpm

## Démarrage

```bash
pnpm install
pnpm dev       # → http://localhost:5173
```

```bash
# .env (optionnel — défaut : http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

```bash
pnpm build     # build de production
pnpm preview   # prévisualisation du build
```

---

## Architecture

```
src/
├── api/
│   ├── client.ts           # Appels Axios · PipelineApiError
│   └── types.ts            # Types partagés (AnalysteResultData, VeilleResultData…)
├── components/
│   ├── AlertBadge.tsx      # Badge coloré low/medium/high/critical (prop compact pour en-têtes)
│   ├── AnalysteResult.tsx  # Bar chart répartition des narratifs
│   ├── CollapsibleCard.tsx # Carte repliable — wrapper des étapes passées
│   ├── ErrorBanner.tsx     # Bandeau d'erreur contextuel + bouton Réessayer
│   ├── HumanGate.tsx       # Validation humaine : Valider / Rejeter
│   ├── Loader.tsx          # Spinner animé + label
│   ├── PeaksTable.tsx      # Tableau des pics de la Veille
│   ├── RedacteurResult.tsx # 3 drafts de communiqué + bouton Copier
│   ├── SessionsList.tsx    # Liste des sessions persistées
│   ├── StepIndicator.tsx   # Barre sticky 5 étapes
│   ├── StrategeResult.tsx  # 3 options de réponse institutionnelle
│   └── VeilleResult.tsx    # Résumé + PeaksTable
├── hooks/
│   └── usePipeline.ts      # State machine · appels API · restore session
└── pages/
    └── Pipeline.tsx        # Page principale
```

---

## Machine d'états

```
idle
  → loading_analyste   POST /analyse/analyste
    → analyste_done
      → loading_veille  POST /analyse/veille
        → awaiting_human
            ↓ Valider                   ↓ Rejeter
          loading_stratege           rejected
            → stratege_done          POST /analyse/rejeter
              → loading_redacteur
                → complete
```

---

## Comportement des étapes passées

Les résultats Analyste et Veille ne disparaissent pas quand le pipeline avance : ils sont repliés automatiquement dans un `CollapsibleCard` (clic pour déplier/replier).

Le repli automatique repose sur le pattern `key` + `defaultOpen` :

```tsx
<CollapsibleCard
  key={veille ? 'analyste-past' : 'analyste-current'}
  defaultOpen={!veille}
  title="Analyse des narratifs"
  summary={`${analyste.narratif_dominant} · ${analyste.tweet_count} tweets`}
>
  <AnalysteResult data={analyste} />
</CollapsibleCard>
```

Quand `veille` arrive, le composant est remonté avec `defaultOpen={false}` → repli automatique.

---

## Appels API

| Fonction | Route | Corps |
| --- | --- | --- |
| `lancerAnalyste()` | `POST /analyse/analyste` | `{}` |
| `lancerVeille(runId)` | `POST /analyse/veille` | `{ run_id }` |
| `lancerStratege(runId, approved)` | `POST /analyse/stratege` | `{ run_id, humain_approved }` |
| `lancerRedacteur(runId)` | `POST /analyse/redacteur` | `{ run_id }` |
| `rejeterSession(runId)` | `POST /analyse/rejeter` | `{ run_id }` |
| `listerSessions()` | `GET /sessions` | — |
| `recupererSession(runId)` | `GET /sessions/{run_id}` | — |
