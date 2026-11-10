import streamlit as st
from database import (create_table,
                      add_model,
                      search_models,
                      toggle_reviewed,
                      update_trust,
                      update_memo,
                      delete_model,
                      get_summary)

from api import search_external_models

create_table()


def print_search_results(results):
    if len(results) == 0:
        st.warning("검색 결과가 없습니다.")
        return

    st.subheader('외부 모델 검색 결과')
    for index, model in enumerate(results, start=1):
        if model['safetensors'] == 1:
            safe_text = 'safetensors 있음'
        else:
            safe_text = '점검 필요'

        st.write(f"{index}. {model['model_id']} / {model['task']} / "
                 f"{model['downloads']:,}회 / {model['license']} / {safe_text}")

        col_info, col_save = st.columns([4, 1])
        with col_info:
            st.write(f"모델 이름: {model['model_id']}")
        with col_save:
            if st.button("내 저장소에 저장", key=f"save_ext_{index}", use_container_width=True):
                added = add_model(model['model_id'], model['task'], model['downloads'],
                                  model['license'], model['safetensors'])
                if added:
                    st.toast(f"'{model['model_id']}'을(를) 저장했습니다.")
                else:
                    st.warning("이미 저장된 모델입니다.")
        st.divider()


def print_models(rows):
    if len(rows) == 0:
        st.info('저장된 모델이 없습니다.')
        return

    st.write(f"총 {len(rows)}건")
    st.write("---")

    for row in rows:
        model_pk = row[0]
        model_id = row[1]
        task = row[2]
        downloads = row[3]
        license_name = row[4]
        safetensors = row[5]
        trust = row[6]
        reviewed = row[7]

        if safetensors == 1:
            safe_text = 'safetensors 있음'
        else:
            safe_text = '점검 필요'

        if reviewed == 1:
            review_text = '검토 완료'
        else:
            review_text = '미검토'

        if trust == 0:
            trust_text = '신뢰도 없음'
        else:
            trust_text = f"신뢰도 {trust}"

        st.write(f'{model_pk}. {model_id} / {task} / {downloads:,}회 / '
                 f'{license_name} / {safe_text} / {review_text} / {trust_text}')

        col1, col2, col3, col4 = st.columns([2, 1.5, 2, 1])

        with col1:  # 검토 상태 변경
            toggle_label = "검토 취소" if reviewed == 1 else "검토 완료"
            if st.button(toggle_label, key=f'toggle_{model_pk}'):
                toggle_reviewed(model_pk)
                st.toast(f"'{model_id}' 검토 상태가 변경되었습니다.")
                st.rerun()

        with col2:  # 신뢰도
            current_trust = trust if 1 <= trust <= 5 else 1
            new_trust = st.selectbox('신뢰도', options=[1, 2, 3, 4, 5],
                                     index=int(current_trust) - 1,
                                     key=f'trust_sel_{model_pk}',
                                     label_visibility='collapsed')

        with col3:  # 신뢰도 저장
            if st.button('신뢰도 저장', key=f'trust_btn_{model_pk}'):
                update_trust(model_pk, new_trust)
                st.toast(f"'{model_id}'의 신뢰도를 저장했습니다.")
                st.rerun()

        with col4:  # 삭제
            if st.button('삭제', key=f"del_{model_pk}"):
                delete_model(model_pk)
                st.toast(f"'{model_id}'을(를) 삭제했습니다.")
                st.rerun()

        with st.expander('메모'):
            memo = st.text_area('메모', value=row[8], key=f'memo_{model_pk}',
                                label_visibility='collapsed',
                                placeholder='출처 · 사용 목적 · 점검 내용')
            if st.button('메모 저장', key=f'memo_btn_{model_pk}'):
                update_memo(model_pk, memo)
                st.toast('메모를 저장했습니다.')
                st.rerun()


st.set_page_config(page_title='AI 모델 안전 점검 웹앱', page_icon='🛡️')

st.title("AI 모델 안전 점검 웹앱")
st.write("허깅페이스에서 모델을 검색해 저장하고, 안전 형식과 점검 상태를 관리합니다.")

menu = st.sidebar.radio("메뉴 선택", ["내 저장소", "직접 등록", "외부 모델 검색", "요약"])

if menu == "내 저장소":
    st.header('내 저장소')
    st.write("저장한 모델을 조회하고 검토 상태, 신뢰도, 메모를 관리할 수 있습니다.")

    col_search, col_filter = st.columns([3, 1])
    with col_search:
        keyword = st.text_input('내 저장소 검색(모델 이름)', placeholder='검색어 입력')
    with col_filter:
        safe_filter = st.selectbox('safetensors', ['전체', '있음', '없음'])

    rows = search_models(keyword.strip(), safe_filter)
    print_models(rows)

elif menu == "직접 등록":
    st.header('직접 등록')
    st.write("API에 없는 모델이나 직접 구한 모델을 기록하세요.")

    with st.form('add_model_form', clear_on_submit=True):
        model_id = st.text_input('모델 이름 *', placeholder='예: my-org/my-model')
        task = st.text_input('작업 종류', placeholder='예: text-generation (비우면 기타)')
        license_name = st.text_input('라이선스', placeholder='예: apache-2.0 (비우면 정보 없음)')
        has_safetensors = st.checkbox('safetensors 형식으로 배포됨')
        memo = st.text_area('메모', placeholder='출처 · 사용 목적 · 점검 내용')
        submitted = st.form_submit_button('저장소에 등록', use_container_width=True)

        if submitted:
            if not model_id.strip():
                st.warning('모델 이름을 입력해주세요.')
            else:
                added = add_model(model_id.strip(),
                                  task.strip() or '기타',
                                  0,
                                  license_name.strip() or '정보 없음',
                                  1 if has_safetensors else 0,
                                  memo.strip())
                if added:
                    st.success('저장소에 등록되었습니다.')
                else:
                    st.warning('이미 저장된 모델입니다.')

elif menu == "외부 모델 검색":
    st.header('외부 모델 검색')
    st.write('허깅페이스 API로 모델을 검색해 저장소에 담을 수 있습니다.')

    search_col, btn_col = st.columns([4, 1])
    with search_col:
        keyword = st.text_input('검색할 모델 이름', placeholder='예: bert, llama, whisper',
                                label_visibility='collapsed')
    with btn_col:
        search_clicked = st.button('모델 검색', use_container_width=True)

    if search_clicked:
        if not keyword.strip():
            st.warning('검색어를 입력해주세요.')
            st.session_state['search_results'] = []
        else:
            try:
                st.session_state['search_results'] = search_external_models(keyword.strip())
            except RuntimeError as error:
                st.error(str(error))
                st.session_state['search_results'] = []

    if 'search_results' in st.session_state:
        print_search_results(st.session_state['search_results'])

else:
    st.header('요약')
    summary = get_summary()

    if summary['total'] == 0:
        st.info('저장된 모델이 없습니다.')
    else:
        total = summary['total']
        safe_ratio = round(summary['safetensors'] / total * 100)
        reviewed_ratio = round(summary['reviewed'] / total * 100)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('저장한 모델', f"{total}개")
        with col2:
            st.metric('safetensors 비율', f"{safe_ratio}%")
        with col3:
            st.metric('검토 완료율', f"{reviewed_ratio}%")

        st.subheader('작업 종류별 건수')
        for task, count in summary['by_task']:
            st.write(f"{task}: {count}건")
