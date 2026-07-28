import random
import pandas as pd
from faker import Faker

fake = Faker('en_IN')
Faker.seed(42)
random.seed(42)

NUM_ROWS = 100

data = []
for _ in range(NUM_ROWS):
    name = fake.first_name()
    # ~10% missing values for Age
    age = None if random.random() < 0.1 else fake.random_int(min=18, max=65)
    salary = fake.random_int(min=30000, max=120000, step=500)
    purchased = random.choice(["Yes", "No"])

    data.append({
        "Name": name,
        "Age": age,
        "Salary": salary,
        "Purchased": purchased
    })

df = pd.DataFrame(data)
df.to_csv("data/raw_fake.csv", index=False)
print(f"Generated {len(df)} synthetic rows in data/raw_fake.csv")
