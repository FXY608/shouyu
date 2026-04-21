"""
手语乐园 - 兴趣区
界面完全不变 | 视频合成功能保留 | 代码重写
"""
import streamlit as st
import os
import tempfile
import time

MOVIEPY_OK = False
try:
    from moviepy import VideoFileClip, concatenate_videoclips
    MOVIEPY_OK = True
except:
    pass

VIDEO_DIR = "videos"
AUDIO_DIR = "temp_audio"

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def text_to_video_clip(text):
    if not MOVIEPY_OK:
        return None
    words = text.split()
    if len(words) == 0:
        words = [text]
    video_paths = []
    for word in words:
        word = word.strip()
        if not word:
            continue
        path = os.path.join(VIDEO_DIR, f"{word}.mp4")
        if os.path.exists(path):
            video_paths.append(path)
    if not video_paths:
        return None
    clips = []
    for path in video_paths:
        try:
            clip = VideoFileClip(path)
            clips.append(clip)
        except Exception as e:
            st.warning(f"加载视频失败 {path}: {e}")
    if not clips:
        return None
    if len(clips) == 1:
        return clips[0]
    else:
        return concatenate_videoclips(clips)

def generate_sign_dance_video(lyrics_lines, progress_callback=None):
    if not MOVIEPY_OK:
        return None, "moviepy 未安装"
    video_clips = []
    failed_lines = []
    for i, line in enumerate(lyrics_lines):
        if progress_callback:
            progress_callback(i, len(lyrics_lines), f"🎬 处理第 {i+1}/{len(lyrics_lines)} 句: {line[:20]}...")
        clip = text_to_video_clip(line)
        if clip:
            video_clips.append(clip)
        else:
            failed_lines.append(line)
    if not video_clips:
        return None, "没有生成任何视频片段"
    if len(video_clips) == 1:
        final_video = video_clips[0]
    else:
        final_video = concatenate_videoclips(video_clips)
    try:
        temp_filename = f"shouyu_temp_{int(time.time())}.mp4"
        temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
        final_video.write_videofile(
            temp_path, 
            codec='libx264', 
            audio_codec='aac',
            verbose=False,
            logger=None
        )
    except Exception as e:
        return None, f"保存失败: {e}"
    final_video.close()
    for clip in video_clips:
        clip.close()
    return temp_path, failed_lines

def interest_section():
    st.markdown('<h3 style="color:#3a5a6e;">🎵 创 · 手语舞</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b8a9e;">上传音乐，让手语随旋律绽放</p>', unsafe_allow_html=True)

    if not MOVIEPY_OK:
        st.error("❌ moviepy 未正确安装")
        st.code("请运行: pip install moviepy==1.0.3", language="bash")
        return

    if not os.path.exists(VIDEO_DIR):
        st.error("❌ videos 文件夹不存在")
        return

    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')]
    if not video_files:
        st.warning("⚠️ videos 文件夹为空")
        return

    st.success(f"✅ 已加载 {len(video_files)} 个手语视频")
    st.markdown("---")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 20px; padding: 1rem; margin: 1rem 0;">
        <h3>🎵 第一步：上传音乐</h3>
    </div>
    """, unsafe_allow_html=True)

    uploaded_audio = st.file_uploader(
        "选择音乐文件",
        type=["mp3", "wav", "m4a"],
        help="支持 MP3、WAV、M4A 格式",
        key="audio_upload"
    )

    audio_path = None
    audio_filename = None
    if uploaded_audio is not None:
        audio_filename = uploaded_audio.name
        audio_save_path = os.path.join(AUDIO_DIR, audio_filename)
        with open(audio_save_path, "wb") as f:
            f.write(uploaded_audio.getbuffer())
        audio_path = audio_save_path
        st.success(f"✅ 已上传：{audio_filename}")

    st.markdown("---")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 20px; padding: 1rem; margin: 1rem 0;">
        <h3>📝 第二步：输入歌词</h3>
        <p>每句一行，系统会根据歌词自动匹配手语视频</p>
    </div>
    """, unsafe_allow_html=True)

    example_lyrics = """你好
谢谢
我爱你"""
    lyrics = st.text_area(
        "歌词内容",
        height=150,
        value=example_lyrics,
        placeholder="你好\n谢谢\n我爱你",
        key="lyrics_input"
    )

    st.markdown("---")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 20px; padding: 1rem; margin: 1rem 0;">
        <h3>🎬 第三步：生成手语舞</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🎬 生成手语舞视频", use_container_width=True, type="primary")

    if "generated_video_path" not in st.session_state:
        st.session_state.generated_video_path = None

    if generate_btn:
        if not lyrics.strip():
            st.warning("请输入歌词")
        elif audio_path is None:
            st.warning("请先上传音乐文件")
        else:
            lines = [l.strip() for l in lyrics.split("\n") if l.strip()]
            progress_bar = st.progress(0, text="准备生成...")
            status_text = st.empty()
            def update_progress(current, total, message):
                if total > 0:
                    progress_bar.progress(current / total, text=message)
                status_text.text(message)
            video_path, failed_lines = generate_sign_dance_video(lines, update_progress)
            progress_bar.empty()
            status_text.empty()
            if video_path:
                st.session_state.generated_video_path = video_path
                st.success("✅ 手语舞视频生成成功！")
            else:
                st.error(f"生成失败：请检查视频素材")

    if st.session_state.generated_video_path and os.path.exists(st.session_state.generated_video_path):
        st.markdown("---")
        st.video(st.session_state.generated_video_path)
        with open(st.session_state.generated_video_path, "rb") as f:
            st.download_button(
                label="📥 下载手语舞视频",
                data=f,
                file_name="shouyu_dance.mp4",
                mime="video/mp4",
                use_container_width=True
            )

if __name__ == "__main__":
    st.set_page_config(page_title="手语舞", page_icon="🎵")
    interest_section()
