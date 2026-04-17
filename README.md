# Feedback Analyzer

## Overview
The Feedback Analyzer is a full-stack web application designed to process and analyze customer feedback. It provides sentiment analysis, star ratings, and AI-generated summaries to help businesses understand customer opinions. The application supports multiple file formats (CSV, Excel, PDF) and offers both manual and bulk feedback analysis through a user-friendly interface.

## Features
- **User Authentication**: Secure signup, login, and logout functionality.
- **Password Management**: Forgot password and change password via email reset links.
- **Feedback Analysis**:
  - Sentiment classification (Positive, Negative, Neutral)
  - Star rating generation (1–5 scale)
  - Text preprocessing and correction
- **File Upload Support**:
  - CSV, Excel, PDF formats
  - Automatic feedback extraction
- **AI-Powered Summary**:
  - Generates concise business insights using OpenAI API
- **Downloadable Results**:
  - Export results as CSV, Excel, or PDF
- **Dashboard**:
  - Personalized dashboard for each user

## How It Works
1. **Authentication**  
   Users sign up and log in securely.

2. **Upload/Input Feedback**  
   Users upload files or enter feedback manually.

3. **Processing Pipeline**
   - Text cleaning and preprocessing  
   - Sentiment analysis using NLP  
   - Star rating assignment  
   - Summary generation  

4. **Results & Export**  
   Users can view and download analyzed results.

## Technologies Used
- **Backend**: Flask (Python)
- **Database**: MySQL (SQLAlchemy ORM)
- **Authentication**: Flask-Login
- **Email Service**: Flask-Mail
- **NLP**: NLTK (VADER), TextBlob
- **AI Integration**: OpenAI API
- **Data Processing**: Pandas, NumPy
- **File Handling**: PyPDF2
- **Visualization**: Matplotlib

## Database Design (SQL)

The application uses **MySQL** to store and manage user and feedback data.

### Tables Used
- **Users Table**
  - Stores user credentials and authentication details
- **Feedback Table**
  - Stores feedback text, sentiment, and ratings

### Sample SQL Queries

CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT,
    sentiment VARCHAR(10),
    rating INT
);

SELECT sentiment, COUNT(*) 
FROM feedback 
GROUP BY sentiment;

### SQL Usage
- Used for storing and retrieving feedback data  
- Used to analyze sentiment distribution  
- Integrated with Flask using SQLAlchemy ORM  

## Installation

1. Clone the repository:
git clone https://github.com/charan-teja-k/projectF.git  
cd feedback-analyzer-original  

2. Install dependencies:
pip install -r requirements.txt  

3. Set up environment variables:
Create a `.env` file and add:
SECRET_KEY=your_secret_key  
MAIL_USERNAME=your_email@example.com  
MAIL_PASSWORD=your_email_password  
OPENAI_API_KEY=your_openai_api_key  

4. Run the application:
python app.py  

5. Open in browser:
http://127.0.0.1:5000  

## Usage
- Register/Login  
- Upload or enter feedback  
- View sentiment, ratings, and summary  
- Download results  

## Folder Structure
- app.py — Main application file  
- requirements.txt — Dependencies  
- templates/ — Frontend HTML  
- static/ — Generated outputs  
- instance/ — Database storage  

## License
This project is licensed under the MIT License.

## Author
Charan Teja K
