# Python Coding Style

Verbindlicher Layout- und Formatierungsstandard fuer alle Python-Dateien (`.py`) in den Projekten von **Diveturtle93**.

Die bewussten Abweichungen von PEP 8 stehen in [Abschnitt 6](#6-abweichungen-von-pep-8).

---

## 1. Allgemeine Regeln

| Regel | Festlegung |
|---|---|
| Einrueckung | **Tabs**, Tabbreite **4**, auch fuer Fortsetzungszeilen |
| Zeilenende | CRLF |
| Zeichensatz | reines ASCII – Umlaute werden als `ae`, `oe`, `ue`, `ss` geschrieben |
| Sprache Kommentare | Deutsch |
| Kommentarstil | nur `#`, nach `#` immer ein Leerzeichen |
| Docstrings | **nicht** verwenden – die Beschreibung steht als Kommentar ueber Funktion, Methode bzw. Klasse |
| Bloecke | Rumpf **immer** in eigener Zeile |
| Anweisungen | eine Anweisung pro Zeile, kein `;` |
| Strings | doppelte Anfuehrungszeichen `"` (nicht geprueft) |
| Python-Version | Python 3.10 oder neuer (`match` / `case`) |

### Trennlinie

Die Trennlinie besteht aus `#` gefolgt von **71** Bindestrichen (72 Zeichen gesamt). Sie steht immer in Spalte 1, auch direkt nach einem eingerueckten Block:

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
- Die Import-Abschnitte und `Variablen definieren` werden **immer** angelegt, auch wenn sie leer sind (dann steht eine Leerzeile zwischen den Linien).
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
6. **Definiere Debug-Symbole** – `DEBUG_<NAME> = False`
7. **Version definieren** – `<NAME>_MAJOR`, `_MINOR`, `_PATCH`, `_DEV`
8. Konstanten definieren
9. Klassen – jede Klasse als eigener Abschnitt (Abschnittsname beschreibend, z. B. `Definiere Statemaschine Typedefines`)
10. **Variablen definieren** – Modulvariablen (immer vorhanden, auch wenn leer)
11. Variablen einbinden – optional, Verweise auf Variablen anderer Module, z. B. `latest = state.latest`
12. Funktionen – jede Funktion als eigener Abschnitt
13. Funktionstabellen definieren – optional, Modulvariablen, die Funktionen dieses Moduls benoetigen (z. B. `{0x237: decode0x237}`); sie koennen erst nach den Funktionen stehen
14. Hauptprogramm – optional, `if __name__ == "__main__":`
15. **Abschluss** – die Datei endet mit einer Trennlinie

Die Reihenfolge wird geprueft; optionale Abschnitte duerfen fehlen, die vorhandenen muessen aber in dieser Reihenfolge stehen.

`<NAME>` ist der Dateiname in Grossbuchstaben ohne Endung (`can_bus.py` → `DEBUG_CAN_BUS`, `CAN_BUS_MAJOR`), bei einem `__init__.py` mit Inhalt der Name des Pakets (`decoders/__init__.py` → `DEBUG_DECODERS`, `DECODERS_MAJOR`).

Nicht benoetigte Debug-Symbole stehen auf `False` oder werden auskommentiert (`# DEBUG_<NAME> = True`); auch dann zaehlen sie als vorhanden.

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

Dekoratoren stehen zwischen Trennlinie und Funktionskopf:

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

#-----------------------------------------------------------------------

# Einfuegen der eigenen Module
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------

# Definiere Debug-Symbole
#-----------------------------------------------------------------------
DEBUG_BEISPIEL							= False
#-----------------------------------------------------------------------

# Version definieren
#-----------------------------------------------------------------------
BEISPIEL_MAJOR							= 0
BEISPIEL_MINOR							= 0
BEISPIEL_PATCH							= 0
BEISPIEL_DEV							= 0
#-----------------------------------------------------------------------

# Konstanten definieren
#-----------------------------------------------------------------------
TIMEOUT									= 1000								# Timeout in ms
#-----------------------------------------------------------------------

# Definiere Beispiel Typedefines
#-----------------------------------------------------------------------
class BeispielStates (enum.IntEnum):
	Aus = 0																	# 0 Ausgeschaltet
	An = 1																	# 1 Eingeschaltet
#-----------------------------------------------------------------------
class Beispiel_TypeDef:
	# Objekt initialisieren
	def __init__ (self):
		self.id = 0															# Identifier
		self.len = 0														# Datenlaenge
#-----------------------------------------------------------------------

# Variablen definieren
#-----------------------------------------------------------------------
Main_Beispiel = Beispiel_TypeDef()											# Globale Beispiel-Variable
_zaehler = 0																# Interner Zaehler
_lock = threading.Lock()													# Schutz fuer Main_Beispiel
#-----------------------------------------------------------------------

# Initialisiere Beispiel
#-----------------------------------------------------------------------
def initBeispiel ():
	global _zaehler

	# Variablen zuruecksetzen
	with _lock:
		Main_Beispiel.id = 0
		Main_Beispiel.len = 0
		_zaehler = 0
#-----------------------------------------------------------------------

# Gebe Wert anhand des Index zurueck
#-----------------------------------------------------------------------
def getBeispiel (index):
	ret = 0

	# Index auswerten
	match index:
		case 0:
			ret = Main_Beispiel.len
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

- Der Rumpf von `if`, `elif`, `else`, `for`, `while`, `with`, `try`, `except`, `finally`, `def`, `class`, `match` und `case` steht **immer** in einer eigenen Zeile.
- Nach Schluesselwoertern ein Leerzeichen, wenn eine Klammer folgt: `if (a or b) and c:`, nicht `if(a or b) and c:`. Ohne Klammer: `if canIsActive:` (keine Klammern um einfache Bedingungen).
- Folgt nur ein einzelnes `return`, steht es ebenfalls eingerueckt in der naechsten Zeile:
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
- Leerer Rumpf: `pass`.
- Ein Kommentar zu einem `elif`- oder `else`-Zweig steht direkt in der Zeile ueber dem `elif` / `else`.

```python
# CAN-Nachricht hat extended ID
if msg.flags.extended == 1:
	header.IDE = CAN_ID_EXT
# CAN-Nachricht hat standard ID
else:
	header.IDE = CAN_ID_STD
```

### `match` / `case`

- Jeder `case` steht in eigener Zeile, der Code darunter eingerueckt.
- Mehrere Werte mit gleichem Code werden mit `|` zusammengefasst: `case 1 | 2:`.
- `case _:` ist **immer** vorhanden und steht als letzter Zweig.
- Ein leerer Zweig enthaelt `pass`.

```python
match wert:
	case 1 | 2:
		# Gemeinsamer Code fuer 1 und 2
		verarbeiten()
	case 3:
		# Code fuer 3
		return "Drei"
	case _:
		pass
```

### Funktionen

- Definition: Leerzeichen zwischen Name und Klammer – `def setState (state):`, auch bei Klassen mit Basisklasse: `class CanManager (Base):`.
- Aufrufe ohne Leerzeichen – `setState(Ready)`, `time.time()`.
- Keine Parameter → `def initBeispiel ():`.
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

- Werte einer Gruppe stehen per Tabs ausgerichtet untereinander: zwischen Name und `=` stehen Tabs bis **Spalte 41**, nach `=` ein Leerzeichen.
- Name in `GROSSBUCHSTABEN` mit `_`.
- Gilt fuer `Definiere Debug-Symbole`, `Version definieren` und `Konstanten definieren` (nicht geprueft).

```python
TIMEOUT									= 1000								# Timeout in ms
RX_BUFFER_SIZE							= 64								# Groesse Empfangspuffer
```

---

## 5. Namenskonventionen

| Element | Konvention | Beispiel |
|---|---|---|
| Dateien / Module | Kleinbuchstaben, `_` als Trenner | `can_bus.py`, `cell_voltages.py` |
| Pakete (Ordner) | Kleinbuchstaben | `decoders`, `callbacks` |
| Debug-Symbol | `DEBUG_<DATEI>` | `DEBUG_CAN_BUS` |
| Versions-Konstanten | `<DATEI>_MAJOR/_MINOR/_PATCH/_DEV` | `CAN_BUS_MAJOR` |
| Konstanten | `GROSSBUCHSTABEN` | `ERROR_RESET` |
| Funktionen / Methoden | camelCase, Modul-Praefix erlaubt | `setState`, `CANwrite` |
| Variablen / Parameter / Attribute | camelCase | `sizeRxBuffer`, `timeError` |
| Globale Instanzen | `Main_<Name>` bzw. `<Modul>_<Name>` | `Main_Statemaschine`, `CAN_Manager` |
| Klassen | PascalCase, `<Name>_TypeDef` / `<Name>TypeDef` erlaubt | `CanManager`, `CAN_PaketTypeDef` |
| Enum-Werte | PascalCase oder `GROSS_MIT_UNTERSTRICH` | `ReadyToDrive`, `RX_SIZE_8` |
| Modulintern | fuehrender `_` | `_unpack`, `_BACKOFF_MAX` |
| Spezialmethoden | unveraendert | `__init__`, `__str__` |

Geprueft werden die Namen von Funktionen, Methoden und Klassen (kein `snake_case`). Methoden, deren Name von einer fremden Bibliothek vorgegeben ist (z. B. `do_GET`), werden gemeldet und koennen ignoriert werden.

---

## 6. Abweichungen von PEP 8

Dieser Standard weicht bewusst von PEP 8 ab:

| PEP 8 | Dieser Standard |
|---|---|
| 4 Leerzeichen | Tabs (Tabbreite 4) |
| `snake_case` fuer Funktionen und Variablen | camelCase |
| `def name(x):` | `def name (x):` |
| 2 Leerzeilen zwischen Funktionen/Klassen | 1 Leerzeile + Abschnitt mit Trennlinien |
| Docstrings | Kommentar ueber der Definition |
| Zeilenkommentar mit 2 Leerzeichen | Tabs bis Spalte 77 |
| `NAME = wert` | `NAME<Tabs>= wert`, `=` auf Spalte 41 |

Linter wie `flake8` oder `pylint` melden diese Punkte; dort die Regeln `W191`, `E101`, `E211`, `E221`, `E302`, `E305`, `N802`, `N803`, `N806` bzw. `C0103` und `C0114`–`C0116` abschalten.

---

## 7. Automatische Pruefung

Das Skript [tools/py_stylecheck.py](tools/py_stylecheck.py) prueft Python-Dateien gegen diesen Standard. Aufruf, Reports, Ausschluesse und Projekteinstellungen sind in [tools/README.md](tools/README.md) beschrieben.

---

## 8. Checkliste

- [ ] Dateikopf vollstaendig (Titel, Sprache, Datum, Version, Autor, Projekt, Quelle)
- [ ] Alle Pflichtabschnitte vorhanden und in der richtigen Reihenfolge
- [ ] Leere Import-Abschnitte trotzdem angelegt
- [ ] Abschnitt `Variablen definieren` vorhanden (auch wenn leer)
- [ ] `Definiere Debug-Symbole` mit `DEBUG_<NAME>` vorhanden
- [ ] Versions-Konstanten vorhanden
- [ ] Datei endet mit Trennlinie
- [ ] Jede Funktion und Klasse mit Beschreibungskommentar und Trennlinien, jede Methode mit Kommentar darueber
- [ ] Tabs statt Leerzeichen, Rumpf immer in eigener Zeile
- [ ] `match` mit `case _:`
- [ ] Kommentare deutsch, ohne Umlaute
- [ ] Keine Docstrings, kein `;`, kein `import *`
