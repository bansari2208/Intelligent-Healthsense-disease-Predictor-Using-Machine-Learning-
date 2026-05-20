from django.shortcuts import render
import joblib
import numpy as np
import warnings
try:
    from sklearn.exceptions import InconsistentVersionWarning
except Exception:  # Fallback for older/newer sklearn variants
    InconsistentVersionWarning = UserWarning

# Load trained model
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
    model = joblib.load("model.pkl")

def home(request):
    return render(request, "index.html")


def predict_disease(request):
    if request.method == "POST":
        symptoms = []

        # Collect 17 symptoms from form
        for i in range(1, 18):
            value = request.POST.get(f"symptom_{i}", "None")
            symptoms.append(value)

        # Convert text → numbers (temporary encoding)
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()

        encoded = [le.fit_transform(symptoms)]

        prediction = model.predict(encoded)

        return render(request, "result.html", {"result": prediction[0]})

    return render(request, "index.html")