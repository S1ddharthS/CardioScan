import csv
import random

def generate_heart_data(num_rows=300):
    header = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']
    
    with open('heart.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        for _ in range(num_rows):
            # Generate realistic-ish synthetic data
            target = random.choice([0, 1])
            
            if target == 1:
                # Higher risk profile
                age = random.randint(45, 75)
                sex = random.choices([0, 1], weights=[0.2, 0.8])[0]
                cp = random.choices([0, 1, 2, 3], weights=[0.4, 0.3, 0.2, 0.1])[0]
                trestbps = random.randint(120, 180)
                chol = random.randint(200, 350)
                fbs = random.choices([0, 1], weights=[0.7, 0.3])[0]
                restecg = random.choices([0, 1, 2], weights=[0.3, 0.5, 0.2])[0]
                thalach = random.randint(100, 150)
                exang = random.choices([0, 1], weights=[0.4, 0.6])[0]
                oldpeak = round(random.uniform(1.0, 4.0), 1)
                slope = random.choices([0, 1, 2], weights=[0.2, 0.5, 0.3])[0]
                ca = random.choices([0, 1, 2, 3, 4], weights=[0.2, 0.3, 0.3, 0.1, 0.1])[0]
                thal = random.choices([1, 2, 3], weights=[0.1, 0.3, 0.6])[0]
            else:
                # Lower risk profile
                age = random.randint(29, 60)
                sex = random.choices([0, 1], weights=[0.5, 0.5])[0]
                cp = random.choices([0, 1, 2, 3], weights=[0.1, 0.2, 0.4, 0.3])[0]
                trestbps = random.randint(90, 130)
                chol = random.randint(120, 220)
                fbs = random.choices([0, 1], weights=[0.9, 0.1])[0]
                restecg = random.choices([0, 1, 2], weights=[0.8, 0.15, 0.05])[0]
                thalach = random.randint(140, 200)
                exang = random.choices([0, 1], weights=[0.9, 0.1])[0]
                oldpeak = round(random.uniform(0.0, 1.0), 1)
                slope = random.choices([0, 1, 2], weights=[0.5, 0.3, 0.2])[0]
                ca = random.choices([0, 1, 2, 3, 4], weights=[0.8, 0.1, 0.05, 0.05, 0.0])[0]
                thal = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
                
            writer.writerow([age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target])

if __name__ == '__main__':
    generate_heart_data()
    print("Created heart.csv with 300 rows of synthetic data.")
