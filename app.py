from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import pandas as pd
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from openai import OpenAI
import PyPDF2
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# --- Mail Configuration ---
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your-email-password'     # Replace with your email password
mail = Mail(app)

# --- Configuration ---
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key
# mysql://avnadmin:AVNS_YnuYKaOcXuCNZSbe6Ls@mysql-8bf3a23-charantejak1123-1503.e.aivencloud.com:21887/defaultdb
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://avnadmin:AVNS_YnuYKaOcXuCNZSbe6Ls@mysql-8bf3a23-charantejak1123-1503.e.aivencloud.com:21887/defaultdb'  # Replace with your DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}

# --- Initialize extensions ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

client = OpenAI(
    api_key="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",  # Replace with your OpenAI API key
    base_url="https://openrouter.ai/api/v1"
)

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables_once():
    if not hasattr(app, 'db_initialized'):
        db.create_all()
        app.db_initialized = True

# --- Authentication Routes ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('signup'))
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please sign in.', 'success')
        return redirect(url_for('signin'))
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Signed in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('signin'))
    return render_template('signin.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('signin'))

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Hello, {current_user.email}! <a href='/logout'>Logout</a> <a href='/change_password'>Change Password</a>"

# --- Password Reset Routes ---
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(user.email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)

            msg = Message(subject="Password Reset Request",
                          recipients=[user.email])
            msg.body = f"""Hello,

To reset your password, please click the link below:

{reset_url}

If you did not request this password reset, please ignore this email.

Thanks,
Your App Team
"""
            try:
                mail.send(msg)
                flash('Password reset link has been sent to your email.', 'info')
            except Exception as e:
                print(f"Failed to send email: {e}")
                flash('Failed to send reset email. Please try again later.', 'danger')
        else:
            flash('Email not found.', 'danger')
        return redirect(url_for('signin'))
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('signin'))
    if request.method == 'POST':
        user = User.query.filter_by(email=email).first()
        if user:
            password = request.form['password']
            user.set_password(password)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('signin'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('signin'))
    return render_template('reset_password.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        if not current_user.check_password(old_password):
            flash('Old password is incorrect.', 'danger')
            return redirect(url_for('change_password'))
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully. Please sign in again.', 'success')
        logout_user()
        return redirect(url_for('signin'))
    return render_template('change_password.html')

# --- Feedback Analyzer Functions ---
def correct_text(text):
    return str(TextBlob(text).correct())

def analyze_sentiment_and_stars(text):
    score = sia.polarity_scores(text)['compound']
    if score >= 0.05:
        sentiment = "Positive"
    elif score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    if score >= 0.5:
        stars = 5
    elif score >= 0.05:
        stars = 4
    elif score > -0.05:
        stars = 3
    elif score > -0.5:
        stars = 2
    else:
        stars = 1

    return sentiment, stars

def generate_summary(text_list):
    combined_text = " ".join(text_list)
    prompt = (
        "Summarize the following customer feedback for a business report:\n\n"
        f"{combined_text}\n\n"
        "Format:\n"
        "- One-sentence executive summary.\n"
        "- 3-5 bullet points highlighting key trends or issues.\n"
        "- Brief recommendation or next steps.\n"
        "Use a professional and engaging tone."
    )

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        if response and response.choices and len(response.choices) > 0:
            summary = response.choices[0].message.content
            return summary
        else:
            return "Summary could not be generated (empty response)."
    except Exception as e:
        print(f"Summary generation failed: {e}")
        return "Summary could not be generated (error occurred)."

def extract_feedbacks_from_pdf(file_stream):
    reader = PyPDF2.PdfReader(file_stream)
    feedbacks = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            feedbacks.extend(lines)
    return feedbacks

# --- Main Routes ---
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    error = None
    star_values = None
    summary_text = None
    show_result = False
    feedback_list = []
    df = None

    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash("No file uploaded", "danger")
        else:
            try:
                filename = file.filename.lower()
                if filename.endswith('.csv'):
                    df = pd.read_csv(file)
                elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                    df = pd.read_excel(file)
                elif filename.endswith('.pdf'):
                    feedbacks = extract_feedbacks_from_pdf(file)
                    if not feedbacks:
                        raise Exception("No feedbacks found in PDF.")
                    df = pd.DataFrame({'Feedback': feedbacks})
                else:
                    flash("Unsupported file type. Please upload a CSV, Excel, or PDF file.", "danger")
                    return render_template(
                        'index.html',
                        active_section='csv',
                        error=error,
                        star_values=star_values,
                        summary=summary_text,
                        show_result=show_result,
                        feedback_list=feedback_list
                    )

                if 'Feedback' not in df.columns:
                    flash("File must have a 'Feedback' column or lines.", "danger")
                else:
                    df['Corrected'] = df['Feedback'].apply(correct_text)
                    df[['Sentiment', 'Stars']] = df['Feedback'].apply(lambda x: pd.Series(analyze_sentiment_and_stars(x)))
                    star_counts = df['Stars'].value_counts().sort_index()
                    star_values = [int(star_counts.get(i, 0)) for i in range(1, 6)]
                    summary_text = generate_summary(df['Corrected'].tolist())
                    show_result = True
                    feedback_list = df[['Corrected', 'Sentiment']].to_dict(orient='records')
                    # Save both summary and data for download
                    df.to_pickle('static/result.pkl')
                    with open('static/summary.txt', 'w', encoding='utf-8') as f:
                        f.write(summary_text)
                    flash("File processed successfully!", "success")
            except Exception as e:
                flash(f"Error processing file: {e}", "danger")

    return render_template(
        'index.html',
        active_section='csv',
        error=error,
        star_values=star_values,
        summary=summary_text,
        show_result=show_result,
        feedback_list=feedback_list
    )

@app.route('/download_result', methods=['GET'])
@login_required
def download_result():
    file_format = request.args.get('format')
    try:
        df = pd.read_pickle('static/result.pkl')
        with open('static/summary.txt', 'r', encoding='utf-8') as f:
            summary_text = f.read()
    except Exception:
        flash("No result available. Please analyze feedback first.", "danger")
        return redirect(url_for('index'))

    download_df = df[['Feedback', 'Sentiment', 'Stars']].copy()

    def get_star_unicode(stars):
        return "★" * int(stars)

    if file_format == 'csv':
        output = io.StringIO()
        download_df.to_csv(output, index=False)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name="result.csv"
        )
    elif file_format == 'excel':
        output = io.BytesIO()
        download_df.to_excel(output, index=False)
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name="result.xlsx"
        )
    elif file_format == 'pdf':
        download_df['Stars (★)'] = download_df['Stars'].apply(get_star_unicode)
        output = io.BytesIO()
        rows_per_page = 20  # Number of reviews per PDF page

        with PdfPages(output) as pdf:
            # --- First page: AI Summary ---
            fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 size
            ax.axis('off')
            ax.text(0.5, 0.5, "AI Summary:\n\n" + summary_text, fontsize=18, ha='center', va='center', wrap=True)
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

            # --- Table pages: Paginate DataFrame ---
            total_rows = len(download_df)
            num_pages = (total_rows + rows_per_page - 1) // rows_per_page
            for page in range(num_pages):
                start = page * rows_per_page
                end = min(start + rows_per_page, total_rows)
                chunk = download_df.iloc[start:end]

                fig, ax = plt.subplots(figsize=(8.27, 11.69))
                ax.axis('off')
                table = ax.table(
                    cellText=chunk.values,
                    colLabels=chunk.columns,
                    loc='center',
                    cellLoc='center'
                )
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.auto_set_column_width(col=list(range(len(chunk.columns))))
                # Optional: Add page number
                ax.text(0.99, 0.01, f"Page {page + 2}", ha='right', va='bottom', fontsize=8, transform=ax.transAxes)
                plt.tight_layout()
                pdf.savefig(fig)
                plt.close(fig)

            # --- Last page: Star Distribution Chart ---
            star_counts = download_df['Stars'].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            bars = ax.bar(star_counts.index, star_counts.values, color=['#021024','#052659','#5483B3','#7DA0CA','#C1E8FF'])
            ax.set_xlabel('Stars')
            ax.set_ylabel('Number of Feedbacks')
            ax.set_title('Feedback Star Distribution')
            ax.set_xticks([1,2,3,4,5])
            ax.set_xticklabels([f"{i} ★" for i in range(1,6)])
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom')
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        output.seek(0)
        return send_file(output, mimetype='application/pdf', as_attachment=True, download_name="result.pdf")
    else:
        flash("Invalid format.", "danger")
        return redirect(url_for('index'))


@app.route('/analyze', methods=['POST'])
@login_required
def analyze_single():
    single_error = None
    single_feedback = ""
    single_corrected = ""
    single_sentiment = ""
    single_stars = 0
    single_emoji = ""
    show_single_result = False
    show_corrected = False

    feedback = request.form.get('feedback', '').strip()
    if not feedback:
        single_error = "No feedback provided"
        flash(single_error, "danger")
    else:
        single_feedback = feedback
        single_corrected = correct_text(feedback)
        single_sentiment, single_stars = analyze_sentiment_and_stars(single_feedback)

        emoji_map = {
            "Positive": "😊",
            "Negative": "😞",
            "Neutral": "😐"
        }
        single_emoji = emoji_map.get(single_sentiment, "")

        show_single_result = True
        show_corrected = (single_corrected.strip() != single_feedback.strip())

    return render_template(
        'index.html',
        active_section='manual',
        single_error=single_error,
        single_feedback=single_feedback,
        single_corrected=single_corrected,
        single_sentiment=single_sentiment,
        single_stars=single_stars,
        single_emoji=single_emoji,
        show_single_result=show_single_result,
        show_corrected=show_corrected
    )

if __name__ == '__main__':
    app.run(debug=True)