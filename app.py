"""
Streamlit UI for Mini RAG.

Usage:
    streamlit run app.py
"""
from pathlib import Path

import streamlit as st

from src.rag_engine import RAGEngine


def initialize_rag() -> RAGEngine:
    """Initialize or load RAG engine."""
    if 'rag' not in st.session_state:
        st.session_state.rag = RAGEngine()
        
        index_path = Path("./index")
        if index_path.exists():
            try:
                with st.spinner("Loading index..."):
                    st.session_state.rag.load_index("./index")
                st.session_state.index_loaded = True
            except Exception as e:
                st.error(f"Error loading index: {e}")
                st.session_state.index_loaded = False
        else:
            st.session_state.index_loaded = False
            
    return st.session_state.rag


def main() -> None:
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Mini-RAG",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Mini-RAG: Local Document Search")
    st.markdown("*Search your PDF documents using semantic similarity*")
    
    rag = initialize_rag()
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.subheader("Index Management")
        
        if st.session_state.get('index_loaded', False):
            st.success("✅ Index loaded")
            num_chunks = len(rag.chunks)
            st.info(f"📊 {num_chunks} chunks indexed")
        else:
            st.warning("⚠️ No index loaded")
            st.info("Place PDF files in ./data/ and click 'Build Index'")
        
        if st.button("🔨 Build Index", help="Build index from PDFs in ./data/"):
            try:
                with st.spinner("Building index... This may take a few minutes."):
                    rag.build_index()
                    rag.save_index("./index")
                st.success("✅ Index built successfully!")
                st.session_state.index_loaded = True
                st.rerun()
            except Exception as e:
                st.error(f"Error building index: {e}")
        
        st.divider()
        
        st.subheader("Search Settings")
        top_k = st.slider(
            "Number of results",
            min_value=1,
            max_value=10,
            value=3,
            help="How many relevant passages to retrieve"
        )
        
        st.divider()
        
        st.subheader("ℹ️ About")
        st.markdown("""
        This is a local RAG system that:
        - 📄 Indexes PDF documents
        - 🔍 Performs semantic search
        - 🚫 Requires no API keys
        - 💻 Runs entirely locally
        """)
    
    # Main content
    if not st.session_state.get('index_loaded', False):
        st.warning("⚠️ Please build the index first using the sidebar.")
        st.info("""
        **Getting Started:**
        1. Place your PDF files in the `./data/` directory
        2. Click "Build Index" in the sidebar
        3. Start searching!
        """)
        return
    
    # Query input
    st.header("🔎 Search Documents")
    
    query = st.text_input(
        "Enter your query:",
        placeholder="e.g., Which sensors support 1200°C?",
        help="Enter a question or topic to search for in your documents"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Perform search
    if search_button and query:
        with st.spinner("Searching..."):
            try:
                results = rag.query(query, top_k=top_k)
                
                if results:
                    st.success(f"✅ Found {len(results)} relevant passages")
                    
                    # Display results
                    st.header("📋 Results")
                    
                    for i, result in enumerate(results, 1):
                        with st.expander(
                            f"**Result {i}** - {result['doc_id']} (Page {result['page']}) - "
                            f"Score: {result['score']:.4f}",
                            expanded=i==1  # Expand first result by default
                        ):
                            # Metadata
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Document", result['doc_id'])
                            with col2:
                                st.metric("Page", result['page'])
                            with col3:
                                st.metric("Similarity Score", f"{result['score']:.4f}")
                            
                            # Text content
                            st.markdown("**Excerpt:**")
                            st.text_area(
                                "Text",
                                value=result['text'],
                                height=200,
                                key=f"result_{i}",
                                label_visibility="collapsed"
                            )
                            
                            st.markdown(
                                f"📄 *Source: {result['doc_id']}.pdf, Page {result['page']}*"
                            )
                else:
                    st.warning("No results found. Try a different query.")
                    
            except Exception as e:
                st.error(f"Error during search: {e}")
    
    elif search_button:
        st.warning("Please enter a query.")


if __name__ == "__main__":
    main()
