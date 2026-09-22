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
    ),
    LearningMaterial(
        filename="sih_policy_ethics.pdf",
        title="Ethical Guidelines in Public Policy",
        extracted_text="Guidelines for maintaining ethical standards while designing and implementing public policies. It covers conflict of interest, transparency, and data privacy in government operations.",
        pages=15
    ),
    LearningMaterial(
        filename="sih_comm_memos.pdf",
        title="Effective Inter-departmental Communication",
        extracted_text="A framework for writing concise, actionable memos between ministries. Emphasizes clarity, professional tone, and structuring requests to minimize bureaucratic delays.",
        pages=8
    ),
    LearningMaterial(
        filename="sih_data_cleaning.pdf",
        title="Best Practices for Cleaning Survey Data",
        extracted_text="A guide to handling missing values, outliers, and duplicates in national survey datasets. Explains imputation methods and validation rules for tabular data.",
        pages=22
    ),
    LearningMaterial(
        filename="sih_sampling_methods.pdf",
        title="Sampling Strategies for Large Populations",
        extracted_text="Techniques for representative sampling in a diverse country. Covers stratified, cluster, and systematic sampling to ensure equitable demographic representation.",
        pages=30
    ),
    LearningMaterial(
        filename="sih_dashboard_design.pdf",
        title="Principles of Effective Government Dashboards",
        extracted_text="Design principles for citizen-facing transparency portals. Focuses on KPI selection, avoiding visual clutter, and mobile-responsive layouts.",
        pages=18
    ),
    LearningMaterial(
        filename="sih_impact_assessment.pdf",
        title="Conducting Policy Impact Assessments",
        extracted_text="Methodologies for evaluating the effectiveness of government schemes post-implementation. Includes defining baseline metrics and measuring socio-economic outcomes.",
        pages=35
    ),
    LearningMaterial(
        filename="sih_public_reporting.pdf",
        title="Guidelines for Public-Facing Reports",
        extracted_text="Standards for publishing open data reports. Covers narrative structuring, jargon reduction, and providing context for complex statistical findings to the general public.",
        pages=14
    ),
    LearningMaterial(
        filename="sih_predictive_modeling.pdf",
        title="Introduction to Predictive Modeling for Planners",
        extracted_text="Basics of using historical data to forecast future trends in resource allocation. Highlights the difference between correlation and causation in policy planning.",
        pages=28
    )
]

db.add_all(demo_materials)
db.commit()
for mat in demo_materials:
    db.refresh(mat)

mat_comp_mappings = [
    ("Mission Karmayogi: Data Visualization Guidelines", "Data Visualization", 95.0),
    ("Statistical Reasoning for Public Policy", "Statistical Reasoning", 90.0),
    ("Data Analysis Handbook for Government Data", "Data Analysis", 85.0),
    ("Ethical Guidelines in Public Policy", "Policy Understanding", 90.0),
    ("Effective Inter-departmental Communication", "Communication", 95.0),
    ("Best Practices for Cleaning Survey Data", "Data Analysis", 88.0),
    ("Sampling Strategies for Large Populations", "Statistical Reasoning", 92.0),
    ("Principles of Effective Government Dashboards", "Data Visualization", 89.0),
    ("Conducting Policy Impact Assessments", "Policy Understanding", 94.0),
    ("Guidelines for Public-Facing Reports", "Communication", 91.0),
    ("Introduction to Predictive Modeling for Planners", "Data Analysis", 80.0)
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

quizzes = [
    Quiz(material_id=demo_materials[0].id, title="Assessment: Data Visualization Guidelines", number_of_questions=3),
    Quiz(material_id=demo_materials[1].id, title="Assessment: Statistical Reasoning", number_of_questions=2),
    Quiz(material_id=demo_materials[2].id, title="Assessment: Government Data Analysis", number_of_questions=2),
    Quiz(material_id=demo_materials[3].id, title="Assessment: Policy Ethics", number_of_questions=4),
    Quiz(material_id=demo_materials[4].id, title="Assessment: Inter-departmental Memos", number_of_questions=4),
    Quiz(material_id=demo_materials[5].id, title="Assessment: Survey Data Cleaning", number_of_questions=4),
    Quiz(material_id=demo_materials[6].id, title="Assessment: Sampling Strategies", number_of_questions=4),
    Quiz(material_id=demo_materials[7].id, title="Assessment: Dashboard Design", number_of_questions=4),
    Quiz(material_id=demo_materials[8].id, title="Assessment: Policy Impact", number_of_questions=4),
    Quiz(material_id=demo_materials[9].id, title="Assessment: Public Reporting", number_of_questions=4),
    Quiz(material_id=demo_materials[10].id, title="Assessment: Predictive Modeling", number_of_questions=4)
]

db.add_all(quizzes)
db.commit()
for q in quizzes:
    db.refresh(q)

def get_comp_id(name):
    return next(c.id for c in competencies if c.name == name)

questions = [
    # Quiz 1: Data Viz (3 questions)
    QuizQuestion(
        quiz_id=quizzes[0].id, question="What is the primary goal of data visualization in public reporting?",
        option_a="To make reports look colorful and artistic.", option_b="To communicate insights clearly and accessibly to citizens and policymakers.", option_c="To hide underlying data flaws from the public.", option_d="To increase the page count of the annual report.",
        correct_answer="B", explanation="The guidelines emphasize clear and accessible communication of insights.", difficulty="Easy", competency_id=get_comp_id("Data Visualization")
    ),
    QuizQuestion(
        quiz_id=quizzes[0].id, question="When displaying a trend over time, which chart type is generally recommended?",
        option_a="Pie Chart", option_b="Scatter Plot", option_c="Line Chart", option_d="Bar Chart",
        correct_answer="C", explanation="Line charts are the standard recommendation for showing trends over time.", difficulty="Medium", competency_id=get_comp_id("Data Visualization")
    ),
    QuizQuestion(
        quiz_id=quizzes[0].id, question="Why is color accessibility important in government dashboards?",
        option_a="It is not important; standard colors are fine.", option_b="To ensure charts are readable by individuals with color vision deficiencies.", option_c="Because certain colors save ink when printing.", option_d="To align with the official flag colors only.",
        correct_answer="B", explanation="Ensuring accessibility for color-blind users is a key requirement.", difficulty="Easy", competency_id=get_comp_id("Data Visualization")
    ),
    # Quiz 2: Stat Reasoning (2 questions)
    QuizQuestion(
        quiz_id=quizzes[1].id, question="How can sampling bias affect the evaluation of a government scheme?",
        option_a="It makes the evaluation faster.", option_b="It has no effect on the final results.", option_c="It leads to conclusions that do not accurately represent the target population.", option_d="It automatically corrects errors in the dataset.",
        correct_answer="C", explanation="Sampling bias skews results away from the true population parameters.", difficulty="Medium", competency_id=get_comp_id("Statistical Reasoning")
    ),
    QuizQuestion(
        quiz_id=quizzes[1].id, question="What does a very low p-value (e.g., < 0.01) indicate in a hypothesis test comparing two policy outcomes?",
        option_a="Strong evidence against the null hypothesis, suggesting a significant difference.", option_b="The policy was a complete failure.", option_c="The results are definitely due to chance.", option_d="The sample size was too small.",
        correct_answer="A", explanation="A low p-value indicates that the observed data is highly unlikely under the null hypothesis.", difficulty="Hard", competency_id=get_comp_id("Statistical Reasoning")
    ),
    # Quiz 3: Data Analysis (2 questions)
    QuizQuestion(
        quiz_id=quizzes[2].id, question="What is the first step when receiving a new administrative dataset for analysis?",
        option_a="Immediately run a complex machine learning model.", option_b="Delete rows with any missing values.", option_c="Perform data quality checks and exploratory data analysis (EDA).", option_d="Publish the raw data directly to a public portal.",
        correct_answer="C", explanation="EDA and quality checks are essential first steps before deeper analysis.", difficulty="Medium", competency_id=get_comp_id("Data Analysis")
    ),
    QuizQuestion(
        quiz_id=quizzes[2].id, question="Why are reproducible research methods emphasized in government data analysis?",
        option_a="To make it harder for others to understand the code.", option_b="To ensure that analyses can be verified, audited, and updated with new data.", option_c="Because it is a requirement of the software vendors.", option_d="To increase the size of the final report.",
        correct_answer="B", explanation="Reproducibility allows for verification, auditing, and easy updates.", difficulty="Medium", competency_id=get_comp_id("Data Analysis")
    ),
    # Quiz 4: Policy Ethics (4 questions)
    QuizQuestion(
        quiz_id=quizzes[3].id, question="Which scenario best describes a conflict of interest in policy making?",
        option_a="Consulting citizens on a new environmental regulation.", option_b="Awarding a government contract to a company owned by a family member.", option_c="Attending an open public hearing on budget allocations.", option_d="Using publicly available census data for research.",
        correct_answer="B", explanation="Awarding contracts to family members compromises objective decision-making.", difficulty="Medium", competency_id=get_comp_id("Policy Understanding")
    ),
    QuizQuestion(
        quiz_id=quizzes[3].id, question="What is the primary reason for transparency in government operations?",
        option_a="To burden officials with extra paperwork.", option_b="To build public trust and ensure accountability.", option_c="To reveal confidential citizen data.", option_d="To slow down the legislative process.",
        correct_answer="B", explanation="Transparency is foundational for public trust and democratic accountability.", difficulty="Easy", competency_id=get_comp_id("Policy Understanding")
    ),
    QuizQuestion(
        quiz_id=quizzes[3].id, question="How should sensitive citizen data be handled according to ethical guidelines?",
        option_a="Sold to third parties for revenue.", option_b="Published on public dashboards for transparency.", option_c="Anonymized and secured to protect individual privacy.", option_d="Stored on unsecured personal devices for easy access.",
        correct_answer="C", explanation="Data privacy dictates that sensitive data must be anonymized and secured.", difficulty="Medium", competency_id=get_comp_id("Policy Understanding")
    ),
    QuizQuestion(
        quiz_id=quizzes[3].id, question="If a statistical officer discovers an error in a published report, what is the ethical course of action?",
        option_a="Ignore the error to avoid public embarrassment.", option_b="Secretly alter the data in the database.", option_c="Acknowledge the error and issue a formal correction.", option_d="Blame a different department for the mistake.",
        correct_answer="C", explanation="Integrity requires acknowledging and correcting errors transparently.", difficulty="Hard", competency_id=get_comp_id("Policy Understanding")
    ),
    # Quiz 5: Inter-departmental Memos (4 questions)
    QuizQuestion(
        quiz_id=quizzes[4].id, question="What is the most important element of an inter-departmental memo's structure?",
        option_a="Using complex bureaucratic jargon.", option_b="A clear, actionable subject line and bottom-line-up-front (BLUF).", option_c="Including a detailed history of the department.", option_d="Writing at least five pages of context.",
        correct_answer="B", explanation="Clarity and immediate actionability are crucial for effective memos.", difficulty="Easy", competency_id=get_comp_id("Communication")
    ),
    QuizQuestion(
        quiz_id=quizzes[4].id, question="When requesting data from another ministry, how should the request be framed?",
        option_a="Vaguely, so they can provide whatever they have.", option_b="With a precise description of the required fields, format, and deadline.", option_c="Demanding immediate compliance without explanation.", option_d="Through an informal phone call only.",
        correct_answer="B", explanation="Precise requests reduce ambiguity and bureaucratic delays.", difficulty="Medium", competency_id=get_comp_id("Communication")
    ),
    QuizQuestion(
        quiz_id=quizzes[4].id, question="Which tone is most appropriate for official government communication?",
        option_a="Highly emotional and urgent.", option_b="Casual and conversational.", option_c="Professional, objective, and respectful.", option_d="Sarcastic and critical.",
        correct_answer="C", explanation="A professional and objective tone maintains institutional respect.", difficulty="Easy", competency_id=get_comp_id("Communication")
    ),
    QuizQuestion(
        quiz_id=quizzes[4].id, question="Why is it important to minimize formatting clutter in official memos?",
        option_a="To save ink when printing.", option_b="To ensure the core message is easily readable and scannable by busy officials.", option_c="Because formatting is not allowed in government software.", option_d="To make the memo look older and more authoritative.",
        correct_answer="B", explanation="Scannability helps busy stakeholders process information quickly.", difficulty="Medium", competency_id=get_comp_id("Communication")
    ),
    # Quiz 6: Survey Data Cleaning (4 questions)
    QuizQuestion(
        quiz_id=quizzes[5].id, question="Which of the following is a common technique for handling missing values in survey data?",
        option_a="Always deleting the entire row.", option_b="Replacing them with the word 'Missing'.", option_c="Imputation using mean, median, or predictive modeling.", option_d="Ignoring them completely during analysis.",
        correct_answer="C", explanation="Imputation is a standard statistical method for handling missing data.", difficulty="Medium", competency_id=get_comp_id("Data Analysis")
    ),
    QuizQuestion(
        quiz_id=quizzes[5].id, question="What is an outlier in the context of administrative datasets?",
        option_a="A data point that perfectly matches the average.", option_b="A data point that differs significantly from other observations.", option_c="A row containing mostly missing values.", option_d="A duplicate entry in the database.",
        correct_answer="B", explanation="Outliers are extreme values that deviate significantly from the rest of the sample.", difficulty="Easy", competency_id=get_comp_id("Data Analysis")
    ),
    QuizQuestion(
        quiz_id=quizzes[5].id, question="Why is deduplication a critical step in data cleaning?",
        option_a="It artificially inflates the dataset size.", option_b="It prevents double-counting, which can severely skew analysis results.", option_c="It is required to encrypt the data.", option_d="It changes the data types of columns.",
        correct_answer="B", explanation="Double-counting leads to inaccurate aggregations and flawed policy decisions.", difficulty="Medium", competency_id=get_comp_id("Data Analysis")
    ),
    QuizQuestion(
        quiz_id=quizzes[5].id, question="What does 'data validation' primarily involve?",
        option_a="Ensuring data conforms to defined rules and constraints (e.g., age must be positive).", option_b="Backing up the database to an external server.", option_c="Creating visualizations from the raw data.", option_d="Deleting old records automatically.",
        correct_answer="A", explanation="Validation checks data against logical rules to ensure accuracy.", difficulty="Medium", competency_id=get_comp_id("Data Analysis")
    ),
    # Quiz 7: Sampling Strategies (4 questions)
    QuizQuestion(
        quiz_id=quizzes[6].id, question="What is the main advantage of stratified sampling?",
        option_a="It requires no prior knowledge of the population.", option_b="It ensures specific subgroups are adequately represented in the sample.", option_c="It is the fastest and cheapest sampling method.", option_d="It only selects individuals from one geographic location.",
        correct_answer="B", explanation="Stratification divides the population into subgroups to ensure representation.", difficulty="Medium", competency_id=get_comp_id("Statistical Reasoning")
    ),
    QuizQuestion(
        quiz_id=quizzes[6].id, question="In a nationwide survey, why might cluster sampling be preferred over simple random sampling?",
        option_a="It is more mathematically accurate.", option_b="It is more cost-effective and logistically feasible for geographically dispersed populations.", option_c="It guarantees every individual has a 100% chance of selection.", option_d="It eliminates all forms of sampling bias.",
        correct_answer="B", explanation="Cluster sampling reduces travel and administrative costs across large areas.", difficulty="Hard", competency_id=get_comp_id("Statistical Reasoning")
    ),
    QuizQuestion(
        quiz_id=quizzes[6].id, question="What characterizes systematic sampling?",
        option_a="Selecting every nth individual from a list after a random start.", option_b="Hand-picking individuals who seem most relevant.", option_c="Sending a survey to everyone in the population.", option_d="Selecting individuals based on their availability.",
        correct_answer="A", explanation="Systematic sampling relies on a fixed interval (n) through the population list.", difficulty="Medium", competency_id=get_comp_id("Statistical Reasoning")
    ),
    QuizQuestion(
        quiz_id=quizzes[6].id, question="Why must researchers be cautious of non-response bias?",
        option_a="Because it means the survey was too short.", option_b="Because individuals who do not respond may differ systematically from those who do.", option_c="Because it increases the overall sample size.", option_d="Because non-responses speed up data entry.",
        correct_answer="B", explanation="If non-responders differ from responders, the survey results will be skewed.", difficulty="Medium", competency_id=get_comp_id("Statistical Reasoning")
    ),
    # Quiz 8: Dashboard Design (4 questions)
    QuizQuestion(
        quiz_id=quizzes[7].id, question="What is a KPI in the context of government dashboards?",
        option_a="Key Public Initiative", option_b="Key Performance Indicator", option_c="Known Policy Issue", option_d="Kinetic Program Integration",
        correct_answer="B", explanation="KPI stands for Key Performance Indicator, a measurable value of success.", difficulty="Easy", competency_id=get_comp_id("Data Visualization")
    ),
    QuizQuestion(
        quiz_id=quizzes[7].id, question="Why is avoiding 'visual clutter' important on a public transparency portal?",
        option_a="It makes the website load slower.", option_b="Clutter confuses users and obscures the most important data insights.", option_c="Cluttered sites use too much server storage.", option_d="It prevents the use of pie charts.",
        correct_answer="B", explanation="A clean design directs attention to key insights without overwhelming the user.", difficulty="Medium", competency_id=get_comp_id("Data Visualization")
    ),
    QuizQuestion(
        quiz_id=quizzes[7].id, question="What does 'mobile-responsive layout' mean?",
        option_a="The dashboard only works on mobile phones.", option_b="The dashboard layout automatically adjusts to fit different screen sizes.", option_c="Users must download an app to view the data.", option_d="The website responds to voice commands.",
        correct_answer="B", explanation="Responsive design ensures accessibility across desktops, tablets, and phones.", difficulty="Easy", competency_id=get_comp_id("Data Visualization")
    ),
    QuizQuestion(
        quiz_id=quizzes[7].id, question="When designing a dashboard for the general public, what level of complexity should be targeted?",
        option_a="Highly complex statistical models without explanation.", option_b="Raw data tables only.", option_c="Clear, high-level summaries with options to drill down for more detail.", option_d="Only text-based reports with no visuals.",
        correct_answer="C", explanation="Providing high-level summaries with drill-down options serves both casual users and analysts.", difficulty="Medium", competency_id=get_comp_id("Data Visualization")
    ),
    # Quiz 9: Policy Impact (4 questions)
    QuizQuestion(
        quiz_id=quizzes[8].id, question="What is the purpose of defining 'baseline metrics' before implementing a policy?",
        option_a="To spend the entire budget early.", option_b="To provide a point of comparison to measure the policy's actual impact later.", option_c="To ensure the policy gets media coverage.", option_d="To identify which department is at fault.",
        correct_answer="B", explanation="Baselines establish the 'before' state to accurately measure the 'after' state.", difficulty="Medium", competency_id=get_comp_id("Policy Understanding")
    ),
    QuizQuestion(
        quiz_id=quizzes[8].id, question="What is a 'socio-economic outcome' in policy assessment?",
        option_a="The number of meetings held about the policy.", option_b="The amount of paper used in printing the policy document.", option_c="The measurable change in living standards, employment, or health of the target population.", option_d="The number of clicks on the government website.",
        correct_answer="C", explanation="Socio-economic outcomes measure real-world impacts on citizens' lives.", difficulty="Medium", competency_id=get_comp_id("Policy Understanding")
    ),
    QuizQuestion(
        quiz_id=quizzes[8].id, question="Why is it important to evaluate a policy 'post-implementation'?",
        option_a="To justify asking for more funding regardless of results.", option_b="To determine if the policy achieved its intended goals and identify areas for improvement.", option_c="To punish the officials who designed it.", option_d="Because it is a formality with no practical use.",
        correct_answer="B", explanation="Evaluation is critical for learning, accountability, and continuous improvement.", difficulty="Easy", competency_id=get_comp_id("Policy Understanding")
    ),
    QuizQuestion(
        quiz_id=quizzes[8].id, question="Which of the following represents a 'confounding variable' in impact assessment?",
        option_a="The primary budget allocated for the scheme.", option_b="An external factor (like an economic recession) that also affects the measured outcome.", option_c="The specific timeline of the policy rollout.", option_d="The name of the policy initiative.",
        correct_answer="B", explanation="Confounding variables make it difficult to attribute changes solely to the policy.", difficulty="Hard", competency_id=get_comp_id("Policy Understanding")
    ),
    # Quiz 10: Public Reporting (4 questions)
    QuizQuestion(
        quiz_id=quizzes[9].id, question="What is the main challenge when communicating complex statistical findings to the general public?",
        option_a="Finding enough paper to print the reports.", option_b="Translating technical jargon into clear, understandable language without losing accuracy.", option_c="Ensuring the report is over 100 pages long.", option_d="Hiding the data sources.",
        correct_answer="B", explanation="Effective public reporting requires balancing technical accuracy with accessibility.", difficulty="Medium", competency_id=get_comp_id("Communication")
    ),
    QuizQuestion(
        quiz_id=quizzes[9].id, question="How should narrative structuring be used in an open data report?",
        option_a="To tell a compelling, logical story about what the data means for the citizen.", option_b="To write fictional accounts of government success.", option_c="To confuse the reader with non-linear storytelling.", option_d="To replace the data entirely with text.",
        correct_answer="A", explanation="A strong narrative contextualizes data, making it meaningful to the reader.", difficulty="Medium", competency_id=get_comp_id("Communication")
    ),
    QuizQuestion(
        quiz_id=quizzes[9].id, question="Why is providing context crucial in public data reports?",
        option_a="It isn't; numbers speak for themselves.", option_b="Without context, citizens may misinterpret the data or draw incorrect conclusions.", option_c="It allows the government to change the data later.", option_d="It makes the report look more academic.",
        correct_answer="B", explanation="Context (like historical trends or definitions) prevents misinterpretation.", difficulty="Medium", competency_id=get_comp_id("Communication")
    ),
    QuizQuestion(
        quiz_id=quizzes[9].id, question="Which approach is best for reducing jargon in a report?",
        option_a="Using Latin phrases.", option_b="Providing a glossary and using everyday language where possible.", option_c="Assuming the reader has a PhD in statistics.", option_d="Using acronyms without spelling them out.",
        correct_answer="B", explanation="Clear language and glossaries bridge the gap between experts and the public.", difficulty="Easy", competency_id=get_comp_id("Communication")
    ),
    # Quiz 11: Predictive Modeling (4 questions)
    QuizQuestion(
        quiz_id=quizzes[10].id, question="What is the primary difference between correlation and causation?",
        option_a="Correlation proves causation.", option_b="Causation means two variables move together; correlation means one causes the other.", option_c="Correlation indicates a relationship between variables; causation indicates that one event is the result of the occurrence of the other.", option_d="They are exactly the same concept.",
        correct_answer="C", explanation="Two variables can be correlated without one causing the other (e.g., due to a third factor).", difficulty="Medium", competency_id=get_comp_id("Data Analysis")
    ),
    QuizQuestion(
        quiz_id=quizzes[10].id, question="How is historical data used in predictive modeling for policy planning?",
        option_a="To change past records.", option_b="To identify patterns and trends that can forecast future scenarios.", option_c="To prove that policies never need to change.", option_d="To automatically write new legislation.",
        correct_answer="B", explanation="Predictive models use past patterns to estimate future probabilities.", difficulty="Medium", competency_id=get_comp_id("Data Analysis")
    ),
    QuizQuestion(
        quiz_id=quizzes[10].id, question="What is a significant risk of relying heavily on predictive models for resource allocation?",
        option_a="The models might accurately predict the future.", option_b="The models may perpetuate historical biases present in the training data.", option_c="The models will use up all the government's computing power.", option_d="The models will refuse to output results.",
        correct_answer="B", explanation="If historical data contains bias, the model will likely reproduce and amplify it.", difficulty="Hard", competency_id=get_comp_id("Data Analysis")
    ),
    QuizQuestion(
        quiz_id=quizzes[10].id, question="Which of the following is an example of predictive modeling in government?",
        option_a="Summarizing last year's tax revenue.", option_b="Publishing an organizational chart of a ministry.", option_c="Using demographic trends to forecast future demand for public schools in a district.", option_d="Writing a press release about a past event.",
        correct_answer="C", explanation="Forecasting future demand based on trends is a classic predictive application.", difficulty="Medium", competency_id=get_comp_id("Data Analysis")
    )
]

db.add_all(questions)
db.commit()

print("KarmaSkill database seeded successfully.")
