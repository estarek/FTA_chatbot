"""
Main Streamlit application for the e-invoice chatbot.
This module integrates all components and provides the user interface.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import time
from typing import Dict, List, Tuple, Optional, Any

# Import custom modules
from data_router import DataRouter
from response_handler import ResponseHandler
from response_generator import ResponseGenerator
from visualization_generator import VisualizationGenerator

# Set page configuration
st.set_page_config(
    page_title="E-Invoice Chatbot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'language' not in st.session_state:
    st.session_state.language = 'en'

if 'selected_table' not in st.session_state:
    st.session_state.selected_table = 'All'

if 'selected_domain' not in st.session_state:
    st.session_state.selected_domain = 'All'

# Initialize components
router = DataRouter()
response_handler = ResponseHandler()
viz_generator = VisualizationGenerator()

# Function to load data
@st.cache_data
def load_data():
    """Load sample data for the chatbot"""
    try:
        # Check if real data files exist
        data_dir = "output"
        if os.path.exists(data_dir):
            data = {}
            
            # Try to load invoices data
            invoices_path = os.path.join(data_dir, "invoices.csv")
            if os.path.exists(invoices_path):
                data['invoices'] = pd.read_csv(invoices_path, low_memory=False, on_bad_lines='skip')
            
            # Try to load items data
            items_path = os.path.join(data_dir, "items.csv")
            if os.path.exists(items_path):
                data['items'] = pd.read_csv(items_path, low_memory=False, on_bad_lines='skip')
            
            # Try to load taxpayers data
            taxpayers_path = os.path.join(data_dir, "taxpayers.csv")
            if os.path.exists(taxpayers_path):
                data['taxpayers'] = pd.read_csv(taxpayers_path, low_memory=False, on_bad_lines='skip')
            
            # Try to load audit logs data
            audit_logs_path = os.path.join(data_dir, "invoice_audit_logs.csv")
            if os.path.exists(audit_logs_path):
                data['audit_logs'] = pd.read_csv(audit_logs_path, low_memory=False, on_bad_lines='skip')
            
            if data:
                return data
        
        # If real data not available, generate synthetic data
        return generate_synthetic_data()
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return generate_synthetic_data()

def generate_synthetic_data():
    """Generate synthetic data for demonstration"""
    # Generate invoices data
    invoices = pd.DataFrame({
        'invoice_number': [f'INV{i:03d}' for i in range(1, 101)],
        'invoice_datetime': pd.date_range(start='2025-01-01', periods=100),
        'buyer_emirate': np.random.choice(['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Fujairah', 'Ras Al Khaimah', 'Umm Al Quwain'], 100),
        'seller_emirate': np.random.choice(['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Fujairah', 'Ras Al Khaimah', 'Umm Al Quwain'], 100),
        'invoice_tax_amount': np.random.uniform(50, 500, 100),
        'invoice_without_tax': np.random.uniform(1000, 10000, 100),
        'invoice_type': np.random.choice(['Standard', 'Credit Note', 'Debit Note'], 100),
        'invoice_category': np.random.choice(['Goods', 'Services', 'Mixed'], 100),
        'invoice_sales_type': np.random.choice(['B2B', 'B2C', 'B2G'], 100),
        'document_status': np.random.choice(['Issued', 'Paid', 'Cancelled'], 100),
        'buyer_name': [f'Company {i}' for i in range(1, 101)],
        'buyer_trn': [f'TRN{i:06d}' for i in range(1, 101)],
        'seller_name': [f'Vendor {i % 20 + 1}' for i in range(1, 101)],
        'seller_trn': [f'TRN{i % 20 + 1:06d}' for i in range(1, 101)],
        'vat_rate': np.random.choice([5.0, 0.0], 100, p=[0.95, 0.05]),
        'vat_category': np.random.choice(['Standard', 'Zero Rated', 'Exempt'], 100, p=[0.95, 0.03, 0.02]),
        'is_anomaly': np.random.choice([0, 1], 100, p=[0.9, 0.1]),
        'anomaly_type': np.random.choice([None, 'Duplicate', 'Round Amount', 'Just Under Limit', 'Foreign Bank'], 100, p=[0.9, 0.025, 0.025, 0.025, 0.025]),
        'anomaly_risk_score': np.random.uniform(0, 1, 100)
    })
    
    # Generate items data
    items = pd.DataFrame({
        'item_id': [f'ITEM{i:04d}' for i in range(1, 301)],
        'invoice_id': [f'INV{np.random.randint(1, 101):03d}' for _ in range(1, 301)],
        'item_name': [f'Product {i % 50 + 1}' for i in range(1, 301)],
        'item_description': [f'Description for Product {i % 50 + 1}' for i in range(1, 301)],
        'quantity': np.random.randint(1, 10, 300),
        'unit_price': np.random.uniform(100, 1000, 300),
        'line_discount': np.random.uniform(0, 50, 300),
        'line_total': np.random.uniform(100, 5000, 300),
        'line_vat_amount': np.random.uniform(5, 250, 300),
        'hs_code': [f'HS{np.random.randint(1000, 9999)}' for _ in range(1, 301)]
    })
    
    # Generate taxpayers data
    taxpayers = pd.DataFrame({
        'tax_number': [f'TRN{i:06d}' for i in range(1, 51)],
        'name': [f'Company {i}' for i in range(1, 51)],
        'registration_date': pd.date_range(start='2020-01-01', periods=50),
        'vat_registration_date': pd.date_range(start='2020-01-15', periods=50),
        'legal_entity_type': np.random.choice(['LLC', 'FZE', 'Sole Proprietorship', 'Partnership'], 50),
        'business_size': np.random.choice(['Small', 'Medium', 'Large'], 50),
        'sector': np.random.choice(['Retail', 'Manufacturing', 'Services', 'Construction', 'Technology'], 50),
        'number_of_employees': np.random.randint(5, 500, 50),
        'ownership_type': np.random.choice(['Local', 'Foreign', 'Mixed'], 50),
        'tax_compliance_score': np.random.uniform(60, 100, 50),
        'bank_account': [f'AE{np.random.randint(100000000, 999999999)}' for _ in range(1, 51)],
        'bank_country': np.random.choice(['UAE', 'UAE', 'UAE', 'UAE', 'Other'], 50)
    })
    
    # Generate audit logs data
    audit_logs = pd.DataFrame({
        'log_id': [f'LOG{i:05d}' for i in range(1, 201)],
        'invoice_id': [f'INV{np.random.randint(1, 101):03d}' for _ in range(1, 201)],
        'timestamp': pd.date_range(start='2025-01-01', periods=200),
        'user_id': [f'USER{np.random.randint(1, 11):02d}' for _ in range(1, 201)],
        'action_type': np.random.choice(['Create', 'Update', 'Delete', 'View'], 200),
        'field_changed': np.random.choice(['Amount', 'Status', 'Date', 'Description', None], 200),
        'old_value': [f'Old Value {i}' for i in range(1, 201)],
        'new_value': [f'New Value {i}' for i in range(1, 201)],
        'system_notes': [f'System note {i}' for i in range(1, 201)]
    })
    
    return {
        'invoices': invoices,
        'items': items,
        'taxpayers': taxpayers,
        'audit_logs': audit_logs
    }

# Function to get example questions
def get_example_questions(lang):
    if lang == 'ar':
        return [
            "ما هو إجمالي ضريبة القيمة المضافة المحصلة في دبي؟",
            "أظهر لي توزيع الفواتير حسب الإمارة",
            "ما هي أنواع الشذوذ الأكثر شيوعًا في الفواتير؟",
            "قارن بين معدلات الامتثال الضريبي عبر القطاعات المختلفة",
            "أظهر لي اتجاه الإيرادات الشهرية على مدار العام الماضي"
        ]
    else:
        return [
            "What is the total VAT collected in Dubai?",
            "Show me the distribution of invoices by emirate",
            "What are the most common anomaly types in invoices?",
            "Compare tax compliance rates across different sectors",
            "Show me the monthly revenue trend over the past year"
        ]

# Function to translate UI text
def get_ui_text(key, lang='en'):
    ui_text = {
        'title': {
            'en': "E-Invoice Chatbot",
            'ar': "روبوت محادثة الفواتير الإلكترونية"
        },
        'subtitle': {
            'en': "Ask questions about e-invoice data in English or Arabic",
            'ar': "اطرح أسئلة حول بيانات الفواتير الإلكترونية باللغة الإنجليزية أو العربية"
        },
        'language_selector': {
            'en': "Select Language",
            'ar': "اختر اللغة"
        },
        'table_filter': {
            'en': "Filter by Table",
            'ar': "تصفية حسب الجدول"
        },
        'domain_filter': {
            'en': "Filter by Domain",
            'ar': "تصفية حسب المجال"
        },
        'api_key': {
            'en': "OpenAI API Key",
            'ar': "مفتاح API لـ OpenAI"
        },
        'api_key_help': {
            'en': "Enter your OpenAI API key to enable the chatbot",
            'ar': "أدخل مفتاح API الخاص بك لـ OpenAI لتمكين روبوت المحادثة"
        },
        'model_selector': {
            'en': "Select Model",
            'ar': "اختر النموذج"
        },
        'temperature': {
            'en': "Response Creativity",
            'ar': "إبداع الاستجابة"
        },
        'chat_placeholder': {
            'en': "Chat with the e-invoice assistant...",
            'ar': "تحدث مع مساعد الفواتير الإلكترونية..."
        },
        'send_button': {
            'en': "Send",
            'ar': "إرسال"
        },
        'clear_button': {
            'en': "Clear Chat",
            'ar': "مسح المحادثة"
        },
        'examples_button': {
            'en': "Show Examples",
            'ar': "عرض أمثلة"
        },
        'welcome_message': {
            'en': "👋 Hello! I'm your e-invoice assistant. Ask me anything about the e-invoice data, tax compliance, or fraud detection.",
            'ar': "👋 مرحبًا! أنا مساعدك للفواتير الإلكترونية. اسألني أي شيء عن بيانات الفواتير الإلكترونية أو الامتثال الضريبي أو كشف الاحتيال."
        },
        'api_key_missing': {
            'en': "⚠️ Please enter your OpenAI API key in the sidebar to enable AI responses.",
            'ar': "⚠️ الرجاء إدخال مفتاح API الخاص بك لـ OpenAI في الشريط الجانبي لتمكين ردود الذكاء الاصطناعي."
        },
        'tables': {
            'en': {
                'All': "All Tables",
                'invoices': "Invoices",
                'items': "Items",
                'taxpayers': "Taxpayers",
                'audit_logs': "Audit Logs"
            },
            'ar': {
                'All': "جميع الجداول",
                'invoices': "الفواتير",
                'items': "العناصر",
                'taxpayers': "دافعي الضرائب",
                'audit_logs': "سجلات التدقيق"
            }
        },
        'domains': {
            'en': {
                'All': "All Domains",
                'tax_compliance': "Tax Compliance",
                'fraud_detection': "Fraud Detection",
                'revenue_analysis': "Revenue Analysis",
                'geographic_distribution': "Geographic Distribution"
            },
            'ar': {
                'All': "جميع المجالات",
                'tax_compliance': "الامتثال الضريبي",
                'fraud_detection': "كشف الاحتيال",
                'revenue_analysis': "تحليل الإيرادات",
                'geographic_distribution': "التوزيع الجغرافي"
            }
        }
    }
    
    return ui_text.get(key, {}).get(lang, ui_text.get(key, {}).get('en', key))

# Function to handle chat input
def handle_chat_input(user_input):
    if not user_input.strip():
        return
    
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Get API key from session state
    api_key = st.session_state.get('api_key', '')
    
    # Initialize response generator with API key
    response_generator = ResponseGenerator(api_key)
    
    # Get data
    data = load_data()
    
    # Get query context
    query_context = router.get_query_context(
        user_input, 
        st.session_state.selected_table if st.session_state.selected_table != 'All' else None
    )
    
    # Override domain if selected in UI
    if st.session_state.selected_domain != 'All':
        query_context['relevant_domains'] = [st.session_state.selected_domain]
        query_context['primary_domain'] = st.session_state.selected_domain
    
    # Prepare response context
    response_context = response_handler.prepare_response_context(query_context, data)
    
    # Generate response
    if response_generator.has_valid_api_key():
        # Use real API
        response = response_generator.generate_response(
            user_input, 
            response_context,
            st.session_state.get('model', 'gpt-3.5-turbo')
        )
    else:
        # Use mock response
        response = response_generator.generate_mock_response(user_input, response_context)
    
    # Format response for language
    if response['success'] and response['response_text']:
        formatted_response = response_handler.format_response_for_language(
            response['response_text'], 
            query_context['language']
        )
    else:
        error_message = response.get('message', 'An error occurred')
        formatted_response = response_handler.format_response_for_language(
            error_message, 
            query_context['language']
        )
    
    # Add response to chat history
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": formatted_response,
        "visualization_type": response.get('visualization_type')
    })

# Function to clear chat history
def clear_chat_history():
    st.session_state.chat_history = []
    # Add welcome message
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": get_ui_text('welcome_message', st.session_state.language)
    })

# Function to set language
def set_language(lang):
    st.session_state.language = lang
    # Update welcome message
    if st.session_state.chat_history and st.session_state.chat_history[0]["role"] == "assistant":
        st.session_state.chat_history[0]["content"] = get_ui_text('welcome_message', lang)

# Function to show example questions
def show_example(example):
    # Set the example as the user input
    st.session_state.user_input = example

# Main function
def main():
    # Load data
    data = load_data()
    
    # Set up the sidebar
    with st.sidebar:
        # Add logo or title
        st.title(get_ui_text('title', st.session_state.language))
        
        # Language selector
        st.subheader(get_ui_text('language_selector', st.session_state.language))
        lang_col1, lang_col2 = st.columns(2)
        with lang_col1:
            if st.button("English", use_container_width=True, 
                         type="primary" if st.session_state.language == 'en' else "secondary"):
                set_language('en')
        with lang_col2:
            if st.button("العربية", use_container_width=True,
                         type="primary" if st.session_state.language == 'ar' else "secondary"):
                set_language('ar')
        
        st.divider()
        
        # Data filters
        st.subheader(get_ui_text('table_filter', st.session_state.language))
        table_options = ['All', 'invoices', 'items', 'taxpayers', 'audit_logs']
        table_display_options = [get_ui_text('tables', st.session_state.language)[option] for option in table_options]
        selected_table_display = st.selectbox(
            label="",
            options=table_display_options,
            index=table_options.index(st.session_state.selected_table),
            label_visibility="collapsed"
        )
        # Map display option back to actual value
        for option, display in zip(table_options, table_display_options):
            if display == selected_table_display:
                st.session_state.selected_table = option
        
        st.subheader(get_ui_text('domain_filter', st.session_state.language))
        domain_options = ['All', 'tax_compliance', 'fraud_detection', 'revenue_analysis', 'geographic_distribution']
        domain_display_options = [get_ui_text('domains', st.session_state.language)[option] for option in domain_options]
        selected_domain_display = st.selectbox(
            label="",
            options=domain_display_options,
            index=domain_options.index(st.session_state.selected_domain),
            label_visibility="collapsed"
        )
        # Map display option back to actual value
        for option, display in zip(domain_options, domain_display_options):
            if display == selected_domain_display:
                st.session_state.selected_domain = option
        
        st.divider()
        
        # API settings
        st.subheader(get_ui_text('api_key', st.session_state.language))
        api_key = st.text_input(
            get_ui_text('api_key_help', st.session_state.language),
            type="password",
            value=st.session_state.get('api_key', ''),
            key="api_key_input"
        )
        st.session_state.api_key = api_key
        
        st.subheader(get_ui_text('model_selector', st.session_state.language))
        model = st.selectbox(
            label="",
            options=["gpt-3.5-turbo", "gpt-4"],
            index=0,
            key="model",
            label_visibility="collapsed"
        )
        
        st.subheader(get_ui_text('temperature', st.session_state.language))
        temperature = st.slider(
            label="",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            key="temperature",
            label_visibility="collapsed"
        )
    
    # Main content area
    st.title(get_ui_text('title', st.session_state.language))
    st.caption(get_ui_text('subtitle', st.session_state.language))
    
    # Initialize chat history with welcome message if empty
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": get_ui_text('welcome_message', st.session_state.language)
        })
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)
                
                # Display visualization if available
                if message["role"] == "assistant" and "visualization_type" in message and message["visualization_type"]:
                    viz_type = message["visualization_type"]
                    
                    # Get the last user message for context
                    last_user_message = ""
                    for msg in reversed(st.session_state.chat_history):
                        if msg["role"] == "user":
                            last_user_message = msg["content"]
                            break
                    
                    if last_user_message:
                        # Get query context
                        query_context = router.get_query_context(last_user_message)
                        
                        # Generate visualization
                        fig = viz_generator.generate_visualization(viz_type, data, query_context)
                        
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
    
    # Chat input and buttons
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        user_input = st.chat_input(
            get_ui_text('chat_placeholder', st.session_state.language),
            key="user_input",
            on_submit=handle_chat_input
        )
    
    with col2:
        if st.button(get_ui_text('clear_button', st.session_state.language), use_container_width=True):
            clear_chat_history()
    
    with col3:
        if st.button(get_ui_text('examples_button', st.session_state.language), use_container_width=True):
            with st.expander("Examples", expanded=True):
                for example in get_example_questions(st.session_state.language):
                    if st.button(example):
                        show_example(example)
    
    # Warning if API key is not set
    if not st.session_state.get('api_key'):
        st.warning(get_ui_text('api_key_missing', st.session_state.language))

# Run the app
if __name__ == "__main__":
    main()
