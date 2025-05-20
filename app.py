import yt_dlp
import streamlit as st
import tempfile
import os

st.title('YouTube オーディオダウンロード')

if 'yt_info' not in st.session_state:
    st.session_state['yt_info'] = None

# URL入力フォーム
with st.form(key="url_form"):
    video_url = st.text_input("YouTubeリンクを入力してください")
    submit = st.form_submit_button("動画情報を取得")

# 情報取得
if submit and video_url:
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(video_url, download=False)
            st.session_state['yt_info'] = info
    except Exception as e:
        st.error(f"動画情報の取得に失敗しました: {str(e)}")

# 情報表示
if st.session_state['yt_info']:
    info = st.session_state['yt_info']
    st.write(f"タイトル: {info['title']}")
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
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                downloaded_file = next((f for f in os.listdir(tmpdir) if f.endswith(".mp3")), None)

                if downloaded_file:
                    file_path = os.path.join(tmpdir, downloaded_file)

                    # メモリに読み込む
                    with open(file_path, "rb") as f:
                        audio_bytes = f.read()

                    # bytesでダウンロードボタンに渡す
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
