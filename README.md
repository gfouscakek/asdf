# AI 모델 안전 점검 웹앱

허깅페이스(Hugging Face)에 공개된 AI 모델을 검색해 내 저장소(SQLite)에 저장하고,
파일 형식 안전성(safetensors 여부)·라이선스·신뢰도·검토 여부·메모를 관리하는 Streamlit 웹앱입니다.

## 파일

| 파일 | 역할 |
|---|---|
| `app.py` | 화면·메뉴 처리, 입력 검증 |
| `database.py` | SQLite 처리 (테이블 생성, 추가·조회·검색·수정·삭제, 요약) |
| `api.py` | 허깅페이스 모델 목록 API 호출 |
| `models.db` | 실행하면 자동 생성되는 SQLite 파일 |

## API
```
GET https://huggingface.co/api/models?search={키워드}&limit=5&sort=downloads&direction=-1
```

API 키가 필요 없습니다. 응답의 `id`, `pipeline_tag`, `downloads`, `tags`에서
모델 이름·작업 종류·다운로드 수·라이선스·safetensors 여부를 뽑습니다.
정보가 없는 모델은 작업 종류 `기타`, 라이선스 `정보 없음`, safetensors `0`으로 저장됩니다.
