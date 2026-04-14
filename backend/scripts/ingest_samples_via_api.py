import os, glob, requests
API = os.environ.get("API_BASE", "http://127.0.0.1:8000")
def main():
  files = []
  for p in glob.glob("data/sample_docs/*"):
    files.append(('files', (os.path.basename(p), open(p, 'rb'), 'application/octet-stream')))
  if not files: print("No sample files found."); return
  r = requests.post(f"{API}/ingest", files=files)
  print(r.status_code, r.text)
if __name__ == "__main__": main()
