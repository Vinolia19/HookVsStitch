🧶 HookVsStitch — Crochet Project Management Database

HookVsStitch is a crochet project management web application developed as a DBMS/SQL internship project.

The application combines a user-friendly crochet project interface with a relational database designed to manage projects, patterns, stitches, materials, and progress.

🌸 Features

- 🧶 Crochet project dashboard
- 📋 Project management
- 📝 Crochet pattern information
- 🪡 Stitch information and usage
- 🧵 Materials management
- 📊 Project progress tracking
- 👤 User information
- 🔎 Project Explorer
- 🗄️ Database Explorer
- 🔗 Database relationship overview
- 📚 SQL and DBMS concepts

🗄️ Database

The project uses SQLite as the database management system.

The database contains 9 main tables:

1. "users"
2. "projects"
3. "patterns"
4. "pattern_rows"
5. "stitches"
6. "row_stitches"
7. "materials"
8. "pattern_materials"
9. "progress"

The database also includes:

- A project progress summary view
- Primary keys
- Foreign keys
- Unique constraints
- Indexes
- Table relationships

🛠️ Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Jinja2
- GitHub

📁 Project Structure

HookVsStitch/
│
├── app.py
├── hookvsstitch.db
├── requirements.txt
│
├── templates/
│   └── index.html
│
└── static/
    └── style.css

🚀 Running the Project Locally

Install the required Python packages:

pip install -r requirements.txt

Run the Flask application:

python app.py

Then open the application in a browser:

http://127.0.0.1:5000

🎯 Project Purpose

The purpose of HookVsStitch is to demonstrate how a relational database can be integrated with a web application to manage structured crochet-related information.

The project demonstrates practical DBMS concepts including:

- Database normalization
- Primary and foreign keys
- One-to-many relationships
- Many-to-many relationships
- SQL joins
- Aggregate functions
- Views
- Indexes
- CRUD-oriented database access

👩‍💻 Project

HookVsStitch — Crochet Project Management Database

Developed as an SQL/DBMS internship project.
