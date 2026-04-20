"""
手语乐园 - 学习区（带搜索功能）
功能：常用词快捷学习 + 搜索扩展词库
"""

import streamlit as st
import os

# ==================== 视频文件夹路径 ====================
VIDEO_DIR = "videos"

# ==================== 常用词库（显示在常用词标签页） ====================
COMMON_WORDS = {
    "👋 问候": ["你好", "谢谢", "对不起", "再见"],
    "👤 人称": ["我", "你", "他", "她"],
    "😊 情感": ["高兴", "伤心", "爱", "喜欢"],
    "🤝 日常": ["帮助", "是", "不是", "好"]
}

# ==================== 扩展词库（可通过搜索找到） ====================
EXTENDED_WORDS = {
    # 医疗类
    "医院": "医院", "医生": "医生", "护士": "护士", "药": "药",
    "挂号": "挂号", "发烧": "发烧", "咳嗽": "咳嗽", "疼痛": "疼痛",
    
    # 餐饮类
    "吃饭": "吃饭", "喝水": "喝水", "米饭": "米饭", "面条": "面条",
    "水果": "水果", "苹果": "苹果", "香蕉": "香蕉", "牛奶": "牛奶",
    
    # 交通类
    "公交": "公交", "地铁": "地铁", "出租车": "出租车", "火车站": "火车站",
    "飞机": "飞机", "汽车": "汽车", "自行车": "自行车", "走路": "走路",
    
    # 购物类
    "买": "买", "卖": "卖", "钱": "钱", "便宜": "便宜",
    "贵": "贵", "超市": "超市", "商场": "商场", "价格": "价格",
    
    # 时间类
    "今天": "今天", "明天": "明天", "昨天": "昨天", "现在": "现在",
    "早上": "早上", "晚上": "晚上", "下午": "下午", "星期": "星期",
    
    # 数量类
    "一": "一", "二": "二", "三": "三", "四": "四",
    "五": "五", "十": "十", "百": "百", "千": "千",
    
    # 家庭类
    "爸爸": "爸爸", "妈妈": "妈妈", "哥哥": "哥哥", "姐姐": "姐姐",
    "弟弟": "弟弟", "妹妹": "妹妹", "爷爷": "爷爷", "奶奶": "奶奶",
    
    # 工作类
    "工作": "工作", "学习": "学习", "老师": "老师", "学生": "学生",
    "公司": "公司", "学校": "学校", "办公室": "办公室", "教室": "教室",
    
    # 休闲类
    "唱歌": "唱歌", "跳舞": "跳舞", "电影": "电影", "音乐": "音乐",
    "运动": "运动", "跑步": "跑步", "游泳": "游泳", "游戏": "游戏",
    
    # 天气类
    "天气": "天气", "晴天": "晴天", "下雨": "下雨", "雪": "雪",
    "热": "热", "冷": "冷", "风": "风", "云": "云",
}

# 合并所有词库（用于搜索）
ALL_WORDS = {**COMMON_WORDS, **EXTENDED_WORDS}

# 将所有常用词展开为一维列表
COMMON_WORDS_LIST = []
for category, words in COMMON_WORDS.items():
    COMMON_WORDS_LIST.extend(words)

# ==================== 搜索函数 ====================
def search_words(keyword):
    """搜索手语词"""
    if not keyword:
        return []
    
    results = []
    
    # 遍历所有词库
    for word in ALL_WORDS.keys():
        if keyword in word:
            results.append(word)
    
    return results

# ==================== 学习区主函数 ====================
def learning_section():
    st.markdown('<h3 style="color:#3a5a6e;">🌱 习 · 手语单字</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b8a9e;">指尖轻触，静待花开</p >', unsafe_allow_html=True)
    # ... 其余代码不变
    
    # 初始化状态
    if "current_word" not in st.session_state:
        st.session_state.current_word = "你好"
    if "play_video" not in st.session_state:
        st.session_state.play_video = False
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "search_performed" not in st.session_state:
        st.session_state.search_performed = False
    
    # ==================== 创建两个标签页 ====================
    tab1, tab2 = st.tabs(["⭐ 常用词", "🔍 搜索词库"])
    
    # ==================== 标签页1：常用词 ====================
    with tab1:
        st.markdown("### 📖 分类学习")
        
        # 按分类显示按钮
        for category, words in COMMON_WORDS.items():
            st.markdown(f"**{category}**")
            cols = st.columns(4)
            for i, word in enumerate(words):
                with cols[i % 4]:
                    # 自定义按钮样式
                    button_key = f"common_{word}"
                    if st.button(word, key=button_key, use_container_width=True):
                        st.session_state.current_word = word
                        st.session_state.play_video = True
            st.markdown("")  # 空行
    
    # ==================== 标签页2：搜索 ====================
    with tab2:
        st.markdown("### 🔍 搜索手语词")
        st.markdown("输入关键词，搜索扩展词库中的手语词")
        
        # 搜索输入框
        search_term = st.text_input(
            "输入关键词",
            placeholder="例如：医院、医生、吃饭、苹果...",
            key="search_input",
            label_visibility="collapsed"
        )
        
        # 搜索按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            search_btn = st.button("🔍 搜索", use_container_width=True)
        
        if search_btn and search_term:
            results = search_words(search_term)
            st.session_state.search_results = results
            st.session_state.search_performed = True
        
        # 显示搜索结果
        if st.session_state.search_performed:
            if st.session_state.search_results:
                st.markdown(f"#### ✅ 找到 {len(st.session_state.search_results)} 个相关词汇：")
                
                # 每行显示4个按钮
                results = st.session_state.search_results
                for i in range(0, len(results), 4):
                    cols = st.columns(4)
                    for j in range(4):
                        if i + j < len(results):
                            word = results[i + j]
                            with cols[j]:
                                if st.button(word, key=f"search_{word}", use_container_width=True):
                                    st.session_state.current_word = word
                                    st.session_state.play_video = True
                                    # 播放后自动切换到常用词标签页
                                    st.session_state.switch_to_common = True
            else:
                st.warning(f"❌ 未找到包含「{search_term}」的词汇")
                st.markdown("""
                <div style="background: #f0f2f6; border-radius: 10px; padding: 1rem; margin-top: 1rem;">
                    <p>💡 <strong>提示：</strong></p>
                    <ul>
                        <li>尝试输入更短的关键词（如「医」而不是「医院」）</li>
                        <li>检查是否有对应的视频文件放入 videos 文件夹</li>
                        <li>可以在代码的 EXTENDED_WORDS 中添加新词</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        # 显示热门搜索建议
        with st.expander("🔥 热门搜索推荐"):
            st.markdown("""
            | 类别 | 推荐搜索词 |
            |------|-----------|
            | 🏥 医疗 | 医院、医生、护士、药 |
            | 🍜 餐饮 | 吃饭、喝水、水果、米饭 |
            | 🚗 交通 | 公交、地铁、出租车、飞机 |
            | 🛒 购物 | 买、卖、钱、便宜 |
            | ⏰ 时间 | 今天、明天、现在、早上 |
            | 👨‍👩‍👧 家庭 | 爸爸、妈妈、哥哥、姐姐 |
            | 💼 工作 | 工作、学习、老师、学生 |
            | 🎵 休闲 | 唱歌、跳舞、音乐、电影 |
            """)
    
    st.markdown("---")
    
    # ==================== 视频播放区域 ====================
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <h3>🤟 当前学习：{st.session_state.current_word}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    video_path = os.path.join(VIDEO_DIR, f"{st.session_state.current_word}.mp4")
    
    if st.session_state.play_video:
        if os.path.exists(video_path):
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            st.video(video_path)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ 视频不存在：{st.session_state.current_word}.mp4")
            st.info("💡 提示：请将视频文件放入 videos 文件夹，或自己拍摄后放入")
        st.session_state.play_video = False
    else:
        if os.path.exists(video_path):
            if st.button("▶ 播放视频", use_container_width=True):
                st.video(video_path)
        else:
            st.info(f"📹 点击上方按钮，学习「{st.session_state.current_word}」的手语")
            

# 获取所有词库（供外部使用）
def get_all_words():
    """返回所有词库"""
    return ALL_WORDS

# 测试用
if __name__ == "__main__":
    st.set_page_config(page_title="手语学习", page_icon="📚")
    learning_section()