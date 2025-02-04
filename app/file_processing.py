import pandas as pd
from pathlib import Path
from typing import List, Optional
import os
import logging
from fastapi import HTTPException





# Set up logger for query_handler.py
def setup_logger():
    logger = logging.getLogger("query_handler")
    logger.setLevel(logging.ERROR)

    handler = logging.FileHandler("logs/query_handler.log")
    handler.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger




logger = setup_logger()






RUNTIME_DIR = Path("runtime")
concatenated_file_path = RUNTIME_DIR / "concatenated_file.xlsx"






if not RUNTIME_DIR.exists():
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    logger.error("Runtime directory created: %s", RUNTIME_DIR)  # Log runtime directory creation





async def save_uploaded_file(file, upload_dir: Path) -> Path:
    """Save the uploaded file to the specified directory."""
    try:
        file_path = upload_dir / file.filename
        with file_path.open("wb") as buffer:
            buffer.write(await file.read())
        return file_path
    except Exception as e:
        logger.error("Error saving uploaded file: %s", str(e))
        raise HTTPException(status_code=500, detail="Error saving uploaded file.")





def validate_and_concatenate_files(file_paths: List[Path], output_dir: Path) -> Path:
    """Validate structure and concatenate files if they have the same columns."""
    dataframes = []
    columns = None

    try:

        for file_path in file_paths:
            file_extension = os.path.splitext(file_path)[1].lower()  # Get the file extension

            if file_extension in ['.csv']:
                    df = pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                logger.error("Unsupported file format: %s",file_path)
                continue  # Skip unsupported files
                

            if columns is None:
                columns = list(df.columns)
            elif list(df.columns) != columns:
                raise ValueError(f"File {file_path.name} has a different structure.")

            # Check for empty values in the current dataframe
            if df.isnull().values.any():
                raise ValueError(f"File {file_path.name} contains empty values. Please clean the data.")

            dataframes.append(df)

        concatenated_df = pd.concat(dataframes, ignore_index=True)

        # Check for empty values in the concatenated dataframe
        if concatenated_df.isnull().values.any():
            logger.error("Empty values found in the concatenated dataframe.")  # Log the error
            raise ValueError("The concatenated dataframe contains empty values. Please clean the data.")

        # Save to RUNTIME_DIR instead of UPLOAD_DIR
        output_file_path = RUNTIME_DIR / "concatenated_file.xlsx"
        concatenated_df.to_excel(output_file_path, index=False)

        # Optionally delete the individual uploaded files after concatenation
        for file_path in file_paths:
            os.remove(file_path)

        return output_file_path



    except ValueError as ve:
        logger.error("Validation error during file processing: %s", ve)
        raise HTTPException(status_code=400, detail=str(ve))


    except Exception as e:
        logger.error("Unexpected error in file processing: %s", e)
        raise HTTPException(status_code=500, detail="Error concatenating files.")




def read_concatenated_file() -> Optional[pd.DataFrame]:
    """Reads the concatenated Excel file and returns a DataFrame."""
    try:
        df = pd.read_excel(concatenated_file_path)
        return df
    except Exception as e:
        logger.error("Error reading the concatenated file: %s",e)
        return None
    

 