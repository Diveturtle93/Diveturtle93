# Python Coding Style

Verbindlicher Layout- und Formatierungsstandard fuer alle Python-Dateien (`.py`) in den Projekten von **Diveturtle93**.

Der Standard uebertraegt den [C Coding Style](C_CODING_STYLE.md) auf Python: gleicher Dateikopf, gleiche Abschnitte, gleiche Trennlinien, gleiche Namensgebung. Wo Python andere Mittel hat (Bloecke durch Einrueckung, kein Praeprozessor), ist die naechstliegende Entsprechung festgelegt. Die bewussten Abweichungen von PEP 8 stehen in [Abschnitt 6](#6-abweichungen-von-pep-8).

---

## 1. Allgemeine Regeln

| Regel | Festlegung |
|---|---|
| Einrueckung | **Tabs**, Tabbreite **4**, auch fuer Fortsetzungszeilen; Tabs und Leerzeichen nie mischen |
| Zeilenende | CRLF |
| Zeichensatz | reines ASCII – Umlaute werden als `ae`, `oe`, `ue`, `ss` geschrieben |
| Sprache Kommentare | Deutsch |
| Kommentarstil | nur `#`, nach `#` immer ein Leerzeichen |
| Docstrings | **nicht** verwenden – die Beschreibung steht als Kommentar ueber Funktion, Methode bzw. Klasse (entspricht "kein Doxygen") |
| Anweisungen | eine Anweisung pro Zeile, kein `;`, kein Rumpf hinter `:` in derselben Zeile |
| Strings | doppelte Anfuehrungszeichen `"` (nicht geprueft) |
| Python-Version | Python 3.10 oder neuer (`match` / `case`) |

### Trennlinie

Die Trennlinie besteht aus `#` gefolgt von **71** Bindestrichen (72 Zeichen gesamt, wie in C). Sie steht immer in Spalte 1, auch direkt nach einem eingerueckten Block:

```python
#-----------------------------------------------------------------------
```

### Abschnitte

Jeder Abschnitt einer Datei hat immer dieselbe Form:

```python
# <Abschnittsname>
#-----------------------------------------------------------------------
<Inhalt>
#-----------------------------------------------------------------------
```

- Zwischen zwei Abschnitten steht genau **eine Leerzeile**.
- Die drei Import-Abschnitte und `Variablen definieren` werden **immer** angelegt, auch wenn sie leer sind (dann steht eine Leerzeile zwischen den Linien).
- Mehrere Klassen innerhalb eines Abschnitts (z. B. zusammengehoerige Enums) werden nur durch eine Trennlinie getrennt (ohne Leerzeile).

---

## 2. Dateikopf

Jede Datei beginnt mit diesem Kopfblock. Zwischen Bezeichner und `:` sowie zwischen `:` und Wert steht jeweils **ein Tab**.

```python
#-----------------------------------------------------------------------
# Titel	:	<dateiname>.py
#-----------------------------------------------------------------------
# Sprache	:	Python
# Datum	:	TT.MM.JJJJ
# Version	:	1.0
# Autor	:	Diveturtle93
# Projekt	:	<Projektname>
# Quelle	:	<optional: URL / Herkunft, sonst leer>
#-----------------------------------------------------------------------
```

- **Titel** – exakter Dateiname inkl. Endung
- **Datum** – Erstellungsdatum im Format `TT.MM.JJJJ`
- **Quelle** – Zeile ist immer vorhanden, darf leer bleiben
- Ausfuehrbare Skripte duerfen in Zeile 1 davor eine Shebang-Zeile haben: `#!/usr/bin/env python3`. Eine `coding`-Zeile entfaellt (reines ASCII).
- Leere Dateien (z. B. ein leeres `__init__.py`) bleiben leer und bekommen keinen Kopf.

---

## 3. Moduldatei (`.py`)

Reihenfolge der Abschnitte (Pflicht, fett = immer vorhanden):

1. **Dateikopf** – davor optional die Shebang-Zeile
2. Beschreibung – optional, nur Kommentare, z. B. Aufruf und Optionen eines Skripts
3. **Einfuegen der standard Module** – Standardbibliothek: `os`, `sys`, `threading`, …
4. **Einfuegen der externen Module** – per `pip` installierte Pakete: `can`, `dash`, `plotly`, …
5. **Einfuegen der eigenen Module** – Module und Pakete des Projekts, relative Importe
6. Version definieren – `<NAME>_MAJOR`, `_MINOR`, `_PATCH`, `_DEV`
7. Konstanten definieren
8. Klassen – jede Klasse als eigener Abschnitt (Abschnittsname beschreibend, z. B. `Definiere Statemaschine Zustaende`)
9. **Variablen definieren** – Modulvariablen (immer vorhanden, auch wenn leer). Der Abschnitt steht nach den Klassen, damit hier Instanzen angelegt werden koennen.
10. Funktionen – jede Funktion als eigener Abschnitt
11. Variablen einbinden – optional, Modulvariablen, die Funktionen dieses Moduls benoetigen (z. B. Zuordnungstabellen `{0x237: decode0x237}`)
12. Hauptprogramm – `if __name__ == "__main__":`

Die Reihenfolge wird geprueft; optionale Abschnitte duerfen fehlen, die vorhandenen muessen aber in dieser Reihenfolge stehen.

`<NAME>` ist der Dateiname in Grossbuchstaben ohne Endung (`can_bus.py` → `CAN_BUS_MAJOR`).

### Imports

- Ein Modul pro `import`-Zeile: `import os`, nicht `import os, sys`. `from paket import a, b` ist erlaubt; lange Listen in Klammern, ein Name pro Zeile, mit Tab eingerueckt.
- Kein `from modul import *`.
- Jeder Import steht im passenden Abschnitt:
  - **standard** – Modul der Standardbibliothek (`sys.stdlib_module_names`)
  - **eigene** – relativer Import (`from . import x`) oder Modul/Paket, das im Projektordner bzw. im Ordner der Datei liegt
  - **extern** – alles andere
- Imports innerhalb von Funktionen sind erlaubt, wenn sie bewusst verzoegert geladen werden sollen.

### Funktionsabschnitt

Jede Funktion bekommt einen beschreibenden Kommentar als Abschnittsname und wird von Trennlinien eingeschlossen:

```python
# <Was die Funktion macht>
#-----------------------------------------------------------------------
def <name> (<Parameter>):
	...
#-----------------------------------------------------------------------
```

Dekoratoren stehen zwischen Trennlinie und Funktionskopf (wie `#if` in C):

```python
# Wert zwischenspeichern
#-----------------------------------------------------------------------
@functools.cache
def readConfig (path):
	...
#-----------------------------------------------------------------------
```

### Klassenabschnitt

Eine Klasse ist ein Abschnitt wie eine Funktion. Innerhalb der Klasse gibt es keine Trennlinien; jede Methode bekommt einen Kommentar **direkt** in der Zeile darueber (gleiche Einrueckung wie `def`), zwischen den Methoden steht eine Leerzeile.

```python
# Verwaltet den CAN-Empfang
#-----------------------------------------------------------------------
class CanManager:
	# Objekt initialisieren
	def __init__ (self):
		self._thread = None

	# Empfang starten
	def start (self, config):
		...
#-----------------------------------------------------------------------
```

### Vorlage

```python
#-----------------------------------------------------------------------
# Titel	:	beispiel.py
#-----------------------------------------------------------------------
# Sprache	:	Python
# Datum	:	12.10.2026
# Version	:	1.0
# Autor	:	Diveturtle93
# Projekt	:	Beispiel
# Quelle	:
#-----------------------------------------------------------------------

# Einfuegen der standard Module
#-----------------------------------------------------------------------
import enum
import threading
#-----------------------------------------------------------------------

# Einfuegen der externen Module
#-----------------------------------------------------------------------
import can
#-----------------------------------------------------------------------

# Einfuegen der eigenen Module
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------

# Version definieren
#-----------------------------------------------------------------------
BEISPIEL_MAJOR = 0
BEISPIEL_MINOR = 0
BEISPIEL_PATCH = 0
BEISPIEL_DEV = 0
#-----------------------------------------------------------------------

# Konstanten definieren
#-----------------------------------------------------------------------
TIMEOUT = 1.0																# Timeout in s
#-----------------------------------------------------------------------

# Definiere Beispiel Zustaende
#-----------------------------------------------------------------------
class BeispielStates (enum.IntEnum):
	Aus = 0																	# 0 Ausgeschaltet
	An = 1																	# 1 Eingeschaltet
#-----------------------------------------------------------------------

# Speichert eine CAN-Nachricht
#-----------------------------------------------------------------------
class BeispielNachricht:
	# Objekt initialisieren
	def __init__ (self, canId, data):
		self.canId = canId													# Identifier
		self.data = data													# Datenbytes
#-----------------------------------------------------------------------

# Variablen definieren
#-----------------------------------------------------------------------
mainBeispiel = BeispielNachricht(0, b"")									# Globale Beispiel-Variable
lock = threading.Lock()														# Schutz fuer mainBeispiel
#-----------------------------------------------------------------------

# Initialisiere Beispiel
#-----------------------------------------------------------------------
def initBeispiel ():
	# Variablen zuruecksetzen
	with lock:
		mainBeispiel.canId = 0
		mainBeispiel.data = b""
#-----------------------------------------------------------------------

# Gebe Wert anhand des Index zurueck
#-----------------------------------------------------------------------
def getBeispiel (index):
	ret = 0

	# Index auswerten
	match index:
		case 0:
			ret = len(mainBeispiel.data)
		case 1 | 2:
			ret = mainBeispiel.canId
		case _:
			pass

	return ret
#-----------------------------------------------------------------------

# Hauptprogramm
#-----------------------------------------------------------------------
if __name__ == "__main__":
	initBeispiel()
	print(getBeispiel(0))
#-----------------------------------------------------------------------
```

---

## 4. Formatierung im Code

### Bloecke und Kontrollstrukturen

- Der Rumpf von `if`, `elif`, `else`, `for`, `while`, `with`, `try`, `except`, `finally`, `def`, `class`, `match` und `case` steht **immer** in einer eigenen Zeile – auch ein einzelnes `return` (in C sind dort die Klammern optional, die neue Zeile ist Pflicht):
  ```python
  # Beende wenn CAN-Bus aktiv ist
  if canIsActive:
  	return

  # Anzahl Nachrichten im Ring zurueckgeben
  if rxRing.head >= rxRing.tail:
  	return rxRing.head - rxRing.tail
  else:
  	return rxRing.size - (rxRing.tail - rxRing.head)
  ```
- Keine Klammern um Bedingungen: `if canIsActive:`, nicht `if (canIsActive):` (nicht geprueft).
- Leerer Rumpf: `pass`.
- Ein Kommentar zu einem `elif`- oder `else`-Zweig steht direkt in der Zeile ueber dem `elif` / `else`, eingerueckt wie das `elif` / `else`.

```python
# CAN-Nachricht hat extended ID
if msg.isExtendedId:
	header.ide = CAN_ID_EXT
# CAN-Nachricht hat standard ID
else:
	header.ide = CAN_ID_STD
```

### `match` / `case`

`match` / `case` ist das Gegenstueck zu `switch` / `case`.

- `case _:` (Standardzweig, entspricht `default`) ist **immer** vorhanden und steht als letzter Zweig.
- Mehrere Werte mit gleichem Code werden mit `|` zusammengefasst: `case 1 | 2:`.
- Ein Durchfallen wie in C gibt es nicht; ein `break` wird nicht benoetigt.
- Ein leerer Zweig enthaelt `pass`.

```python
match state:
	case States.Ok:
		return "OK"
	case States.Error | States.Timeout:
		return "Error"
	case _:
		return "Unbekannt"
```

### Funktionen und Klassen

- Definition: Leerzeichen zwischen Name und Klammer – `def setState (state):`, `class CanManager (Base):`.
- Aufrufe ohne Leerzeichen – `setState(Ready)`, `time.time()`.
- Keine Parameter → `def initBeispiel ():`
- Typ-Annotationen sind erlaubt: `def send (self, canId: int, data: bytes) -> bool:`.

### Kommentare

- **Blockkommentar** ueber einer Anweisungsgruppe: eigene Zeile, gleiche Einrueckung wie der Code.
- **Zeilenkommentar** hinter Code (Konstanten, Enum-Werte, Attribute, Variablen): mit Tabs auf **Spalte 77** (Tabbreite 4) ausgerichtet. Ist der Code laenger, reicht ein Tab.
- Enum-Werte werden im Kommentar mit ihrem Zahlenwert begonnen: `# 3 Anlasser betaetigt`.

### Leerzeilen

- Zwischen logischen Bloecken innerhalb einer Funktion eine Leerzeile.
- Vor `return` darf zur Trennung eine Leerzeile stehen.
- Zwischen Methoden einer Klasse eine Leerzeile.

### Konstanten

- Name in `GROSSBUCHSTABEN` mit `_`, je ein Leerzeichen um `=`.
- Zusammengehoerige Werte (Listen, Dictionaries) stehen ein Eintrag pro Zeile, mit Tab eingerueckt.

---

## 5. Namenskonventionen

| Element | Konvention | Beispiel |
|---|---|---|
| Dateien / Module | Kleinbuchstaben, `_` als Trenner | `can_bus.py`, `cell_voltages.py` |
| Pakete (Ordner) | Kleinbuchstaben | `decoders`, `callbacks` |
| Versions-Konstanten | `<DATEI>_MAJOR/_MINOR/_PATCH/_DEV` | `CAN_BUS_MAJOR` |
| Konstanten | `GROSSBUCHSTABEN` | `BACKOFF_MAX` |
| Funktionen / Methoden | camelCase | `canRxThread`, `getBeispiel` |
| Variablen / Parameter / Attribute | camelCase | `rxTs`, `stopEvent`, `self.canId` |
| Globale Instanzen | camelCase, `main<Name>` bzw. `<modul><Name>` | `mainStatemaschine`, `canManager` |
| Klassen | PascalCase | `CanManager`, `CanConfig` |
| Enum-Werte | PascalCase oder `GROSS_MIT_UNTERSTRICH` | `ReadyToDrive`, `RX_SIZE_8` |
| Modulintern | fuehrender `_` | `_unpack`, `_BACKOFF_MAX` |
| Spezialmethoden | unveraendert | `__init__`, `__str__` |

Geprueft werden die Namen von Funktionen, Methoden und Klassen. Methoden, deren Name von einer fremden Bibliothek vorgegeben ist (z. B. `do_GET`), werden gemeldet und koennen ignoriert werden.

---

## 6. Abweichungen von PEP 8

Damit C- und Python-Code im selben Projekt gleich aussehen, weicht dieser Standard bewusst von PEP 8 ab:

| PEP 8 | Dieser Standard |
|---|---|
| 4 Leerzeichen | Tabs (Tabbreite 4) |
| `snake_case` fuer Funktionen und Variablen | camelCase |
| `def name(x):` | `def name (x):` |
| 2 Leerzeilen zwischen Funktionen/Klassen | 1 Leerzeile + Abschnitt mit Trennlinien |
| Docstrings | Kommentar ueber der Definition |
| Zeilenkommentar mit 2 Leerzeichen | Tabs bis Spalte 77 |

Linter wie `flake8` oder `pylint` melden diese Punkte; dort die Regeln `W191`, `E101`, `E211`, `E302`, `E305`, `N802`, `N803`, `N806` bzw. `C0103` und `C0114`–`C0116` abschalten.

---

## 7. Automatische Pruefung

Das Skript [tools/py_stylecheck.py](tools/py_stylecheck.py) prueft Python-Dateien gegen diesen Standard (benoetigt Python 3.10+, keine weiteren Pakete; nutzt Hilfsfunktionen aus [tools/c_stylecheck.py](tools/c_stylecheck.py)).

```sh
py tools/py_stylecheck.py                           # alle Ordner neben diesem Repo
py tools/py_stylecheck.py ../EAuto_Dashboard        # ein Ordner
py tools/py_stylecheck.py "../EAuto_*"              # beliebige Ordner oder Glob-Muster
py tools/py_stylecheck.py tools/py_stylecheck.py    # eine Datei
py tools/py_stylecheck.py -q                        # nur Dateien mit Befund anzeigen
py tools/py_stylecheck.py -s                        # nur Zusammenfassung
py tools/py_stylecheck.py ../EAuto_Dashboard -x openblt  # zusaetzlich Pfade ausschliessen (Regex)
py tools/py_stylecheck.py -r                        # je Projekt Report nach reports/<JJJJMMTT>_<Projekt>_py.txt
py tools/py_stylecheck.py -r -f                     # Reports nur fuer Projekte mit Befunden
py tools/py_stylecheck.py -c                        # alle Python-Reports in reports/ loeschen
py tools/py_stylecheck.py -c -r                     # alte Python-Reports loeschen, danach neu schreiben
```

Ein Report listet je Datei jeden Befund mit Zeilennummer und Kategorie (`Datei` = betrifft die ganze Datei, z. B. fehlender Abschnitt). Jeder per Pfad oder Glob gefundene Ordner gilt als eigenes Projekt. Der Dateiname endet auf `_py` (z. B. `20261012_EAuto_Dashboard_py.txt`), damit er nicht mit dem C-Report desselben Projekts kollidiert; ein Report vom selben Tag wird ueberschrieben, aeltere bleiben erhalten. `-c` loescht nur die Python-Reports (`<JJJJMMTT>_<Projekt>_py.txt`); `c_stylecheck.py -c` loescht dagegen alle Reports im Ordner.

Ordner ohne `.py`-Dateien werden beim Standardaufruf (alle Ordner neben diesem Repo) stillschweigend uebersprungen. Virtuelle Umgebungen (`venv`, `.venv`, `env`), `__pycache__`, `build`, `dist`, `site-packages` sowie Git-Submodule aus der `.gitmodules` des Projekts werden automatisch uebersprungen. Mit `--no-default-exclude` werden sie mitgeprueft.

Projektspezifische Einstellungen stehen optional in der Datei `.py_stylecheck` im Projektordner (gleicher Aufbau wie `.c_stylecheck`). Ordner oder einzelne Dateien werden relativ zum Projektordner angegeben, mehrere mit Komma getrennt:

```ini
[stylecheck]
exclude = openblt, Test   # diese Ordner/Dateien zusaetzlich ausschliessen (z. B. fremde Bibliotheken)
include = backend, ui     # nur diese Ordner pruefen
```

Rueckgabewert: `0` = keine Befunde, `1` = Befunde, `2` = keine Dateien gefunden.

---

## 8. Checkliste

- [ ] Dateikopf vollstaendig (Titel, Sprache, Datum, Version, Autor, Projekt, Quelle)
- [ ] Alle Pflichtabschnitte vorhanden und in der richtigen Reihenfolge
- [ ] Leere Import-Abschnitte trotzdem angelegt, `Variablen definieren` vorhanden (auch wenn leer)
- [ ] Jeder Import im passenden Abschnitt, ein Modul pro `import`-Zeile, kein `import *`
- [ ] Jede Funktion und Klasse mit Beschreibungskommentar und Trennlinien
- [ ] Jede Methode mit Kommentar direkt darueber
- [ ] Tabs statt Leerzeichen, CRLF, Rumpf immer in eigener Zeile, kein `;`
- [ ] `def name (...)` mit Leerzeichen, Namen in camelCase bzw. PascalCase
- [ ] `match` immer mit `case _:`
- [ ] Kommentare deutsch, ohne Umlaute, keine Docstrings
