import requests

def test_strategy_scan():
    url = "http://localhost:8000/strategy/scan"
    payload = {"sample": "data"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Strategy scan executed"
    assert data["status"] == "success"

if __name__ == "__main__":
    test_strategy_scan()
    print("test_strategy_scan passed.")
