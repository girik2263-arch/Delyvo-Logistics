from pathlib import Path

f = Path("frontend/index.html")
s = f.read_text()

if "DELYVO_NDR_MANAGER" in s:
    raise SystemExit("NDR UI already exists; no change made")

new = r'''
<section id="DELYVO_NDR_MANAGER"
style="margin:25px;padding:20px;background:#fff;border-radius:16px">

<h2>⚠️ NDR Management</h2>

<div style="display:grid;gap:10px;max-width:650px">

<input id="ndrShipmentId"
placeholder="Shipment UUID"
style="padding:10px">

<input id="ndrReason"
placeholder="NDR reason"
style="padding:10px">

<textarea id="ndrNotes"
placeholder="NDR notes / remarks"
style="padding:10px;min-height:80px"></textarea>

<div style="display:flex;gap:10px;flex-wrap:wrap">
<button onclick="loadNDR()">Load NDR</button>
<button onclick="createNDR()">Create NDR</button>
</div>

<hr>

<select id="ndrAction"
style="padding:10px">
<option value="">Select action</option>
<option value="reattempt">Reattempt Delivery</option>
<option value="rto">RTO</option>
<option value="cancel">Cancel Shipment</option>
</select>

<button onclick="applyNDRAction()">Apply NDR Action</button>

</div>

<pre id="ndrBox"
style="margin-top:15px;background:#f7f7f7;padding:15px;border-radius:10px;overflow:auto">
Enter a shipment UUID
</pre>

</section>

<script>

function ndrShipmentId(){
  return document.getElementById("ndrShipmentId").value.trim();
}

function ndrShow(data){
  document.getElementById("ndrBox").textContent =
    JSON.stringify(data,null,2);
}

async function loadNDR(){

  const id = ndrShipmentId();
  const box = document.getElementById("ndrBox");

  if(!id){
    box.textContent = "Shipment UUID required";
    return;
  }

  box.textContent = "Loading NDR...";

  try{

    const r = await fetch(
      "/api/shipments/"+encodeURIComponent(id)+"/ndr"
    );

    const data = await r.json();

    ndrShow({
      http_status:r.status,
      response:data
    });

  }catch(e){
    box.textContent = "Unable to load NDR";
  }
}

async function createNDR(){

  const id = ndrShipmentId();
  const reason = document.getElementById("ndrReason").value.trim();
  const notes = document.getElementById("ndrNotes").value.trim();
  const box = document.getElementById("ndrBox");

  if(!id){
    box.textContent = "Shipment UUID required";
    return;
  }

  if(!reason){
    box.textContent = "NDR reason required";
    return;
  }

  if(!confirm("Create NDR for this shipment?")){
    return;
  }

  box.textContent = "Creating NDR...";

  try{

    const r = await fetch(
      "/api/shipments/"+encodeURIComponent(id)+"/ndr",
      {
        method:"POST",
        headers:{
          "Content-Type":"application/json"
        },
        body:JSON.stringify({
          reason:reason,
          notes:notes
        })
      }
    );

    const data = await r.json();

    ndrShow({
      http_status:r.status,
      response:data
    });

  }catch(e){
    box.textContent = "Unable to create NDR";
  }
}

async function applyNDRAction(){

  const id = ndrShipmentId();
  const action = document.getElementById("ndrAction").value;
  const box = document.getElementById("ndrBox");

  if(!id){
    box.textContent = "Shipment UUID required";
    return;
  }

  if(!action){
    box.textContent = "Select an NDR action";
    return;
  }

  if(!confirm("Apply NDR action '"+action+"'?")){
    return;
  }

  box.textContent = "Applying NDR action...";

  try{

    const r = await fetch(
      "/api/shipments/"+encodeURIComponent(id)+"/ndr/action",
      {
        method:"POST",
        headers:{
          "Content-Type":"application/json"
        },
        body:JSON.stringify({
          action:action
        })
      }
    );

    const data = await r.json();

    ndrShow({
      http_status:r.status,
      response:data
    });

  }catch(e){
    box.textContent = "Unable to apply NDR action";
  }
}

</script>
'''

s = s.replace("</body>", new + "\n</body>", 1)
f.write_text(s)

print("OK NDR UI added")
print("Backup: frontend/index.html.ndr-ui-backup")
print("DB changes: none")
