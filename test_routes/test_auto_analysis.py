import requests

def test_auto_analysis():
    url = "http://localhost:8000/ml/auto"
    payload = {"sample": "data"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Auto analysis executed"
    assert data["status"] == "success"

if __name__ == "__main__":
    test_auto_analysis()
    print("test_auto_analysis passed.")
