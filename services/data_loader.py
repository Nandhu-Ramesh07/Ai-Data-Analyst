import pandas as pd

def load_data(uploaded_file):
    
    """
    Load data from an uploaded file (CSV or Excel).
    """
    
    file_name = uploaded_file.name.lower()

    if file_name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    elif file_name.endswith('.xlsx'):
        data = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
    