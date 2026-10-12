# Stylecheck-Tools

Die Skripte pruefen Quelldateien gegen die Coding Styles von **Diveturtle93**:

| Skript | Prueft | Regeln | Voraussetzung |
|---|---|---|---|
| [c_stylecheck.py](c_stylecheck.py) | `.c` / `.h` | [C Coding Style](../C_CODING_STYLE.md) | Python 3 |
| [py_stylecheck.py](py_stylecheck.py) | `.py` | [Python Coding Style](../PYTHON_CODING_STYLE.md) | Python 3.10+, nutzt Hilfsfunktionen aus `c_stylecheck.py` |

Beide Skripte benoetigen keine weiteren Pakete und haben dieselben Optionen. Die Beispiele zeigen `c_stylecheck.py`, fuer Python wird nur der Skriptname getauscht.

---

## Aufruf

```sh
py tools/c_stylecheck.py                          # alle Ordner neben diesem Repo
py tools/c_stylecheck.py ../STM32_Canbus          # ein Ordner
py tools/c_stylecheck.py "../EAuto_*" ../IMD_*    # beliebige Ordner oder Glob-Muster
py tools/c_stylecheck.py ../STM32_Millis/millis.h # eine Datei
py tools/c_stylecheck.py -q                       # nur Dateien mit Befund anzeigen
py tools/c_stylecheck.py -s                       # nur Zusammenfassung
py tools/c_stylecheck.py ../EAuto_BMS -x openblt  # zusaetzlich Pfade ausschliessen (Regex)
py tools/c_stylecheck.py -r                       # je Projekt Report schreiben
py tools/c_stylecheck.py "../EAuto_*" -r          # Reports fuer andere Ordner
py tools/c_stylecheck.py -r -f                    # Reports nur fuer Projekte mit Befunden
py tools/c_stylecheck.py -c                       # alle Reports der Sprache loeschen
py tools/c_stylecheck.py -c out                   # alle Reports der Sprache in out/ loeschen
py tools/c_stylecheck.py -c -r                    # alte Reports loeschen, danach neu schreiben
py tools/c_stylecheck.py --no-default-exclude     # automatische Ausschluesse abschalten
```

Jeder per Pfad oder Glob gefundene Ordner gilt als eigenes Projekt. Ordner ohne passende Dateien werden beim Standardaufruf stillschweigend uebersprungen.

Rueckgabewert: `0` = keine Befunde, `1` = Befunde, `2` = keine Dateien gefunden.

---

## Reports

Mit `-r` wird je Projekt ein Report geschrieben, Standard-Ordner ist `reports/` in diesem Repo. Jede Sprache hat einen eigenen Unterordner:

| Skript | Report-Ordner | Beispiel |
|---|---|---|
| `c_stylecheck.py` | `reports/c/` | `reports/c/20261008_STM32_Canbus.txt` |
| `py_stylecheck.py` | `reports/py/` | `reports/py/20261012_EAuto_Dashboard.txt` |

- Ein Report listet je Datei jeden Befund mit Zeilennummer und Kategorie (`Datei` = betrifft die ganze Datei, z. B. fehlender Abschnitt).
- Der Dateiname beginnt mit dem Datum `<JJJJMMTT>`; ein Report vom selben Tag wird ueberschrieben, aeltere bleiben erhalten.
- Zusaetzlich entsteht immer `<JJJJMMTT>_Uebersicht.txt` mit einer Zeile je gepruefem Projekt (Dateien, Befunde, Report geschrieben ja/nein). Die Uebersicht enthaelt auch mit `-f` alle Projekte.
- `-c` loescht alle Reports (`<JJJJMMTT>_*.txt`, jedes Datum, jedes Projekt, auch die Uebersicht) im Unterordner der eigenen Sprache; andere Dateien und die Reports der anderen Sprache bleiben erhalten.

Der Ordner `reports/` steht in der `.gitignore`.

---

## Automatische Ausschluesse

Git-Submodule aus der `.gitmodules` des Projekts werden immer uebersprungen; sie sind eigene Repos und werden dort geprueft. Dazu kommen je Sprache:

**C**

- HAL-, CMSIS- und Startup-Dateien werden uebersprungen.
- Von STM32CubeMX generierte Dateien (z. B. unter `Core/`) werden nur zwischen `/* USER CODE BEGIN ... */` und `/* USER CODE END ... */` geprueft. Der Bereich `Header` (ST-Lizenzkopf) und die Pruefungen der Dateistruktur (Kopfblock, Abschnitte, Header, Debug-Symbole, Reihenfolge) entfallen, fehlerhafte Marker werden gemeldet. Im Report sind diese Dateien mit `nur USER CODE` gekennzeichnet.

**Python**

- Virtuelle Umgebungen (`venv`, `.venv`, `env`), `__pycache__`, `build`, `dist` und `site-packages` werden uebersprungen.

Mit `--no-default-exclude` werden alle diese Dateien vollstaendig geprueft.

---

## Projekteinstellungen (`.stylecheck`)

Projektspezifische Einstellungen stehen optional in der Datei `.stylecheck` im Projektordner. Sie wird von beiden Skripten gelesen:

| Abschnitt | Gilt fuer |
|---|---|
| `[stylecheck]` | beide Sprachen |
| `[c]` | nur `c_stylecheck.py`, ergaenzt `[stylecheck]` |
| `[py]` | nur `py_stylecheck.py`, ergaenzt `[stylecheck]` |

Ordner oder einzelne Dateien werden relativ zum Projektordner angegeben, mehrere mit Komma getrennt:

```ini
[stylecheck]
exclude = Test                  # fuer C und Python ausschliessen

[c]
exclude = Application/Inc/git.h # nur fuer C zusaetzlich ausschliessen
include = Core, Application     # nur diese Ordner pruefen

[py]
exclude = openblt               # nur fuer Python zusaetzlich ausschliessen
```

Die Datei wird nur angelegt, wenn die automatischen Ausschluesse nicht reichen. Die frueheren Dateien `.c_stylecheck` und `.py_stylecheck` werden nicht mehr gelesen; liegen sie noch im Projekt, gibt das Skript eine Warnung aus.
