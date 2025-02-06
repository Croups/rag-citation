import streamlit as st
import os
from rag import RAGSystem
import json
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(layout="wide")

def init_session_state():
    if 'rag' not in st.session_state:
        st.session_state.rag = RAGSystem(api_key=os.environ['ANTHROPIC_API_KEY'])
        st.session_state.chat_history = []
        st.session_state.show_citations = {}

def main():
    st.markdown("""
        <style>
        .chat-container { margin-bottom: 2rem; }
        .user-question { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; }
        .answer-text { padding: 1rem 0; }
        .citation-box { background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border: 1px solid #e9ecef; }
        .info-box { 
            background-color: #e3f2fd; 
            padding: 1.5rem; 
            border-radius: 0.5rem; 
            margin: 1rem 0; 
            border-left: 5px solid #2196f3;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Document Q&A System")
    
    st.markdown("""
        <div class="info-box">
        This is a RAG (Retrieval-Augmented Generation) implementation that combines Claude's citation capabilities 
        with Microsoft's Markitdown library. The system processes multiple document formats and provides 
        in-text citations to maintain transparency and traceability in AI-generated responses.
        </div>
    """, unsafe_allow_html=True)
    
    init_session_state()

    with st.sidebar:
        st.header("Upload Documents")
        files = st.file_uploader("Upload your documents here", 
                                accept_multiple_files=True, 
                                type=['txt', 'pdf', 'docx', 'pptx'])
        
        if files:
            with st.spinner('Processing documents...'):
                for file in files:
                    temp_path = f"temp_{file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(file.getvalue())
                    st.session_state.rag.add_document(temp_path)
                    os.remove(temp_path)
                st.success(f"{len(files)} documents processed")

    chat_container = st.container()
    question = st.chat_input("Ask a question about your documents")
    
    if question:
        with st.spinner('Processing...'):
            response = st.session_state.rag.ask(question)
            st.session_state.chat_history.append({
                "question": question,
                "response": response
            })

    with chat_container:
        for idx, chat in enumerate(reversed(st.session_state.chat_history)):
            st.markdown(f"""<div class='user-question'><b>Q:</b> {chat['question']}</div>""", 
                      unsafe_allow_html=True)
            
            response_lines = chat['response'].split('\n')
            answer = []
            citations = []
            collecting_citations = False
            
            for line in response_lines:
                if line.startswith('Citations:'):
                    collecting_citations = True
                    continue
                if collecting_citations:
                    if line.strip() and not line.startswith('-' * 10):
                        citations.append(line)
                else:
                    if not line.startswith('Response Text:') and not line.startswith('-' * 10):
                        answer.append(line)
            
            st.markdown(f"""<div class='answer-text'>{''.join(answer)}</div>""", 
                      unsafe_allow_html=True)
            
            if citations:
                col1, col2 = st.columns([1, 4])
                with col1:
                    button_label = "Hide Citations" if st.session_state.show_citations.get(idx, False) else "Show Citations"
                    if st.button(button_label, key=f"cite_{idx}"):
                        st.session_state.show_citations[idx] = not st.session_state.show_citations.get(idx, False)
                
                if st.session_state.show_citations.get(idx, False):
                    citation_text = '\n'.join(citations)
                    st.markdown(f"<div class='citation-box'>{citation_text}</div>", 
                              unsafe_allow_html=True)
            st.divider()

if __name__ == "__main__":
    main()