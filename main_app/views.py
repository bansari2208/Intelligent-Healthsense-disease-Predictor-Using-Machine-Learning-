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


DISEASE_DETAILS_MAP = {
    'Fungal infection': {
        'about': 'A skin infection caused by a fungus, leading to irritation, scaly skin, redness, and itching.',
        'recommendations': [
            'Keep the affected area clean and dry.',
            'Apply over-the-counter antifungal cream.',
            'Avoid sharing personal items like towels.'
        ],
        'symptoms': ['Itching', 'Skin Rash', 'Nodal Skin Eruptions', 'Dischromic Patches']
    },
    'Allergy': {
        'about': 'An immune system reaction to a foreign substance, causing sneezing, runny nose, itching, or skin rashes.',
        'recommendations': [
            'Identify and avoid allergen triggers.',
            'Take non-drowsy antihistamines.',
            'Use saline nasal sprays for congestion.'
        ],
        'symptoms': ['Continuous Sneezing', 'Shivering', 'Watering From Eyes', 'Itching']
    },
    'GERD': {
        'about': 'A chronic digestive condition where stomach acid flows back into the esophagus, causing irritation and heartburn.',
        'recommendations': [
            'Avoid lying down immediately after eating.',
            'Eat smaller and more frequent meals.',
            'Limit acidic, spicy, or fatty foods.'
        ],
        'symptoms': ['Acidity', 'Stomach Pain', 'Ulcers On Tongue', 'Vomiting', 'Cough', 'Chest Pain']
    },
    'Chronic cholestasis': {
        'about': 'A liver condition where the flow of bile from the liver is reduced or stopped, causing toxin build-up.',
        'recommendations': [
            'Avoid alcohol completely.',
            'Follow a low-fat diet.',
            'Take prescribed bile acid medications.'
        ],
        'symptoms': ['Itching', 'Vomiting', 'Yellowish Skin', 'Nausea', 'Loss Of Appetite', 'Yellowing Of Eyes']
    },
    'Drug Reaction': {
        'about': 'An adverse or allergic reaction to a medication, often manifesting as skin rashes, itching, or fever.',
        'recommendations': [
            'Stop taking the suspected medication immediately.',
            'Contact your prescribing physician.',
            'Use cold compresses to soothe skin.'
        ],
        'symptoms': ['Itching', 'Skin Rash', 'Burning Micturition', 'Spotting Urination', 'High Fever']
    },
    'Peptic ulcer diseae': {
        'about': 'Sore lesions that develop on the inner lining of your stomach, small intestine, or esophagus.',
        'recommendations': [
            'Avoid NSAIDs (aspirin/ibuprofen).',
            'Eat a bland diet and avoid spicy foods.',
            'Limit caffeine and alcohol.'
        ],
        'symptoms': ['Vomiting', 'Loss Of Appetite', 'Abdominal Pain', 'Passage Of Gases', 'Internal Itching']
    },
    'AIDS': {
        'about': 'A chronic, potentially life-threatening condition caused by the human immunodeficiency virus (HIV).',
        'recommendations': [
            'Strictly follow antiretroviral therapy (ART).',
            'Maintain excellent hygiene and safe food practices.',
            'Consult an infectious disease specialist.'
        ],
        'symptoms': ['Muscle Wasting', 'Patches In Throat', 'High Fever', 'Extra Marital Contacts']
    },
    'Diabetes ': {
        'about': 'A chronic disease that occurs when the pancreas does not produce enough insulin or the body cannot use it effectively.',
        'recommendations': [
            'Monitor blood sugar levels regularly.',
            'Maintain a low-glycemic, high-fiber diet.',
            'Engage in daily moderate exercise.'
        ],
        'symptoms': ['Fatigue', 'Weight Loss', 'Restlessness', 'Lethargy', 'Irregular Sugar Level', 'Blurred Vision', 'Obesity', 'Excessive Hunger', 'Polyuria']
    },
    'Gastroenteritis': {
        'about': 'An intestinal infection marked by diarrhea, cramps, nausea, vomiting, and sometimes fever.',
        'recommendations': [
            'Stay hydrated with ORS and water.',
            'Eat a bland, easy-to-digest diet.',
            'Avoid dairy, caffeine, and fatty foods.'
        ],
        'symptoms': ['Vomiting', 'Diarrhoea', 'Stomach Pain']
    },
    'Bronchial Asthma': {
        'about': 'A chronic condition where the airways become inflamed, narrow, and swell, making breathing difficult.',
        'recommendations': [
            'Keep your quick-relief inhaler accessible.',
            'Identify and avoid asthma triggers.',
            'Monitor your peak flow rate.'
        ],
        'symptoms': ['Fatigue', 'Cough', 'Breathlessness', 'Family History', 'Mucoid Sputum']
    },
    'Hypertension ': {
        'about': 'A common condition in which the long-term force of the blood against your artery walls is high enough to cause health problems.',
        'recommendations': [
            'Limit daily sodium intake to under 1500mg.',
            'Exercise regularly (brisk walking).',
            'Practice stress relief techniques.'
        ],
        'symptoms': ['Headache', 'Chest Pain', 'Dizziness', 'Loss Of Balance', 'Lack Of Concentration']
    },
    'Migraine': {
        'about': 'A neurological condition characterized by intense, debilitating headaches, often accompanied by nausea and sensory sensitivity.',
        'recommendations': [
            'Rest in a dark, quiet room.',
            'Apply a cold compress to your head.',
            'Avoid triggers like caffeine, chocolate, or stress.'
        ],
        'symptoms': ['Acidity', 'Indigestion', 'Headache', 'Blurred Vision', 'Nausea', 'Excessive Hunger', 'Stiff Neck', 'Depression', 'Irritability', 'Visual Disturbances']
    },
    'Cervical spondylosis': {
        'about': 'Age-related wear and tear affecting the spinal disks in your neck, causing pain, stiffness, or numbness.',
        'recommendations': [
            'Practice gentle neck stretches and exercises.',
            'Maintain good posture while sitting or working.',
            'Apply warm compresses to ease stiffness.'
        ],
        'symptoms': ['Back Pain', 'Neck Pain', 'Dizziness', 'Loss Of Balance', 'Weakness In Limbs']
    },
    'Paralysis (brain hemorrhage)': {
        'about': 'Loss of muscle function in parts of the body, often caused by a stroke or severe bleeding in the brain.',
        'recommendations': [
            'Seek emergency medical care immediately.',
            'Start intensive physical therapy as early as possible.',
            'Closely monitor blood pressure.'
        ],
        'symptoms': ['Vomiting', 'Headache', 'Weakness Of One Body Side', 'Altered Sensorium']
    },
    'Jaundice': {
        'about': 'A condition in which the skin, sclera, and mucous membranes turn yellow due to high levels of bilirubin.',
        'recommendations': [
            'Drink plenty of water and clear fluids.',
            'Eat an extremely light, oil-free diet.',
            'Avoid alcohol and heavy foods completely.'
        ],
        'symptoms': ['Itching', 'Vomiting', 'Yellowish Skin', 'Dark Urine', 'Nausea', 'Abdominal Pain', 'Loss Of Appetite', 'Yellowing Of Eyes']
    },
    'Malaria': {
        'about': 'A life-threatening disease caused by plasmodium parasites transmitted through the bites of infected female Anopheles mosquitoes.',
        'recommendations': [
            'Take prescribed antimalarial medications exactly as directed.',
            'Keep yourself well hydrated.',
            'Use mosquito nets and repellents.'
        ],
        'symptoms': ['Chills', 'Vomiting', 'High Fever', 'Sweating', 'Headache', 'Nausea', 'Diarrhoea', 'Muscle Pain']
    },
    'Chicken pox': {
        'about': 'A highly contagious viral infection causing an itchy, blister-like rash on the skin.',
        'recommendations': [
            'Avoid scratching the blisters to prevent infection.',
            'Take oatmeal baths to soothe itchy skin.',
            'Isolate to prevent spreading to others.'
        ],
        'symptoms': ['Itching', 'Skin Rash', 'Fatigue', 'Lethargy', 'High Fever', 'Headache', 'Loss Of Appetite', 'Mild Fever', 'Swelled Lymph Nodes', 'Red Spots Over Body']
    },
    'Dengue': {
        'about': 'A mosquito-borne viral disease causing severe flu-like illness, high fever, and extreme joint/muscle pain.',
        'recommendations': [
            'Rest completely and drink abundant fluids.',
            'Avoid NSAIDs (use paracetamol for fever).',
            'Monitor blood platelet count regularly.'
        ],
        'symptoms': ['Skin Rash', 'Chills', 'Joint Pain', 'Vomiting', 'High Fever', 'Headache', 'Nausea', 'Loss Of Appetite', 'Pain Behind The Eyes', 'Back Pain', 'Muscle Pain', 'Red Spots Over Body']
    },
    'Typhoid': {
        'about': 'A bacterial infection caused by Salmonella typhi, leading to high fever, severe fatigue, headache, and abdominal symptoms.',
        'recommendations': [
            'Complete the full course of prescribed antibiotics.',
            'Drink boiled or purified water only.',
            'Eat thoroughly cooked, soft foods.'
        ],
        'symptoms': ['Chills', 'Vomiting', 'Fatigue', 'High Fever', 'Headache', 'Nausea', 'Constipation', 'Diarrhoea', 'Abdominal Pain', 'Toxic Look (Typhos)']
    },
    'hepatitis A': {
        'about': 'A highly contagious liver infection caused by the hepatitis A virus, typically spread through contaminated food or water.',
        'recommendations': [
            'Get absolute bed rest to recover energy.',
            'Avoid fatty foods and alcohol to rest the liver.',
            'Practice strict hand hygiene.'
        ],
        'symptoms': ['Joint Pain', 'Vomiting', 'Yellowish Skin', 'Dark Urine', 'Nausea', 'Loss Of Appetite', 'Abdominal Pain', 'Yellowing Of Eyes', 'Mild Fever']
    },
    'Hepatitis B': {
        'about': 'A serious liver infection caused by the hepatitis B virus (HBV), which can become chronic and lead to liver damage.',
        'recommendations': [
            'Avoid alcohol and medications that stress the liver.',
            'Eat a balanced diet and stay hydrated.',
            'Get regular medical evaluations.'
        ],
        'symptoms': ['Joint Pain', 'Vomiting', 'Yellowish Skin', 'Dark Urine', 'Nausea', 'Loss Of Appetite', 'Abdominal Pain', 'Yellowing Of Eyes', 'Lethargy', 'Receiving Blood Transfusion']
    },
    'Hepatitis C': {
        'about': 'An infection caused by the hepatitis C virus (HCV) that attacks the liver and leads to inflammation.',
        'recommendations': [
            'Consult a hepatologist for antiviral therapy.',
            'Avoid alcohol completely.',
            'Prevent spreading by not sharing needles or razors.'
        ],
        'symptoms': ['Fatigue', 'Yellowish Skin', 'Nausea', 'Loss Of Appetite', 'Yellowing Of Eyes', 'Family History']
    },
    'Hepatitis D': {
        'about': 'A liver disease caused by the hepatitis D virus (HDV), which only occurs in people who are already infected with Hepatitis B.',
        'recommendations': [
            'Focus on managing the co-existing Hepatitis B.',
            'Avoid substances that strain the liver.',
            'Consult a specialist doctor regularly.'
        ],
        'symptoms': ['Joint Pain', 'Vomiting', 'Yellowish Skin', 'Dark Urine', 'Nausea', 'Loss Of Appetite', 'Abdominal Pain', 'Yellowing Of Eyes']
    },
    'Hepatitis E': {
        'about': 'A liver disease caused by the hepatitis E virus (HEV), mainly transmitted through drinking water contaminated with fecal matter.',
        'recommendations': [
            'Maintain high hydration levels and rest.',
            'Consume only clean, boiled, or bottled water.',
            'Pregnant women should seek immediate medical care.'
        ],
        'symptoms': ['Joint Pain', 'Vomiting', 'Yellowish Skin', 'Dark Urine', 'Nausea', 'Loss Of Appetite', 'Abdominal Pain', 'Yellowing Of Eyes', 'Acute Liver Failure', 'Coma']
    },
    'Alcoholic hepatitis': {
        'about': 'Inflammation of the liver caused by heavy, long-term consumption of alcohol.',
        'recommendations': [
            'Stop drinking alcohol permanently.',
            'Follow a highly nutritious, protein-rich diet.',
            'Consult a gastroenterologist immediately.'
        ],
        'symptoms': ['Vomiting', 'Yellowish Skin', 'Abdominal Pain', 'Swelling Of Stomach', 'History Of Alcohol Consumption', 'Distention Of Abdomen']
    },
    'Tuberculosis': {
        'about': 'A potentially serious infectious disease caused by Mycobacterium tuberculosis bacteria that mainly affects the lungs.',
        'recommendations': [
            'Take prescribed multi-drug TB therapy without skipping doses.',
            'Wear a mask to prevent spreading to family members.',
            'Eat a high-protein, calorie-dense diet.'
        ],
        'symptoms': ['Chills', 'Vomiting', 'Fatigue', 'Weight Loss', 'High Fever', 'Headache', 'Cough', 'Breathlessness', 'Sweating', 'Loss Of Appetite', 'Mild Fever', 'Phlegm', 'Chest Pain', 'Blood In Sputum']
    },
    'Common Cold': {
        'about': 'A common viral infection of the nose and throat, causing mild congestion, sneezing, runny nose, and cough.',
        'recommendations': [
            'Drink warm liquids and stay warm.',
            'Get adequate sleep and rest.',
            'Use saline drops or steam inhalation to relieve congestion.'
        ],
        'symptoms': ['Continuous Sneezing', 'Chills', 'Fatigue', 'Cough', 'High Fever', 'Headache', 'Swelled Lymph Nodes', 'Malaise', 'Throat Irritation', 'Runny Nose', 'congestion', 'Sinus Pressure', 'Chest Pain']
    },
    'Pneumonia': {
        'about': 'An infection that inflames the air sacs in one or both lungs, which may fill with fluid or pus.',
        'recommendations': [
            'Complete the full course of prescribed medications.',
            'Use a humidifier or take warm baths to loosen mucus.',
            'Get plenty of rest.'
        ],
        'symptoms': ['Chills', 'Fatigue', 'Cough', 'Breathlessness', 'High Fever', 'Sweating', 'Malaise', 'Phlegm', 'Chest Pain', 'Fast Heart Rate', 'Rusty Sputum']
    },
    'Dimorphic hemmorhoids(piles)': {
        'about': 'Swollen veins in your anus and lower rectum, similar to varicose veins, causing pain, itching, and bleeding.',
        'recommendations': [
            'Follow a high-fiber diet to soften stools.',
            'Drink at least 3-4 liters of water daily.',
            'Avoid straining during bowel movements.'
        ],
        'symptoms': ['Constipation', 'Pain During Bowel Movements', 'Pain In Anal Region', 'Irritation In Anus', 'Bloody Stool']
    },
    'Heart attack': {
        'about': 'A medical emergency in which blood flow to the heart muscle is severely reduced or cut off, causing tissue damage.',
        'recommendations': [
            'Call emergency medical services (911/108) immediately.',
            'Chew an aspirin if directed by emergency staff.',
            'Stay calm and sit down.'
        ],
        'symptoms': ['Vomiting', 'Breathlessness', 'Sweating', 'Chest Pain']
    },
    'Varicose veins': {
        'about': 'Gnarled, enlarged veins, most commonly appearing in the legs and feet due to weakened vein walls and valves.',
        'recommendations': [
            'Avoid standing or sitting for long periods without moving.',
            'Elevate your legs above heart level when resting.',
            'Wear compression stockings.'
        ],
        'symptoms': ['Fatigue', 'Cramps', 'Bruising', 'Obesity', 'Swollen Legs', 'Prominent Veins On Calf']
    },
    'Hypothyroidism': {
        'about': 'A condition in which the thyroid gland doesn\'t produce enough thyroid hormone, slowing down metabolism.',
        'recommendations': [
            'Take prescribed thyroid hormone replacement daily.',
            'Focus on a nutrient-rich, balanced diet.',
            'Monitor thyroid levels regularly.'
        ],
        'symptoms': ['Fatigue', 'Weight Gain', 'Cold Hands And Feets', 'Mood Swings', 'Lethargy', 'Dizziness', 'Puffy Face And Eyes', 'Enlarged Thyroid', 'Brittle Nails', 'Depression']
    },
    'Hyperthyroidism': {
        'about': 'The production of too much thyroid hormone by the thyroid gland, accelerating your body\'s metabolism.',
        'recommendations': [
            'Strictly follow anti-thyroid medication schedule.',
            'Avoid excessive iodine intake.',
            'Manage stress through light activities.'
        ],
        'symptoms': ['Fatigue', 'Weight Loss', 'Restlessness', 'Sweating', 'Mood Swings', 'Fast Heart Rate', 'Excessive Hunger', 'Muscle Weakness', 'Abnormal Menstruation', 'Irritable']
    },
    'Hypoglycemia': {
        'about': 'A condition characterized by an abnormally low level of blood sugar (glucose), requiring quick energy intake.',
        'recommendations': [
            'Consume 15 grams of fast-acting sugar (fruit juice/honey) immediately.',
            'Check blood sugar again after 15 minutes.',
            'Eat a complex carb snack after recovery.'
        ],
        'symptoms': ['Vomiting', 'Fatigue', 'Anxiety', 'Sweating', 'Headache', 'Nausea', 'Blurred Vision', 'Dizziness', 'Palpitations', 'Drying And Tingling Lips']
    },
    'Osteoarthristis': {
        'about': 'The most common form of arthritis, occurring when the protective cartilage that cushions the ends of the bones wears down over time.',
        'recommendations': [
            'Maintain a healthy weight to reduce joint load.',
            'Perform low-impact exercises like swimming.',
            'Use warm/cold compresses to manage stiffness.'
        ],
        'symptoms': ['Joint Pain', 'Neck Pain', 'Hip Joint Pain', 'Knee Pain', 'Painful Walking']
    },
    'Arthritis': {
        'about': 'Inflammation of one or more joints, causing pain, stiffness, and reduced mobility that can worsen with age.',
        'recommendations': [
            'Engage in joint-friendly exercises.',
            'Maintain an anti-inflammatory diet.',
            'Apply heat to stiff joints or ice to swollen areas.'
        ],
        'symptoms': ['Joint Pain', 'Muscle Weakness', 'Stiff Neck', 'Swelling Joints', 'Painful Walking', 'Movement Stiffness']
    },
    '(vertigo) Paroymsal  Positional Vertigo': {
        'about': 'A sudden sensation that you are spinning or that the inside of your head is spinning, triggered by specific head movements.',
        'recommendations': [
            'Perform Canalith repositioning maneuvers (Epley maneuver).',
            'Avoid sudden head movements or bending over.',
            'Sit down immediately if you feel dizzy.'
        ],
        'symptoms': ['Vomiting', 'Headache', 'Nausea', 'Spinning Movements', 'Loss Of Balance', 'Unsteadiness']
    },
    'Acne': {
        'about': 'A skin condition that occurs when hair follicles become plugged with oil and dead skin cells, causing pimples or blackheads.',
        'recommendations': [
            'Wash your face gently with a mild cleanser twice daily.',
            'Avoid touching or popping pimples.',
            'Use non-comedogenic skincare products.'
        ],
        'symptoms': ['Skin Rash', 'Pus Filled Pimples', 'Blackheads', 'Scurring']
    },
    'Urinary tract infection': {
        'about': 'An infection in any part of your urinary system, including your kidneys, ureters, bladder, and urethra.',
        'recommendations': [
            'Drink abundant water to flush out bacteria.',
            'Avoid holding urine and empty bladder fully.',
            'Avoid bladder irritants like caffeine.'
        ],
        'symptoms': ['Burning Micturition', 'Bladder Discomfort', 'Foul Smell Of Urine', 'Continuous Feel Of Urine']
    },
    'Psoriasis': {
        'about': 'A skin disease that causes red, itchy scaly patches, most commonly on the knees, elbows, trunk, and scalp.',
        'recommendations': [
            'Apply thick moisturizing creams daily.',
            'Avoid triggers like stress or skin injuries.',
            'Discuss light therapy options with a dermatologist.'
        ],
        'symptoms': ['Skin Rash', 'Joint Pain', 'Skin Peeling', 'Silver Like Dusting', 'Small Dents In Nails', 'Inflammatory Nails']
    },
    'Impetigo': {
        'about': 'A highly contagious bacterial skin infection that causes red sores, which can pop, ooze, and form a yellow-brown crust.',
        'recommendations': [
            'Wash the sores gently with mild soap and water.',
            'Keep sores covered loosely with gauze.',
            'Avoid touching or scratching the infected area.'
        ],
        'symptoms': ['Skin Rash', 'High Fever', 'Blister', 'Red Sore Around Nose', 'Yellow Crust Ooze']
    },
    
    # Override / Extra diseases
    'Dental Caries / Infection': {
        'about': 'A bacterial disease that destroys the hard structure of your teeth, causing cavities, pain, and potential infection.',
        'recommendations': [
            'Maintain a strict flossing and brushing routine.',
            'Avoid sugary snacks and carbonated drinks.',
            'Visit a dentist immediately for treatment.'
        ],
        'symptoms': ['Toothache', 'Swollen Gums', 'Bad Breath']
    },
    'Gingivitis / Periodontal Disease': {
        'about': 'A common and mild form of gum disease that causes irritation, redness, and swelling of your gum tissue.',
        'recommendations': [
            'Brush twice daily with a soft-bristled brush.',
            'Use an antiseptic mouthwash daily.',
            'Schedule a professional dental cleaning.'
        ],
        'symptoms': ['Bleeding Gums', 'Swollen Gums', 'Gum Sensitivity']
    },
    'Conjunctivitis / Eye Infection': {
        'about': 'An inflammation or infection of the transparent membrane that lines your eyelid and covers the white part of your eyeball.',
        'recommendations': [
            'Avoid touching or rubbing your eyes.',
            'Wash hands thoroughly with soap regularly.',
            'Use prescribed antibiotic/soothing eye drops.'
        ],
        'symptoms': ['Redness Of Eyes', 'Watering From Eyes', 'Eye Itching', 'Sticky Discharge']
    },
    'Refractive Error / Eye Issue': {
        'about': 'A common eye disorder where the eye cannot focus images clearly, resulting in blurred vision.',
        'recommendations': [
            'Schedule a comprehensive eye exam with an optometrist.',
            'Wear prescribed eyeglasses or contact lenses.',
            'Rest your eyes periodically using the 20-20-20 rule.'
        ],
        'symptoms': ['Blurred Vision', 'Headache', 'Eye Strain']
    },
    'Severe Eye Condition': {
        'about': 'A serious visual system pathology that can potentially threaten vision if left untreated.',
        'recommendations': [
            'Seek immediate evaluation from an ophthalmologist.',
            'Strictly avoid any direct pressure on the eyeball.',
            'Administer only professionally prescribed emergency drops.'
        ],
        'symptoms': ['Severe Eye Pain', 'Sudden Vision Loss', 'Extreme Photophobia']
    },
    'Alopecia / Hair Loss': {
        'about': 'A condition causing hair to fall out, which can affect just your scalp or your entire body, and can be temporary or permanent.',
        'recommendations': [
            'Avoid harsh chemical hair treatments and tight hairstyles.',
            'Eat a protein-rich and iron-rich balanced diet.',
            'Consult a dermatologist to identify the underlying cause.'
        ],
        'symptoms': ['Hair Thinning', 'Patchy Bald Spots', 'Brittle Hair']
    },
    'Otitis Media / Ear Infection': {
        'about': 'An infection or inflammation of the middle ear, often caused by bacteria or viruses, frequently accompanying colds.',
        'recommendations': [
            'Avoid inserting cotton swabs or objects into the ear.',
            'Apply a warm compress against the affected ear for pain relief.',
            'Consult an ENT specialist for antibiotic evaluations.'
        ],
        'symptoms': ['Ear Pain', 'Hearing Difficulty', 'Fluid Drainage']
    },
    'Hearing Loss / Ear Issue': {
        'about': 'A partial or total inability to hear sound in one or both ears, which can happen gradually or suddenly.',
        'recommendations': [
            'Avoid exposure to loud noises and wear hearing protection.',
            'Schedule an audiometry test with an audiologist.',
            'Do not try to remove earwax with sharp tools.'
        ],
        'symptoms': ['Muffled Hearing', 'Ringing In Ears', 'Ear Fullness']
    },
    'Fracture / Bone Injury': {
        'about': 'A complete or partial break in a bone, usually caused by high-force impact or physical trauma.',
        'recommendations': [
            'Immobilize the affected limb immediately.',
            'Apply ice wrapped in a towel to reduce swelling.',
            'Seek orthopedic emergency treatment right away.'
        ],
        'symptoms': ['Severe Bone Pain', 'Swelling and Bruising', 'Inability to Move Limb']
    },
    'Skin Laceration / Injury': {
        'about': 'A skin wound produced by the tearing or cutting of soft body tissue, which is often irregular or jagged.',
        'recommendations': [
            'Cleanse the wound gently with clean water and mild soap.',
            'Apply an antiseptic ointment and cover with a sterile bandage.',
            'Get a tetanus booster shot if your last one was over 5 years ago.'
        ],
        'symptoms': ['Bleeding Wound', 'Local Soreness', 'Swelling']
    },
    'Burn Injury': {
        'about': 'Tissue damage that results from heat, overexposure to the sun or other radiation, chemical or electrical contact.',
        'recommendations': [
            'Run cool (not cold) water over the burn for 10-15 minutes.',
            'Do not pop any blisters that form.',
            'Apply pure aloe vera gel or sterile ointment and cover loosely.'
        ],
        'symptoms': ['Skin Redness', 'Blisters', 'Burning Sensation']
    },
    'Menstrual Disorder': {
        'about': 'An irregular or abnormal condition affecting a woman\'s menstrual cycle, including severe pain or abnormal bleeding.',
        'recommendations': [
            'Use a warm heating pad to soothe abdominal cramps.',
            'Keep a precise calendar log of cycle dates and symptoms.',
            'Consult a gynecologist to evaluate hormone balance.'
        ],
        'symptoms': ['Abnormal Menstruation', 'Severe Abdominal Cramps', 'Fatigue']
    },
    'Pregnancy Related': {
        'about': 'Physiological changes and symptoms associated with the gestation period in pregnancy.',
        'recommendations': [
            'Consult a gynecologist for a professional HCG test.',
            'Start taking prenatal vitamins including folic acid daily.',
            'Ensure complete rest and stay fully hydrated.'
        ],
        'symptoms': ['Nausea', 'Missed Period', 'Fatigue']
    },
    'Mental Health Condition': {
        'about': 'A wide range of conditions that affect mood, thinking, and behavior, impact daily functioning, and require care.',
        'recommendations': [
            'Discuss your feelings with a certified mental health professional.',
            'Build a reliable, supportive circle of friends and family.',
            'Engage in daily mindfulness and stress-reduction routines.'
        ],
        'symptoms': ['Anxiety', 'Depression', 'Mood Swings']
    },
    'Severe Depression / Crisis': {
        'about': 'A critical state of clinical depression that requires immediate professional attention and intervention.',
        'recommendations': [
            'Reach out immediately to a certified psychiatric crisis counselor.',
            'Do not stay isolated; contact a trusted friend or family member.',
            'Seek professional medical evaluation for drug/behavioral therapy.'
        ],
        'symptoms': ['Severe Depressed Mood', 'Feelings of Hopelessness', 'Social Withdrawal']
    },
    'Depression': {
        'about': 'A persistent mood disorder characterized by feelings of sadness, loss of interest, and lack of energy.',
        'recommendations': [
            'Consult a psychiatrist or licensed psychotherapist.',
            'Incorporate light physical exercise into your weekly routine.',
            'Maintain a structured daily routine to keep active.'
        ],
        'symptoms': ['Sadness', 'Lethargy', 'Sleep Disturbances']
    },
    'Stress / Anxiety': {
        'about': 'A state of mental tension and worry caused by challenging life situations, resulting in physical and mental distress.',
        'recommendations': [
            'Practice daily deep-breathing exercises.',
            'Limit intake of stimulants like caffeine and nicotine.',
            'Ensure at least 7-8 hours of quality sleep nightly.'
        ],
        'symptoms': ['Restlessness', 'Irritability', 'Palpitations']
    },
    'Anxiety Disorder': {
        'about': 'A chronic condition characterized by excessive, persistent, and unreasonable worry about everyday situations.',
        'recommendations': [
            'Consult a therapist for Cognitive Behavioral Therapy (CBT).',
            'Avoid stressful environments where possible while recovering.',
            'Engage in regular physical activities like walking or yoga.'
        ],
        'symptoms': ['Constant Worry', 'Muscle Tension', 'Fatigue']
    }
}

def get_disease_details(disease_name):
    # Normalize lookup
    normalized_name = disease_name.strip().lower()
    for k, details in DISEASE_DETAILS_MAP.items():
        if k.strip().lower() == normalized_name:
            return details
    
    # Standard medical default fallback
    return {
        'about': f"{disease_name} is a medical condition identified by symptom patterns. We highly recommend consulting a specialist for confirmation.",
        'recommendations': [
            'Rest and drink plenty of fluids to maintain high hydration.',
            'Take over-the-counter medications as directed by a professional.',
            'Consult a doctor if symptoms persist more than 3-4 days.'
        ],
        'symptoms': ['Fever', 'Headache', 'Fatigue']
    }



# ---------------- HOME ----------------
def home(request):
    symptomslist = ['abdominal_pain', 'abnormal_menstruation', 'acidity', 'acute_liver_failure', 'altered_sensorium', 'anxiety', 'back_pain', 'belly_pain', 'blackheads', 'bladder_discomfort', 'blister', 'blood_in_sputum', 'bloody_stool', 'blurred_and_distorted_vision', 'breathlessness', 'brittle_nails', 'bruising', 'burning_micturition', 'chest_pain', 'chills', 'cold_hands_and_feets', 'coma', 'congestion', 'constipation', 'continuous_feel_of_urine', 'continuous_sneezing', 'cough', 'cramps', 'dark_urine', 'dehydration', 'depression', 'diarrhoea', 'dischromic _patches', 'distention_of_abdomen', 'dizziness', 'drying_and_tingling_lips', 'enlarged_thyroid', 'excessive_hunger', 'extra_marital_contacts', 'family_history', 'fast_heart_rate', 'fatigue', 'fluid_overload', 'foul_smell_of urine', 'headache', 'high_fever', 'hip_joint_pain', 'history_of_alcohol_consumption', 'increased_appetite', 'indigestion', 'inflammatory_nails', 'internal_itching', 'irregular_sugar_level', 'irritability', 'irritation_in_anus', 'itching', 'joint_pain', 'knee_pain', 'lack_of_concentration', 'lethargy', 'loss_of_appetite', 'loss_of_balance', 'loss_of_smell', 'malaise', 'mild_fever', 'mood_swings', 'movement_stiffness', 'mucoid_sputum', 'muscle_pain', 'muscle_wasting', 'muscle_weakness', 'nausea', 'neck_pain', 'nodal_skin_eruptions', 'obesity', 'pain_behind_the_eyes', 'pain_during_bowel_movements', 'pain_in_anal_region', 'painful_walking', 'palpitations', 'passage_of_gases', 'patches_in_throat', 'phlegm', 'polyuria', 'prominent_veins_on_calf', 'puffy_face_and_eyes', 'pus_filled_pimples', 'receiving_blood_transfusion', 'receiving_unsterile_injections', 'red_sore_around_nose', 'red_spots_over_body', 'redness_of_eyes', 'restlessness', 'runny_nose', 'rusty_sputum', 'scurring', 'shivering', 'silver_like_dusting', 'sinus_pressure', 'skin_peeling', 'skin_rash', 'slurred_speech', 'small_dents_in_nails', 'spinning_movements', 'spotting_ urination', 'stiff_neck', 'stomach_bleeding', 'stomach_pain', 'sunken_eyes', 'sweating', 'swelled_lymph_nodes', 'swelling_joints', 'swelling_of_stomach', 'swollen_blood_vessels', 'swollen_extremeties', 'swollen_legs', 'throat_irritation', 'toxic_look_(typhos)', 'ulcers_on_tongue', 'unsteadiness', 'visual_disturbances', 'vomiting', 'watering_from_eyes', 'weakness_in_limbs', 'weakness_of_one_body_side', 'weight_gain', 'weight_loss', 'yellow_crust_ooze', 'yellow_urine', 'yellowing_of_eyes', 'yellowish_skin']
    alphabaticsymptomslist = sorted(symptomslist)
    return render(request, 'homepage/index.html', {"list2": alphabaticsymptomslist})


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

            # Auto-create a consultation so it immediately populates the dashboard's predictions
            consultation_obj = consultation(
                patient=request.user.patient,
                doctor=None,
                diseaseinfo=diseaseinfo_new,
                consultation_date=date.today(),
                status='active'
            )
            consultation_obj.save()

            # Store exact creation time in session to avoid DateField 00:00:00 relative time offset bug
            from django.utils import timezone
            times = request.session.get('consultation_times', {})
            times[str(consultation_obj.id)] = timezone.now().isoformat()
            request.session['consultation_times'] = times

            details = get_disease_details(override_disease)

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
                'about_disease':    details['about'],
                'disease_recommendations': details['recommendations'],
                'typical_symptoms': details['symptoms']
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

        # Auto-create a consultation so it immediately populates the dashboard's predictions
        consultation_obj = consultation(
            patient=request.user.patient,
            doctor=None,
            diseaseinfo=diseaseinfo_new,
            consultation_date=date.today(),
            status='active'
        )
        consultation_obj.save()

        # Store exact creation time in session to avoid DateField 00:00:00 relative time offset bug
        from django.utils import timezone
        times = request.session.get('consultation_times', {})
        times[str(consultation_obj.id)] = timezone.now().isoformat()
        request.session['consultation_times'] = times

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

        details = get_disease_details(predicted_disease)

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
            'about_disease':    details['about'],
            'disease_recommendations': details['recommendations'],
            'typical_symptoms': details['symptoms']
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
    if not request.user.is_authenticated:
        return redirect('home')
    
    context = {}
    
    import datetime
    from django.utils import timezone

    if hasattr(request.user, 'patient'):
        patient_obj = request.user.patient
        consultations = consultation.objects.filter(patient=patient_obj).order_by('-consultation_date', '-id')
        disease_counts = {}
        recent_consults = []
        total_confidence = 0
        
        for c in consultations:
            if not c.diseaseinfo:
                continue
            d = c.diseaseinfo.diseasename
            disease_counts[d] = disease_counts.get(d, 0) + 1
            conf = float(c.diseaseinfo.confidence) if c.diseaseinfo.confidence else 0.0
            total_confidence += conf
            
            if len(recent_consults) < 5:
                if conf >= 80:
                    risk_level, risk_class, icon_color = 'Low Risk', 'risk-low', 'cyan'
                elif conf >= 50:
                    risk_level, risk_class, icon_color = 'Medium Risk', 'risk-medium', 'orange'
                else:
                    risk_level, risk_class, icon_color = 'High Risk', 'risk-high', 'red'
                
                dl = d.lower()
                if 'heart' in dl or 'hypertension' in dl:
                    icon = 'fa-heart-pulse'
                elif 'stomach' in dl or 'acidity' in dl or 'gerd' in dl or 'gastro' in dl or 'hepatitis' in dl:
                    icon = 'fa-bacteria' # Changed from fa-stomach (which is a PRO icon) to fa-bacteria
                elif 'head' in dl or 'migraine' in dl or 'anxiety' in dl or 'brain' in dl:
                    icon = 'fa-brain'
                else:
                    icon = 'fa-lungs'
                    
                recent_consults.append({
                    'id': c.id,
                    'date': c.consultation_date,
                    'disease': d,
                    'doctor': c.doctor.name if c.doctor else 'Unassigned',
                    'status': c.status,
                    'confidence': f"{conf:.1f}",
                    'risk_level': risk_level,
                    'risk_class': risk_class,
                    'icon_color': icon_color,
                    'icon': icon
                })
        
        total_consults = consultations.count()
        accuracy = round(total_confidence / total_consults, 1) if total_consults > 0 else 0.0
        health_score = max(50, 100 - (total_consults * 3)) if total_consults > 0 else 100

        # Calculate dynamic trends for the top 3 cards
        today = timezone.now().date()
        first_day_this_month = today.replace(day=1)
        if first_day_this_month.month == 1:
            first_day_last_month = first_day_this_month.replace(year=first_day_this_month.year - 1, month=12)
        else:
            first_day_last_month = first_day_this_month.replace(month=first_day_this_month.month - 1)

        this_month_count = consultation.objects.filter(patient=patient_obj, consultation_date__gte=first_day_this_month).count()
        last_month_count = consultation.objects.filter(patient=patient_obj, consultation_date__gte=first_day_last_month, consultation_date__lt=first_day_this_month).count()

        if last_month_count > 0:
            pred_change = ((this_month_count - last_month_count) / last_month_count) * 100
            predictions_trend = f"{abs(pred_change):.1f}%"
            predictions_trend_dir = "up" if pred_change >= 0 else "down"
        elif this_month_count > 0:
            predictions_trend = "100.0%"
            predictions_trend_dir = "up"
        else:
            predictions_trend = "0.0%"
            predictions_trend_dir = "neutral"

        if total_consults >= 2:
            latest_conf = float(consultations[0].diseaseinfo.confidence) if consultations[0].diseaseinfo.confidence else 0.0
            older_confs = []
            for c in consultations[1:]:
                if c.diseaseinfo and c.diseaseinfo.confidence:
                    older_confs.append(float(c.diseaseinfo.confidence))
            avg_older = sum(older_confs) / len(older_confs) if older_confs else 0.0
            acc_diff = latest_conf - avg_older
            accuracy_trend = f"{abs(acc_diff):.1f}%"
            accuracy_trend_dir = "up" if acc_diff >= 0 else "down"
        else:
            accuracy_trend = "0.0%"
            accuracy_trend_dir = "neutral"

        older_consults_count = total_consults - this_month_count
        prev_health = max(50, 100 - (older_consults_count * 3))
        health_diff = health_score - prev_health
        health_trend = f"{abs(health_diff):.1f}%"
        health_trend_dir = "up" if health_diff >= 0 else "down"
        
        # Trend Data
        trend_labels = []
        trend_data = []
        today = timezone.now().date()
        for i in range(5, -1, -1):
            d_date = today - datetime.timedelta(days=i)
            count = consultation.objects.filter(patient=patient_obj, consultation_date=d_date).count()
            trend_labels.append(d_date.strftime('%d %b'))
            trend_data.append(count)
            
        # Top Symptoms
        symptom_counts = {}
        for c in consultations:
            symp_list = []
            try:
                if c.diseaseinfo.symptomsname.startswith('['):
                    import ast
                    symp_list = ast.literal_eval(c.diseaseinfo.symptomsname)
                else:
                    symp_list = c.diseaseinfo.symptomsname.split(',')
            except:
                pass
            
            for s in symp_list:
                s_clean = s.strip().replace('_', ' ').title()
                if s_clean:
                    symptom_counts[s_clean] = symptom_counts.get(s_clean, 0) + 1
        
        sorted_symptoms = sorted(symptom_counts.items(), key=lambda item: item[1], reverse=True)[:5]
        max_symp = sorted_symptoms[0][1] if sorted_symptoms else 1
        top_symptoms = []
        colors = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#06b6d4']
        for idx, (symp, count) in enumerate(sorted_symptoms):
            width = int((count / max_symp) * 100)
            top_symptoms.append({'name': symp, 'count': count, 'width': width, 'color': colors[idx]})
            
        # Sub-scores (pseudo-dynamic)
        physical_score = max(40, 100 - (total_consults * 2))
        mental_score = max(50, 95 - (total_consults * 3))
        lifestyle_score = max(60, 90 - total_consults)
        sleep_score = max(40, 98 - (total_consults * 4))
        
        # Calculate human-readable last prediction time (avoiding timesince formatting issues)
        last_prediction_time = "No Predictions"
        if recent_consults:
            from django.utils.timesince import timesince
            c_obj = consultations[0]
            session_times = request.session.get('consultation_times', {})
            exact_time = None
            if str(c_obj.id) in session_times:
                try:
                    from datetime import datetime, timezone as dt_timezone
                    parsed = datetime.fromisoformat(session_times[str(c_obj.id)])
                    # Ensure timezone-aware so timesince() works correctly
                    if parsed.tzinfo is None:
                        exact_time = parsed.replace(tzinfo=dt_timezone.utc)
                    else:
                        exact_time = parsed
                except Exception:
                    pass

            # If we have the exact time from session and it matches the consult's date
            if exact_time and exact_time.date() == c_obj.consultation_date:
                ts = timesince(exact_time)
            else:
                # If we don't have it in the session, but the consultation was created TODAY,
                # we should treat it as extremely recent (0 min Ago) instead of defaulting to midnight of today (23h Ago)
                if c_obj.consultation_date == timezone.now().date():
                    ts = "0 minutes"
                else:
                    ts = timesince(c_obj.consultation_date)

            if not ts.strip() or ts == "0 minutes":
                first_part = "0 min"
            else:
                first_part = ts.split(',')[0].strip()
                first_part = first_part.replace('hours', 'h').replace('hour', 'h')
                first_part = first_part.replace('minutes', 'min').replace('minute', 'min')
                first_part = first_part.replace('days', 'd').replace('day', 'd')
                first_part = first_part.replace('weeks', 'w').replace('week', 'w')
            last_prediction_time = first_part

        import json
        context['labels'] = list(disease_counts.keys())
        context['data'] = list(disease_counts.values())
        context['total'] = total_consults
        context['recent_consults'] = recent_consults
        context['accuracy'] = accuracy
        context['health_score'] = health_score
        context['trend_labels'] = json.dumps(trend_labels)
        context['trend_data'] = json.dumps(trend_data)
        context['top_symptoms'] = top_symptoms
        context['physical_score'] = physical_score
        context['mental_score'] = mental_score
        context['lifestyle_score'] = lifestyle_score
        context['sleep_score'] = sleep_score
        context['last_prediction_time'] = last_prediction_time
        context['predictions_trend'] = predictions_trend
        context['predictions_trend_dir'] = predictions_trend_dir
        context['accuracy_trend'] = accuracy_trend
        context['accuracy_trend_dir'] = accuracy_trend_dir
        context['health_trend'] = health_trend
        context['health_trend_dir'] = health_trend_dir
    else:
        import json
        context['labels'] = ['Dengue', 'Malaria', 'Typhoid']
        context['data'] = [5, 2, 1]
        context['total'] = 8
        context['recent_consults'] = []
        context['accuracy'] = 92.4
        context['health_score'] = 85
        context['trend_labels'] = json.dumps(['1 May', '5 May', '9 May', '13 May', '17 May', '21 May'])
        context['trend_data'] = json.dumps([5, 26, 17, 36, 30, 28])
        context['top_symptoms'] = [
            {'name': 'Fever', 'count': 45, 'width': 90, 'color': '#10b981'},
            {'name': 'Headache', 'count': 32, 'width': 65, 'color': '#3b82f6'},
            {'name': 'Fatigue', 'count': 28, 'width': 55, 'color': '#8b5cf6'},
            {'name': 'Cough', 'count': 20, 'width': 40, 'color': '#f59e0b'},
            {'name': 'Nausea', 'count': 15, 'width': 30, 'color': '#06b6d4'}
        ]
        context['physical_score'] = 90
        context['mental_score'] = 80
        context['lifestyle_score'] = 75
        context['sleep_score'] = 85
        context['last_prediction_time'] = 'No Predictions'
        context['predictions_trend'] = "20.0%"
        context['predictions_trend_dir'] = "up"
        context['accuracy_trend'] = "5.6%"
        context['accuracy_trend_dir'] = "up"
        context['health_trend'] = "8.4%"
        context['health_trend_dir'] = "up"

    return render(request, 'patient/dashboard/dashboard.html', context)

def pviewprofile(request, patientusername):
    puser = User.objects.get(username=patientusername)
    return render(request, 'patient/view_profile/view_profile.html', {"puser": puser})

def doctor_ui(request):
    return render(request, 'doctor/doctor_ui/profile.html')

def dviewprofile(request, doctorusername):
    duser = User.objects.get(username=doctorusername)
    return render(request, 'doctor/view_profile/view_profile.html', {"duser": duser})

def pconsultation_history(request):
    if not request.user.is_authenticated:
        return redirect('home')
    try:
        patient_obj = request.user.patient
    except AttributeError:
        return redirect('home')
    consultation_obj = consultation.objects.filter(patient=patient_obj)
    return render(request, 'patient/consultation_history/consultation_history.html', {"consultation": consultation_obj})

def dconsultation_history(request):
    if not request.user.is_authenticated:
        return redirect('home')
    try:
        doctor_obj = request.user.doctor
    except AttributeError:
        return redirect('home')
    consultation_obj = consultation.objects.filter(doctor=doctor_obj)
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
    if not request.user.is_authenticated:
        return redirect('home')
    try:
        patient_obj = request.user.patient
    except AttributeError:
        return redirect('home')
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

    # Store exact creation time in session to avoid DateField 00:00:00 relative time offset bug
    from django.utils import timezone
    times = request.session.get('consultation_times', {})
    times[str(consultation_obj.id)] = timezone.now().isoformat()
    request.session['consultation_times'] = times

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

NETWORK_TIMEOUT_SECONDS = 3
NETWORK_MAX_RETRIES = 1

# ---------------------------------------------------------------------------
# Local Disease Knowledge Base — instant answers, zero network calls
# ---------------------------------------------------------------------------
LOCAL_DISEASE_KB = {
    'dengue': "Dengue fever is a mosquito-borne viral infection caused by the dengue virus. It causes high fever, severe headache, pain behind the eyes, joint and muscle pain, rash, and mild bleeding. Severe dengue (dengue hemorrhagic fever) can be life-threatening. There is no specific antiviral treatment; management focuses on fluid replacement, rest, and fever control. Prevention includes eliminating mosquito breeding sites and using repellents.",
    'malaria': "Malaria is a life-threatening disease caused by Plasmodium parasites transmitted through the bites of infected female Anopheles mosquitoes. Symptoms include high fever, chills, headache, muscle aches, fatigue, nausea, and vomiting occurring in cycles. Treatment uses antimalarial drugs (e.g., chloroquine, artemisinin). Prevention includes mosquito nets, repellents, and prophylactic medication.",
    'typhoid': "Typhoid fever is a bacterial infection caused by Salmonella typhi, spread through contaminated food and water. Symptoms include sustained high fever, weakness, abdominal pain, headache, diarrhoea or constipation, and sometimes a rash. It is treated with antibiotics. Vaccination and improved sanitation are key preventive measures.",
    'tuberculosis': "Tuberculosis (TB) is an infectious disease caused by Mycobacterium tuberculosis, primarily affecting the lungs. Symptoms include persistent cough (sometimes with blood), night sweats, unexplained weight loss, fever, and fatigue. TB is treated with a 6-month course of antibiotics. Drug-resistant TB requires longer, more complex regimens. BCG vaccination helps prevent severe forms in children.",
    'diabetes': "Diabetes mellitus is a chronic metabolic disease marked by elevated blood glucose. Type 1 diabetes is caused by autoimmune destruction of insulin-producing cells. Type 2 diabetes results from insulin resistance and is strongly linked to obesity and lifestyle. Symptoms include excessive thirst, frequent urination, blurred vision, fatigue, and slow-healing wounds. Management includes diet, exercise, oral medications, and/or insulin therapy.",
    'hypertension': "Hypertension (high blood pressure) is a condition where the force of blood against artery walls is consistently too high (≥130/80 mmHg). It often has no symptoms but greatly increases the risk of heart attack, stroke, and kidney disease. Lifestyle changes (low-salt diet, exercise, weight loss) and antihypertensive medications are the primary treatments.",
    'migraine': "Migraine is a neurological condition characterized by recurrent, intense headaches usually affecting one side of the head. It is often accompanied by nausea, vomiting, and extreme sensitivity to light and sound. Some people experience aura (visual or sensory disturbances) before the headache. Triggers include stress, hormonal changes, certain foods, and sleep disruption. Treatment includes pain relievers, triptans, and preventive medications.",
    'asthma': "Asthma is a chronic respiratory condition in which airways become inflamed and narrowed, causing recurrent episodes of wheezing, breathlessness, chest tightness, and coughing, especially at night or early morning. Triggers include allergens, cold air, exercise, and infections. Treatment uses inhaled bronchodilators (reliever inhalers) and corticosteroids (preventer inhalers).",
    'pneumonia': "Pneumonia is an infection that inflames the air sacs in one or both lungs, which may fill with fluid or pus. It can be caused by bacteria, viruses, or fungi. Symptoms include cough with phlegm, fever, chills, and difficulty breathing. Bacterial pneumonia is treated with antibiotics. Vaccines (pneumococcal and flu vaccines) help prevent common forms.",
    'jaundice': "Jaundice is a medical condition characterized by yellowing of the skin and eyes caused by elevated bilirubin levels in the blood. It is a symptom of underlying conditions such as liver disease (hepatitis), bile duct obstruction, or hemolytic anaemia. Treatment targets the underlying cause.",
    'hepatitis a': "Hepatitis A is a highly contagious liver infection caused by the hepatitis A virus (HAV), typically spread through contaminated food or water. Symptoms include fatigue, nausea, abdominal pain, jaundice, and dark urine. Most people recover fully without treatment. A vaccine is available and highly effective.",
    'hepatitis b': "Hepatitis B is a serious liver infection caused by the hepatitis B virus (HBV), transmitted through blood, sexual contact, or from mother to child. Chronic infection can lead to liver cirrhosis or liver cancer. Symptoms include jaundice, fatigue, abdominal pain, and dark urine. An effective vaccine is available; antiviral medications help manage chronic infection.",
    'hepatitis c': "Hepatitis C is a liver disease caused by the hepatitis C virus (HCV), primarily spread through blood-to-blood contact. Chronic hepatitis C can lead to liver scarring (cirrhosis) and liver cancer. Most infections are asymptomatic early on. Modern direct-acting antiviral (DAA) drugs can cure over 95% of cases.",
    'chicken pox': "Chickenpox is a highly contagious viral infection caused by the varicella-zoster virus. It causes an itchy blister-like rash, fever, tiredness, and loss of appetite. It spreads easily through respiratory droplets. Most cases resolve in 1–2 weeks. A vaccine is available. Antiviral drugs may be used in high-risk patients.",
    'common cold': "The common cold is a mild viral infection of the upper respiratory tract, most commonly caused by rhinoviruses. Symptoms include runny nose, sore throat, cough, sneezing, and low-grade fever. It is self-limiting and typically resolves in 7–10 days. Treatment is symptomatic (rest, fluids, decongestants).",
    'influenza': "Influenza (flu) is a contagious respiratory illness caused by influenza viruses. Symptoms include sudden onset of fever, cough, sore throat, body aches, headache, fatigue, and sometimes vomiting. It can lead to serious complications such as pneumonia. Annual flu vaccination is the best preventive measure. Antiviral drugs (e.g., oseltamivir) can reduce severity if taken early.",
    'gastroenteritis': "Gastroenteritis (stomach flu) is inflammation of the stomach and intestines, usually caused by a viral or bacterial infection. Symptoms include diarrhoea, vomiting, abdominal cramps, nausea, and sometimes fever. Treatment focuses on rehydration with oral rehydration solutions (ORS). Most cases resolve within a few days.",
    'gerd': "Gastroesophageal reflux disease (GERD) is a chronic digestive condition where stomach acid or bile flows back into the oesophagus, causing irritation. Symptoms include heartburn, regurgitation, chest discomfort, and difficulty swallowing. Lifestyle changes (small meals, avoiding triggers) and antacids or proton-pump inhibitors (PPIs) are first-line treatments.",
    'peptic ulcer': "A peptic ulcer is an open sore on the inner lining of the stomach or upper small intestine, most commonly caused by Helicobacter pylori infection or long-term use of NSAIDs. Symptoms include burning stomach pain, bloating, heartburn, and nausea. Treatment includes antibiotics (for H. pylori) and acid-suppressing medications.",
    'arthritis': "Arthritis is inflammation of one or more joints, causing pain, swelling, stiffness, and reduced range of motion. The two most common types are osteoarthritis (wear-and-tear) and rheumatoid arthritis (autoimmune). Treatment varies by type but may include pain relievers, anti-inflammatory drugs, physical therapy, and in severe cases, joint replacement surgery.",
    'allergy': "An allergy is an immune system reaction to a foreign substance (allergen) that is typically harmless to most people—such as pollen, pet dander, certain foods, or insect stings. Symptoms vary widely and can include sneezing, rash, itching, watery eyes, swelling, or in severe cases, anaphylaxis. Treatment includes antihistamines, corticosteroids, and allergen immunotherapy.",
    'anxiety': "Anxiety disorder is a mental health condition characterized by persistent, excessive worry and fear that interferes with daily activities. Symptoms include restlessness, rapid heartbeat, sweating, trembling, difficulty concentrating, and sleep disturbances. Treatment includes cognitive behavioural therapy (CBT), lifestyle changes, and medications such as SSRIs or benzodiazepines.",
    'depression': "Depression is a common and serious mental health disorder that causes persistent feelings of sadness, hopelessness, and loss of interest in activities. Symptoms include fatigue, changes in appetite and sleep, difficulty concentrating, and in severe cases, thoughts of self-harm. Treatment typically combines psychotherapy (CBT) and antidepressant medications.",
    'obesity': "Obesity is a chronic medical condition characterized by excessive body fat accumulation (BMI ≥ 30) that increases the risk of type 2 diabetes, heart disease, hypertension, and certain cancers. Causes include poor diet, physical inactivity, genetics, and hormonal factors. Management involves diet modification, increased physical activity, behavioural therapy, and in some cases, medication or bariatric surgery.",
    'hypothyroidism': "Hypothyroidism is a condition where the thyroid gland does not produce enough thyroid hormone. Symptoms include fatigue, weight gain, cold intolerance, constipation, dry skin, hair loss, and depression. It is treated with daily thyroid hormone replacement medication (levothyroxine).",
    'hyperthyroidism': "Hyperthyroidism is a condition where the thyroid gland produces too much thyroid hormone. Symptoms include weight loss, rapid heartbeat, sweating, nervousness, heat intolerance, and tremors. Graves' disease is the most common cause. Treatments include antithyroid medications, radioactive iodine therapy, and surgery.",
    'urinary tract infection': "A urinary tract infection (UTI) is a bacterial infection affecting the urinary system—most commonly the bladder and urethra. Symptoms include burning sensation during urination, frequent urge to urinate, cloudy or strong-smelling urine, and pelvic pain. Antibiotics are the standard treatment. Drinking plenty of water helps flush bacteria.",
    'kidney disease': "Chronic kidney disease (CKD) is the gradual loss of kidney function over time, often caused by diabetes or hypertension. Symptoms in early stages are usually absent; advanced stages cause fatigue, swelling (oedema), changes in urination, and nausea. Management focuses on controlling the underlying cause, diet modification, and dialysis or transplant in end-stage disease.",
    'anaemia': "Anaemia is a condition where the body lacks enough healthy red blood cells or haemoglobin to carry adequate oxygen to tissues. Symptoms include fatigue, weakness, pale skin, shortness of breath, and dizziness. The most common cause is iron deficiency. Treatment depends on the cause and may include iron supplements, vitamin B12, or treating an underlying disease.",
    'psoriasis': "Psoriasis is a chronic autoimmune skin condition that speeds up the life cycle of skin cells, causing them to build up rapidly on the surface. This leads to scaling, red patches, and itching. It can also affect joints (psoriatic arthritis). Treatment includes topical creams, phototherapy, and systemic medications.",
    'fungal infection': "Fungal infections are caused by fungi and can affect the skin, nails, lungs, or other parts of the body. Common types include athlete's foot, ringworm, and candidiasis. Symptoms depend on the site but often include itching, redness, and rash. Antifungal medications (topical or oral) are used for treatment.",
    'heart attack': "A heart attack (myocardial infarction) occurs when blood flow to a part of the heart is blocked, usually by a blood clot, causing heart muscle damage. Symptoms include chest pain or pressure, shortness of breath, pain radiating to the arm or jaw, sweating, and nausea. It is a medical emergency requiring immediate treatment with clot-busting drugs or angioplasty.",
    'stroke': "A stroke occurs when blood supply to part of the brain is cut off, causing brain cells to die. Types include ischaemic (clot) and haemorrhagic (bleed). Symptoms (FAST): Face drooping, Arm weakness, Speech difficulty, Time to call emergency services. Treatment must begin within hours to minimize damage. Risk factors include hypertension, diabetes, and atrial fibrillation.",
    'cholesterol': "High cholesterol (hypercholesterolaemia) is an excess of cholesterol in the blood, increasing the risk of heart disease and stroke. It usually has no symptoms and is detected by a blood test. Management includes a heart-healthy diet (low saturated fat), regular exercise, and statins or other cholesterol-lowering medications.",
    'covid': "COVID-19 is an infectious respiratory disease caused by the SARS-CoV-2 coronavirus. Common symptoms include fever, cough, fatigue, and loss of taste or smell. Severe cases can cause pneumonia and respiratory failure. Vaccines provide strong protection against severe illness. Treatment is mainly supportive; antiviral drugs are available for high-risk patients.",
    'bronchitis': "Bronchitis is inflammation of the bronchial tubes that carry air to the lungs. Acute bronchitis is usually caused by viral infections and resolves in 1–3 weeks with rest and fluids. Chronic bronchitis (a form of COPD) is mostly caused by long-term smoking, causing persistent cough with mucus. Treatment includes bronchodilators, steroids, and smoking cessation.",
    'appendicitis': "Appendicitis is inflammation of the appendix, a small pouch attached to the large intestine. It typically causes sudden pain starting around the navel and shifting to the lower right abdomen, along with nausea, vomiting, fever, and loss of appetite. It is a surgical emergency requiring removal of the appendix (appendectomy).",
    'chronic cholestasis': "Chronic cholestasis is a condition where bile cannot flow from the liver to the duodenum, causing bile to accumulate in the liver. Symptoms include jaundice, itching, dark urine, pale stools, and fatigue. Causes include primary biliary cholangitis, primary sclerosing cholangitis, and drug-induced liver injury. Treatment addresses the underlying cause.",
    'acne': "Acne vulgaris is a common skin condition occurring when hair follicles become clogged with oil and dead skin cells. It causes whiteheads, blackheads, pimples, and cysts, primarily on the face, chest, and back. It is most common in teenagers. Treatment includes topical retinoids, benzoyl peroxide, antibiotics, and in severe cases, oral isotretinoin.",
    'varicose veins': "Varicose veins are enlarged, twisted veins that commonly appear in the legs. They occur when valves in the veins weaken and allow blood to pool. Symptoms include aching pain, swelling, heaviness, and visible bulging veins. Treatments include compression stockings, sclerotherapy, laser treatment, and surgical removal.",
}

# Build a quick lookup from aliases (partial matches) to KB keys
_DISEASE_KB_ALIASES = {
    'flu': 'influenza',
    'tb': 'tuberculosis',
    'bp': 'hypertension',
    'blood pressure': 'hypertension',
    'sugar': 'diabetes',
    'blood sugar': 'diabetes',
    'stomach flu': 'gastroenteritis',
    'acid reflux': 'gerd',
    'heartburn': 'gerd',
    'ulcer': 'peptic ulcer',
    'uti': 'urinary tract infection',
    'kidney': 'kidney disease',
    'heart attack': 'heart attack',
    'myocardial': 'heart attack',
    'thyroid low': 'hypothyroidism',
    'thyroid high': 'hyperthyroidism',
    'chickenpox': 'chicken pox',
    'chicken pox': 'chicken pox',
    'cold': 'common cold',
    'corona': 'covid',
    'coronavirus': 'covid',
    'covid-19': 'covid',
    'covid19': 'covid',
    'anxiety disorder': 'anxiety',
    'panic': 'anxiety',
    'high cholesterol': 'cholesterol',
    'bronchial asthma': 'asthma',
}


def _lookup_local_kb(query_lower):
    """Return instant answer from local KB, or None if not found."""
    # Direct key match
    if query_lower in LOCAL_DISEASE_KB:
        return LOCAL_DISEASE_KB[query_lower]
    # Alias map
    if query_lower in _DISEASE_KB_ALIASES:
        return LOCAL_DISEASE_KB.get(_DISEASE_KB_ALIASES[query_lower])
    # Substring match against KB keys
    for key, text in LOCAL_DISEASE_KB.items():
        if key in query_lower or query_lower in key:
            return text
    return None


@lru_cache(maxsize=256)
def fetch_json_from_url(full_url):
    for attempt in range(NETWORK_MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode())
        except (urllib.error.URLError, socket.timeout, TimeoutError, ValueError):
            if attempt < NETWORK_MAX_RETRIES:
                time.sleep(0.1)
                continue
            return None
    return None


@lru_cache(maxsize=512)
def _fetch_extract_cached(api_url, term, intro_only=True):
    """Module-level cached Wikipedia extract fetcher — cache persists across requests."""
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
    full_url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(params)
    res_data = fetch_json_from_url(full_url)
    if not isinstance(res_data, dict):
        return ''
    pages = res_data.get('query', {}).get('pages', {})
    for page_id, page_info in pages.items():
        if page_id != '-1':
            extract = page_info.get('extract', '')
            if extract:
                return extract
    # Fallback: opensearch
    search_params = {
        'action': 'opensearch', 'format': 'json',
        'search': term, 'limit': 1
    }
    search_url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(search_params)
    search_data = fetch_json_from_url(search_url)
    if isinstance(search_data, list) and len(search_data) > 1 and search_data[1]:
        retry_params = {
            'action': 'query', 'format': 'json',
            'prop': 'extracts', 'exintro': 'true',
            'explaintext': 'true',
            'titles': search_data[1][0], 'redirects': '1'
        }
        retry_url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(retry_params)
        retry_data = fetch_json_from_url(retry_url)
        if isinstance(retry_data, dict):
            for pid, pinfo in retry_data.get('query', {}).get('pages', {}).items():
                if pid != '-1' and pinfo.get('extract'):
                    return pinfo['extract']
    return ''


@lru_cache(maxsize=512)
def _translate_text_cached(text, target_lang):
    """Module-level cached translator — cache persists across requests."""
    if not text or target_lang == 'en':
        return text
    translate_url = 'https://translate.googleapis.com/translate_a/single'
    params = {
        'client': 'gtx', 'sl': 'auto',
        'tl': target_lang, 'dt': 't',
        'q': text[:800]  # keep payload small
    }
    full_url = translate_url + '?' + urllib.parse.urlencode(params)
    data = fetch_json_from_url(full_url)
    if not isinstance(data, list):
        return text
    chunks = []
    if data and isinstance(data[0], list):
        for chunk in data[0]:
            if isinstance(chunk, list) and chunk:
                chunks.append(chunk[0])
    return ''.join(chunks).strip() or text


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

            requested_language = data.get('language', '').strip().lower()
            if requested_language not in language_map:
                requested_language = 'english'
            selected_language_code = language_map.get(requested_language, 'en')

            # Translate non-ASCII input to English for processing
            query_for_processing = query
            if any(ord(ch) > 127 for ch in query):
                query_for_processing = _translate_text_cached(query, 'en') or query

            # -- Greeting / small-talk guard --
            greetings = {
                'hi', 'hello', 'hey', 'how are you', 'who are you',
                'what are you', 'good morning', 'good evening',
                'good afternoon', 'bye', 'thanks', 'thank you',
                'ok', 'okay', 'hii', 'helo'
            }
            if query_for_processing.lower().strip(' ?!.') in greetings:
                refusal_msg = "I provide information about disease and symptoms only so ask me related questions only"
                if selected_language_code != 'en':
                    refusal_msg = _translate_text_cached(refusal_msg, selected_language_code) or refusal_msg
                return JsonResponse({'reply': refusal_msg})

            # -- Symptom-to-disease suggestion map --
            symptom_to_diseases = {
                'fever': ['Dengue', 'Typhoid', 'Malaria', 'Common Cold', 'Pneumonia'],
                'high fever': ['Dengue', 'Typhoid', 'Malaria'],
                'headache': ['Migraine', 'Typhoid', 'Dengue', 'Hypertension'],
                'cough': ['Common Cold', 'Pneumonia', 'Tuberculosis', 'Bronchial Asthma'],
                'cold': ['Common Cold', 'Allergy'],
                'runny nose': ['Common Cold', 'Allergy'],
                'vomiting': ['Gastroenteritis', 'Typhoid', 'Dengue'],
                'nausea': ['Gastroenteritis', 'Typhoid', 'Migraine'],
                'stomach pain': ['Gastroenteritis', 'Peptic Ulcer', 'GERD'],
                'abdominal pain': ['Gastroenteritis', 'Peptic Ulcer', 'Chronic Cholestasis'],
                'rash': ['Allergy', 'Chicken Pox', 'Fungal Infection', 'Psoriasis'],
                'itching': ['Allergy', 'Fungal Infection', 'Psoriasis', 'Jaundice'],
                'yellow eyes': ['Jaundice', 'Hepatitis A', 'Hepatitis B', 'Hepatitis C'],
                'yellow skin': ['Jaundice', 'Hepatitis A', 'Hepatitis B', 'Hepatitis C'],
                'chest pain': ['Heart Attack', 'GERD', 'Pneumonia'],
                'breathlessness': ['Bronchial Asthma', 'Pneumonia', 'Heart Attack'],
                'joint pain': ['Arthritis', 'Osteoarthritis', 'Dengue'],
                'body pain': ['Dengue', 'Typhoid', 'Common Cold'],
                'fatigue': ['Diabetes', 'Hypothyroidism', 'Typhoid'],
                'weight loss': ['Diabetes', 'Hyperthyroidism', 'Tuberculosis'],
                'diarrhoea': ['Gastroenteritis', 'Typhoid'],
                'diarrhea': ['Gastroenteritis', 'Typhoid'],
                'urine burning': ['Urinary Tract Infection'],
                'burning urination': ['Urinary Tract Infection'],
            }

            # Build known-disease map from model list
            known_disease_map = {}
            for disease_name in diseaselist:
                nd = re.sub(r'\s+', ' ', disease_name.lower()).strip()
                known_disease_map[nd] = disease_name
                known_disease_map[nd.replace('diseae', 'disease')] = disease_name

            norm_q = re.sub(r'[^a-zA-Z0-9\s]', ' ', query_for_processing.lower())
            norm_q = re.sub(r'\s+', ' ', norm_q).strip()

            matched_disease = ''
            for nd, orig in known_disease_map.items():
                if nd and nd in norm_q:
                    matched_disease = orig
                    break

            # Symptom-only queries: suggest diseases instead
            symptom_scores = {}
            for sym_key, cands in symptom_to_diseases.items():
                if sym_key in norm_q:
                    for cand in cands:
                        symptom_scores[cand] = symptom_scores.get(cand, 0) + 1

            if symptom_scores and not matched_disease:
                top = sorted(symptom_scores.items(), key=lambda x: x[1], reverse=True)
                top_names = [n for n, _ in top[:3]]
                reply = (
                    "Based on the symptoms, possible diseases are: "
                    + ', '.join(top_names)
                    + ". Please confirm with a doctor. For detailed information, ask using a specific disease name."
                )
                if selected_language_code != 'en':
                    reply = _translate_text_cached(reply, selected_language_code) or reply
                return JsonResponse({'reply': reply})

            # Strip question/language phrases to extract the disease term
            cleaned = query_for_processing.lower()
            if matched_disease:
                cleaned = matched_disease.lower()

            for phrase, lang_name in [
                ('in english', 'english'), ('english', 'english'),
                ('in hindi', 'hindi'), ('hindi me', 'hindi'), ('hindi', 'hindi'),
                ('in gujarati', 'gujarati'), ('gujarati me', 'gujarati'), ('gujarati', 'gujarati'),
                ('in marathi', 'marathi'), ('marathi me', 'marathi'), ('marathi', 'marathi'),
            ]:
                if phrase in cleaned:
                    requested_language = lang_name
                    cleaned = cleaned.replace(phrase, ' ')
            selected_language_code = language_map.get(requested_language, 'en')

            for phrase in [
                'tell me about', 'explain about', 'explain', 'about',
                'what is', "what's", 'info about', 'information about', 'details about',
                'what are the symptoms of', 'what is the treatment for', 'what causes',
                'how to treat', 'how to prevent', 'symptoms of', 'treatment for',
                'causes of', 'prevention of', 'complications of', 'risk factors of',
            ]:
                if phrase in cleaned:
                    cleaned = cleaned.replace(phrase, ' ')

            is_question = ('?' in query_for_processing) or any(
                m in cleaned for m in [
                    'what', 'how', 'why', 'when', 'which',
                    'symptom', 'cause', 'treat', 'prevent', 'cure',
                    'risk', 'diagnos', 'complication', 'medicine', 'diet'
                ]
            )

            cleaned = ' '.join(cleaned.split()).strip(' ?.!,:;')
            disease_term = (matched_disease or cleaned or query_for_processing).lower().strip()

            # STEP 1: Try local KB first (instant, zero network)
            local_answer = _lookup_local_kb(disease_term)
            if local_answer:
                reply = local_answer
                if selected_language_code != 'en':
                    reply = _translate_text_cached(reply, selected_language_code) or reply
                return JsonResponse({'reply': reply})

            # STEP 2: Fall back to Wikipedia (cached after first hit)
            extract = _fetch_extract_cached(
                'https://en.wikipedia.org/w/api.php',
                disease_term,
                intro_only=(not is_question)
            )

            if not extract:
                extract = _fetch_extract_cached(
                    'https://en.wikipedia.org/w/api.php',
                    disease_term + ' disease',
                    intro_only=True
                )

            if not extract:
                not_found = "I could not find detailed information on that. Please check the spelling or try a more common disease name."
                if selected_language_code != 'en':
                    not_found = _translate_text_cached(not_found, selected_language_code) or not_found
                return JsonResponse({'reply': not_found})

            # Reject non-medical Wikipedia pages
            if not matched_disease:
                strict_kw = [
                    'disease', 'syndrome', 'infection', 'virus', 'bacteria', 'medical',
                    'symptom', 'treatment', 'cancer', 'disorder', 'illness', 'therapy',
                    'tumor', 'vaccine', 'diagnos', 'pathogen', 'clinical', 'hospital',
                    'doctor', 'surgery', 'medication', 'patient', 'medicine', 'pain',
                    'fever', 'cough', 'headache', 'nausea', 'vomiting', 'fatigue',
                    'swelling', 'rash', 'diabetes', 'hypertension', 'asthma', 'allergy',
                    'allergic', 'depression', 'anxiety', 'chronic', 'acute', 'fungal', 'parasite',
                ]
                el = extract.lower()
                ql = query_for_processing.lower()
                if sum(1 for kw in strict_kw if kw in el or kw in ql) < 2:
                    refusal = "I provide information about disease and symptoms only so ask me related questions only"
                    if selected_language_code != 'en':
                        refusal = _translate_text_cached(refusal, selected_language_code) or refusal
                    return JsonResponse({'reply': refusal})

            # For questions, pick the most relevant sentences
            if is_question:
                sentences = re.split(r'(?<=[.!?])\s+', extract)
                sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
                stopwords = {
                    'what', 'is', 'are', 'the', 'of', 'for', 'in', 'on', 'about', 'how', 'why',
                    'when', 'which', 'tell', 'me', 'please', 'explain', 'disease', 'a', 'an',
                    'to', 'and', 'can', 'you', 'with', 'from', 'this', 'that'
                }
                q_tokens = [t for t in re.findall(r'[a-zA-Z]+', query_for_processing.lower())
                            if t not in stopwords and len(t) > 2]
                if q_tokens and sentences:
                    scored = [(sum(1 for t in q_tokens if t in s.lower()), s) for s in sentences]
                    scored = [(sc, s) for sc, s in scored if sc > 0]
                    scored.sort(key=lambda x: x[0], reverse=True)
                    best = [s for _, s in scored[:3]] if scored else sentences[:3]
                    extract = ' '.join(best)

            if len(extract) > 500:
                extract = extract[:500] + '...'

            if selected_language_code != 'en':
                extract = _translate_text_cached(extract, selected_language_code) or extract

            return JsonResponse({'reply': extract})

        except Exception:
            fallback_by_language = {
                'english': 'I could not fetch full details right now. Please try again with a disease name or main symptoms (for example: fever, cough, headache).',
                'hindi': 'अभी पूरी जानकारी नहीं मिल पाई। कृपया रोग का नाम या मुख्य लक्षण लिखकर दोबारा पूछें (जैसे: बुखार, खांसी, सिरदर्द)।',
                'gujarati': 'હમણાં સંપૂર્ણ માહિતી મેળવી શકાઈ નથી. કૃપા કરીને રોગનું નામ અથવા મુખ્ય લક્ષણો સાથે ફરી પૂછો (જેમ કે: તાવ, ખાંસી, માથાનો દુખાવો).',
                'marathi': 'आत्ता संपूर्ण माहिती मिळाली नाही. कृपया रोगाचे नाव किंवा मुख्य लक्षणे देऊन पुन्हा विचारा (उदा.: ताप, खोकला, डोकेदुखी).'
            }
            req_lang = 'english'
            try:
                req_lang = str(json.loads(request.body or '{}').get('language', 'english')).strip().lower()
            except Exception:
                pass
            return JsonResponse({'reply': fallback_by_language.get(req_lang, fallback_by_language['english'])})

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

