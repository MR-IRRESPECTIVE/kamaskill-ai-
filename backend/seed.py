from database import SessionLocal, engine, Base

from models import (
    Employee,
    Competency,
    EmployeeCompetency,
    Course,
    CourseCompetency,
    Role,
    RoleCompetency,
    LearningMaterial,
    MaterialCompetency,
    Quiz,
    QuizQuestion,
    QuizAttempt,
    Assessment
)


Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Clear existing data

db.query(QuizAttempt).delete()
db.query(Assessment).delete()
db.query(QuizQuestion).delete()
db.query(Quiz).delete()
db.query(MaterialCompetency).delete()
db.query(LearningMaterial).delete()
db.query(CourseCompetency).delete()
db.query(EmployeeCompetency).delete()
db.query(Course).delete()
db.query(Employee).delete()
db.query(RoleCompetency).delete()
db.query(Role).delete()
db.query(Competency).delete()

db.commit()


# Competencies

competencies = [

    Competency(
        name="Data Analysis",
        description="Ability to analyse and interpret datasets.",
        category="Technical"
    ),

    Competency(
        name="Statistical Reasoning",
        description="Ability to apply statistical concepts and interpret results.",
        category="Technical"
    ),

    Competency(
        name="Data Visualization",
        description="Ability to communicate insights through effective visualizations.",
        category="Technical"
    ),

    Competency(
        name="Communication",
        description="Ability to communicate findings clearly to stakeholders.",
        category="Behavioural"
    ),

    Competency(
        name="Policy Understanding",
        description="Understanding of policy implications of statistical information.",
        category="Domain"
    )
]


db.add_all(competencies)
db.commit()


# Refresh IDs
for competency in competencies:
    db.refresh(competency)


# Employee

employee = Employee(
    name="Rahul Sharma",
    email="rahul.sharma@gov.in",
    department="Statistics Department",
    role="Statistical Officer",
    experience=4
)

db.add(employee)
db.commit()
db.refresh(employee)


# Employee Competencies

levels = {
    "Data Analysis": (72, 85),
    "Statistical Reasoning": (48, 80),
    "Data Visualization": (55, 80),
    "Communication": (76, 75),
    "Policy Understanding": (68, 70)
}


for competency in competencies:

    current, required = levels[competency.name]

    db.add(
        EmployeeCompetency(
            employee_id=employee.id,
            competency_id=competency.id,
            current_level=current,
            required_level=required
        )
    )


# Courses

courses = [

    Course(
        title="Advanced Statistical Reasoning",
        description=(
            "Statistical inference, hypothesis testing, "
            "sampling and statistical interpretation."
        ),
        difficulty="Intermediate",
        duration=6,
        content=(
            "This course covers statistical reasoning, "
            "sampling methods, hypothesis testing and "
            "interpretation of statistical results."
        )
    ),

    Course(
        title="Data Visualization Fundamentals",
        description=(
            "Learn how to communicate data insights "
            "using effective visualizations."
        ),
        difficulty="Beginner",
        duration=4,
        content=(
            "Charts, graphs, dashboards, visual storytelling "
            "and communicating insights."
        )
    ),

    Course(
        title="Advanced Data Analysis",
        description=(
            "Practical methods for analysing government datasets."
        ),
        difficulty="Advanced",
        duration=8,
        content=(
            "Data cleaning, exploratory analysis, statistical "
            "analysis and interpretation."
        )
    )
]


db.add_all(courses)
db.commit()

for course in courses:
    db.refresh(course)


# Course → Competency mapping

competency_map = {
    "Advanced Statistical Reasoning": {
        "Statistical Reasoning": 90,
        "Data Analysis": 70
    },

    "Data Visualization Fundamentals": {
        "Data Visualization": 95,
        "Communication": 60
    },

    "Advanced Data Analysis": {
        "Data Analysis": 95,
        "Statistical Reasoning": 75
    }
}


for course in courses:

    mappings = competency_map[course.title]

    for competency_name, coverage in mappings.items():

        competency = next(
            c for c in competencies
            if c.name == competency_name
        )

        db.add(
            CourseCompetency(
                course_id=course.id,
                competency_id=competency.id,
                coverage=coverage
            )
        )


db.commit()
db.close()

# Create roles
statistical_officer = Role(
    name="Statistical Officer",
    description="Government officer responsible for statistical analysis, reporting and interpretation."
)

data_analyst = Role(
    name="Data Analyst",
    description="Professional responsible for analysing datasets and communicating data insights."
)

db.add_all([
    statistical_officer,
    data_analyst
])

db.commit()

db.refresh(statistical_officer)
db.refresh(data_analyst)

# Role competency requirements

role_requirements = {
    "Statistical Officer": {
        "Data Analysis": 85,
        "Statistical Reasoning": 80,
        "Data Visualization": 80,
        "Communication": 75,
        "Policy Understanding": 70
    },

    "Data Analyst": {
        "Data Analysis": 90,
        "Statistical Reasoning": 75,
        "Data Visualization": 85,
        "Communication": 75
    }
}

roles = {
    "Statistical Officer": statistical_officer,
    "Data Analyst": data_analyst
}

for role_name, requirements in role_requirements.items():

    role = roles[role_name]

    for competency_name, required_level in requirements.items():

        competency = next(
            c for c in competencies
            if c.name == competency_name
        )

        db.add(
            RoleCompetency(
                role_id=role.id,
                competency_id=competency.id,
                required_level=required_level
            )
        )

db.commit()

# --- SIH DEMO QUIZZES ---
print("Seeding demo quizzes...")

demo_materials = [
    LearningMaterial(
        filename="sih_data_viz_guide.pdf",
        title="Mission Karmayogi: Data Visualization Guidelines",
        extracted_text="This document outlines the standard guidelines for visualizing data across ministries. It covers best practices for creating clear, accessible, and impactful charts and dashboards for public reporting.",
        pages=12
    ),
    LearningMaterial(
        filename="sih_stat_reasoning_manual.pdf",
        title="Statistical Reasoning for Public Policy",
        extracted_text="An essential manual for statistical officers. Topics include hypothesis testing in social schemes, avoiding sampling bias in surveys, and interpreting p-values correctly when evaluating program outcomes.",
        pages=25
    ),
    LearningMaterial(
        filename="sih_data_analysis_handbook.pdf",
        title="Data Analysis Handbook for Government Data",
        extracted_text="A comprehensive guide to cleaning, joining, and analyzing large administrative datasets using Python and SQL. Emphasizes data quality checks and reproducible research methods.",
        pages=40
    )
]

db.add_all(demo_materials)
db.commit()
for mat in demo_materials:
    db.refresh(mat)

# Map competencies to materials
mat_comp_mappings = [
    ("Mission Karmayogi: Data Visualization Guidelines", "Data Visualization", 95.0),
    ("Statistical Reasoning for Public Policy", "Statistical Reasoning", 90.0),
    ("Data Analysis Handbook for Government Data", "Data Analysis", 85.0)
]

for title, comp_name, relevance in mat_comp_mappings:
    mat = next(m for m in demo_materials if m.title == title)
    comp = next(c for c in competencies if c.name == comp_name)
    db.add(MaterialCompetency(
        material_id=mat.id,
        competency_id=comp.id,
        relevance=relevance
    ))

db.commit()

# Create Quizzes
quizzes = [
    Quiz(
        material_id=demo_materials[0].id,
        title="Assessment: Data Visualization Guidelines",
        number_of_questions=3
    ),
    Quiz(
        material_id=demo_materials[1].id,
        title="Assessment: Statistical Reasoning",
        number_of_questions=2
    ),
    Quiz(
        material_id=demo_materials[2].id,
        title="Assessment: Government Data Analysis",
        number_of_questions=2
    )
]

db.add_all(quizzes)
db.commit()
for q in quizzes:
    db.refresh(q)

# Create Quiz Questions
questions = [
    # Quiz 1: Data Viz
    QuizQuestion(
        quiz_id=quizzes[0].id,
        question="What is the primary goal of data visualization in public reporting?",
        option_a="To make reports look colorful and artistic.",
        option_b="To communicate insights clearly and accessibly to citizens and policymakers.",
        option_c="To hide underlying data flaws from the public.",
        option_d="To increase the page count of the annual report.",
        correct_answer="B",
        explanation="The guidelines emphasize clear and accessible communication of insights.",
        difficulty="Easy",
        competency_id=next(c.id for c in competencies if c.name == "Data Visualization")
    ),
    QuizQuestion(
        quiz_id=quizzes[0].id,
        question="When displaying a trend over time, which chart type is generally recommended?",
        option_a="Pie Chart",
        option_b="Scatter Plot",
        option_c="Line Chart",
        option_d="Bar Chart",
        correct_answer="C",
        explanation="Line charts are the standard recommendation for showing trends over time.",
        difficulty="Medium",
        competency_id=next(c.id for c in competencies if c.name == "Data Visualization")
    ),
    QuizQuestion(
        quiz_id=quizzes[0].id,
        question="Why is color accessibility important in government dashboards?",
        option_a="It is not important; standard colors are fine.",
        option_b="To ensure charts are readable by individuals with color vision deficiencies.",
        option_c="Because certain colors save ink when printing.",
        option_d="To align with the official flag colors only.",
        correct_answer="B",
        explanation="Ensuring accessibility for color-blind users is a key requirement.",
        difficulty="Easy",
        competency_id=next(c.id for c in competencies if c.name == "Data Visualization")
    ),
    # Quiz 2: Stat Reasoning
    QuizQuestion(
        quiz_id=quizzes[1].id,
        question="How can sampling bias affect the evaluation of a government scheme?",
        option_a="It makes the evaluation faster.",
        option_b="It has no effect on the final results.",
        option_c="It leads to conclusions that do not accurately represent the target population.",
        option_d="It automatically corrects errors in the dataset.",
        correct_answer="C",
        explanation="Sampling bias skews results away from the true population parameters.",
        difficulty="Medium",
        competency_id=next(c.id for c in competencies if c.name == "Statistical Reasoning")
    ),
    QuizQuestion(
        quiz_id=quizzes[1].id,
        question="What does a very low p-value (e.g., < 0.01) indicate in a hypothesis test comparing two policy outcomes?",
        option_a="Strong evidence against the null hypothesis, suggesting a significant difference.",
        option_b="The policy was a complete failure.",
        option_c="The results are definitely due to chance.",
        option_d="The sample size was too small.",
        correct_answer="A",
        explanation="A low p-value indicates that the observed data is highly unlikely under the null hypothesis.",
        difficulty="Hard",
        competency_id=next(c.id for c in competencies if c.name == "Statistical Reasoning")
    ),
    # Quiz 3: Data Analysis
    QuizQuestion(
        quiz_id=quizzes[2].id,
        question="What is the first step when receiving a new administrative dataset for analysis?",
        option_a="Immediately run a complex machine learning model.",
        option_b="Delete rows with any missing values.",
        option_c="Perform data quality checks and exploratory data analysis (EDA).",
        option_d="Publish the raw data directly to a public portal.",
        correct_answer="C",
        explanation="EDA and quality checks are essential first steps before deeper analysis.",
        difficulty="Medium",
        competency_id=next(c.id for c in competencies if c.name == "Data Analysis")
    ),
    QuizQuestion(
        quiz_id=quizzes[2].id,
        question="Why are reproducible research methods emphasized in government data analysis?",
        option_a="To make it harder for others to understand the code.",
        option_b="To ensure that analyses can be verified, audited, and updated with new data.",
        option_c="Because it is a requirement of the software vendors.",
        option_d="To increase the size of the final report.",
        correct_answer="B",
        explanation="Reproducibility allows for verification, auditing, and easy updates.",
        difficulty="Medium",
        competency_id=next(c.id for c in competencies if c.name == "Data Analysis")
    )
]

db.add_all(questions)
db.commit()

print("KarmaSkill database seeded successfully.")