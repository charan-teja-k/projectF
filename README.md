
# Feedback Analyzer

## Overview
The Feedback Analyzer is a web application designed to process and analyze customer feedback. It provides sentiment analysis, star ratings, and a summarized report of the feedback. The application supports multiple file formats, including CSV, Excel, and PDF, and offers a user-friendly interface for both manual and bulk feedback analysis.

## Features
- **User Authentication**: Secure signup, login, and logout functionality.
- **Password Management**: Forgot password and change password features with email-based reset links.
- **Feedback Analysis**:
  - Sentiment analysis (Positive, Negative, Neutral).
  - Star rating generation (1 to 5 stars).
  - Text correction for feedback.
- **File Upload Support**:
  - CSV, Excel, and PDF file formats.
  - Automatic extraction of feedback from uploaded files.
- **Summary Generation**: AI-powered summary of customer feedback for business reports.
- **Downloadable Results**: Export analyzed feedback as CSV, Excel, or PDF files.
- **Dashboard**: Personalized dashboard for logged-in users.

## How It Works
1. **Authentication**: Users must sign up and log in to access the application.
2. **Upload Feedback**: Upload a file containing customer feedback or manually input feedback.
3. **Analysis**: The application processes the feedback to:
   - Correct text errors.
   - Perform sentiment analysis.
   - Assign star ratings.
   - Generate a summary.
4. **Download Results**: Users can download the analyzed feedback and summary in their preferred format.

## Technologies Used
- **Backend**: Flask (Python)
- **Database**: MySQL (via SQLAlchemy)
- **Authentication**: Flask-Login
- **Email**: Flask-Mail
- **Sentiment Analysis**: NLTK (VADER SentimentIntensityAnalyzer)
- **Text Correction**: TextBlob
- **AI Integration**: OpenAI API
- **File Handling**: Pandas, PyPDF2
- **Visualization**: Matplotlib

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/charan-teja-k/projectF.git
   cd feedback-analyzer-original
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add the following variables:
     ```env
     SECRET_KEY=your_secret_key
     MAIL_USERNAME=your_email@example.com
     MAIL_PASSWORD=your_email_password
     OPENAI_API_KEY=your_openai_api_key
     ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Access the application at `http://127.0.0.1:5000`.

## Usage
- **Sign Up**: Create an account to access the application.
- **Upload Feedback**: Upload a file or manually input feedback for analysis.
- **View Results**: Check the sentiment, star ratings, and summary.
- **Download Results**: Export the results in your preferred format.

## Folder Structure
- `app.py`: Main application file.
- `requirements.txt`: List of dependencies.
- `templates/`: HTML templates for the web interface.
- `static/`: Static files (e.g., processed results).
- `instance/`: Database file.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Author
Charan Teja K
