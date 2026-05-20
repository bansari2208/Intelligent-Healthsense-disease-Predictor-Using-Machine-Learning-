import joblib
import pprint

model = joblib.load('model.pkl')
print(type(model))
print(dir(model))
# Print the classes
if hasattr(model, 'classes_'):
    print("Classes:", model.classes_)

if hasattr(model, 'feature_count_'):
    print("Feature count shape:", model.feature_count_.shape)

