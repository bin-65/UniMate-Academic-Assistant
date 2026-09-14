import streamlit as st
import fitz  # PyMuPDF

class PDFSummarizer:
    def __init__(self):
        pass

    def render_ui(self):
        st.markdown("### 📖 PDF Lecture Notes & Document Summarizer")
        st.markdown("Upload your semester notes, research papers, or syllabus PDFs to extract key academic insights instantly.")

        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        
        if uploaded_file is not None:
            with st.spinner("Analyzing document structure..."):
                try:
                    # Read PDF using PyMuPDF (fitz)
                    file_bytes = uploaded_file.read()
                    doc = fitz.open(stream=file_bytes, filetype="pdf")
                    
                    text_content = ""
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        text_content += page.get_text()
                    
                    total_words = len(text_content.split())
                    
                    st.success(f"Successfully processed PDF! Total Pages: {len(doc)} | Total Words: {total_words}")
                    
                    # Display quick preview & simulated smart summary
                    with st.expander("🔍 View Extracted Text Preview"):
                        st.write(text_content[:1500] + "..." if len(text_content) > 1500 else text_content)
                        
                    if st.button("Generate Smart Academic Summary"):
                        with st.spinner("Synthesizing key academic notes..."):
                            # Summary generation logic
                            summary_output = self._generate_summary(text_content)
                            st.markdown("### 📝 Academic Summary & Key Takeaways")
                            st.markdown(summary_output)
                            
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")

    def _generate_summary(self, text: str) -> str:
        # Fast local summary extraction or fallback formatting
        paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 40]
        key_points = paragraphs[:5] if len(paragraphs) >= 5 else paragraphs
        
        formatted_points = "\n".join([f"• {pt}" for pt in key_points])
        
        return (
            "**Document Core Breakdown:**\n\n"
            f"{formatted_points}\n\n"
            "**Recommended Action Items for Students:**\n"
            "1. Review highlighted core concepts thoroughly.\n"
            "2. Note down any equations or definitions for upcoming exams.\n"
            "3. Use the UniMate Chat tab to ask specific questions about this document."
        )
