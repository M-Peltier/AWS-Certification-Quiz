# AWS Certification Practice Quiz

An interactive AWS Certification Practice Quiz application developed using **Python and Streamlit**. This project helps users prepare for AWS certification exams by providing a realistic exam experience with randomized questions, timed assessments, automatic grading, detailed answer explanations, and performance tracking.

## Project Overview

The AWS Certification Practice Quiz is designed to help learners test their knowledge of Amazon Web Services (AWS) cloud computing concepts and prepare for certification exams, particularly the **AWS Certified Cloud Practitioner (CLF-C02)** exam.

The application loads practice questions from a CSV file and provides an interactive web-based testing environment.

## Key Features

- **65-Minute Exam Timer:** Simulates a timed AWS certification practice exam with an automatic countdown.
- **Randomized Questions:** Shuffles questions for a different exam experience each time.
- **Randomized Answer Choices:** Changes answer order while maintaining accurate grading.
- **Multiple-Choice Questions:** Supports questions with single or multiple correct answers.
- **Automatic Grading:** Calculates scores immediately after exam submission.
- **Detailed Answer Explanations:** Helps learners understand correct and incorrect answers.
- **Score History:** Saves previous exam results using a local SQLite database.
- **Performance Tracking:** Allows users to monitor their progress over time.
- **CSV-Based Question Bank:** Makes it easy to add, remove, or update questions.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Interactive web interface |
| Pandas | CSV data processing |
| SQLite | Local exam score storage |
| PyCharm | Development environment |
| GitHub | Version control and project hosting |

## Project Structure

```text
AWS-Certification-Quiz/
├── aws_quiz_app_updated.py
├── AWS_Quiz_Bank.csv
├── requirements.txt
├── README.md
└── .gitignore
```

The SQLite score-history database is created locally when the application runs.


### Run the Application

```bash
streamlit run aws_quiz_app_updated.py
```

The application will open in your browser, typically at:

`http://localhost:8501`

## How to Use

1. Launch the AWS Certification Practice Quiz.
2. Select the available exam settings.
3. Start the practice exam.
4. Answer the AWS certification questions before the 65-minute timer expires.
5. Submit the completed exam.
6. Review your score, correct answers, and explanations.
7. View your saved score history to track your progress.
8. Start another practice exam to reinforce your AWS knowledge.

## Learning Objectives

This project supports learning and review of AWS Cloud Practitioner topics, including:

- Cloud Concepts
- Security and Compliance
- Cloud Technology and Services
- Billing, Pricing, and Support

These topics align with the major knowledge areas covered by the AWS Certified Cloud Practitioner certification.

## Future Enhancements

Potential improvements include:

- Topic-based quizzes
- Customizable exam durations
- Review of previously missed questions
- Performance dashboards and charts
- User authentication
- Cloud-based score storage
- Online deployment through Streamlit Community Cloud

## Disclaimer

This project is an independent educational resource and is not affiliated with, endorsed by, or sponsored by Amazon Web Services (AWS).

AWS and related trademarks belong to Amazon Web Services, Inc.

Practice questions are intended for educational purposes and do not represent official AWS certification exam questions.

## Project Purpose

This project was developed to combine Python programming, interactive web application development, and AWS cloud certification preparation.

It demonstrates practical experience with Python, Streamlit, CSV data management, SQLite databases, and GitHub version control while providing a useful tool for cloud computing education.
