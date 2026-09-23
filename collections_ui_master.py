from pathlib import Path

f = Path("frontend/index.html")
s = f.read_text()

if "DELYVO_COLLECTIONS_MANAGER" in s:
    raise SystemExit("Collections UI already exists; no change made")

new = r'''
<section id="DELYVO_COLLECTIONS_MANAGER"
style="margin:25px;padding:20px;background:#fff;border-radius:16px">

<h2>💰 COD Collections</h2>

<div style="display:grid;gap:10px;max-width:700px">

<input id="collectionShipmentId"
placeholder="Shipment ID"
style="padding:10px">

<input id="collectionAmount"
type="number"
step="0.01"
placeholder="Collection amount"
style="padding:10px">

<select id="collectionStatus" style="padding:10px">
<option value="pending">Pending</option>
<option value="collected">Collected</option>
<option value="remitted">Remitted</option>
<option value="failed">Failed</option>
<option value="cancelled">Cancelled</option>
</select>

<select id="collectionPaymentMethod" style="padding:10px">
<option value="">Payment method</option>
<option value="cash">Cash</option>
<option value="upi">UPI</option>
<option value="bank_transfer">Bank Transfer</option>
<option value="card">Card</option>
</select>

<input id="collectionTransactionRef"
placeholder="Transaction reference (optional)"
style="padding:10px">

<textarea id="collectionNotes"
placeholder="Notes"
style="padding:10px;min-height:80px"></textarea>

<div style="display:flex;gap:10px;flex-wrap:wrap">
<button onclick="loadCollections()">Load Collections</button>
<button onclick="createCollection()">Create Collection</button>
</div>

<hr>

<input id="updateCollectionId"
placeholder="Collection ID for update"
style="padding:10px">

<button onclick="updateCollection()">Update Collection</button>

<hr>

<button onclick="loadFinanceSummary()">Finance Summary</button>

</div>

<pre id="collectionsBox"
style="margin-top:15px;background:#f7f7f7;padding:15px;border-radius:10px;overflow:auto">
Select an action
</pre>

</section>

<script>

function collectionBox(data){
  document.getElementById("collectionsBox").textContent =
    JSON.stringify(data,null,2);
}

async function loadCollections(){

  const box = document.getElementById("collectionsBox");
  box.textContent = "Loading collections...";

  try{

    const r = await fetch("/api/collections");
    const data = await r.json();

    collectionBox({
      http_status:r.status,
      response:data
    });

  }catch(e){
    box.textContent = "Unable to load collections";
  }
}

async function createCollection(){

  const shipmentId =
    document.getElementById("collectionShipmentId").value.trim();

  const amount =
    document.getElementById("collectionAmount").value;

  const status =
    document.getElementById("collectionStatus").value;

  const paymentMethod =
    document.getElementById("collectionPaymentMethod").value;

  const transactionRef =
    document.getElementById("collectionTransactionRef").value.trim();

  const notes =
    document.getElementById("collectionNotes").value.trim();

  const box = document.getElementById("collectionsBox");

  if(!shipmentId){
    box.textContent = "Shipment ID required";
    return;
  }

  if(!amount || Number(amount) <= 0){
    box.textContent = "Valid collection amount required";
    return;
  }

  if(!confirm("Create this COD collection?")){
    return;
  }

  box.textContent = "Creating collection...";

  try{

    const r = await fetch("/api/collections",{
      method:"POST",
      headers:{
        "Content-Type":"application/json"
      },
      body:JSON.stringify({
        shipment_id:shipmentId,
        amount:Number(amount),
        status:status,
        payment_method:paymentMethod || null,
        transaction_ref:transactionRef || null,
        notes:notes || null
      })
    });

    const data = await r.json();

    collectionBox({
      http_status:r.status,
      response:data
    });

  }catch(e){
    box.textContent = "Unable to create collection";
  }
}

async function updateCollection(){

  const id =
    document.getElementById("updateCollectionId").value.trim();

  const status =
    document.getElementById("collectionStatus").value;

  const paymentMethod =
    document.getElementById("collectionPaymentMethod").value;

  const transactionRef =
    document.getElementById("collectionTransactionRef").value.trim();

  const notes =
    document.getElementById("collectionNotes").value.trim();

  const amount =
    document.getElementById("collectionAmount").value;

  const box = document.getElementById("collectionsBox");

  if(!id){
    box.textContent = "Collection ID required";
    return;
  }

  if(!confirm("Update this collection?")){
    return;
  }

  box.textContent = "Updating collection...";

  const payload = {
    status:status,
    payment_method:paymentMethod || null,
    transaction_ref:transactionRef || null,
    notes:notes || null
  };

  if(amount !== ""){
    payload.amount = Number(amount);
  }

  try{

    const r = await fetch(
      "/api/collections/"+encodeURIComponent(id),
      {
        method:"PATCH",
        headers:{
          "Content-Type":"application/json"
        },
        body:JSON.stringify(payload)
      }
    );

    const data = await r.json();

    collectionBox({
      http_status:r.status,
      response:data
    });

  }catch(e){
    box.textContent = "Unable to update collection";
  }
}

async function loadFinanceSummary(){

  const box = document.getElementById("collectionsBox");
  box.textContent = "Loading finance summary...";

  try{

    const r = await fetch("/api/finance/summary");
    const data = await r.json();

    collectionBox({
      http_status:r.status,
      response:data
    });

  }catch(e){
    box.textContent = "Unable to load finance summary";
  }
}

</script>
'''

s = s.replace("</body>", new + "\n</body>", 1)
f.write_text(s)

print("OK COD collections UI added")
print("Backup: frontend/index.html.collections-ui-backup")
print("DB changes: none")
