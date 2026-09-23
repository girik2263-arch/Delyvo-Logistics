from pathlib import Path
import shutil, re, py_compile

# ---------- BACKEND ----------
f = Path("app/routes/lifecycle.py")
b = Path("app/routes/lifecycle.py.dispatched-backup")

if not b.exists():
    shutil.copy2(f, b)

t = f.read_text()
t2 = re.sub(r',\s*"dispatched"', '', t)

if t2 == t:
    print("BACKEND: dispatched already absent")
else:
    f.write_text(t2)
    print("BACKEND: dispatched removed")

py_compile.compile(str(f), doraise=True)
print("BACKEND SYNTAX: OK")

# ---------- FRONTEND ----------
html = Path("../frontend/index.html")
hb = Path("../frontend/index.html.dispatched-backup")

if not hb.exists():
    shutil.copy2(html, hb)

h = html.read_text()

# Remove exact option from shipment status dropdown.
h2 = re.sub(
    r'<option[^>]*value=["\']dispatched["\'][^>]*>.*?</option>',
    '',
    h,
    flags=re.I | re.S
)

if h2 == h:
    print("FRONTEND: dispatched option already absent")
else:
    html.write_text(h2)
    print("FRONTEND: dispatched option removed")

# ---------- VERIFICATION ----------
print("BACKEND dispatched:", '"dispatched"' in f.read_text())
print("FRONTEND dispatched option:",
      bool(re.search(r'<option[^>]*value=["\']dispatched["\']', html.read_text(), re.I)))

if '"dispatched"' in f.read_text():
    raise SystemExit("FAIL: backend still contains dispatched")

if re.search(r'<option[^>]*value=["\']dispatched["\']', html.read_text(), re.I):
    raise SystemExit("FAIL: frontend still contains dispatched option")

print("===== LIFECYCLE ALIGNMENT COMPLETE =====")
