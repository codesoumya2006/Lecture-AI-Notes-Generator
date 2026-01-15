import streamlit as st
import logging
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from core.audio_pipeline import AudioPipeline
from core.transcribe_fast import FastTranscriber
from core.chunker import AudioChunker
from core.llm_fast import OllamaLLM
from services.youtube import YouTubeDownloader
from services.recorder import AudioRecorder
from services.notes import NotesGenerator
from services.exam import ExamGenerator
from services.pdf import PDFExporter
from services.audio_utils import get_unique_audio_path
from services.youtube_audio import download_audio
from services.transcription import transcribe_audio

# Page configuration
st.set_page_config(
    page_title="Lecture Voice-to-Notes Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    /* Fixed boundaries for content areas with scrolling */
    .stExpander .streamlit-expanderContent {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 10px;
        background-color: #fafafa;
    }
    .stTextArea textarea {
        max-height: 300px;
        overflow-y: auto;
    }
    .stExpander {
        margin-bottom: 10px;
    }
    .markdown-text-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 10px;
        background-color: #fafafa;
    }
    /* Ensure all content in expanders is contained */
    .stExpander [data-testid="stExpander"] .streamlit-expanderContent {
        max-height: 400px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None
if "processing" not in st.session_state:
    st.session_state.processing = False

# Reset session state when URL changes
if "last_url" not in st.session_state:
    st.session_state.last_url = None

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    st.divider()
    
    llm_model = st.selectbox(
        "LLM Model",
        ["mistral", "neural-chat", "dolphin-mixtral"],
        help="Select language model for text generation"
    )
    
    transcribe_model = st.selectbox(
        "Transcription Model",
        ["base", "small", "medium"],
        help="Larger models are slower but more accurate"
    )
    
    st.divider()
    st.markdown("### ℹ️ Info")
    st.info("""
    **Lecture Voice-to-Notes Generator**
    
    - 🎤 Record lectures
    - 📝 Transcribe audio
    - 📚 Generate study notes
    - ✅ Create practice exams
    - 📄 Export to PDF
    
    100% Offline • CPU Only
    """)

# Main header
st.title("📚 Lecture Voice-to-Notes Generator")
st.markdown("Convert lectures to study materials in seconds")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎙️ Input Audio",
    "📝 Transcribe",
    "📚 Study Notes",
    "✅ Exam Generator",
    "📄 Export"
])

# =======================
# TAB 1: INPUT AUDIO
# =======================
with tab1:
    st.header("Input Your Audio")
    
    input_method = st.radio(
        "Choose input method:",
        ["Record Lecture", "Upload Audio File", "Download from YouTube"],
        horizontal=True
    )
    
    if input_method == "Record Lecture":
        st.subheader("🎤 Record Live Lecture")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start Recording", key="start_record"):
                st.session_state.recording = True
                st.info("Recording started... Speak now!")
                
                try:
                    recorder = AudioRecorder()
                    recorder.start_recording()
                    st.session_state.recorder = recorder
                except Exception as e:
                    st.error(f"Error starting recording: {e}")
        
        with col2:
            if st.button("⏹️ Stop Recording", key="stop_record"):
                if hasattr(st.session_state, 'recorder'):
                    try:
                        audio_path = st.session_state.recorder.stop_recording()
                        st.session_state.audio_file = audio_path
                        st.session_state.recording = False
                        st.success(f"Recording saved: {audio_path}")
                    except Exception as e:
                        st.error(f"Error stopping recording: {e}")
    
    elif input_method == "Upload Audio File":
        st.subheader("📤 Upload Audio File")
        uploaded_file = st.file_uploader(
            "Choose audio file (MP3, WAV, M4A)",
            type=["mp3", "wav", "m4a", "ogg", "flac"]
        )
        
        if uploaded_file:
            audio_path = f"./uploads/{uploaded_file.name}"
            os.makedirs("./uploads", exist_ok=True)
            
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.audio_file = audio_path
            st.success(f"✓ File uploaded: {uploaded_file.name}")
    
    else:  # YouTube
        st.subheader("🎥 Download from YouTube")

        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=..."
        )

        if youtube_url:
            if youtube_url != st.session_state.last_url:
                st.session_state.transcript = None
                st.session_state.last_url = youtube_url

            if st.button("⬇️ Download Audio"):
                try:
                    with st.spinner("Downloading audio..."):
                        audio_path = get_unique_audio_path(youtube_url)
                        download_audio(youtube_url, audio_path)
                        st.session_state.audio_file = audio_path
                        st.success(f"✓ Downloaded: {audio_path}")
                except Exception as e:
                    st.error(f"Error downloading: {e}")
    
    # Display current audio file
    if st.session_state.audio_file:
        st.divider()
        st.success(f"📁 Current audio: {st.session_state.audio_file}")

# =======================
# TAB 2: TRANSCRIBE
# =======================
with tab2:
    st.header("Transcribe Audio to Text")
    
    if not st.session_state.audio_file:
        st.warning("⚠️ Please upload or record audio first (in 'Input Audio' tab)")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📁 File: {st.session_state.audio_file}")
        with col2:
            if st.button("🚀 Transcribe", key="transcribe_btn"):
                st.session_state.processing = True
        
        if st.session_state.processing:
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("1️⃣ Loading audio...")
                progress_bar.progress(20)

                # Load and process audio
                audio_pipeline = AudioPipeline()
                audio = audio_pipeline.process_audio_file(st.session_state.audio_file)

                status_text.text("2️⃣ Transcribing audio...")
                progress_bar.progress(60)

                # Transcribe
                transcript = transcribe_audio(st.session_state.audio_file)
                st.session_state["transcript"] = transcript.strip()

                progress_bar.progress(100)
                status_text.text("✓ Transcription complete!")

                st.session_state.processing = False
                st.success("✓ Audio transcribed successfully!")

            except Exception as e:
                st.error(f"Error during transcription: {e}")
                logger.error(f"Transcription error: {e}")
                st.session_state.processing = False
        
        # Display transcript
        if st.session_state.transcript:
            st.divider()
            st.subheader("📄 Transcript")

            # Display with word count
            word_count = len(st.session_state.transcript.split())
            st.caption(f"📊 {word_count} words")

            transcript_display = st.text_area(
                "Lecture Transcription",
                value=st.session_state.transcript,
                height=300,
                disabled=False
            )

            # Update if edited
            st.session_state["transcript"] = transcript_display.strip()

# =======================
# TAB 3: STUDY NOTES
# =======================
with tab3:
    st.header("Generate Study Notes")

    if not st.session_state.transcript:
        st.warning("⚠️ Please transcribe audio first (in 'Transcribe' tab)")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📚 Generate Notes", key="gen_notes"):
                try:
                    with st.spinner("Generating notes..."):
                        notes_gen = NotesGenerator()
                        notes = notes_gen.generate_structured_notes(st.session_state.transcript)
                        st.session_state.generated_notes = notes
                        st.success("✓ Notes generated!")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col2:
            if st.button("📋 Summary", key="gen_summary"):
                try:
                    with st.spinner("Generating summary..."):
                        notes_gen = NotesGenerator()
                        summary = notes_gen.generate_summary(st.session_state.transcript, "medium")
                        st.session_state.generated_summary = summary
                        st.success("✓ Summary generated!")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col3:
            if st.button("📖 Study Guide", key="gen_guide"):
                try:
                    with st.spinner("Generating study guide..."):
                        notes_gen = NotesGenerator()
                        guide = notes_gen.generate_study_guide(st.session_state.transcript)
                        st.session_state.generated_guide = guide
                        st.success("✓ Study guide generated!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.divider()
        
        # Display generated content
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if "generated_notes" in st.session_state:
                with st.expander("📚 Study Notes", expanded=True):
                    st.markdown(st.session_state.generated_notes)
        
        with col2:
            if "generated_summary" in st.session_state:
                with st.expander("📋 Summary", expanded=True):
                    st.markdown(st.session_state.generated_summary)
        
        with col3:
            if "generated_guide" in st.session_state:
                with st.expander("📖 Study Guide", expanded=True):
                    st.markdown(st.session_state.generated_guide)

# =======================
# TAB 4: EXAM GENERATOR
# =======================
with tab4:
    st.header("Generate Practice Exam")

    if not st.session_state.transcript:
        st.warning("⚠️ Please transcribe audio first (in 'Transcribe' tab)")
    else:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🎯 MCQ (5)", key="gen_mcq"):
                try:
                    with st.spinner("Generating MCQs..."):
                        exam_gen = ExamGenerator()
                        mcqs = exam_gen.generate_multiple_choice(st.session_state.transcript, 5)
                        st.session_state.generated_mcqs = mcqs
                        st.success("✓ MCQs generated!")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col2:
            if st.button("📝 Short Answer", key="gen_short"):
                try:
                    with st.spinner("Generating questions..."):
                        exam_gen = ExamGenerator()
                        questions = exam_gen.generate_short_answer_questions(st.session_state.transcript, 5)
                        st.session_state.generated_short = questions
                        st.success("✓ Questions generated!")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col3:
            if st.button("✓/✗ True/False", key="gen_tf"):
                try:
                    with st.spinner("Generating questions..."):
                        exam_gen = ExamGenerator()
                        questions = exam_gen.generate_true_false(st.session_state.transcript, 5)
                        st.session_state.generated_tf = questions
                        st.success("✓ Questions generated!")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col4:
            if st.button("📚 Full Test", key="gen_full"):
                try:
                    with st.spinner("Generating complete test..."):
                        exam_gen = ExamGenerator()
                        test = exam_gen.generate_practice_test(st.session_state.transcript)
                        # Set individual session state keys for each type
                        st.session_state.generated_mcqs = test.get("multiple_choice", [])
                        st.session_state.generated_short = test.get("short_answer", [])
                        st.session_state.generated_tf = test.get("true_false", [])
                        st.session_state.generated_full_test = test
                        st.success("✓ Practice test generated!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.divider()

        # Display questions
        col1, col2 = st.columns(2)

        with col1:
            if "generated_mcqs" in st.session_state:
                with st.expander("🎯 Multiple Choice Questions"):
                    for i, q in enumerate(st.session_state.generated_mcqs, 1):
                        st.write(f"**Q{i}: {q.get('question', 'Question')}")
                        if q.get('options'):
                            for opt in q['options']:
                                st.write(f"- {opt}")
                        st.caption(f"Answer: {q.get('answer', '?')}")
                        st.divider()

        with col2:
            if "generated_short" in st.session_state:
                with st.expander("📝 Short Answer Questions"):
                    for i, q in enumerate(st.session_state.generated_short, 1):
                        st.write(f"**Q{i}: {q}")
                        st.divider()

        with col3:
            if "generated_tf" in st.session_state:
                with st.expander("✓/✗ True/False Questions"):
                    for i, q in enumerate(st.session_state.generated_tf, 1):
                        st.write(f"**Q{i}: {q.get('statement', 'Statement')}")
                        st.caption(f"Answer: {q.get('answer', '?')}")
                        st.divider()

        if "generated_full_test" in st.session_state:
            with st.expander("📚 Complete Practice Test"):
                test = st.session_state.generated_full_test
                if test.get("multiple_choice"):
                    st.subheader("🎯 Multiple Choice")
                    for i, q in enumerate(test["multiple_choice"], 1):
                        st.write(f"**Q{i}: {q.get('question')}")
                        for opt in q.get('options', []):
                            st.write(f"- {opt}")
                        st.caption(f"Answer: {q.get('answer')}")
                        st.divider()
                if test.get("short_answer"):
                    st.subheader("📝 Short Answer")
                    for i, q in enumerate(test["short_answer"], 1):
                        st.write(f"**Q{i}: {q}")
                        st.divider()
                if test.get("true_false"):
                    st.subheader("✓/✗ True/False")
                    for i, q in enumerate(test["true_false"], 1):
                        st.write(f"**Q{i}: {q.get('statement')}")
                        st.caption(f"Answer: {q.get('answer')}")
                        st.divider()

                if test.get("essay"):
                    st.subheader("📖 Essay Prompts")
                    for i, q in enumerate(test["essay"], 1):
                        st.write(f"**Prompt {i}: {q}")
                        st.divider()

# =======================
# TAB 5: EXPORT
# =======================
with tab5:
    st.header("Export to PDF")

    if not st.session_state.transcript:
        st.warning("⚠️ Please transcribe audio first")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Export Transcript", key="export_transcript_btn"):
                transcript = st.session_state.get("transcript", "").strip()

                if not transcript:
                    st.warning("Transcript not available. Please generate transcription first.")
                else:
                    pdf_bytes = PDFExporter().export_transcript_bytes("Lecture Transcript", transcript)

                    st.download_button(
                        label="⬇️ Download Transcript PDF",
                        data=pdf_bytes,
                        file_name="lecture_transcript.pdf",
                        mime="application/pdf",
                        key="download_transcript"
                    )

        with col2:
            if "generated_notes" in st.session_state:
                st.download_button(
                    label="💾 Export Notes",
                    data=PDFExporter().export_notes_bytes("Lecture Notes", st.session_state.generated_notes),
                    file_name="notes.pdf",
                    mime="application/pdf",
                    key="download_notes"
                )

        with col3:
            if "generated_mcqs" in st.session_state:
                st.download_button(
                    label="💾 Export Exam",
                    data=PDFExporter().export_exam_bytes("Practice Exam", st.session_state.generated_mcqs),
                    file_name="exam.pdf",
                    mime="application/pdf",
                    key="download_exam"
                )

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    <p>💡 Lecture Voice-to-Notes Generator | 🚀 100% Offline | 🔥 Ultra-Fast Processing</p>
    </div>
""", unsafe_allow_html=True)
