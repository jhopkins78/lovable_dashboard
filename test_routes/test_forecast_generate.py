import requests

def test_forecast_generate():
    url = "http://localhost:8000/forecast/generate"
    payload = {"sample": "data"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Forecast generation executed"
    assert data["status"] == "success"

if __name__ == "__main__":
    test_forecast_generate()
    print("test_forecast_generate passed.")
