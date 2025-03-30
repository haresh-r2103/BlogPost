#!/usr/bin/env python3
import os
import time
import base64
import streamlit as st
from typing import List, Dict
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from markdown2 import markdown
from fpdf import FPDF
import tempfile


from secret_api_keys import HUGGINGFACEHUB_API_TOKEN

# Configuration
CONFIG = {
    "llm_model": "mistralai/Mistral-7B-Instruct-v0.2",
    "default_keywords": ["remote work", "hybrid work", "HR policies"],
    "encoding": "utf-8",
    "trending_topics": [
        "Remote Work Policies in 2024",
        "AI in HR: Current Trends",
        "Employee Wellness Programs",
        "Diversity and Inclusion Strategies",
        "Hybrid Work Best Practices"
    ]
}

# Initialize Streamlit
st.set_page_config(page_title="HR Blog Generator", page_icon="📝", layout="wide")

def setup_environment():
    """Set up the environment with API keys"""
    os.environ['HUGGINGFACEHUB_API_TOKEN'] = HUGGINGFACEHUB_API_TOKEN

def initialize_llm():
    """Initialize the LLM with configured parameters"""
    return HuggingFaceEndpoint(
        repo_id=CONFIG["llm_model"],
        temperature=0.7,
        max_new_tokens=2000,
        repetition_penalty=1.1
    )

def get_trending_topics():
    """Return trending HR topics"""
    return CONFIG["trending_topics"]

def research_topic(topic: str) -> Dict:
    """Simulate research by returning predefined data"""
    return {
        "topic": topic,
        "keywords": CONFIG["default_keywords"],
        "sources": [
            "https://www.shrm.org",
            "https://hbr.org",
            "https://www.gartner.com"
        ]
    }

def create_outline(llm, research_data: Dict) -> List[Dict]:
    """Generate a blog post outline"""
    prompt = PromptTemplate(
        input_variables=["topic", "keywords"],
        template="""
        Create a detailed blog post outline about {topic} focusing on these keywords: {keywords}.
        Include:
        - Introduction
        - 3-4 main sections with 2-3 sub-sections each
        - Conclusion
        - Call to action
        
        Format as markdown headings (## for sections, ### for sub-sections).
        """
    )
    
    chain = prompt | llm
    result = chain.invoke({
        "topic": research_data["topic"],
        "keywords": ", ".join(research_data["keywords"])
    })
    
    # Simple outline parser
    outline = []
    current_section = None
    for line in result.split('\n'):
        line = line.strip()
        if line.startswith('## '):
            if current_section:
                outline.append(current_section)
            current_section = {
                'title': line[3:],
                'subsections': []
            }
        elif line.startswith('### '):
            if current_section:
                current_section['subsections'].append(line[4:])
    
    if current_section:
        outline.append(current_section)
    
    return outline

def generate_section(llm, section_info: Dict) -> str:
    """Generate content for one section"""
    prompt = PromptTemplate(
        input_variables=["title", "subsections"],
        template="""
        Write a detailed blog section about: {title}
        
        Cover these sub-topics:
        {subsections}
        
        Requirements:
        - 300-500 words
        - Professional but engaging tone
        - Use markdown formatting
        - Include relevant examples or statistics
        """
    )
    
    chain = prompt | llm
    return chain.invoke({
        "title": section_info["title"],
        "subsections": "\n- ".join(section_info["subsections"])
    })

def generate_full_content(llm, outline: List[Dict]) -> str:
    """Generate complete blog content"""
    sections = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, section in enumerate(outline):
        status_text.text(f"Generating section {i+1}/{len(outline)}: {section['title']}")
        content = generate_section(llm, section)
        sections.append(f"## {section['title']}\n\n{content}")
        time.sleep(1)  # Rate limiting
        progress_bar.progress((i + 1) / len(outline))
    
    status_text.text("Content generation complete!")
    time.sleep(0.5)
    status_text.empty()
    progress_bar.empty()
    
    return "\n\n".join(sections)

def optimize_content(llm, content: str, keywords: List[str]) -> str:
    """Optimize content for SEO"""
    prompt = PromptTemplate(
        input_variables=["content", "keywords"],
        template="""
        Optimize this blog content for SEO focusing on: {keywords}
        
        Original content:
        {content}
        
        Improvements needed:
        1. Natural keyword integration
        2. Readability improvements
        3. Meta description
        4. Heading structure
        5. Internal linking suggestions
        
        Return optimized content in markdown.
        """
    )
    
    chain = prompt | llm
    return chain.invoke({
        "content": content,
        "keywords": ", ".join(keywords)
    })

def review_content(llm, content: str) -> str:
    """Review and improve content quality"""
    prompt = PromptTemplate(
        input_variables=["content"],
        template="""
        Review and improve this blog content:
        
        {content}
        
        Check for:
        1. Grammar and spelling
        2. Logical flow
        3. Consistency
        4. Tone appropriateness
        5. Clarity
        
        Return improved content.
        """
    )
    
    chain = prompt | llm
    return chain.invoke({"content": content})

def convert_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML"""
    return markdown(markdown_content)

def convert_to_pdf(markdown_content: str) -> bytes:
    """Convert markdown to PDF"""
    html = convert_to_html(markdown_content)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Simple conversion - for better results consider using WeasyPrint
    for line in html.split('\n'):
        if line.startswith('<h1>'):
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt=line.replace('<h1>', '').replace('</h1>', ''), ln=1)
            pdf.set_font("Arial", size=12)
        elif line.startswith('<h2>'):
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt=line.replace('<h2>', '').replace('</h2>', ''), ln=1)
            pdf.set_font("Arial", size=12)
        elif line.strip():
            pdf.multi_cell(0, 5, txt=line.replace('<p>', '').replace('</p>', ''))
    
    return pdf.output(dest='S').encode('latin1')

def create_download_button(content: str, format_type: str, file_name: str):
    """Create a download button for the content"""
    if format_type == "markdown":
        file_ext = "md"
        mime_type = "text/markdown"
        data = content.encode(CONFIG["encoding"])
    elif format_type == "html":
        file_ext = "html"
        mime_type = "text/html"
        data = convert_to_html(content).encode(CONFIG["encoding"])
    elif format_type == "pdf":
        file_ext = "pdf"
        mime_type = "application/pdf"
        data = convert_to_pdf(content)
    elif format_type == "txt":
        file_ext = "txt"
        mime_type = "text/plain"
        data = content.encode(CONFIG["encoding"])
    
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{file_name}.{file_ext}">Download {file_ext.upper()}</a>'
    st.markdown(href, unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    st.title("📝 HR Blog Post Generator")
    st.markdown("Generate SEO-optimized HR blog posts in multiple formats")
    
    setup_environment()
    
    if not os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
        st.error("Please set HUGGINGFACEHUB_API_TOKEN in secrets.toml or environment variables")
        return
    
    # Sidebar controls
    with st.sidebar:
        st.header("Configuration")
        topic_option = st.radio(
            "Select topic source:",
            ("Choose from trending", "Enter custom topic")
        )
        
        if topic_option == "Choose from trending":
            selected_topic = st.selectbox(
                "Select trending HR topic:",
                get_trending_topics()
            )
        else:
            selected_topic = st.text_input("Enter your custom topic:", "Remote Work Policies")
        
        output_format = st.selectbox(
            "Select output format:",
            ["markdown", "html", "pdf", "txt"]
        )
        
        generate_button = st.button("Generate Blog Post")
    
    # Main content area
    if generate_button:
        with st.spinner("Initializing..."):
            llm = initialize_llm()
        
        st.subheader(f"Generating: {selected_topic}")
        
        # Research phase
        with st.expander("Research Details", expanded=False):
            research_data = research_topic(selected_topic)
            st.json(research_data)
        
        # Outline generation
        with st.status("Creating outline..."):
            outline = create_outline(llm, research_data)
            st.json([section["title"] for section in outline])
        
        # Content generation
        full_content = generate_full_content(llm, outline)
        
        # Optimization
        with st.status("Optimizing for SEO..."):
            optimized_content = optimize_content(llm, full_content, research_data["keywords"])
        
        # Review
        with st.status("Final review..."):
            final_content = review_content(llm, optimized_content)
        
        # Display results
        st.subheader("Generated Blog Post")
        st.markdown(final_content)
        
        # Download buttons
        st.subheader("Download Options")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_download_button(final_content, "markdown", "hr_blog")
        with col2:
            create_download_button(final_content, "html", "hr_blog")
        with col3:
            create_download_button(final_content, "pdf", "hr_blog")
        with col4:
            create_download_button(final_content, "txt", "hr_blog")

if __name__ == "__main__":
    main()


