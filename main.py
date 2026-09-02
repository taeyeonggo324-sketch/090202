import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client
import uuid

st.set_page_config(page_title="AI 3D 피팅 & 패션 커뮤니티", page_icon="👗", layout="wide")

# -------------------------------------------------------------------
# 0. 커스텀 CSS 스타일링 (깔끔한 쇼핑몰 & 커뮤니티 UI 디자인)
# -------------------------------------------------------------------
st.markdown("""
    <style>
    /* 상단 기본 여백 줄이기 */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
    
    /* 메인 타이틀 커스텀 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    
    /* 메인 서브타이틀 커스텀 */
    .sub-title {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }

    /* 탭(Tab) 메뉴 디자인 깔끔하게 다듬기 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid #E2E8F0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        font-weight: 600;
        font-size: 1.05rem;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        padding: 0px 20px;
    }

    .stTabs [aria-selected="true"] {
        color: #2563EB !important;
        border-bottom: 2px solid #2563EB !important;
    }

    /* 카드 스타일 하이라이트 박스 */
    .info-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
    }
    
    /* 강조 뱃지 디자인 */
    .size-badge {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 1. Supabase 연동 설정
# -------------------------------------------------------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://your-supabase-url.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "your-anon-key")

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_supabase()

if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())

# -------------------------------------------------------------------
# 2. 사이드바 - 공통 신체 스펙 & 취향 입력
# -------------------------------------------------------------------
st.sidebar.header("📏 내 신체 스펙 입력")
gender = st.sidebar.radio("성별", ["남성", "여성"], horizontal=True)
height = st.sidebar.number_input("키 (cm)", min_value=140, max_value=210, value=175)
weight = st.sidebar.number_input("몸무게 (kg)", min_value=30, max_value=150, value=70)
waist_inch = st.sidebar.number_input("허리 둘레 (인치)", min_value=20, max_value=45, value=30)
foot_size = st.sidebar.number_input("발 사이즈 (mm)", min_value=210, max_value=320, value=265)

st.sidebar.divider()
st.sidebar.header("🎨 핏 & 무드 설정")
fit_style = st.sidebar.selectbox("선호하는 핏", ["레귤러핏", "오버핏/와이드핏", "슬림핏"])
user_mood = st.sidebar.text_input("원하는 무드", "스트릿, 시티보이, 미니멀 등").strip()

# -------------------------------------------------------------------
# 3. 메인 화면 헤더 영역
# -------------------------------------------------------------------
st.markdown('<div class="main-title">👕 AI 패션 스튜디오 & 커뮤니티</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">내 몸에 딱 맞는 핏을 3D로 확인하고, 패션 사람들과 착장 스타일을 나눠보세요.</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🧍 3D 피팅룸 & 맞춤 추천", "📸 패션 커뮤니티 피드"])

# ===================================================================
# TAB 1: 3D 피팅룸 및 맞춤 추천
# ===================================================================
with tab1:
    col_3d, col_rec = st.columns([1.2, 1])
    
    with col_3d:
        st.subheader("3D 핏 시뮬레이션")
        st.caption("🖱️ 마우스 드래그로 360도 회전하며 핏감을 자유롭게 확인하세요.")
        
        scale_y = height / 175.0
        scale_x = (weight / 70.0) ** 0.5
        fit_scale = 1.0 if fit_style == "레귤러핏" else (0.88 if fit_style == "슬림핏" else 1.18)

        three_js_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>body {{ margin: 0; overflow: hidden; background-color: #f8f9fa; }} canvas {{ width: 100vw; height: 100vh; }}</style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        </head>
        <body>
            <script>
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0xf8f9fa);
                const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(0, 1.2, 3.8);
                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                document.body.appendChild(renderer.domElement);
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;

                scene.add(new THREE.AmbientLight(0xffffff, 0.8));
                const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
                dirLight.position.set(2, 4, 3);
                scene.add(dirLight);

                const bodyGeo = new THREE.CylinderGeometry(0.2 * {scale_x}, 0.15 * {scale_x}, 1.6 * {scale_y}, 32);
                const bodyMat = new THREE.MeshStandardMaterial({{ color: 0xd1d5db }});
                const body = new THREE.Mesh(bodyGeo, bodyMat);
                body.position.y = (1.6 * {scale_y}) / 2;
                scene.add(body);

                const clothGeo = new THREE.CylinderGeometry(0.22 * {scale_x} * {fit_scale}, 0.2 * {scale_x} * {fit_scale}, 0.8 * {scale_y}, 32);
                const clothMat = new THREE.MeshStandardMaterial({{ color: 0x2563eb, roughness: 0.4 }});
                const cloth = new THREE.Mesh(clothGeo, clothMat);
                cloth.position.y = body.position.y + 0.2;
                scene.add(cloth);

                function animate() {{ requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }}
                animate();
            </script>
        </body>
        </html>
        """
        components.html(three_js_code, height=390)

    with col_rec:
        st.subheader("📊 맞춤 추천 사이즈")
        
        if gender == "남성":
            top_base = "M" if weight < 68 else ("L" if weight < 78 else "XL")
        else:
            top_base = "S" if weight < 52 else ("M" if weight < 60 else "L")
            
        pants_alpha = "S" if waist_inch <= 27 else ("M" if waist_inch <= 30 else ("L" if waist_inch <= 33 else "XL"))

        # 카드 형태 결과 박스
        st.markdown(f"""
            <div class="info-card">
                <b>📌 신체 스펙 기반 요약</b><br><br>
                • 권장 상의: <span class="size-badge">{top_base}</span><br>
                • 권장 바지: <span class="size-badge">{waist_inch}인치 ({pants_alpha})</span><br>
                • 권장 신발: <span class="size-badge">{foot_size} mm</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("##### 🏢 주요 브랜드별 추천")
        st.write(f"- **무신사 스탠다드:** 상의 `{top_base}` / 바지 `{waist_inch}인치`")
        st.write(f"- **유니클로:** 상의 `{top_base}` / 바지 `{waist_inch}인치`")
        st.write(f"- **자라 (ZARA):** 상의 `한 치수 작게` / 바지 `{max(26, waist_inch - 1)}인치`")
        
        st.divider()
        st.markdown("##### 💡 AI 무드 코디 추천")
        st.info(f"**{user_mood if user_mood else '캐주얼'} 무드:** 선택하신 핏감에 맞춰 와이드 카고 팬츠와 레이어드 티셔츠 스타일을 제안합니다.")

# ===================================================================
# TAB 2: 착샷 공유 커뮤니티 피드
# ===================================================================
with tab2:
    if not supabase:
        st.warning("Supabase 설정이 필요합니다. `.streamlit/secrets.toml`을 확인해 주세요.")
    else:
        with st.expander("📸 내 착샷 공유하기", expanded=False):
            with st.form("post_form", clear_on_submit=True):
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    nickname = st.text_input("닉네임", value="패셔니스타")
                    content = st.text_area("오늘의 스타일 설명")
                    uploaded_file = st.file_uploader("착용 사진 업로드", type=["jpg", "png", "jpeg"])
                with col_p2:
                    top_info = st.text_input("상의 정보", placeholder="예: 무신사 오버핏 셔츠 L")
                    bottom_info = st.text_input("하의 정보", placeholder="예: 자라 와이드 팬츠 30")
                    shoes_info = st.text_input("신발 정보", placeholder="예: 나이키 에어포스 270")

                if st.form_submit_button("피드에 올려 공유하기"):
                    if uploaded_file:
                        try:
                            file_bytes = uploaded_file.read()
                            file_path = f"posts/{uuid.uuid4()}.png"
                            supabase.storage.from_("fashion-images").upload(file_path, file_bytes)
                            img_url = supabase.storage.from_("fashion-images").get_public_url(file_path)

                            supabase.table("posts").insert({
                                "nickname": nickname,
                                "user_specs": f"{height}cm / {weight}kg",
                                "content": content,
                                "image_url": img_url,
                                "top_info": top_info,
                                "bottom_info": bottom_info,
                                "shoes_info": shoes_info
                            }).execute()
                            st.success("게시 완료!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"업로드 오류: {e}")

        st.divider()
        
        try:
            posts = supabase.table("posts").select("*").order("created_at", desc=True).execute().data
            for post in posts:
                post_id = post["id"]
                
                # 피드 카드 레이아웃
                st.markdown(f"**👤 {post['nickname']}** <span style='color:gray; font-size:0.9rem;'>({post.get('user_specs', '')})</span>", unsafe_allow_html=True)
                
                f_col1, f_col2 = st.columns([1, 1])
                with f_col1:
                    st.image(post["image_url"], use_container_width=True)
                with f_col2:
                    st.write(post["content"])
                    with st.expander("🏷️ 착장 옷 정보 보기", expanded=True):
                        st.write(f"👕 **상의:** {post.get('top_info', '정보 없음')}")
                        st.write(f"👖 **하의:** {post.get('bottom_info', '정보 없음')}")
                        st.write(f"👟 **신발:** {post.get('shoes_info', '정보 없음')}")

                    likes = post.get("likes_count", 0)
                    if st.button(f"❤️ {likes}", key=f"like_{post_id}"):
                        supabase.table("posts").update({"likes_count": likes + 1}).eq("id", post_id).execute()
                        st.rerun()
                st.divider()
        except:
            st.info("등록된 착샷 게시물이 없습니다. 첫 번째 착샷을 공유해 보세요!")
streamlit
supabase
three-js
