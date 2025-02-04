import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import base64
import logging
from app.file_processing import read_concatenated_file





# Set up logging
def setup_logger():
    logger = logging.getLogger("streamlit_main")
    logger.setLevel(logging.ERROR)

    handler = logging.FileHandler("logs/streamlit_main.log")
    handler.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger





logger = setup_logger()





# Streamlit Configuration
# URL of the FastAPI backend (replace with your actual FastAPI URL)
API_URL = "http://127.0.0.1:8000"





# Streamlit Interface
st.set_page_config(page_title="Ad Campaign File Upload and Query System", page_icon="📈", layout="wide")





# Sidebar with description and instructions
st.sidebar.title("Instructions:")
st.sidebar.write(
    """


    This app allows you to upload ad campaign data files (CSV/XLSX) and ask questions related to the data.


    1. **Upload your files**: You can upload multiple files (CSV or Excel).


    2. **Ask a Query**: Enter any query related to the data, like 'Show impressions vs time' or 'Generate graph'.
    

    3. **See Results**: Get your query results or visualizations!
    """
)


# Main Title
st.title("Ad Campaign File Upload and Query System 📊")





# File upload with enhanced guidance
st.subheader("Upload Ad Campaign Files")
uploaded_files = st.file_uploader("Choose CSV/XLSX files", type=["csv", "xlsx"], accept_multiple_files=True)
st.markdown("**Note**: Ensure your file structure is consistent for successful concatenation.")






if uploaded_files:
    files = []
    for uploaded_file in uploaded_files:

        files.append(("files", (uploaded_file.name, uploaded_file, uploaded_file.type)))

    # Button to trigger file concatenation (not uploading immediately)
    if st.button("Concatenate Files"):

        if files:
            with st.spinner("Uploading and concatenating files..."):
                try:
                    # Send files to the backend for processing
                    response = requests.post(f"{API_URL}/upload/", files=files)

                    if response.status_code == 200:
                        st.success(f"Files uploaded and concatenated successfully! {response.json()['message']}")
                        st.write("Output file path:", response.json().get("output_file"))
                        df = read_concatenated_file()
                        st.write(df.describe().T)



                    else:
                        st.error(f"Error uploading files: {response.json()['detail']}")

                except requests.exceptions.RequestException as e:
                    logger.error("File concatenation request failed: %s", e)
                    st.error("An error occurred while uploading the files. Please try again.")
        
        else:

            st.warning("Please upload files first.")





# Query Section with input box and improved UX
st.subheader("Ask Your Query")





# Input for the query
query = st.text_input("Enter your query (e.g., 'Show impressions vs time')")





# Button to trigger query processing
if st.button("Submit Query") and query:

    with st.spinner("Processing your query..."):

        try:

                
            query_payload = {"prompt": query}
            response = requests.post(f"{API_URL}/query/", json=query_payload)

            if response.status_code == 200:

                data = response.json()

                if "image" in data:
                    # Display the visualization
                    image_data = BytesIO(base64.b64decode(data["image"]))
                    image = Image.open(image_data)
                    st.image(image, caption="Generated Visualization", use_column_width=True)

                else:
                    st.write(data["response"])

            else:
                st.error(f"Error with query: {response.json()['detail']}")

        except requests.exceptions.RequestException as e:
            logger.error("Query submission failed: %s", e)
            st.error("An error occurred while processing your query. Please try again.")






# Add a footer
st.markdown(
    """
    --- 
    Developed for Segumento ❤️

    If you are getting any error, just try again.

    LLMs can make mistakes, so double-check it.
    """
)


