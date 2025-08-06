#!/usr/bin/env python3
"""
FastAPI 서버 실행 스크립트
"""
import os
import sys
from pathlib import Path

# 현재 스크립트가 있는 venv 폴더의 site-packages 경로를 찾아서 sys.path에 추가합니다.
# 이렇게 하면 Uvicorn의 자식 프로세스도 패키지를 확실하게 찾을 수 있습니다.
venv_path = Path(sys.executable).parent.parent
site_packages = venv_path / "Lib" / "site-packages"

import uvicorn
from dotenv import load_dotenv

def main():
    """서버 실행"""
    # .env 파일 로드
    load_dotenv()
    
    # 환경변수 체크
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("📝 .env 파일을 생성하고 API 키를 설정해주세요.")
        print("   예: GEMINI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # 서버 설정
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"🚀 Harbor Agent API 서버 시작")
    print(f"📍 주소: http://{host}:{port}")
    print(f"📚 API 문서: http://{host}:{port}/docs")
    print(f"🔍 헬스체크: http://{host}:{port}/health")
    print("=" * 50)
    
    # 서버 실행
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=False,
            log_level=log_level
        )
    except KeyboardInterrupt:
        print("\n👋 서버를 종료합니다.")
    except Exception as e:
        print(f"❌ 서버 실행 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()