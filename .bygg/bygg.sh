#!/usr/bin/env bash
# Bygger Freeport Soul Collectives brandbook. Allt körs i Docker, inget installeras lokalt.
#
#   .bygg/bygg.sh               allt: bilder, PDF, kontroller och zip
#   .bygg/bygg.sh bilder        bara bilderna (webbversion/img och bilder/live-guldton)
#   .bygg/bygg.sh pdf           bara brandbook.pdf (gör tryckbilder först om de saknas)
#   .bygg/bygg.sh kontroll      kontrollera PDF (sidantal, 300 ppi) och webbversion
#   .bygg/bygg.sh zip           packa .bygg/ut/Freeport-Soul-Collective-Brandbook.zip
#   .bygg/bygg.sh visa 1,3,17   rendera sidor till .bygg/tmp/forhandsvisning för granskning
#   .bygg/bygg.sh importera <kamerafil> <namn> [--morkare 1.0]   nytt foto till bilder/live-original
set -euo pipefail
cd "$(dirname "$0")/.."          # projektroten = boken

SIDOR=20                         # tryckeriet kräver 20 eller 24 sidor
TMP=.bygg/tmp
CUBE=guldton/fsc-guldton.cube
U="$(id -u):$(id -g)"
STEG="${1:-allt}"

image() { docker image inspect "$1" >/dev/null 2>&1 || { echo "Bygger Docker-imagen $1"; docker build -q -t "$1" ".bygg/docker/$2" >/dev/null; }; }
kor() { local img=$1; shift; docker run --rm -u "$U" -v "$PWD:/p" -w /p "$img" python3 -I "$@"; }

image fsc-imgtools imgtools
image fsc-pw pw
image fsc-pdfcheck pdfcheck
mkdir -p "$TMP" .bygg/ut

bilder() {
  echo "== Bilder till boken"
  kor fsc-imgtools .bygg/skript/producera.py .bygg/bilder.json "$TMP/tryck" webbversion/img "$CUBE"
  echo "== Guldtonade foton i full upplösning till bilder/live-guldton"
  kor fsc-imgtools .bygg/skript/guldton.py .bygg/bilder.json "$CUBE"
}
pdf() {
  [ -f "$TMP/tryck/rapport.json" ] || bilder
  echo "== brandbook.pdf"
  kor fsc-pw .bygg/skript/pdf.py . "$TMP/tryck" "$TMP/utskrift"
}
kontroll() {
  echo "== Kontroll av PDF"
  kor fsc-pdfcheck .bygg/skript/kontroll.py brandbook.pdf "$SIDOR" "$TMP/sidor"
  echo "== Kontroll av webbversionen"
  kor fsc-pw .bygg/skript/kontroll_webb.py webbversion/index.html
}
packa() {
  echo "== Zip"
  kor fsc-imgtools .bygg/skript/packa.py .bygg/ut/Freeport-Soul-Collective-Brandbook.zip
}

case "$STEG" in
  bilder)    bilder ;;
  pdf)       pdf ;;
  kontroll)  kontroll ;;
  zip)       packa ;;
  visa)      kor fsc-pw .bygg/skript/forhandsvisa.py webbversion/index.html "$TMP/forhandsvisning" ${2:-} ;;
  importera) shift; kor fsc-imgtools .bygg/skript/importera.py "$@" ;;
  allt)      bilder; pdf; kontroll; packa; echo "Klart. Sidorna som PNG finns i $TMP/sidor, zipen i .bygg/ut." ;;
  *)         sed -n '2,11p' "$0"; exit 1 ;;
esac
