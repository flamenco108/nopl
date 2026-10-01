#!/bin/bash

# czas w sekundach do wprowadzenia domyślnej wiadomości do komitu
CZAS=30

# Domyślna wiadomość komitu
default_message="$USER@$(hostname -s) AUTO-KOMIT $(date)"

# Funkcja do odliczania czasu w tle
countdown() {
    local end=$((SECONDS+$CZAS))
    while [ $SECONDS -lt $end ]; do
        sleep 1
    done
    echo -e "\nCzas minął. Używam domyślnej wiadomości."
}

# Prośba o wprowadzenie wiadomości komitu
echo ""
echo "Wprowadź wiadomość komitu (lub naciśnij Enter dla domyślnej wiadomości):"
echo ""
echo "Domyślna wiadomość: $default_message"
echo ""
echo "Masz $CZAS sekund na wprowadzenie wiadomości:"

# Uruchomienie odliczania w tle
countdown &
countdown_pid=$!

# Oczekiwanie na input użytkownika
read -t $CZAS komitmessage

# Zatrzymanie procesu odliczania
kill $countdown_pid 2>/dev/null

# Jeśli użytkownik nie wprowadził niczego, użyj domyślnej wiadomości
if [ -z "$komitmessage" ]; then
    komitmessage="$default_message"
fi

GIT=$(which git)

# Komitowanie zmian
$GIT add --all . && \
$GIT commit -m "$komitmessage" && \
$GIT push origin master
# $GIT push master
