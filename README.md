# AI Data Analysis with RAPIDS
This project is an interactive data analysis application that leverages AI capabilities and GPU-accelerated computing to provide insightful analyses and visualizations of uploaded datasets. It combines a user-friendly interface with a backend that makes use of the NVIDIA RAPIDS libraries and algorithms to automate data processing and analysis while also using a data API with caching to greatly increase the speed of results.
This project was inspired by another I created, but contains all new, custom code and features like LLM integration, custom PDF and PPTX reports, cuDF and cuML powered visualizations, and more.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Restrictions and Limitations](#restrictions-and-limitations)
- [How to Install and Run the Project](#how-to-install-and-run-the-project)
- [How to Use the Project](#how-to-use-the-project)
- [System Architecture](#system-architecture)
- [Report Generation Process](#report-generation)
- [Component Interaction](#component-interaction)
- [Data Flow](#data-flow)
  
### Prerequisites

- NVIDIA GPU with CUDA support
- API key for LLM Provider of your choice (HuggingFace, NVIDIA, or Google Gemini)
> If on Windows, WSL2.  See this page for information: [Windows Subsystem for Linux Documentation | Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/install)

### Restrictions and Limitations
-	LLM Models: The project is designed to work with specific LLM providers (HuggingFace, NVIDIA, Google Gemini). Speed of report and presentation generation will vary depending upon the provider and model chosen.
-	File Size: While cuDF allows for processing of larger datasets, there may still be limitations based on available GPU memory.

### How to Install and Run the Project
1.	Install NVIDIA AI Workbench by following the instructions for your operating system:  [Install AI Workbench - NVIDIA Docs](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/overview.html)
2.	Open NVIDIA AI Workbench and under My Locations, select Local
3.	The My Projects Page will load. Click Clone Project on the right.  A pop-up will appear to enter the project data.  Enter the following:
a.	Repository URL: https://github.com/msamylea/nvidia-alm
b.	Path: /home/workbench/nvidia-workbench/nvidia-alm
4.	Click the Clone button.

 ![image](https://github.com/user-attachments/assets/7ccba2c0-fcf5-4040-a36e-993fd51771e4)


5.	File Browser section will load:

 ![image](https://github.com/user-attachments/assets/fd673b4e-b7d3-4bdf-9d83-6a2bc2f00e44)


6.	Click Environment on the left side:

 ![image](https://github.com/user-attachments/assets/5facfda1-5675-4c49-9459-9c82d9592f01)


7.	It should now say “BUILDING PLEASE WAIT” beside Environment on the main section:

![image](https://github.com/user-attachments/assets/487c65b0-f84d-4579-b304-8056e9154e54)


8.	Wait for build to complete and change to “Ready”:

![image](https://github.com/user-attachments/assets/d1db17bb-6b04-4173-aeb3-223c90dc1e7f)


9.	Click Start Environment on the right side of the main section of the Environment tab:

![image](https://github.com/user-attachments/assets/9bd624ea-16aa-4e39-b4d1-7a574ee35085)


10.	Scroll down the page to the Applications section and toggle dash-app from stopped to running:

![image](https://github.com/user-attachments/assets/4f12fc51-d7bb-4535-a965-2c2cd6f30c3c)


11.	A webpage should automatically open to localhost:1000/projects/nvidia-alm/applications/dash-app/

![image](https://github.com/user-attachments/assets/1f098796-7e93-4ca1-a9f2-b551d8bf4247)


### How to Use the Project

#### Click on the Configure LLM button in the Step 1 Box, and a pop-up will appear to configure the LLM provider and model:

 ![image](https://github.com/user-attachments/assets/914f691f-f5c1-4628-a16c-f2beb5736476)


1.	From the top dropdown menu, select a provider from either HuggingFace, NVIDIA, or Google Gemini.
2.	Next, enter your selected model in the Model Name section.  The format for provider model names is as follows:
    - HuggingFace: uses format ‘creator/modelname’.  Example: nvidia/Llama-3.1-Nemotron-70B-Instruct-HF.  You can find a list of available models here: [HuggingFace Models](https://huggingface.co/models)
    - NVIDIA: uses format ‘creator/modelname’. Example: nvidia/llama-3.1-nemotron-70b-instruct. You can find available models here: [Try NVIDIA NIM APIs](https://build.nvidia.com/nim)
    - Google Gemini: options include - gemini-1.5-flash, gemini-1.5-flash-8b, gemini-1.5-pro.  Models can be found here: [Gemini models  |  Gemini API  |  Google AI for Developers](https://ai.google.dev/gemini-api/docs/models/gemini)
3.	Enter your API key for the selected provider.
4.	Select a temperature from the slider (lower temperature recommended).
5.	Enter the max tokens for your chosen model.
6.	Click Submit

You should now see that the Provider and selected model display in the main bar at the top of the page:

  ![image](https://github.com/user-attachments/assets/eba3dba7-f587-41df-a9a5-323f32e54bcd)


#### The next step is Step 2, Upload Dataset.  
1.	Click the Upload Dataset button.
2.	Select a dataset from your local computer and click Open.
3.	If the file upload was successful, the top bar will display the dataset as Data Uploaded
  
![image](https://github.com/user-attachments/assets/074fa8d2-74f2-448e-8647-86d9f8ebb9fa)

#### For Step 3, enter the analysis target or questions you have about your data in the Step 3 section.
1.	Enter your query / analysis target
2.	Click Generate Report

A pop-up appears to customize your end report:

![image](https://github.com/user-attachments/assets/bcab2bc4-3eaf-4f3b-802e-49c3f47d6371)

 
You may do any of the following on the left side (Suggested Report Title and Sections):
-	Change the Report Title
-	Uncheck sections to include
-	Add a new section under “Optional: Add new section”

You may do any of the following on the right side (Optional: Report Styling):
-	Enter a company name
-	Upload a company logo
-	Select a primary and secondary color for the report

Once you have made your choices, click Generate Report at the bottom of the pop-up.

You will now see a bar-chart animation as the LLM processes your request against the dataset and prepares the final report.

When the processing is completed, you can scroll down and see the full PDF report.  To save it, click the disk icon on the bar:

  ![image](https://github.com/user-attachments/assets/a9393411-9cbc-42d0-8753-1ab92dad566a)


#### If you want to create a PowerPoint presentation, you can proceed to Step 4 by clicking ‘Generate Presentation’ in the Step 4 box.

A pop-up will appear allowing you to select the theme for your presentation:
  
![image](https://github.com/user-attachments/assets/8fa58422-a374-425b-997b-98ca53decae0)

Select from the dropdown menu at the top, and then click Submit.

After the presentation is prepared, you will get a prompt from your browser to download the presentation.  You can click Open or Save As and proceed to view the final presentation:
 
![image](https://github.com/user-attachments/assets/b3f0d483-70a0-4f09-85d7-2a523bace1ef)

#### Finally, if you would like to continue or have questions beyond your initial query, you can click the Chat tab beside the Home tab at the top of the page:

![image](https://github.com/user-attachments/assets/c0c04c9c-5cd5-47d9-9192-941f2f7342f2)


Enter your query and click Send:

![image](https://github.com/user-attachments/assets/61b73ee9-555c-4d85-b1b0-069caf7253c0)
  

You can now continue chatting with the LLM about your data:
 
![image](https://github.com/user-attachments/assets/eaece3b2-c1c0-4ee1-a85f-b2a276c3dd6e)


## System Architecture

![main-flow](https://github.com/user-attachments/assets/d1b3503d-22cc-4534-a233-edf63eabecf1)

 
## Report Generation

![report-generation](https://github.com/user-attachments/assets/f98bdc6f-4f75-4df5-b1ce-b16fc48205b3)

 
## Component Interaction

![component-interaction](https://github.com/user-attachments/assets/a9a3c9d3-90c1-49fc-b098-d8fa2360ec27)

## Data Flow

![data-flow](https://github.com/user-attachments/assets/3004f960-edfb-44e8-9e4f-bbcca6b73733)





