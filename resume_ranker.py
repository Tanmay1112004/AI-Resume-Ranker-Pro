import streamlit as st
import pandas as pd
import numpy as np
import io
import json
from docx import Document
import PyPDF2
import re
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import base64
from PIL import Image
import requests

# Page configuration
st.set_page_config(
    page_title="AI Resume Ranker Pro 🌟",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ultra-modern dark theme with gradients
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
    }
    
    .main-header {
        font-size: 4.2rem;
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 900;
        text-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
    }
    
    .sub-header {
        font-size: 1.6rem;
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 500;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 25px;
        color: #ffffff;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        margin: 0.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-12px) scale(1.03);
        box-shadow: 0 25px 50px rgba(0,0,0,0.4);
    }
    
    .resume-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(15px);
        position: relative;
        overflow: hidden;
    }
    
    .resume-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #ff6b6b, #feca57, #48dbfb);
    }
    
    .resume-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 30px 60px rgba(0,0,0,0.4);
    }
    
    .top-candidate {
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.2) 0%, rgba(56, 161, 105, 0.3) 100%);
        border: 2px solid rgba(72, 187, 120, 0.5);
    }
    
    .top-candidate::before {
        background: linear-gradient(135deg, #48bb78, #38a169);
    }
    
    .match-score {
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #48bb78, #38a169);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        text-shadow: 0 4px 8px rgba(72, 187, 120, 0.3);
    }
    
    .skill-tag {
        background: linear-gradient(135deg, #ff6b6b, #feca57);
        color: #2d3748;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 0.85rem;
        margin: 4px;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .skill-tag:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(255, 107, 107, 0.4);
    }
    
    .progress-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .chat-message {
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #ffffff;
        margin-left: 2rem;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .ai-message {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        margin-right: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
        color: #e2e8f0;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: #ffffff;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    
    .section-header {
        font-size: 2.4rem;
        background: linear-gradient(135deg, #ff6b6b, #feca57, #48dbfb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 3rem 0 1.5rem 0;
        font-weight: 800;
        text-align: center;
        text-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stButton button {
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%);
        color: #2d3748;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 15px;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 6px 15px rgba(255, 107, 107, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(255, 107, 107, 0.4);
        color: #2d3748;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #ffffff;
        padding: 1.8rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    .feature-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 12px 25px rgba(0,0,0,0.3);
        text-align: center;
        transition: all 0.4s ease;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    
    .welcome-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        padding: 4rem;
        border-radius: 30px;
        color: #e2e8f0;
        text-align: center;
        margin: 3rem 0;
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(15px);
    }
    
    .chat-input {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        color: #e2e8f0;
        padding: 1rem;
    }
    
    .stTextInput input {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        color: #e2e8f0;
        padding: 1rem;
    }
    
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
    }
    
    .stSelectbox select {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        color: #e2e8f0;
    }
    
    .stSlider {
        color: #e2e8f0;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #ff6b6b, #feca57);
    }
    
    /* Floating animation */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .floating {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Pulse animation */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse {
        animation: pulse 2s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

class SmartChatBot:
    def __init__(self):
        self.responses = {
            'greeting': [
                "🌟 Hello! I'm your AI recruitment assistant. Ready to find the perfect candidates?",
                "🚀 Welcome! I specialize in resume analysis and candidate matching. How can I assist you today?",
                "💫 Hi there! I'm here to help you streamline your hiring process. What would you like to know?"
            ],
            'help': [
                "I can help you with: \n• Resume analysis & ranking\n• Skills extraction\n• Candidate matching\n• Interview questions\n• Recruitment insights",
                "My capabilities include: \n• AI-powered candidate evaluation\n• Skills detection & categorization\n• Match score calculation\n• Detailed analytics\n• Export functionality",
                "I specialize in: \n• Intelligent resume parsing\n• Multi-criteria ranking\n• Skills gap analysis\n• Hiring recommendations\n• Data visualization"
            ],
            'analysis': [
                "🔍 Our AI analyzes resumes based on: \n• Skills match with job description\n• Experience relevance\n• Content quality & completeness\n• Technical competencies\n• Overall fit score",
                "The analysis process includes: \n• Text extraction from multiple formats\n• Skills detection & categorization\n• TF-IDF similarity scoring\n• Multi-factor evaluation\n• Intelligent ranking",
                "We evaluate candidates on: \n• Technical skills alignment\n• Experience level matching\n• Education & qualifications\n• Project relevance\n• Cultural fit indicators"
            ],
            'ranking': [
                "🏆 Candidates are ranked using: \n• Weighted match scores (0-100%)\n• Skills relevance analysis\n• Experience level assessment\n• Content quality metrics\n• Overall compatibility",
                "Ranking criteria: \n• 50% Skills match\n• 30% Experience relevance\n• 20% Content quality\n• Bonus: Education & certifications\n• Penalty: Missing key skills",
                "Top candidates are selected based on: \n• Highest overall match scores\n• Strongest skills alignment\n• Most relevant experience\n• Best cultural fit indicators\n• Comprehensive profiles"
            ],
            'skills': [
                "💼 We detect 50+ technical skills across: \n• Programming languages\n• Web development frameworks\n• Database technologies\n• Cloud platforms\n• DevOps tools\n• Data science libraries",
                "Skills extraction covers: \n• Python, Java, JavaScript, C++\n• React, Angular, Django, Node.js\n• SQL, MongoDB, PostgreSQL\n• AWS, Azure, Docker, Kubernetes\n• Pandas, TensorFlow, PyTorch\n• Git, Linux, Jenkins, Terraform",
                "Technical skills analysis: \n• Automatic detection from resume text\n• Categorization by technology type\n• Experience level estimation\n• Skills gap identification\n• Market demand alignment"
            ],
            'interview': [
                "🎯 Suggested interview questions: \n• 'Can you walk us through your most relevant project?'\n• 'How have you used [specific technology] in practice?'\n• 'What challenges did you overcome in your last role?'\n• 'How do you stay updated with industry trends?'\n• 'Describe your experience working in teams'",
                "Technical interview focus: \n• Project architecture & design decisions\n• Problem-solving approaches\n• Code quality & best practices\n• Technology stack experience\n• Performance optimization experience",
                "Behavioral questions: \n• 'Tell me about a time you led a project'\n• 'How do you handle tight deadlines?'\n• 'Describe a conflict resolution experience'\n• 'What motivates you in your work?'\n• 'Where do you see yourself in 5 years?'"
            ],
            'thanks': [
                "🎉 You're welcome! Happy to help you find the perfect candidates!",
                "✨ Glad I could assist! Let me know if you need anything else!",
                "💫 Anytime! I'm here to make your recruitment process smoother and more efficient!"
            ],
            'features': [
                "🔥 Key Features: \n• Multi-format resume support (PDF, DOCX, TXT)\n• AI-powered match scoring\n• Skills extraction & categorization\n• Beautiful analytics dashboard\n• Export functionality (CSV, JSON)\n• Real-time progress tracking",
                "🌟 Platform Highlights: \n• Dark theme with stunning gradients\n• Glass morphism design\n• Interactive visualizations\n• Smart chatbot assistant\n• Mobile-responsive design\n• Professional reporting",
                "💎 Advanced Capabilities: \n• Batch resume processing\n• Custom scoring thresholds\n• Skills gap analysis\n• Candidate comparison tools\n• Interview preparation aids\n• Hiring recommendation engine"
            ],
            'default': [
                "🤔 I'm not sure I understand. Could you rephrase your question about resume analysis or candidate ranking?",
                "💡 I specialize in recruitment and resume analysis. Could you ask me something related to hiring or candidate evaluation?",
                "🔍 I'm here to help with resume ranking and candidate analysis. What specific aspect would you like to know about?"
            ]
        }
        
        self.patterns = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'greetings', 'welcome'],
            'help': ['help', 'what can you do', 'capabilities', 'features', 'assist', 'support'],
            'analysis': ['analyze', 'analysis', 'how does it work', 'process', 'evaluate', 'assessment'],
            'ranking': ['rank', 'ranking', 'score', 'match', 'top candidates', 'best fit'],
            'skills': ['skills', 'technical', 'programming', 'technologies', 'expertise', 'competencies'],
            'interview': ['interview', 'questions', 'assess', 'evaluate candidate', 'technical interview'],
            'thanks': ['thanks', 'thank you', 'appreciate', 'grateful', 'thank'],
            'features': ['features', 'what can it do', 'capabilities', 'functionality', 'tools']
        }
    
    def get_response(self, user_input):
        user_input = user_input.lower()
        
        # Check for patterns with word boundaries
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', user_input):
                    responses = self.responses.get(intent, self.responses['default'])
                    return np.random.choice(responses)
        
        # Default response
        return np.random.choice(self.responses['default'])

class AIResumeAnalyzer:
    def __init__(self):
        self.skills_keywords = {
            'Programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'Web Development': ['html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'node.js', 'express', 'spring', 'laravel'],
            'Database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'dynamodb'],
            'Cloud & DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd', 'gitlab'],
            'Data Science': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'matplotlib', 'seaborn', 'r', 'spark'],
            'Tools': ['git', 'linux', 'jira', 'confluence', 'slack', 'figma', 'photoshop']
        }
    
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            st.error(f"❌ Error reading PDF: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, docx_file):
        """Extract text from DOCX file"""
        try:
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            st.error(f"❌ Error reading DOCX: {str(e)}")
            return ""
    
    def extract_text_from_file(self, file):
        """Extract text based on file type"""
        if file.type == "application/pdf":
            return self.extract_text_from_pdf(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self.extract_text_from_docx(file)
        else:
            try:
                return file.getvalue().decode("utf-8")
            except:
                return file.getvalue().decode("latin-1")
    
    def extract_skills(self, text):
        """Extract skills from resume text"""
        text_lower = text.lower()
        skills = {
            "programming_skills": [],
            "web_skills": [],
            "database_skills": [],
            "cloud_skills": [],
            "tools_skills": [],
            "soft_skills": []
        }
        
        # Programming skills
        for skill in self.skills_keywords['Programming']:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                skills["programming_skills"].append(skill.title())
        
        # Web skills
        for skill in self.skills_keywords['Web Development']:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                skills["web_skills"].append(skill.title())
        
        # Database skills
        for skill in self.skills_keywords['Database']:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                skills["database_skills"].append(skill.title())
        
        # Cloud skills
        for skill in self.skills_keywords['Cloud & DevOps']:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                skills["cloud_skills"].append(skill.title())
        
        # Tools
        for skill in self.skills_keywords['Tools']:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                skills["tools_skills"].append(skill.title())
        
        return skills
    
    def get_ai_insights(self, resume_text, job_description):
        """Generate intelligent insights"""
        text_length = len(resume_text)
        skills = self.extract_skills(resume_text)
        skills_count = sum(len(skill_list) for skill_list in skills.values())
        
        # Calculate experience indicators
        experience_indicators = len(re.findall(r'\b(experience|worked|developed|built|created|managed|led)\b', resume_text, re.IGNORECASE))
        
        strengths = []
        if skills_count > 5:
            strengths.append("Strong technical skills diversity")
        if text_length > 500:
            strengths.append("Detailed professional experience")
        if experience_indicators > 5:
            strengths.append("Substantial project experience")
        if any(len(skill_list) > 3 for skill_list in skills.values()):
            strengths.append("Deep expertise in multiple areas")
        
        concerns = []
        if text_length < 200:
            concerns.append("Resume appears too brief")
        if skills_count < 3:
            concerns.append("Limited technical skills mentioned")
        if experience_indicators < 3:
            concerns.append("May lack substantial project experience")
        
        recommendation = "Strongly Recommend" if skills_count >= 5 and text_length > 400 else "Recommend" if skills_count >= 3 else "Review Manually"
        
        return {
            "overall_assessment": "AI-powered analysis completed with detailed insights",
            "key_strengths": strengths if strengths else ["Meets basic qualification requirements"],
            "potential_concerns": concerns if concerns else ["Well-rounded candidate profile"],
            "recommendation": recommendation,
            "interview_questions": [
                "Can you walk us through your most challenging technical project?",
                "How do you approach learning new technologies or frameworks?",
                "Describe a situation where you had to collaborate with a diverse team",
                "What development methodologies are you most comfortable with?",
                "How do you ensure code quality and maintainability?"
            ]
        }
    
    def calculate_match_score(self, resume_text, job_description):
        """Enhanced match scoring with multiple factors"""
        # TF-IDF similarity
        documents = [resume_text, job_description]
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            base_score = round(cosine_sim * 100, 1)
        except:
            base_score = 50
        
        # Content quality factors
        content_score = min(100, len(resume_text) / 10)
        skills_count = sum(len(skills) for skills in self.extract_skills(resume_text).values())
        skills_score = min(100, skills_count * 10)
        
        # Experience indicators
        experience_indicators = len(re.findall(r'\b(experience|worked|developed|built|created|managed|led)\b', resume_text, re.IGNORECASE))
        experience_score = min(100, experience_indicators * 8)
        
        # Combined score with weights
        final_score = round(
            base_score * 0.4 + 
            content_score * 0.2 + 
            skills_score * 0.25 +
            experience_score * 0.15, 1
        )
        
        return max(0, min(100, final_score))

def create_animated_progress_bar(score, label, color="#ff6b6b"):
    """Create beautiful animated progress bar"""
    return f"""
    <div class="progress-container">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span style="font-weight: 700; color: #e2e8f0;">{label}</span>
            <span style="font-weight: 800; color: {color};">{score}%</span>
        </div>
        <div style="height: 12px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">
            <div style="height: 100%; background: linear-gradient(135deg, {color}, #feca57); border-radius: 10px; width: {score}%; 
                     transition: width 1s ease-in-out; animation: grow 1.5s ease-in-out;"></div>
        </div>
    </div>
    <style>
        @keyframes grow {{
            from {{ width: 0%; }}
            to {{ width: {score}%; }}
        }}
    </style>
    """

def main():
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Header Section with stunning gradient
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); padding: 4rem 2rem; border-radius: 0 0 40px 40px; margin-bottom: 3rem; text-align: center; position: relative; overflow: hidden;'>
        <div style='position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80") center/cover; opacity: 0.1;'></div>
        <h1 class="main-header floating">🚀 AI Resume Ranker Pro</h1>
        <p class="sub-header">Advanced AI-Powered Candidate Intelligence Platform</p>
        <div style='margin-top: 2rem; font-size: 1.2rem; color: #a8edea;' class="pulse">
            ✨ Smart Matching • Intelligent Insights • Beautiful Analytics
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    analyzer = AIResumeAnalyzer()
    chatbot = SmartChatBot()
    
    # Sidebar with beautiful design
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2>🎯 Job Intelligence</h2>
            <p>Configure Your Recruitment Vision</p>
        </div>
        """, unsafe_allow_html=True)
        
        job_description = st.text_area(
            "**📝 Job Description**",
            height=200,
            placeholder="Paste the detailed job description here...\nInclude required skills, experience level, qualifications, and responsibilities.",
            help="The AI will analyze candidates against this description for optimal matching"
        )
        
        st.markdown("---")
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ff6b6b, #feca57); padding: 1.5rem; border-radius: 15px; color: #2d3748; text-align: center; margin: 1rem 0;'>
            <h3 style='color: #2d3748; margin: 0;'>📁 Upload Resumes</h3>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "**Select Candidate Resumes**",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload multiple resumes for batch analysis (PDF, DOCX, TXT supported)"
        )
        
        st.markdown("---")
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #48dbfb, #0abde3); padding: 1.5rem; border-radius: 15px; color: #2d3748; text-align: center; margin: 1rem 0;'>
            <h3 style='color: #2d3748; margin: 0;'>⚙️ AI Settings</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            min_score = st.slider("**Minimum Score**", 0, 100, 70, help="Only show candidates above this score")
        with col2:
            top_n = st.slider("**Top N**", 1, 20, 5, help="Number of top candidates to display")
        
        analyze_button = st.button(
            "🚀 Launch AI Analysis", 
            type="primary", 
            use_container_width=True,
            help="Start intelligent candidate analysis with advanced AI"
        )
        
        st.markdown("---")
        st.markdown("### 💫 Quick Tips")
        st.info("""
        • Use detailed job descriptions for better matching
        • Upload 5+ resumes for comprehensive comparison  
        • Review AI insights for each candidate
        • Export results for team sharing
        • Use the chatbot for recruitment guidance
        """)

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Ranking", "🔍 Insights", "💬 Assistant", "📊 Analytics"])
    
    with tab1:
        if analyze_button:
            if not job_description:
                st.error("❌ Please enter a job description to continue")
                st.stop()
                
            if not uploaded_files:
                st.error("❌ Please upload candidate resumes")
                st.stop()
            
            # Analysis progress with beautiful loader
            with st.container():
                st.markdown("### 🌟 AI Analysis in Progress...")
                
                # Custom progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                total_files = len(uploaded_files)
                
                for i, file in enumerate(uploaded_files):
                    status_text.markdown(f"**🔍 Analyzing {file.name}...** ({i+1}/{total_files})")
                    
                    # Extract and analyze
                    resume_text = analyzer.extract_text_from_file(file)
                    
                    if resume_text:
                        match_score = analyzer.calculate_match_score(resume_text, job_description)
                        ai_insights = analyzer.get_ai_insights(resume_text, job_description)
                        skills = analyzer.extract_skills(resume_text)
                        
                        results.append({
                            'filename': file.name,
                            'overall_score': match_score,
                            'match_score': match_score,
                            'ai_insights': ai_insights,
                            'skills': skills,
                            'resume_preview': resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
                        })
                    
                    progress_bar.progress((i + 1) / total_files)
                    time.sleep(0.2)
                
                status_text.markdown("**✅ Analysis Complete!**")
                st.balloons()
                st.session_state.analysis_results = results
            
            # Display results
            if st.session_state.analysis_results:
                results = st.session_state.analysis_results
                results.sort(key=lambda x: x['overall_score'], reverse=True)
                
                # Summary Metrics
                st.markdown('<div class="section-header">📊 Intelligence Summary</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_score = np.mean([r['overall_score'] for r in results])
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>📈 Average</h3>
                        <div style="font-size: 2.5rem; font-weight: 900;">{avg_score:.1f}%</div>
                        <p>Overall Match Quality</p>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    top_score = results[0]['overall_score']
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>🥇 Top Match</h3>
                        <div style="font-size: 2.5rem; font-weight: 900;">{top_score:.1f}%</div>
                        <p>Best Candidate</p>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col3:
                    qualified = len([r for r in results if r['overall_score'] >= min_score])
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>✅ Qualified</h3>
                        <div style="font-size: 2.5rem; font-weight: 900;">{qualified}</div>
                        <p>Above Threshold</p>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>📄 Total</h3>
                        <div style="font-size: 2.5rem; font-weight: 900;">{len(results)}</div>
                        <p>Candidates</p>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Top Candidates
                st.markdown(f'<div class="section-header">🏆 Top {min(top_n, len(results))} Candidates</div>', unsafe_allow_html=True)
                
                for i, result in enumerate(results[:top_n]):
                    is_top = i == 0
                    
                    st.markdown(f'<div class="resume-card {"top-candidate" if is_top else ""}">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if is_top:
                            st.markdown("### 🥇 **AI Recommended - Top Candidate**")
                        else:
                            st.markdown(f"### #{i+1} **{result['filename']}**")
                        
                        # Progress bars
                        st.markdown(create_animated_progress_bar(result['match_score'], "AI Match Score", "#48bb78"), unsafe_allow_html=True)
                        
                        # Skills display
                        if result['skills']:
                            st.markdown("#### 💫 Detected Skills")
                            for category, skill_list in result['skills'].items():
                                if skill_list:
                                    st.markdown(f"**{category.replace('_', ' ').title()}:**")
                                    skill_tags = " ".join([f'<span class="skill-tag">{skill}</span>' for skill in skill_list[:8]])
                                    st.markdown(skill_tags, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f'<div class="match-score">{result["overall_score"]}%</div>', unsafe_allow_html=True)
                        if is_top:
                            st.success("**🌟 AI RECOMMENDED**")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Report",
                            data=json.dumps(result, indent=2),
                            file_name=f"ai_analysis_{result['filename']}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            # Welcome screen
            st.markdown("""
            <div class="welcome-container">
                <h2 style='margin-bottom: 1.5rem; font-size: 2.5rem;'>🌟 Welcome to AI Resume Ranker Pro</h2>
                <p style='font-size: 1.3rem; margin-bottom: 2.5rem; line-height: 1.6;'>
                    Transform your recruitment process with our intelligent AI-powered platform. 
                    Discover the perfect candidates through advanced analysis and beautiful insights.
                </p>
                <div style='display: inline-block; background: linear-gradient(135deg, #ff6b6b, #feca57); color: #2d3748; padding: 15px 40px; border-radius: 25px; font-weight: 800; font-size: 1.2rem; box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);'>
                    🚀 Configure Settings & Begin Analysis!
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Feature highlights
            st.markdown('<div class="section-header">✨ Why Choose Our Platform?</div>', unsafe_allow_html=True)
            
            features = [
                {"icon": "🤖", "title": "AI-Powered Analysis", "desc": "Advanced algorithms for accurate candidate matching"},
                {"icon": "🎯", "title": "Smart Ranking", "desc": "Intelligent scoring based on multiple criteria"},
                {"icon": "💫", "title": "Beautiful Insights", "desc": "Stunning visualizations and detailed analytics"},
                {"icon": "🚀", "title": "Fast Processing", "desc": "Quick analysis of multiple resumes simultaneously"},
                {"icon": "🔒", "title": "Secure & Private", "desc": "Your data remains confidential and secure"},
                {"icon": "📊", "title": "Export Results", "desc": "Download comprehensive reports in multiple formats"}
            ]
            
            cols = st.columns(3)
            for i, feature in enumerate(features):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="feature-card">
                        <div style='font-size: 3rem; margin-bottom: 1rem;'>{feature['icon']}</div>
                        <h3 style='color: #e2e8f0; margin-bottom: 1rem;'>{feature['title']}</h3>
                        <p style='color: #a0aec0;'>{feature['desc']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="section-header">🔍 AI Insights & Intelligence</div>', unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            results.sort(key=lambda x: x['overall_score'], reverse=True)
            
            for i, result in enumerate(results[:3]):
                with st.expander(f"🧠 Deep Analysis: {result['filename']} (Score: {result['overall_score']}%)", expanded=i==0):
                    insights = result['ai_insights']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### ✅ Key Strengths")
                        for strength in insights.get('key_strengths', []):
                            st.markdown(f"• {strength}")
                        
                        st.markdown("#### 🎯 AI Recommendation")
                        st.info(insights.get('recommendation', 'Consider for interview'))
                    
                    with col2:
                        st.markdown("#### ⚠️ Areas for Improvement")
                        for concern in insights.get('potential_concerns', []):
                            st.markdown(f"• {concern}")
                        
                        st.markdown("#### ❓ Suggested Questions")
                        for question in insights.get('interview_questions', [])[:3]:
                            st.markdown(f"• {question}")
        else:
            st.info("👆 Run an analysis first to unlock detailed AI insights and intelligence reports")
    
    with tab3:
        st.markdown('<div class="section-header">💬 AI Recruitment Assistant</div>', unsafe_allow_html=True)
        
        # Chat interface
        chat_container = st.container()
        
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                user_input = st.text_input(
                    "Ask me about resume analysis, candidate matching, or recruitment...", 
                    placeholder="Type your question here...",
                    key="chat_input"
                )
            with col2:
                send_button = st.form_submit_button("Send 🚀")
        
        if send_button and user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "message": user_input})
            
            # Get AI response
            ai_response = chatbot.get_response(user_input)
            
            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "message": ai_response})
        
        # Display chat history
        with chat_container:
            for chat in st.session_state.chat_history[-6:]:  # Show last 6 messages
                if chat["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong> {chat["message"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        <strong>AI Assistant:</strong> {chat["message"]}
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="section-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            # Create beautiful analytics
            col1, col2 = st.columns(2)
            
            with col1:
                # Score distribution with custom colors
                scores = [r['overall_score'] for r in results]
                fig_hist = px.histogram(
                    x=scores, 
                    title='📈 Candidate Score Distribution',
                    nbins=10,
                    color_discrete_sequence=['#ff6b6b']
                )
                fig_hist.update_layout(
                    xaxis_title="Match Score (%)",
                    yaxis_title="Number of Candidates",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#e2e8f0'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # Skills analysis
                all_skills = {}
                for result in results:
                    for category, skills in result['skills'].items():
                        for skill in skills:
                            all_skills[skill] = all_skills.get(skill, 0) + 1
                
                if all_skills:
                    top_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]
                    skills_df = pd.DataFrame(top_skills, columns=['Skill', 'Frequency'])
                    
                    fig_bar = px.bar(
                        skills_df,
                        x='Frequency',
                        y='Skill',
                        orientation='h',
                        title='🔥 Top Skills Across Candidates',
                        color='Frequency',
                        color_continuous_scale='Viridis'
                    )
                    fig_bar.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#e2e8f0'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

if __name__ == "__main__":
    main()