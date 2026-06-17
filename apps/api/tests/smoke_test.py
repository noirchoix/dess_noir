import requests
BASE = 'http://localhost:8000'
for path in ['/api/v1/dess/health', '/api/v1/dess/summary', '/api/v1/dess/metrics', '/api/v1/dess/predictions?limit=3', '/api/v1/dess/reactants', '/api/v1/dess/products', '/api/v1/dess/ranks']:
    r = requests.get(BASE + path, timeout=20)
    print(path, r.status_code)
    r.raise_for_status()
r = requests.post(BASE + '/api/v1/dess/score', json={'reactants': ['CC(=O)O'], 'candidates': ['CC(=O)Oc1ccc(CC=C)cc1OC']}, timeout=20)
print('/api/v1/dess/score', r.status_code)
r.raise_for_status()
print('DESS smoke test passed')
