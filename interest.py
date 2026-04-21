"""
手语乐园 - 兴趣区（手语舞）【已修复报错版】
"""

import streamlit as st
import os
import tempfile
import time
import traceback

# 导入 moviepy（修复重复导入问题）
try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
    MOVIEPY_OK = True
except ImportError:
    MOVIEPY_OK = False

# 配置路径
VIDEO_DIR = "videos"
AUDIO_DIR = "temp_audio"

# 创建文件夹
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

def text_to_video_clip(text):
    """把一句话转成手语视频片段（无声）"""
    if not MOVIEPY_OK:
        return None

    words = text.split()
    if not words:
        return None

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
            st.warning(f"加载视频失败 {path}: {str(e)}")

    if not clips:
        return None

    try:
        final_clip = concatenate_videoclips(clips, method="compose")
        return final_clip
    except Exception as e:
        for c in clips:
            c.close()
        return None

def generate_sign_dance_video(lyrics_lines, audio_path, progress_callback=None):
    """生成带音乐的手语舞视频（核心修复）"""
    if not MOVIEPY_OK:
        return None, "moviepy 未安装"

    video_clips = []
    failed_lines = []

    # 拼接歌词视频
    for i, line in enumerate(lyrics_lines):
        if progress_callback:
            progress_callback(i, len(lyrics_lines), f"🎬 处理第 {i+1}/{len(lyrics_lines)} 句")
        
        clip = text_to_video_clip(line)
        if clip:
            video_clips.append(clip)
        else:
            failed_lines.append(line)

    if not video_clips:
        return None, "没有匹配到手语视频"

    # 合并视频片段
    try:
        final_video = concatenate_videoclips(video_clips, method="compose")
    except Exception as e:
        for c in video_clips:
            c.close()
        return None, f"视频合并失败：{str(e)}"

    # 添加背景音乐（核心修复）
    try:
        audio_clip = AudioFileClip(audio_path)
        video_duration = final_video.duration
        audio_duration = audio_clip.duration

        # 音乐长度适配
        if audio_duration > video_duration:
            audio_clip = audio_clip.subclip(0, video_duration)
        final_video = final_video.set_audio(audio_clip)
    except Exception as e:
        st.warning(f"背景音乐添加失败：{str(e)}")

    # 保存最终视频（稳定版）
    try:
        temp_path = tempfile.mktemp(suffix=".mp4")
        final_video.write_videofile(
            temp_path,
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            verbose=False,
            logger=None
        )

        # 关闭所有资源，避免占用
        final_video.close()
        audio_clip.close()
        for clip in video_clips:
            clip.close()

        return temp_path, failed_lines

    except Exception as e:
        try:
            final_video.close()
            audio_clip.close()
        except:
            pass
        return None, f"视频保存失败：{str(e)}"

def interest_section():
    st.markdown('<h3 style="color:#3a5a6e;">🎵 创 · 手语舞</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b8a9e;">上传音乐，让手语随旋律绽放</p>', unsafe_allow_html=True)

    # 依赖检查
    if not MOVIEPY_OK:
        st.error("❌ 请安装依赖：pip install moviepy")
        return

    # 素材检查
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')]
    if not video_files:
        st.warning("⚠️ videos 文件夹为空，请放入 单词.mp4 格式的手语视频")
        return
    st.success(f"✅ 已加载 {len(video_files)} 个手语视频")

    st.markdown("---")

    # ==================== 第一步：上传音乐 ====================
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 20px; padding: 1rem; margin: 1rem 0;">
        <h3>🎵 第一步：上传音乐</h3>
    </div>
    """, unsafe_allow_html=True)

    uploaded_audio = st.file_uploader(
        "选择音乐文件", type=["mp3", "wav", "m4a"], key="audio_upload"
    )
    audio_path = None
    if uploaded_audio is not None:
        audio_path = os.path.join(AUDIO_DIR, uploaded_audio.name)
        with open(audio_path, "wb") as f:
            f.write(uploaded_audio.getbuffer())
        st.success(f"✅ 已上传：{uploaded_audio.name}")
        st.audio(audio_path)

    st.markdown("---")

    # ==================== 第二步：输入歌词 ====================
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 20px; padding: 1rem; margin: 1rem 0;">
        <h3>📝 第二步：输入歌词（每行一句）</h3>
    </div>
    """, unsafe_allow_html=True)

    lyrics = st.text_area(
        "歌词内容", height=150, value="你好\n谢谢\n我爱你", key="lyrics_input"
    )

    # 检查缺失视频
    if lyrics.strip():
        lines = [l.strip() for l in lyrics.splitlines() if l.strip()]
        all_words = set()
        for line in lines:
            all_words.update(line.split())
        
        missing = [w for w in all_words if not os.path.exists(os.path.join(VIDEO_DIR, f"{w}.mp4"))]
        if missing:
            with st.expander("⚠️ 缺少视频文件"):
                st.write(", ".join([f"{w}.mp4" for w in missing]))

    st.markdown("---")

    # ==================== 第三步：生成 ====================
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 20px; padding: 1rem; margin: 1rem 0;">
        <h3>🎬 第三步：生成手语舞</h3>
    </div>
    """, unsafe_allow_html=True)

    if "generated_video" not in st.session_state:
        st.session_state.generated_video = None

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🎬 生成带音乐的手语舞", use_container_width=True, type="primary")

    if generate_btn:
        if not audio_path:
            st.warning("请先上传音乐！")
        elif not lyrics.strip():
            st.warning("请输入歌词！")
        else:
            lines = [l.strip() for l in lyrics.splitlines() if l.strip()]
            if not lines:
                st.warning("歌词不能为空行")
            else:
                # 进度条
                progress_bar = st.progress(0)
                status = st.empty()

                def update_progress(cur, total, msg):
                    progress_bar.progress(cur / total)
                    status.text(msg)

                # 生成
                video_path, failed = generate_sign_dance_video(lines, audio_path, update_progress)
                progress_bar.empty()
                status.empty()

                if video_path and os.path.exists(video_path):
                    st.session_state.generated_video = video_path
                    st.success("✅ 视频生成成功！")
                    if failed:
                        st.warning(f"⚠️ 未匹配：{', '.join(failed)}")
                else:
                    st.error(f"❌ 生成失败：{failed}")

    # ==================== 展示结果 ====================
    if st.session_state.generated_video and os.path.exists(st.session_state.generated_video):
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); border-radius: 20px; padding: 1rem; text-align:center;">
            <h3>🎬 你的手语舞</h3>
        </div>
        """, unsafe_allow_html=True)

        st.video(st.session_state.generated_video)

        # 下载
        with open(st.session_state.generated_video, "rb") as f:
            st.download_button(
                "📥 下载手语舞视频",
                data=f,
                file_name="手语舞.mp4",
                mime="video/mp4",
                use_container_width=True
            )

# 测试运行
if __name__ == "__main__":
    st.set_page_config(page_title="手语舞工坊", page_icon="🎵", layout="wide")
    interest_section()
