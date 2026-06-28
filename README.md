# 🧬 GROMate Analysis Tool

Your friendly all-in-one Python companion for **GROMACS post-MD analysis**. GROMate automates the **10 most common post-simulation analyses** for a protein–ligand MD trajectory — RMSD, RMSF, Rg, SASA, distance, contacts, and PCA — with interactive group selection and consistently named output files.

---

## ✨ Features

- **One script, ten analyses** — no need to remember `gmx` syntax or re-type commands.
- **Interactive group selection** with sensible **pre-filled defaults** (just press `Enter` to accept).
- **Custom output prefix** — name your complex once (e.g. `FGFR_LIGAND1_complex`) and every output file is automatically named consistently:
  ```
  FGFR_LIGAND1_complex_RMSD_PROT.xvg
  FGFR_LIGAND1_complex_RMSD_LIG.xvg
  FGFR_LIGAND1_complex_RMSF.xvg
  FGFR_LIGAND1_complex_RG.xvg
  FGFR_LIGAND1_complex_SASA.xvg
  FGFR_LIGAND1_complex_DIST.xvg
  FGFR_LIGAND1_complex_CON.xvg
  FGFR_LIGAND1_complex_EIG.xvg / .trr
  FGFR_LIGAND1_complex_PROJ_123.xvg
  FGFR_LIGAND1_complex_2D.xvg
  ```
- **Flexible input files** — TPR and XTC filenames are asked at runtime (defaults to `md_0_1.tpr` / `complex_fit.xtc`, but you can type any name, e.g. `fitted.xtc`).
- **Dry-run mode** — preview every `gmx` command and stdin input before actually running anything.
- **Pre-execution summary table** — review all groups, tools, and output filenames in one place before committing.
- **Input file validation** — checks that the `.tpr` and `.xtc` files actually exist before starting.
- **Colorized terminal output** — clear sectioning, ✔/✘ status markers, and a final pass/fail report.
- **Graceful error handling** — captures `gmx` stderr on failure instead of crashing the whole pipeline; one failed analysis doesn't stop the rest.
- **`Ctrl+C` safe** — clean exit message instead of a stack trace.

---

## 📋 Requirements

| Requirement | Notes |
|---|---|
| Python 3.7+ | No external pip packages needed — uses only the standard library |
| GROMACS (`gmx`) | Must be installed and on your `PATH` (or loaded via `module load gromacs`) |
| Input files | A `.tpr` file and a **fitted** `.xtc` trajectory in the working directory |
| Index groups | Default group numbers (`1`=Protein, `4`=Backbone, `13`=Ligand) assume a custom index file — adjust if yours differs |

---

## 🚀 Usage

```bash
python3 gromate.py
```

The script will prompt you for everything — no command-line arguments required.

### Step-by-step flow

1. **Project Setup**
   - TPR file name
   - Fitted XTC file name
   - Complex/project name → used as the output filename prefix
   - Dry-run? (y/n)
2. **Group Selection** — for each of the 10 analyses, accept the default group number or type your own.
3. **Command Summary** — a table of every command, group selection, and output file is shown for review.
4. **Confirm & Run** — type `Y`/Enter to proceed, or `n` to abort.
5. **Final Summary** — pass/fail status for every analysis.

---

## 📊 Analysis Table (defaults used by the script)

| # | Analysis | GROMACS Tool | Sel. 1 | Sel. 2 | Output File |
|---|---|---|---|---|---|
| 1 | Protein RMSD | `gmx rms` | 4 (Backbone) | 4 (Backbone) | `<prefix>_RMSD_PROT.xvg` |
| 2 | Ligand RMSD | `gmx rms` | 4 (Backbone) | 13 (Ligand) | `<prefix>_RMSD_LIG.xvg` |
| 3 | RMSF | `gmx rmsf -res` | 1 (Protein) | — | `<prefix>_RMSF.xvg` |
| 4 | Radius of Gyration | `gmx gyrate` | 1 (Protein) | — | `<prefix>_RG.xvg` |
| 5 | SASA | `gmx sasa` | 1 (Protein) | — | `<prefix>_SASA.xvg` |
| 6 | Min Distance | `gmx mindist` | 1 (Protein) | 13 (Ligand) | `<prefix>_DIST.xvg` |
| 7 | Contacts (≤0.6 nm) | `gmx mindist -d 0.6` | 1 (Protein) | 13 (Ligand) | `<prefix>_CON.xvg` |
| 8 | PCA Covariance | `gmx covar` | 4 (Backbone) | 4 (Backbone) | `<prefix>_EIG.xvg` + `.trr` |
| 9 | PCA 1D Projection | `gmx anaeig` | 4 (Backbone) | 4 (Backbone) | `<prefix>_PROJ_123.xvg` |
| 10 | PCA 2D Projection | `gmx anaeig` | 4 (Backbone) | 4 (Backbone) | `<prefix>_2D.xvg` |

> All values are editable at runtime — the table above is just the pre-filled default.

---

## 🗂 Example Session

```
▶  TPR file name [md_0_1.tpr]:
▶  Fitted XTC trajectory file name [complex_fit.xtc]: fitted.xtc
▶  Complex / project name (used as output prefix) [complex]: FGFR_LIGAND1_complex
▶  Dry-run mode? (print commands only, don't execute) [y/N]:

  [1] Protein RMSD
▶  Selection 1 – fit/reference group (Backbone) [4]:
▶  Selection 2 – RMSD group (Backbone) [4]:
...
```

Resulting file: `FGFR_LIGAND1_complex_RMSD_PROT.xvg`

---

## ⚠️ Known Limitations

- Group numbers (1, 4, 13...) are **assumptions** based on a custom `index.ndx` — if your ligand isn't group 13, you must override it at the prompt.
- The script doesn't auto-generate an index file (`gmx make_ndx`) — you must create one yourself beforehand if the ligand isn't in the default groups.
- No plotting — output is raw `.xvg`; you'll need `xmgrace`,  or Python (`matplotlib`/`pandas`) to visualize the curves.
- Sequential execution — analyses run one after another, not in parallel.
- Hardcoded list of 10 analyses — no plugin/config system for adding custom `gmx` commands.

---

## 📁 File Naming Convention Summary

| Analysis | Output Suffix |
|---|---|
| Protein RMSD | `RMSD_PROT.xvg` |
| Ligand RMSD | `RMSD_LIG.xvg` |
| RMSF | `RMSF.xvg` |
| Radius of Gyration | `RG.xvg` |
| SASA | `SASA.xvg` |
| Min Distance | `DIST.xvg` |
| Contacts | `CON.xvg` |
| PCA Covariance | `EIG.xvg`, `EIG.trr` |
| PCA 1D Projection | `PROJ_123.xvg` |
| PCA 2D Projection | `2D.xvg` |

All suffixes are prefixed with your chosen complex name and an underscore: `<complex_name>_<SUFFIX>`.

---

## 📄 License

Use, modify, and distribute freely for academic and research purposes.

---

<p align="center"><i>Made with 🧪 for the MD community — GROMate, your buddy for post-simulation analysis.</i></p>
