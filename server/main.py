from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
from pathlib import Path
import tempfile
import os
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from engine.analyzer import TyphoonSafetyAnalyzer
from shared.config import Config

app = FastAPI(
    title="태풍 안전 분석 API",
    description="이미지를 분석하여 태풍시 위험요소를 탐지하는 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 구체적인 origin으로 변경해야 합니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 analyzer 인스턴스 생성
try:
    analyzer = TyphoonSafetyAnalyzer(debug=False)
except Exception as e:
    print(f"Error initializing analyzer: {e}")
    sys.exit(1)

@app.get("/")
async def read_root():
    """API 상태 확인"""
    return {"status": "ok", "message": "태풍 안전 분석 API가 정상 작동중입니다"}

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    이미지를 분석하여 태풍시 위험요소를 탐지합니다.
    
    - **file**: 분석할 이미지 파일 (jpg, jpeg, png, bmp 형식 지원)
    """
    # 파일 형식 검증
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        raise HTTPException(
            status_code=400,
            detail="지원하지 않는 파일 형식입니다. jpg, jpeg, png, bmp 형식만 지원합니다."
        )
    
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # 이미지 분석
        result = analyzer.analyze_image(temp_path)
        
        # 임시 파일 삭제
        os.unlink(temp_path)
        
        return JSONResponse(
            content=result,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    
    except Exception as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 