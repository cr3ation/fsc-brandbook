# Bygga och ändra brandbooken

Projektroten **är** boken, med samma struktur som paketet som levereras:

```
bilder/        live-original (mästerfiler), live-guldton (genereras), stamningsbilder
farger/  guldton/  logo/  typsnitt/
webbversion/   index.html (källan för all text och layout), fonts/, img/ (genereras)
brandbook.pdf  (genereras)
LÄSMIG.txt
```

Allt som behövs för att bygga ligger i den här dolda mappen, `.bygg/`. Inget installeras lokalt. Allt körs i Docker.

```
.bygg/bygg.sh            # bilder, PDF, kontroller och zip
```

| I `.bygg/` | Innehåll | I git |
|---|---|---|
| `bygg.sh` | Byggkommandot | ja |
| `bilder.json` | Vilket foto som hamnar i vilken bildyta, med utsnitt, färgbehandling och alla beslut | ja |
| `startsida-2x.png` | Skärmbilden av startsidan som visas på s.18 | ja |
| `skript/`, `docker/` | Byggskript (Python) och Dockerfiler | ja |
| `reserv/` | Alternativ som inte valdes, kamerafilerna med EXIF och förslagssidan | nej |
| `tmp/`, `ut/` | Mellanresultat och den färdiga zipen | nej |

## Ändra text eller layout

Ändra i `webbversion/index.html`, granska och bygg:

```
.bygg/bygg.sh visa 3,17      # renderar sidorna 3 och 17 till .bygg/tmp/forhandsvisning/
.bygg/bygg.sh pdf && .bygg/bygg.sh kontroll
```

Boken ska ha **20 sidor**, eftersom tryckeriet kräver 20 eller 24. Kontrollen stoppar bygget om sidantalet är fel. Lägger du till eller tar bort en sida måste du också räkna om:
- innehållsförteckningen på s.2,
- sidnumren i sidfötterna,
- hänvisningar som "(s. 17)" i texterna och i `LÄSMIG.txt`, `guldton/LÄSMIG.txt`,
- `SIDOR` i `bygg.sh`.

## Byta ett foto

1. Lägg in fotot som mästerfil: `.bygg/bygg.sh importera <kamerafil> <namn>`. Det blir `bilder/live-original/live-<namn>-original.jpg`, i sRGB och utan EXIF. Med `--morkare 1.0` mörkas en starkt mättad bakgrund, till exempel en orange gardin, ett steg.
2. I `bilder.json`: lägg till ett motiv (`fil`, `exp`, `con`, `paketnamn`) och peka bildytan mot det. `cx`/`cy` är utsnittets mitt (0–1) och `scale` är hur stor del av största möjliga utsnitt som används.
3. `.bygg/bygg.sh bilder` och sedan `.bygg/bygg.sh visa <sida>` för att granska.
4. Ta bort mästerfiler som inte längre används från `bilder/live-original/`.

Kontrollen kräver minst 300 ppi. Färgfoton guldtonas med `guldton/fsc-guldton.cube`, efter exponering (`exp`, i steg) och kontrast (`con`).
- `"original": true` ger bilden utan guldton, för före/efter på s.16.
- `"kanttoning"` tonar en kant mot Midnatt där en CSS-toning ligger över fotot. Det syns inte, men hindrar PDF-visare från att visa en ljus glipa.

Reservalternativen i `reserv/reserver.json` är färdiga att klistra in.

## Regler att hålla

Boken ska vara enhetlig. Ändringar får inte gå emot det boken själv säger:
- **Färg:** guld är accent, och guld och champagne används aldrig på ljus botten (s.11).
- **Typografi:** Playfair till rubriker och kursiva ingresser och citat, DM Sans till brödtext och etiketter (s.12–13).
- **Bilder:** livebilder guldtonas, inga vinjetter (s.15–16).
- **Namnet:** skrivs Freeport Soul Collective, med versalt F, S och C (s.17).
- **Logotyp:** det finns bara skrivstilslogotypen. Det finns inget alternativt ordmärke.

## Startsidan på s.18

Bilden är en skärmbild av den riktiga startsidan med AI-stämningsbilden i stället för reelen, eftersom reelen har lila scenljus. Ta om den med:

```
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD:/p" -w /p fsc-pw python3 -I .bygg/skript/startsida.py \
  bilder/stamningsbilder/stamning-mikrofon-saxofon.jpg .bygg/startsida-2x.png
```

`docker/ffmpeg/` behövs inte för bygget. Den används för att ta ut bildrutor ur bandets reel eller guldtona den.
