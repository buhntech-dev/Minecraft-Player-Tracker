import base64, json, os, time
from pathlib import Path
import requests

BASE=Path(__file__).resolve().parent
cfg=json.loads((BASE/"config.json").read_text(encoding="utf-8"))
class Rcon:
    def __init__(self):
        try: from mcrcon import MCRcon
        except ImportError: raise SystemExit("Bitte installieren: pip install mcrcon")
        self.client=MCRcon(cfg["rcon_host"],cfg["rcon_password"],port=int(cfg["rcon_port"]))
    def __enter__(self): self.client.connect(); return self
    def __exit__(self,*args): self.client.disconnect()
    def cmd(self,s):
        try:return self.client.command(s).strip()
        except Exception:return ""
def score(rcon, player, objective):
    out=rcon.cmd(f"scoreboard players get {player} {objective}")
    # RCON antwortet z.B. 'Steve has 12 [deaths]'
    import re
    m=re.search(r"has (-?\\d+)",out)
    return int(m.group(1)) if m else 0
def publish(payload):
    owner,repo,branch=cfg["github_owner"],cfg["github_repo"],cfg["github_branch"]
    path="data/players.json"; url=f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers={"Authorization":f"Bearer {cfg['github_token']}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}
    old=requests.get(url,headers=headers,params={"ref":branch},timeout=20)
    body={"message":"Update Minecraft player statistics","content":base64.b64encode(json.dumps(payload,ensure_ascii=False,indent=2).encode()).decode(),"branch":branch}
    if old.status_code==200: body["sha"]=old.json()["sha"]
    elif old.status_code not in (404,): old.raise_for_status()
    res=requests.put(url,headers=headers,json=body,timeout=30);res.raise_for_status()
def main():
    blocks=cfg.get("block_ids",[])
    while True:
        records=[]
        with Rcon() as r:
            online=r.cmd("list")
            for p in cfg["players"]:
                name=p["name"]
                # Objective names must match datapack setup.
                mined={b:score(r,name,"mined_"+b) for b in blocks}
                records.append({"name":name,"serverId":str(p["serverId"]),"uuid":None,
                    "online":name.lower() in online.lower(),"deaths":score(r,name,"deaths"),
                    "playTimeTicks":score(r,name,"play_time"),"mobKills":score(r,name,"mob_kills"),
                    "playerKills":score(r,name,"player_kills"),"walkOneCm":score(r,name,"walk_cm"),
                    "jumps":score(r,name,"jumps"),"mined":mined,"placed":{}})
        publish({"updatedAt":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"players":records})
        print("Statistiken veröffentlicht:",time.strftime("%H:%M:%S"))
        time.sleep(max(60,int(cfg.get("poll_seconds",300))))
if __name__=="__main__":
    try: main()
    except KeyboardInterrupt: print("Bridge beendet.")
