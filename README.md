# HR Blog Post Generator

## System Architecture

The HR Blog Post Generator is a Streamlit-based web application that integrates a Hugging Face Large Language Model (LLM) to generate SEO-optimized HR blog posts. The architecture consists of the following components:

- **Frontend (Streamlit)**: Provides the user interface to input blog topics, select formats, and download content.
- **Backend (Python, LangChain)**: Handles research, content generation, optimization, and review using the Hugging Face API.
- **LLM (Mistral-7B-Instruct-v0.2 via Hugging Face Endpoint)**: Generates structured blog content based on user-selected topics.
- **Storage (Memory-based)**: No persistent storage; all content is generated on demand and available for download.

## Agent Workflow

1. **User Input**:
   - The user selects a trending topic or enters a custom topic.
   - Chooses the output format (Markdown, HTML, PDF, TXT).
   - Clicks the 'Generate Blog Post' button.

2. **Setup & Research**:
   - The system sets up environment variables (API keys).
   - Research details (keywords, sources) are gathered.

3. **Content Generation**:
   - An outline is generated using the LLM.
   - Each section is written by invoking the LLM iteratively.

4. **Optimization & Review**:
   - The content is optimized for SEO.
   - A final review improves readability, grammar, and logical flow.

5. **Download & Output**:
   - The final content is displayed.
   - Download buttons are provided for multiple formats.

## Tools and Frameworks Used

- **Streamlit**: Web interface for user interaction.
- **LangChain**: Framework for integrating LLM workflows.
- **Hugging Face API**: Provides access to Mistral-7B-Instruct-v0.2.
- **Markdown2**: Converts generated content to HTML.
- **FPDF**: Converts blog content to a downloadable PDF.
- **Tempfile & Base64**: Handles temporary storage and encoding for downloads.

## Installation and Execution Steps

### Prerequisites
- Python 3.8+
- A Hugging Face API key
- Required dependencies installed

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/hr-blog-generator.git
   cd hr-blog-generator
   ```

2. **Set Up Virtual Environment (Optional but Recommended)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up API Key**:
   - Create a `.env` or `secrets.toml` file.
   - Add `HUGGINGFACEHUB_API_TOKEN = "your_api_key"`.

### Execution

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will launch in your default browser, allowing you to generate and download blog posts dynamically.

---

This README provides an overview of how the HR Blog Post Generator functions, including its architecture, workflow, dependencies, and setup instructions.

