---
name: read-paper
description: Read and analyze arXiv papers. Given an arXiv link or ID, download the paper, extract all figures first, generate structured reading notes in both Chinese and English with convincing figures, and push to GitHub. (user)
allowed_prompts:
  - tool: Bash
    prompt: download PDF from arxiv
  - tool: Bash
    prompt: extract figures from PDF
  - tool: Bash
    prompt: git operations
---

# Read Paper Skill

Read arXiv papers and generate structured reading notes with figures, then push to GitHub.

## IMPORTANT: Autonomous Execution

**This skill runs autonomously from start to finish. DO NOT ask the user "Do you want to proceed?" or any similar confirmation questions.**

Execute ALL steps in sequence without pausing:
1. Parse input and fetch metadata
2. Create folder and download PDF
3. Extract all figures
4. Render pages if needed
5. Review figures
6. Read the PDF
7. Generate both Chinese and English notes
8. Save all files
9. Git commit and push

**Never stop to ask for confirmation. Complete the entire workflow automatically.**

## Trigger

Use `/read-paper` followed by an arXiv link or ID.

## Input Formats

Accepts any of these formats:
- arXiv ID: `2301.07041`
- arXiv URL: `https://arxiv.org/abs/2301.07041`
- arXiv PDF URL: `https://arxiv.org/pdf/2301.07041.pdf`

## Workflow

When triggered with an arXiv paper:

### Step 1: Parse Input

Extract the arXiv ID from the input. Examples:
- `2301.07041` → `2301.07041`
- `https://arxiv.org/abs/2301.07041` → `2301.07041`
- `https://arxiv.org/pdf/2301.07041.pdf` → `2301.07041`

### Step 2: Fetch Paper Information

Use the arXiv API to get paper metadata (title, authors, last updated date):
```bash
curl -s "https://export.arxiv.org/api/query?id_list=ARXIV_ID"
```

Extract from the XML response:
- `<title>` - Paper title
- `<author>` - Authors
- `<updated>` - Last edited date (format: YYYY-MM-DD from the full timestamp)

### Step 3: Create Folder and Download PDF

1. Create the paper folder:
```bash
cd ~/projects/claude-skill-read-paper
mkdir -p "paper-YYYY-MM-DD-short-title"
```

2. Download the paper PDF directly to the folder:
```bash
curl -L -o "paper-YYYY-MM-DD-short-title/paper.pdf" "https://arxiv.org/pdf/ARXIV_ID.pdf"
```

### Step 4: Extract ALL Figures from PDF (BEFORE Reading)

**IMPORTANT**: Extract all figures FIRST, before reading the paper. This allows you to review and select the most convincing figures for the notes.

```bash
cd "paper-YYYY-MM-DD-short-title"
mkdir -p figures
```

**Method 1: PyMuPDF (Recommended)**
```python
python3.8 << 'EOF'
import fitz
doc = fitz.open("paper.pdf")
img_count = 0
for page_num in range(len(doc)):
    page = doc[page_num]
    images = page.get_images(full=True)
    for img in images:
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        with open(f"figures/fig-{img_count:03d}.{image_ext}", "wb") as f:
            f.write(image_bytes)
        print(f"Extracted: fig-{img_count:03d}.{image_ext} (page {page_num + 1})")
        img_count += 1
print(f"Total: {img_count} figures extracted")
EOF
```

**Method 2: pdfimages (if PyMuPDF unavailable)**
```bash
pdfimages -png paper.pdf figures/fig
```

**Method 3: pdftoppm (convert pages to images)**
```bash
pdftoppm -png -r 150 paper.pdf figures/page
```

### Step 5: Review Extracted Figures

**CRITICAL STEP**: Before reading the paper, review ALL extracted figures to understand their content:

1. Use the Read tool to view each figure image
2. Identify what each figure shows:
   - Architecture/overview diagrams
   - Method illustrations
   - Experimental results (tables, charts)
   - Ablation study figures
   - Comparison figures
3. Note the figure filenames and their content for later reference
4. Skip small icons or decorative images (usually < 5KB)

This step ensures you can select the most convincing and relevant figures when writing notes.

### Step 6: Read the PDF

Use the Read tool to read the PDF file. When reading:
1. Pay attention to all figures and their captions in the paper
2. Match figure numbers (Fig. 1, Figure 2, etc.) with the extracted image files
3. Note which figures are most important for understanding the paper

### Step 7: Generate Notes with Convincing Figures

After reading the paper and reviewing figures, generate TWO separate markdown files.

**Figure Selection Criteria** - Include figures that:
- Provide visual evidence for key claims
- Show architecture or method overview clearly
- Display experimental results that support conclusions
- Illustrate comparisons or ablation studies
- Help readers understand complex concepts

**Figure Placement**:
- `# Insight` section: Overview/architecture diagram
- `# Contribution` section: Method illustrations for each contribution
- `# Experiments` section: Results charts, tables, ablation figures
- `## Limitation` section: Failure cases or statistical figures if relevant

**Figure Reference Format**:
```markdown
![Description](figures/fig-XXX.png)
*Figure X: Caption explaining what the figure shows and why it's important*
```

### Step 8: Save Files

Save the following files in the paper folder:
- `paper.pdf` - Original paper (already downloaded in Step 3)
- `notes_zh.md` - Chinese notes with figure references
- `notes_en.md` - English notes with figure references
- `figures/` - Directory containing extracted figures

### Step 9: Push to GitHub

```bash
cd ~/projects/claude-skill-read-paper
git add .
git commit -m "Add notes: Paper Title (arXiv:XXXX.XXXXX)"
git push
```

Return the GitHub folder URL to the user.

---

## Note Template

Each markdown file should follow this structure:

```markdown
# Quick View

**Title**: [Paper title]
**Authors**: [Author list]
**arXiv**: [arXiv ID with link]
**Year**: [Publication year]

# Question

[What research question does this paper address?]

# Task

[What specific task is this paper trying to solve?]

# Challenge

[What technical challenges did previous methods face? Why is this problem hard?]

# Insight

[What is the core insight or key idea that solves the challenge? One sentence high-level thought, NOT specific technical contribution.]

![Overview Figure](figures/fig-XXX.png)
*Figure X: Brief description of the main architecture or approach*

# Contribution

[List each technical contribution with:]
1. **[Contribution Name]**
   - **Approach**: [How is it done?]
   - **Technical Advantage**: [Why is this better?]

![Method Figure](figures/fig-XXX.png)
*Figure X: Diagram showing the method*

2. **[Contribution Name]**
   - **Approach**: [How is it done?]
   - **Technical Advantage**: [Why is this better?]

# Experiments

## Core Contribution Impact (Ablation Studies)
[What is the impact of each core contribution on performance?]

![Results Figure](figures/fig-XXX.png)
*Figure/Table X: Key experimental results*

## Limitation
[What are the failure cases? On what kind of data does it fail?]

![Limitation Figure](figures/fig-XXX.png)
*Figure X: Statistics or failure cases (if applicable)*
```

---

## Output Requirements

1. **Two Separate Files**: Generate `notes_zh.md` (Chinese) and `notes_en.md` (English)
2. **Extract Figures First**: Always extract all figures before reading the paper
3. **Review Figures**: View extracted figures to understand their content before writing notes
4. **Select Convincing Figures**: Only include figures that add value and support key points
5. **PDF Included**: Save original paper as `paper.pdf` in the folder
6. **Depth**: Be specific and technical, not generic summaries
7. **Insight vs Contribution**: Clearly distinguish high-level insight from concrete technical contributions
8. **Ablation Focus**: When discussing experiments, prioritize ablation studies

## Folder Structure

For paper `2301.07041` (Verifiable Fully Homomorphic Encryption, updated 2023-02-11):

```
~/projects/claude-skill-read-paper/
├── paper-2023-02-11-verifiable-fhe/
│   ├── paper.pdf           # Original paper
│   ├── notes_zh.md         # Chinese notes (with figures)
│   ├── notes_en.md         # English notes (with figures)
│   └── figures/            # ALL extracted figures
│       ├── fig-000.png     # Review each to understand content
│       ├── fig-001.png
│       └── ...
├── README.md
└── SKILL.md
```

## Figure Selection Guidelines

When reviewing extracted figures, categorize them:

| Category | Where to Use | Priority |
|----------|--------------|----------|
| Architecture/Overview | Insight section | High |
| Method diagrams | Contribution section | High |
| Results tables/charts | Experiments section | High |
| Ablation figures | Ablation subsection | High |
| Comparison charts | Experiments section | Medium |
| Statistics/distributions | Limitation section | Medium |
| Small icons (< 5KB) | Skip | Low |
| Decorative images | Skip | Low |

## Final Output

After completing all steps, display:
1. List of extracted figures with brief descriptions
2. Confirmation message with list of saved files
3. GitHub folder URL: `https://github.com/0xPabloxx/Paper-Skill/tree/main/paper-YYYY-MM-DD-short-title`
