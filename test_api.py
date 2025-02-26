import requests

# API 엔드포인트 URL
URL = "http://127.0.0.1:8000/generate_til"

# 테스트 데이터 (정상 요청)
valid_data = {
    "user_notes": "FastAPI와 LangChain을 사용하여 API를 만들었다."
}

# 테스트 1: 정상 요청
def test_generate_til():
    response = requests.post(URL, json=valid_data)
    print("\n 테스트 1: 정상 요청")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

    response_json = response.json()
    print("\n✅ 테스트 1: 정상 요청 통과")
    print("📌 응답 데이터:", response_json)

# 테스트 2: 빈 요청 데이터 (에러 발생 예상)
def test_generate_til_empty():
    response = requests.post(URL, json={})
    print("\n 테스트 2: 빈 요청 데이터")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

# 테스트 3: 잘못된 데이터 타입 (숫자를 보낼 경우)
invalid_data = {
    "user_notes": 12345
}

def test_generate_til_invalid():
    response = requests.post(URL, json=invalid_data)
    print("\n테스트 3: 잘못된 데이터 타입")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

# 모든 테스트 실행
if __name__ == "__main__":
    test_generate_til()
    #test_generate_til_empty()
    #test_generate_til_invalid()
