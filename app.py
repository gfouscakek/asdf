"""AI 모델 안전 점검 웹앱 (ModelCheck) — 데스크톱 레이아웃

설계: DESIGN.md (사이드바 248px + 상단바 + 행 그리드)
"""
import html

import streamlit as st

from database import (create_table, add_model, search_models, toggle_reviewed,
                      update_trust, update_memo, delete_model, get_summary)
from api import search_external_models

create_table()

st.set_page_config(page_title='ModelCheck — AI 모델 안전 점검', page_icon='🛡️',
                   layout='wide', initial_sidebar_state='expanded')

# ---------------------------------------------------------------- 토큰
BLUE = '#006FFD'
BLUE_INK = '#0060DB'
BLUE_DEEP = '#0050B3'
BLUE_TINT = '#EAF2FF'
VIOLET = '#6F8AFF'
BORDER = '#E8E9F1'
BG = '#F8F9FE'
INK = '#1F2024'
SUB = '#71727A'
MUTED = '#6B6D76'
AMBER_INK = '#9A4F0C'
AMBER_TINT = '#FFF4E6'
GREEN = '#1FA97F'
GREEN_INK = '#137A5B'
GREEN_TINT = '#E7FAE8'

NAV_KEY = 'nav'
if 'goto' in st.session_state:            # 버튼 → 다음 실행에서 내비 변경
    st.session_state[NAV_KEY] = st.session_state.pop('goto')

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"],
.stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stWidgetLabel"],
.stApp .mc-page-title, .stApp .mc-page-sub, .stApp .mc-section-title,
.stApp button, .stApp input, .stApp textarea {{
  font-family:Inter, 'Noto Sans KR', -apple-system, 'Malgun Gothic', sans-serif;
  -webkit-font-smoothing:antialiased;
}}
.stApp {{ background:{BG}; }}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{ display:none; }}

/* ---------- 사이드바 ---------- */
[data-testid="stSidebar"] {{
  width:248px !important; min-width:248px !important; background:#fff;
  border-right:1px solid {BORDER};
  overflow-x:hidden !important;          /* Streamlit 자체 거터(8px)로 생기는 가로 스크롤 방지 */
}}
[data-testid="stSidebarHeader"] {{ display:none; }}
[data-testid="stSidebar"] > div:first-child {{ padding:0 16px; }}
[data-testid="stSidebarUserContent"] {{ padding:16px 0 !important; }}
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"] {{ display:none; }}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap:4px; }}

.mc-brand {{ display:flex; align-items:center; gap:10px; padding:0 6px 12px; }}
.mc-logo {{
  width:36px; height:36px; border-radius:12px; color:#fff; font-size:12.5px; font-weight:800;
  display:flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg, {BLUE} 0%, {BLUE_INK} 100%);
  box-shadow:0 6px 14px rgba(0,111,253,.28);
}}
.mc-brand b {{ display:block; font-size:14.5px; font-weight:800; color:{INK}; letter-spacing:-.3px; }}
.mc-brand span {{ font-size:10.5px; color:{MUTED}; font-weight:600; }}

/* 사이드바 내비 (세로 라디오) */
/* 라디오 묶음은 기본적으로 내용 폭(66px)으로 줄어든다. 사이드바 폭을 꽉 채워야
   오른쪽 빈 공간이 사라지고 선택 하이라이트가 행 전체를 덮는다. */
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(div[role="radiogroup"]) {{
  width:100% !important; align-self:stretch !important;
}}
[data-testid="stSidebar"] div[role="radiogroup"] {{
  display:flex; flex-direction:column; gap:2px;
  width:100% !important; align-items:stretch !important;
}}
[data-testid="stSidebar"] div[role="radiogroup"] label {{
  width:100% !important; box-sizing:border-box; margin:0 !important; padding:8px 12px; border-radius:12px;
  font-size:13px; font-weight:700; color:{SUB}; transition:color .12s, background-color .12s; cursor:pointer;
  display:flex; align-items:center; gap:8px;
}}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{ background:{BG}; }}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:focus-visible) {{ outline:2px solid {BLUE_INK}; outline-offset:2px; }}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
  background:{BLUE_TINT}; color:{BLUE_INK};
}}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {{ color:{BLUE_INK} !important; }}
[data-testid="stSidebar"] div[role="radiogroup"] label > div > div:first-child {{ display:none; }}
[data-testid="stSidebar"] div[role="radiogroup"] label p {{ font-size:13px !important; font-weight:700 !important; }}

.mc-side-foot {{
  margin-top:14px; padding:12px 14px; border-radius:16px; background:{BG}; border:1px solid {BORDER};
}}
.mc-side-foot div {{ display:flex; justify-content:space-between; font-size:11.5px; color:{SUB}; margin:3px 0; }}
.mc-side-foot b {{ color:{INK}; font-weight:700; font-variant-numeric:tabular-nums; }}

/* ---------- 본문 ---------- */
.block-container {{ max-width:1120px; padding:28px 36px 56px; }}
[data-testid="stVerticalBlock"] {{ gap:0.6rem; }}
/* Streamlit 은 stMarkdown 에 margin-bottom:-1rem 을 줘서 HTML 블록이 아래 요소와 겹친다 */
[data-testid="stMarkdown"], [data-testid="stMarkdownContainer"] {{ margin-bottom:0 !important; }}

.stApp .mc-page-title {{ margin:0; font-size:22px; font-weight:800; color:{INK}; letter-spacing:-.6px; line-height:1.3; text-wrap:balance; }}
.mc-page-sub {{ font-size:12.5px; color:{SUB}; margin-top:4px; line-height:1.4; text-wrap:pretty; }}
.stApp .mc-section-title {{ margin:26px 0 8px; font-size:16px; font-weight:700; color:{INK}; line-height:1.3; }}

/* 목록 헤더: 행과 같은 st.columns 비율을 쓴다 */
div[data-testid="stHorizontalBlock"]:has(.mc-thcell) {{ padding:0 19px; gap:16px; margin:8px 0 2px; }}
.mc-thcell {{ font-size:11px; font-weight:700; color:{MUTED}; letter-spacing:.02em; }}
.mc-thcell.r {{ text-align:right; }}

/* 행: stVerticalBlock > stLayoutWrapper > stHorizontalBlock(.mc-row 포함) 인 컨테이너만 카드로 */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] .mc-row) {{
  background:#fff !important; border:1px solid {BORDER} !important; border-radius:16px !important;
  padding:12px 19px !important; transition:border-color .15s, box-shadow .15s; box-shadow:0 1px 2px rgba(31,32,36,.03);
}}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] .mc-row):hover {{
  border-color:#CFD8EA !important; box-shadow:0 8px 22px rgba(31,32,36,.07);
}}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] .mc-row)
  div[data-testid="stVerticalBlock"] {{
  background:transparent !important; border:none !important; padding:0 !important;
  margin:0 !important; box-shadow:none !important;
}}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] .mc-row)
  [data-testid="stHorizontalBlock"] {{ align-items:center; gap:16px; }}

/* 신뢰도 1~5: 한 줄 유지 */
[data-testid="stButtonGroup"] div[role="radiogroup"] {{ flex-wrap:nowrap !important; gap:4px !important; }}
/* 팝오버 버튼의 화살표 제거 */
[data-testid="stPopoverButton"] div[aria-hidden="true"] {{ display:none; }}

.mc-row {{ display:flex; gap:12px; align-items:center; min-width:0; }}
.mc-avatar {{
  flex:0 0 40px; width:40px; height:40px; border-radius:13px; display:flex;
  align-items:center; justify-content:center; font-size:12px; font-weight:800; letter-spacing:-.3px;
}}
.av-blue {{ background:{BLUE_TINT}; color:{BLUE_INK}; }}
.av-amber {{ background:{AMBER_TINT}; color:{AMBER_INK}; }}
.mc-title {{ font-size:14.5px; font-weight:700; color:{INK}; letter-spacing:-.3px;
             white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.mc-meta {{ font-size:11.5px; color:{SUB}; margin-top:2px;
            white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.mc-num {{ font-size:12.5px; font-weight:700; color:{INK}; text-align:right; font-variant-numeric:tabular-nums; }}
.mc-cell {{ font-size:12px; color:{SUB}; text-align:right;
            white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}

.chip {{ display:inline-flex; align-items:center; font-size:10px; font-weight:700;
         padding:3px 8px; border-radius:999px; margin:4px 4px 0 0; }}
.chip-blue {{ background:{BLUE_TINT}; color:{BLUE_INK}; }}
.chip-amber {{ background:{AMBER_TINT}; color:{AMBER_INK}; }}
.chip-green {{ background:{GREEN_TINT}; color:{GREEN_INK}; }}
.chip-grey {{ background:#F2F3F7; color:{MUTED}; }}

/* 위젯 */
[data-testid="stWidgetLabel"] p {{ font-size:11px !important; font-weight:700 !important; color:{MUTED} !important; }}
/* Streamlit 은 입력창을 바깥 래퍼(RootElement)와 안쪽 input 두 겹으로 그린다.
   바깥 래퍼에 기본 진한 테두리가 있어서, 래퍼를 테두리 기준으로 쓰고 안쪽 input 은 테두리를 뺀다. */
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"] {{
  border:1px solid {BORDER} !important; border-radius:12px !important; background:#fff !important;
  transition:border-color .15s, box-shadow .15s;
}}
[data-testid="stTextInputRootElement"]:focus-within, [data-testid="stTextAreaRootElement"]:focus-within {{
  border-color:{BLUE} !important; box-shadow:0 0 0 3px rgba(0,111,253,.12) !important;
}}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {{
  border:none !important; box-shadow:none !important; background:transparent !important;
  border-radius:12px !important; font-size:13px !important; color:{INK} !important; padding:10px 12px !important;
}}
[data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {{
  color:{MUTED} !important; opacity:1;
}}
div[data-baseweb="select"] > div {{
  border-radius:12px !important; border-color:{BORDER} !important; background:#fff !important;
  font-size:12.5px !important; min-height:40px;
}}
/* Streamlit 1.65 의 segmented_control 버튼은 data-testid 가 없고 role="radio" 로 식별된다 */
[data-testid="stButtonGroup"] button[role="radio"] {{
  border-radius:999px !important; font-size:11.5px !important; font-weight:700 !important;
  min-height:32px; min-width:34px; border:1px solid {BORDER} !important;
  background:#fff !important; color:{SUB} !important; padding:0 6px; box-shadow:none !important;
}}
[data-testid="stButtonGroup"] button[role="radio"]:hover {{ border-color:{BLUE} !important; color:{BLUE_INK} !important; }}
[data-testid="stButtonGroup"] button[role="radio"][aria-checked="true"] {{
  background:{BLUE_INK} !important; color:#fff !important; border-color:{BLUE_INK} !important;
  box-shadow:0 4px 10px rgba(0,111,253,.28) !important;
}}
[data-testid="stButtonGroup"] button[role="radio"][aria-checked="true"] p,
[data-testid="stButtonGroup"] button[role="radio"][aria-checked="true"] div {{ color:#fff !important; }}
[data-testid="stToggle"] p {{ font-size:11.5px !important; font-weight:600 !important; color:{SUB} !important; }}

.stButton > button, .stFormSubmitButton > button, [data-testid="stPopover"] button {{
  border-radius:12px; border:1px solid {BORDER}; background:#fff; color:{INK};
  font-weight:700; font-size:12px; min-height:38px; width:100%;
}}
.stButton > button:hover, [data-testid="stPopover"] button:hover {{
  border-color:{BLUE}; color:{BLUE_INK};
}}
.stButton > button:focus-visible, [data-testid="stPopover"] button:focus-visible,
[data-testid="stButtonGroup"] button[role="radio"]:focus-visible {{ outline:2px solid {BLUE_INK}; outline-offset:2px; }}
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {{
  background:{BLUE_INK} !important; border:none !important; color:#fff !important;
  box-shadow:0 6px 16px rgba(0,111,253,.24) !important;
}}
[data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primaryFormSubmit"]:hover {{
  background:{BLUE_DEEP} !important; color:#fff !important;
}}
[data-testid="stBaseButton-primaryFormSubmit"] p {{ color:#fff !important; }}

/* 폼 */
[data-testid="stForm"] {{
  background:#fff !important; border:1px solid {BORDER} !important; border-radius:18px !important;
  padding:22px !important;
}}

/* 지표 타일 */
.mc-stats {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:16px; margin:6px 0 4px; }}
.mc-stat {{ background:#fff; border:1px solid {BORDER}; border-radius:20px; padding:18px 20px;
            position:relative; overflow:hidden; }}
.mc-stat::after {{ content:""; position:absolute; inset:0 auto 0 0; width:4px; }}
.mc-stat.s1::after {{ background:{BLUE}; }}
.mc-stat.s2::after {{ background:{GREEN}; }}
.mc-stat.s3::after {{ background:{VIOLET}; }}
.mc-stat b {{ display:block; font-size:28px; font-weight:800; color:{INK}; letter-spacing:-1px; font-variant-numeric:tabular-nums; }}
.mc-stat span {{ font-size:11.5px; color:{SUB}; font-weight:600; }}

.mc-bar-row {{ display:grid; grid-template-columns:240px 1fr 40px; align-items:center; gap:14px; margin:10px 0; }}
.mc-bar-label {{ font-size:12.5px; font-weight:600; color:{INK}; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.mc-bar-track {{ height:10px; border-radius:999px; background:#EFF1F6; overflow:hidden; }}
.mc-bar-fill {{ height:10px; border-radius:999px; background:{BLUE}; }}
.mc-bar-value {{ font-size:11.5px; font-weight:700; color:{SUB}; text-align:right; font-variant-numeric:tabular-nums; }}

.mc-empty {{
  background:#fff; border:1px dashed #C9CDD9; border-radius:20px; padding:56px 24px;
  text-align:center; color:{MUTED}; font-size:12.5px; line-height:1.6;
}}
.mc-empty b {{ display:block; font-size:15px; font-weight:700; color:{INK}; margin-bottom:6px; }}

[data-testid="stAlert"] {{ border-radius:14px; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- 공통
def safe(text):
    return html.escape(str(text))


def chip(text, tone):
    return f'<span class="chip chip-{tone}">{safe(text)}</span>'


def initials(model_id):
    name = model_id.split('/')[-1]
    return ''.join(ch for ch in name if ch.isalnum())[:2].upper() or 'AI'


def compact(number):
    if number >= 1_000_000:
        return f'{number / 1_000_000:.1f}M'
    if number >= 1_000:
        return f'{number / 1_000:.1f}K'
    return str(number)


def empty_state(title, text, cta_label=None, cta_target=None):
    st.markdown(f'<div class="mc-empty"><b>{safe(title)}</b>{safe(text)}</div>', unsafe_allow_html=True)
    if cta_label:
        col_a, col_b, col_c = st.columns([2, 1.2, 2])
        with col_b:
            if st.button(cta_label, key=f'cta_{title}', use_container_width=True, type='primary'):
                st.session_state['goto'] = cta_target
                st.rerun()


# 저장소 목록 / 검색 결과 목록의 컬럼 비율. 헤더와 행이 같은 값을 쓴다.
REPO_COLS = [3.2, 0.8, 1.0, 0.7, 2.5, 0.6]
SEARCH_COLS = [3.6, 0.9, 1.1, 0.9]


def header_row(labels, ratios):
    cells = st.columns(ratios)
    for cell, (label, align) in zip(cells, labels):
        with cell:
            st.markdown(f'<div class="mc-thcell {align}">{safe(label)}</div>', unsafe_allow_html=True)


def model_cell(row):
    model_id, task, downloads, license_name = row[1], row[2], row[3], row[4]
    safetensors, trust, reviewed = row[5], row[6], row[7]
    tone = 'blue' if safetensors == 1 else 'amber'
    chips = chip('safetensors 있음', 'blue') if safetensors == 1 else chip('점검 필요', 'amber')
    chips += chip('검토 완료', 'green') if reviewed == 1 else chip('미검토', 'grey')
    st.markdown(f"""
    <div class="mc-row">
      <div class="mc-avatar av-{tone}">{safe(initials(model_id))}</div>
      <div style="min-width:0">
        <div class="mc-title">{safe(model_id)}</div>
        <div class="mc-meta">{safe(task)} · {safe(license_name)}</div>
        <div>{chips}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------- 사이드바
summary = get_summary()
reviewed_ratio = round(summary['reviewed'] / summary['total'] * 100) if summary['total'] else 0
safe_ratio = round(summary['safetensors'] / summary['total'] * 100) if summary['total'] else 0

with st.sidebar:
    st.markdown("""
    <div class="mc-brand">
      <div class="mc-logo">MC</div>
      <div><b>ModelCheck</b><span>AI 모델 안전 점검</span></div>
    </div>
    """, unsafe_allow_html=True)

    nav = st.radio('메뉴', ['저장소', '등록', '검색', '요약'],
                   key=NAV_KEY, label_visibility='collapsed')

    st.markdown(f"""
    <div class="mc-side-foot">
      <div><span>저장한 모델</span><b>{summary['total']}</b></div>
      <div><span>safetensors</span><b>{safe_ratio}%</b></div>
      <div><span>검토 완료</span><b>{reviewed_ratio}%</b></div>
    </div>
    """, unsafe_allow_html=True)


def page_head(title, sub, action_label=None, action_target=None):
    col_title, col_action = st.columns([3, 1], vertical_alignment='bottom')
    with col_title:
        st.markdown(f'<h1 class="mc-page-title">{safe(title)}</h1>'
                    f'<div class="mc-page-sub">{safe(sub)}</div>', unsafe_allow_html=True)
    with col_action:
        if action_label and st.button(action_label, use_container_width=True, type='primary'):
            st.session_state['goto'] = action_target
            st.rerun()


# ---------------------------------------------------------------- 1) 저장소
if nav == '저장소':
    page_head('내 저장소', f"저장한 모델 {summary['total']}개 · 검토 완료 {reviewed_ratio}%",
              '모델 검색', '검색')

    col_search, col_filter = st.columns([3, 1], vertical_alignment='bottom')
    with col_search:
        keyword = st.text_input('검색', placeholder='모델 이름으로 검색 (예: bert)',
                                label_visibility='collapsed')
    with col_filter:
        safe_filter = st.selectbox('safetensors', ['전체', '있음', '없음'],
                                   label_visibility='collapsed')

    rows = search_models(keyword.strip(), safe_filter)

    if len(rows) == 0:
        if keyword.strip() or safe_filter != '전체':
            empty_state('조건에 맞는 모델이 없어요', '검색어나 필터를 바꿔 보세요.')
        else:
            empty_state('저장된 모델이 없어요', '허깅페이스에서 모델을 찾아 담아 보세요.',
                        '모델 검색', '검색')
    else:
        header_row([('모델', ''), ('다운로드', 'r'), ('라이선스', 'r'),
                    ('검토', ''), ('신뢰도', ''), ('', '')], REPO_COLS)
        for row in rows:
            model_pk, trust, reviewed = row[0], row[6], row[7]
            with st.container():
                c_name, c_dl, c_lic, c_rev, c_trust, c_more = st.columns(
                    REPO_COLS, vertical_alignment='center')
                with c_name:
                    model_cell(row)
                with c_dl:
                    st.markdown(f'<div class="mc-num">{compact(row[3])}</div>', unsafe_allow_html=True)
                with c_lic:
                    st.markdown(f'<div class="mc-cell">{safe(row[4])}</div>', unsafe_allow_html=True)
                with c_rev:
                    new_state = st.toggle('검토', value=bool(reviewed), key=f'review_{model_pk}',
                                          label_visibility='collapsed')
                    if new_state != bool(reviewed):
                        toggle_reviewed(model_pk)
                        st.rerun()
                with c_trust:
                    new_trust = st.segmented_control(
                        '신뢰도', [1, 2, 3, 4, 5], default=trust if trust else None,
                        key=f'trust_{model_pk}', label_visibility='collapsed')
                    if new_trust and new_trust != trust:
                        update_trust(model_pk, new_trust)
                        st.rerun()
                with c_more:
                    with st.popover('⋯', use_container_width=True):
                        memo = st.text_area('메모', value=row[8], key=f'memo_{model_pk}',
                                            height=110, placeholder='출처 · 사용 목적 · 점검 내용')
                        if st.button('메모 저장', key=f'save_memo_{model_pk}', use_container_width=True):
                            update_memo(model_pk, memo)
                            st.toast('메모를 저장했습니다.')
                            st.rerun()
                        if st.button('삭제', key=f'del_{model_pk}', use_container_width=True):
                            delete_model(model_pk)
                            st.toast('저장소에서 삭제했습니다.')
                            st.rerun()

# ---------------------------------------------------------------- 2) 등록
elif nav == '등록':
    page_head('직접 등록', 'API에 없는 모델이나 직접 구한 모델을 기록합니다.')

    col_form, col_guide = st.columns([2, 1], vertical_alignment='top')
    with col_form:
        with st.form('add_model_form', clear_on_submit=True):
            model_id = st.text_input('모델 이름 *', placeholder='예: my-org/my-model')
            task = st.text_input('작업 종류', placeholder='예: text-generation (비우면 기타)')
            license_name = st.text_input('라이선스', placeholder='예: apache-2.0 (비우면 정보 없음)')
            has_safetensors = st.checkbox('safetensors 형식으로 배포됨')
            memo = st.text_area('메모', placeholder='출처 · 사용 목적 · 점검 내용', height=100)
            submitted = st.form_submit_button('저장소에 등록', use_container_width=True, type='primary')

            if submitted:
                if not model_id.strip():
                    st.warning('모델 이름을 입력해주세요.')
                else:
                    added = add_model(model_id.strip(), task.strip() or '기타', 0,
                                      license_name.strip() or '정보 없음',
                                      1 if has_safetensors else 0, memo.strip())
                    if added:
                        st.success('저장소에 등록했습니다.')
                    else:
                        st.warning('이미 저장된 모델입니다.')
    with col_guide:
        st.markdown(f"""
        <div style="background:#fff;border:1px solid {BORDER};border-radius:18px;padding:18px 20px;">
          <div style="font-size:12.5px;font-weight:800;color:{INK};margin-bottom:8px;">입력 안내</div>
          <div style="font-size:12px;color:{SUB};line-height:1.75;">
            <b>모델 이름</b>은 저장소의 고유 키입니다. 같은 이름은 다시 저장되지 않습니다.<br>
            <b>safetensors</b>는 pickle(.bin)보다 안전한 파일 형식입니다. 배포 형식을 모르면 체크하지 마세요.
          </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------- 3) 검색
elif nav == '검색':
    page_head('외부 모델 검색', '허깅페이스에서 모델을 찾아 안전 형식과 라이선스를 확인합니다.')

    col_input, col_button = st.columns([4, 1], vertical_alignment='bottom')
    with col_input:
        keyword = st.text_input('검색어', placeholder='예: llama, bert, whisper',
                                label_visibility='collapsed')
    with col_button:
        search_clicked = st.button('검색', use_container_width=True, type='primary')

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

    results = st.session_state.get('search_results', [])

    if results:
        st.markdown(f'<div class="mc-page-sub" style="margin:10px 0 6px;">검색 결과 {len(results)}건</div>',
                    unsafe_allow_html=True)
        header_row([('모델', ''), ('다운로드', 'r'), ('라이선스', 'r'), ('', '')], SEARCH_COLS)
        saved_ids = {saved[1] for saved in search_models('', '전체')}
        for index, model in enumerate(results):
            with st.container():
                c_name, c_dl, c_lic, c_action = st.columns(
                    SEARCH_COLS, vertical_alignment='center')
                with c_name:
                    row = (None, model['model_id'], model['task'], model['downloads'],
                           model['license'], model['safetensors'], 0, 0, '')
                    model_cell(row)
                with c_dl:
                    st.markdown(f'<div class="mc-num">{compact(model["downloads"])}</div>',
                                unsafe_allow_html=True)
                with c_lic:
                    st.markdown(f'<div class="mc-cell">{safe(model["license"])}</div>',
                                unsafe_allow_html=True)
                with c_action:
                    # 이미 담은 모델도 눌러 볼 수 있다. add_model 이 False 를 돌려주면(UNIQUE 충돌) 경고만 띄운다.
                    already = model['model_id'] in saved_ids
                    label = '저장됨' if already else '담기'
                    if st.button(label, key=f'save_ext_{index}', use_container_width=True,
                                 type='secondary' if already else 'primary'):
                        added = add_model(model['model_id'], model['task'], model['downloads'],
                                          model['license'], model['safetensors'])
                        if added:
                            st.toast(f"'{model['model_id']}' 저장 완료")
                            st.rerun()
                        else:
                            st.toast('이미 저장된 모델입니다.')
    elif search_clicked:
        empty_state('검색 결과가 없어요', '다른 키워드로 다시 시도해 보세요.')
    else:
        empty_state('모델을 검색해 보세요', '예: llama, bert, whisper')

# ---------------------------------------------------------------- 4) 요약
else:
    page_head('요약', '저장한 모델의 안전 형식과 검토 진행 상황입니다.')

    if summary['total'] == 0:
        empty_state('아직 데이터가 없어요', '모델을 저장하면 여기에 통계가 나타납니다.',
                    '모델 검색', '검색')
    else:
        st.markdown(f"""
        <div class="mc-stats">
          <div class="mc-stat s1"><b>{summary['total']}</b><span>저장한 모델</span></div>
          <div class="mc-stat s2"><b>{safe_ratio}%</b><span>safetensors 비율</span></div>
          <div class="mc-stat s3"><b>{reviewed_ratio}%</b><span>검토 완료율</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<h2 class="mc-section-title">작업 종류별</h2>',
                    unsafe_allow_html=True)
        max_count = max(count for _, count in summary['by_task'])
        for task, count in summary['by_task']:
            width = max(round(count / max_count * 100), 6)
            st.markdown(f"""
            <div class="mc-bar-row">
              <div class="mc-bar-label">{safe(task)}</div>
              <div class="mc-bar-track"><div class="mc-bar-fill" style="width:{width}%"></div></div>
              <div class="mc-bar-value">{count}</div>
            </div>
            """, unsafe_allow_html=True)
