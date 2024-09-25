# AI Data Analysis Project

This project is an interactive data analysis application that leverages AI capabilities and GPU-accelerated computing to provide insightful analyses and visualizations of uploaded datasets. It combines a user-friendly interface with a backend that makes use of the NVIDIA RAPIDS libraries and algorithms to automate data processing and analysis while also using a data API with caching to greatly increase the speed of results.

## Features and Functionality

1. **LLM Integration**: Configure and connect to various Language Learning Models (LLMs) for AI-powered analysis.
2. **Data Upload**: Upload and process various file formats including CSV, Parquet, and JSON.
3. **Interactive Analysis**: Generate custom reports and visualizations based on user queries.
4. **Chat Interface**: Engage in conversational data analysis with an AI assistant.
5. **PDF Report Generation**: Create detailed PDF reports with customizable styling options.
6. **PowerPoint Presentation**: Automatically generate PowerPoint presentations based on the analysis.
7. **Dynamic Visualizations**: Create and display various types of plots and charts.
8. **GPU-Accelerated Data Processing**: Utilize NVIDIA RAPIDS (cuDF and cuML) for high-speed data manipulation and machine learning.

## GPU-Accelerated Data Processing with cuDF and cuML

This project leverages NVIDIA's RAPIDS suite, specifically cuDF and cuML, to perform GPU-accelerated data processing and machine learning tasks:

- **cuDF**: A GPU DataFrame library that provides a pandas-like API for processing and analyzing large datasets on NVIDIA GPUs. In this project, cuDF is used for:
  - Fast data loading and preprocessing
  - Efficient handling of large datasets
  - Quick data transformations and aggregations

- **cuML**: A suite of GPU-accelerated machine learning algorithms that provides scikit-learn-like APIs. In this project, cuML is used for:
  - Accelerated linear regression modeling for on the fly plot generation
  - Fast train-test splits for model evaluation
  - Potential for other machine learning tasks (clustering, dimensionality reduction, etc.)

The use of these GPU-accelerated libraries significantly enhances the performance of data processing and analysis tasks, especially for large datasets.

## Running the Project in AI Workbench

### Prerequisites

- NVIDIA GPU with CUDA support
- [NVIDIA AI Workbench installed](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/overview.html)

### Setup and Run Instructions

1. Open NVIDIA AI Workbench and select your location.

2. Select Clone Project and use this GitHub repository.

3. To set up and run automatically if `dash-app` is not already in the workspace:
   - Under Environment, select `Add -> Custom Application`
   - Enter the following, then rebuild and toggle to run automatically:
     - **Name**: `dash-app`
     - **Class**: `Web Application`
     - **Start Command**: `cd /project/code && PROXY_PREFIX=$PROXY_PREFIX python3 run_app.py`
     - **Health Check Command**: `curl -f "http://localhost:10000/projects/nvidia-alm/applications/dash-app/"`
     - **Stop Command**: `pkill -f '^python3 run_app.py'`
     - **Auto Launch**: `True`
     - **Port**: `10000`
     - **URL**: `http://localhost:10000/projects/nvidia-alm/applications/dash-app/`

4. If you don't want to add the custom application, open the project through Visual Studio Code in NVIDIA AI Workbench, then run `run_app.py`.
## System Requirements

- **GPU**: NVIDIA GPU with CUDA support (minimum 8GB VRAM recommended)
- **CUDA**: Compatible CUDA version (refer to RAPIDS documentation for specific version requirements)
- **RAM**: Minimum 16GB, 32GB or more recommended for large datasets
- **Storage**: At least 20GB of free space
- **OS**: Linux-based system (Ubuntu 20.04 or later recommended)

## Restrictions and Limitations

- **LLM Models**: The project is designed to work with specific LLM providers (HuggingFace, NVIDIA, Google Gemini). Other providers may not be compatible. Speed of report and presentation generation will vary depending upon the provider and model chosen.
- **File Size**: While cuDF allows for processing of larger datasets compared to pandas, there may still be limitations based on available GPU memory.
- **API Keys**: Users need to provide their own API keys for the LLM services.
- **GPU Compatibility**: The project requires an NVIDIA GPU compatible with RAPIDS libraries.

## Additional Notes

- The application uses a combination of Dash, FastAPI, and various data processing libraries.
- The project includes a caching mechanism to improve performance for repeated analyses.
- Custom CSS and styling are applied to enhance the user interface.
- The use of cuDF and cuML provides significant performance benefits, especially for large-scale data processing and machine learning tasks.

