#!/usr/bin/env python3
# ----------------------------------------------------------------------
# Titel   : c_stylecheck.py
# Sprache : Python 3
# Datum   : 08.10.2026
# Autor   : Diveturtle93
# Zweck   : Prueft C-Dateien (.c/.h) gegen C_CODING_STYLE.md
# ----------------------------------------------------------------------
#
# Aufruf:
#   py tools/c_stylecheck.py                      -> alle Ordner ../STM32_* neben diesem Repo
#   py tools/c_stylecheck.py ../STM32_Canbus      -> einzelner Ordner
#   py tools/c_stylecheck.py ../EAuto_* ../IMD_*  -> beliebige Ordner / Glob-Muster
#   py tools/c_stylecheck.py ../STM32_Millis/millis.h   -> einzelne Datei
#   py tools/c_stylecheck.py -r                   -> Reports nach reports/<JJJJMMTT>_<Projekt>.txt
#
# Optionen:
#   -r / --report [DIR]  je Projekt einen Report <JJJJMMTT>_<Projekt>.txt schreiben (Standard: reports/)
#   -q / --quiet         Dateien ohne Befund nicht anzeigen
#   -s / --summary       nur Zusammenfassung je Kategorie
#   -x / --exclude REGEX zusaetzliche Pfade ausschliessen (mehrfach moeglich)
#   --no-default-exclude HAL/CMSIS/CubeMX-Dateien nicht automatisch ausschliessen
#
# Ein Projekt ist jeder Ordner, der als Pfad angegeben oder per Glob gefunden wird.
#
# Automatisch uebersprungen: Drivers/, Middlewares/, Debug/, Release/, build/,
# HAL-/Startup-/System-Dateien sowie alle Dateien mit "USER CODE BEGIN" (CubeMX).
#
# Rueckgabewert: 0 = keine Befunde, 1 = Befunde vorhanden, 2 = keine Dateien gefunden
# ----------------------------------------------------------------------

import argparse
import collections
import datetime
import glob
import os
import re
import sys

SEP = "//" + "-" * 70
COMMENT_COL = 77
TAB_WIDTH = 4

# Generierte bzw. fremde Dateien (STM32CubeMX, HAL, CMSIS, Build-Ausgaben)
DEFAULT_EXCLUDE = [
    r"[\\/]\.git[\\/]",
    r"[\\/](Drivers|Middlewares|CMSIS|Debug|Release|build)[\\/]",
    r"stm32\w*_hal",
    r"stm32\w*_it\.[ch]$",
    r"system_stm32",
    r"startup_",
    r"syscalls\.c$",
    r"sysmem\.c$",
]

INC_SECTIONS = [
    "// Einfuegen der standard Include-Dateien",
    "// Einfuegen der STM Include-Dateien",
    "// Einfuegen der eigenen Include Dateien",
]
HEAD_KEYS = ["Titel", "Sprache", "Datum", "Version", "Autor", "Projekt", "Quelle"]
KEYWORDS = {"if", "for", "while", "switch", "return", "sizeof", "else"}


# Ein Befund: Zeile (0 = ganze Datei), Kategorie, Zusatzinfo
class Issue:
    def __init__(self, line, cat, info=""):
        self.line, self.cat, self.info = line, cat, info


# Spalte (1-basiert) eines Zeichens bei Tabbreite 4
def tabcol(line, idx):
    col = 0
    for ch in line[:idx]:
        col = (col // TAB_WIDTH + 1) * TAB_WIDTH if ch == "\t" else col + 1
    return col + 1


def next_code_line(lines, i):
    return next((x for x in lines[i + 1:] if x.strip()), "")


# Naechste Anweisung nach Zeile i: ueberspringt Leerzeilen, Kommentare, Praeprozessor-
# Zeilen und alternative if-Bedingungen in #if/#ifdef-Zweigen
def next_statement(L, i):
    crossed_pp = False
    for x in L[i + 1:]:
        s = strip_code(x).strip()
        if not s:
            continue
        if s.startswith("#"):
            crossed_pp = True
            continue
        if crossed_pp and re.match(r"(if|else if)\s*\(.*\)$", s):
            continue
        return s
    return ""


def short(l):
    return l.strip()[:80]


def strip_code(l):
    code = re.sub(r'"(\\.|[^"])*"', '""', l)
    code = re.sub(r"'(\\.|[^'])*'", "''", code)
    return re.sub(r"//.*", "", code).rstrip()


FALLTHROUGH = re.compile(r"^\s*(//\s*fall(s)?[ -]?thr(ough|u)\b.*|__attribute__\s*\(\(\s*fallthrough\s*\)\)\s*;.*|\[\[fallthrough\]\]\s*;.*)$", re.I)
TERMINATOR = re.compile(r"^\s*(break|continue|return\b.*|goto\s+\w+)\s*;$")
LABEL = re.compile(r"^\s*(case\b.*|default\s*):\s*$")


# case-Block ohne break/return, dem eine weitere Marke folgt, braucht "// fall through"
def check_fallthrough(L, i, add):
    start = next(j for j in range(i + 1, len(L)) if L[j].strip())
    depth, end = 0, None
    for j in range(start, len(L)):
        c = strip_code(L[j])
        depth += c.count("{") - c.count("}")
        if depth == 0:
            end = j
            break
    if end is None:
        return
    after = next((x for x in L[end + 1:] if strip_code(x).strip()), "")
    if not LABEL.match(strip_code(after)):
        return
    body = [x for x in L[start + 1:end] if x.strip()]
    if not body:
        return
    if FALLTHROUGH.match(body[-1]):
        return
    last_code = next((strip_code(x) for x in reversed(body) if strip_code(x).strip()), "")
    if TERMINATOR.match(last_code):
        return
    add(i + 1, "case ohne break (Fall-through nicht markiert)", short(L[i]))


# Eine Datei pruefen, Rueckgabe: Liste von Issue, sortiert nach Zeile
def check_file(path):
    raw = open(path, "rb").read()
    issues = []

    def add(line, cat, info=""):
        issues.append(Issue(line, cat, info))

    try:
        text = raw.decode("ascii")
        ascii_ok = True
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")
        ascii_ok = False

    raw_lines = text.split("\n")
    L = [l[:-1] if l.endswith("\r") else l for l in raw_lines]
    fname = os.path.basename(path)
    is_header = fname.endswith(".h")
    name = os.path.splitext(fname)[0].upper()

    # Zeilenende
    lf_lines = [i + 1 for i, l in enumerate(raw_lines[:-1]) if not l.endswith("\r")]
    if lf_lines:
        if len(lf_lines) == len(raw_lines) - 1:
            add(0, "Zeilenende", "nur LF statt CRLF")
        else:
            for n in lf_lines:
                add(n, "Zeilenende", "LF statt CRLF")

    # Kopfblock
    if L[0] != SEP:
        add(1, "Kopfblock", "Zeile 1 ist keine Trennlinie")
    for k in HEAD_KEYS:
        found = [(i, l) for i, l in enumerate(L[:12]) if re.match(rf"//\s*{k}\b", l)]
        if not found:
            add(0, "Kopfblock", f"'{k}' fehlt")
            continue
        i, l = found[0]
        if not re.match(rf"// {k}\t:", l):
            add(i + 1, "Kopfblock", f"'{k}' Format abweichend: {short(l)}")
        if k == "Titel" and not l.rstrip().endswith(fname):
            add(i + 1, "Kopfblock", f"Titel != Dateiname: {short(l)}")
        if k == "Datum" and not re.search(r"\d\d\.\d\d\.\d{4}", l):
            add(i + 1, "Kopfblock", f"Datum nicht TT.MM.JJJJ: {short(l)}")
        if k == "Autor" and "Diveturtle93" not in l:
            add(i + 1, "Kopfblock", f"Autor: {short(l)}")

    # Include-Abschnitte
    for s in INC_SECTIONS:
        pos = [i + 1 for i, l in enumerate(L) if l == s]
        if not pos:
            similar = [i + 1 for i, l in enumerate(L) if l.startswith("// Einfuegen") and l not in INC_SECTIONS]
            add(similar[0] if similar else 0, "Abschnitte", f"fehlt/abweichend: '{s[3:]}'")
        for n in pos[1:]:
            add(n, "Abschnitte", f"doppelt: '{s[3:]}'")

    # Debug Symbols
    for i, l in enumerate(L):
        if re.match(r"//\s*\w+\s+Debug Symbols", l) and l != "// Definiere Debug Symbols":
            add(i + 1, "Abschnitte", f"Debug-Abschnitt heisst '{l.strip()}' statt 'Definiere Debug Symbols'")

    if is_header:
        guard = f"INC_{name}_H_"
        if "#pragma once" not in L:
            add(0, "Header", "#pragma once fehlt")
        elif "// Saveguard symbol" not in L:
            idx = L.index("#pragma once")
            add(max(idx - 1, 1), "Header", f"Abschnittsname '{L[max(idx - 2, 0)].strip()}' statt 'Saveguard symbol'")
        if f"#ifndef {guard}" not in L:
            found = [(i, l) for i, l in enumerate(L) if l.startswith("#ifndef")][:1]
            add(found[0][0] + 1 if found else 0, "Header", f"Include-Guard nicht {guard}")
        if f"#endif /* {guard} */" not in L:
            found = [i for i, l in enumerate(L) if l.startswith("#endif")]
            add(found[-1] + 1 if found else 0, "Header", f"'#endif /* {guard} */' fehlt")
        tail = [(i, l) for i, l in enumerate(L) if l.strip()]
        if not tail or tail[-1][1] != SEP:
            add(tail[-1][0] + 1 if tail else 0, "Header", "Datei endet nicht mit Trennlinie")
        if "// Version definieren" not in L:
            add(0, "Header", "Abschnitt 'Version definieren' fehlt")
        missing = [v for v in ("MAJOR", "MINOR", "PATCH", "DEV")
                   if not any(re.match(rf"#define\s+{name}_{v}\b", l) for l in L)]
        if missing:
            add(0, "Header", f"Versions-Defines fehlen: {', '.join(name + '_' + v for v in missing)}")
        has_proto = any(re.match(r"^\w[\w\s\*]*\s\*?\w+\s*\(.*\)\s*;", l) for l in L)
        if has_proto and "// Funktionen definieren" not in L:
            add(0, "Header", "Abschnitt 'Funktionen definieren' fehlt")
    else:
        var = [(i, l) for i, l in enumerate(L) if re.match(r"//\s*Variablen\b", l)]
        if var and "// Variablen definieren" not in L:
            add(var[0][0] + 1, "Abschnitte", f"Variablen-Abschnitt heisst '{var[0][1].strip()}' statt 'Variablen definieren'")

    # Zeilenweise Pruefungen
    in_block = False
    for i, l in enumerate(L):
        n = i + 1
        s = l.strip()
        if not ascii_ok and any(ord(c) > 127 for c in l):
            add(n, "Nicht-ASCII", short(l))
        if s.startswith("//-") and l != SEP:
            add(n, "Trennlinie falsche Laenge", f"{len(l)} statt {len(SEP)} Zeichen")
        if re.match(r"^ +\S", l) and not in_block:
            add(n, "Einrueckung mit Leerzeichen", short(l))
        if "/*" in l and not re.match(r"#endif /\* .* \*/", s):
            add(n, "/* */-Kommentar", short(l))
        if "/*" in l and "*/" not in l:
            in_block = True
        if "*/" in l:
            in_block = False
        if re.search(r"/\*\*|///|[@\\](brief|param|return)\b", l):
            add(n, "Doxygen", short(l))
        if 'extern "C"' in l:
            add(n, 'extern "C"', short(l))
        if re.match(r"//[^\s\-/]", s):
            add(n, "Kommentar ohne Leerzeichen nach //", short(l))
        if s == "//":
            add(n, "leerer Kommentar")

        # Code ohne Kommentare und Strings
        code = re.sub(r'"(\\.|[^"])*"', '""', l)
        code = re.sub(r"//.*", "", code).rstrip()

        if code.endswith("{") and code.strip() != "{" and not re.search(r"=\s*\{$", code) and not in_block:
            add(n, "K&R-Klammer (nicht Allman)", short(l))
        if re.match(r"\s*(case\b.*|default\s*):\s*$", code):
            # Mehrere Marken untereinander erlaubt, nur die letzte braucht den Block
            nxt = re.sub(r"//.*", "", next_code_line(L, i)).strip()
            if nxt != "{" and not re.match(r"(case\b.*|default\s*):$", nxt):
                add(n, "case ohne { }-Block", short(l))
            elif nxt == "{":
                check_fallthrough(L, i, add)
        if re.match(r"\s*switch\s*\(", code):
            depth, found = 0, False
            for x in L[i + 1:]:
                depth += x.count("{") - x.count("}")
                if re.match(r"\s*default\s*:", x):
                    found = True
                if depth <= 0 and "}" in x:
                    break
            if not found:
                add(n, "switch ohne default", short(l))
        if re.match(r"\s*(if|else if|for|while)\s*\(.*\)\s*$", code) or re.match(r"\s*else\s*$", code):
            nxt = next_statement(L, i)
            is_if = re.match(r"\s*(if|else)\b", code)
            if nxt != "{" and not (is_if and re.match(r"return\b.*;$", nxt)):
                add(n, "if/else/for ohne { }", short(l))
        if re.match(r"\s*(if|for|while|switch)\(", code):
            add(n, "kein Leerzeichen nach Schluesselwort", short(l))

        # Funktionsdefinition / Prototyp (nur am Zeilenanfang)
        fm = re.match(r"^(?!typedef|#|return|else|static inline)[A-Za-z_][\w\s\*]*?\b([A-Za-z_]\w*)(\s*)\((.*)\)\s*(;)?\s*$", code)
        if fm and fm.group(1) not in KEYWORDS:
            is_def = fm.group(4) is None and next_code_line(L, i).strip() == "{"
            is_proto = fm.group(4) == ";"
            if is_def or is_proto:
                if fm.group(2) == "":
                    add(n, "kein Leerzeichen vor ( bei Deklaration/Definition", short(l))
                if fm.group(3).strip() == "":
                    add(n, "leere Parameterliste statt (void)", short(l))
            if is_def:
                prev = L[max(0, i - 2):i]
                if not (len(prev) == 2 and prev[1] == SEP and re.match(r"// \S", prev[0])):
                    add(n, "Funktion ohne Kommentar+Trennlinie davor", short(l))

        # Zeilenkommentar hinter Code
        cm = re.search(r"\S(\s+)//", l)
        if cm and not s.startswith("//") and '"' not in l[:cm.start() + 1]:
            col = tabcol(l, cm.end() - 2)
            before = l[:cm.start() + 1].strip()
            ctx = f"{before[:40]}{' ...' if len(before) > 40 else ''}  {l[cm.end() - 2:].strip()[:40]}"
            if col != COMMENT_COL and tabcol(l, cm.start() + 1) < COMMENT_COL - 1:
                add(n, f"Zeilenkommentar nicht auf Spalte {COMMENT_COL}", f"Spalte {col}: {ctx}")
            if " " in cm.group(1):
                add(n, "Kommentar mit Leerzeichen statt Tabs ausgerichtet", ctx)

    issues.sort(key=lambda x: x.line)
    return issues


# Von STM32CubeMX generierte Datei (enthaelt USER CODE Marker)
def is_generated(path):
    with open(path, "rb") as f:
        return b"USER CODE BEGIN" in f.read()


def list_c_files(path):
    if os.path.isfile(path):
        return [path] if path.endswith((".c", ".h")) else []
    return sorted(glob.glob(os.path.join(path, "**", "*.[ch]"), recursive=True))


# Pfade/Globs zu Projekten aufloesen: {Projektname: (Basisordner, [Dateien])}
def collect_projects(targets, excludes, skip_generated=True):
    projects = collections.OrderedDict()
    seen = set()
    for t in targets:
        matches = glob.glob(t) or ([t] if os.path.exists(t) else [])
        if not matches:
            print(f"Warnung: '{t}' nicht gefunden", file=sys.stderr)
        for m in sorted(matches):
            m = os.path.abspath(m)
            base = m if os.path.isdir(m) else os.path.dirname(m)
            proj = os.path.basename(base)
            for p in list_c_files(m):
                p = os.path.abspath(p)
                if p in seen or any(re.search(x, p, re.I) for x in excludes):
                    continue
                if skip_generated and is_generated(p):
                    continue
                seen.add(p)
                projects.setdefault(proj, (base, []))[1].append(p)
    return projects


def format_issue(issue):
    where = f"Z.{issue.line:5}" if issue.line else "Datei  "
    info = f"  ->  {issue.info}" if issue.info else ""
    return f"  {where}  [{issue.cat}]{info}"


# Report-Text fuer ein Projekt erzeugen
def build_report(proj, base, results):
    total = collections.Counter()
    count = sum(len(i) for _, i in results)
    clean = sum(1 for _, i in results if not i)
    for _, iss in results:
        for x in iss:
            total[x.cat] += 1

    out = []
    out.append("=" * 72)
    out.append(f"Style-Report : {proj}")
    out.append(f"Ordner       : {base}")
    out.append(f"Erstellt     : {datetime.datetime.now():%d.%m.%Y %H:%M}")
    out.append(f"Regeln       : C_CODING_STYLE.md")
    out.append(f"Geprueft     : {len(results)} Dateien, davon {clean} ohne Befund")
    out.append(f"Befunde      : {count}")
    out.append("=" * 72)

    if total:
        out.append("")
        out.append("Befunde je Kategorie")
        out.append("-" * 72)
        for c, n in total.most_common():
            out.append(f"{n:6}  {c}")

    for p, iss in results:
        out.append("")
        out.append("-" * 72)
        out.append(f"{os.path.relpath(p, base)}  ({len(iss)} Befunde)")
        out.append("-" * 72)
        if not iss:
            out.append("  keine Befunde")
        for x in iss:
            out.append(format_issue(x))
    out.append("")
    return "\n".join(out)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(here)
    own_dir = os.path.dirname(repo_dir)
    default_target = os.path.join(own_dir, "STM32_*")
    default_reports = os.path.join(repo_dir, "reports")

    ap = argparse.ArgumentParser(description="Prueft C-Dateien gegen C_CODING_STYLE.md")
    ap.add_argument("paths", nargs="*", help=f"Ordner, Dateien oder Glob-Muster (Standard: {default_target})")
    ap.add_argument("-r", "--report", nargs="?", const=default_reports, metavar="DIR",
                    help=f"je Projekt Report <JJJJMMTT>_<Projekt>.txt schreiben (Standard: {default_reports})")
    ap.add_argument("-q", "--quiet", action="store_true", help="Dateien ohne Befund nicht anzeigen")
    ap.add_argument("-s", "--summary", action="store_true", help="nur Zusammenfassung ausgeben")
    ap.add_argument("-x", "--exclude", action="append", default=[], metavar="REGEX", help="zusaetzlich ausschliessen")
    ap.add_argument("--no-default-exclude", action="store_true", help="HAL/CMSIS/CubeMX-Dateien mitpruefen")
    args = ap.parse_args()

    excludes = args.exclude + ([] if args.no_default_exclude else DEFAULT_EXCLUDE)
    projects = collect_projects(args.paths or [default_target], excludes, not args.no_default_exclude)
    if not projects:
        print("Keine .c/.h-Dateien gefunden.")
        return 2

    if args.report:
        os.makedirs(args.report, exist_ok=True)
    date_prefix = datetime.date.today().strftime("%Y%m%d")

    total = collections.Counter()
    n_files = n_clean = 0
    for proj, (base, files) in projects.items():
        results = [(p, check_file(p)) for p in files]
        n_files += len(results)
        n_clean += sum(1 for _, i in results if not i)
        for _, iss in results:
            for x in iss:
                total[x.cat] += 1

        if args.report:
            path = os.path.join(args.report, f"{date_prefix}_{proj}.txt")
            with open(path, "w", encoding="ascii", errors="replace", newline="\r\n") as f:
                f.write(build_report(proj, base, results))
            print(f"{proj:30} {sum(len(i) for _, i in results):6} Befunde  -> {os.path.relpath(path)}")
            continue

        if args.summary:
            continue
        for p, iss in results:
            if args.quiet and not iss:
                continue
            print(f"\n### {proj}/{os.path.relpath(p, base)}  ({len(iss)} Befunde)")
            for x in iss:
                print(format_issue(x))

    print("\n=== Befunde je Kategorie ===")
    for c, n in total.most_common():
        print(f"{n:6}  {c}")
    print(f"\nGeprueft: {len(projects)} Projekte, {n_files} Dateien, davon {n_clean} ohne Befund")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
