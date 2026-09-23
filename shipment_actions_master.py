from pathlib import Path

f = Path("frontend/index.html")
s = f.read_text()

if "DELYVO_SHIPMENT_ACTIONS" in s:
    raise SystemExit("Shipment actions UI already exists; no change made")

new = r'''
<section id="DELYVO_SHIPMENT_ACTIONS"
style="margin:25px;padding:20px;background:#fff;border-radius:16px">
<h2>⚙️ Shipment Actions</h2>

<div style="display:grid;gap:10px;max-width:600px">
<input id="actionShipmentId"
placeholder="Shipment UUID"
style="padding:10px">

<select id="shipmentStatus"
style="padding:10px">
<option value="">Select status</option>
<option value="created">Created</option>
<option value="pickup_requested">Pickup Requested</option>
<option value="picked_up">Picked Up</option>
<option value="at_hub">At Hub</option>
<option value="dispatched">Dispatched</option>
<option value="out_for_delivery">Out For Delivery</option>
<option value="delivered">Delivered</option>
<option value="cancelled">Cancelled</option>
<option value="ndr">NDR</option>
<option value="rto">RTO</option>
</select>

<button onclick="updateShipmentStatus()">Update Status</button>

<hr>

<input id="actionPilotId"
placeholder="Pilot UUID"
style="padding:10px">

<button onclick="assignShipmentPilot()">Assign Pilot</button>
</div>

<pre id="shipmentActionBox"
style="margin-top:15px;background:#f7f7f7;padding:15px;border-radius:10px;overflow:auto">
Select an action
</pre>
</section>

<script>
function actionShipmentId(){
  return document.getElementById("actionShipmentId").value.trim();
}

function actionBox(data){
  document.getElementById("shipmentActionBox").textContent =
    JSON.stringify(data,null,2);
}

async function updateShipmentStatus(){
  const id=actionShipmentId();
  const status=document.getElementById("shipmentStatus").value;
  const box=document.getElementById("shipmentActionBox");

  if(!id){
    box.textContent="Shipment UUID required";
    return;
  }

  if(!status){
    box.textContent="Select a status";
    return;
  }

  if(!confirm("Update shipment status to '"+status+"'?")){
    return;
  }

  box.textContent="Updating status...";

  try{
    const r=await fetch(
      "/api/shipments/"+encodeURIComponent(id)+"/status",
      {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({status:status})
      }
    );

    const data=await r.json();
    actionBox({http_status:r.status,response:data});
  }catch(e){
    box.textContent="Unable to update shipment status";
  }
}

async function assignShipmentPilot(){
  const id=actionShipmentId();
  const pilot=document.getElementById("actionPilotId").value.trim();
  const box=document.getElementById("shipmentActionBox");

  if(!id){
    box.textContent="Shipment UUID required";
    return;
  }

  if(!pilot){
    box.textContent="Pilot UUID required";
    return;
  }

  if(!confirm("Assign this pilot to the shipment?")){
    return;
  }

  box.textContent="Assigning pilot...";

  try{
    const r=await fetch(
      "/api/shipments/"+encodeURIComponent(id)+"/assign-pilot",
      {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({pilot_id:pilot})
      }
    );

    const data=await r.json();
    actionBox({http_status:r.status,response:data});
  }catch(e){
    box.textContent="Unable to assign pilot";
  }
}
</script>
'''

s = s.replace("</body>", new + "\n</body>", 1)
f.write_text(s)

print("OK shipment actions UI added")
print("Backup: frontend/index.html.shipment-actions-backup")
print("DB changes: none")
