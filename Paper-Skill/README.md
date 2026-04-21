# Read Paper Skill for Claude Code

A Claude Code skill that reads arXiv papers and generates structured reading notes in both Chinese and English, with convincing figures extracted from the paper, then automatically pushes to GitHub.

## Features

- Accepts arXiv ID or URL in multiple formats
- Automatically downloads paper PDF and saves to repo
- **Extracts ALL figures first** before reading paper
- **Reviews figures** to select the most convincing ones
- Generates structured notes in **both Chinese and English**
- **Embeds relevant figures** in notes to improve readability
- Auto-saves to GitHub with organized folder structure

## Workflow

1. Download PDF from arXiv
2. **Extract all figures** from PDF (using PyMuPDF)
3. **Review extracted figures** to understand their content
4. Read the paper
5. **Select convincing figures** for each section of notes
6. Generate bilingual notes with embedded figures
7. Push to GitHub

## Installation

```bash
# Clone this repository
git clone https://github.com/0xPabloxx/Paper-Skill.git

# Copy skill to Claude Code skills directory
mkdir -p ~/.claude/skills/read-paper
cp Paper-Skill/SKILL.md ~/.claude/skills/read-paper/
cp Paper-Skill/README.md ~/.claude/skills/read-paper/
```

### Recommended: Install PyMuPDF for figure extraction

```bash
pip install pymupdf
```

### Alternative: Install poppler-utils

```bash
# Ubuntu/Debian
sudo apt install poppler-utils

# macOS
brew install poppler
```

## Usage

In Claude Code, use the `/read-paper` command:

```
/read-paper 2301.07041
```

Or with full URL:
```
/read-paper https://arxiv.org/abs/2301.07041
```

## Output Structure

After running the skill, files are saved to:

```
Paper-Skill/
├── paper-2023-02-11-verifiable-fhe/
│   ├── paper.pdf          # Original paper
│   ├── notes_zh.md        # Chinese notes (with figures)
│   ├── notes_en.md        # English notes (with figures)
│   └── figures/           # ALL extracted figures
│       ├── fig-000.png    # Reviewed and categorized
│       ├── fig-001.png
│       └── ...
├── paper-2024-01-15-another-paper/
│   └── ...
├── README.md
└── SKILL.md
```

## Note Template

Each note includes:

- **Quick View**: Title, authors, arXiv link, year
- **Question**: Research question addressed
- **Task**: Specific task being solved
- **Challenge**: Technical challenges of previous methods
- **Insight**: Core high-level idea + **overview figure**
- **Contribution**: Technical contributions + **method figures**
- **Experiments**: Ablation studies + **result figures/tables**
- **Limitation**: Failure cases + **statistics figures**

## Figure Selection

Figures are selected based on their value:

| Category | Where Used | Priority |
|----------|------------|----------|
| Architecture/Overview | Insight | High |
| Method diagrams | Contribution | High |
| Results charts/tables | Experiments | High |
| Ablation figures | Experiments | High |
| Comparison charts | Experiments | Medium |
| Statistics | Limitation | Medium |
| Small icons (< 5KB) | Skipped | - |

## Requirements

- Claude Code CLI
- Internet connection (for arXiv access)
- Git configured with push access to your fork
- PyMuPDF (`pip install pymupdf`) or `poppler-utils` for figure extraction

## License

MIT
