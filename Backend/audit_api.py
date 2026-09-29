import json
import os
import re
from pathlib import Path
from app.main import app

schema = app.openapi()
paths = schema.get("paths", {})

# Read all integration & security test files content
tests_dir = Path("tests")
test_files = list(tests_dir.rglob("*.py"))
test_contents = {}
for tf in test_files:
    try:
        test_contents[str(tf)] = tf.read_text(encoding="utf-8")
    except Exception:
        pass

endpoint_records = []

for path, path_item in sorted(paths.items()):
    for method, op in sorted(path_item.items()):
        if method.lower() not in ("get", "post", "put", "patch", "delete"):
            continue
        
        m_upper = method.upper()
        summary = op.get("summary") or op.get("operationId") or ""
        tags = op.get("tags") or ["General"]
        tag = tags[0]
        
        # Check security
        security = op.get("security", [])
        has_auth = bool(security or (schema.get("security") and security is not None))
        
        # Parameters & body
        params = op.get("parameters", [])
        req_body = op.get("requestBody")
        req_schema = None
        if req_body:
            content = req_body.get("content", {})
            for ctype, cdata in content.items():
                req_schema = cdata.get("schema", {}).get("$ref", ctype)
                break
                
        # Responses
        responses = list(op.get("responses", {}).keys())
        
        # Check if tested in any test file
        # Convert path to regex, e.g. /api/v1/certificates/{id} -> /api/v1/certificates/
        path_pattern = re.sub(r'\{[^}]+\}', r'[^/"\'\\s]+', path)
        matching_tests = []
        for tf_path, content in test_contents.items():
            if re.search(path_pattern, content):
                matching_tests.append(os.path.basename(tf_path))
            elif summary and summary in content:
                matching_tests.append(os.path.basename(tf_path))
                
        matching_tests = sorted(list(set(matching_tests)))
        
        endpoint_records.append({
            "method": m_upper,
            "path": path,
            "tag": tag,
            "summary": summary,
            "auth": "Bearer JWT/Key" if has_auth else "Public",
            "request_body": req_schema or ("Params" if params else "None"),
            "responses": responses,
            "tested": len(matching_tests) > 0,
            "test_files": matching_tests
        })

print(f"Total endpoints analyzed: {len(endpoint_records)}")
tested_count = sum(1 for e in endpoint_records if e["tested"])
untested_count = len(endpoint_records) - tested_count
print(f"Directly referenced in tests: {tested_count}")
print(f"Not explicitly matched: {untested_count}")

# Save JSON report
with open("endpoint_inventory.json", "w", encoding="utf-8") as f:
    json.dump(endpoint_records, f, indent=2)

print("Saved endpoint_inventory.json")
