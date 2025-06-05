# 태풍 안전 분석 API 서버

## 시작하기

1. 가상환경 활성화:
```bash
# Windows
.\\venv\\Scripts\\activate

# Linux/Mac
source venv/bin/activate
```

2. 서버 실행:
```bash
cd server
python main.py
```

서버가 시작되면 다음 주소에서 API를 사용할 수 있습니다:
- API 엔드포인트: http://127.0.0.1:8000
- Swagger UI 문서: http://127.0.0.1:8000/docs
- ReDoc 문서: http://127.0.0.1:8000/redoc

## API 엔드포인트

### GET /
- 설명: API 상태 확인
- 응답: `{"status": "ok", "message": "태풍 안전 분석 API가 정상 작동중입니다"}`

### POST /analyze
- 설명: 이미지를 분석하여 태풍시 위험요소를 탐지
- 요청: multipart/form-data
  - file: 이미지 파일 (jpg, jpeg, png, bmp)
- 응답: JSON 형식의 분석 결과

## 사용 예시 (Python)

```python
import requests

# 이미지 파일 업로드 및 분석
with open('image.jpg', 'rb') as f:
    response = requests.post('http://127.0.0.1:8000/analyze', files={'file': f})

# 결과 출력
print(response.json())
```

## 에러 처리

- 400: 잘못된 파일 형식
- 500: 서버 내부 오류 