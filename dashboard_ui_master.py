from pathlib import Path
import shutil,re

f=Path("frontend/index.html")
shutil.copy2(f,"frontend/index.html.ui-backup")

s=f.read_text()

old=re.compile(
r'<section id="DELYVO_CONTROL_CENTER".*?</section><script>async function dc\(x\).*?</script>',
re.S
)

new='''<section id="DELYVO_CONTROL_CENTER" style="margin:25px;padding:20px;background:#fff;border-radius:16px">
<h2>🚚 Delyvo Control Center</h2>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin:15px 0">
<button onclick="dc("companies")">Companies</button>
<button onclick="dc("shipments")">Shipments</button>
<button onclick="dc("hubs")">Hubs</button>
<button onclick="dc("pilots")">Pilots</button>
<button onclick="dc("finance")">Finance</button>
<button onclick="dc("reports")">Reports</button>
</div>
<pre id="dcbox" style="background:#f7f7f7;padding:15px;border-radius:10px;overflow:auto">Select a section</pre>
</section>
<script>
async function dc(x){
  const box=document.getElementById("dcbox");
  box.textContent="Loading...";
  try{
    let url="/api/control/"+x;
    if(x==="finance") url="/api/finance/summary";
    if(x==="reports") url="/api/reports/status";
    const r=await fetch(url);
    const data=await r.json();
    box.textContent=JSON.stringify(data,null,2);
  }catch(e){
    box.textContent="Unable to load data";
  }
}
</script>'''

if old.search(s):
    s=old.sub(new,s,count=1)
else:
    raise SystemExit("Existing Control Center block not found; no change made")

f.write_text(s)

print("OK dashboard UI updated")
print("Backup: frontend/index.html.ui-backup")
print("Real APIs: control + finance + reports")
