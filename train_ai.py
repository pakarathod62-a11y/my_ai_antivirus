import csv
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

print("1. Reading and cleaning dataset...")

clean_rows = []
with open('dataset.csv', 'r', encoding='latin1', errors='ignore') as f:
    reader = csv.reader((line.replace('\x00', '') for line in f))
    for i, row in enumerate(reader):
        if i >= 1000:
            break
        if row:
            clean_rows.append(row)

# कॉलम नेम देने के बजाय ऑटोमैटिक कॉलम्स जनरेट किए गए हैं
data = pd.DataFrame(clean_rows).dropna()

# डेटा को नंबर में बदलें
for col in data.columns:
    data[col] = LabelEncoder().fit_transform(data[col].astype(str))

X = data.iloc[:, :-1] 
y = data.iloc[:, -1]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("2. Training AI model...")
model = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, 'antivirus_ai_model.pkl')
print("3. SUCCESS! AI model saved as antivirus_ai_model.pkl!")
