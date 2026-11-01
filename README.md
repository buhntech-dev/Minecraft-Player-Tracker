# Minecraft Player Tracker – Java Vanilla + GitHub Pages

Dieses Projekt besteht aus einer statischen Webseite (GitHub Pages), einem Vanilla-Datapack und einer kleinen Python-Bridge, die auf dem Minecraft-Server-Rechner läuft.

## Was erfasst wird?
- Tode, Spielzeit, Sprünge, Laufstrecke, Spieler-/Mob-Kills (Minecraft-Statistikwerte)
- Block-Abbau pro Blocktyp (Minecraft-Scoreboard-Statistik)
- Block-Platzierung: Vanilla bietet dafür keine allgemeine, dauerhaft abrufbare Scoreboard-Statistik. Das Datapack erfasst deshalb Platzierungen über Advancement-Ereignisse nicht vollständig für beliebige Blöcke. Für vollständige Place-Logs ist ein Server-Plugin/Mod oder ein eigenes Event-Logging-System nötig. Dieses Projekt zeigt Platzierungen daher als optionale Daten und behauptet nicht, sie vollständig zu erfassen.
- Vanilla kann keine historische Liste rückwirkend erzeugen. Der Tracker erfasst Werte ab Installation.

## 1. GitHub Pages einrichten
1. Erstelle ein privates oder öffentliches GitHub-Repository und lade den Inhalt dieses Ordners hoch.
2. In **Settings → Pages** wähle `Deploy from a branch`, Branch `main`, Ordner `/ (root)`.
3. Warte, bis GitHub Pages die URL anzeigt.
4. Lege unter **Settings → Secrets and variables → Actions** kein Token für die Webseite an: Das Token gehört ausschließlich auf den Minecraft-Server-Rechner in die Bridge-Konfiguration.

## 2. Minecraft Vanilla vorbereiten
1. Öffne `server.properties` und setze `enable-rcon=true`.
2. Setze ein starkes `rcon.password` und `rcon.port=25575`.
3. Starte den Server neu. RCON niemals ins öffentliche Internet freigeben; in der Firewall nur localhost zulassen.
4. Kopiere `datapacks/playertracker` in die Welt unter `world/datapacks/playertracker`.
5. Starte den Server neu oder führe `/reload` aus.
6. Prüfe `/datapack list` und `/scoreboard objectives list`.

**Wichtig:** Die enthaltene Datapack-Grundlage legt einige Statistik-Ziele an. Minecraft-Scoreboard-Kriterien sind versionsabhängig; bei einem Versionswechsel muss die Liste der Block-IDs ggf. angepasst werden. Die Bridge ist bewusst auf eine kleine, wartbare Liste vorbereitet. Für wirklich jeden Blocktyp muss `bridge/config.json` um die passenden Kriterien erweitert werden.

## 3. Bridge installieren
Auf dem Server-Rechner Python 3.10+ installieren. Im Ordner `bridge`:
```bash
python -m pip install -r requirements.txt
```
`config.json` bearbeiten:
- `rcon_host`: `127.0.0.1` lassen, wenn Bridge und Minecraft auf demselben Rechner laufen.
- `rcon_password`: dein RCON-Passwort.
- `github_owner`, `github_repo`, `github_branch`: GitHub-Repository-Daten.
- `github_token`: Fine-grained Personal Access Token mit **Contents: Read and write** nur für dieses Repository. Niemals in die Webseite oder ins öffentliche Repository schreiben.
- `players`: Spielername und deine frei gewählte Server-ID eintragen.
- `block_ids`: Block-IDs ergänzen, die du verfolgen willst.

Dann:
```bash
python bridge.py
```
Die Bridge liest alle konfigurierten Spieler regelmäßig über RCON aus und aktualisiert `data/players.json` im GitHub-Repository. Die Webseite zeigt nach dem nächsten Seitenaufruf die aktualisierten Werte.

## 4. Spieler hinzufügen
In `bridge/config.json`:
```json
{"name":"Steve","serverId":"1001"}
```
Der Name muss exakt dem Minecraft-Spielernamen entsprechen. Die Server-ID ist eine eigene Kennung, keine automatisch von Minecraft vergebene ID.

## Einschränkungen von Vanilla
Minecraft Vanilla hat keine vollständige Spieler-Aktionshistorie und keine eingebaute allgemeine Statistik für jeden gesetzten Block. Die Datapack-/Scoreboard-Statistiken liefern Zähler, keine Liste mit Zeit, Koordinaten oder einzelnen Aktionen. Für vollständige gebaute/abgebaute Block-Historie (inklusive Koordinaten und Zeit) wäre Paper/Spigot mit Logging-Plugin oder ein Mod erforderlich.
