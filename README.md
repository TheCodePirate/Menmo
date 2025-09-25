# Funding Assistant Experience

Det här repositoriet innehåller en statisk prototyp av Menmos Funding Assistant &ndash; ett komplett B2B-gränssnitt inspirerat av moderna Azure- och Oracle-applikationer. Upplevelsen visar hur organisationer kan kombinera en citerande AI-assistent med kataloger för bidrag, behörighetskontroller, hållbarhetsmål, en orkestrerad ansökningspipeline samt ett portföljnav för ledningen. Dokument Intelligence-modellerna (Read, Layout och Prebuilt Forms) har egna sidor som beskriver hur de används i arbetsflödet.

## Starta gränssnittet lokalt

Servera innehållet i [`web/`](web/) med valfri statisk webbserver. Med Python 3 installerat kan du köra:

```bash
python3 -m http.server 8080 --directory web
```

Öppna <http://localhost:8080/> i webbläsaren för att starta Funding Assistant. Navigera via vänstermenyn för att utforska Funding Assistant, programkatalogen, behörighets- och hållbarhetsmodulerna, pipeline-översikten, Document Intelligence-sidorna eller versionarkivet. Använd länken **Company Home** uppe till höger för att se hela portföljen med statusar och rekommenderade åtgärder.
