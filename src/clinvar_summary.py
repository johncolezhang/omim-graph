import pandas as pd
import json

def handle_summary():
    df_variant = pd.read_csv("data/clinvar/variant_summary.txt", sep="\t", dtype=str).fillna("")
    print()

if __name__ == "__main__":
    handle_summary()