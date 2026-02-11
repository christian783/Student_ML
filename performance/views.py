import joblib
import numpy as np
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

model = joblib.load('performance/model.pkl')

def index(request):
    return render(request, 'performance/index.html')

@api_view(['POST'])
def predict_performance(request):
    data = request.data

    try:
        hours_studied = float(data.get('hours_studied'))
        sleep_hours = float(data.get('sleep_hours'))
        previous_scores = float(data.get('previous_scores'))
        extracurricular = bool(data.get('extracurricular'))
        sample_papers = int(data.get('sample_papers'))
    except (TypeError, ValueError):
        return Response({'error': 'Invalid input types'}, status=400)

    if not (0 <= hours_studied <= 12):
        return Response({'error': 'hours_studied must be between 0 and 12'}, status=400)

    if not (3 <= sleep_hours <= 10):
        return Response({'error': 'sleep_hours must be between 3 and 10'}, status=400)

    if not (hours_studied + sleep_hours < 24):
        return Response({'error': 'Sum of hours_studied and sleep_hours must not exceed 24'}, status=400)
    
    if (extracurricular == True and hours_studied + sleep_hours == 24):
        return Response({'error': 'If extracurricular is true, sum of hours_studied and sleep_hours must be less than 24'}, status=400)

    features = np.array([[
        hours_studied,
        previous_scores,
        1 if extracurricular else 0,
        sleep_hours,
        sample_papers,
    ]])

    prediction = model.predict(features)[0]

    return Response({
        'predicted_performance_index': round(float(prediction), 2)
    })
