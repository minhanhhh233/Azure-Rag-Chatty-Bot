from fastapi.testclient import TestClient
from app import app
import time

client = TestClient(app)

def test_list_files():
    # Test
    response = client.get('/list_files')
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'files' in data
    assert isinstance(data['files'], list)
    assert "index.json" not in response.json()["files"]

def test_upload():
    with open("test_file.pdf", "rb") as file:
        response = client.post("/upload", files={"uploaded_file": ("test_file.pdf", file)})

    time.sleep(50)
    # Check the response
    assert response.status_code == 200
    assert response.json() == {"message": "File uploaded successfully"}

    # Check that the uploaded file is listed
    response = client.get("/list_files")
    
    assert response.status_code == 200
    assert "test_file.pdf" in response.json()["files"]

def test_delete_file():
    # Delete the file
    response = client.delete("/delete_file/test_file.pdf")
    
    time.sleep(50)
    # Check the response
    assert response.status_code == 200
    assert response.json() == {"message": "test_file.pdf has been deleted."}

    # Check that the deleted file is no longer listed
    response = client.get("/list_files")
    assert response.status_code == 200
    assert "test_file.pdf" not in response.json()["files"]