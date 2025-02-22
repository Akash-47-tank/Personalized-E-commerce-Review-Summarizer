from src.utils.data_generator import generate_sample_data
import os

def main():
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Generate sample data
    output_path = os.path.join(data_dir, "generated_reviews.csv")
    generate_sample_data(output_path, num_reviews=200)

if __name__ == "__main__":
    main()
