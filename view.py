import os
import pandas as pd
import matplotlib.pyplot as plt

# Define the path to your Excel file relative to this script
file_path = os.path.join(os.path.dirname(__file__), "verification.xlsx")

def plot_verification_data(path):
    # Check if the file exists before proceeding
    if not os.path.exists(path):
        print(f"Error: The file at '{path}' could not be found.")
        print("Please verify the file path and try again.")
        return

    try:
        # Read the Excel file (requires 'openpyxl' dependency installed)
        df = pd.read_excel(path, sheet_name=1)  # sheet_name=1 reads the 2nd sheet (0-indexed)
        
        # Clean column names by removing any accidental leading/trailing whitespaces
        df.columns = df.columns.str.strip()
        
        # Expected column names
        x_col = 't'
        y_col = 'del H'
        
        # Verify if columns exist in the sheet
        if x_col in df.columns and y_col in df.columns:
            # Sort by time 't' to ensure line plots connect properly sequentially
            df = df.sort_values(by=x_col)
            
            # Create the plot
            # Using LaTeX notation for professional mathematical labels
            plt.plot(df[x_col], df[y_col], marker='o', markersize=4, linestyle='-', color='#1f77b4', linewidth=1.5, label=r'$\Delta H$')
            
            # Labeling axes and title
            plt.xlabel(r'Time, $t$', fontsize=12)
            plt.ylabel(r'Change in Head, $\Delta H$', fontsize=12)
            plt.title(r'Verification Analysis: $\Delta H$ vs $t$', fontsize=14, fontweight='bold', pad=15)
            
            # Enhancing plot appearance
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.legend(loc='best', fontsize=11)
            
            # Ensure labels are not truncated or overlapping
            plt.tight_layout()
            
            # Display the plot window
            plt.show()
            
        else:
            print(f"Error: Could not find both '{x_col}' and '{y_col}' columns.")
            print(f"Found columns in file: {df.columns.tolist()}")
            
    except Exception as e:
        print(f"An unexpected error occurred while reading or plotting the data: {e}")

if __name__ == "__main__":
    plot_verification_data(file_path)