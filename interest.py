"""
手语乐园 - 兴趣区（手语舞）
"""

import streamlit as st
import os
import tempfile
import time

# 导入 moviepy
try:
    from moviepy import VideoFileClip, concatenate_videoclips
    MOVIEPY_OK = True
except ImportError:
    try:
        from moviepy import VideoFileClip, concatenate_videoclips
        MOVIEPY_OK = True
    except ImportError:
        MOVIEPY_OK = False

# 配置路径
VIDEO_DIR = "videos"
AUDIO_DIR = "temp_audio"

# 创建临时音频文件夹
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def text_to_video_clip(text):
    """把一句话转成手语视频片段（无声）"""
    
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
    """生成手语舞视频（无声）"""
    
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
    
    # 修复FFMPEG错误：使用更稳定的保存方式
    try:
        # 使用带时间戳的文件名，避免冲突
        temp_filename = f"shouyu_temp_{int(time.time())}.mp4"
        temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
        
        # 写入视频文件，指定编码器
        final_video.write_videofile(
            temp_path, 
            codec='libx264', 
            audio_codec='aac',
            verbose=False,
            logger=None
        )
    except Exception as e:
        # 如果失败，尝试更简单的方式
        try:
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            final_video.write_videofile(temp_path)
        except Exception as e2:
            final_video.close()
            for clip in video_clips:
                clip.close()
            return None, f"保存失败: {e2}"
    
    final_video.close()
    for clip in video_clips:
        clip.close()
    
    return temp_path, failed_lines

def interest_section():
    st.markdown('<h3 style="color:#3a5a6e;">🎵 创 · 手语舞</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b8a9e;">上传音乐，让手语随旋律绽放</p >', unsafe_allow_html=True)
    # ... 其余代码不变
    
    if not MOVIEPY_OK:
        st.error("❌ moviepy 未正确安装")
        st.code("请运行: pip install moviepy==1.0.3", language="bash")
        return
    
    if not os.path.exists(VIDEO_DIR):
        st.error("❌ videos 文件夹不存在")
        st.info("请在项目文件夹中创建 videos 文件夹，并放入手语视频文件")
        return
    
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')]
    if not video_files:
        st.warning("⚠️ videos 文件夹为空")
        st.info("请放入手语视频文件，如：你好.mp4、谢谢.mp4")
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
    
    # ==================== 第二步：输入歌词 ====================
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
        help="每句歌词占一行，确保 videos 文件夹中有对应的视频文件",
        key="lyrics_input"
    )
    
    if lyrics.strip():
        lines = [l.strip() for l in lyrics.split("\n") if l.strip()]
        st.caption(f"📊 共 {len(lines)} 句歌词")
        
        all_words = set()
        for line in lines:
            for word in line.split():
                all_words.add(word.strip())
        
        missing_videos = []
        for word in all_words:
            if word and not os.path.exists(os.path.join(VIDEO_DIR, f"{word}.mp4")):
                missing_videos.append(word)
        
        if missing_videos:
            with st.expander("⚠️ 缺少以下视频文件"):
                for word in missing_videos:
                    st.write(f"• {word}.mp4")
                st.info("请将对应的视频文件放入 videos 文件夹")
    
    st.markdown("---")
    
    # ==================== 第三步：生成 ====================
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
            
            if not lines:
                st.warning("歌词不能为空")
            else:
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
                    
                    if failed_lines:
                        st.warning(f"⚠️ 以下句子处理失败：{', '.join(failed_lines)}")
                else:
                    st.error(f"生成失败：{failed_lines if isinstance(failed_lines, str) else '请检查视频素材'}")
    
    # ==================== 显示结果 ====================
    if st.session_state.generated_video_path and os.path.exists(st.session_state.generated_video_path):
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); border-radius: 20px; padding: 1rem; margin: 1rem 0;">
            <h3 style="text-align: center;">🎬 生成结果</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 手语舞视频
        st.video(st.session_state.generated_video_path)
        
        # 下载按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with open(st.session_state.generated_video_path, "rb") as f:
                st.download_button(
                    label="📥 下载手语舞视频",
                    data=f,
                    file_name="shouyu_dance.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
        
        # 音乐试听区
        if audio_path and os.path.exists(audio_path):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fa709a30 0%, #fee14030 100%); border-radius: 20px; padding: 1rem; margin: 1rem 0;">
                <h3 style="text-align: center;">🎵 音乐试听</h3>
                <p style="text-align: center;">边听音乐边看手语舞，跟着节奏学习</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 音乐播放器
            st.audio(audio_path, format="audio/mp3")
            
            try:
                from moviepy import AudioFileClip
                test_audio = AudioFileClip(audio_path)
                st.caption(f"🎵 {audio_filename} | 时长：{test_audio.duration:.1f} 秒")
                test_audio.close()
            except:
                st.caption(f"🎵 {audio_filename}")
            
            st.info("💡 提示：可以同时播放音乐和手语舞视频，边听边学！")

# 测试用
if __name__ == "__main__":
    st.set_page_config(page_title="手语舞", page_icon="🎵")
    interest_section()
