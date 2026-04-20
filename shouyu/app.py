"""
手语乐园 - 最终完整版
功能：学习区 + 兴趣区（手语舞）
视觉：浅绿色底 + 4色块切割 + 20片飘落树叶 + 点击开花
"""

import streamlit as st
from learning import learning_section
from interest import interest_section
import streamlit.components.v1 as components

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="手语乐园 | 用手语传递爱与温暖",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS 样式 ====================
st.markdown("""
<style>
    /* 背景 - 浅绿色底 */
    .stApp {
        background: #e8f5e9;
    }
    
    /* 标题区域 */
    .main-title {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
    }
    .main-title h1 {
        font-size: 3rem;
        color: #2d4a2d;
        margin: 0;
        letter-spacing: 0.05em;
    }
    .main-title p {
        font-size: 1rem;
        color: #4a6e4a;
        margin-top: 0.5rem;
    }
    
    /* 白色卡片 - 毛玻璃效果 */
    .choice-card {
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(4px);
        border-radius: 28px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        margin: 0.5rem;
        border: 1px solid rgba(255,255,255,0.5);
    }
    .choice-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.98);
        box-shadow: 0 15px 35px rgba(0,0,0,0.12);
    }
    .choice-card h2 {
        color: #2d4a2d;
        font-size: 2rem;
        margin: 0 0 0.5rem 0;
    }
    .choice-card p {
        color: #5a6e5a;
        font-size: 1rem;
        margin: 0;
        line-height: 1.5;
    }
    .choice-card .emoji {
        font-size: 2.5rem;
        margin-top: 0.8rem;
        display: block;
    }
    
    /* 内容卡片 */
    .content-card {
        background: rgba(255, 255, 255, 0.94);
        backdrop-filter: blur(4px);
        border-radius: 28px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.5);
    }
    
    /* 按钮样式 */
    .stButton button {
        background: linear-gradient(135deg, #f5f5dc 0%, #e8e0c8 100%);
        color: #2d4a2d;
        border-radius: 40px;
        border: none;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #ffffe0 0%, #f0e8d0 100%);
        transform: scale(0.98);
    }
    
    /* 返回按钮 */
    .back-btn {
        margin-bottom: 1rem;
    }
    
    /* 页脚 */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        color: #4a6e4a;
        font-size: 0.8rem;
        border-top: 1px solid rgba(0,0,0,0.06);
    }
    
    /* 隐藏默认的Streamlit菜单 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== 背景：4色块切割 ====================
st.markdown("""
<div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 0; pointer-events: none;">
    <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <!-- 整体浅绿色背景 -->
        <rect x="0" y="0" width="100%" height="100%" fill="#e8f5e9"/>
        <!-- 左上色块 -->
        <rect x="0" y="0" width="50%" height="50%" fill="#c8e6c9" opacity="0.85"/>
        <!-- 右上色块 -->
        <rect x="50%" y="0" width="50%" height="50%" fill="#a5d6a7" opacity="0.85"/>
        <!-- 左下色块 -->
        <rect x="0" y="50%" width="50%" height="50%" fill="#81c784" opacity="0.85"/>
        <!-- 右下色块 -->
        <rect x="50%" y="50%" width="50%" height="50%" fill="#66bb6a" opacity="0.85"/>
        <!-- 白色切割线 -->
        <line x1="50%" y1="0" x2="50%" y2="100%" stroke="white" stroke-width="3.5"/>
        <line x1="0" y1="50%" x2="100%" y2="50%" stroke="white" stroke-width="3.5"/>
    </svg>
</div>
""", unsafe_allow_html=True)

# ==================== 飘落树叶（20片） ====================
st.markdown("""
<style>
    @keyframes fall {
        0% { top: -10%; opacity: 0.8; transform: rotate(0deg);}
        100% { top: 110%; opacity: 0; transform: rotate(360deg);}
    }
    
    .falling-leaf {
        position: fixed;
        top: -10%;
        animation: fall linear infinite;
        pointer-events: none;
        z-index: 999;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .falling-leaf:nth-child(1) { left: 3%; animation-duration: 14s; animation-delay: 0s; font-size: 1.2rem; color: #2e7d32; }
    .falling-leaf:nth-child(2) { left: 8%; animation-duration: 19s; animation-delay: 3s; font-size: 0.9rem; color: #388e3c; }
    .falling-leaf:nth-child(3) { left: 13%; animation-duration: 11s; animation-delay: 1s; font-size: 1.5rem; color: #43a047; }
    .falling-leaf:nth-child(4) { left: 18%; animation-duration: 17s; animation-delay: 5s; font-size: 1.0rem; color: #4caf50; }
    .falling-leaf:nth-child(5) { left: 23%; animation-duration: 13s; animation-delay: 2s; font-size: 1.4rem; color: #66bb6a; }
    .falling-leaf:nth-child(6) { left: 28%; animation-duration: 20s; animation-delay: 4s; font-size: 1.1rem; color: #81c784; }
    .falling-leaf:nth-child(7) { left: 33%; animation-duration: 15s; animation-delay: 1.5s; font-size: 1.6rem; color: #2e7d32; }
    .falling-leaf:nth-child(8) { left: 38%; animation-duration: 12s; animation-delay: 6s; font-size: 0.8rem; color: #388e3c; }
    .falling-leaf:nth-child(9) { left: 43%; animation-duration: 18s; animation-delay: 2.5s; font-size: 1.3rem; color: #43a047; }
    .falling-leaf:nth-child(10) { left: 48%; animation-duration: 16s; animation-delay: 3.5s; font-size: 1.7rem; color: #4caf50; }
    .falling-leaf:nth-child(11) { left: 53%; animation-duration: 14s; animation-delay: 1.8s; font-size: 1.0rem; color: #66bb6a; }
    .falling-leaf:nth-child(12) { left: 58%; animation-duration: 21s; animation-delay: 4.5s; font-size: 1.2rem; color: #81c784; }
    .falling-leaf:nth-child(13) { left: 63%; animation-duration: 11s; animation-delay: 0.8s; font-size: 1.5rem; color: #2e7d32; }
    .falling-leaf:nth-child(14) { left: 68%; animation-duration: 19s; animation-delay: 5.5s; font-size: 0.9rem; color: #388e3c; }
    .falling-leaf:nth-child(15) { left: 73%; animation-duration: 13s; animation-delay: 2.2s; font-size: 1.4rem; color: #43a047; }
    .falling-leaf:nth-child(16) { left: 78%; animation-duration: 17s; animation-delay: 3.8s; font-size: 1.1rem; color: #4caf50; }
    .falling-leaf:nth-child(17) { left: 83%; animation-duration: 15s; animation-delay: 1.2s; font-size: 1.6rem; color: #66bb6a; }
    .falling-leaf:nth-child(18) { left: 88%; animation-duration: 12s; animation-delay: 4.2s; font-size: 0.8rem; color: #81c784; }
    .falling-leaf:nth-child(19) { left: 93%; animation-duration: 18s; animation-delay: 2.8s; font-size: 1.3rem; color: #2e7d32; }
    .falling-leaf:nth-child(20) { left: 98%; animation-duration: 20s; animation-delay: 3.2s; font-size: 1.0rem; color: #388e3c; }
</style>

<div class="falling-leaf">🍃</div>
<div class="falling-leaf">🍂</div>
<div class="falling-leaf">🌿</div>
<div class="falling-leaf">🍃</div>
<div class="falling-leaf">🍂</div>
<div class="falling-leaf">🍃</div>
<div class="falling-leaf">🌿</div>
<div class="falling-leaf">🍂</div>
<div class="falling-leaf">🍃</div>
<div class="falling-leaf">🍂</div>
<div class="falling-leaf">🌿</div>
<div class="falling-leaf">🍃</div>
<div class="falling-leaf">🍂</div>
<div class="falling-leaf">🍃</div>
<div class="falling-leaf">🌿</div>
<div class="falling-leaf">🍂</div>
<div class="falling-leaf">🍃</div>
<div class="falling-leaf">🍂</div>
<div class="falling-leaf">🌿</div>
<div class="falling-leaf">🍃</div>
""", unsafe_allow_html=True)

# ==================== 点击开花特效 ====================
components.html("""
<script>
document.addEventListener('click', function(e) {
    // 避免在按钮上重复触发
    if(e.target.tagName === 'BUTTON' || e.target.closest('button')) return;
    
    const leaves = ['🍃', '🍂', '🌿'];
    const leaf = document.createElement('div');
    leaf.innerText = leaves[Math.floor(Math.random() * leaves.length)];
    leaf.style.position = 'fixed';
    leaf.style.left = (e.clientX - 15) + 'px';
    leaf.style.top = (e.clientY - 15) + 'px';
    leaf.style.fontSize = '1.8rem';
    leaf.style.opacity = '1';
    leaf.style.transition = 'all 0.8s cubic-bezier(0.2, 0.9, 0.4, 1.1)';
    leaf.style.pointerEvents = 'none';
    leaf.style.zIndex = '10000';
    leaf.style.filter = 'drop-shadow(0 2px 6px rgba(0,0,0,0.2))';
    document.body.appendChild(leaf);
    
    setTimeout(() => {
        leaf.style.opacity = '0';
        leaf.style.transform = 'translateY(-50px) rotate(30deg) scale(1.2)';
    }, 20);
    setTimeout(() => {
        leaf.remove();
    }, 800);
});
</script>
""", height=0)

# ==================== 状态管理 ====================
if "start" not in st.session_state:
    st.session_state.start = False
if "mode" not in st.session_state:
    st.session_state.mode = None

# ==================== 开场动画 ====================
if not st.session_state.start:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-top: 30vh;">
            <h1 style="font-size: 4rem; color:#2d4a2d; margin: 0;">🍃 手语乐园</h1>
            <p style="font-size: 1.2rem; color:#4a6e4a; margin-top: 1rem;">用手语，传递爱与温暖</p >
            <div style="margin-top: 3rem;">
                <div style="display: inline-block; padding: 0.5rem 2rem; background: rgba(255,255,255,0.8); border-radius: 50px; color: #2d4a2d;">
                    🍃 点击下方按钮开始 🍂
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("🍃 进入森林", use_container_width=True):
                st.session_state.start = True
                st.rerun()
    st.stop()

# ==================== 选择区 ====================
if st.session_state.mode is None:
    st.markdown('<div class="main-title"><h1>🍃 手语乐园</h1><p>选择你想去的地方</p ></div>', unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2, gap="large")
    
    with col_left:
        st.markdown("""
        <div class="choice-card">
            <h2>📚 学习区</h2>
            <p>学习手语单字<br>从基础开始，掌握日常手语</p >
            <span class="emoji">🍃</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入学习区", key="go_learning", use_container_width=True):
            st.session_state.mode = "learning"
            st.rerun()
    
    with col_right:
        st.markdown("""
        <div class="choice-card">
            <h2>🎵 兴趣区</h2>
            <p>手语舞工坊<br>上传音乐，生成手语舞视频</p >
            <span class="emoji">🍂</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入兴趣区", key="go_interest", use_container_width=True):
            st.session_state.mode = "interest"
            st.rerun()
    
    st.stop()

# ==================== 学习区模式 ====================
if st.session_state.mode == "learning":
    col1, col2, col3 = st.columns([1, 10, 1])
    with col1:
        if st.button("← 返回", key="back_learning", use_container_width=True):
            st.session_state.mode = None
            st.rerun()
    
    st.markdown('<div class="main-title"><h1>📚 学习区</h1><p>指尖轻触，如叶飘落</p ></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    learning_section()
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 兴趣区模式 ====================
elif st.session_state.mode == "interest":
    col1, col2, col3 = st.columns([1, 10, 1])
    with col1:
        if st.button("← 返回", key="back_interest", use_container_width=True):
            st.session_state.mode = None
            st.rerun()
    
    st.markdown('<div class="main-title"><h1>🎵 兴趣区</h1><p>让手语随风起舞</p ></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    interest_section()
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 页脚 ====================
st.markdown('<div class="footer">🍃 用手语，传递爱与温暖 | 让沟通无障碍，让世界更美好</div>', unsafe_allow_html=True)