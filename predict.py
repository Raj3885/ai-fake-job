import pandas as pd
import joblib
import sys
import os
from contextlib import contextmanager

from ml_pipeline import text_agent, keyword_agent, sentiment_agent, combine_features

@contextmanager
def suppress_stdout():
    """Context manager to suppress print statements from the pipeline agents"""
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

def interactive_inference():
    print("Loading saved model and vectorizer...")
    
    with suppress_stdout():
        model = joblib.load("xgboost_model.pkl")
        vectorizer = joblib.load("tfidf_vectorizer.pkl")
        auto_fraud_keywords = joblib.load("auto_fraud_keywords.pkl")
    
    print("Ready.\n")
    
    while True:
        try:
            user_input = input("Enter text (type 'exit' to stop):\n> ").strip()
            if not user_input:
                continue
            if user_input.lower() == 'exit':
                break
                
            # Formatting input text explicitly to match train structure
            word_count = len(user_input.split())
            modified_text = user_input
            if word_count < 20: # Keyword duplication padding
                modified_text = f"{user_input} {user_input} {user_input}"
                
            simulated_structure = (f"TITLE: {modified_text} "
                                   f"COMPANY: "
                                   f"DESCRIPTION: {modified_text} "
                                   f"REQUIREMENTS: {modified_text} "
                                   f"BENEFITS:")
                                   
            text_series = pd.Series([simulated_structure])
            
            # Hide the raw agent print logs so the CLI remains clean
            with suppress_stdout():
                clean_text = text_agent(text_series)
                tfidf_matrix = vectorizer.transform(clean_text)
                keyword_features, _ = keyword_agent(clean_text, auto_fraud_keywords)
                sentiment_features, _ = sentiment_agent(clean_text)
                final_features = combine_features(tfidf_matrix, keyword_features, sentiment_features)
                
                predictions = model.predict(final_features)
                probabilities = model.predict_proba(final_features)
            
            # Predict and parse probabilities
            label = "Fake" if predictions[0] == 1 else "Real"
            risk_prob = probabilities[0][1] # Probability the class is exactly 1 (Fake)
            class_prob = probabilities[0][predictions[0]] # Probability of chosen prediction
            
            print(f"\nPrediction: {label}")
            print(f"Confidence: {class_prob:.2f}")
            print(f"Risk Score: {int(risk_prob * 100)}%\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error processing prediction: {e}")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    interactive_inference()
