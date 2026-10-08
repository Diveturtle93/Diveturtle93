# C Coding Style

Verbindlicher Layout- und Formatierungsstandard fuer alle C-Dateien (`.c` / `.h`) in den Projekten von **Diveturtle93**.

---

## 1. Allgemeine Regeln

| Regel | Festlegung |
|---|---|
| Einrueckung | **Tabs**, Tabbreite **4** |
| Zeilenende | CRLF |
| Zeichensatz | reines ASCII – Umlaute werden als `ae`, `oe`, `ue`, `ss` geschrieben |
| Sprache Kommentare | Deutsch |
| Kommentarstil | nur `//`, keine `/* */`-Bloecke (Ausnahme: `#endif /* INC_<NAME>_H_ */`) |
| Doxygen | **nicht** verwenden |
| `extern "C"` | **nicht** verwenden |
| Klammerstil | Allman (jede `{` und `}` in eigener Zeile) |

### Trennlinie

Die Trennlinie besteht aus `//` gefolgt von **70** Bindestrichen (72 Zeichen gesamt):

```c
//----------------------------------------------------------------------
```

### Abschnitte

Jeder Abschnitt einer Datei hat immer dieselbe Form:

```c
// <Abschnittsname>
//----------------------------------------------------------------------
<Inhalt>
//----------------------------------------------------------------------
```

- Zwischen zwei Abschnitten steht genau **eine Leerzeile**.
- Die Include-Abschnitte werden **immer** angelegt, auch wenn sie leer sind (dann steht eine Leerzeile zwischen den Linien).
- Mehrere Typdefinitionen innerhalb eines Abschnitts werden nur durch eine Trennlinie getrennt (ohne Leerzeile).

---

## 2. Dateikopf

Jede Datei (`.c` und `.h`) beginnt mit diesem Kopfblock. Zwischen Bezeichner und `:` sowie zwischen `:` und Wert steht jeweils **ein Tab**.

```c
//----------------------------------------------------------------------
// Titel	:	<dateiname>.h
//----------------------------------------------------------------------
// Sprache	:	C
// Datum	:	TT.MM.JJJJ
// Version	:	1.0
// Autor	:	Diveturtle93
// Projekt	:	<Projektname>
// Quelle	:	<optional: URL / Herkunft, sonst leer>
//----------------------------------------------------------------------
```

- **Titel** – exakter Dateiname inkl. Endung
- **Datum** – Erstellungsdatum im Format `TT.MM.JJJJ`
- **Quelle** – Zeile ist immer vorhanden, darf leer bleiben

---

## 3. Header-Datei (`.h`)

Reihenfolge der Abschnitte (Pflicht, fett = immer vorhanden):

1. **Dateikopf**
2. **Saveguard symbol** – `#pragma once`
3. **Dateiheader definieren** – Include-Guard `INC_<NAME>_H_`
4. **Einfuegen der standard Include-Dateien** – `<stdint.h>`, `<stdbool.h>`, …
5. **Einfuegen der STM Include-Dateien** – `"main.h"`, `"can.h"`, …
6. **Einfuegen der eigenen Include Dateien**
7. Definiere Debug Symbols – `DEBUG_<NAME>` innerhalb von `#ifdef DEBUG`
8. **Version definieren** – `<NAME>_MAJOR`, `_MINOR`, `_PATCH`, `_DEV`
9. Konstanten definieren
10. Typedefs (Abschnittsname beschreibend, z. B. `Typedefines definieren`, `Definiere Statemaschine Typedefines`)
11. Definiere globale Variablen (`extern`)
12. **Funktionen definieren** – Prototypen
13. **Abschluss** – `#endif /* INC_<NAME>_H_ */` + Trennlinie

`<NAME>` ist der Dateiname in Grossbuchstaben ohne Endung (`canbus.h` → `INC_CANBUS_H_`, `CANBUS_MAJOR`, `DEBUG_CANBUS`).

Innerhalb von `#ifdef` / `#endif` wird mit einem Tab eingerueckt. Nicht benoetigte Debug-Symbole werden auskommentiert (`//	#define ...`).

### Vorlage

```c
//----------------------------------------------------------------------
// Titel	:	beispiel.h
//----------------------------------------------------------------------
// Sprache	:	C
// Datum	:	08.10.2026
// Version	:	1.0
// Autor	:	Diveturtle93
// Projekt	:	Beispiel
// Quelle	:
//----------------------------------------------------------------------

// Saveguard symbol
//----------------------------------------------------------------------
#pragma once
//----------------------------------------------------------------------

// Dateiheader definieren
//----------------------------------------------------------------------
#ifndef INC_BEISPIEL_H_
#define INC_BEISPIEL_H_
//----------------------------------------------------------------------

// Einfuegen der standard Include-Dateien
//----------------------------------------------------------------------
#include <stdint.h>
//----------------------------------------------------------------------

// Einfuegen der STM Include-Dateien
//----------------------------------------------------------------------

//----------------------------------------------------------------------

// Einfuegen der eigenen Include Dateien
//----------------------------------------------------------------------

//----------------------------------------------------------------------

// Definiere Debug Symbols
//----------------------------------------------------------------------
#ifdef DEBUG
	#define DEBUG_BEISPIEL
#endif
//----------------------------------------------------------------------

// Version definieren
//----------------------------------------------------------------------
#define BEISPIEL_MAJOR					0
#define BEISPIEL_MINOR					0
#define BEISPIEL_PATCH					0
#define BEISPIEL_DEV					0
//----------------------------------------------------------------------

// Konstanten definieren
//----------------------------------------------------------------------
#define TIMEOUT							1000								// Timeout in ms
//----------------------------------------------------------------------

// Definiere Beispiel Typedefines
//----------------------------------------------------------------------
typedef enum
{
	Aus,																	// 0 Ausgeschaltet
	An,																		// 1 Eingeschaltet
} beispielStates;
//----------------------------------------------------------------------
typedef struct
{
	uint32_t id;															// Identifier
	uint8_t len;															// Datenlaenge
} Beispiel_TypeDef;
//----------------------------------------------------------------------

// Definiere globale Variablen
//----------------------------------------------------------------------
extern Beispiel_TypeDef Main_Beispiel;										// Globale Beispiel-Variable
//----------------------------------------------------------------------

// Funktionen definieren
//----------------------------------------------------------------------
void initBeispiel (void);													// Beispiel initialisieren
uint8_t getBeispiel (uint8_t index);										// Wert zurueckgeben
//----------------------------------------------------------------------

#endif /* INC_BEISPIEL_H_ */
//----------------------------------------------------------------------
```

---

## 4. Quelldatei (`.c`)

Reihenfolge der Abschnitte:

1. **Dateikopf**
2. **Einfuegen der standard Include-Dateien**
3. **Einfuegen der STM Include-Dateien**
4. **Einfuegen der eigenen Include Dateien** – der eigene Header steht hier
5. Variablen definieren – globale und `static` Variablen
6. Funktionen – jede Funktion als eigener Abschnitt

### Funktionsabschnitt

Jede Funktion bekommt einen beschreibenden Kommentar als Abschnittsname und wird von Trennlinien eingeschlossen:

```c
// <Was die Funktion macht>
//----------------------------------------------------------------------
<Rueckgabetyp> <name> (<Parameter>)
{
	...
}
//----------------------------------------------------------------------
```

### Vorlage

```c
//----------------------------------------------------------------------
// Titel	:	beispiel.c
//----------------------------------------------------------------------
// Sprache	:	C
// Datum	:	08.10.2026
// Version	:	1.0
// Autor	:	Diveturtle93
// Projekt	:	Beispiel
// Quelle	:
//----------------------------------------------------------------------

// Einfuegen der standard Include-Dateien
//----------------------------------------------------------------------

//----------------------------------------------------------------------

// Einfuegen der STM Include-Dateien
//----------------------------------------------------------------------
#include "main.h"
//----------------------------------------------------------------------

// Einfuegen der eigenen Include Dateien
//----------------------------------------------------------------------
#include "beispiel.h"
//----------------------------------------------------------------------

// Variablen definieren
//----------------------------------------------------------------------
Beispiel_TypeDef Main_Beispiel;												// Globale Beispiel-Variable
static uint8_t zaehler = 0;													// Interner Zaehler
//----------------------------------------------------------------------

// Initialisiere Beispiel
//----------------------------------------------------------------------
void initBeispiel (void)
{
	// Variablen zuruecksetzen
	Main_Beispiel.id = 0;
	Main_Beispiel.len = 0;
	zaehler = 0;
}
//----------------------------------------------------------------------

// Gebe Wert anhand des Index zurueck
//----------------------------------------------------------------------
uint8_t getBeispiel (uint8_t index)
{
	uint8_t ret = 0;

	// Index auswerten
	switch (index)
	{
		case 0:
		{
			ret = Main_Beispiel.len;
			break;
		}
		default:
		{
			break;
		}
	}

	return ret;
}
//----------------------------------------------------------------------
```

---

## 5. Formatierung im Code

### Klammern und Kontrollstrukturen

- Allman-Stil fuer Funktionen, `if`, `else`, `for`, `while`, `switch`, `struct`, `enum`, `union`.
- Nach Schluesselwoertern ein Leerzeichen: `if (`, `switch (`, `while (`.
- `if` / `else` **immer** mit geschweiften Klammern.
- Ausnahme: Folgt auf ein `if`, `else if` oder `else` direkt ein einzelnes `return ...;`, sind keine Klammern noetig:
  ```c
  // Beende wenn CAN-Bus aktiv ist
  if (canIsActive)
  	return;

  // Anzahl Nachrichten im Ring zurueckgeben
  if (rxRing.head >= rxRing.tail)
  	return rxRing.head - rxRing.tail;
  else
  	return rxRing.size - (rxRing.tail - rxRing.head);
  ```
- Unterscheidet sich die Bedingung je nach Controller, stehen die alternativen `if`-Zeilen in `#if` / `#ifdef`-Zweigen. Die gemeinsame `{` folgt erst nach dem letzten `#endif`:
  ```c
  #if defined (STM32F1) || defined (STM32G0)
  	if (HAL_OK != HAL_FLASH_Program(FLASH_TYPEPROGRAM_DOUBLEWORD, address, tmp))
  #endif

  #ifdef STM32F7
  	if (HAL_OK != HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, address, tmp))
  #endif
  	{
  		status |= FLASH_ERROR_WRITE;
  	}
  ```
- Ein Kommentar zu einem `else`-Zweig steht direkt in der Zeile ueber dem `else`.

```c
// CAN-Nachricht hat extended ID
if (msg->flags.extended == 1)
{
	header.IDE = CAN_ID_EXT;
}
// CAN-Nachricht hat standard ID
else
{
	header.IDE = CAN_ID_STD;
}
```

### `switch` / `case`

- Jeder `case` und `default` bekommt einen eigenen `{ }`-Block.
- Mehrere `case`-Marken mit gleichem Code stehen direkt untereinander; nur die **letzte** Marke bekommt den `{ }`-Block.
- `break;` steht **innerhalb** des Blocks.
- `default` ist immer vorhanden.
- Jeder Block endet mit `break;`, `return`, `continue` oder `goto`. Ausnahme: der letzte Block im `switch`.
- Gewolltes Durchfallen (Fall-through) ist erlaubt, muss aber als **letzte Zeile im Block** mit diesem Kommentar markiert werden:
  `// fall through - <Begruendung>`
  Die Schreibweise `fall through` erkennt auch GCC (`-Wimplicit-fallthrough`); hinter dem Bindestrich steht die deutsche Begruendung. Ein `break;` nur innerhalb eines `if` zaehlt nicht – auch dann ist die Markierung noetig.
- Mehrere `case`-Marken direkt untereinander brauchen **keine** Markierung.

```c
switch (wert)
{
	case 1:
	case 2:
	{
		// Gemeinsamer Code fuer 1 und 2
		break;
	}
	case 5:
	{
		// Zusaetzlich Code von 3 ausfuehren
		vorbereiten();
		// fall through - Code von 3 ebenfalls ausfuehren
	}
	case 3:
	{
		// Code fuer 3
		break;
	}
	default:
	{
		break;
	}
}
```

### Funktionen

- Deklaration und Definition: Leerzeichen zwischen Name und Klammer – `void setState (uint8_t state)`.
- Aufrufe ohne Leerzeichen – `setState(Ready);`, `HAL_GetTick();`.
- Keine Parameter → `(void)`.

### Kommentare

- **Blockkommentar** ueber einer Anweisungsgruppe: eigene Zeile, gleiche Einrueckung wie der Code.
- **Zeilenkommentar** hinter Code (Defines, Enum-Werte, Struct-Member, Variablen, Prototypen): mit Tabs auf **Spalte 77** (Tabbreite 4) ausgerichtet. Ist der Code laenger, reicht ein Tab.
- Enum-Werte werden im Kommentar mit ihrem Zahlenwert begonnen: `// 3 Anlasser betaetigt`.

### Leerzeilen

- Zwischen logischen Bloecken innerhalb einer Funktion eine Leerzeile.
- Vor `break;` bzw. `return` darf zur Trennung eine Leerzeile stehen.

### `#define`

- Werte einer Gruppe stehen per Tabs ausgerichtet untereinander.
- Name in `GROSSBUCHSTABEN` mit `_`.

---

## 6. Namenskonventionen

| Element | Konvention | Beispiel |
|---|---|---|
| Dateien | Kleinbuchstaben, `_` als Trenner | `canbus_ringbuffer.c` |
| Include-Guard | `INC_<DATEI>_H_` | `INC_CANBUS_H_` |
| Versions-Defines | `<DATEI>_MAJOR/_MINOR/_PATCH/_DEV` | `MILLIS_MAJOR` |
| Konstanten / Makros | `GROSSBUCHSTABEN` | `ERROR_RESET` |
| Funktionen | camelCase, Modul-Praefix erlaubt | `setState`, `CANwrite` |
| Variablen | camelCase | `sizeRxBuffer`, `timeError` |
| Globale Instanzen | `Main_<Name>` bzw. `<Modul>_<Name>` | `Main_Statemaschine` |
| Struct-Typen | `<Name>_TypeDef` / `<Name>TypeDef` | `CAN_PaketTypeDef` |
| Enum-Werte | PascalCase oder `GROSS_MIT_UNTERSTRICH` | `ReadyToDrive`, `RX_SIZE_8` |

---

## 7. Automatische Pruefung

Das Skript [tools/c_stylecheck.py](tools/c_stylecheck.py) prueft C-Dateien gegen diesen Standard (benoetigt Python 3, keine weiteren Pakete).

```sh
py tools/c_stylecheck.py                          # alle Ordner ../STM32_* neben diesem Repo
py tools/c_stylecheck.py ../STM32_Canbus          # ein Ordner
py tools/c_stylecheck.py "../EAuto_*" ../IMD_*    # beliebige Ordner oder Glob-Muster
py tools/c_stylecheck.py ../STM32_Millis/millis.h # eine Datei
py tools/c_stylecheck.py -q                       # nur Dateien mit Befund anzeigen
py tools/c_stylecheck.py -s                       # nur Zusammenfassung
py tools/c_stylecheck.py ../EAuto_BMS -x openblt  # zusaetzlich Pfade ausschliessen (Regex)
py tools/c_stylecheck.py -r                       # je Projekt Report nach reports/<JJJJMMTT>_<Projekt>.txt
py tools/c_stylecheck.py "../EAuto_*" -r          # Reports fuer andere Ordner
```

Ein Report listet je Datei jeden Befund mit Zeilennummer und Kategorie (`Datei` = betrifft die ganze Datei, z. B. fehlender Abschnitt). Jeder per Pfad oder Glob gefundene Ordner gilt als eigenes Projekt. Der Dateiname beginnt mit dem Datum (z. B. `20261008_STM32_Canbus.txt`); ein Report vom selben Tag wird ueberschrieben, aeltere bleiben erhalten. Der Ordner `reports/` steht in der `.gitignore`.

HAL-, CMSIS-, Startup- und von STM32CubeMX generierte Dateien (`USER CODE BEGIN`) werden automatisch uebersprungen; mit `--no-default-exclude` werden sie mitgeprueft. Rueckgabewert: `0` = keine Befunde, `1` = Befunde, `2` = keine Dateien gefunden.

---

## 8. Checkliste

- [ ] Dateikopf vollstaendig (Titel, Sprache, Datum, Version, Autor, Projekt, Quelle)
- [ ] Alle Pflichtabschnitte vorhanden und in der richtigen Reihenfolge
- [ ] Leere Include-Abschnitte trotzdem angelegt
- [ ] `.h`: `#pragma once` **und** Include-Guard `INC_<NAME>_H_`
- [ ] `.h`: Versions-Defines vorhanden
- [ ] Jede Funktion mit Beschreibungskommentar und Trennlinien
- [ ] Tabs statt Leerzeichen, Allman-Klammern
- [ ] `case`-Bloecke mit `{ }`, `default` vorhanden
- [ ] Kommentare deutsch, ohne Umlaute
- [ ] Kein Doxygen, kein `extern "C"`
