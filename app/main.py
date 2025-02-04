from fastapi import FastAPI, Query, UploadFile, File, HTTPException
from pathlib import Path
from typing import List
from app.file_processing import save_uploaded_file, validate_and_concatenate_files, read_concatenated_file
from .query_handler import handle_user_query
from .graph_generator import generate_visualization_code, execute_visualization_code
from pydantic import BaseModel
import logging





# Set up logger for main.py
def setup_logger():
    logger = logging.getLogger("main")
    logger.setLevel(logging.ERROR)

    handler = logging.FileHandler("logs/main.log")
    handler.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger




# Initialize the logger
logger = setup_logger()

app = FastAPI()





# Consistent upload directory (UPLOAD_DIR)
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)






@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    if len(files) > 60:
        logger.error("File upload exceeded limit: %d files", len(files))
        raise HTTPException(status_code=400, detail="You can upload a maximum of 60 files.")

    file_paths = []
    for file in files:
        file_path = await save_uploaded_file(file, UPLOAD_DIR)
        file_paths.append(file_path)

    # Validate and concatenate files
    try:
        concatenated_file_path = validate_and_concatenate_files(file_paths, UPLOAD_DIR)
        logger.info("Files concatenated successfully.")
        return {"message": "Files concatenated successfully", "output_file": str(concatenated_file_path)}
    except Exception as e:
        logger.error("Error during file concatenation: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Concatenation failed: {str(e)}")

class QueryRequest(BaseModel):
    prompt: str







@app.post("/query/")
async def query_data(request: QueryRequest):
    """
    Endpoint to query the concatenated ad campaign data or generate visualizations.
    """
    try:
        df = read_concatenated_file()
        if df is None:
            logger.error("No concatenated file found when processing query: %s", request.prompt)
            raise HTTPException(status_code=404, detail="No concatenated file found.")
        
        # Check if the prompt is related to visualization
        if any(keyword in request.prompt.lower() for keyword in ["plot", "visualize", "graph", "chart"]):
            # Generate and execute visualization code 

            data_sample = df.head(5).to_string(index=False)  # Provide a sample of the data
            visualization_code = generate_visualization_code(request.prompt, data_sample)
            image_base64 = execute_visualization_code(visualization_code, df)
            logger.info("Visualization generated successfully for prompt: %s", request.prompt)
            return {"response": "Visualization generated successfully.", "image": image_base64}

        else:
            # Handle as a regular query
            response = handle_user_query(request.prompt, df)
            logger.info("Query handled successfully for prompt: %s", request.prompt)
            return {"response": response}

    except Exception as e:
        logger.error("Error processing query '%s': %s", request.prompt, str(e))
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")



