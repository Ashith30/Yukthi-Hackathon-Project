import json
from app import app

# Create a test client
with app.test_client() as client:
    # Set up a session first
    with client.session_transaction() as sess:
        sess['user'] = {
            'id': 'test-uuid',
            'email': 'test@example.com',
            'name': 'Test User'
        }
        
    response = client.post('/assessment/submit', json={
        "answers": [
            {"question": "Q1", "answer": "Opt1"}
        ]
    })
    
    print(response.status_code)
    print(response.get_json())
