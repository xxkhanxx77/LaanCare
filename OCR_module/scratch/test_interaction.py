import httpx
import json
import sys

# Ensure UTF-8 output for terminal
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8100"
HEADERS = {"X-API-Key": "medguard-secret-key"}

def test_interaction():
    print("\nChecking interaction for Aspirin...")
    # Using a 30s timeout
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(
                f"{BASE_URL}/api/check_interaction",
                headers=HEADERS,
                params={"name": "Aspirin"}
            )
            print(r.status_code)
            data = r.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_interaction()
