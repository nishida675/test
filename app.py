import yt_dlp
import streamlit as st
import tempfile
import os
import subprocess

st.title('YouTube オーディオダウンロード')

if 'yt_info' not in st.session_state:
    st.session_state['yt_info'] = None

# キャッシュクリア関数
def clear_yt_dlp_cache():
    try:
        subprocess.run(["yt-dlp", "--rm-cache-dir"], check=True)
        st.success("yt-dlpのキャッシュをクリアしました。")
    except Exception as e:
        st.warning(f"キャッシュクリアに失敗しました: {str(e)}")

# URL入力フォーム
with st.form(key="url_form"):
    video_url = st.text_input("YouTubeリンクを入力してください")
    submit = st.form_submit_button("動画情報を取得")

# 情報取得
if submit and video_url:
    clear_yt_dlp_cache()  # キャッシュを毎回クリア
    try:
        ydl_opts = {
            'quiet': True,
            'force_generic_extractor': False,
            'noplaylist': True,
            'default_search': 'ytsearch',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            st.session_state['yt_info'] = info
    except Exception as e:
        st.error(f"動画情報の取得に失敗しました: {str(e)}")

# 情報表示
if st.session_state['yt_info']:
    info = st.session_state['yt_info']
    st.write(f"タイトル: {info.get('title', '不明')}")
    if 'thumbnail' in info:
        st.image(info['thumbnail'])

    if st.button("音声(mp3)をダウンロード"):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = os.path.join(tmpdir, '%(title)s.%(ext)s')
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_path,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                    'noplaylist': True,
                    'headers': {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
                    }
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                downloaded_file = next((f for f in os.listdir(tmpdir) if f.endswith(".mp3")), None)

                if downloaded_file:
                    file_path = os.path.join(tmpdir, downloaded_file)
                    with open(file_path, "rb") as f:
                        audio_bytes = f.read()

                    st.download_button(
                        label="ここをクリックしてダウンロード",
                        data=audio_bytes,
                        file_name=downloaded_file,
                        mime="audio/mpeg"
                    )
                else:
                    st.error("音声ファイルが見つかりませんでした。")
        except Exception as e:
            st.error(f"ダウンロード中にエラーが発生しました: {str(e)}")
