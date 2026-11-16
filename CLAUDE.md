# Interpreted-Context-Methdology

ICM is a framework for building structured, multi-stage AI workflows out of markdown files and folder conventions. Each workspace gives AI agents the right context at each stage of a task, and gives humans clear edit surfaces between stages.

## Folder Map

```
model-workspace-protocol/
├── CLAUDE.md                          (you are here)
├── README.md                          (project overview)
├── LICENSE
├── _core/                             (shared conventions and templates)
│   ├── CONVENTIONS.md                 (source of truth for all patterns)
│   ├── placeholder-syntax.md          (how {{VARIABLES}} work)
│   └── templates/                     (blank starting points for new workspaces)
└── workspaces/
    ├── script-to-animation/           (content idea -> animated video)
    ├── course-deck-production/        (unstructured material -> course PowerPoints)
    ├── workspace-builder/             (builds new MWP workspaces)
    └── hces-lab/                      (builds and measures the HCES gate and memory store)
hces/                                  (HCES v1: `python -m hces gate | remember | recall`, see hces/README.md)
```

## Routing

| You want to... | Go to |
|-----------------|-------|
| Create content with script-to-animation | `workspaces/script-to-animation/CLAUDE.md` |
| Build course slide decks from source material | `workspaces/course-deck-production/CLAUDE.md` |
| Build a new workspace for any domain | `workspaces/workspace-builder/CLAUDE.md` |
| Pick the reference sections a stage task needs | `python -m hces gate` (Pattern 16 in `_core/CONVENTIONS.md`) |
| Store or look up facts that change over time | `python -m hces remember` / `recall` (Pattern 17) |
| See how HCES was built and measured | `workspaces/hces-lab/CLAUDE.md` |
| Read the full MWP specification | `_core/CONVENTIONS.md` |
| Understand the placeholder system | `_core/placeholder-syntax.md` |
| Use a template for a new workspace | `_core/templates/` |

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Run onboarding in whatever workspace you are in |
| `status` | Show pipeline completion for the current workspace |
| `gate` | Run the HCES gate for the current stage and task, then read `output/gate-kept.md` instead of the whole reference files |
| `remember` | Store a dated note in this workspace's memory (`memory.sqlite`) |
| `recall` | Answer from this workspace's memory as of a date |

## How It Works

Each workspace is self-contained with its own CLAUDE.md. Navigate into a workspace folder and that workspace's CLAUDE.md takes over. You do not need to read this root file once you are inside a workspace.
