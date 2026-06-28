#!/usr/bin/env python3
"""
GROMACS MD Analysis Automation Script
Runs a standard post-MD analysis pipeline.
Group selections are pre-filled with standard defaults — just press Enter to accept.
"""

import subprocess
import sys
import os

# ─────────────────────────────────────────────
#  ANSI colour helpers
# ─────────────────────────────────────────────
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════╗
║         GROMACS MD POST-ANALYSIS PIPELINE                ║
║         Automated Analysis Script                        ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

def section(title: str):
    print(f"\n{YELLOW}{BOLD}{'─'*58}{RESET}")
    print(f"{YELLOW}{BOLD}  {title}{RESET}")
    print(f"{YELLOW}{BOLD}{'─'*58}{RESET}")

def info(msg: str):
    print(f"  {CYAN}ℹ{RESET}  {msg}")

def success(msg: str):
    print(f"  {GREEN}✔{RESET}  {msg}")

def error(msg: str):
    print(f"  {RED}✘{RESET}  {msg}")

def prompt(msg: str, default: str = "") -> str:
    hint = f" {DIM}[{default}]{RESET}" if default else ""
    val = input(f"  {BOLD}▶{RESET}  {msg}{hint}: ").strip()
    return val if val else default

def prompt_int(msg: str, default: int) -> int:
    while True:
        raw = input(f"  {BOLD}▶{RESET}  {msg} {DIM}[{default}]{RESET}: ").strip()
        if raw == "":
            return default
        try:
            return int(raw)
        except ValueError:
            print(f"  {RED}Please enter a valid integer.{RESET}")

# ─────────────────────────────────────────────
#  Run a GROMACS command
# ─────────────────────────────────────────────
def run_gmx(cmd, stdin_groups=None, dry_run=False):
    cmd_str = " ".join(cmd)
    print(f"\n  {DIM}$ {cmd_str}{RESET}")
    if stdin_groups:
        print(f"  {DIM}  stdin → {' | '.join(str(g) for g in stdin_groups)}{RESET}")

    if dry_run:
        return True

    stdin_input = ("\n".join(str(g) for g in stdin_groups) + "\n").encode() if stdin_groups else None

    try:
        result = subprocess.run(cmd, input=stdin_input, capture_output=True)
        if result.returncode != 0:
            error(f"Command failed (exit {result.returncode})")
            stderr = result.stderr.decode(errors="replace").strip()
            if stderr:
                print(f"  {RED}{stderr[-800:]}{RESET}")
            return False
        return True
    except FileNotFoundError:
        error("'gmx' not found – is GROMACS loaded/installed?")
        return False

# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
def main():
    banner()

    # ── 1. Global inputs ──────────────────────
    section("Step 1 · Project Setup")

    tpr_file     = prompt("TPR file name", "md_0_1.tpr")
    xtc_file     = prompt("Fitted XTC trajectory file name", "complex_fit.xtc")
    complex_name = prompt("Complex / project name (used as output prefix)", "complex")

    dry_run_ans = prompt("Dry-run mode? (print commands only, don't execute) [y/N]", "N")
    dry_run = dry_run_ans.strip().lower() in ("y", "yes")

    if dry_run:
        info("DRY-RUN mode — commands will be printed but NOT executed.")

    if not dry_run:
        for f in (tpr_file, xtc_file):
            if not os.path.isfile(f):
                error(f"File not found: {f}")
                sys.exit(1)
        success("Input files found.")

    # ── Output name builder (CAPS suffix) ─────
    def out(suffix):
        return f"{complex_name}_{suffix}"

    # ═══════════════════════════════════════════
    #  2. Pre-filled group selection
    # ═══════════════════════════════════════════
    section("Step 2 · Group Selection  (press Enter to accept defaults)")

    print(f"""
  {DIM}Defaults follow the standard analysis table.
  Common groups:  0=System  1=Protein  3=C-alpha  4=Backbone  13=Ligand
  Adjust group numbers to match YOUR index file if needed.{RESET}
""")

    # [1] Protein RMSD  → Sel1: 4 (Backbone)  Sel2: 4 (Backbone)
    print(f"{BOLD}  [1] Protein RMSD{RESET}")
    prot_rmsd_ref  = prompt_int("    Selection 1 – fit/reference group  (Backbone)", 4)
    prot_rmsd_calc = prompt_int("    Selection 2 – RMSD group           (Backbone)", 4)

    # [2] Ligand RMSD   → Sel1: 4 (Backbone)  Sel2: 13 (Ligand)
    print(f"\n{BOLD}  [2] Ligand RMSD{RESET}")
    lig_rmsd_ref  = prompt_int("    Selection 1 – fit/reference group  (Backbone)", 4)
    lig_rmsd_calc = prompt_int("    Selection 2 – ligand group         (Ligand)",   13)

    # [3] RMSF          → Sel1: 1 (Protein)
    print(f"\n{BOLD}  [3] RMSF{RESET}")
    rmsf_grp = prompt_int("    Selection 1 – group               (Protein)",   1)

    # [4] Radius of Gyration → Sel1: 1 (Protein)
    print(f"\n{BOLD}  [4] Radius of Gyration (Rg){RESET}")
    rg_grp = prompt_int("    Selection 1 – group               (Protein)",   1)

    # [5] SASA          → Sel1: 1 (Protein)
    print(f"\n{BOLD}  [5] SASA{RESET}")
    sasa_grp = prompt_int("    Selection 1 – group               (Protein)",   1)

    # [6] Min Distance  → Sel1: 1 (Protein)  Sel2: 13 (Ligand)
    print(f"\n{BOLD}  [6] Minimum Distance{RESET}")
    mindist_grp1 = prompt_int("    Selection 1 – protein group      (Protein)", 1)
    mindist_grp2 = prompt_int("    Selection 2 – ligand group       (Ligand)",  13)

    # [7] Contacts      → Sel1: 1 (Protein)  Sel2: 13 (Ligand)  cutoff: 0.6
    print(f"\n{BOLD}  [7] Contacts{RESET}")
    contacts_grp1   = prompt_int("    Selection 1 – protein group      (Protein)", 1)
    contacts_grp2   = prompt_int("    Selection 2 – ligand group       (Ligand)",  13)
    contacts_cutoff = prompt("    Distance cutoff (nm)", "0.6")

    # [8] PCA Covar     → Sel1: 4 (Backbone)  Sel2: 4 (Backbone)
    print(f"\n{BOLD}  [8] PCA – Covariance (gmx covar){RESET}")
    pca_covar_grp1 = prompt_int("    Selection 1 – fit group          (Backbone)", 4)
    pca_covar_grp2 = prompt_int("    Selection 2 – analysis group     (Backbone)", 4)

    # [9] PCA 1D Proj   → Sel1: 4 (Backbone)  Sel2: 4
    print(f"\n{BOLD}  [9] PCA – 1D Projection (gmx anaeig){RESET}")
    pca_1d_grp1  = prompt_int("    Selection 1 – fit group          (Backbone)", 4)
    pca_1d_grp2  = prompt_int("    Selection 2 – projection group   (Backbone)", 4)
    pca_1d_first = prompt("    First eigenvector", "1")
    pca_1d_last  = prompt("    Last eigenvector",  "3")

    # [10] PCA 2D Proj  → Sel1: 4 (Backbone)  Sel2: 4
    print(f"\n{BOLD}  [10] PCA – 2D Projection (gmx anaeig){RESET}")
    pca_2d_grp1 = prompt_int("    Selection 1 – fit group          (Backbone)", 4)
    pca_2d_grp2 = prompt_int("    Selection 2 – projection group   (Backbone)", 4)

    # ═══════════════════════════════════════════
    #  3. Summary table
    # ═══════════════════════════════════════════
    section("Step 3 · Command Summary")

    rows = [
        ("Protein RMSD",  "gmx rms",    f"{prot_rmsd_ref} / {prot_rmsd_calc}",  out("RMSD_PROT.xvg")),
        ("Ligand RMSD",   "gmx rms",    f"{lig_rmsd_ref} / {lig_rmsd_calc}",    out("RMSD_LIG.xvg")),
        ("RMSF",          "gmx rmsf",   f"{rmsf_grp}",                           out("RMSF.xvg")),
        ("Rg",            "gmx gyrate", f"{rg_grp}",                             out("RG.xvg")),
        ("SASA",          "gmx sasa",   f"{sasa_grp}",                           out("SASA.xvg")),
        ("Min Distance",  "gmx mindist",f"{mindist_grp1} / {mindist_grp2}",      out("DIST.xvg")),
        ("Contacts",      "gmx mindist",f"{contacts_grp1} / {contacts_grp2}",    out("CON.xvg")),
        ("PCA Covar",     "gmx covar",  f"{pca_covar_grp1} / {pca_covar_grp2}",  out("EIG.xvg")),
        ("PCA 1D Proj",   "gmx anaeig", f"{pca_1d_grp1} / {pca_1d_grp2}",        out("PROJ_123.xvg")),
        ("PCA 2D Proj",   "gmx anaeig", f"{pca_2d_grp1} / {pca_2d_grp2}",        out("2D.xvg")),
    ]

    w = [15, 14, 12, 44]
    hdr = f"  {'Analysis':<{w[0]}} {'Tool':<{w[1]}} {'Groups':<{w[2]}} {'Output file':<{w[3]}}"
    print(f"\n{DIM}{hdr}{RESET}")
    print(f"  {DIM}{'─'*(sum(w)+2)}{RESET}")
    for r in rows:
        print(f"  {r[0]:<{w[0]}} {DIM}{r[1]:<{w[1]}}{RESET} {r[2]:<{w[2]}} {GREEN}{r[3]}{RESET}")

    confirm = prompt("\nProceed with execution? [Y/n]", "Y")
    if confirm.strip().lower() in ("n", "no"):
        info("Aborted by user.")
        sys.exit(0)

    # ═══════════════════════════════════════════
    #  4. Execute
    # ═══════════════════════════════════════════
    section("Step 4 · Running Analyses")
    results = {}

    # [1] Protein RMSD
    print(f"\n{BOLD}  [1/10] Protein RMSD{RESET}")
    ok = run_gmx(
        ["gmx", "rms", "-s", tpr_file, "-f", xtc_file,
         "-o", out("RMSD_PROT.xvg"), "-tu", "ns"],
        stdin_groups=[prot_rmsd_ref, prot_rmsd_calc], dry_run=dry_run)
    results["Protein RMSD"] = ok
    (success if ok else error)(out("RMSD_PROT.xvg"))

    # [2] Ligand RMSD
    print(f"\n{BOLD}  [2/10] Ligand RMSD{RESET}")
    ok = run_gmx(
        ["gmx", "rms", "-s", tpr_file, "-f", xtc_file,
         "-o", out("RMSD_LIG.xvg"), "-tu", "ns"],
        stdin_groups=[lig_rmsd_ref, lig_rmsd_calc], dry_run=dry_run)
    results["Ligand RMSD"] = ok
    (success if ok else error)(out("RMSD_LIG.xvg"))

    # [3] RMSF
    print(f"\n{BOLD}  [3/10] RMSF{RESET}")
    ok = run_gmx(
        ["gmx", "rmsf", "-s", tpr_file, "-f", xtc_file,
         "-o", out("RMSF.xvg"), "-res"],
        stdin_groups=[rmsf_grp], dry_run=dry_run)
    results["RMSF"] = ok
    (success if ok else error)(out("RMSF.xvg"))

    # [4] Radius of Gyration
    print(f"\n{BOLD}  [4/10] Radius of Gyration{RESET}")
    ok = run_gmx(
        ["gmx", "gyrate", "-s", tpr_file, "-f", xtc_file,
         "-o", out("RG.xvg"), "-tu", "ns"],
        stdin_groups=[rg_grp], dry_run=dry_run)
    results["Rg"] = ok
    (success if ok else error)(out("RG.xvg"))

    # [5] SASA
    print(f"\n{BOLD}  [5/10] SASA{RESET}")
    ok = run_gmx(
        ["gmx", "sasa", "-s", tpr_file, "-f", xtc_file,
         "-o", out("SASA.xvg"), "-tu", "ns"],
        stdin_groups=[sasa_grp], dry_run=dry_run)
    results["SASA"] = ok
    (success if ok else error)(out("SASA.xvg"))

    # [6] Minimum Distance
    print(f"\n{BOLD}  [6/10] Minimum Distance{RESET}")
    ok = run_gmx(
        ["gmx", "mindist", "-s", tpr_file, "-f", xtc_file,
         "-od", out("DIST.xvg"), "-tu", "ns"],
        stdin_groups=[mindist_grp1, mindist_grp2], dry_run=dry_run)
    results["Min Distance"] = ok
    (success if ok else error)(out("DIST.xvg"))

    # [7] Contacts
    print(f"\n{BOLD}  [7/10] Contacts{RESET}")
    ok = run_gmx(
        ["gmx", "mindist", "-s", tpr_file, "-f", xtc_file,
         "-on", out("CON.xvg"), "-d", contacts_cutoff, "-tu", "ns"],
        stdin_groups=[contacts_grp1, contacts_grp2], dry_run=dry_run)
    results["Contacts"] = ok
    (success if ok else error)(out("CON.xvg"))

    # [8] PCA Covariance
    print(f"\n{BOLD}  [8/10] PCA – Covariance{RESET}")
    ok = run_gmx(
        ["gmx", "covar", "-s", tpr_file, "-f", xtc_file,
         "-o", out("EIG.xvg"), "-v", out("EIG.trr")],
        stdin_groups=[pca_covar_grp1, pca_covar_grp2], dry_run=dry_run)
    results["PCA Covar"] = ok
    (success if ok else error)(f"{out('EIG.xvg')} + {out('EIG.trr')}")

    # [9] PCA 1D Projection
    print(f"\n{BOLD}  [9/10] PCA – 1D Projection{RESET}")
    ok = run_gmx(
        ["gmx", "anaeig", "-s", tpr_file, "-f", xtc_file,
         "-v", out("EIG.trr"), "-proj", out("PROJ_123.xvg"),
         "-first", str(pca_1d_first), "-last", str(pca_1d_last), "-tu", "ns"],
        stdin_groups=[pca_1d_grp1, pca_1d_grp2], dry_run=dry_run)
    results["PCA 1D"] = ok
    (success if ok else error)(out("PROJ_123.xvg"))

    # [10] PCA 2D Projection
    print(f"\n{BOLD}  [10/10] PCA – 2D Projection{RESET}")
    ok = run_gmx(
        ["gmx", "anaeig", "-s", tpr_file, "-f", xtc_file,
         "-v", out("EIG.trr"), "-2d", out("2D.xvg"),
         "-first", "1", "-last", "2"],
        stdin_groups=[pca_2d_grp1, pca_2d_grp2], dry_run=dry_run)
    results["PCA 2D"] = ok
    (success if ok else error)(out("2D.xvg"))

    # ═══════════════════════════════════════════
    #  5. Final summary
    # ═══════════════════════════════════════════
    section("Step 5 · Final Summary")
    passed = sum(1 for v in results.values() if v)
    total  = len(results)

    for name, ok in results.items():
        status = f"{GREEN}DONE  {RESET}" if ok else f"{RED}FAILED{RESET}"
        print(f"  {name:<20}  {status}")

    print(f"\n  {BOLD}Result: {passed}/{total} analyses completed.{RESET}")

    if passed == total:
        print(f"\n  {GREEN}{BOLD}All analyses finished successfully!{RESET}")
        print(f"  Output files prefixed with: {CYAN}{complex_name}_{RESET}\n")
    else:
        print(f"\n  {YELLOW}Some analyses failed — check the errors above.{RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {YELLOW}Interrupted by user.{RESET}\n")
        sys.exit(0)
