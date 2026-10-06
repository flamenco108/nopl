# nopl - Nowa Ortografia PoLska - plus narzędzia

## Ortografia ASCII dla języka polskiego

Przy pomocy tej ortografii możemy pisać dowolny tekst po polsku, zachować czytelność,
ale nie musimy używać znaków spoza tablicy ASCII. A to oznacza, że możemy używać 
dowolnej klawiatury, a przede wszystkim najpopularniejszej. I o to mi chodziło.


[toc]

---

## Nowa Ortografia PoLska ASCII (Wariant zero)

Domyślna specyfikacja ortograficzna dla systemu **NOPL**, służąca do konwersji tekstu z tradycyjnej ortografii polskiej na wariant zgodny z podstawowym alfabetem ASCII (bez polskich znaków diakrytycznych).

---

### 🛠️ Informacje Techniczne

| Parametr | Wartość |
| --- | --- |
| **Nazwa wariantu** | Nowa Ortografia PoLska ASCII (Wariant zero) |
| **Identyfikator (ID)** | `zero` |
| **Przełączniki CLI** | `-a`, `--zero` |
| **Rozszerzenie pliku** | `.zero` |
| **Opis** | Domyślny wariant zero (`-a`) – w celach poznawczych |

---

### 🔤 Zasady Konwersji (Rules)

#### 1. Polskie litery diakrytyczne (Samogłoski i Spółgłoski)

| Litera PL | Zapis NOPL | Przykład konwersji |
| --- | --- | --- |
| **ą** | `aa` | *sąsiad* $\rightarrow$ **saasiad** |
| **ć** | `cj` | *ćwiczenie* $\rightarrow$ **cjviczenie** |
| **ę** | `ee` | *potęga* $\rightarrow$ **poteega** |
| **ł** | `ll` | *iłołupki* $\rightarrow$ **illollupki** |
| **ń** | `nj` | *bańka* $\rightarrow$ **banjka** |
| **ó** | `oo` | *ogórek* $\rightarrow$ **ogoorek** |
| **ś** | `sj` | *śpiewaczka* $\rightarrow$ **sjpiewaczka** |
| **ź** | `zj` | *źrebię* $\rightarrow$ **zjrebiee** |
| **ż** | `zh` | *żagiel* $\rightarrow$ **zhagiel** |

---

#### 2. Dwuznaki, Trójznaki i Czwórznaki

| Wzorce PL | Zapis NOPL | Uwagi / Przykłady |
| --- | --- | --- |
| **dź** | `dj` | *dźwięk* $\rightarrow$ **djwieek** |
| **dż** | `dzh` | *dżdżownica* $\rightarrow$ **dzhdzhownica** |
| **ść** | `sjcj` | połączenie `ś` (`sj`) + `ć` (`cj`) |
| **ch**, **cz**, **dz**, **rz**, **sz**, **di**, **cj**, **dzi**, **szcz** | *bez zmian* | zachowują tradycyjny zapis |

---

### 🧩 Reguły Wyrażeń Regularnych (Regex Patterns)

Wyrażenia regularne mają wyższy priorytet nad standardowymi regułami słownikowymi, zapobiegając błędnemu rozbijaniu złożeń i rdzeni wyrazowych:

```yaml
regex_patterns:
  to_target:
    - pattern: 'marz([lłn])'
      replace: '\g<0>'
  from_target:
    - pattern: 'marz([lłn])'
      replace: '\g<0>'

```

* **Zastosowanie:** Zabezpieczenie rdzenia czasownikowego *marz-* (np. *marzli*, *zmarzną*, *zamarzł*) przed niepożądanymi przekształceniami głosek $r+z$.

---

### 💡 Omówienie Zmiękczania i Jotowania

Wariacja ta zachowuje analogię do oryginalnej polskiej fonetyki i ortografii:

1. **Zmiękczenia udźwięcznione** (z następującą samogłoską): *cienko*, *sianko*, *niebo*, *ziewasz*.
2. **Zmiękczenia ubezdźwięcznione** (przed spółgłoską lub na końcu wyrazu): *śpiewasz*, *ćwiczenie*, *koń*, *źrebię*.
3. **Jotowanie obcego pochodzenia**: *kolacja*, *pasja*, *okazja*.

Aby wprowadzać jak najmniej zmian w tekście, bezpośredniej podmianie podlegają wyłącznie polskie znaki ze znakami diakrytycznymi (`ć` $\rightarrow$ `cj`, `ś` $\rightarrow$ `sj`, `ń` $\rightarrow$ `nj`, `ź` $\rightarrow$ `zj`), z uwzględnieniem faktu, że w języku polskim występują one w kontekście ze spółgłoską lub na końcu wyrazu.



## nopl - skrypt tłumaczący

### Skrypt `nopl.py` — Silnik Transkrypcji Ortograficznej

`nopl.py` to bezzależnościowy skrypt Python służący do automatycznej konwersji tekstów z tradycyjnej polskiej ortografii (PL) na alternatywne warianty zapisu bez diakrytyków (NOPL) oraz do wykonywania dwukierunkowej translacji powrotnej (NOPL → PL)[cite: 17].

#### Kluczowe funkcjonalności

* **Obsługa wariantów ortografii z YAML:** Ładuje definicje wariantów z katalogu `nopl_config/` (oraz wbudowaną domyślną konfigurację)[cite: 17].
* **Jednoprzebiegowy silnik reguł (Master-Regex):** Łączy zaawansowane reguły wyrażeń regularnych (`regex_patterns`) ze słownikiem zamian prostych (`rules`), gwarantując priorytet wyjątkom phonotaktycznym[cite: 17].
* **Pamięć powrotna (Cache kolizji):** Podczas konwersji z flagą `-r` tworzy pliki w katalogu `nopl_cache/`, zapisując słowa stanowiące dwuznaczności, co gwarantuje 100% bezstratną rekonstrukcję oryginału[cite: 17].
* **Metadane w nagłówkach:** Automatycznie wstawia oraz odczytuje nagłówki YAML (np. `nopl_variant: zero`) w przetwarzanych plikach, ułatwiając ich automatyczne odkodowanie[cite: 17].

#### Szybki start (Przykłady użycia)

```bash
# 1. Konwersja pliku domyślnym wariantem (-a)
./nopl.py plik.txt

# 2. Konwersja z wygenerowaniem pamięci powrotnej (cache kolizji)
./nopl.py -a -r plik.txt

# 3. Konwersja wybranym wariantem (np. -b / --aupl)
./nopl.py -b plik.txt

# 4. Automatyczna translacja powrotna z NOPL na PL
./nopl.py -r plik.zero.txt

# 5. Wyświetlenie listy dostępnych ortografii
./nopl.py --list

```

## Jak to się stało

Przenikliwe promieniowanie słoneczne pewnego gorącego dnia na plaży bałtyckiej sprawiło,
że z nudów pomyślałem o takim oto problemie: **polska ortografia**, choć tak dobrze już 
opracowana i zaadaptowana do współczesnej techniki, **ma jednak poważną słabość**, której
nie ma jej angielska odpowiedniczka. Otóż gdy klepiemy w klawiaturę, musimy w specjalny 
sposób wyciskać polskie znaki `ąęśżźćółń`. W tym celu musimy nacisnąć "Prawy Alt" lub 
dawniej zwany "Alt Gr" oraz literę, która najbardziej ów znak przypomina.

Dla klepacza posługującego się dwoma palcami na klawiaturze być może nie stanowi to problemu.
Ale dla piszącego bezwzrokowo jest to wybicie z rytmu, konieczność wykręcenia nadgarstka
i kciuka, spowolnienie pisania.

Po powrocie z plaży przystąpiłem do eksperymentów. Wyszło mi, że wyciśnięcie dowolnej
innej kombinacji klawiszy literowych - ale po kolei - jest znacznie szybsze niż 
kombinowanie z Altem. I tak dojrzało postanowienie stworzenia Nowej Polskiej Ortografii.

Jej podstawowym założeniem miało być czyste ASCII - ograczyć się wyłącznie do znaków 
dostępnych w tej tablicy, a zachować czytelność pisma.

Wkrótce okazało się, że możliwości jest więcej, niż mogłem się spodziewać. I tak oto 
dogadałem się z LLM'em i przy pomocy *vibe-codingu* wytworzyłem narzędzie pomocnicze,
którego zadaniem jest tłumaczenie tekstów w tę i nazad z zadanej ortografii.

Zapraszam innych wariatów, którzy chcieliby wypróbować to zagadnienie do testów. 
Liczę na uwagi krytyczne (na pochwały też).
