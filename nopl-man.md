# Podręcznik Użytkownika Skryptu `nopl.py`

Skrypt `nopl.py` jest uniwersalnym, bezzależnościowym silnikiem służącym do transkrypcji tekstów z tradycyjnej ortografii polskiej (PL) na alternatywne warianty zapisu (np. bez znaków diakrytycznych NOPL) oraz do wykonywania automatycznej translacji powrotnej (NOPL $\rightarrow$ PL).


---

## ⚙️ Wymagania i instalacja

* **Python:** Wersja `3.6` lub nowsza.
* **Zależności:** Skrypt jest w pełni samowystarczalny. Jeśli biblioteka `PyYAML` jest zainstalowana w systemie, skrypt z niej skorzysta; w przeciwnym razie użyje wbudowanego, autorskiego parsera YAML (`parse_yaml_fallback`).

Samo uruchomienie nie wymaga instalacji dodatkowych pakietów:

```bash
chmod +x nopl.py
./nopl.py --help

```

---

## ⚡ Szybki start (Ściągawka)

| Operacja | Polecenie | Wyjście / Opis |
| --- | --- | --- |
| **Lista ortografii** | `./nopl.py --list` | Wyświetla rejestr wszystkich dostępnych wariantów. |
| **Konwersja domyślna** | `./nopl.py plik.txt` | Tworzy `plik.zero.txt` (używając wariantu `-a`). |
| **Konwersja z Cache** | `./nopl.py -a -r plik.txt` | Tworzy `plik.zero.txt` oraz plik pamięci w `nopl_cache/`. |
| **Własny wariant** | `./nopl.py -b plik.txt` | Tworzy plik wyjściowy zgodny z przełącznikiem `-b` (np. `plik.aupl.txt`). |
| **Powrót do PL** | `./nopl.py -r plik.zero.txt` | Tworzy `plik.pl.txt` (odtwarza oryginalny język polski). |

---

## 🚀 Tryby pracy i składnia CLI

### 1. Wyświetlanie informacji

* **Lista wariantów:**
```bash
./nopl.py --list

```


Przeszukuje katalog `nopl_config/` i wyświetla tabelę znalezionych plików ortografii wraz z ich identyfikatorami, rozszerzeniami oraz przypisanymi flagami CLI.
* **Pomoc:**
```bash
./nopl.py -h
# lub
./nopl.py --help

```



---

### 2. Transkrypcja wprost (PL $\rightarrow$ NOPL)

Podanie nazwy pliku wejściowego powoduje jego przetworzenie na wybrany wariant NOPL.

```bash
# Użycie domyślnej ortografii (flaga -a / wariant zero)
./nopl.py dokument.txt

# Jawne podanie wariantu za pomocą flagi
./nopl.py -b dokument.txt
./nopl.py --aupl dokument.txt

```

#### Zachowanie skryptu:

1. Skrypt odczytuje treść pliku `dokument.txt`.
2. Wykonuje konwersję zgodnie z regułami wybranej ortografii.
3. Zapisuje plik wynikowy w tym samym katalogu, dodając rozszerzenie wariantu (np. `dokument.zero.txt` lub `dokument.aupl.txt`).
4. Do pliku wynikowego dodawany jest nagłówek metadanych w formacie YAML:
```yaml
---
nopl_variant: zero
---

```



---

### 3. Translacja powrotna (NOPL $\rightarrow$ PL)

Aby przywrócić tekst z wariantu NOPL do tradycyjnej polskiej ortografii, należy użyć flagi odwrócenia `-r` (lub `--rev` / `--reverse`).

```bash
./nopl.py -r dokument.zero.txt

```

#### Zachowanie skryptu:

1. Skrypt automatycznie wykrywa użyty wariant NOPL na podstawie nagłówka metadanych `nopl_variant:` lub rozszerzenia pliku.
2. Ładuje hierarchicznie pliki pamięci powrotnej (cache).
3. Odtwarza tekst w języku polskim i zapisuje go w pliku z przedrostkiem/przyrostkiem `.pl` (np. `dokument.pl.txt`).

---

## 🧠 Mechanizm pamięci powrotnej (Cache)

Język polski posiada homonimy i niejednoznaczności fonetyczne, które po usunięciu diakrytyków mogą prowadzić do kolizji (np. *może* i *morze* mogą w niektórych wariantach dać ten sam zapis). Aby zapewnić **100% bezstratną rekonstrukcję oryginału**, skrypt `nopl.py` wykorzystuje system pamięci powrotnej.

### Generowanie pamięci cache (`-r` podczas kodowania)

Gdy uruchomisz konwersję wprost z dołączoną flagą `-r`:

```bash
./nopl.py -a -r dokument.txt

```

Silnik wykona symulację odkodowania tekstu. Jeśli wykryje słowa, które po przejściu w obie strony nie wracają do swojej pierwotnej postaci, zapisze je jako listę wyjątków w katalogu `nopl_cache/`:

```text
nopl_cache/dokument.txt.zero.cache

```

### Hierarchia wczytywania cache przy odkodowywaniu

Podczas wykonywania `./nopl.py -r dokument.zero.txt` skrypt szuka ochrony dla słów w następującej kolejności:

1. **Cache lokalny:** `nopl_cache/<nazwa_pliku>.<id_wariantu>.cache`.
2. **Cache globalny/regionalny:** Wszelkie pliki `*.cache` znajdujące się w katalogu `nopl_config/`.

---

## 🛠️ Tworzenie i struktura plików konfiguracji (YAML)

Nowe warianty ortografii dodaje się poprzez umieszczenie pliku `.yaml` w katalogu `nopl_config/`.

### Wzorzec pliku konfiguracyjnego (`nopl_config/moj_wariant.yaml`)

```yaml
# Nazwa wyświetlana na liście i w pomocy
name: "Moja Ortografia Eksperymentalna"

# Unikalny identyfikator systemowy
id: "mojawyp"

# Flagi CLI przypisane do wariantu
flag:
  - "-m"
  - "--moja"

# Przyrostek pliku wynikowego
file_ext: ".moja"

# Zbiór samogłosek (używany do logiki zmiękczeń)
vowels: "aeiouy"

description: "Krótki opis mojej ortografii"

# Tabela podstawowej translacji znaków i dwuznaków
rules:
  ą: "aa"
  ć: "cj"
  ę: "ee"
  ł: "w"
  ń: "nj"
  ó: "oo"
  ś: "sj"
  w: "v"
  ź: "zj"
  ż: "zh"
  ch: "h"
  cz: "ch"
  dz: "dz"
  dź: "dj"
  dż: "dh"
  rz: "rh"
  sz: "sh"

# Wyrażenia regularne (wyższy priorytet niż sekcja 'rules')
regex_patterns:
  to_target:
    # Zabezpieczenie rdzenia 'marz-' przed zamianą 'rz' -> 'rh'
    - pattern: 'marz([lłn])'
      replace: '\g<0>'
  from_target:
    - pattern: 'marz([lłn])'
      replace: '\g<0>'

```

---

## 🏗️ Architektura silnika transkrypcji

Silnik `nopl.py` wykorzystuje **jednoprzebiegowy Master-Regex** (single-pass regex engine) do przetwarzania tekstu:

1. **Priorytetyzacja:** Wzorce z sekcji `regex_patterns` są umieszczane na początku zbiorczego wyrażenia regularnego, co daje im bezwzględny priorytet nad standardowymi regułami ze słownika `rules`.
2. **Sortowanie słownika:** Reguły z sekcji `rules` są automatycznie sortowane według długości klucza (od najdłuższych do najkrótszych, np. `szcz` przed `sz` i `s`), co zapobiega błędnemu częściowemu dopasowywaniu wieloznaków.
3. **Maskowanie znaku `v`:** Przed przystąpieniem do konwersji litera `v` obecna w tekście źródłowym jest tymczasowo zamieniana na bezpieczny znak Unikodu (`\uE000`), co zapobiega konfliktom w wariantach przekształcających `w` $\rightarrow$ `v`.
4. **Obsługa wielkości liter:** Silnik automatycznie rozpoznaje i zachowuje wielkość liter (małe litery, *Capitalized*, MAŁE LITERY).

---

## 🚨 Kody błędów (Exit Codes)

Skrypt zwraca następujące kody wyjścia do powłoki systemowej:

| Kod | Znaczenie |
| --- | --- |
| **`0`** | Sukces (operacja zakończona powodzeniem). |
| **`1`** | Błąd argumentów CLI (brak pliku lub nieokreślona operacja). |
| **`2`** | Plik wejściowy nie istnieje. |
| **`4`** | Błąd spójności (nagłówek pliku wskazuje inny wariant niż nazwa pliku). |
| **`5`** | Brak pliku konfiguracyjnego dla wskazanego wariantu ortografii. |