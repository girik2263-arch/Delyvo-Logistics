from pathlib import Path
import re

f = Path("frontend/index.html")
s = f.read_text()

block = re.compile(
    r'<section id="DELYVO_SHIPMENT_MANAGER".*?</section>',
    re.S
)

new = '''<section id="DELYVO_SHIPMENT_MANAGER"
style="margin:25px;padding:20px;background:#fff;border-radius:16px">
<h2>📦 Shipment Management</h2>

<div style="display:flex;gap:10px;flex-wrap:wrap;margin:15px 0">
<button onclick="loadShipments()">Load Shipments</button>
<button onclick="loadShipmentReport()">Report</button>
</div>

<div id="shipmentBox"
style="background:#f7f7f7;padding:15px;border-radius:10px;overflow:auto">
Click Load Shipments
</div>
</section>

<script>
async function loadShipments(){
  const box=document.getElementById("shipmentBox");
  box.textContent="Loading shipments...";

  try{
    const r=await fetch("/api/shipments");
    const data=await r.json();

    if(!Array.isArray(data)){
      box.textContent=JSON.stringify(data,null,2);
      return;
    }

    if(!data.length){
      box.textContent="No shipments found.";
      return;
    }

    box.innerHTML=data.map(s => `
      <div style="padding:12px;margin:8px 0;background:#fff;border-radius:10px">
        <b>${s.awb || s.id || "Shipment"}</b><br>
        Customer: ${s.customer_name || "-"}<br>
        City: ${s.delivery_city || "-"}<br>
        Status: <b>${s.status || "-"}</b>
      </div>
    `).join("");
  }catch(e){
    box.textContent="Unable to load shipments";
  }
}

async function loadShipmentReport(){
  const box=document.getElementById("shipmentBox");
  box.textContent="Loading report...";

  try{
    const r=await fetch("/api/reports/status");
    const data=await r.json();
    box.textContent=JSON.stringify(data,null,2);
  }catch(e){
    box.textContent="Unable to load report";
  }
}
</script>'''

if block.search(s):
    s = block.sub(new, s, count=1)
elif "DELYVO_SHIPMENT_MANAGER" not in s:
    s = s.replace("</body>", new + "\n</body>", 1)
else:
    raise SystemExit("Shipment section state unclear; no change made")

f.write_text(s)

print("OK shipment UI updated")
print("Backup: frontend/index.html.shipments-ui-backup")
