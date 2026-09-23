from pathlib import Path

f = Path("frontend/index.html")
s = f.read_text()

if "DELYVO_SHIPMENT_DETAILS" in s:
    raise SystemExit("Shipment details UI already exists; no change made")

new = r'''
<section id="DELYVO_SHIPMENT_DETAILS"
style="margin:25px;padding:20px;background:#fff;border-radius:16px">
<h2>🔎 Shipment Details</h2>

<div style="display:flex;gap:10px;flex-wrap:wrap;margin:15px 0">
<input id="shipmentIdInput"
placeholder="Enter shipment UUID"
style="padding:10px;flex:1;min-width:220px">
<button onclick="loadShipmentDetails()">Details</button>
<button onclick="loadShipmentTracking()">Tracking</button>
</div>

<div id="shipmentDetailsBox"
style="background:#f7f7f7;padding:15px;border-radius:10px;overflow:auto">
Enter a shipment UUID
</div>
</section>

<script>
async function shipmentRequest(url, options={}){
  const r=await fetch(url, options);
  const data=await r.json();
  return {status:r.status,data:data};
}

function shipmentId(){
  return document.getElementById("shipmentIdInput").value.trim();
}

function showShipmentData(data){
  document.getElementById("shipmentDetailsBox").textContent =
    JSON.stringify(data,null,2);
}

async function loadShipmentDetails(){
  const id=shipmentId();
  const box=document.getElementById("shipmentDetailsBox");

  if(!id){
    box.textContent="Shipment UUID required";
    return;
  }

  box.textContent="Loading shipment...";

  try{
    const result=await shipmentRequest("/api/shipments/"+encodeURIComponent(id));
    showShipmentData(result.data);
  }catch(e){
    box.textContent="Unable to load shipment";
  }
}

async function loadShipmentTracking(){
  const id=shipmentId();
  const box=document.getElementById("shipmentDetailsBox");

  if(!id){
    box.textContent="Shipment UUID required";
    return;
  }

  box.textContent="Loading tracking...";

  try{
    const result=await shipmentRequest(
      "/api/shipments/"+encodeURIComponent(id)+"/tracking"
    );
    showShipmentData(result.data);
  }catch(e){
    box.textContent="Unable to load tracking";
  }
}
</script>
'''

s = s.replace("</body>", new + "\n</body>", 1)
f.write_text(s)

print("OK shipment details UI added")
print("Backup: frontend/index.html.shipment-details-backup")
print("DB changes: none")
