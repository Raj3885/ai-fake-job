import pandas as pd
from sklearn.utils import resample

# Load dataset
print("Loading dataset...")
df = pd.read_csv('fake_job_postings.csv')

print(f"Original dataset shape: {df.shape}")
print("Class distribution before balancing:")
print(df['fraudulent'].value_counts())

# Preprocessing: Handling missing values
print("Preprocessing: Filling missing values for text columns with empty strings...")
text_cols = ['title', 'location', 'department', 'salary_range', 'company_profile', 
             'description', 'requirements', 'benefits', 'employment_type', 
             'required_experience', 'required_education', 'industry', 'function']

for col in text_cols:
    if col in df.columns:
        df[col] = df[col].fillna(' ')

# Separate majority and minority classes
df_majority = df[df['fraudulent'] == 0]
df_minority = df[df['fraudulent'] == 1]

print(f"Fake job postings (1) count: {len(df_minority)}")
print(f"Real job postings (0) count: {len(df_majority)}")

if len(df_minority) < len(df_majority):
    print("Fake job posting is indeed the minority class. Proceeding with oversampling...")
    # Oversample minority class
    df_minority_upsampled = resample(df_minority, 
                                     replace=True,     # sample with replacement
                                     n_samples=len(df_majority),    # to match majority class
                                     random_state=42) # reproducible results
    
    # Combine majority class with upsampled minority class
    df_balanced = pd.concat([df_majority, df_minority_upsampled])
    
    # Shuffle the dataset so that classes are mixed
    df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("Class distribution after balancing:")
    print(df_balanced['fraudulent'].value_counts())
    
    output_filename = 'fake_job_postings_oversampled.csv'
    df_balanced.to_csv(output_filename, index=False)
    print(f"Saved balanced dataset to: {output_filename}")
else:
    print("Fake job posting is not the minority class. No further action taken.")
