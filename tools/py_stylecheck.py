#!/usr/bin/env python3
#-----------------------------------------------------------------------
# Titel	:	py_stylecheck.py
#-----------------------------------------------------------------------
# Sprache	:	Python
# Datum	:	12.10.2026
# Version	:	1.0
# Autor	:	Diveturtle93
# Projekt	:	Diveturtle93
# Quelle	:
#-----------------------------------------------------------------------

# Beschreibung
#-----------------------------------------------------------------------
# Prueft Python-Dateien (.py) gegen PYTHON_CODING_STYLE.md
# Aufruf:
#   py tools/py_stylecheck.py                      -> alle Ordner neben diesem Repo
#   py tools/py_stylecheck.py ../EAuto_Dashboard   -> einzelner Ordner
#   py tools/py_stylecheck.py "../EAuto_*"         -> beliebige Ordner / Glob-Muster
#   py tools/py_stylecheck.py tools/py_stylecheck.py   -> einzelne Datei
#   py tools/py_stylecheck.py -r                   -> Reports nach reports/py/<JJJJMMTT>_<Projekt>.txt
#   py tools/py_stylecheck.py -r -f                -> Reports nur fuer Projekte mit Befunden
#   py tools/py_stylecheck.py -c                   -> alle Python-Reports in reports/py/ loeschen
#
# Optionen:
#   -r / --report [DIR]  je Projekt einen Report DIR/py/<JJJJMMTT>_<Projekt>.txt schreiben (Standard: reports/),
#                        dazu immer DIR/py/<JJJJMMTT>_Uebersicht.txt ueber alle Projekte
#   -f / --findings-only mit -r nur Reports fuer Projekte mit Befunden schreiben, die Uebersicht
#                        enthaelt weiterhin alle Projekte
#   -c / --clean [DIR]   alle Reports DIR/py/<JJJJMMTT>_*.txt loeschen (Standard: reports/),
#                        mit -r werden danach neue Reports geschrieben
#   -q / --quiet         Dateien ohne Befund nicht anzeigen
#   -s / --summary       nur Zusammenfassung je Kategorie
#   -x / --exclude REGEX zusaetzliche Pfade ausschliessen (mehrfach moeglich)
#   --no-default-exclude virtuelle Umgebungen, Caches, Build-Ordner und Submodule mitpruefen
#
# Projekt-Einstellungen (optional): Datei .stylecheck im Projektordner (gemeinsam mit c_stylecheck.py)
#   [stylecheck]                  -> gilt fuer C und Python
#   exclude = openblt, Test       -> diese Ordner/Dateien zusaetzlich ausschliessen
#   [py]                          -> gilt nur fuer Python, ergaenzt [stylecheck]
#   include = backend, ui         -> nur diese Ordner pruefen
#
# Rueckgabewert: 0 = keine Befunde, 1 = Befunde vorhanden, 2 = keine Dateien gefunden
#-----------------------------------------------------------------------

# Einfuegen der standard Module
#-----------------------------------------------------------------------
import argparse
import ast
import collections
import datetime
import glob
import io
import os
import re
import sys
import tokenize
#-----------------------------------------------------------------------

# Einfuegen der externen Module
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------

# Einfuegen der eigenen Module
#-----------------------------------------------------------------------
from c_stylecheck import Issue, checkOrder, cleanReports, formatIssue, inDirs, normDir, projectSettings, tabcol, writeOverview
#-----------------------------------------------------------------------

# Definiere Debug-Symbole
#-----------------------------------------------------------------------
DEBUG_PY_STYLECHECK						= False
#-----------------------------------------------------------------------

# Version definieren
#-----------------------------------------------------------------------
PY_STYLECHECK_MAJOR						= 1
PY_STYLECHECK_MINOR						= 0
PY_STYLECHECK_PATCH						= 0
PY_STYLECHECK_DEV						= 0
#-----------------------------------------------------------------------

# Konstanten definieren
#-----------------------------------------------------------------------
SEP										= "#" + "-" * 71					# Trennlinie, 72 Zeichen
COMMENT_COL								= 77								# Spalte der Zeilenkommentare
REPORT_SUBDIR							= "py"								# Reports nach <DIR>/py/

# Virtuelle Umgebungen, Caches und Build-Ausgaben
DEFAULT_EXCLUDE							= [
	r"[\\/](\.git|\.venv|venv|env|__pycache__|\.tox|\.mypy_cache|\.pytest_cache|build|dist|site-packages|node_modules)[\\/]",
]

IMPORT_SECTIONS							= {
	"standard": "# Einfuegen der standard Module",
	"extern": "# Einfuegen der externen Module",
	"eigene": "# Einfuegen der eigenen Module",
}
DESC_SECTION							= "# Beschreibung"
DEBUG_SECTION							= "# Definiere Debug-Symbole"
DEBUG_NAME								= re.compile(r"#\s*\w+\s+Debug[\s-]*Symbol", re.I)
VERSION_SECTION							= "# Version definieren"
CONST_SECTION							= "# Konstanten definieren"
VAR_SECTION								= "# Variablen definieren"
VAR_INC_SECTION							= "# Variablen einbinden"
TABLE_SECTION							= "# Funktionstabellen definieren"
MAIN_SECTION							= "# Hauptprogramm"
HEAD_KEYS								= ["Titel", "Sprache", "Datum", "Version", "Autor", "Projekt", "Quelle"]
VERSION_KEYS							= ["MAJOR", "MINOR", "PATCH", "DEV"]

# Rang der Abschnitte fuer die Reihenfolgepruefung, gleiche Reihenfolge wie C (.h + .c)
RANK_CLASS								= 8
RANK_FUNC								= 11
SECTION_RANKS							= [
	(DESC_SECTION, 1),
	(IMPORT_SECTIONS["standard"], 2),
	(IMPORT_SECTIONS["extern"], 3),
	(IMPORT_SECTIONS["eigene"], 4),
	(DEBUG_SECTION, 5),
	(VERSION_SECTION, 6),
	(CONST_SECTION, 7),
	(VAR_SECTION, 9),
	(VAR_INC_SECTION, 10),
	(TABLE_SECTION, 12),
	(MAIN_SECTION, 13),
]

# Zeilen, die mit diesen Schluesselwoertern beginnen, enden mit ':' und einem Block
COMPOUND								= {"if", "elif", "else", "for", "while", "with", "try", "except", "finally", "def", "class", "async"}
SOFT_COMPOUND							= {"match", "case"}
OPEN									= {"(", "[", "{"}
CLOSE									= {")", "]", "}"}
STRING_TOKENS							= {tokenize.STRING} | {getattr(tokenize, n) for n in ("FSTRING_MIDDLE", "TSTRING_MIDDLE") if hasattr(tokenize, n)}

# Schluesselwoerter, nach denen vor "(" ein Leerzeichen steht
SPACE_KEYWORDS							= {"if", "elif", "while", "for"}

# Namen wie in C: Funktionen camelCase (Modul-Praefix erlaubt), Klassen PascalCase oder <Name>_TypeDef
CAMEL									= re.compile(r"^_*[A-Za-z][a-zA-Z0-9]*$")
PASCAL									= re.compile(r"^_*[A-Z][a-zA-Z0-9]*(_[A-Z][a-zA-Z0-9]*)*$")
DUNDER									= re.compile(r"^__\w+__$")
#-----------------------------------------------------------------------

# Variablen definieren
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------

# Zeile fuer die Ausgabe kuerzen
#-----------------------------------------------------------------------
def short (l):
	return l.strip()[:80]
#-----------------------------------------------------------------------

# Abschnittsform: Name, Trennlinie, Inhalt, Trennlinie, danach Leerzeile oder Dateiende
#-----------------------------------------------------------------------
def checkSectionForm (L, i, add):
	name = L[i][2:]
	if i + 1 >= len(L) or L[i + 1] != SEP:
		add(i + 1, "Abschnitte", f"'{name}' ohne Trennlinie danach")
		return

	end = next((j for j in range(i + 2, len(L)) if L[j] == SEP), None)
	if end is None:
		add(i + 1, "Abschnitte", f"'{name}' ohne abschliessende Trennlinie")
	elif end + 1 < len(L) and L[end + 1].strip():
		add(end + 2, "Abschnitte", f"keine Leerzeile nach Abschnitt '{name}'")
#-----------------------------------------------------------------------

# Zeilenindex -> Abschnittsname ("# <Name>"), fuer jede Zeile zwischen den Trennlinien
#-----------------------------------------------------------------------
def sectionMap (L):
	owner = {}
	for i in range(len(L) - 1):
		if L[i].startswith("# ") and L[i + 1] == SEP:
			end = next((j for j in range(i + 2, len(L)) if L[j] == SEP), len(L))
			for j in range(i + 2, end):
				owner.setdefault(j, L[i])
	return owner
#-----------------------------------------------------------------------

# Art eines Imports: "standard", "extern" oder "eigene"
#-----------------------------------------------------------------------
def importKind (module, level, fileDir, base):
	if level > 0:
		return "eigene"

	top = module.split(".")[0]
	if top in sys.stdlib_module_names or top == "__future__":
		return "standard"

	# Modul oder Paket liegt im Ordner der Datei oder im Projektordner
	for d in (fileDir, base):
		if os.path.isfile(os.path.join(d, top + ".py")) or os.path.isdir(os.path.join(d, top)):
			return "eigene"
	return "extern"
#-----------------------------------------------------------------------

# Zeilennummern (1-basiert) innerhalb mehrzeiliger Strings
#-----------------------------------------------------------------------
def stringRows (tokens):
	rows = set()
	for t in tokens:
		if t.type in STRING_TOKENS and t.end[0] > t.start[0]:
			rows.update(range(t.start[0] + 1, t.end[0] + 1))
	return rows
#-----------------------------------------------------------------------

# Kommentare pruefen: Trennlinien, Leerzeichen nach #, Ausrichtung der Zeilenkommentare
#-----------------------------------------------------------------------
def checkComments (L, tokens, add):
	for t in tokens:
		if t.type != tokenize.COMMENT:
			continue

		n, col = t.start
		l = L[n - 1]
		c = t.string
		code = l[:col].rstrip()

		# Trennlinie
		if c.startswith("#-"):
			if c == SEP and l != SEP:
				add(n, "Trennlinie eingerueckt", short(l))
			elif c != SEP:
				add(n, "Trennlinie falsche Laenge", f"{len(c)} statt {len(SEP)} Zeichen")
			continue

		if c == "#":
			# Leere Kommentarzeile nur innerhalb eines Kommentarblocks erlaubt
			isCmt = lambda j: 0 < j <= len(L) and L[j - 1].strip().startswith("#") and not L[j - 1].strip().startswith("#-")
			if code or not (isCmt(n - 1) and isCmt(n + 1)):
				add(n, "leerer Kommentar")
		elif re.match(r"#\S", c) and not (n == 1 and c.startswith("#!")):
			add(n, "Kommentar ohne Leerzeichen nach #", short(l))

		# Zeilenkommentar hinter Code
		if code:
			ctx = f"{code.strip()[:40]}{' ...' if len(code.strip()) > 40 else ''}  {c[:40]}"
			if tabcol(l, col) != COMMENT_COL and tabcol(l, len(code)) < COMMENT_COL - 1:
				add(n, f"Zeilenkommentar nicht auf Spalte {COMMENT_COL}", f"Spalte {tabcol(l, col)}: {ctx}")
			if " " in l[len(code):col]:
				add(n, "Kommentar mit Leerzeichen statt Tabs ausgerichtet", ctx)
#-----------------------------------------------------------------------

# Logische Zeile pruefen: nach dem ':' eines Blockkopfs darf nichts mehr folgen
#-----------------------------------------------------------------------
def checkLogicalLine (toks, softLines, add):
	if not toks or toks[0].type != tokenize.NAME:
		return

	first = toks[0]
	isSoft = first.string in SOFT_COMPOUND and first.start[0] in softLines
	if first.string not in COMPOUND and not isSoft:
		return

	depth = 0
	for k, t in enumerate(toks):
		if t.type != tokenize.OP:
			continue
		if t.string in OPEN:
			depth += 1
		elif t.string in CLOSE:
			depth -= 1
		elif t.string == ":" and depth == 0:
			if k + 1 < len(toks):
				add(first.start[0], "Anweisung in derselben Zeile wie ':'", short(first.line))
			return
#-----------------------------------------------------------------------

# Token pruefen: Semikolon, Leerzeichen nach Schluesselwort, Bloecke in einer Zeile
#-----------------------------------------------------------------------
def checkTokens (tokens, softLines, add):
	skip = (tokenize.NL, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT)
	line = []
	for k, t in enumerate(tokens):
		if t.type == tokenize.OP and t.string == ";":
			add(t.start[0], "Semikolon", short(t.line))

		# "if(" statt "if (" (match nur, wenn es als Schluesselwort steht)
		isKeyword = t.string in SPACE_KEYWORDS or (t.string == "match" and t.start[0] in softLines)
		if t.type == tokenize.NAME and isKeyword and k + 1 < len(tokens):
			nxt = tokens[k + 1]
			if nxt.string == "(" and nxt.start == t.end:
				add(t.start[0], "kein Leerzeichen nach Schluesselwort", short(t.line))

		if t.type in (tokenize.NEWLINE, tokenize.ENDMARKER):
			checkLogicalLine(line, softLines, add)
			line = []
		elif t.type not in skip:
			line.append(t)
#-----------------------------------------------------------------------

# Erste Zeile (0-basiert) einer Definition, Dekoratoren eingeschlossen
#-----------------------------------------------------------------------
def defStart (node):
	return min([d.lineno for d in node.decorator_list] + [node.lineno]) - 1
#-----------------------------------------------------------------------

# Block "if __name__ == ...:" auf Modulebene
#-----------------------------------------------------------------------
def isMainBlock (node):
	if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
		return False
	return isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__"
#-----------------------------------------------------------------------

# Abschnitt einer Klasse/Funktion auf Modulebene pruefen, Rueckgabe: Anker fuer die Reihenfolge
#-----------------------------------------------------------------------
def checkDefSection (L, node, add):
	isClass = isinstance(node, ast.ClassDef)
	kind = "Klasse" if isClass else "Funktion"
	label = f"Klasse {node.name}" if isClass else f"Funktion {node.name} ()"
	k = defStart(node)

	# Davor: Kommentar + Trennlinie, Dekoratoren duerfen dazwischen stehen
	prev = L[max(0, k - 2):k]
	ok = len(prev) == 2 and prev[1] == SEP and re.match(r"# \S", prev[0])

	# Mehrere Klassen in einem Abschnitt, nur durch eine Trennlinie getrennt
	if isClass and len(prev) == 2 and prev[1] == SEP and re.match(r"\s+\S", prev[0]):
		ok = True
	if not ok:
		add(k + 1, f"{kind} ohne Kommentar+Trennlinie davor", short(L[node.lineno - 1]))

	# Danach: Trennlinie (eingerueckte Kommentare am Ende des Rumpfs zaehlen noch zum Rumpf)
	end = next((j for j in range(node.end_lineno, len(L)) if L[j].strip() and not re.match(r"\s+#", L[j])), None)
	if end is None or L[end] != SEP:
		add(node.end_lineno, f"{kind} ohne Trennlinie danach", label)
	elif end + 1 < len(L) and L[end + 1].strip() and not L[end + 1].startswith("class "):
		add(end + 2, "Abschnitte", f"keine Leerzeile nach {label}")
	return (k, RANK_CLASS if isClass else RANK_FUNC, label)
#-----------------------------------------------------------------------

# Import auf Modulebene pruefen: richtiger Import-Abschnitt, ein Modul je Zeile
#-----------------------------------------------------------------------
def checkImport (L, node, owners, fileDir, base, add):
	if isinstance(node, ast.Import):
		if len(node.names) > 1:
			add(node.lineno, "mehrere Module in einer import-Zeile", short(L[node.lineno - 1]))
		kinds = {importKind(a.name, 0, fileDir, base) for a in node.names}
	else:
		kinds = {importKind(node.module or "", node.level, fileDir, base)}

	owner = owners.get(node.lineno - 1)
	for kind in sorted(kinds):
		want = IMPORT_SECTIONS[kind]
		if owner == want:
			continue
		if owner in IMPORT_SECTIONS.values():
			add(node.lineno, "Import im falschen Abschnitt", f"{short(L[node.lineno - 1])}  ->  '{want[2:]}'")
		else:
			add(node.lineno, "Import ausserhalb der Import-Abschnitte", short(L[node.lineno - 1]))
#-----------------------------------------------------------------------

# Syntaxbaum pruefen, Rueckgabe: Anker der Klassen/Funktionen fuer die Reihenfolge
#-----------------------------------------------------------------------
def checkTree (L, tree, fileDir, base, add):
	anchors = []

	# Pruefungen fuer alle Knoten
	for node in ast.walk(tree):
		if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
			body = node.body
			if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
				add(body[0].lineno, "Docstring", short(L[body[0].lineno - 1]))

		if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
			m = re.match(r"^\s*(async\s+)?def\s+\w+(\s*)\(", L[node.lineno - 1])
			if m and m.group(2) == "":
				add(node.lineno, "kein Leerzeichen vor ( bei def", short(L[node.lineno - 1]))
			if not DUNDER.match(node.name) and not CAMEL.match(node.name):
				add(node.lineno, "Funktionsname nicht camelCase", node.name)
		elif isinstance(node, ast.ClassDef):
			m = re.match(r"^\s*class\s+\w+(\s*)\(", L[node.lineno - 1])
			if m and m.group(1) == "":
				add(node.lineno, "kein Leerzeichen vor ( bei class", short(L[node.lineno - 1]))
			if not PASCAL.match(node.name):
				add(node.lineno, "Klassenname nicht PascalCase", node.name)

			# Jede Methode mit Kommentar direkt darueber
			for item in node.body:
				if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
					k = defStart(item)
					if k == 0 or not L[k - 1].strip().startswith("# "):
						add(k + 1, "Methode ohne Kommentar davor", short(L[item.lineno - 1]))
		elif isinstance(node, ast.Match):
			last = node.cases[-1]
			if last.guard is not None or not (isinstance(last.pattern, ast.MatchAs) and last.pattern.pattern is None):
				add(node.lineno, "match ohne case _", short(L[node.lineno - 1]))
		elif isinstance(node, ast.ImportFrom) and any(a.name == "*" for a in node.names):
			add(node.lineno, "import *", short(L[node.lineno - 1]))

	# Pruefungen auf Modulebene
	owners = sectionMap(L)
	for node in tree.body:
		if isinstance(node, (ast.Import, ast.ImportFrom)):
			checkImport(L, node, owners, fileDir, base, add)
		elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
			anchors.append(checkDefSection(L, node, add))
		elif isMainBlock(node):
			k = node.lineno - 1
			if k < 2 or L[k - 2] != MAIN_SECTION or L[k - 1] != SEP:
				add(node.lineno, "Abschnitte", f"'if __name__ ...' nicht im Abschnitt '{MAIN_SECTION[2:]}'")
	return anchors
#-----------------------------------------------------------------------

# Zeilen, an denen match/case als Schluesselwort steht (weiche Schluesselwoerter)
#-----------------------------------------------------------------------
def softKeywordLines (tree):
	lines = set()
	for node in ast.walk(tree):
		if isinstance(node, ast.Match):
			lines.add(node.lineno)
			lines.update(c.pattern.lineno for c in node.cases)
	return lines
#-----------------------------------------------------------------------

# Positionen der bekannten Abschnitte fuer die Reihenfolgepruefung
#-----------------------------------------------------------------------
def orderAnchors (L, defs):
	anchors = list(defs)
	head = next((i for i, l in enumerate(L) if re.match(r"#\s*Titel\b", l)), None)
	if head is not None:
		anchors.append((head, 0, "Kopfblock"))
	for s, rank in SECTION_RANKS:
		if s in L:
			anchors.append((L.index(s), rank, s[2:]))
	anchors.sort(key=lambda a: a[0])
	return anchors
#-----------------------------------------------------------------------

# Kopfblock pruefen, Zeile 1 darf eine Shebang-Zeile sein
#-----------------------------------------------------------------------
def checkHead (L, fname, add):
	off = 1 if L[0].startswith("#!") else 0
	if off >= len(L) or L[off] != SEP:
		add(off + 1, "Kopfblock", f"Zeile {off + 1} ist keine Trennlinie")

	for k in HEAD_KEYS:
		found = [(i, l) for i, l in enumerate(L[:off + 12]) if re.match(rf"#\s*{k}\b", l)]
		if not found:
			add(0, "Kopfblock", f"'{k}' fehlt")
			continue

		i, l = found[0]
		if not re.match(rf"# {k}\t:", l):
			add(i + 1, "Kopfblock", f"'{k}' Format abweichend: {short(l)}")
		if k == "Titel" and not l.rstrip().endswith(fname):
			add(i + 1, "Kopfblock", f"Titel != Dateiname: {short(l)}")
		if k == "Sprache" and "Python" not in l:
			add(i + 1, "Kopfblock", f"Sprache nicht Python: {short(l)}")
		if k == "Datum" and not re.search(r"\d\d\.\d\d\.\d{4}", l):
			add(i + 1, "Kopfblock", f"Datum nicht TT.MM.JJJJ: {short(l)}")
		if k == "Autor" and "Diveturtle93" not in l:
			add(i + 1, "Kopfblock", f"Autor: {short(l)}")
#-----------------------------------------------------------------------

# Pflichtabschnitte pruefen: Import-Abschnitte und Variablen definieren
#-----------------------------------------------------------------------
def checkSections (L, add):
	for s in IMPORT_SECTIONS.values():
		pos = [i for i, l in enumerate(L) if l == s]
		if not pos:
			similar = [i + 1 for i, l in enumerate(L) if l.startswith("# Einfuegen") and l not in IMPORT_SECTIONS.values()]
			add(similar[0] if similar else 0, "Abschnitte", f"fehlt/abweichend: '{s[2:]}'")
		for i in pos[1:]:
			add(i + 1, "Abschnitte", f"doppelt: '{s[2:]}'")
		for i in pos:
			checkSectionForm(L, i, add)

	# "Variablen definieren" ist Pflicht, "Variablen einbinden" optional
	var = [(i, l) for i, l in enumerate(L) if re.match(r"#\s*Variable", l, re.I)]
	defs = [i for i, l in var if l == VAR_SECTION]
	incs = [i for i, l in var if l == VAR_INC_SECTION]
	for i, l in var:
		if l not in (VAR_SECTION, VAR_INC_SECTION) and re.match(r"#\s*Variable\w*\s+einbinden", l, re.I):
			add(i + 1, "Abschnitte", f"Variablen-Abschnitt heisst '{l.strip()}' statt '{VAR_INC_SECTION[2:]}'")
	if not defs:
		other = [i for i, l in var if l != VAR_INC_SECTION]
		if other:
			add(other[0] + 1, "Abschnitte", f"Variablen-Abschnitt heisst '{L[other[0]].strip()}' statt '{VAR_SECTION[2:]}'")
		else:
			add(0, "Abschnitte", f"fehlt: '{VAR_SECTION[2:]}'")
	for sec, pos in ((VAR_SECTION, defs), (VAR_INC_SECTION, incs)):
		for i in pos[1:]:
			add(i + 1, "Abschnitte", f"doppelt: '{sec[2:]}'")
		for i in pos:
			checkSectionForm(L, i, add)

	# Optionale Abschnitte mit festem Namen
	for s in (DESC_SECTION, VERSION_SECTION, CONST_SECTION, TABLE_SECTION, MAIN_SECTION):
		if s in L:
			checkSectionForm(L, L.index(s), add)

	# Datei endet mit einer Trennlinie (wie der Abschluss einer .h-Datei)
	tail = [(i, l) for i, l in enumerate(L) if l.strip()]
	if tail and tail[-1][1] != SEP:
		add(tail[-1][0] + 1, "Dateiende", "Datei endet nicht mit Trennlinie")
#-----------------------------------------------------------------------

# <NAME> fuer Debug-Symbol und Versions-Konstanten: Dateiname gross ohne Endung, bei __init__.py der Paketname
#-----------------------------------------------------------------------
def moduleName (path):
	name = os.path.splitext(os.path.basename(path))[0]
	if name == "__init__":
		name = os.path.basename(os.path.dirname(os.path.abspath(path)))
	return re.sub(r"\W", "_", name).upper()
#-----------------------------------------------------------------------

# Pflichtabschnitt "Definiere Debug-Symbole" mit DEBUG_<NAME> (auskommentiert zaehlt als vorhanden)
#-----------------------------------------------------------------------
def checkDebugSymbols (L, path, add):
	name = moduleName(path)
	for i, l in enumerate(L):
		if DEBUG_NAME.match(l) and l != DEBUG_SECTION:
			add(i + 1, "Abschnitte", f"Debug-Abschnitt heisst '{l.strip()}' statt '{DEBUG_SECTION[2:]}'")

	pos = [i for i, l in enumerate(L) if l == DEBUG_SECTION or DEBUG_NAME.match(l)]
	if not pos:
		add(0, "Debug-Symbole", f"Abschnitt '{DEBUG_SECTION[2:]}' fehlt")
		return

	checkSectionForm(L, pos[0], add)
	end = next((j for j in range(pos[0] + 2, len(L)) if L[j] == SEP), len(L))
	sym = re.compile(rf"^(#\s*)?DEBUG_{name}\s*=")
	if not any(sym.match(l) for l in L[pos[0] + 2:end]):
		add(pos[0] + 1, "Debug-Symbole", f"'DEBUG_{name} = ...' fehlt")
#-----------------------------------------------------------------------

# Pflichtabschnitt "Version definieren" mit <NAME>_MAJOR/_MINOR/_PATCH/_DEV
#-----------------------------------------------------------------------
def checkVersion (L, path, add):
	name = moduleName(path)
	if VERSION_SECTION not in L:
		add(0, "Version", f"Abschnitt '{VERSION_SECTION[2:]}' fehlt")

	missing = [v for v in VERSION_KEYS if not any(re.match(rf"{name}_{v}\s*=", l) for l in L)]
	if missing:
		add(0, "Version", f"Versions-Konstanten fehlen: {', '.join(name + '_' + v for v in missing)}")
#-----------------------------------------------------------------------

# Eine Datei pruefen, Rueckgabe: Liste von Issue, sortiert nach Zeile
# base: Projektordner, dort liegende Module/Pakete gelten als eigene Module
#-----------------------------------------------------------------------
def checkFile (path, base):
	raw = open(path, "rb").read()
	issues = []

	# Befund hinzufuegen
	def add (line, cat, info=""):
		issues.append(Issue(line, cat, info))

	# Leere Dateien (z. B. __init__.py) werden nicht geprueft
	if not raw.strip():
		return issues

	try:
		text = raw.decode("ascii")
		asciiOk = True
	except UnicodeDecodeError:
		text = raw.decode("utf-8", errors="replace")
		asciiOk = False

	rawLines = text.split("\n")
	L = [l[:-1] if l.endswith("\r") else l for l in rawLines]
	fname = os.path.basename(path)

	# Zeilenende
	lfLines = [i + 1 for i, l in enumerate(rawLines[:-1]) if not l.endswith("\r")]
	if lfLines:
		if len(lfLines) == len(rawLines) - 1:
			add(0, "Zeilenende", "nur LF statt CRLF")
		else:
			for n in lfLines:
				add(n, "Zeilenende", "LF statt CRLF")

	checkHead(L, fname, add)
	checkSections(L, add)
	checkDebugSymbols(L, path, add)
	checkVersion(L, path, add)

	# Quelltext ohne CR auswerten
	src = "\n".join(L)
	try:
		tree = ast.parse(src)
		tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))
	except (SyntaxError, tokenize.TokenError) as e:
		add(getattr(e, "lineno", 0) or 0, "Syntaxfehler", str(e))
		tree = None
		tokens = []

	# Zeilenweise Pruefungen
	inString = stringRows(tokens)
	for i, l in enumerate(L):
		n = i + 1
		if not asciiOk and any(ord(c) > 127 for c in l):
			add(n, "Nicht-ASCII", short(l))
		if n not in inString and re.match(r"^\t* +\S", l):
			add(n, "Einrueckung mit Leerzeichen", short(l))

	defs = []
	if tree is not None:
		checkComments(L, tokens, add)
		checkTokens(tokens, softKeywordLines(tree), add)
		defs = checkTree(L, tree, os.path.dirname(os.path.abspath(path)), base, add)

	# Reihenfolge der Abschnitte
	checkOrder(orderAnchors(L, defs), add)

	issues.sort(key=lambda x: x.line)
	return issues
#-----------------------------------------------------------------------

# Alle .py-Dateien einer Datei- oder Ordnerangabe
#-----------------------------------------------------------------------
def listPyFiles (path):
	if os.path.isfile(path):
		return [path] if path.endswith(".py") else []
	return sorted(glob.glob(os.path.join(path, "**", "*.py"), recursive=True))
#-----------------------------------------------------------------------

# Pfade/Globs zu Projekten aufloesen: {Projektname: (Basisordner, [Datei])}
# defaults: Git-Submodule ueberspringen, quiet: Ordner ohne .py-Dateien nicht melden
#-----------------------------------------------------------------------
def collectProjects (targets, excludes, defaults=True, quiet=False):
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

			# Einstellungen nur fuer Projektordner, nicht fuer einzeln angegebene Dateien
			exclDirs, inclDirs = projectSettings(base, defaults, "py") if os.path.isdir(m) else ([], [])
			for p in listPyFiles(m):
				p = os.path.abspath(p)
				if p in seen or any(re.search(x, p, re.I) for x in excludes):
					continue
				rel = normDir(os.path.relpath(p, base))
				if inDirs(rel, exclDirs) or (inclDirs and not inDirs(rel, inclDirs)):
					continue
				seen.add(p)
				projects.setdefault(proj, (base, []))[1].append(p)
			if os.path.isdir(m) and proj not in projects and not quiet:
				print(f"Hinweis: {proj}: keine Dateien zu pruefen", file=sys.stderr)
	return projects
#-----------------------------------------------------------------------

# Ueberschrift je Datei
#-----------------------------------------------------------------------
def fileTitle (p, base, iss):
	return f"{os.path.relpath(p, base)}  ({len(iss)} Befunde)"
#-----------------------------------------------------------------------

# Report-Text fuer ein Projekt erzeugen
#-----------------------------------------------------------------------
def buildReport (proj, base, results):
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
	out.append("Regeln       : PYTHON_CODING_STYLE.md")
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
		out.append(fileTitle(p, base, iss))
		out.append("-" * 72)
		if not iss:
			out.append("  keine Befunde")
		for x in iss:
			out.append(formatIssue(x))
	out.append("")
	return "\n".join(out)
#-----------------------------------------------------------------------

# Kommandozeile auswerten und Projekte pruefen
#-----------------------------------------------------------------------
def main ():
	# Nicht-ASCII-Zeichen aus geprueften Dateien duerfen die Ausgabe nicht abbrechen
	sys.stdout.reconfigure(errors="replace")

	here = os.path.dirname(os.path.abspath(__file__))
	repoDir = os.path.dirname(here)
	ownDir = os.path.dirname(repoDir)
	defaultTarget = os.path.join(ownDir, "*")
	defaultReports = os.path.join(repoDir, "reports")

	ap = argparse.ArgumentParser(description="Prueft Python-Dateien gegen PYTHON_CODING_STYLE.md")
	ap.add_argument("paths", nargs="*", help=f"Ordner, Dateien oder Glob-Muster (Standard: {defaultTarget})")
	ap.add_argument("-r", "--report", nargs="?", const=defaultReports, metavar="DIR",
		help=f"je Projekt Report DIR/{REPORT_SUBDIR}/<JJJJMMTT>_<Projekt>.txt und eine Uebersicht schreiben (Standard: {defaultReports})")
	ap.add_argument("-f", "--findings-only", action="store_true",
		help="mit -r nur Reports fuer Projekte mit Befunden schreiben, die Uebersicht enthaelt alle Projekte")
	ap.add_argument("-c", "--clean", nargs="?", const=defaultReports, metavar="DIR",
		help=f"alle Python-Reports in DIR/{REPORT_SUBDIR}/ loeschen (Standard: {defaultReports}), mit -r danach neu schreiben")
	ap.add_argument("-q", "--quiet", action="store_true", help="Dateien ohne Befund nicht anzeigen")
	ap.add_argument("-s", "--summary", action="store_true", help="nur Zusammenfassung ausgeben")
	ap.add_argument("-x", "--exclude", action="append", default=[], metavar="REGEX", help="zusaetzlich ausschliessen")
	ap.add_argument("--no-default-exclude", action="store_true", help="virtuelle Umgebungen, Caches, Build-Ordner und Submodule mitpruefen")
	args = ap.parse_args()

	if args.clean:
		print(f"{cleanReports(os.path.join(args.clean, REPORT_SUBDIR))} Reports geloescht")
		if not args.report:
			return 0

	excludes = args.exclude + ([] if args.no_default_exclude else DEFAULT_EXCLUDE)
	projects = collectProjects(args.paths or [defaultTarget], excludes, not args.no_default_exclude, not args.paths)
	if not projects:
		print("Keine .py-Dateien gefunden.")
		return 2

	reportDir = os.path.join(args.report, REPORT_SUBDIR) if args.report else None
	if reportDir:
		os.makedirs(reportDir, exist_ok=True)
	datePrefix = datetime.date.today().strftime("%Y%m%d")

	total = collections.Counter()
	nFiles = 0
	nClean = 0
	rows = []
	for proj, (base, files) in projects.items():
		results = [(p, checkFile(p, base)) for p in files]
		nFiles += len(results)
		nClean += sum(1 for _, i in results if not i)
		for _, iss in results:
			for x in iss:
				total[x.cat] += 1

		if reportDir:
			nIssues = sum(len(i) for _, i in results)
			written = nIssues > 0 or not args.findings_only
			rows.append((proj, len(results), sum(1 for _, i in results if not i), nIssues, written))
			if not written:
				print(f"{proj:30} {0:6} Befunde  -> kein Report")
				continue
			path = os.path.join(reportDir, f"{datePrefix}_{proj}.txt")
			with open(path, "w", encoding="ascii", errors="replace", newline="\r\n") as f:
				f.write(buildReport(proj, base, results))
			print(f"{proj:30} {nIssues:6} Befunde  -> {os.path.relpath(path)}")
			continue

		if args.summary:
			continue
		for p, iss in results:
			if args.quiet and not iss:
				continue
			print(f"\n### {proj}/{fileTitle(p, base, iss)}")
			for x in iss:
				print(formatIssue(x))

	if reportDir:
		writeOverview(reportDir, datePrefix, "Python", "PYTHON_CODING_STYLE.md", rows, total)

	print("\n=== Befunde je Kategorie ===")
	for c, n in total.most_common():
		print(f"{n:6}  {c}")
	print(f"\nGeprueft: {len(projects)} Projekte, {nFiles} Dateien, davon {nClean} ohne Befund")
	return 1 if total else 0
#-----------------------------------------------------------------------

# Hauptprogramm
#-----------------------------------------------------------------------
if __name__ == "__main__":
	sys.exit(main())
#-----------------------------------------------------------------------
