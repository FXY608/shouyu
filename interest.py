"""
手语乐园 - 兴趣区（手语舞）
优化版：支持 Streamlit Cloud 部署
"""

import streamlit as st
import os
import tempfile
import time
import re
import shutil

# 导入 moviepy
try:
    from moviepy import VideoFileClip, concatenate_videoclips
    MOVIEPY_OK = True
except ImportError:
    try:
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        MOVIEPY_OK = True
    except ImportError:
        MOVIEPY_OK = False

# 配置路径（使用临时目录）
def get_temp_dir():
    """获取临时目录（兼容云端部署）"""
    if os.path.exists('/tmp'):
        return '/tmp/shouyu_cache'
    else:
        return tempfile.gettempdir()

TEMP_DIR = get_temp_dir()
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def preprocess_text(text):
    """预处理文本，去除标点符号，转为小写"""
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    text = text.lower()
    return text

def find_video_for_word(word, video_mapping):
    """为单个词查找对应的视频文件（使用内存映射）"""
    word = word.strip()
    if not word:
        return None
    
    # 直接从映射中查找（避免重复读取文件系统）
    return video_mapping.get(word)

def load_videos_to_memory(video_dir):
    """将所有视频加载到内存映射（避免重复读取文件系统）"""
    if not os.path.exists(video_dir):
        return {}
    
    video_mapping = {}
    for filename in os.listdir(video_dir):
        if filename.endswith(('.mp4', '.MP4', '.mov', '.MOV', '.avi')):
            # 去除扩展名作为键
            name = os.path.splitext(filename)[0]
            name = name.lower()
            video_mapping[name] = os.path.join(video_dir, filename)
    
    return video_mapping

def text_to_video_clip(text, video_mapping):
    """把一句话转成手语视频片段（自动压缩）"""
    
    if not MOVIEPY_OK:
        return None
    
    text = preprocess_text(text)
    words = text.split()
    
    video_paths = []
    for word in words:
        if not word:
            continue
        
        video_path = find_video_for_word(word, video_mapping)
        if video_path:
            video_paths.append(video_path)
    
    if not video_paths:
        return None
    
    clips = []
    for path in video_paths:
        try:
            clip = VideoFileClip(path)
            # 修改这里：resize → resized
            if clip.h > 360:
                clip = clip.resized(height=360)  # ← 改这里
            # 限制时长
            if clip.duration > 3:
                clip = clip.subclipped(0, 3)
            clips.append(clip)
        except Exception as e:
            st.warning(f"加载视频失败: {e}")
            continue
    
    if not clips:
        return None
    
    if len(clips) == 1:
        return clips[0]
    else:
        try:
            return concatenate_videoclips(clips, method="compose")
        except:
            return concatenate_videoclips(clips)

def generate_sign_dance_video(lyrics_lines, video_mapping, progress_callback=None):
    """生成手语舞视频（优化版）"""
    
    if not MOVIEPY_OK:
        return None, "moviepy 未安装"
    
    if not video_mapping:
        return None, "没有找到任何视频素材"
    
    video_clips = []
    failed_lines = []
    
    for i, line in enumerate(lyrics_lines):
        if progress_callback:
            progress_callback(i, len(lyrics_lines), f"🎬 处理第 {i+1}/{len(lyrics_lines)} 句")
        
        clip = text_to_video_clip(line, video_mapping)
        if clip:
            # 修改这里：resize → resized
            if clip.h > 480:
                clip = clip.resized(height=480)  # ← 改这里
            video_clips.append(clip)
        else:
            failed_lines.append(line)
    
    if not video_clips:
        return None, "没有生成任何视频片段"
    
    # 合成所有片段
    try:
        if len(video_clips) == 1:
            final_video = video_clips[0]
        else:
            final_video = concatenate_videoclips(video_clips, method="compose")
    except Exception as e:
        return None, f"视频合成失败: {e}"
    
    # 保存视频
    try:
        st.info("🎬 正在渲染视频，请稍候...")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4', dir=TEMP_DIR) as temp_file:
            temp_path = temp_file.name
        
        final_video.write_videofile(
            temp_path,
            codec='libx264',
            audio_codec='aac',
            fps=20,
            preset='ultrafast',
            bitrate='500k',
            threads=2
        )
        
        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
            raise Exception("视频文件生成失败")
        
        # 清理资源
        final_video.close()
        for clip in video_clips:
            try:
                clip.close()
            except:
                pass
        
        return temp_path, failed_lines
        
    except Exception as e:
        final_video.close()
        for clip in video_clips:
            try:
                clip.close()
            except:
                pass
        return None, f"视频保存失败: {e}"

def cleanup_temp_files(file_path):
    """清理临时文件"""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except:
        pass

def interest_section():
    st.markdown('<h3 style="color:#3a5a6e;">🎵 创 · 手语舞</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b8a9e;">上传音乐，让手语随旋律绽放</p>', unsafe_allow_html=True)
    
    # 检查依赖
    if not MOVIEPY_OK:
        st.error("❌ moviepy 未正确安装")
        st.code("请运行以下命令安装：\npip install moviepy", language="bash")
        st.info("如果安装后仍有问题，请重启 Streamlit 应用")
        return
    
    # 加载视频素材到内存映射
    video_dir = "videos"
    if not os.path.exists(video_dir):
        st.error(f"❌ {video_dir} 文件夹不存在")
        st.info(f"请创建 {video_dir} 文件夹，并放入手语视频文件")
        return
    
    video_mapping = load_videos_to_memory(video_dir)
    if not video_mapping:
        st.warning(f"⚠️ {video_dir} 文件夹中没有找到视频文件")
        st.info("请放入 .mp4 或 .mov 格式的视频文件，命名格式示例：你好.mp4、谢谢.mp4")
        return
    
    st.success(f"✅ 已加载 {len(video_mapping)} 个手语视频素材")
    
    # 显示可用的视频列表
    with st.expander("📹 查看可用视频素材"):
        video_list = list(video_mapping.keys())
        cols = st.columns(3)
        for idx, video_name in enumerate(video_list[:12]):
            with cols[idx % 3]:
                st.text(f"• {video_name}")
        if len(video_list) > 12:
            st.text(f"... 还有 {len(video_list) - 12} 个")
    
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
        
        # 使用 tempfile 保存音频（兼容云端）
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_filename.split(".")[-1]}', dir=TEMP_DIR) as temp_audio:
            temp_audio.write(uploaded_audio.getbuffer())
            audio_path = temp_audio.name
        
        st.success(f"✅ 已上传：{audio_filename}")
        
        # 显示音乐信息
        try:
            from moviepy import AudioFileClip
            test_audio = AudioFileClip(audio_path)
            st.caption(f"⏱️ 音乐时长：{test_audio.duration:.1f} 秒")
            test_audio.close()
        except:
            pass
    
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
        help="每句歌词占一行，确保有对应的视频文件",
        key="lyrics_input"
    )
    
    if lyrics.strip():
        lines = [l.strip() for l in lyrics.split("\n") if l.strip()]
        st.caption(f"📊 共 {len(lines)} 句歌词")
        
        # 检查缺失的视频
        all_words = set()
        for line in lines:
            processed_line = preprocess_text(line)
            for word in processed_line.split():
                if word:
                    all_words.add(word)
        
        missing_videos = []
        available_videos = []
        
        for word in all_words:
            if word in video_mapping:
                available_videos.append(word)
            else:
                missing_videos.append(word)
        
        if available_videos:
            st.success(f"✅ 找到 {len(available_videos)} 个词的视频素材")
        
        if missing_videos:
            with st.expander(f"⚠️ 缺少 {len(missing_videos)} 个视频文件"):
                for word in missing_videos[:10]:
                    st.write(f"• {word}.mp4")
                if len(missing_videos) > 10:
                    st.write(f"... 还有 {len(missing_videos) - 10} 个")
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
    
    # 初始化 session state
    if "generated_video_path" not in st.session_state:
        st.session_state.generated_video_path = None
    
    # 清理旧的临时文件
    if st.session_state.generated_video_path and os.path.exists(st.session_state.generated_video_path):
        cleanup_temp_files(st.session_state.generated_video_path)
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
                        progress = current / total
                        progress_bar.progress(progress, text=message)
                    status_text.text(message)
                
                # 生成视频
                video_path, failed_lines = generate_sign_dance_video(lines, video_mapping, update_progress)
                
                progress_bar.empty()
                status_text.empty()
                
                if video_path and os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                    st.session_state.generated_video_path = video_path
                    st.success("✅ 手语舞视频生成成功！")
                    
                    if failed_lines:
                        st.warning(f"⚠️ 以下 {len(failed_lines)} 个句子处理失败：{', '.join(failed_lines[:3])}")
                        if len(failed_lines) > 3:
                            st.write(f"... 还有 {len(failed_lines) - 3} 个")
                else:
                    error_msg = failed_lines if isinstance(failed_lines, str) else "请检查视频素材"
                    st.error(f"生成失败：{error_msg}")
    
    # ==================== 显示结果 ====================
    if st.session_state.generated_video_path and os.path.exists(st.session_state.generated_video_path):
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); border-radius: 20px; padding: 1rem; margin: 1rem 0;">
            <h3 style="text-align: center;">🎬 生成结果</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示视频（st.video 对 H.264 编码的 mp4 支持良好）
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
        
        # 音乐同步播放区域
        if audio_path and os.path.exists(audio_path):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fa709a30 0%, #fee14030 100%); border-radius: 20px; padding: 1rem; margin: 1rem 0;">
                <h3 style="text-align: center;">🎵 音乐同步播放</h3>
                <p style="text-align: center;">💡 提示：同时播放音乐和手语舞视频，边听边学！</p>
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

# 测试用
if __name__ == "__main__":
    st.set_page_config(
        page_title="手语舞 - 手语乐园",
        page_icon="🎵",
        layout="wide"
    )
    interest_section()
