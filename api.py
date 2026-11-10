import requests

API_URL = 'https://huggingface.co/api/models'
LIMIT = 5


def search_external_models(keyword):
    """허깅페이스 모델 목록 API로 키워드를 검색해 dict 리스트로 돌려준다."""
    if keyword.strip() == '':
        return []

    params = {
        'search': keyword.strip(),
        'limit': LIMIT,
        'sort': 'downloads',
        'direction': -1,
    }

    try:
        response = requests.get(API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        raise RuntimeError('네트워크 오류가 발생했습니다. 잠시 후 다시 시도하세요.')
    except ValueError:
        raise RuntimeError('응답 데이터를 처리할 수 없습니다.')

    results = []
    for item in data:
        tags = item.get('tags') or []

        # tags 안의 'license:apache-2.0' 형태에서 라이선스 이름만 뽑는다.
        license_name = '정보 없음'
        for tag in tags:
            if tag.startswith('license:'):
                license_name = tag.replace('license:', '')
                break

        model = {
            'model_id': item.get('id', '이름 없음'),
            'task': item.get('pipeline_tag') or '기타',
            'downloads': item.get('downloads', 0),
            'license': license_name,
            'safetensors': 1 if 'safetensors' in tags else 0,
        }
        results.append(model)

    return results
