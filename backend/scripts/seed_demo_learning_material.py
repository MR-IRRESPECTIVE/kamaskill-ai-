import os
import sys
from fpdf import FPDF
from pypdf import PdfReader

# Add parent dir to path so we can import models and database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Competency, LearningMaterial, MaterialCompetency

def generate_pdf(filepath):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    content = [
        "Data Visualization Fundamentals",
        "",
        "1. Purpose and Value of Data Visualization",
        "Data visualization is the graphical representation of information and data. By using visual elements like charts, graphs, and maps, data visualization tools provide an accessible way to see and understand trends, outliers, and patterns in data. In the context of government and public service, visualizing data effectively bridges the gap between complex datasets and decision-makers, allowing for data-driven policy making.",
        "",
        "2. Data Types and Choosing Appropriate Visual Representations",
        "Before selecting a chart, one must understand the data type. Categorical data (e.g., departments, regions) requires different handling than continuous numerical data (e.g., budget allocations over time, population density). Continuous data often pairs well with line charts or scatter plots, whereas categorical data is typically best represented with bar charts or pie charts. The choice of representation dictates how easily the audience can extract the intended message.",
        "",
        "3. Bar Charts",
        "Bar charts are the workhorse of data visualization. They are best used for comparing different categories or tracking changes over time when the changes are large. A horizontal bar chart is particularly useful when category names are long, as it provides ample space for labels without rotating the text. It is a strict rule that the y-axis of a bar chart must start at zero; otherwise, the visual comparison of the bars' lengths becomes highly misleading.",
        "",
        "4. Line Charts",
        "Line charts are optimal for displaying continuous data over a period of time. They excel at showing trends, accelerations, decelerations, and volatility. When plotting multiple lines on a single chart to compare different groups, it is recommended to limit the number of lines to four or five to avoid a 'spaghetti chart' which confuses the reader. Unlike bar charts, the y-axis on a line chart does not strictly need to start at zero, provided the axis is clearly labeled to show the baseline.",
        "",
        "5. Scatter Plots",
        "Scatter plots are used to observe and show relationships or correlations between two numeric variables. For example, plotting 'training hours' against 'productivity score' might reveal a positive correlation. Scatter plots can also help identify outliers or clusters within a dataset. Adding a trendline (line of best fit) can help guide the viewer's eye to the general direction of the relationship.",
        "",
        "6. Histograms",
        "Histograms look similar to bar charts but serve a completely different purpose. They are used to show the distribution of a single continuous variable by dividing the data into 'bins' or intervals. For instance, displaying the age distribution of employees in a department. Because the data is continuous, there should be no gaps between the bars in a histogram, unlike the distinct gaps present in a bar chart.",
        "",
        "7. Comparing Categories",
        "When comparing multiple categories across different sub-groups, clustered (grouped) bar charts or stacked bar charts are common. Clustered bar charts are best for comparing the individual sub-group values, while stacked bar charts are better for showing the total size of the category alongside the proportion of its sub-components. However, comparing the inner segments of a stacked bar chart can be cognitively difficult unless they are the bottom-most segment.",
        "",
        "8. Showing Trends Over Time",
        "While line charts are the default for trends over time, area charts can also be used. An area chart is essentially a line chart with the area below the line filled in. Stacked area charts are useful to show how the total composition changes over time. However, similar to stacked bar charts, tracking the exact value of the middle layers in a stacked area chart is challenging.",
        "",
        "9. Showing Relationships/Correlation",
        "Besides scatter plots, bubble charts can add a third dimension to relationship visualization by varying the size of the data points. Heatmaps use color intensity to show relationships between two variables in a matrix format, which is particularly useful for identifying 'hot spots' or concentrations of data.",
        "",
        "10. Choosing an Appropriate Chart",
        "The most critical decision in data visualization is choosing the right chart for the right goal. If the goal is comparison, use bar charts. If the goal is trend analysis, use line charts. If the goal is composition, use stacked bars or (sparingly) pie charts. If the goal is relationship, use scatter plots. Always prioritize the audience's ability to quickly grasp the insight over creating a complex, novel visual.",
        "",
        "11. Visual Hierarchy",
        "Visual hierarchy involves guiding the viewer's eye to the most important information first. This is achieved through size, color, contrast, and placement. The most critical data point or finding should be the most visually prominent element on the page. Background elements like grid lines and axes should be subdued (e.g., light grey) to prevent them from competing with the actual data.",
        "",
        "12. Labels and Annotations",
        "Relying solely on legends forces the viewer to constantly look back and forth, increasing cognitive load. Direct labeling-placing the category name directly next to the line or bar-is heavily preferred. Annotations (short explanatory text on the chart) should be used to point out specific anomalies, events, or key takeaways, directly telling the reader why a specific spike or drop occurred.",
        "",
        "13. Axes and Scale",
        "Proper scaling is crucial for honest visualization. Dual y-axes (having two different scales on the left and right) should generally be avoided because they can artificially create the illusion of correlation where none exists by manipulating the scales. If two variables have vastly different scales, it is usually better to create two separate, vertically aligned charts.",
        "",
        "14. Avoiding Misleading Visualizations",
        "Visualizations can easily mislead if principles are ignored. Common deceptive practices include: truncating the y-axis on a bar chart to exaggerate differences, using 3D effects which distort proportions (making slices in the front of a 3D pie chart look artificially larger), and cherry-picking timeframes to show a desired trend while ignoring the broader context.",
        "",
        "15. Clarity and Simplicity",
        "The concept of the 'data-to-ink ratio', introduced by Edward Tufte, suggests that every drop of 'ink' on a chart should present data. Non-data ink (heavy gridlines, unnecessary borders, decorative 3D effects, background shading) should be erased. A clean, minimalist design ensures that the data itself stands out without distraction.",
        "",
        "16. Color Usage and Accessibility",
        "Color should be used strategically, not purely for decoration. A single color should be used for a bar chart unless highlighting a specific bar. When using color to distinguish categories, ensure the palette is accessible to color-blind users (e.g., avoiding red-green combinations). Relying on intensity (light to dark) or patterns in addition to hue can make charts more accessible.",
        "",
        "17. Dashboard Design",
        "A dashboard should provide a high-level overview at a glance. The most important metrics (Key Performance Indicators) should be placed at the top left, as this is where western readers look first. Interactive elements like filters can allow users to drill down, but the default view must immediately answer the user's primary business question without requiring interaction.",
        "",
        "18. Interpreting Visual Patterns",
        "When analyzing a visualization, look for the 'four standard patterns': Trend (the general direction), Seasonality (repeating cycles), Outliers (points far outside the normal range), and Variance (how spread out the data is). Understanding these allows a data analyst to formulate hypotheses about the underlying causes.",
        "",
        "19. Common Visualization Mistakes",
        "A frequent mistake is using a pie chart for too many categories. Pie charts should be limited to 2-4 categories; beyond that, it becomes impossible to accurately compare the sizes of the slices. Another mistake is using a sequential color palette (light to dark) for categorical data (like different departments) where a diverging or qualitative palette would be appropriate.",
        "",
        "20. Communicating Insights to Decision-Makers",
        "Decision-makers often lack the time to interpret complex charts. Therefore, every chart presented to leadership should have a clear, descriptive title that states the conclusion (e.g., 'Q3 Revenue Dropped Due to Supply Chain Issues' rather than 'Q3 Revenue Analysis'). The visual should act as evidence for the title's claim, making the takeaway immediate and undeniable."
    ]

    for line in content:
        pdf.multi_cell(0, 10, txt=line)
    
    pdf.output(filepath)
    print(f"Generated PDF: {filepath}")

def seed_database(filepath):
    db = SessionLocal()
    
    # 1. Read the PDF using pypdf to ensure it works with the existing pipeline
    reader = PdfReader(filepath)
    extracted_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    
    num_pages = len(reader.pages)
    title = "Data Visualization Fundamentals"
    filename = os.path.basename(filepath)
    
    # 2. Idempotency check: see if it already exists
    existing_material = db.query(LearningMaterial).filter(LearningMaterial.title == title).first()
    
    if existing_material:
        print("Material already exists, updating...")
        existing_material.extracted_text = extracted_text
        existing_material.pages = num_pages
        material = existing_material
    else:
        print("Creating new LearningMaterial...")
        material = LearningMaterial(
            filename=filename,
            title=title,
            extracted_text=extracted_text,
            pages=num_pages
        )
        db.add(material)
        db.flush() # get ID
        
    # 3. Find the Competency
    comp = db.query(Competency).filter(Competency.name == "Data Visualization").first()
    if not comp:
        print("Error: Data Visualization competency not found!")
        db.close()
        return

    # 4. Map it
    existing_mapping = db.query(MaterialCompetency).filter(
        MaterialCompetency.material_id == material.id,
        MaterialCompetency.competency_id == comp.id
    ).first()
    
    if existing_mapping:
        existing_mapping.relevance = 100.0
        print("Updated existing MaterialCompetency mapping.")
    else:
        mapping = MaterialCompetency(
            material_id=material.id,
            competency_id=comp.id,
            relevance=100.0
        )
        db.add(mapping)
        print("Created MaterialCompetency mapping.")
        
    db.commit()
    db.close()
    print("Database seeding completed.")

if __name__ == "__main__":
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_viz_fundamentals.pdf")
    generate_pdf(pdf_path)
    seed_database(pdf_path)
