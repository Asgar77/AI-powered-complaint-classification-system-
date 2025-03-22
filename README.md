# AI-Powered Complaint Classification System

![Screenshot 2025-03-21 164557](https://github.com/user-attachments/assets/b02fa651-8bfc-4dcd-abe2-c87839c1a645)


## 🚀 Overview

This intelligent system leverages the Groq LLM API to automatically classify customer complaints into appropriate departments. Built with Streamlit and SQLite, it provides an end-to-end solution for customer service optimization with smart routing capabilities.

### ✨ Key Features

- **LLM-Powered Classification**: Automatic routing using Groq's llama3-70b model
- **Confidence Scoring**: Detection of uncertain classifications with admin alerts
- **Email Notification System**: Automated escalation for low-confidence cases
- **SQLite Database**: Persistent storage with search capabilities
- **Dark-Themed UI**: Modern interface with responsive design

## 📋 Table of Contents

- [Demo](#-demo)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [System Architecture](#-system-architecture)
- [Contributing](#-contributing)
- [License](#-license)

## 🎮 Demo

### Complaint Submission Flow
![Screenshot 2025-03-21 164635](https://github.com/user-attachments/assets/afbc6903-c0e0-4217-9ce2-2cd17a17d044)


### Management Dashboard
![Screenshot 2025-03-21 164651](https://github.com/user-attachments/assets/bad559ce-bd56-47ab-9b4a-ea68031c25f9)


## 💻 Technology Stack

- **Frontend**: Streamlit, Custom CSS
- **Backend**: Python 3.8+
- **Database**: SQLite
- **AI/ML**: Groq API, LLaMA 3 (70B parameter model)
- **Email**: SMTP, MIME
- **Data Processing**: Pandas, Regex

## 🔧 Installation

### Prerequisites

- Python 3.8+
- Groq API access credentials
- Email account for notifications (Gmail recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-powered-complaint-classification-system.git
   cd AI-powered-complaint-classification-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure secrets:
   ```bash
   mkdir -p .streamlit
   cp .streamlit/secrets_example.toml .streamlit/secrets.toml
   # Edit secrets.toml with your credentials
   ```

## 🚀 Usage

Launch the application:

```bash
streamlit run app.py
```

The system will be available at http://localhost:8501

### Complaint Submission Process

1. Navigate to "Submit Complaint" in the sidebar
2. Complete all required fields
3. Submit the form
4. Review the AI classification results
5. Override department classification if needed

### Complaint Management

1. Select "View Complaints" in the sidebar
2. Use the search function for targeted filtering
3. View complaint details in expandable sections
4. Export all data to CSV for further analysis

## ⚙️ Configuration

### Secrets Management

Create `.streamlit/secrets.toml` with:

```toml
[email]
sender_email = "your-email@gmail.com"
sender_password = "your-app-password"
admin_email = "admin@example.com"

[groq]
api_key = "your-groq-api-key"
```

Note: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) for enhanced security.

### Department Configuration

Customize the department list in `app.py`:

```python
DEPARTMENTS = ["Technical Support", "Billing", "Customer Service", "Shipping", "General Queries"]
```

## 🏗️ System Architecture

### Component Diagram

```
┌─────────────────┐     ┌───────────────┐     ┌─────────────────┐
│ Streamlit UI    │────▶│ Core Logic    │────▶│ SQLite Database │
└─────────────────┘     └───────────────┘     └─────────────────┘
        │                       │                      
        │                       │                      
        ▼                       ▼                      
┌─────────────────┐     ┌───────────────┐              
│ Form Validation │     │ Groq LLM API  │              
└─────────────────┘     └───────────────┘              
                                │                       
                                ▼                       
                        ┌───────────────┐              
                        │ SMTP Email    │              
                        │ Notification  │              
                        └───────────────┘              
```

### Classification Process

1. Complaint text is extracted from form submission
2. Text is sent to Groq API with custom prompt
3. LLaMA 3 model analyzes content and context
4. Department classification is returned with confidence score
5. Low confidence triggers administrative review

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

Developed by Shaik Asgar ((https://github.com/Asgar77/)) | [LinkedIn](www.linkedin.com/in/shaik-asgar)
