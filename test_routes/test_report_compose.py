import requests

def test_report_compose():
    url = "http://localhost:8000/reports/compose"
    payload = {"sample": "data"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Report composition executed"
    assert data["status"] == "success"

if __name__ == "__main__":
    test_report_compose()
    print("test_report_compose passed.")
