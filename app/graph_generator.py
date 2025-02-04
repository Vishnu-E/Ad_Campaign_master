import openai
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from fastapi import HTTPException
import logging





# Set up logger for graph_generator.py
def setup_logger():
    logger = logging.getLogger("graph_generator")
    logger.setLevel(logging.ERROR)

    handler = logging.FileHandler("logs/graph_generator.log")  # Log directory and file
    handler.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger





logger = setup_logger()






def generate_visualization_code(prompt, data_sample):
    """
    Generates Python code for data visualization based on a user prompt.

    Args:
        prompt (str): User's prompt describing the desired visualization.
        data_sample (str): String representation of the data (first few rows).

    Returns:
        str: Python code for the visualization.
    """
    user_query = f"""
    Here is a sample of the dataset:
    {data_sample}

    Generate Python code for the following visualization. 
    Use the variable name 'data' for the dataset. 
    Also mention code to convert date columns to month-date-year format format to if needed.
    should handle this error : Visualization Execution Failed: time data 13-01-2022 doesn't match format %m-%d-%Y, at position 12. You might want to try: - passing `format` if your strings have a consistent format; - passing `format='ISO8601'` if your strings are all ISO8601 but not necessarily in exactly the same format; - passing `format='mixed'`, and the format will be inferred for each element individually. You might want to use `dayfirst` alongside this.
    Return only the code with plt.plot:
    {prompt}
    """

    try:
        response =openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a data scientist who writes Python code for data visualization. Always use the variable name 'data' for the dataset. Do not include any explanations or comments in the response."
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            temperature=0.6
        )

        # Extract and return only the code
        code = response.choices[0].message.content
        code = code.strip().replace("```python", "").replace("```", "")  # Clean Markdown markers
        print(code)
        return code

    except Exception as e:
        logger.error("Visualization Code Generation Failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Visualization Code Generation Failed: {e}")






def execute_visualization_code(code, data):
    """
    Executes the generated Python code and returns the plot as a Base64-encoded image.

    Args:
        code (str): The Python code to execute.
        data (pd.DataFrame): The dataset used for visualization.

    Returns:
        str: Base64-encoded image of the plot.
    """
    try:
        # Define a local scope for the code execution
        local_scope = {"data": data, "plt": plt, "pd":pd}

        # Execute the code
        exec(code, {}, local_scope)

        # Save the plot to a BytesIO object
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        # Encode the image to Base64
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        # return local_scope['plt'] 
        return image_base64

    except Exception as e:
        logger
        raise HTTPException(status_code=500, detail=f"Visualization Execution Failed: {e}")

