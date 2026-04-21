"""
手语乐园 - 学习区
界面完全不变 | 功能完整保留 | 代码重写
"""
import streamlit as st
import os

VIDEO_DIR = "videos"

COMMON_WORDS = {
    "👋 问候": ["你好", "谢谢", "对不起", "再见"],
    "👤 人称": ["我", "你", "他", "她"],
    "😊 情感": ["高兴", "伤心", "爱", "喜欢"],
    "🤝 日常": ["帮助", "是", "不是", "好"]
}

EXTENDED_WORDS = {
    "医院": "医院", "医生": "医生", "护士": "护士", "药": "药",
    "挂号": "挂号", "发烧": "发烧", "咳嗽": "咳嗽", "疼痛": "疼痛",
    "吃饭": "吃饭", "喝水": "喝水", "米饭": "米饭", "面条": "面条",
    "水果": "水果", "苹果": "苹果", "香蕉": "香蕉", "牛奶": "牛奶",
    "公交": "公交", "地铁": "地铁", "出租车": "出租车", "火车站": "火车站",
    "飞机": "飞机", "汽车": "汽车", "自行车": "自行车", "走路": "走路",
    "买": "买", "卖": "卖", "钱": "钱", "便宜": "便宜",
    "贵": "贵", "超市": "超市", "商场": "商场", "价格": "价格",
    "今天": "今天", "明天": "明天", "昨天": "昨天", "现在": "现在",
    "早上": "早上", "晚上": "晚上", "下午": "下午", "星期": "星期",
    "一": "一", "二": "二", "三": "三", "四": "四",
    "五": "五", "十": "十", "百": "百", "千": "千",
    "爸爸": "爸爸", "妈妈": "妈妈", "哥哥": "哥哥", "姐姐": "姐姐",
    "弟弟": "弟弟", "妹妹": "妹妹", "爷爷": "爷爷", "奶奶": "奶奶",
    "工作": "工作", "学习": "学习", "老师": "老师", "学生": "学生",
    "公司": "公司", "学校": "学校", "办公室": "办公室", "教室": "教室",
    "唱歌": "唱歌", "跳舞": "跳舞", "电影": "电影", "音乐": "音乐",
    "运动": "运动", "跑步": "跑步", "游泳": "游泳", "游戏": "游戏",
    "天气": "天气", "晴天": "晴天", "下雨": "下雨", "雪": "雪",
    "热": "热", "冷": "冷", "风": "风", "云": "云",
}

ALL_WORDS = {}
for cate, wlist in COMMON_WORDS.items():
    for w in wlist:
        ALL_WORDS[w] = w
ALL_WORDS.update(EXTENDED_WORDS)

def search_words(keyword):
    if not keyword:
        return []
    res = []
    for word in ALL_WORDS:
        if keyword in word:
            res.append(word)
    return res

def learning_section():
    st.markdown('<h3 style="color:#3a5a6e;">🌱 习 · 手语单字</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b8a9e;">指尖轻触，静待花开</p>', unsafe_allow_html=True)

    if "current_word" not in st.session_state:
        st.session_state.current_word = "你好"
    if "play_video" not in st.session_state:
        st.session_state.play_video = False
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "search_performed" not in st.session_state:
        st.session_state.search_performed = False

    tab1, tab2 = st.tabs(["⭐ 常用词", "🔍 搜索词库"])

    with tab1:
        st.markdown("### 📖 分类学习")
        for category, words in COMMON_WORDS.items():
            st.markdown(f"**{category}**")
            cols = st.columns(4)
            for i, word in enumerate(words):
                with cols[i % 4]:
                    if st.button(word, key=f"common_{word}", use_container_width=True):
                        st.session_state.current_word = word
                        st.session_state.play_video = True
            st.markdown("")

    with tab2:
        st.markdown("### 🔍 搜索手语词")
        st.markdown("输入关键词，搜索扩展词库中的手语词")
        search_term = st.text_input(
            "输入关键词",
            placeholder="例如：医院、医生、吃饭、苹果...",
            key="search_input",
            label_visibility="collapsed"
        )
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            search_btn = st.button("🔍 搜索", use_container_width=True)
        if search_btn and search_term:
            results = search_words(search_term)
            st.session_state.search_results = results
            st.session_state.search_performed = True

        if st.session_state.search_performed:
            if st.session_state.search_results:
                st.markdown(f"#### ✅ 找到 {len(st.session_state.search_results)} 个相关词汇：")
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
            else:
                st.warning(f"❌ 未找到包含「{search_term}」的词汇")

    st.markdown("---")

    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <h3>🤟 当前学习：{st.session_state.current_word}</h3>
    </div>
    """, unsafe_allow_html=True)

    video_path = os.path.join(VIDEO_DIR, f"{st.session_state.current_word}.mp4")

    if st.session_state.play_video:
        if os.path.exists(video_path):
            st.video(video_path)
        else:
            st.warning(f"⚠️ 视频不存在：{st.session_state.current_word}.mp4")
        st.session_state.play_video = False
    else:
        if os.path.exists(video_path):
            if st.button("▶ 播放视频", use_container_width=True):
                st.video(video_path)
        else:
            st.info(f"📹 点击上方按钮，学习「{st.session_state.current_word}」的手语")

if __name__ == "__main__":
    st.set_page_config(page_title="手语学习", page_icon="📚")
    learning_section()
