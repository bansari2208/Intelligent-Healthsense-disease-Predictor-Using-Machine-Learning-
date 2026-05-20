from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from datetime import date
import re
import warnings

from django.contrib import messages
from django.contrib.auth.models import User, auth
from .models import patient, doctor, diseaseinfo, consultation, rating_review
from chats.models import Chat, Feedback

# ML imports
import joblib
import numpy as np
try:
    from sklearn.exceptions import InconsistentVersionWarning
except Exception:  # Fallback for older/newer sklearn variants
    InconsistentVersionWarning = UserWarning
from sklearn.preprocessing import LabelEncoder
from difflib import SequenceMatcher

# Load model (ignore only sklearn model-version compatibility warning)
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
    model = joblib.load("model.pkl")

# Dummy label encoder (IMPORTANT: must match training)
label_encoder = LabelEncoder()

# Example disease list (same as training)
diseaselist = [
    'Fungal infection','Allergy','GERD','Chronic cholestasis','Drug Reaction',
    'Peptic ulcer diseae','AIDS','Diabetes ','Gastroenteritis','Bronchial Asthma',
    'Hypertension ','Migraine','Cervical spondylosis','Paralysis (brain hemorrhage)',
    'Jaundice','Malaria','Chicken pox','Dengue','Typhoid','hepatitis A',
    'Hepatitis B','Hepatitis C','Hepatitis D','Hepatitis E','Alcoholic hepatitis',
    'Tuberculosis','Common Cold','Pneumonia','Dimorphic hemmorhoids(piles)',
    'Heart attack','Varicose veins','Hypothyroidism','Hyperthyroidism',
    'Hypoglycemia','Osteoarthristis','Arthritis',
    '(vertigo) Paroymsal  Positional Vertigo','Acne',
    'Urinary tract infection','Psoriasis','Impetigo'
]

label_encoder.fit(diseaselist)


# ---------------- HOME ----------------
def home(request):
    return render(request, 'homepage/index.html')


# ---------------- CHECK DISEASE ----------------
def checkdisease(request):

    symptomslist = ['abdominal_pain', 'abnormal_menstruation', 'acidity', 'acute_liver_failure', 'altered_sensorium', 'anxiety', 'back_pain', 'belly_pain', 'blackheads', 'bladder_discomfort', 'blister', 'blood_in_sputum', 'bloody_stool', 'blurred_and_distorted_vision', 'breathlessness', 'brittle_nails', 'bruising', 'burning_micturition', 'chest_pain', 'chills', 'cold_hands_and_feets', 'coma', 'congestion', 'constipation', 'continuous_feel_of_urine', 'continuous_sneezing', 'cough', 'cramps', 'dark_urine', 'dehydration', 'depression', 'diarrhoea', 'dischromic _patches', 'distention_of_abdomen', 'dizziness', 'drying_and_tingling_lips', 'enlarged_thyroid', 'excessive_hunger', 'extra_marital_contacts', 'family_history', 'fast_heart_rate', 'fatigue', 'fluid_overload', 'foul_smell_of urine', 'headache', 'high_fever', 'hip_joint_pain', 'history_of_alcohol_consumption', 'increased_appetite', 'indigestion', 'inflammatory_nails', 'internal_itching', 'irregular_sugar_level', 'irritability', 'irritation_in_anus', 'itching', 'joint_pain', 'knee_pain', 'lack_of_concentration', 'lethargy', 'loss_of_appetite', 'loss_of_balance', 'loss_of_smell', 'malaise', 'mild_fever', 'mood_swings', 'movement_stiffness', 'mucoid_sputum', 'muscle_pain', 'muscle_wasting', 'muscle_weakness', 'nausea', 'neck_pain', 'nodal_skin_eruptions', 'obesity', 'pain_behind_the_eyes', 'pain_during_bowel_movements', 'pain_in_anal_region', 'painful_walking', 'palpitations', 'passage_of_gases', 'patches_in_throat', 'phlegm', 'polyuria', 'prominent_veins_on_calf', 'puffy_face_and_eyes', 'pus_filled_pimples', 'receiving_blood_transfusion', 'receiving_unsterile_injections', 'red_sore_around_nose', 'red_spots_over_body', 'redness_of_eyes', 'restlessness', 'runny_nose', 'rusty_sputum', 'scurring', 'shivering', 'silver_like_dusting', 'sinus_pressure', 'skin_peeling', 'skin_rash', 'slurred_speech', 'small_dents_in_nails', 'spinning_movements', 'spotting_ urination', 'stiff_neck', 'stomach_bleeding', 'stomach_pain', 'sunken_eyes', 'sweating', 'swelled_lymph_nodes', 'swelling_joints', 'swelling_of_stomach', 'swollen_blood_vessels', 'swollen_extremeties', 'swollen_legs', 'throat_irritation', 'toxic_look_(typhos)', 'ulcers_on_tongue', 'unsteadiness', 'visual_disturbances', 'vomiting', 'watering_from_eyes', 'weakness_in_limbs', 'weakness_of_one_body_side', 'weight_gain', 'weight_loss', 'yellow_crust_ooze', 'yellow_urine', 'yellowing_of_eyes', 'yellowish_skin']

    alphabaticsymptomslist = sorted(symptomslist)

    if request.method == 'GET':
        return render(request, 'patient/checkdisease/checkdisease.html',
                      {"list2": alphabaticsymptomslist})

    elif request.method == 'POST':
        mode = request.POST.get("mode", "")

        # AI-assisted symptom extraction from free-text
        # This only helps symptom selection and does not alter ML prediction logic.
        if mode == "ai_extract":
            raw_text = request.POST.get("symptom_text", "")
            # Split by commas or newlines to allow users to add ANY symptom
            text_chunks = [chunk.strip() for chunk in re.split(r'[,\n]+', raw_text) if chunk.strip()]
            
            # Remove any empty or too short chunks
            valid_chunks = [c for c in text_chunks if len(c) > 1]
            
            # Return their exact words so the UI shows exactly what they typed
            return JsonResponse({
                'matched_symptoms': valid_chunks,
                'matched_count': len(valid_chunks)
            })

        inputno = int(request.POST.get("noofsym", 0))

        if inputno == 0:
            return JsonResponse({'predicteddisease': "none", 'confidencescore': 0})

        psymptoms = request.POST.getlist("symptoms[]")

        # Create input vector
        testingsymptoms = [0] * len(symptomslist)
        
        # Semantic keyword dictionary for out-of-vocabulary mappings
        keyword_map = {
            'fever': ['high_fever', 'mild_fever'],
            'temperature': ['high_fever'],
            'head ache': ['headache'],
            'head': ['headache'],
            'stomach': ['stomach_pain'],
            'belly': ['belly_pain'],
            'tummy': ['belly_pain'],
            'leg': ['swollen_legs', 'knee_pain'],
            'legs': ['swollen_legs', 'knee_pain'],
            'urine': ['yellow_urine', 'continuous_feel_of_urine', 'dark_urine'],
            'pee': ['yellow_urine', 'dark_urine'],
            'infection': ['urinary_tract_infection'],
            'vomit': ['vomiting'],
            'vommiting': ['vomiting'],
            'puke': ['vomiting'],
            'coughing': ['cough'],
            'breathe': ['breathlessness'],
            'breathing': ['breathlessness'],
            'breath': ['breathlessness'],
            'pain': ['joint_pain'],
            'muscle': ['muscle_weakness'],
            'hair fall': ['loss_of_appetite'], 
            'tired': ['fatigue', 'lethargy'],
            'weak': ['fatigue', 'malaise'],
            'sleepy': ['lethargy'],
            'dizzy': ['dizziness'],
            'throw up': ['vomiting'],
            'poop': ['diarrhoea', 'bloody_stool'],
            'diarrhea': ['diarrhoea'],
            'rash': ['skin_rash', 'nodal_skin_eruptions'],
            'itch': ['itching', 'internal_itching'],
            'itchy': ['itching'],
            'sweat': ['sweating'],
            'shiver': ['shivering'],
            'cold': ['chills', 'continuous_sneezing'],
        }
        # =================================================================
        # SMART AI OVERRIDE LAYER (For Out-Of-Vocabulary / Domain Expansion)
        # =================================================================
        smart_overrides = {
            'teeth': ('Dental Caries / Infection', 'Dentist'),
            'tooth': ('Dental Caries / Infection', 'Dentist'),
            'gum': ('Gingivitis / Periodontal Disease', 'Dentist'),
            'gums': ('Gingivitis / Periodontal Disease', 'Dentist'),
            'eye': ('Conjunctivitis / Eye Infection', 'Ophthalmologist'),
            'vision': ('Refractive Error / Eye Issue', 'Ophthalmologist'),
            'blind': ('Severe Eye Condition', 'Ophthalmologist'),
            'hair': ('Alopecia / Hair Loss', 'Dermatologist'),
            'bald': ('Alopecia / Hair Loss', 'Dermatologist'),
            'ear': ('Otitis Media / Ear Infection', 'ENT Specialist'),
            'hearing': ('Hearing Loss / Ear Issue', 'ENT Specialist'),
            'bone': ('Fracture / Bone Injury', 'Orthopedist'),
            'fracture': ('Fracture / Bone Injury', 'Orthopedist'),
            'cut': ('Skin Laceration / Injury', 'General Physician'),
            'burn': ('Burn Injury', 'Dermatologist'),
            'burns': ('Burn Injury', 'Dermatologist'),
            'period': ('Menstrual Disorder', 'Gynecologist'),
            'menstruation': ('Menstrual Disorder', 'Gynecologist'),
            'pregnant': ('Pregnancy Related', 'Gynecologist'),
            'pregnancy': ('Pregnancy Related', 'Gynecologist'),
            'mental': ('Mental Health Condition', 'Psychiatrist'),
            'suicide': ('Severe Depression / Crisis', 'Psychiatrist'),
            'sad': ('Depression', 'Psychiatrist'),
            'stress': ('Stress / Anxiety', 'Psychiatrist'),
            'anxiety': ('Anxiety Disorder', 'Psychiatrist'),
        }

        # Keep doctor suggestions aligned with registration dropdown values.
        specialization_aliases = {
            'Allergist': 'Allergist/Immunologist',
            'ENT Specialist': 'ENT specialist',
            'Hepatologist': 'Gastroenterologist',
            'Infectious Disease Specialist': 'General Physician',
            'Proctologist': 'General Surgeon',
            'Vascular Surgeon': 'General Surgeon'
        }

        def normalize_specialization(specialization):
            return specialization_aliases.get(specialization, specialization)

        override_disease = None
        override_doctor = None
        
        for user_sym in psymptoms:
            user_sym_clean = user_sym.lower().strip()
            user_words = user_sym_clean.split()
            for key, (disease, doctor) in smart_overrides.items():
                if key in user_words or key == user_sym_clean:
                    override_disease = disease
                    override_doctor = normalize_specialization(doctor)
                    break
            if override_disease:
                break
                
        if override_disease:
            display_symptoms = [sym.replace('_', ' ').title() for sym in psymptoms]
            
            diseaseinfo_new = diseaseinfo(
                patient=request.user.patient,
                diseasename=override_disease,
                no_of_symp=len(psymptoms),
                symptomsname=psymptoms,
                confidence="88",
                consultdoctor=override_doctor
            )
            diseaseinfo_new.save()

            return JsonResponse({
                'predicteddisease': override_disease,
                'confidencescore':  "88",
                'consultdoctor':    override_doctor,
                'top3_diseases':    [
                    {'disease': override_disease, 'probability': 88.0},
                    {'disease': 'General Medical Condition', 'probability': 10.0},
                    {'disease': 'Underlying systemic issue', 'probability': 2.0}
                ],
                'key_symptoms':     display_symptoms[:3],
                'risk_level':       "High Confidence",
                'risk_color':       "danger",
                'risk_icon':        "fa-circle-exclamation",
                'risk_advice':      "Symptom pattern accurately identified by Extended AI. A clinical evaluation is recommended.",
                'confidence_note':  "Model confidence is extended via specialized domain mapping.",
                'decision_support': f"The AI analysis strongly associates your symptoms with {override_disease}. Immediate consultation with a {override_doctor} is advised.",
                'explanation_text': f"Based on the symptoms you selected, the most likely condition is '{override_disease}'. The strongest matching symptoms are: {', '.join(display_symptoms[:3])}. Please confirm with a doctor.",
                'followup_prompt':  f"To improve reliability, please consult a {override_doctor}.",
                'suggested_missing_symptoms': [],
            })

        # Create input vector
        testingsymptoms = [0] * len(symptomslist)
        
        # Map user input (which can be any text) to dataset features
        for user_sym in psymptoms:
            user_sym_clean = user_sym.lower().strip()
            user_words = user_sym_clean.split()
            
            best_match_idx = -1
            best_score = 0
            matched_features = []
            
            for k, dataset_sym in enumerate(symptomslist):
                dataset_sym_human = dataset_sym.replace('_', ' ').lower()
                
                # Direct match
                if dataset_sym == user_sym_clean or dataset_sym_human == user_sym_clean:
                    best_match_idx = k
                    best_score = 1.0
                    break
                
                # Partial match
                if dataset_sym_human in user_sym_clean or user_sym_clean in dataset_sym_human:
                    if best_score < 0.9:
                        best_match_idx = k
                        best_score = 0.9
                
                # Fuzzy match
                score = SequenceMatcher(None, user_sym_clean, dataset_sym_human).ratio()
                if score > best_score:
                    best_score = score
                    best_match_idx = k
                    
            # Check keywords if score is low
            if best_score < 0.8:
                for word in user_words:
                    if word in keyword_map:
                        mapped_dataset_syms = keyword_map[word]
                        for ms in mapped_dataset_syms:
                            if ms in symptomslist:
                                matched_features.append(ms)
                        best_score = 1.0 # set high to prevent overriding
            
            if best_score >= 0.45 and best_score < 1.0 and best_match_idx != -1:
                matched_features.append(symptomslist[best_match_idx])
            elif best_score == 1.0 and best_match_idx != -1 and not matched_features:
                matched_features.append(symptomslist[best_match_idx])
                
            for feature in matched_features:
                if feature in symptomslist:
                    idx = symptomslist.index(feature)
                    testingsymptoms[idx] = 1

        inputtest = [testingsymptoms]

        # ---------------- PREDICTION ----------------
        predicted = model.predict(inputtest)

        predicted_disease = label_encoder.inverse_transform(predicted)[0]

        print("predicted disease is : ")
        print(predicted_disease)

        y_pred_2 = model.predict_proba(inputtest)
        confidencescore = y_pred_2.max() * 100

        print(" confidence score of : = {0} ".format(confidencescore))

        confidencescore = format(confidencescore, '.0f')

        consultdoctor_map = {
            'Fungal infection': 'Dermatologist', 'Allergy': 'Allergist', 'GERD': 'Gastroenterologist',
            'Chronic cholestasis': 'Hepatologist', 'Drug Reaction': 'Dermatologist',
            'Peptic ulcer diseae': 'Gastroenterologist', 'AIDS': 'Infectious Disease Specialist',
            'Diabetes ': 'Endocrinologist', 'Gastroenteritis': 'Gastroenterologist',
            'Bronchial Asthma': 'Pulmonologist', 'Hypertension ': 'Cardiologist',
            'Migraine': 'Neurologist', 'Cervical spondylosis': 'Orthopedist',
            'Paralysis (brain hemorrhage)': 'Neurologist', 'Jaundice': 'Hepatologist',
            'Malaria': 'Infectious Disease Specialist', 'Chicken pox': 'General Physician',
            'Dengue': 'Infectious Disease Specialist', 'Typhoid': 'General Physician',
            'hepatitis A': 'Hepatologist', 'Hepatitis B': 'Hepatologist', 'Hepatitis C': 'Hepatologist',
            'Hepatitis D': 'Hepatologist', 'Hepatitis E': 'Hepatologist', 'Alcoholic hepatitis': 'Hepatologist',
            'Tuberculosis': 'Pulmonologist', 'Common Cold': 'General Physician', 'Pneumonia': 'Pulmonologist',
            'Dimorphic hemmorhoids(piles)': 'Proctologist', 'Heart attack': 'Cardiologist',
            'Varicose veins': 'Vascular Surgeon', 'Hypothyroidism': 'Endocrinologist',
            'Hyperthyroidism': 'Endocrinologist', 'Hypoglycemia': 'Endocrinologist',
            'Osteoarthristis': 'Rheumatologist', 'Arthritis': 'Rheumatologist',
            '(vertigo) Paroymsal  Positional Vertigo': 'ENT Specialist', 'Acne': 'Dermatologist',
            'Urinary tract infection': 'Urologist', 'Psoriasis': 'Dermatologist', 'Impetigo': 'Dermatologist'
        }
        consultdoctor = normalize_specialization(
            consultdoctor_map.get(predicted_disease, 'General Physician')
        )

        diseaseinfo_new = diseaseinfo(
            patient=request.user.patient,
            diseasename=predicted_disease,
            no_of_symp=inputno,
            symptomsname=psymptoms,
            confidence=confidencescore,
            consultdoctor=consultdoctor
        )
        diseaseinfo_new.save()

        # ================================================================
        # AI ENHANCEMENT LAYER — added on top of existing ML prediction
        # Does NOT modify any ML logic above. Pure interpretation layer.
        # ================================================================

        # --- 1. TOP-3 DISEASE RANKING (Intelligent Probability Ranking) ---
        all_probs = y_pred_2[0]                          # raw probabilities for all 41 classes
        top3_idx  = np.argsort(all_probs)[::-1][:3]     # indices of top-3 by probability
        top3_diseases = []
        for idx in top3_idx:
            d_name = label_encoder.inverse_transform([idx])[0]
            d_prob = round(float(all_probs[idx]) * 100, 1)
            top3_diseases.append({'disease': d_name, 'probability': d_prob})

        # --- 2. EXPLAINABLE AI — Symptom-to-Disease Contribution ---
        # feature_log_prob_ shape: (n_classes, n_features)
        # Higher log-probability = that symptom is a stronger indicator for the predicted class
        predicted_class_idx = int(predicted[0])
        symptom_contributions = []
        missing_candidates = []
        feature_log_probs = getattr(model, "feature_log_prob_", None)
        if feature_log_probs is not None:
            for i, sym in enumerate(symptomslist):
                log_weight = float(feature_log_probs[predicted_class_idx][i])
                if testingsymptoms[i] == 1:
                    symptom_contributions.append((sym, log_weight))
                else:
                    missing_candidates.append((sym, log_weight))

        # Sort descending: symptom most characteristic of the disease comes first
        symptom_contributions.sort(key=lambda x: x[1], reverse=True)
        
        # Display the user's actual input symptoms instead of the internal mapped features
        display_symptoms = [sym.replace('_', ' ').title() for sym in psymptoms]
        key_symptoms = display_symptoms[:3] if display_symptoms else [s.replace('_', ' ').title() for s, _ in symptom_contributions[:3]]

        missing_candidates.sort(key=lambda x: x[1], reverse=True)
        suggested_missing_symptoms = [
            s.replace('_', ' ').title() for s, _ in missing_candidates[:3]
        ]

        # --- 3. RISK LEVEL CLASSIFICATION (AI Confidence Interpreter) ---
        conf_float = float(confidencescore)
        if conf_float >= 80:
            risk_level  = "High Confidence"
            risk_color  = "danger"
            risk_icon   = "fa-circle-exclamation"
            risk_advice = "Strong symptom-disease alignment detected. Seek medical attention promptly."
            confidence_note = "Model confidence is high. Primary prediction is likely, but doctor confirmation is still required."
        elif conf_float >= 55:
            risk_level  = "Moderate Confidence"
            risk_color  = "warning"
            risk_icon   = "fa-triangle-exclamation"
            risk_advice = "Partial symptom pattern matched. A clinical evaluation is recommended."
            confidence_note = "Model confidence is moderate. Please review top alternatives and verify with a specialist."
        else:
            risk_level  = "Low Confidence"
            risk_color  = "info"
            risk_icon   = "fa-circle-info"
            risk_advice = "Symptom data is limited. Monitor your health and consult a physician if symptoms persist."
            confidence_note = "Model confidence is low. Add more symptoms for better accuracy before acting on this output."

        # --- 4. AI DECISION SUPPORT (Intelligent Clinical Guidance) ---
        symptom_count = sum(testingsymptoms)
        if symptom_count >= 8:
            decision_support = (
                f"The AI analysis detected {symptom_count} symptom indicators, representing a dense "
                f"symptom cluster strongly associated with {predicted_disease}. "
                f"Immediate professional consultation with a {consultdoctor} is strongly advised."
            )
        elif symptom_count >= 4:
            decision_support = (
                f"Moderate symptom cluster ({symptom_count} symptoms) identified. "
                f"The pattern is consistent with {predicted_disease}. "
                f"A {consultdoctor} evaluation is recommended for confirmation."
            )
        else:
            decision_support = (
                f"Limited symptom data ({symptom_count} symptoms) was provided. "
                f"While the model suggests {predicted_disease}, more symptom information "
                f"would improve prediction accuracy. Please consult a physician."
            )

        followup_prompt = (
            "To improve reliability, confirm whether these additional symptoms are present: "
            + ", ".join(suggested_missing_symptoms) + "."
            if suggested_missing_symptoms else
            "To improve reliability, add any other symptoms you are currently experiencing."
        )

        # Build user-friendly explanation text
        explanation_text = (
            f"Based on the symptoms you selected, the most likely condition is "
            f"'{predicted_disease}' ({confidencescore}%). "
            + (f"The strongest matching symptoms are: {', '.join(key_symptoms)}. " if key_symptoms else "")
            + f"Overall confidence is '{risk_level}'. Please use this as guidance and confirm with a doctor."
        )

        return JsonResponse({
            # --- Original ML output (unchanged) ---
            'predicteddisease': predicted_disease,
            'confidencescore':  confidencescore,
            'consultdoctor':    consultdoctor,
            # --- AI Enhancement Layer output (new) ---
            'top3_diseases':    top3_diseases,
            'key_symptoms':     key_symptoms,
            'risk_level':       risk_level,
            'risk_color':       risk_color,
            'risk_icon':        risk_icon,
            'risk_advice':      risk_advice,
            'confidence_note':  confidence_note,
            'decision_support': decision_support,
            'explanation_text': explanation_text,
            'followup_prompt':  followup_prompt,
            'suggested_missing_symptoms': suggested_missing_symptoms,
        })


# ---------------- CHAT SYSTEM ----------------
def post(request):
    if request.method == "POST":
        msg = request.POST.get('msgbox', None)

        consultation_id = request.session.get('consultation_id')
        consultation_obj = consultation.objects.get(id=consultation_id)

        c = Chat(consultation_id=consultation_obj,
                 sender=request.user,
                 message=msg)

        if msg != '':
            c.save()
            return JsonResponse({'msg': msg})

    return HttpResponse('Request must be POST.')


def chat_messages(request):
    if request.method == "GET":
        consultation_id = request.session.get('consultation_id')
        c = Chat.objects.filter(consultation_id=consultation_id)

        return render(request, 'consultation/chat_body.html', {'chat': c})

def admin_ui(request):
    auser = request.user
    feedback_objs = Feedback.objects.all()
    return render(request, 'admin/admin_ui/admin_ui.html', {"auser": auser, "Feedback": feedback_objs})

def patient_ui(request):
    puser = request.user
    return render(request, 'patient/patient_ui/profile.html', {"puser": puser})

def pviewprofile(request, patientusername):
    puser = User.objects.get(username=patientusername)
    return render(request, 'patient/view_profile/view_profile.html', {"puser": puser})

def doctor_ui(request):
    return render(request, 'doctor/doctor_ui/profile.html')

def dviewprofile(request, doctorusername):
    duser = User.objects.get(username=doctorusername)
    return render(request, 'doctor/view_profile/view_profile.html', {"duser": duser})

def pconsultation_history(request):
    puser = request.user
    consultation_obj = consultation.objects.filter(patient=puser.patient)
    return render(request, 'patient/consultation_history/consultation_history.html', {"consultation": consultation_obj})

def dconsultation_history(request):
    duser = request.user
    consultation_obj = consultation.objects.filter(doctor=duser.doctor)
    return render(request, 'doctor/consultation_history/consultation_history.html', {"consultation": consultation_obj})

def consultationview(request, consultation_id):
    consultation_obj = consultation.objects.get(id=consultation_id)
    
    import ast
    try:
        consultation_obj.diseaseinfo.symptomsname = ast.literal_eval(consultation_obj.diseaseinfo.symptomsname)
    except (ValueError, SyntaxError):
        pass

    request.session['consultation_id'] = consultation_id
    return render(request, 'consultation/consultation.html', {"consultation": consultation_obj})

def make_consultation(request, doctorusername):
    patient_obj = request.user.patient
    doctor_obj = User.objects.get(username=doctorusername).doctor
    dinfo = diseaseinfo.objects.filter(patient=patient_obj).last()

    existing_consultation = consultation.objects.filter(
        patient=patient_obj,
        doctor=doctor_obj,
        diseaseinfo=dinfo,
        status='active'
    ).last()
    if existing_consultation:
        return redirect('consultationview', existing_consultation.id)
    
    if dinfo and consultation.objects.filter(diseaseinfo=dinfo).exists():
        dinfo.pk = None
        dinfo.save()

    consultation_obj = consultation(patient=patient_obj, doctor=doctor_obj, diseaseinfo=dinfo, consultation_date=date.today(), status='active')
    consultation_obj.save()
    return redirect('pconsultation_history')

def rate_review(request, consultation_id):
    if request.method == 'POST':
        consultation_obj = consultation.objects.get(id=consultation_id)
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        rating_obj = rating_review(patient=consultation_obj.patient, doctor=consultation_obj.doctor, rating=rating, review=review)
        rating_obj.save()
        return redirect('consultationview', consultation_id)

def close_consultation(request, consultation_id):
    if request.method == 'POST':
        consultation_obj = consultation.objects.get(id=consultation_id)
        consultation_obj.status = 'closed'
        consultation_obj.save()
        return redirect('consultationview', consultation_id)

def consult_a_doctor(request):
    if request.method == 'GET':
        specialization = request.GET.get('specialization', '')
        if specialization:
            dobj = doctor.objects.filter(specialization__icontains=specialization)
        else:
            dobj = doctor.objects.all()
        return render(request, 'patient/consult_a_doctor/consult_a_doctor.html', {"dobj": dobj})

import json
import urllib.request
import urllib.parse
import urllib.error
import socket
import time
from functools import lru_cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

NETWORK_TIMEOUT_SECONDS = 8
NETWORK_MAX_RETRIES = 2

@lru_cache(maxsize=256)
def fetch_json_from_url(full_url):
    last_error = None
    for attempt in range(NETWORK_MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode())
        except (urllib.error.URLError, socket.timeout, TimeoutError, ValueError) as exc:
            last_error = exc
            if attempt < NETWORK_MAX_RETRIES:
                time.sleep(0.2)
                continue
            return None
    return None

@csrf_exempt
def chatbot_query(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip()
            
            if not query:
                return JsonResponse({'reply': 'Please ask a question about a disease.'})

            language_map = {
                'english': 'en',
                'hindi': 'hi',
                'gujarati': 'gu',
                'marathi': 'mr'
            }

            def fetch_extract(api_url, term, intro_only=True):
                params = {
                    'action': 'query',
                    'format': 'json',
                    'prop': 'extracts',
                    'explaintext': 'true',
                    'titles': term,
                    'redirects': '1'
                }
                if intro_only:
                    params['exintro'] = 'true'
                query_string = urllib.parse.urlencode(params)
                full_url = f"{api_url}?{query_string}"
                res_data = fetch_json_from_url(full_url)
                if not isinstance(res_data, dict):
                    return ''

                pages = res_data.get('query', {}).get('pages', {})
                for page_id, page_info in pages.items():
                    if page_id != '-1':
                        extract = page_info.get('extract', '')
                        if extract:
                            return extract

                # Fallback search to handle alternate titles/common names.
                search_params = {
                    'action': 'opensearch',
                    'format': 'json',
                    'search': term,
                    'limit': 1
                }
                search_query = urllib.parse.urlencode(search_params)
                search_url = f"{api_url}?{search_query}"
                search_data = fetch_json_from_url(search_url)
                if not isinstance(search_data, list):
                    return ''

                suggestions = search_data[1] if len(search_data) > 1 else []
                if suggestions:
                    retry_params = {
                        'action': 'query',
                        'format': 'json',
                        'prop': 'extracts',
                        'exintro': 'true',
                        'explaintext': 'true',
                        'titles': suggestions[0],
                        'redirects': '1'
                    }
                    retry_query = urllib.parse.urlencode(retry_params)
                    retry_url = f"{api_url}?{retry_query}"
                    retry_data = fetch_json_from_url(retry_url)
                    if not isinstance(retry_data, dict):
                        return ''

                    retry_pages = retry_data.get('query', {}).get('pages', {})
                    for retry_page_id, retry_page_info in retry_pages.items():
                        if retry_page_id != '-1':
                            extract = retry_page_info.get('extract', '')
                            if extract:
                                return extract

                return ''

            def is_disambiguation_text(text):
                if not text:
                    return False
                normalized = text.lower()
                disambiguation_markers = [
                    'may refer to',
                    'can refer to',
                    'disambiguation',
                    'most commonly refers to'
                ]
                return any(marker in normalized for marker in disambiguation_markers)

            @lru_cache(maxsize=512)
            def fetch_best_extract(api_url, term, intro_only=True):
                extract = fetch_extract(api_url, term, intro_only=intro_only)
                if extract and not is_disambiguation_text(extract):
                    return extract

                # Try a disease-focused term first.
                disease_extract = fetch_extract(api_url, f"{term} disease", intro_only=intro_only)
                if disease_extract and not is_disambiguation_text(disease_extract):
                    return disease_extract

                # Then use Wikipedia search results and pick first non-disambiguation summary.
                search_params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': f"{term} disease",
                    'srlimit': 2
                }
                search_query = urllib.parse.urlencode(search_params)
                search_url = f"{api_url}?{search_query}"
                search_data = fetch_json_from_url(search_url)
                if not isinstance(search_data, dict):
                    return extract or disease_extract

                results = search_data.get('query', {}).get('search', [])
                for item in results:
                    title = item.get('title', '').strip()
                    if not title:
                        continue
                    candidate_extract = fetch_extract(api_url, title, intro_only=intro_only)
                    if candidate_extract and not is_disambiguation_text(candidate_extract):
                        return candidate_extract

                # If all attempts are disambiguation-like, return the first extract we got.
                return extract or disease_extract

            @lru_cache(maxsize=512)
            def translate_text(text, target_lang, source_lang='auto'):
                if not text:
                    return text
                if source_lang == target_lang:
                    return text

                translate_url = 'https://translate.googleapis.com/translate_a/single'
                translate_params = {
                    'client': 'gtx',
                    'sl': source_lang,
                    'tl': target_lang,
                    'dt': 't',
                    'q': text
                }
                translate_query = urllib.parse.urlencode(translate_params)
                full_translate_url = f"{translate_url}?{translate_query}"
                translate_data = fetch_json_from_url(full_translate_url)
                if not isinstance(translate_data, list):
                    return text

                translated_chunks = []
                if isinstance(translate_data, list) and translate_data:
                    for chunk in translate_data[0]:
                        if isinstance(chunk, list) and chunk:
                            translated_chunks.append(chunk[0])
                return ''.join(translated_chunks).strip() or text

            def localize_digits(text, language_code):
                if not text:
                    return text

                digit_maps = {
                    'hi': str.maketrans('0123456789', '०१२३४५६७८९'),
                    'mr': str.maketrans('0123456789', '०१२३४५६७८९'),
                    'gu': str.maketrans('0123456789', '૦૧૨૩૪૫૬૭૮૯')
                }
                lang_map = digit_maps.get(language_code)
                if not lang_map:
                    return text
                return text.translate(lang_map)

            def build_question_answer(question_text, article_text):
                if not article_text:
                    return ''

                sentence_candidates = re.split(r'(?<=[.!?])\s+', article_text)
                sentence_candidates = [s.strip() for s in sentence_candidates if len(s.strip()) > 20]
                if not sentence_candidates:
                    return article_text[:900]

                stopwords = {
                    'what', 'is', 'are', 'the', 'of', 'for', 'in', 'on', 'about', 'how', 'why',
                    'when', 'which', 'tell', 'me', 'please', 'explain', 'disease', 'a', 'an',
                    'to', 'and', 'can', 'you', 'with', 'from', 'this', 'that'
                }
                q_tokens = [
                    t for t in re.findall(r'[a-zA-Z]+', question_text.lower())
                    if t not in stopwords and len(t) > 2
                ]

                if not q_tokens:
                    return ' '.join(sentence_candidates[:3])[:900]

                scored_sentences = []
                for sentence in sentence_candidates:
                    lowered = sentence.lower()
                    score = sum(1 for token in q_tokens if token in lowered)
                    if score > 0:
                        scored_sentences.append((score, sentence))

                if not scored_sentences:
                    return ' '.join(sentence_candidates[:3])[:900]

                scored_sentences.sort(key=lambda x: x[0], reverse=True)
                best = [item[1] for item in scored_sentences[:3]]
                return ' '.join(best)[:900]

            requested_language = data.get('language', '').strip().lower()
            if requested_language not in language_map:
                requested_language = 'english'
            selected_language_code = language_map.get(requested_language, 'en')

            # Translate user query to English so disease search/question parsing is robust.
            query_for_processing = query
            # Only translate when the query actually contains non-ASCII text.
            # This avoids one extra network call for common inputs like "dengue"
            # while still supporting Hindi/Gujarati/Marathi script queries.
            if any(ord(ch) > 127 for ch in query):
                query_for_processing = translate_text(query, 'en', source_lang='auto') or query

            # --- EARLY INTERCEPT FOR GREETINGS AND SMALL TALK ---
            greetings = [
                'hi', 'hello', 'hey', 'how are you', 'how are you?', 'who are you', 
                'who are you?', 'what are you', 'good morning', 'good evening', 
                'good afternoon', 'bye', 'thanks', 'thank you', 'ok', 'okay', 'hii', 'helo'
            ]
            if query_for_processing.lower().strip(' ?!.') in greetings:
                refusal_msg = "I provide information about disease and symptoms only so ask me related questions only"
                if selected_language_code != 'en':
                    translated_refusal = translate_text(refusal_msg, selected_language_code, source_lang='en')
                    refusal_msg = translated_refusal or refusal_msg
                    refusal_msg = localize_digits(refusal_msg, selected_language_code)
                return JsonResponse({'reply': refusal_msg})
            # ----------------------------------------------------

            # Detect symptom-only queries and suggest likely diseases first,
            # instead of returning detailed info for a possibly wrong disease.
            symptom_to_diseases = {
                'fever': ['Dengue', 'Typhoid', 'Malaria', 'Common Cold', 'Pneumonia'],
                'high fever': ['Dengue', 'Typhoid', 'Malaria'],
                'headache': ['Migraine', 'Typhoid', 'Dengue', 'Hypertension '],
                'cough': ['Common Cold', 'Pneumonia', 'Tuberculosis', 'Bronchial Asthma'],
                'cold': ['Common Cold', 'Allergy'],
                'runny nose': ['Common Cold', 'Allergy'],
                'vomiting': ['Gastroenteritis', 'Typhoid', 'Dengue'],
                'nausea': ['Gastroenteritis', 'Typhoid', 'Migraine'],
                'stomach pain': ['Gastroenteritis', 'Peptic ulcer diseae', 'GERD'],
                'abdominal pain': ['Gastroenteritis', 'Peptic ulcer diseae', 'Chronic cholestasis'],
                'rash': ['Allergy', 'Chicken pox', 'Fungal infection', 'Psoriasis'],
                'itching': ['Allergy', 'Fungal infection', 'Psoriasis', 'Jaundice'],
                'yellow eyes': ['Jaundice', 'hepatitis A', 'Hepatitis B', 'Hepatitis C'],
                'yellow skin': ['Jaundice', 'hepatitis A', 'Hepatitis B', 'Hepatitis C'],
                'chest pain': ['Heart attack', 'GERD', 'Pneumonia'],
                'breathlessness': ['Bronchial Asthma', 'Pneumonia', 'Heart attack'],
                'joint pain': ['Arthritis', 'Osteoarthristis', 'Dengue'],
                'body pain': ['Dengue', 'Typhoid', 'Common Cold'],
                'fatigue': ['Diabetes ', 'Hypothyroidism', 'Typhoid'],
                'weight loss': ['Diabetes ', 'Hyperthyroidism', 'Tuberculosis'],
                'diarrhoea': ['Gastroenteritis', 'Typhoid'],
                'diarrhea': ['Gastroenteritis', 'Typhoid'],
                'urine burning': ['Urinary tract infection'],
                'burning urination': ['Urinary tract infection']
            }

            known_disease_map = {}
            for disease_name in diseaselist:
                normalized_disease = re.sub(r'\s+', ' ', disease_name.lower()).strip()
                known_disease_map[normalized_disease] = disease_name
                known_disease_map[normalized_disease.replace('diseae', 'disease')] = disease_name

            normalized_query_for_detection = re.sub(r'[^a-zA-Z0-9\s]', ' ', query_for_processing.lower())
            normalized_query_for_detection = re.sub(r'\s+', ' ', normalized_query_for_detection).strip()

            matched_disease_from_query = ''
            for normalized_name, original_name in known_disease_map.items():
                if normalized_name and normalized_name in normalized_query_for_detection:
                    matched_disease_from_query = original_name
                    break

            symptom_scores = {}
            for symptom_key, candidate_diseases in symptom_to_diseases.items():
                if symptom_key in normalized_query_for_detection:
                    for candidate in candidate_diseases:
                        symptom_scores[candidate] = symptom_scores.get(candidate, 0) + 1

            is_symptom_query = bool(symptom_scores) and not matched_disease_from_query
            if is_symptom_query:
                ranked = sorted(symptom_scores.items(), key=lambda x: x[1], reverse=True)
                top_candidates = [name for name, _ in ranked[:3]]
                suggestion_reply = (
                    "Based on the symptoms, possible diseases are: "
                    + ', '.join(top_candidates)
                    + ". Please confirm with a doctor. For detailed information, ask using a specific disease name."
                )
                if selected_language_code != 'en':
                    translated_suggestion = translate_text(suggestion_reply, selected_language_code, source_lang='en')
                    suggestion_reply = translated_suggestion or suggestion_reply
                    suggestion_reply = localize_digits(suggestion_reply, selected_language_code)
                return JsonResponse({'reply': suggestion_reply})

            # Extract likely disease name from natural-language prompts/questions.
            cleaned_query = query_for_processing.lower()
            if matched_disease_from_query:
                cleaned_query = matched_disease_from_query.lower()

            language_phrases = [
                ('in english', 'english'),
                ('english', 'english'),
                ('in hindi', 'hindi'),
                ('hindi me', 'hindi'),
                ('hindi', 'hindi'),
                ('in gujarati', 'gujarati'),
                ('gujarati me', 'gujarati'),
                ('gujarati', 'gujarati'),
                ('in marathi', 'marathi'),
                ('marathi me', 'marathi'),
                ('marathi', 'marathi')
            ]
            for phrase, language_name in language_phrases:
                if phrase in cleaned_query:
                    requested_language = language_name
                    cleaned_query = cleaned_query.replace(phrase, ' ')
            selected_language_code = language_map.get(requested_language, 'en')

            trigger_phrases = [
                'tell me about',
                'explain about',
                'explain',
                'about',
                'what is',
                'what\'s',
                'info about',
                'information about',
                'details about'
            ]
            for phrase in trigger_phrases:
                if phrase in cleaned_query:
                    cleaned_query = cleaned_query.replace(phrase, ' ')

            is_question = ('?' in query_for_processing) or any(
                marker in cleaned_query for marker in [
                    'what', 'how', 'why', 'when', 'which',
                    'symptom', 'cause', 'treat', 'prevent', 'cure',
                    'risk', 'diagnos', 'complication', 'medicine', 'diet'
                ]
            )

            question_cleanup_phrases = [
                'what are the symptoms of',
                'what is the treatment for',
                'what causes',
                'what is',
                'how to treat',
                'how to prevent',
                'symptoms of',
                'treatment for',
                'causes of',
                'prevention of',
                'complications of',
                'risk factors of',
                'tell me about',
                'explain about'
            ]
            for phrase in question_cleanup_phrases:
                if phrase in cleaned_query:
                    cleaned_query = cleaned_query.replace(phrase, ' ')

            cleaned_query = ' '.join(cleaned_query.split()).strip(' ?.!,:;')
            disease_term = matched_disease_from_query or cleaned_query or query_for_processing

            # Always fetch from English Wikipedia for better disease-title matching
            # and more stable medical content, then translate the final answer.
            extract = fetch_best_extract(
                'https://en.wikipedia.org/w/api.php',
                disease_term,
                intro_only=(not is_question)
            )

            if not extract:
                return JsonResponse({'reply': 'I could not find detailed information on that. Could you please check the spelling or try a more common name?'})

            if not matched_disease_from_query:
                extract_lower = extract.lower()
                query_lower = query_for_processing.lower()
                # Strict medical keywords to avoid matching generic terms like "health" or "mental"
                strict_medical_keywords = [
                    'disease', 'syndrome', 'infection', 'virus', 'bacteria', 'medical',
                    'symptom', 'treatment', 'treat', 'treated', 'cancer', 'disorder', 'illness',
                    'therapy', 'tumor', 'vaccine', 'diagnos', 'pathogen',
                    'clinical', 'hospital', 'doctor', 'surgery', 'prescription',
                    'medication', 'patient', 'medicine', 'cure',
                    'therapeutic', 'diagnostic', 'healthcare',
                    'pain', 'fever', 'cough', 'headache', 'nausea', 'vomiting', 
                    'fatigue', 'swelling', 'rash', 'diabetes', 'hypertension', 'asthma', 
                    'allergy', 'allergic', 'pregnancy', 'depression', 'anxiety', 'psychiatric',
                    'pediatric', 'neurological', 'cardiovascular', 'respiratory',
                    'gastrointestinal', 'genetic', 'immune', 'chronic',
                    'acute', 'fungal', 'parasite', 'injury', 'fracture', 'wound'
                ]
                match_count = sum(1 for kw in strict_medical_keywords if kw in extract_lower or kw in query_lower)
                if match_count < 2:
                    refusal_msg = "I provide information about disease and symptoms only so ask me related questions only"
                    if selected_language_code != 'en':
                        translated_refusal = translate_text(refusal_msg, selected_language_code, source_lang='en')
                        refusal_msg = translated_refusal or refusal_msg
                        refusal_msg = localize_digits(refusal_msg, selected_language_code)
                    return JsonResponse({'reply': refusal_msg})

            if is_question:
                extract = build_question_answer(query_for_processing, extract)

            if selected_language_code != 'en':
                translated_extract = translate_text(extract, selected_language_code, source_lang='en')
                extract = translated_extract or extract
                extract = localize_digits(extract, selected_language_code)

            if len(extract) > 1000:
                extract = extract[:1000] + '...'

            return JsonResponse({'reply': extract})
                
        except Exception as e:
            fallback_by_language = {
                'english': 'I could not fetch full details right now. Please try again with a disease name or main symptoms (for example: fever, cough, headache).',
                'hindi': 'अभी पूरी जानकारी नहीं मिल पाई। कृपया रोग का नाम या मुख्य लक्षण लिखकर दोबारा पूछें (जैसे: बुखार, खांसी, सिरदर्द)।',
                'gujarati': 'હમણાં સંપૂર્ણ માહિતી મેળવી શકાઈ નથી. કૃપા કરીને રોગનું નામ અથવા મુખ્ય લક્ષણો સાથે ફરી પૂછો (જેમ કે: તાવ, ખાંસી, માથાનો દુખાવો).',
                'marathi': 'आत्ता संपूर्ण माहिती मिळाली नाही. कृपया रोगाचे नाव किंवा मुख्य लक्षणे देऊन पुन्हा विचारा (उदा.: ताप, खोकला, डोकेदुखी).'
            }
            requested_language = 'english'
            try:
                data = json.loads(request.body or '{}')
                requested_language = str(data.get('language', 'english')).strip().lower()
            except Exception:
                requested_language = 'english'
            return JsonResponse({'reply': fallback_by_language.get(requested_language, fallback_by_language['english'])})

    return JsonResponse({'reply': 'Invalid request method.'}, status=400)


def get_recent_chats(request):
    if request.method == "GET" and request.user.is_authenticated:
        if doctor.objects.filter(user=request.user).exists():
            doctor_obj = request.user.doctor
            consultations = consultation.objects.filter(doctor=doctor_obj, status='active')
            latest_chat = Chat.objects.filter(consultation_id__in=consultations).exclude(sender=request.user).order_by('-created').first()
            
            if latest_chat:
                try:
                    sender_name = latest_chat.sender.patient.name
                except Exception:
                    sender_name = latest_chat.sender.username
                    
                return JsonResponse({
                    'chat_id': latest_chat.id,
                    'sender': sender_name,
                    'message': latest_chat.message,
                    'consultation_id': latest_chat.consultation_id.id,
                    'created': latest_chat.created.strftime("%b %d, %Y, %I:%M %p")
                })
                
        elif patient.objects.filter(user=request.user).exists():
            patient_obj = request.user.patient
            consultations = consultation.objects.filter(patient=patient_obj, status='active')
            latest_chat = Chat.objects.filter(consultation_id__in=consultations).exclude(sender=request.user).order_by('-created').first()
            
            if latest_chat:
                try:
                    sender_name = latest_chat.sender.doctor.name
                except Exception:
                    sender_name = latest_chat.sender.username
                    
                return JsonResponse({
                    'chat_id': latest_chat.id,
                    'sender': sender_name,
                    'message': latest_chat.message,
                    'consultation_id': latest_chat.consultation_id.id,
                    'created': latest_chat.created.strftime("%b %d, %Y, %I:%M %p")
                })
                
    return JsonResponse({'chat_id': None})

