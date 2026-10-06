#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==============================================================================
N O P L . P Y  --  Uniwersalny Silnik Transkrypcji i Odwracalności Ortografii
==============================================================================
Skrypt służy do konwersji tekstów z polskiej ortografii tradycyjnej (PL) na
alternatywne warianty zapisu (NOPL) i z powrotem.
"""

import sys
import os
import re
from pathlib import Path

try:
    import yaml
    HAS_PYYAML = True
except ImportError:
    HAS_PYYAML = False

DEFAULT_EMBEDDED_YAML = r"""
# Pełna, czytelna nazwa wariantu wyświetlana w interfejsie i pomocy
name: "Nowa Ortografia PoLska ASCII (Wariant zero)"

# Unikalny identyfikator systemowy używany w nagłówkach plików i nazwach cache
id: "zero"

# Lista przełączników CLI przypisanych do tej ortografii
flag:
  - "-a"
  - "--zero"

# Przyrostek dodawany do nazwy pliku po konwersji
file_ext: ".zero"

# Zbiór samogłosek
vowels: "aeiouy"

description: "Domyślny wariant zero (-a) - w celach poznawczych"

rules:
#  a: "*"
  ą: "aa" # sąsiad -> saasiad
#  b: "*"
#  c: "*"
  ć: "cj" # ćwiczenie -> cjviczenie
#  d: "*"
#  e: "*"
  ę: "ee" # potęga -> poteega
#  f: "*"
#  g: "*"
#  h: "*"
#  i: "*"
#  j: "*"
#  k: "*"
#  l: "*"
  ł: "ll" # iłołupki -> illollupki
#  m: "*"
#  n: "*"
  ń: "nj" # bańka -> banjka
#  o: "*"
  ó: "oo" # ogórek -> ogoorek
#  p: "*"
#  r: "*"
#  s: "*"
  ś: "sj" # śpiewaczka -> sjpievaczka
#  t: "*"
#  u: "*"
#  w: "*"
#  y: "*"
#  z: "*"
  ź: "zj" # źrebię -> zjrebiee
  ż: "zh" # żagiel -> zhagiel
## dwuznaki
#  ci: "*"
#  ni: "*"
#  si: "*"
#  zi: "*"
  ch: "ch" # chętka -> cheetka
  cz: "cz" # czwórka -> czwoorka
  dz: "dz" # dzyń -> dzynj
  dź: "dj" # dźwięk -> djwieek
  dż: "dzh" # dżdżownica -> dzhdzhownica
  rz: "rz" # rzeka -> rzeka
  sz: "sz" # szyna -> szyna
  di: "di" # diereza -> diereza
  cj: "cj" # kolacja -> kolacja
### trójznaki
  dzi: "dzi" # dzik -> dzik
#### czwór-znaki
  szcz: "szcz"
  ść: "sjcj"

regex_patterns:
  to_target: # tłumaczenie pl -> nopl
#    - pattern: '\b(na|nad|nie|od|pod|prze|przed|z|za)(r)'
#      replace: '\1#r'
#    - pattern: '([aeiouy])s\b'
#      replace: '\1z'
    - pattern: 'marz([lłn])'
      replace: '\\g<0>'
  from_target: # tłumaczenie nopl -> pl
#    - pattern: '#r'
#      replace: 'r'
    - pattern: 'marz([lłn])'
      replace: '\\g<0>'

## Omówienie zmiękczania i jotowania
# Z podobną niekonsekwencją jak w oryginalnej polskiej ortografii mamy 
# zmiękczenie udźwięcznione (po którym następuje samogłoska) oraz ubezdźwięcznione,
# po którym następuje spółgłoska (lub koniec wyrazu):
# cienko, sianko, niebo, ziewasz
# śpiewasz, ćwiczenie, koń, źrebię
# Mamy też jotowanie pochodzące z języków obcych:
# kolacja, pasja, okazja
# Aby wprowadzać jak najmniej zmian do ortografii podmianie podlegają wyłącznie 
# znaki polskie: ć->cj,ś->sj,ń->nj,ź->zj
# ale pamiętajmy, że w języku polskim mają one zastosowanie wyłącznie w kontakcie
# ze spółgłoską (lub na końcu wyrazu)!
# Jeżeli chcemy zabezpieczyć się przed błędną translacją **wsteczną** wyrazów np. z
# sanskrytu (np. śiwa), niestety, trzeba sporządzić stosowne reguły regex, lub
# zgodzić się, że ortografia jest trochę niejasna, jak w innych językach.

"""

MASK_V_CHAR = "\uE000"
HEADER_BOUNDARY = "---"
RESERVED_FLAGS = {"-h", "--help", "-r", "--rev", "--reverse", "--list"}


def parse_yaml_fallback(text: str) -> dict:
    data = {"rules": {}}
    in_rules = False
    
    for line in text.splitlines():
        line_strip = line.strip()
        if not line_strip or line_strip.startswith('#'):
            continue
            
        if line_strip == "rules:":
            in_rules = True
            continue
            
        if in_rules:
            if ":" in line_strip:
                k, v = line_strip.split(":", 1)
                k = k.strip().strip('"').strip("'")
                v = v.strip().strip('"').strip("'")
                data["rules"][k] = v
        else:
            if ":" in line_strip:
                k, v = line_strip.split(":", 1)
                k = k.strip().strip('"').strip("'")
                v = v.strip().strip('"').strip("'")
                data[k] = v
    return data


def load_yaml_string(yaml_str: str) -> dict:
    if HAS_PYYAML:
        return yaml.safe_load(yaml_str)
    return parse_yaml_fallback(yaml_str)


DEFAULT_CONFIG = load_yaml_string(DEFAULT_EMBEDDED_YAML)
DEFAULT_VARIANT_ID = DEFAULT_CONFIG["id"]
DEFAULT_FILE_EXT = DEFAULT_CONFIG["file_ext"]


def get_flags_list(cfg: dict) -> list:
    flags = []
    for key in ("flags", "flag"):
        if key in cfg and cfg[key]:
            val = cfg[key]
            if isinstance(val, list):
                flags.extend([str(item).strip() for item in val if item])
            else:
                flags.append(str(val).strip())
    return list(dict.fromkeys(flags))


DEFAULT_FLAGS = get_flags_list(DEFAULT_CONFIG)
DEFAULT_FLAG = DEFAULT_FLAGS[0] if DEFAULT_FLAGS else "-a"


def validate_orthography_config(cfg: dict, source_name: str) -> bool:
    if not isinstance(cfg, dict):
        return False
    for required_key in ("id", "rules"):
        if required_key not in cfg or not cfg[required_key]:
            return False
    cfg_flags = get_flags_list(cfg)
    if not cfg_flags:
        return False
    for flag in cfg_flags:
        if flag in RESERVED_FLAGS:
            return False
    if not isinstance(cfg["rules"], dict) or not cfg["rules"]:
        return False
    return True


def load_all_orthographies(input_file_path: Path = None) -> dict:
    orthographies = {}
    if validate_orthography_config(DEFAULT_CONFIG, "EMBEDDED_YAML"):
        orthographies[DEFAULT_VARIANT_ID] = DEFAULT_CONFIG

    search_dirs = [Path(__file__).parent / "nopl_config"]
    if input_file_path:
        search_dirs.append(input_file_path.parent / "nopl_config")

    for cdir in search_dirs:
        if cdir.exists() and cdir.is_dir():
            for yfile in cdir.glob("*.yaml"):
                try:
                    cfg = load_yaml_string(yfile.read_text(encoding="utf-8"))
                    if validate_orthography_config(cfg, yfile.name):
                        existing_flags = set()
                        for c in orthographies.values():
                            existing_flags.update(get_flags_list(c))
                        cfg_flags = get_flags_list(cfg)
                        has_conflict = any(f in existing_flags for f in cfg_flags)
                        if has_conflict and cfg["id"] not in orthographies:
                            continue
                        orthographies[cfg["id"]] = cfg
                except Exception:
                    pass
    return orthographies


def get_cache_path(input_path: Path, orth_id: str) -> Path:
    cache_dir = input_path.parent / "nopl_cache"
    cache_dir.mkdir(exist_ok=True, parents=True)
    return cache_dir / f"{input_path.name}.{orth_id}.cache"


def load_combined_cache(input_path: Path, target_variant: str, orig_path: Path) -> set:
    protected_words = set()
    found_sources = []

    local_cache_path = get_cache_path(orig_path, target_variant)
    if local_cache_path.exists():
        words = local_cache_path.read_text(encoding="utf-8").splitlines()
        protected_words.update(w.strip() for w in words if w.strip())
        found_sources.append(f"nopl_cache/{local_cache_path.name} [LOKALNY]")

    config_dirs = [
        Path(__file__).parent / "nopl_config",
        input_path.parent / "nopl_config"
    ]
    
    global_cache_files = []
    for cdir in config_dirs:
        if cdir.exists() and cdir.is_dir():
            for gfile in cdir.glob("*.cache"):
                if target_variant in gfile.name:
                    global_cache_files.append(gfile)

    global_cache_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    for gfile in global_cache_files:
        words = gfile.read_text(encoding="utf-8").splitlines()
        new_words = [w.strip() for w in words if w.strip()]
        protected_words.update(new_words)
        found_sources.append(f"nopl_config/{gfile.name}")

    if found_sources:
        print(f"Cache : Wczytano hierarchicznie źródła: {', '.join(found_sources)} (łącznie {len(protected_words)} unikanych słów)")
    else:
        print("INFORMACJA: Brak plików pamięci powrotnej. Przetwarzanie czysto algorytmiczne.")

    return protected_words


def encode_single_pass(text: str, cfg: dict) -> str:
    rules_dict = cfg.get("rules", {})
    regex_cfg = cfg.get("regex_patterns", {})
    to_target_regex = regex_cfg.get("to_target", []) if isinstance(regex_cfg, dict) else []

    patterns = []
    actions = {}

    # 1. Reguły z sekcji Regex mają bezwzględny priorytet
    for idx, item in enumerate(to_target_regex):
        if isinstance(item, dict) and "pattern" in item and "replace" in item:
            grp_name = f"REGEX_{idx}"
            patterns.append(f"(?P<{grp_name}>{item['pattern']})")
            actions[grp_name] = ("REGEX", item['replace'])

    # 2. Dopisujemy reguły ze słownika 'rules'
    sorted_rules = sorted(rules_dict.items(), key=lambda x: len(x[0]), reverse=True)
    for idx, (pl, nopl) in enumerate(sorted_rules):
        grp_name = f"RULE_{idx}"
        patterns.append(f"(?P<{grp_name}>{re.escape(pl)})")
        actions[grp_name] = ("RULE", nopl)

    if not patterns:
        return text

    master_regex = re.compile("|".join(patterns), re.IGNORECASE)

    def replacer(match):
        grp = match.lastgroup
        kind, val = actions[grp]
        if kind == "REGEX":
            return match.expand(val)
        else:
            matched = match.group(0)
            if matched.isupper():
                return val.upper()
            elif matched[0].isupper():
                return val[0].upper() + val[1:]
            return val.lower()

    text_masked = text.replace('v', MASK_V_CHAR).replace('V', MASK_V_CHAR.upper())
    res = master_regex.sub(replacer, text_masked)
    return res.replace(MASK_V_CHAR, 'v').replace(MASK_V_CHAR.upper(), 'V')


def decode_single_pass(text: str, cfg: dict, protected_words: set = None) -> str:
    rules_dict = cfg.get("rules", {})
    vowels_set = set(cfg.get("vowels", "aeiouy"))
    regex_cfg = cfg.get("regex_patterns", {})
    from_target_regex = regex_cfg.get("from_target", []) if isinstance(regex_cfg, dict) else []

    reverse_rules = []
    for pl, nopl in rules_dict.items():
        reverse_rules.append((nopl, pl))
    reverse_rules.sort(key=lambda x: (len(x[0]), 1 if x[0] == x[1] else 0), reverse=True)

    patterns = []
    actions = {}

    # 1. Regexy z section from_target wygrywają z ogólnym słownikiem
    for idx, item in enumerate(from_target_regex):
        if isinstance(item, dict) and "pattern" in item and "replace" in item:
            grp_name = f"REGEX_{idx}"
            patterns.append(f"(?P<{grp_name}>{item['pattern']})")
            actions[grp_name] = ("REGEX", item['replace'])

    # 2. Odwrócone reguły ze słownika
    seen_nopl = set()
    for idx, (nopl, pl) in enumerate(reverse_rules):
        if nopl in seen_nopl:
            continue
        seen_nopl.add(nopl)
        grp_name = f"RULE_{idx}"
        patterns.append(f"(?P<{grp_name}>{re.escape(nopl)})")
        actions[grp_name] = ("RULE", pl)

    master_regex = re.compile("|".join(patterns), re.IGNORECASE) if patterns else None

    def replacer(match):
        grp = match.lastgroup
        kind, val = actions[grp]
        if kind == "REGEX":
            return match.expand(val)

        target_pl = val
        matched = match.group(0)

        if target_pl in ('ś', 'ć', 'ń', 'ź', 'dź', 'ę', 'ą'):
            next_char = match.string[match.end():match.end() + 1]
            if next_char and next_char.lower() in vowels_set:
                return matched

        if matched.isupper():
            return target_pl.upper()
        elif matched[0].isupper():
            return target_pl[0].upper() + target_pl[1:]
        return target_pl.lower()

    if protected_words:
        nopl_to_pl_cache = {}
        for pl_word in protected_words:
            nopl_w = encode_single_pass(pl_word, cfg)
            nopl_to_pl_cache[nopl_w] = pl_word
            nopl_to_pl_cache[nopl_w.lower()] = pl_word.lower()
            nopl_to_pl_cache[nopl_w.capitalize()] = pl_word.capitalize()

        def process_word(word_match):
            w = word_match.group(0)
            if w in nopl_to_pl_cache:
                return nopl_to_pl_cache[w]
            return master_regex.sub(replacer, w) if master_regex else w

        return re.sub(r'\b[\w\x80-\xff-]+\b', process_word, text)

    return master_regex.sub(replacer, text) if master_regex else text


def build_and_save_cache(input_path: Path, orth_id: str, text_pl: str, cfg: dict):
    words = re.findall(r'\b[\w\x80-\xff-]+\b', text_pl)
    collisions = set()

    for word in set(words):
        enc = encode_single_pass(word, cfg)
        dec = decode_single_pass(enc, cfg)
        if dec != word:
            collisions.add(word)

    cache_path = get_cache_path(input_path, orth_id)
    if collisions:
        cache_path.write_text("\n".join(sorted(collisions)), encoding="utf-8")
        print(f"Cache : Zapisano {len(collisions)} słów do nopl_cache/{cache_path.name}")
    elif cache_path.exists():
        cache_path.unlink()


def write_converted_file(output_path: Path, text_content: str, orth_id: str):
    if text_content.startswith(HEADER_BOUNDARY):
        parts = text_content.split(HEADER_BOUNDARY, 2)
        if len(parts) >= 3:
            yaml_header = parts[1].rstrip()
            yaml_header += f"\nnopl_variant: {orth_id}\n"
            full_text = f"{HEADER_BOUNDARY}{yaml_header}\n{HEADER_BOUNDARY}{parts[2]}"
            output_path.write_text(full_text, encoding="utf-8")
            return

    header = f"{HEADER_BOUNDARY}\nnopl_variant: {orth_id}\n{HEADER_BOUNDARY}\n"
    output_path.write_text(header + text_content, encoding="utf-8")


def read_file_metadata(file_path: Path) -> str:
    try:
        content = file_path.read_text(encoding="utf-8")
        if content.startswith(HEADER_BOUNDARY):
            parts = content.split(HEADER_BOUNDARY, 2)
            if len(parts) >= 3:
                yaml_part = parts[1]
                for line in yaml_part.splitlines():
                    if line.startswith("nopl_variant:"):
                        return line.replace("nopl_variant:", "").strip().strip('"').strip("'")
    except Exception:
        pass
    return None


def print_simple_usage():
    print("Sposób użycia:")
    print(f"  ./nopl.py plik.txt              (Konwersja PL -> NOPL domyślnym wariantem {DEFAULT_FLAG})")
    print(f"  ./nopl.py {DEFAULT_FLAG} plik.txt           (Konwersja PL -> NOPL domyślnym wariantem {DEFAULT_FLAG})")
    print(f"  ./nopl.py {DEFAULT_FLAG} -r plik.txt        (Konwersja PL -> NOPL z utworzeniem nopl_cache)")
    print(f"  ./nopl.py -r plik{DEFAULT_FILE_EXT}.txt        (Rozpoznanie i translacja powrotna NOPL -> PL)")
    print("  ./nopl.py --list                (Wyświetla dostępne ortografie)")
    print("  ./nopl.py -h / --help           (Pełna instrukcja)")


def print_full_help(ortho_dict: dict):
    default_cfg = ortho_dict.get(DEFAULT_VARIANT_ID, DEFAULT_CONFIG)
    def_name = default_cfg.get('name', 'Domyślna')
    
    print(__doc__)
    print("===============================================================================")
    print("I. PODSTAWOWE SPOSOBY WYWOŁANIA")
    print("===============================================================================")
    print(f"  1. Konwersja PL -> NOPL (domyślny wariant: {def_name}):")
    print(f"     ./nopl.py plik.txt              (zwykła konwersja domyślnym wariantem {DEFAULT_FLAG})")
    print(f"     ./nopl.py {DEFAULT_FLAG} plik.txt           (jawne wywołanie wariantu {DEFAULT_FLAG})")
    print(f"     ./nopl.py {DEFAULT_FLAG} -r plik.txt        (konwersja z utworzeniem nopl_cache/)")
    print(f"     ./nopl.py -r plik.txt           (skrót: konwersja domyślna z nopl_cache/)")
    print("\n  2. Konwersja PL -> NOPL własnym wariantem (np. -f dla nopl_fonetyczna):")
    print("     ./nopl.py -f plik.txt")
    print("     ./nopl.py -f -r plik.txt")
    print("\n  3. Translacja powrotna NOPL -> PL (automatyczna detekcja ortografii):")
    print(f"     ./nopl.py -r plik{DEFAULT_FILE_EXT}.txt")
    print("\n  4. Informacje o systemie:")
    print("     ./nopl.py --list                (lista zarejestrowanych wariantów)")
    print("     ./nopl.py -h / --help           (niniejsza instrukcja)")


def main():
    args = sys.argv[1:]
    ortho_dict = load_all_orthographies()

    if not args:
        print_simple_usage()
        return 0

    if "-h" in args or "--help" in args:
        print_full_help(ortho_dict)
        return 0

    if "--list" in args:
        print("Dostępne warianty ortografii w systemie:")
        for oid, cfg in ortho_dict.items():
            flags_str = ", ".join(get_flags_list(cfg))
            ext = cfg.get('file_ext', DEFAULT_FILE_EXT)
            print(f"  • {oid:<15} ({flags_str:<12}) - {cfg.get('name')} (Ext: {ext})")
        return 0

    use_cache_gen = False
    input_file_str = None
    selected_variant_id = None
    has_explicit_variant_flag = False

    if "-r" in args or "--rev" in args or "--reverse" in args:
        use_cache_gen = True

    for oid, cfg in ortho_dict.items():
        cfg_flags = get_flags_list(cfg)
        if any(flag in args for flag in cfg_flags):
            selected_variant_id = oid
            has_explicit_variant_flag = True
            break

    for arg in args:
        if arg not in ("-r", "-rev", "--reverse") and not arg.startswith("-"):
            input_file_str = arg
            break

    if not input_file_str:
        print("Błąd: Nie podano pliku do przetworzenia.\n", file=sys.stderr)
        print_simple_usage()
        return 1

    input_path = Path(input_file_str)
    if not input_path.exists():
        print(f"Błąd: Plik '{input_path}' nie istnieje.", file=sys.stderr)
        return 2

    ortho_dict = load_all_orthographies(input_path)

    is_converted_file = False
    if read_file_metadata(input_path) is not None:
        is_converted_file = True
    else:
        for oid, cfg in ortho_dict.items():
            ext = cfg.get("file_ext", DEFAULT_FILE_EXT)
            if ext and ext in input_path.name:
                is_converted_file = True
                break

    if has_explicit_variant_flag or (not use_cache_gen and not is_converted_file) or (use_cache_gen and not is_converted_file):
        if selected_variant_id is None:
            selected_variant_id = DEFAULT_VARIANT_ID

        cfg = ortho_dict.get(selected_variant_id)
        text = input_path.read_text(encoding="utf-8")
        converted = encode_single_pass(text, cfg)

        out_ext = cfg.get("file_ext", DEFAULT_FILE_EXT)
        out_path = input_path.parent / f"{input_path.stem}{out_ext}{input_path.suffix}"
        
        write_converted_file(out_path, converted, selected_variant_id)

        flags_used_str = ", ".join(get_flags_list(cfg))
        print(f"Wariant: {cfg.get('name')} [{selected_variant_id}] ({flags_used_str})")
        print(f"Źródło : {input_path}")
        print(f"Wynik  : {out_path}")

        if use_cache_gen:
            build_and_save_cache(input_path, selected_variant_id, text, cfg)
        else:
            print("Cache  : Wyłączony (użyj -r obok flagi wariantu, aby zapisać pamięć powrotną).")

    elif use_cache_gen and is_converted_file:
        meta_variant = read_file_metadata(input_path)
        filename_variant = None
        for oid, cfg in ortho_dict.items():
            ext = cfg.get("file_ext", DEFAULT_FILE_EXT)
            if ext and ext in input_path.name:
                filename_variant = oid
                break

        if meta_variant and filename_variant and meta_variant != filename_variant:
            print(f"BŁĄD SPRZECZNOŚCI: Nagłówek pliku wskazuje ortografię '{meta_variant}', "
                  f"ale nazwa pliku sugeruje '{filename_variant}'. Przerwanie pracy!", file=sys.stderr)
            return 4

        target_variant = meta_variant or filename_variant or DEFAULT_VARIANT_ID
        
        if target_variant not in ortho_dict:
            print(f"Błąd: Nie odnaleziono konfiguracji dla ortografii '{target_variant}'.", file=sys.stderr)
            return 5

        cfg = ortho_dict[target_variant]
        ext_to_remove = cfg.get("file_ext", DEFAULT_FILE_EXT)
        orig_filename = input_path.name.replace(ext_to_remove, "")
        orig_path = input_path.parent / orig_filename
        
        protected_words = load_combined_cache(input_path, target_variant, orig_path)

        raw_lines = input_path.read_text(encoding="utf-8").splitlines(keepends=True)
        clean_lines = []
        fm_count = 0
        for line in raw_lines:
            if line.strip() == HEADER_BOUNDARY:
                fm_count += 1
                if fm_count <= 2:
                    continue
            if fm_count < 2:
                continue
            clean_lines.append(line)

        text_nopl = "".join(clean_lines) if fm_count >= 2 else "".join(raw_lines)
        restored_text = decode_single_pass(text_nopl, cfg, protected_words)

        out_path = input_path.parent / f"{orig_path.stem}.pl{input_path.suffix}"
        out_path.write_text(restored_text, encoding="utf-8")

        print(f"Odkodowano ortografię: {cfg.get('name')} [{target_variant}]")
        print(f"Źródło: {input_path}")
        print(f"Wynik : {out_path}")

    else:
        print("Błąd: Nie określono operacji. Podaj nazwę pliku, flagę wariantu lub flagę powrotu (-r).\n", file=sys.stderr)
        print_simple_usage()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())