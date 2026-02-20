import requests
import time
import subprocess
import sys

def test_login_page():
    print("Testing /login route...")
    try:
        response = requests.get("http://localhost:5000/login")
        if response.status_code == 200:
            print("✅ /login route accessible")
            if "Sign in" in response.text:
                print("✅ Login page content verified")
            else:
                print("❌ Login page content mismatch")
        else:
            print(f"❌ /login returned {response.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")

if __name__ == "__main__":
    test_login_page()
