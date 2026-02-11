import pandas as pd
from performance.models import StudentPerformance
def run():
    df = pd.read_csv('dataset.csv')

    for _, row in df.iterrows():
        StudentPerformance.objects.create(
            hours_studied=row['study_hours'],
            previous_scores=row['Previous Scores'],
            extracurricular=row['extracurricular'],
            sleep_hours=row['sleep_hours'],
            sample_papers=row['Sample Question Papers Practiced'],
            performance_index=row['Performance Index'],
        )
    print("Data loaded successfully!")