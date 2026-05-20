import joblib
import warnings

warnings.filterwarnings('ignore')
model = joblib.load('model.pkl')
print('n_features_in_:', getattr(model, 'n_features_in_', None))

try:
    model.predict([[0]*17])
    print('Predicts on 17 OK')
except Exception as e:
    print('Error on 17:', e)

try:
    model.predict([[0]*132])
    print('Predicts on 132 OK')
except Exception as e:
    print('Error on 132:', e)
