import streamlit as st
import json
import os
import io
import zipfile

# Config
st.set_page_config(page_title="UI Prompt Reviewer", layout="centered")

# Load JSON
@st.cache_data
def load_data(file):
    return json.load(file)

# Save function
def save_data(filename, data):
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Create ZIP for download
def create_zip(kept, discarded):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("kept_prompts.json", json.dumps(kept, indent=2, ensure_ascii=False))
        zf.writestr("discarded_prompts.json", json.dumps(discarded, indent=2, ensure_ascii=False))
    zip_buffer.seek(0)
    return zip_buffer

st.title("📊 UI Prompt Reviewer")

uploaded_file = st.file_uploader("Upload your JSON file", type=["json"])
if uploaded_file:
    data = load_data(uploaded_file)
    total = len(data)

    if "start_index" not in st.session_state:
        start_index = st.number_input("Enter starting record index (0-based):", min_value=0, max_value=total-1, value=0, step=1, key="input_index")
        if st.button("Confirm starting index"):
            st.session_state.start_index = start_index
            st.session_state.current = start_index
            st.rerun()

        st.stop()

    if "current" not in st.session_state:
        st.session_state.current = st.session_state.start_index
    if "kept" not in st.session_state:
        st.session_state.kept = []
    if "discarded" not in st.session_state:
        st.session_state.discarded = []

    current = st.session_state.current

    if current < total:
        item = data[current]

        st.markdown(f"### 📝 Prompt {current + 1} / {total}")

        st.write(item.get("prompt", "No prompt found"))

        st.write("")  # Blank line before UI preview
        if item.get("previewUrl"):
            st.markdown("#### 🎨 UI Preview")
            st.image(item["previewUrl"], width=400)

            st.write("")  # Blank line before buttons

            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Keep", key=f"keep_{current}"):
                        st.session_state.kept.append(item)
                        st.session_state.current += 1
                        save_data("kept_prompts.json", st.session_state.kept)
                        save_data("discarded_prompts.json", st.session_state.discarded)
                        st.rerun()
                with col2:
                    if st.button("❌ Discard", key=f"discard_{current}"):
                        st.session_state.discarded.append(item)
                        st.session_state.current += 1
                        save_data("kept_prompts.json", st.session_state.kept)
                        save_data("discarded_prompts.json", st.session_state.discarded)
                        st.rerun()

                # Download button right below keep/discard buttons
                zip_buffer = create_zip(st.session_state.kept, st.session_state.discarded)
                st.download_button(
                    "⬇️ Download All (ZIP)",
                    data=zip_buffer,
                    file_name="prompt_reviews.zip",
                    mime="application/zip",
                    key="zip_download"
                )
        else:
            st.warning("No preview URL found for this prompt.")

    else:
        st.success("🎉 Review complete!")
        save_data("kept_prompts.json", st.session_state.kept)
        save_data("discarded_prompts.json", st.session_state.discarded)
        st.write(f"Total kept: {len(st.session_state.kept)}")
        st.write(f"Total discarded: {len(st.session_state.discarded)}")

        # Also provide download button here at the end
        zip_buffer = create_zip(st.session_state.kept, st.session_state.discarded)
        st.download_button(
            "⬇️ Download All (ZIP)",
            data=zip_buffer,
            file_name="prompt_reviews.zip",
            mime="application/zip",
            key="zip_download_final"
        )
