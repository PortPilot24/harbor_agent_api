# Harbor Agent API ⚓

## 프로젝트 소개

**Harbor Agent API**는 대한민국 항만 관련 법규, 업무 매뉴얼, 안전 규정 등에 대한 질문에 답변하는 전문 AI 에이전트입니다. Google의 Gemini 모델을 기반으로 RAG(Retrieval-Augmented Generation) 기술을 활용하여, 복잡하고 방대한 항만 관련 문서에서 정확한 정보를 찾아내 사용자에게 명확한 답변을 제공합니다.

본 프로젝트는 FastAPI를 사용하여 구축되었으며, 벡터 데이터베이스로는 ChromaDB를 활용하여 관련 문서를 효율적으로 검색합니다.

-----

## ✨ 주요 기능

  * **🤖 지능형 AI 에이전트**: Gemini API를 활용하여 사용자의 질문 의도를 파악하고 자연어 답변을 생성합니다.
  * **📚 RAG (검색 증강 생성)**: ChromaDB 벡터 저장소에 저장된 항만 법률 및 업무 매뉴얼을 검색하여, AI의 답변을 실제 데이터 기반으로 보강합니다.
  * **🛠️ 다중 도구(Multi-Tool) 사용**: `법률 검색`과 `매뉴얼 검색` 등 여러 도구를 복합적으로 사용하여 복잡한 질문에 대한 해결책을 찾습니다.
  * **🔄 다중 단계 추론**: 한 번의 검색으로 답변이 불충분할 경우, 추가적인 도구 호출을 통해 정보를 보강하고 최종 답변을 생성하는 과정을 거칩니다.
  * **⚡️ 비동기 API 서버**: FastAPI를 기반으로 구축되어 빠르고 효율적인 비동기 처리를 지원합니다.
  * **📄 자동 API 문서**: Swagger UI와 ReDoc을 통해 API 문서를 자동으로 생성하여 손쉬운 테스트와 확인이 가능합니다.

-----

## ⚙️ 시스템 아키텍처

Harbor Agent는 다음과 같은 흐름으로 사용자의 요청을 처리합니다.

1.  **사용자 요청 (Query)**: 사용자가 항만 관련 질문을 API 서버(`POST /query`)에 전송합니다.
2.  **Agent 처리 시작**: `HarborAgent`가 요청을 받아 대화 내역과 시스템 프롬프트를 구성합니다.
3.  **도구 사용 결정 (Gemini)**: `HarborAgent`는 Gemini 모델에게 현재 질문과 사용 가능한 도구 목록(법률 검색, 매뉴얼 검색)을 전달하며 어떤 도구를 사용해야 할지 판단을 요청합니다.
4.  **정보 검색 (ChromaDB)**: Gemini 모델의 판단에 따라 `HarborAgent`는 `ChromaDBManager`를 통해 필요한 도구(예: `search_legal_documents`)를 실행합니다. 이 과정에서 ChromaDB에 저장된 벡터화된 문서에서 질문과 가장 관련성 높은 내용을 검색합니다.
5.  **결과 종합 및 답변 생성 (Gemini)**: 검색된 정보를 다시 Gemini 모델에게 전달하여, 이를 바탕으로 사용자에게 제공할 최종 답변을 생성하도록 요청합니다.
      * 만약 정보가 부족하면, Agent는 추가로 도구를 사용하거나(최대 2회), 최종적으로 일반 지식을 활용하여 답변을 보강합니다.
6.  **사용자 응답**: 생성된 최종 답변이 JSON 형식으로 사용자에게 반환됩니다.

-----

## 🔧 시작하기

### 사전 준비

  * **Python 3.9 이상**
  * **Git**
  * **Google Gemini API 키**: [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 발급받으세요.

### 설치 및 설정

**1. 프로젝트 클론**

```bash
git clone https://github.com/your-username/harbor-agent-api.git
cd harbor-agent-api
```

**2. 가상 환경 생성 및 활성화**

프로젝트의 의존성을 관리하기 위해 가상 환경을 사용하는 것을 권장합니다.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. 필요 패키지 설치**

`requirements.txt` 파일에 명시된 모든 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

**4. `.env` 파일 설정**

프로젝트 루트 디렉터리에 `.env` 파일을 생성하고 아래 내용을 복사하여 붙여넣습니다.

```ini
# .env

# Gemini API 키 (필수)
GEMINI_API_KEY=your_gemini_api_key_here

# ChromaDB 저장 경로 (선택적, 기본값: ./chroma_db)
CHROMA_DB_PATH=./chroma_db

# 상세한 API 호출 로그 출력 여부 (선택적, 기본값: true)
VERBOSE_API_CALLS=true

# 서버 설정 (선택적)
HOST=127.0.0.1 # 실제 서버 배포 시에는 0.0.0.0 사용
PORT=8000

# 로그 레벨 (선택적, DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

  * `GEMINI_API_KEY`: 발급받은 본인의 Gemini API 키로 반드시 교체해야 합니다.

### ⚠️ 중요: 데이터 준비 (ChromaDB 벡터 저장소 생성)

본 프로젝트의 AI 에이전트가 정확한 답변을 생성하기 위해서는, 사전에 항만 관련 법률 및 매뉴얼 데이터를 벡터화하여 ChromaDB 데이터베이스에 저장하는 과정이 **반드시 필요합니다.**

이 과정을 위해, 프로젝트 내에 데이터 전처리 및 DB 생성 파이프라인을 포함했습니다.

**데이터베이스 생성 절차 요약:**

1.  **전처리 코드 확인**: 프로젝트 루트의 `data_preprocessing` 폴더로 이동하여 `README.md` 파일을 먼저 읽어보세요. 데이터 준비를 위한 상세한 설명과 요구사항이 명시되어 있습니다.

2.  **원본 데이터 준비**: 분석하고자 하는 항만 관련 법률, 매뉴얼 등의 원본 파일(`.docx`, `.pdf`, `.pptx`)을 `data_preprocessing/data` 폴더 안에 준비합니다. (폴더가 없다면 생성해주세요.)

3.  **전처리 파이프라인 실행**:

      * `data_preprocessing/data_preprocessing_code.ipynb` Jupyter Notebook 파일을 엽니다.
      * 노트북 내 `Config` 클래스의 설정을 본인의 환경에 맞게 수정한 후, 전체 셀을 순서대로 실행합니다.
      * 이 파이프라인은 문서 파싱, 구조 분석, 텍스트 청킹, 임베딩, 그리고 ChromaDB 저장까지의 모든 과정을 자동화합니다.

4.  **DB 생성 확인**: 파이프라인 실행이 완료되면 노트북 내 `Config` 클래스에 지정된 경로(기본값: `data_preprocessing/chroma_db`)에 벡터 데이터베이스 파일들이 생성됩니다.

5.  **API 서버 연동**: 프로젝트 루트의 `.env` 파일에 있는 `CHROMA_DB_PATH` 환경 변수의 경로를 **위 4번 단계에서 생성된 ChromaDB 폴더의 경로로 정확하게 지정**해야 API 서버가 해당 DB를 정상적으로 읽을 수 있습니다.

    ```ini
    # .env 예시
    # 전처리 파이프라인에서 생성된 DB 경로를 지정합니다.
    CHROMA_DB_PATH=./data_preprocessing/chroma_db
    ```
    
-----

## 🚀 서버 실행

프로젝트 루트 디렉터리에서 아래 명령어를 실행하여 FastAPI 서버를 시작합니다. `run.py` 스크립트는 `.env` 파일의 환경 변수를 자동으로 로드하고 Uvicorn 서버를 실행합니다.

```bash
python run.py
```

서버가 성공적으로 실행되면 다음과 같은 메시지가 터미널에 나타납니다.

```
🚀 Harbor Agent API 서버 시작
📍 주소: http://127.0.0.1:8000
📚 API 문서: http://127.0.0.1:8000/docs
🔍 헬스체크: http://127.0.0.1:8000/health
==================================================
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     HarborAgent 초기화 완료
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

이제 웹 브라우저에서 `http://127.0.0.1:8000/docs`로 접속하여 API 문서를 확인하고 직접 테스트해볼 수 있습니다.

-----

## 📄 API 엔드포인트

### `POST /query`

사용자의 질문을 받아 AI 에이전트가 처리하고 답변을 반환합니다.

  * **Request Body**:

<!-- end list -->

```json
{
  "query": "컨테이너 하역 작업 시 안전 규정에 대해 알려주세요"
}
```

  * **Success Response (200 OK)**:

<!-- end list -->

```json
{
  "answer": "컨테이너 하역 시에는 '항만안전작업규칙' 제10조에 따라 다음과 같은 안전 규정을 준수해야 합니다. 첫째, 작업자는 반드시 안전모와 안전화를 착용해야 합니다. 둘째, 크레인 신호수와 작업자 간의 명확한 신호 체계가 수립되어야 합니다. (이하 생략)",
  "query": "컨테이너 하역 작업 시 안전 규정에 대해 알려주세요",
  "tool_calls": [
    {
      "tool": "search_legal_documents",
      "source_file": "항만안전작업규칙.pdf"
    }
  ],
  "iterations": 2,
  "success": true
}
```

### `GET /health`

서버와 AI 에이전트의 현재 상태를 확인합니다.

  * **Response (200 OK)**:

<!-- end list -->

```json
{
  "status": "healthy",
  "agent_status": "ready",
  "api_version": "1.0.0"
}
```

### `GET /status`

서버의 상세 상태 정보와 사용 가능한 엔드포인트 목록을 반환합니다.

### `GET /`

API 서버가 실행 중임을 알리는 간단한 메시지를 반환합니다.

-----

## 🌳 프로젝트 구조

```
harbor-agent-api/
├── data_preprocessing/
│   ├── data_preprocessing_code.ipynb  # 데이터 전처리/임베딩 노트북
│   └── README.md             # 데이터 전처리 파이프라인 상세 설명
│
├── .env                  # 환경 변수 설정 파일 (직접 생성)
├── .gitignore            # Git 추적 제외 목록
├── main.py               # FastAPI 애플리케이션 정의
├── harbor_agent.py       # 핵심 AI 에이전트 로직
├── models.py             # Pydantic 데이터 모델
├── run.py                # 서버 실행 스크립트
├── requirements.txt      # Python 패키지 의존성 목록
├── venv/                 # Python 가상 환경 폴더 (직접 생성)
└── chroma_db/            # 벡터 DB 폴더 (직접 생성)
```

-----

## 🔑 환경 변수

`.env` 파일을 통해 다음 환경 변수들을 설정할 수 있습니다.

| 변수명              | 설명                                                         | 필수 여부 | 기본값          |
| ------------------- | ------------------------------------------------------------ | --------- | --------------- |
| `GEMINI_API_KEY`    | Google Gemini API 키                                         | **필수** | 없음            |
| `CHROMA_DB_PATH`    | ChromaDB 데이터베이스 파일이 저장될 로컬 경로입니다.         | 선택      | `./chroma_db`   |
| `VERBOSE_API_CALLS` | `true`로 설정 시, Gemini API 호출 전 프롬프트 내용을 로그로 출력합니다. | 선택      | `true`          |
| `HOST`              | 서버가 실행될 호스트 주소입니다.                               | 선택      | `127.0.0.1`     |
| `PORT`              | 서버가 실행될 포트 번호입니다.                                 | 선택      | `8000`          |
| `LOG_LEVEL`         | 애플리케이션의 로그 레벨입니다. (DEBUG, INFO, WARNING, ERROR)  | 선택      | `INFO`          |

-----

## 🐛 문제 해결

  * **`GEMINI_API_KEY 환경변수가 설정되지 않았습니다.` 오류 발생 시:**
      * 프로젝트 루트에 `.env` 파일이 있는지 확인하세요.
      * `.env` 파일 안에 `GEMINI_API_KEY=your_api_key_here` 형식이 올바르게 작성되었는지 확인하세요.
  * **서버 실행 후 `Agent가 초기화되지 않았습니다.` 오류 발생 시:**
      * 서버 시작 로그에 `HarborAgent 초기화 실패`와 같은 다른 오류 메시지가 없는지 확인하세요. API 키가 유효하지 않거나 네트워크 문제일 수 있습니다.
  * **질문에 대한 답변이 항상 "관련 정보를 찾을 수 없었습니다."로 나올 경우:**
      * ChromaDB 데이터베이스가 올바르게 생성되었는지 확인하세요. `CHROMA_DB_PATH` 경로에 `chroma.sqlite3` 파일과 데이터 파일들이 있는지 확인해야 합니다.
      * 데이터 준비(Ingestion) 과정이 질문에 답변하기에 충분한 데이터를 포함하고 있는지 검토하세요.
