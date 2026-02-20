import requests
import sys

def test_quiz_api():
    base_url = "http://localhost:5000"
    
    print("Testing Quiz API...")
    
    try:
        # 1. Test fetch questions
        print("1. Fetching quiz questions...")
        response = requests.get(f"{base_url}/api/quiz/questions")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Successfully fetched {len(data['questions'])} questions")
                # Show first question
                q = data['questions'][0]
                print(f"   First question: {q['question']}")
                print(f"   Category: {q['category']}")
            else:
                print("❌ API returned success=False")
        else:
            print(f"❌ API returned status code {response.status_code}")
            
        # 2. Test submit answer
        print("\n2. Submitting test answer...")
        q_id = data['questions'][0]['id']
        payload = {
            "user_id": 1,
            "question_id": q_id,
            "selected_answer": "B"
        }
        response = requests.post(f"{base_url}/api/quiz/submit", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                result = data['result']
                print(f"✅ Successfully submitted answer. Correct? {result['is_correct']}")
                print(f"   Explanation: {result['explanation'][:50]}...")
            else:
                print("❌ Submit API returned success=False")
        else:
            print(f"❌ Submit API returned status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("   Make sure the Flask app is running (python backend/app.py)")

if __name__ == "__main__":
    test_quiz_api()
