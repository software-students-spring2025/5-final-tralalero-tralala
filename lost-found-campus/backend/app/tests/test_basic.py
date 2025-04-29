# backend/tests/test_items.py

import json
from unittest.mock import patch, MagicMock
import pytest
from app.main import app

@pytest.fixture
def client():
    """Fixture to create a test client."""
    app.config["TESTING"] = True
    app.secret_key = "testsecret"
    with app.test_client() as client:
        yield client

@patch('app.main.insert_item')
def test_submit_lost_item_success(mock_insert_item, client):
    """Test successful submission of a lost item."""
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'

    # Mock insert_item to succeed
    mock_insert_item.return_value = None

    data = {
        "name": "Lost Wallet",
        "location": "Library"
    }
    response = client.post(
        "/items/lost",
        data=json.dumps(data),
        content_type="application/json"
    )

    assert response.status_code == 201
    assert b"Lost item added" in response.data
    mock_insert_item.assert_called_once_with(data, "testuser@example.com")


@patch('app.main.insert_item')
def test_submit_lost_item_unauthorized(mock_insert_item, client):
    """Test submission of a lost item without login (unauthorized)."""
    data = {
        "name": "Lost Keys",
        "location": "Cafeteria"
    }
    response = client.post(
        "/items/lost",
        data=json.dumps(data),
        content_type="application/json"
    )

    assert response.status_code == 401
    assert b"Unauthorized" in response.data
    mock_insert_item.assert_not_called()

@patch('app.main.get_all_items')
def test_get_items_success(mock_get_all_items, client):
    """Test getting items successfully with optional status filter."""
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'

    # Mock get_all_items to return fake data
    fake_items = [
        {"name": "Lost Wallet", "location": "Library", "status": "lost"},
        {"name": "Lost Keys", "location": "Gym", "status": "lost"}
    ]
    mock_get_all_items.return_value = fake_items

    response = client.get('/items?status=lost')

    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert isinstance(data, list)
    assert data == fake_items

    mock_get_all_items.assert_called_once_with(status="lost", owner="testuser@example.com")


@patch('app.main.get_all_items')
def test_get_items_unauthorized(mock_get_all_items, client):
    """Test accessing items without being logged in (unauthorized)."""
    response = client.get('/items')

    assert response.status_code == 401
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "Unauthorized"

    mock_get_all_items.assert_not_called()

@patch('app.main.delete_item_by_title')
def test_delete_item_success(mock_delete_item_by_title, client):
    """Test successfully deleting an item."""
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'

    # Mock delete_item_by_title to simulate 1 item deleted
    mock_result = MagicMock()
    mock_result.deleted_count = 1
    mock_delete_item_by_title.return_value = mock_result

    response = client.delete('/items/Lost%20Wallet')  # URL encoding for spaces

    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert "item(s) deleted" in data["message"]

    mock_delete_item_by_title.assert_called_once_with("Lost Wallet", "testuser@example.com")


@patch('app.main.delete_item_by_title')
def test_delete_item_not_found(mock_delete_item_by_title, client):
    """Test deleting an item that does not exist."""
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'

    # Mock delete_item_by_title to simulate 0 items deleted
    mock_result = MagicMock()
    mock_result.deleted_count = 0
    mock_delete_item_by_title.return_value = mock_result

    response = client.delete('/items/NonexistentItem')

    assert response.status_code == 404
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "No matching items found"

    mock_delete_item_by_title.assert_called_once_with("NonexistentItem", "testuser@example.com")

@patch('app.main.delete_item_by_id')
def test_delete_item_by_id_success(mock_delete_item_by_id, client):
    """Test successful deletion by item ID."""
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'

    # Mock delete_item_by_id to simulate successful deletion
    mock_result = MagicMock()
    mock_result.deleted_count = 1
    mock_delete_item_by_id.return_value = mock_result

    response = client.delete('/items/id/12345')

    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert "item(s) deleted" in data["message"]

    mock_delete_item_by_id.assert_called_once_with("12345", "testuser@example.com")


@patch('app.main.delete_item_by_id')
def test_delete_item_by_id_not_found(mock_delete_item_by_id, client):
    """Test deletion by item ID when no matching item is found."""
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'

    # Mock delete_item_by_id to simulate no deletion
    mock_result = MagicMock()
    mock_result.deleted_count = 0
    mock_delete_item_by_id.return_value = mock_result

    response = client.delete('/items/id/nonexistent_id')

    assert response.status_code == 404
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "No matching item found"

    mock_delete_item_by_id.assert_called_once_with("nonexistent_id", "testuser@example.com")


@patch('app.main.delete_item_by_id')
def test_delete_item_by_id_no_result(mock_delete_item_by_id, client):
    """Test deletion by item ID when delete_item_by_id returns None (error)."""
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'

    # Mock delete_item_by_id to return None
    mock_delete_item_by_id.return_value = None

    response = client.delete('/items/id/invalid_id')

    assert response.status_code == 404
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "No matching item found"

    mock_delete_item_by_id.assert_called_once_with("invalid_id", "testuser@example.com")

@patch('app.main.update_item_by_id')
def test_update_item_success(mock_update_item_by_id, client):
    """Test successfully updating an item."""
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'

    mock_update_item_by_id.return_value = 1  # 1 item modified

    data = {
        "name": "Updated Wallet",
        "location": "Updated Library"
    }
    response = client.put('/items/id/12345', json=data)

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()["message"] == "Item updated"

    mock_update_item_by_id.assert_called_once_with("12345", data, "testuser@example.com")


@patch('app.main.update_item_by_id')
def test_update_item_no_item_updated(mock_update_item_by_id, client):
    """Test updating an item but no item matched."""
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'

    mock_update_item_by_id.return_value = 0  # 0 items modified

    data = {
        "name": "Nonexistent Wallet"
    }
    response = client.put('/items/id/12345', json=data)

    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["message"] == "No item updated"

    mock_update_item_by_id.assert_called_once_with("12345", data, "testuser@example.com")


@patch('app.main.update_item_by_id')
def test_update_item_invalid_id(mock_update_item_by_id, client):
    """Test updating an item with an invalid ID."""
    # Simulate logged-in user
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'

    mock_update_item_by_id.return_value = None  # Invalid ID case

    data = {
        "name": "Invalid Item"
    }
    response = client.put('/items/id/invalid_id', json=data)

    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["error"] == "Invalid item ID"

    mock_update_item_by_id.assert_called_once_with("invalid_id", data, "testuser@example.com")

@patch('app.main.create_user')
def test_register_success(mock_create_user, client):
    """Test successful user registration."""
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepassword"
    }

    response = client.post('/register', json=data)

    assert response.status_code == 201
    assert response.is_json
    assert response.get_json()["message"] == "User registered successfully"

    mock_create_user.assert_called_once_with(
        "test@example.com", "testuser", "securepassword"
    )

@patch('app.main.create_user')
def test_register_missing_fields(mock_create_user, client):
    """Test registration failure due to missing fields."""
    # Missing username
    data = {
        "email": "test@example.com",
        "password": "securepassword"
    }

    response = client.post('/register', json=data)

    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["error"] == "Missing fields"

    mock_create_user.assert_not_called()


@patch('app.main.verify_user')
def test_login_success(mock_verify_user, client):
    """Test successful user login."""
    # Mock verify_user to return True (valid credentials)
    mock_verify_user.return_value = True

    data = {
        "email": "test@example.com",
        "password": "securepassword"
    }

    response = client.post('/login', json=data)

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()["message"] == "Login successful"

    mock_verify_user.assert_called_once_with(
        "test@example.com", "securepassword"
    )

    # Check if session is correctly set
    with client.session_transaction() as sess:
        assert sess["user"] == "test@example.com"

@patch('app.main.verify_user')
def test_login_invalid_credentials(mock_verify_user, client):
    """Test failed user login due to invalid credentials."""
    # Mock verify_user to return False (invalid credentials)
    mock_verify_user.return_value = False

    data = {
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }

    response = client.post('/login', json=data)

    assert response.status_code == 401
    assert response.is_json
    assert response.get_json()["error"] == "Invalid credentials"

    mock_verify_user.assert_called_once_with(
        "wrong@example.com", "wrongpassword"
    )

    # Check that session is NOT set
    with client.session_transaction() as sess:
        assert "user" not in sess

def test_logout(client):
    """Test successful logout clears session."""
    # Set up a fake logged-in user
    with client.session_transaction() as sess:
        sess["user"] = "testuser@example.com"

    response = client.post('/logout')

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()["message"] == "Logout successful"

    # Check that session is cleared
    with client.session_transaction() as sess:
        assert "user" not in sess

"""
The following tests apply to functions not used in production.
Therefore, for coverage, tests assert true. (Even without these the coverage)
"""
def test_me_logged_in(client):
    """Test /me when user is logged in."""
    with client.session_transaction() as sess:
        sess["user"] = "testuser@example.com"

    response = client.get('/me')

    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    
    assert "session" in data
    assert data["session"].get("user") == "testuser@example.com"

def test_me_not_logged_in(client):
    """Test /me when no user is logged in."""
    # No session setup

    response = client.get('/me')

    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()

    assert "session" in data
    assert data["session"] == {}  # session should be empty