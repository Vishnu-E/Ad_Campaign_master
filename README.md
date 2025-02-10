<!-- # Internship Project Plan

## Overview
This project involves processing up to 100 Excel files containing ad campaign reports. The goal is to concatenate these files if they have the same structure, answer user queries related to the data, and handle out-of-context queries appropriately. The project will be deployed using FastAPI and Docker.

## Steps

1. **Upload Files**
    - Allow users to upload up to 100 Excel files containing ad campaign reports.

2. **Concatenate Files**
    - Check if the uploaded files have the same structure.
    - If they do, concatenate them into a single file.
    - If they do not, notify the user about the structural differences.

3. **User Queries**
    - Allow users to submit queries related to the concatenated file.
    - Provide answers to these queries based on the data in the file.

4. **Handle Out-of-Context Queries**
    - Identify and handle queries that are out of context (e.g., "Who is the president of the USA?").
    - Notify the user that the query is out of context.

5. **Graph Generation**
    - Handle queries that request visualizations (e.g., "Give graph of impression vs time").
    - Generate and provide the requested graphs.

6. **Deployment**
    - Use FastAPI to build the API for handling file uploads, queries, and graph generation and Streamlit for Deployment.
    - Create a Docker image for the application to facilitate deployment.

## Technologies
- **FastAPI**: For building the API.
- **Streamlit**: For deploying.
- **Docker**: For containerizing the application.
- **Pandas**: For data manipulation and concatenation.
- **Matplotlib/Seaborn**: For generating graphs.

## Getting Started
1. Clone the repository.
    ```bash
    git clone <repository-url>
    ```
2. Navigate to the project directory.
    ```bash
    cd /d:/Jio-AIDS/Segumento/Project/Main
    ```
3. Build and run the Docker container.
    ```bash
    docker build -t ad-campaign-reports .
    docker run -p 8000:8000 ad-campaign-reports
    ```

## Usage
- Upload Excel files via the provided endpoint.
- Submit queries related to the data.
- Receive answers and visualizations based on the queries.

## Contributing
- Fork the repository.
- Create a new branch for your feature or bug fix.
- Submit a pull request with a detailed description of your changes.

## License
This project is licensed under the MIT License.
  -->



















# Ad Campaign File Query & Visualization System

## **Overview**
This project processes up to 100 ad campaign files, allowing users to:
- Concatenate and validate uploaded files.
- Submit natural language queries for data insights.
- Generate visualizations based on queries.
- Handle irrelevant or out-of-context queries gracefully.

## **Features**
- File uploads with structure validation.
- Natural language query handling (powered by OpenAI).
- Dynamic graph generation.
- Seamless deployment with Docker and Streamlit.

---

## **Technologies**
- **FastAPI**: Backend API.
- **Streamlit**: Frontend interface.
- **LangChain + OpenAI**: Natural language processing.
- **Pandas**: Data handling and manipulation.
- **Matplotlib/Seaborn**: Graph generation.
- **Docker**: Containerization for deployment.

---

## **Setup**

### **1. Clone Repository**
```bash
git clone <repository-url>
cd <project-directory>
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Configure Environment**
```bash
cp .env.example .env
# Edit the .env file to add your OpenAI API key
OPENAI_API_KEY=<your-openai-api-key>
```

### **4. Run Application**
#### **Option 1: Using Streamlit**
```bash
streamlit run streamlit_main.py
```

#### **Option 2: Using Docker**
```bash
docker build -t ad-campaign-reports .
docker run -p 8000:8000 ad-campaign-reports
```

---

## **Usage**

### **Endpoints**
- `/upload`: Upload ad campaign files.
- `/query`: Submit a query related to the concatenated data.

### **Examples**
#### **Uploading Files:**
Using cURL:
```bash
curl -X POST "http://127.0.0.1:8000/upload/" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F "files=@file1.xlsx" \
-F "files=@file2.xlsx"
```

#### **Querying Data:**
```json
POST /query/
{
    "prompt": "What is the total cost of all campaigns in 2023?"
}
```

#### **Visualization:**
```json
POST /query/
{
    "prompt": "Show a line chart of impressions over time."
}
```

---

## **Contributing**
1. Fork the repository and clone your fork.
2. Create a new branch for your feature:
    ```bash
    git checkout -b feature/<feature-name>
    ```
3. Make your changes and commit:
    ```bash
    git add .
    git commit -m "Description of changes"
    ```
4. Push to your fork and create a pull request:
    ```bash
    git push origin feature/<feature-name>
    ```

---

## **License**
Licensed under the MIT License.
