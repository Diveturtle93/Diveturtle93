#!/usr/bin/env python3
#-----------------------------------------------------------------------
# Titel	:	c_stylecheck.py
#-----------------------------------------------------------------------
# Sprache	:	Python
# Datum	:	08.10.2026
# Version	:	1.0
# Autor	:	Diveturtle93
# Projekt	:	Diveturtle93
# Quelle	:
#-----------------------------------------------------------------------

# Beschreibung
#-----------------------------------------------------------------------
# Prueft C-Dateien (.c/.h) gegen C_CODING_STYLE.md
# Aufruf:
#   py tools/c_stylecheck.py                      -> alle Ordner ../STM32_* neben diesem Repo
#   py tools/c_stylecheck.py ../STM32_Canbus      -> einzelner Ordner
#   py tools/c_stylecheck.py ../EAuto_* ../IMD_*  -> beliebige Ordner / Glob-Muster
#   py tools/c_stylecheck.py ../STM32_Millis/millis.h   -> einzelne Datei
#   py tools/c_stylecheck.py -r                   -> Reports nach reports/<JJJJMMTT>_<Projekt>.txt
#   py tools/c_stylecheck.py -r -f                -> Reports nur fuer Projekte mit Befunden
#   py tools/c_stylecheck.py -c                   -> alle Reports in reports/ loeschen
#   py tools/c_stylecheck.py -c out               -> alle Reports in out/ loeschen
#
# Optionen:
#   -r / --report [DIR]  je Projekt einen Report <JJJJMMTT>_<Projekt>.txt schreiben (Standard: reports/)
#   -f / --findings-only mit -r nur Reports fuer Projekte mit Befunden schreiben
#   -c / --clean [DIR]   alle Reports <JJJJMMTT>_<Projekt>.txt im Ordner loeschen, egal welches
#                        Projekt (Standard: reports/), mit -r werden danach neue Reports geschrieben
#   -q / --quiet         Dateien ohne Befund nicht anzeigen
#   -s / --summary       nur Zusammenfassung je Kategorie
#   -x / --exclude REGEX zusaetzliche Pfade ausschliessen (mehrfach moeglich)
#   --no-default-exclude HAL/CMSIS-Dateien und Submodule mitpruefen, CubeMX-Dateien vollstaendig pruefen
#
# Ein Projekt ist jeder Ordner, der als Pfad angegeben oder per Glob gefunden wird.
#
# Automatisch uebersprungen: Drivers/, Middlewares/, Debug/, Release/, build/,
# HAL-/Startup-/System-Dateien sowie Git-Submodule aus der .gitmodules des Projekts
# (werden separat geprueft).
#
# Von STM32CubeMX generierte Dateien ("USER CODE BEGIN") werden nur zwischen
# USER CODE BEGIN und USER CODE END geprueft, ohne den Bereich "Header" und ohne
# Pruefungen der Dateistruktur (Kopfblock, Abschnitte, Header, Reihenfolge).
#
# Projekt-Einstellungen (optional): Datei .c_stylecheck im Projektordner
#   [stylecheck]
#   exclude = Lib, Test           -> diese Ordner zusaetzlich ausschliessen
#   include = Core, Application   -> nur diese Ordner pruefen
# Ordner oder Dateien werden relativ zum Projektordner angegeben, mehrere mit Komma getrennt.
#
# Rueckgabewert: 0 = keine Befunde, 1 = Befunde vorhanden, 2 = keine Dateien gefunden
#-----------------------------------------------------------------------

# Einfuegen der standard Module
#-----------------------------------------------------------------------
import argparse
import collections
import configparser
import datetime
import glob
import os
import re
import sys
#-----------------------------------------------------------------------

# Einfuegen der externen Module
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------

# Einfuegen der eigenen Module
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------

# Konstanten definieren
#-----------------------------------------------------------------------
CONFIG_FILE = ".c_stylecheck"												# Projekt-Einstellungen
SEP = "//" + "-" * 70														# Trennlinie, 72 Zeichen
COMMENT_COL = 77															# Spalte der Zeilenkommentare
TAB_WIDTH = 4																# Tabbreite

# Generierte bzw. fremde Dateien (STM32CubeMX, HAL, CMSIS, Build-Ausgaben)
DEFAULT_EXCLUDE = [
	r"[\\/]\.git[\\/]",
	r"[\\/](Drivers|Middlewares|CMSIS|Debug|Release|build)[\\/]",
	r"stm32\w*_hal(?!_msp\.c$)",
	r"system_stm32",
	r"startup_",
	r"syscalls\.c$",
	r"sysmem\.c$",
]

INC_SECTIONS = [
	"// Einfuegen der standard Include-Dateien",
	"// Einfuegen der STM Include-Dateien",
	"// Einfuegen der eigenen Include-Dateien",
]
GUARD_SECTION = "// Sicherheitssymbol"
DEBUG_SECTION = "// Definiere Debug-Symbole"
DEBUG_NAME = re.compile(r"//\s*\w+\s+Debug[\s-]*Symbol", re.I)
VAR_SECTION = "// Variablen definieren"
VAR_INC_SECTION = "// Variablen einbinden"
HEAD_KEYS = ["Titel", "Sprache", "Datum", "Version", "Autor", "Projekt", "Quelle"]
KEYWORDS = {"if", "for", "while", "switch", "return", "sizeof", "else"}

# CubeMX-Dateien: nur Bereiche zwischen USER CODE BEGIN/END pruefen
USER_CODE = re.compile(r"^\s*/\*\s*USER CODE (BEGIN|END)\s+(.+?)\s*\*/\s*$")
USER_CODE_SKIP = {"Header"}
MARKER_CAT = "USER CODE Marker"

# Pruefungen der Dateistruktur, im USER-CODE-Modus nicht sinnvoll
FILE_CATS = {"Kopfblock", "Abschnitte", "Header", "Debug-Symbole", "Reihenfolge"}

# switch/case: Fall-through-Markierung, Blockende, case-Marke
FALLTHROUGH = re.compile(r"^\s*(//\s*fall(s)?[ -]?thr(ough|u)\b.*|__attribute__\s*\(\(\s*fallthrough\s*\)\)\s*;.*|\[\[fallthrough\]\]\s*;.*)$", re.I)
TERMINATOR = re.compile(r"^\s*(break|continue|return\b.*|goto\s+\w+)\s*;$")
LABEL = re.compile(r"^\s*(case\b.*|default\s*):\s*$")
#-----------------------------------------------------------------------

# Ein Befund: Zeile (0 = ganze Datei), Kategorie, Zusatzinfo
#-----------------------------------------------------------------------
class Issue:
	# Befund anlegen
	def __init__ (self, line, cat, info=""):
		self.line = line
		self.cat = cat
		self.info = info
#-----------------------------------------------------------------------

# Variablen definieren
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------

# Spalte (1-basiert) eines Zeichens bei Tabbreite 4
#-----------------------------------------------------------------------
def tabcol (line, idx):
	col = 0
	for ch in line[:idx]:
		col = (col // TAB_WIDTH + 1) * TAB_WIDTH if ch == "\t" else col + 1
	return col + 1
#-----------------------------------------------------------------------

# Naechste nicht leere Zeile nach Zeile i
#-----------------------------------------------------------------------
def nextCodeLine (lines, i):
	return next((x for x in lines[i + 1:] if x.strip()), "")
#-----------------------------------------------------------------------

# Naechste Anweisung nach Zeile i: ueberspringt Leerzeilen, Kommentare, Praeprozessor-
# Zeilen und alternative if-Bedingungen in #if/#ifdef-Zweigen
#-----------------------------------------------------------------------
def nextStatement (L, i):
	crossedPp = False
	for x in L[i + 1:]:
		s = stripCode(x).strip()
		if not s:
			continue
		if s.startswith("#"):
			crossedPp = True
			continue
		if crossedPp and re.match(r"(if|else if)\s*\(.*\)$", s):
			continue
		return s
	return ""
#-----------------------------------------------------------------------

# Zeile fuer die Ausgabe kuerzen
#-----------------------------------------------------------------------
def short (l):
	return l.strip()[:80]
#-----------------------------------------------------------------------

# Code ohne Strings, Zeichenkonstanten und //-Kommentar
#-----------------------------------------------------------------------
def stripCode (l):
	code = re.sub(r'"(\\.|[^"])*"', '""', l)
	code = re.sub(r"'(\\.|[^'])*'", "''", code)
	return re.sub(r"//.*", "", code).rstrip()
#-----------------------------------------------------------------------

# case-Block ohne break/return, dem eine weitere Marke folgt, braucht "// fall through"
#-----------------------------------------------------------------------
def checkFallthrough (L, i, add):
	start = next(j for j in range(i + 1, len(L)) if L[j].strip())
	depth = 0
	end = None
	for j in range(start, len(L)):
		c = stripCode(L[j])
		depth += c.count("{") - c.count("}")
		if depth == 0:
			end = j
			break
	if end is None:
		return

	after = next((x for x in L[end + 1:] if stripCode(x).strip()), "")
	if not LABEL.match(stripCode(after)):
		return

	body = [x for x in L[start + 1:end] if x.strip()]
	if not body:
		return
	if FALLTHROUGH.match(body[-1]):
		return

	lastCode = next((stripCode(x) for x in reversed(body) if stripCode(x).strip()), "")
	if TERMINATOR.match(lastCode):
		return
	add(i + 1, "case ohne break (Fall-through nicht markiert)", short(L[i]))
#-----------------------------------------------------------------------

# Abschnittsform: Name, Trennlinie, Inhalt, Trennlinie, danach Leerzeile oder Dateiende
#-----------------------------------------------------------------------
def checkSectionForm (L, i, add):
	name = L[i].strip()[3:]
	if i + 1 >= len(L) or L[i + 1] != SEP:
		add(i + 1, "Abschnitte", f"'{name}' ohne Trennlinie danach")
		return

	end = next((j for j in range(i + 2, len(L)) if L[j] == SEP), None)
	if end is None:
		add(i + 1, "Abschnitte", f"'{name}' ohne abschliessende Trennlinie")
	elif end + 1 < len(L) and L[end + 1].strip():
		add(end + 2, "Abschnitte", f"keine Leerzeile nach Abschnitt '{name}'")
#-----------------------------------------------------------------------

# Header mit passender .c-Datei braucht 'Definiere Debug-Symbole' mit DEBUG_<NAME> in #ifdef DEBUG
#-----------------------------------------------------------------------
def checkDebugSymbols (L, name, add):
	# Falsch benannte Abschnitte zaehlen hier mit, der Name wird unter "Abschnitte" gemeldet
	pos = [i for i, l in enumerate(L) if l == DEBUG_SECTION or DEBUG_NAME.match(l)]
	if not pos:
		add(0, "Debug-Symbole", f"Abschnitt '{DEBUG_SECTION[3:]}' fehlt (passende .c-Datei vorhanden)")
		return

	checkSectionForm(L, pos[0], add)
	sym = re.compile(rf"^(//)?\s*#define\s+DEBUG_{name}\b")
	inIfdef = False
	for l in L[pos[0] + 1:]:
		if re.match(r"#ifdef\s+DEBUG\b", l):
			inIfdef = True
		elif l.startswith("#endif"):
			inIfdef = False
		elif inIfdef and sym.match(l):
			return
	add(pos[0] + 1, "Debug-Symbole", f"'#define DEBUG_{name}' innerhalb von '#ifdef DEBUG' fehlt")
#-----------------------------------------------------------------------

# Reihenfolge der Abschnitte: anchors = [(Zeilenindex, Rang, Name)] in Dateireihenfolge
# Gemeldet werden nur Abschnitte ausserhalb der laengsten korrekt sortierten Folge
#-----------------------------------------------------------------------
def checkOrder (anchors, add):
	n = len(anchors)
	best = [1] * n
	prev = [-1] * n
	for i in range(n):
		for j in range(i):
			if anchors[j][1] <= anchors[i][1] and best[j] + 1 > best[i]:
				best[i] = best[j] + 1
				prev[i] = j

	keep = set()
	end = max(range(n), key=lambda i: (best[i], i)) if n else -1
	while end >= 0:
		keep.add(end)
		end = prev[end]

	for i, (line, rank, label) in enumerate(anchors):
		if i in keep:
			continue
		later = next((a for j, a in enumerate(anchors[:i]) if j in keep and a[1] > rank), None)
		if later:
			add(line + 1, "Reihenfolge", f"'{label}' steht nach '{later[2]}'")
			continue
		earlier = next((a for j, a in enumerate(anchors) if j > i and j in keep and a[1] < rank), None)
		if earlier:
			add(line + 1, "Reihenfolge", f"'{label}' steht vor '{earlier[2]}'")
#-----------------------------------------------------------------------

# Positionen der bekannten Abschnitte fuer die Reihenfolgepruefung
#-----------------------------------------------------------------------
def orderAnchors (L, isHeader, guard, firstFunc):
	anchors = []

	# Erste Zeile, auf die pred zutrifft, als Anker eintragen
	def first (pred, rank, label):
		pos = next((i for i, l in enumerate(L) if pred(l)), None)
		if pos is not None:
			anchors.append((pos, rank, label))

	first(lambda l: re.match(r"//\s*Titel\b", l), 0, "Kopfblock")
	if isHeader:
		first(lambda l: l == "#pragma once", 1, GUARD_SECTION[3:])
		first(lambda l: l == f"#ifndef {guard}", 2, "Dateiheader definieren")
	for k, s in enumerate(INC_SECTIONS):
		first(lambda l, s=s: l == s, 3 + k, s[3:])

	if isHeader:
		first(lambda l: l == DEBUG_SECTION or DEBUG_NAME.match(l), 6, DEBUG_SECTION[3:])
		first(lambda l: l == "// Version definieren", 7, "Version definieren")
		first(lambda l: l == "// Konstanten definieren", 8, "Konstanten definieren")

		# Typedef-Abschnitte haben beschreibende Namen, es zaehlen alle
		for i, l in enumerate(L[:-1]):
			if re.match(r"//.*typedef", l, re.I) and L[i + 1] == SEP:
				anchors.append((i, 9, l[3:].strip()))
		first(lambda l: l == "// Definiere globale Variablen", 10, "Definiere globale Variablen")
		first(lambda l: l == "// Funktionen definieren", 11, "Funktionen definieren")
		first(lambda l: l == f"#endif /* {guard} */", 12, "Abschluss")
	else:
		first(lambda l: l == VAR_SECTION, 6, VAR_SECTION[3:])
		first(lambda l: l == VAR_INC_SECTION, 7, VAR_INC_SECTION[3:])
		if firstFunc:
			anchors.append((firstFunc[0], 8, f"Funktion {firstFunc[1]} ()"))

	anchors.sort(key=lambda a: a[0])
	return anchors
#-----------------------------------------------------------------------

# Zeilenindizes innerhalb der USER CODE Bereiche (ohne Markerzeilen und USER_CODE_SKIP)
# Rueckgabe: (Menge der Zeilenindizes, [Issue fuer fehlerhafte Marker])
#-----------------------------------------------------------------------
def userCodeLines (L):
	active = set()
	markers = []
	openMarker = None
	for i, l in enumerate(L):
		m = USER_CODE.match(l)
		if not m:
			if openMarker and openMarker[1] not in USER_CODE_SKIP:
				active.add(i)
			continue

		kind, name = m.groups()
		if kind == "BEGIN":
			if openMarker:
				markers.append(Issue(i + 1, MARKER_CAT, f"BEGIN {name} vor END {openMarker[1]}"))
			openMarker = (i, name)
		else:
			if not openMarker or openMarker[1] != name:
				markers.append(Issue(i + 1, MARKER_CAT, f"END {name} ohne passendes BEGIN"))
			openMarker = None

	if openMarker:
		markers.append(Issue(openMarker[0] + 1, MARKER_CAT, f"BEGIN {openMarker[1]} ohne END"))
	return active, markers
#-----------------------------------------------------------------------

# Basisnamen (klein) aller .c-Dateien unterhalb eines Ordners, inkl. ausgeschlossener
#-----------------------------------------------------------------------
def cBasenames (base):
	files = glob.glob(os.path.join(base, "**", "*.c"), recursive=True)
	return {os.path.splitext(os.path.basename(p))[0].lower() for p in files}
#-----------------------------------------------------------------------

# Eine Datei pruefen, Rueckgabe: Liste von Issue, sortiert nach Zeile
# cNames: Basisnamen der .c-Dateien im Projekt (zusaetzlich: Ordner der Datei und ../Src)
# userCode: nur Zeilen zwischen USER CODE BEGIN/END pruefen (CubeMX-Dateien)
#-----------------------------------------------------------------------
def checkFile (path, cNames=None, userCode=False):
	raw = open(path, "rb").read()
	issues = []

	# Befund hinzufuegen
	def add (line, cat, info=""):
		issues.append(Issue(line, cat, info))

	try:
		text = raw.decode("ascii")
		asciiOk = True
	except UnicodeDecodeError:
		text = raw.decode("utf-8", errors="replace")
		asciiOk = False

	rawLines = text.split("\n")
	L = [l[:-1] if l.endswith("\r") else l for l in rawLines]
	fname = os.path.basename(path)
	isHeader = fname.endswith(".h")
	name = os.path.splitext(fname)[0].upper()

	# Zeilenende
	lfLines = [i + 1 for i, l in enumerate(rawLines[:-1]) if not l.endswith("\r")]
	if lfLines:
		if len(lfLines) == len(rawLines) - 1:
			add(0, "Zeilenende", "nur LF statt CRLF")
		else:
			for n in lfLines:
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

	# Debug-Symbole (ein Name, egal ob ein oder mehrere Symbole)
	for i, l in enumerate(L):
		if DEBUG_NAME.match(l) and l != DEBUG_SECTION:
			add(i + 1, "Abschnitte", f"Debug-Abschnitt heisst '{l.strip()}' statt '{DEBUG_SECTION[3:]}'")

	if isHeader:
		guard = f"INC_{name}_H_"
		if "#pragma once" not in L:
			add(0, "Header", "#pragma once fehlt")
		elif GUARD_SECTION not in L:
			idx = L.index("#pragma once")
			add(max(idx - 1, 1), "Header", f"Abschnittsname '{L[max(idx - 2, 0)].strip()}' statt '{GUARD_SECTION[3:]}'")
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
		hasProto = any(re.match(r"^\w[\w\s\*]*\s\*?\w+\s*\(.*\)\s*;", l) for l in L)
		if hasProto and "// Funktionen definieren" not in L:
			add(0, "Header", "Abschnitt 'Funktionen definieren' fehlt")

		d = os.path.dirname(os.path.abspath(path))
		local = cBasenames(d) | cBasenames(os.path.join(os.path.dirname(d), "Src"))
		if name.lower() in (cNames or set()) | local:
			checkDebugSymbols(L, name, add)
	else:
		# "Variablen definieren" ist Pflicht, "Variablen einbinden" optional (nur Schreibweise + Form)
		var = [(i, l) for i, l in enumerate(L) if re.match(r"//\s*Variable", l, re.I)]
		defs = [i for i, l in var if l == VAR_SECTION]
		incs = [i for i, l in var if l == VAR_INC_SECTION]
		for i, l in var:
			if l not in (VAR_SECTION, VAR_INC_SECTION) and re.match(r"//\s*Variable\w*\s+einbinden", l, re.I):
				add(i + 1, "Abschnitte", f"Variablen-Abschnitt heisst '{l.strip()}' statt '{VAR_INC_SECTION[3:]}'")
		if not defs:
			other = [i for i, l in var if l != VAR_INC_SECTION]
			if other:
				add(other[0] + 1, "Abschnitte", f"Variablen-Abschnitt heisst '{L[other[0]].strip()}' statt '{VAR_SECTION[3:]}'")
			else:
				add(0, "Abschnitte", f"fehlt: '{VAR_SECTION[3:]}'")
		for sec, pos in ((VAR_SECTION, defs), (VAR_INC_SECTION, incs)):
			for i in pos[1:]:
				add(i + 1, "Abschnitte", f"doppelt: '{sec[3:]}'")
			for i in pos:
				checkSectionForm(L, i, add)

	# Zeilenweise Pruefungen
	inBlock = False
	firstFunc = None
	for i, l in enumerate(L):
		n = i + 1
		s = l.strip()
		if not asciiOk and any(ord(c) > 127 for c in l):
			add(n, "Nicht-ASCII", short(l))
		if s.startswith("//-") and l != SEP:
			add(n, "Trennlinie falsche Laenge", f"{len(l)} statt {len(SEP)} Zeichen")
		if re.match(r"^ +\S", l) and not inBlock:
			add(n, "Einrueckung mit Leerzeichen", short(l))
		if "/*" in l and not re.match(r"#endif /\* .* \*/", s):
			add(n, "/* */-Kommentar", short(l))
		if "/*" in l and "*/" not in l:
			inBlock = True
		if "*/" in l:
			inBlock = False
		if re.search(r"/\*\*|///|[@\\](brief|param|return)\b", l):
			add(n, "Doxygen", short(l))
		if 'extern "C"' in l:
			add(n, 'extern "C"', short(l))
		if re.match(r"//[^\s\-/]", s):
			add(n, "Kommentar ohne Leerzeichen nach //", short(l))
		if s == "//":
			# Leere Kommentarzeile nur innerhalb eines Kommentarblocks erlaubt
			isCmt = lambda j: 0 <= j < len(L) and L[j].strip().startswith("//") and not L[j].strip().startswith("//-")
			if not (isCmt(i - 1) and isCmt(i + 1)):
				add(n, "leerer Kommentar")

		# Code ohne Kommentare und Strings
		code = re.sub(r'"(\\.|[^"])*"', '""', l)
		code = re.sub(r"//.*", "", code).rstrip()

		if code.endswith("{") and code.strip() != "{" and not re.search(r"=\s*\{$", code) and not inBlock:
			add(n, "K&R-Klammer (nicht Allman)", short(l))
		if re.match(r"\s*(case\b.*|default\s*):\s*$", code):
			# Mehrere Marken untereinander erlaubt, nur die letzte braucht den Block
			# Ausnahme: direkt folgendes einzelnes "return ...;" oder "break;" braucht keinen Block
			nxt = re.sub(r"//.*", "", nextCodeLine(L, i)).strip()
			if nxt != "{" and not re.match(r"(case\b.*|default\s*):$", nxt) and not re.match(r"(return\b.*|break\s*);$", nxt):
				add(n, "case ohne { }-Block", short(l))
			elif nxt == "{":
				checkFallthrough(L, i, add)
		if re.match(r"\s*switch\s*\(", code):
			depth = 0
			found = False
			for x in L[i + 1:]:
				depth += x.count("{") - x.count("}")
				if re.match(r"\s*default\s*:", x):
					found = True
				if depth <= 0 and "}" in x:
					break
			if not found:
				add(n, "switch ohne default", short(l))
		if re.match(r"\s*(if|else if|for|while)\s*\(.*\)\s*$", code) or re.match(r"\s*else\s*$", code):
			nxt = nextStatement(L, i)
			isIf = re.match(r"\s*(if|else)\b", code)
			if nxt != "{" and not (isIf and re.match(r"return\b.*;$", nxt)):
				add(n, "if/else/for ohne { }", short(l))
		if re.match(r"\s*(if|for|while|switch)\(", code):
			add(n, "kein Leerzeichen nach Schluesselwort", short(l))

		# Funktionsdefinition / Prototyp (nur am Zeilenanfang)
		fm = re.match(r"^(?!typedef|#|return|else|static inline)[A-Za-z_][\w\s\*]*?\b([A-Za-z_]\w*)(\s*)\((.*)\)\s*(;)?\s*$", code)
		if fm and fm.group(1) not in KEYWORDS:
			isDef = fm.group(4) is None and nextCodeLine(L, i).strip() == "{"
			isProto = fm.group(4) == ";"
			if isDef or isProto:
				if fm.group(2) == "":
					add(n, "kein Leerzeichen vor ( bei Deklaration/Definition", short(l))
				if fm.group(3).strip() == "":
					add(n, "leere Parameterliste statt (void)", short(l))
			if isDef:
				if firstFunc is None:
					firstFunc = (i, fm.group(1))

				# #if / #ifdef zwischen Trennlinie und Funktion sind erlaubt
				k = i
				while k > 0 and re.match(r"\s*#\s*(if|ifdef|ifndef|elif)\b", L[k - 1]):
					k -= 1
				prev = L[max(0, k - 2):k]
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

	# Reihenfolge der Abschnitte
	checkOrder(orderAnchors(L, isHeader, f"INC_{name}_H_", firstFunc), add)

	# USER-CODE-Modus: Befunde nur aus den Bereichen, Zeilenende-Befund fuer die ganze Datei bleibt
	if userCode:
		active, markers = userCodeLines(L)
		issues = [x for x in issues if x.cat not in FILE_CATS
			and ((x.line - 1) in active or (x.line == 0 and x.cat == "Zeilenende"))] + markers

	issues.sort(key=lambda x: x.line)
	return issues
#-----------------------------------------------------------------------

# Von STM32CubeMX generierte Datei (enthaelt USER CODE Marker)
#-----------------------------------------------------------------------
def isGenerated (path):
	with open(path, "rb") as f:
		return b"USER CODE BEGIN" in f.read()
#-----------------------------------------------------------------------

# Alle .c/.h-Dateien einer Datei- oder Ordnerangabe
#-----------------------------------------------------------------------
def listCFiles (path):
	if os.path.isfile(path):
		return [path] if path.endswith((".c", ".h")) else []
	return sorted(glob.glob(os.path.join(path, "**", "*.[ch]"), recursive=True))
#-----------------------------------------------------------------------

# Ordnerangabe vereinheitlichen: Schraegstriche, klein, ohne fuehrendes/abschliessendes /
#-----------------------------------------------------------------------
def normDir (d):
	return d.strip().replace("\\", "/").strip("/").lower()
#-----------------------------------------------------------------------

# Projekt-Einstellungen: ([auszuschliessende Ordner], [zu pruefende Ordner]), relativ zum Projekt
# submodules: Pfade aus .gitmodules ausschliessen
#-----------------------------------------------------------------------
def projectSettings (base, submodules=True):
	excl = []
	incl = []
	gitmodules = os.path.join(base, ".gitmodules")
	if submodules and os.path.isfile(gitmodules):
		with open(gitmodules, encoding="utf-8", errors="replace") as f:
			excl += [m.group(1) for m in re.finditer(r"^\s*path\s*=\s*(.+?)\s*$", f.read(), re.M)]

	cfgPath = os.path.join(base, CONFIG_FILE)
	if os.path.isfile(cfgPath):
		cfg = configparser.ConfigParser(inline_comment_prefixes=("#", ";"))
		cfg.read(cfgPath, encoding="utf-8")
		sec = cfg["stylecheck"] if cfg.has_section("stylecheck") else {}
		for k in sec:
			if k not in ("exclude", "include"):
				print(f"Warnung: {cfgPath}: unbekannter Eintrag '{k}'", file=sys.stderr)
		excl += sec.get("exclude", "").split(",")
		incl += sec.get("include", "").split(",")
	return [normDir(d) for d in excl if d.strip()], [normDir(d) for d in incl if d.strip()]
#-----------------------------------------------------------------------

# Liegt die Datei (relativ zum Projekt) in einem der Ordner?
#-----------------------------------------------------------------------
def inDirs (rel, dirs):
	return any(rel == d or rel.startswith(d + "/") for d in dirs)
#-----------------------------------------------------------------------

# Pfade/Globs zu Projekten aufloesen: {Projektname: (Basisordner, [(Datei, nur USER CODE)])}
# defaults: Git-Submodule ueberspringen, CubeMX-Dateien nur in den USER CODE Bereichen pruefen
#-----------------------------------------------------------------------
def collectProjects (targets, excludes, defaults=True):
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
			exclDirs, inclDirs = projectSettings(base, defaults) if os.path.isdir(m) else ([], [])
			for p in listCFiles(m):
				p = os.path.abspath(p)
				if p in seen or any(re.search(x, p, re.I) for x in excludes):
					continue
				rel = normDir(os.path.relpath(p, base))
				if inDirs(rel, exclDirs) or (inclDirs and not inDirs(rel, inclDirs)):
					continue
				seen.add(p)
				projects.setdefault(proj, (base, []))[1].append((p, defaults and isGenerated(p)))
			if os.path.isdir(m) and proj not in projects:
				print(f"Hinweis: {proj}: keine Dateien zu pruefen", file=sys.stderr)
	return projects
#-----------------------------------------------------------------------

# Alle Reports <JJJJMMTT>_<Projekt>.txt im Ordner loeschen, Rueckgabe: Anzahl
#-----------------------------------------------------------------------
def cleanReports (reportDir):
	if not os.path.isdir(reportDir):
		print(f"Hinweis: Report-Ordner '{reportDir}' nicht vorhanden", file=sys.stderr)
		return 0

	pattern = re.compile(r"^\d{8}_.+\.txt$", re.I)
	count = 0
	for f in sorted(os.listdir(reportDir)):
		path = os.path.join(reportDir, f)
		if pattern.match(f) and os.path.isfile(path):
			os.remove(path)
			print(f"geloescht: {os.path.relpath(path)}")
			count += 1
	return count
#-----------------------------------------------------------------------

# Einen Befund als Ausgabezeile formatieren
#-----------------------------------------------------------------------
def formatIssue (issue):
	where = f"Z.{issue.line:5}" if issue.line else "Datei  "
	info = f"  ->  {issue.info}" if issue.info else ""
	return f"  {where}  [{issue.cat}]{info}"
#-----------------------------------------------------------------------

# Ueberschrift je Datei, userCode: Dateien, die nur in den USER CODE Bereichen geprueft wurden
#-----------------------------------------------------------------------
def fileTitle (p, base, iss, userCode):
	mode = ", nur USER CODE" if p in userCode else ""
	return f"{os.path.relpath(p, base)}  ({len(iss)} Befunde{mode})"
#-----------------------------------------------------------------------

# Report-Text fuer ein Projekt erzeugen
#-----------------------------------------------------------------------
def buildReport (proj, base, results, userCode=()):
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
	out.append("Regeln       : C_CODING_STYLE.md")
	out.append(f"Geprueft     : {len(results)} Dateien, davon {clean} ohne Befund, {len(userCode)} nur USER CODE")
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
		out.append(fileTitle(p, base, iss, userCode))
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
	here = os.path.dirname(os.path.abspath(__file__))
	repoDir = os.path.dirname(here)
	ownDir = os.path.dirname(repoDir)
	defaultTarget = os.path.join(ownDir, "STM32_*")
	defaultReports = os.path.join(repoDir, "reports")

	ap = argparse.ArgumentParser(description="Prueft C-Dateien gegen C_CODING_STYLE.md")
	ap.add_argument("paths", nargs="*", help=f"Ordner, Dateien oder Glob-Muster (Standard: {defaultTarget})")
	ap.add_argument("-r", "--report", nargs="?", const=defaultReports, metavar="DIR",
		help=f"je Projekt Report <JJJJMMTT>_<Projekt>.txt schreiben (Standard: {defaultReports})")
	ap.add_argument("-f", "--findings-only", action="store_true",
		help="mit -r nur Reports fuer Projekte mit Befunden schreiben")
	ap.add_argument("-c", "--clean", nargs="?", const=defaultReports, metavar="DIR",
		help=f"alle Reports im Ordner loeschen (Standard: {defaultReports}), mit -r danach neu schreiben")
	ap.add_argument("-q", "--quiet", action="store_true", help="Dateien ohne Befund nicht anzeigen")
	ap.add_argument("-s", "--summary", action="store_true", help="nur Zusammenfassung ausgeben")
	ap.add_argument("-x", "--exclude", action="append", default=[], metavar="REGEX", help="zusaetzlich ausschliessen")
	ap.add_argument("--no-default-exclude", action="store_true", help="HAL/CMSIS-Dateien und Submodule mitpruefen, CubeMX-Dateien vollstaendig pruefen")
	args = ap.parse_args()

	if args.clean:
		print(f"{cleanReports(args.clean)} Reports geloescht")
		if not args.report:
			return 0

	excludes = args.exclude + ([] if args.no_default_exclude else DEFAULT_EXCLUDE)
	projects = collectProjects(args.paths or [defaultTarget], excludes, not args.no_default_exclude)
	if not projects:
		print("Keine .c/.h-Dateien gefunden.")
		return 2

	if args.report:
		os.makedirs(args.report, exist_ok=True)
	datePrefix = datetime.date.today().strftime("%Y%m%d")

	total = collections.Counter()
	nFiles = 0
	nClean = 0
	for proj, (base, files) in projects.items():
		cNames = cBasenames(base)
		results = [(p, checkFile(p, cNames, uc)) for p, uc in files]
		userCode = {p for p, uc in files if uc}
		nFiles += len(results)
		nClean += sum(1 for _, i in results if not i)
		for _, iss in results:
			for x in iss:
				total[x.cat] += 1

		if args.report:
			nIssues = sum(len(i) for _, i in results)
			if args.findings_only and not nIssues:
				print(f"{proj:30} {0:6} Befunde  -> kein Report")
				continue
			path = os.path.join(args.report, f"{datePrefix}_{proj}.txt")
			with open(path, "w", encoding="ascii", errors="replace", newline="\r\n") as f:
				f.write(buildReport(proj, base, results, userCode))
			print(f"{proj:30} {nIssues:6} Befunde  -> {os.path.relpath(path)}")
			continue

		if args.summary:
			continue
		for p, iss in results:
			if args.quiet and not iss:
				continue
			print(f"\n### {proj}/{fileTitle(p, base, iss, userCode)}")
			for x in iss:
				print(formatIssue(x))

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
