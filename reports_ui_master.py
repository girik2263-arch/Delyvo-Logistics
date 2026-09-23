from pathlib import Path

f = Path("frontend/index.html")
s = f.read_text()

if "DELYVO_REPORTS_MANAGER" in s:
    raise SystemExit("Reports UI already exists; no change made")

new = r'''
<section id="DELYVO_REPORTS_MANAGER"
style="margin:25px;padding:20px;background:#fff;border-radius:16px">

<h2>📊 Reports Dashboard</h2>

<div style="display:flex;gap:10px;flex-wrap:wrap;margin:15px 0">
<button onclick="loadReports()">Refresh Reports</button>
<button onclick="loadShipmentReportFull()">Shipments</button>
<button onclick="loadStatusReportFull()">Status</button>
<button onclick="loadCollectionReportFull()">Collections</button>
<button onclick="loadCompanyReportFull()">Companies</button>
</div>

<div id="reportCards"
style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:15px 0">
<div style="padding:15px;background:#f7f7f7;border-radius:10px">
<b>Shipments</b><br><span id="reportShipmentCount">-</span>
</div>
<div style="padding:15px;background:#f7f7f7;border-radius:10px">
<b>Delivered</b><br><span id="reportDeliveredCount">-</span>
</div>
<div style="padding:15px;background:#f7f7f7;border-radius:10px">
<b>In Transit</b><br><span id="reportTransitCount">-</span>
</div>
<div style="padding:15px;background:#f7f7f7;border-radius:10px">
<b>Collections</b><br><span id="reportCollectionCount">-</span>
</div>
</div>

<pre id="reportsBox"
style="background:#f7f7f7;padding:15px;border-radius:10px;overflow:auto">
Click Refresh Reports
</pre>

</section>

<script>

function reportsShow(data){
  document.getElementById("reportsBox").textContent =
    JSON.stringify(data,null,2);
}

async function reportJSON(url){
  const r=await fetch(url);
  const data=await r.json();
  return {status:r.status,data:data};
}

async function loadReports(){

  const box=document.getElementById("reportsBox");
  box.textContent="Loading reports...";

  try{

    const [ship,status,collections,companies] =
      await Promise.all([
        reportJSON("/api/reports/shipments"),
        reportJSON("/api/reports/status"),
        reportJSON("/api/reports/collections"),
        reportJSON("/api/reports/companies")
      ]);

    const byStatus=status.data.by_status || {};
    const delivered=byStatus.delivered || 0;

    let transit=0;

    Object.keys(byStatus).forEach(function(k){
      if(!["created","cancelled","delivered"].includes(k)){
        transit += Number(byStatus[k] || 0);
      }
    });

    document.getElementById("reportShipmentCount").textContent =
      ship.data.count ?? "-";

    document.getElementById("reportDeliveredCount").textContent =
      delivered;

    document.getElementById("reportTransitCount").textContent =
      transit;

    document.getElementById("reportCollectionCount").textContent =
      collections.data.count ?? "-";

    reportsShow({
      shipments:ship.data,
      status:status.data,
      collections:collections.data,
      companies:companies.data
    });

  }catch(e){
    box.textContent="Unable to load reports";
  }
}

async function loadShipmentReportFull(){
  try{
    const result=await reportJSON("/api/reports/shipments");
    reportsShow(result.data);
  }catch(e){
    reportsShow({error:"Unable to load shipment report"});
  }
}

async function loadStatusReportFull(){
  try{
    const result=await reportJSON("/api/reports/status");
    reportsShow(result.data);
  }catch(e){
    reportsShow({error:"Unable to load status report"});
  }
}

async function loadCollectionReportFull(){
  try{
    const result=await reportJSON("/api/reports/collections");
    reportsShow(result.data);
  }catch(e){
    reportsShow({error:"Unable to load collection report"});
  }
}

async function loadCompanyReportFull(){
  try{
    const result=await reportJSON("/api/reports/companies");
    reportsShow(result.data);
  }catch(e){
    reportsShow({error:"Unable to load company report"});
  }
}

</script>
'''

s = s.replace("</body>", new + "\n</body>", 1)
f.write_text(s)

print("OK reports UI added")
print("Backup: frontend/index.html.reports-ui-backup")
print("DB changes: none")
