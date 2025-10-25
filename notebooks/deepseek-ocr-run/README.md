# [DeepSeek-OCR](https://medium.com/@harishpillai1994/how-to-run-deepseek-ocr-545b8da322ac)

DeepSeek-OCR automates the conversion of PDFs to structured Markdown using deep learning. To run the code within Google Colab follow these steps:

## How It Works

### 1. Environment and GPU Setup

First, the notebook configures Colab to use GPU acceleration, ensuring fast and efficient OCR processing. It upgrades core dependencies, installs PyTorch (CUDA 11.8), essential libraries like Transformers, and utilities for handling PDFs and images.

### 2. Uploading Your PDF

A simple interface lets you upload a single PDF file for processing. The notebook checks to ensure only one file is selected and then confirms the filename for your reference.

### 3. Converting PDF Pages to Images

The notebook converts each page of your uploaded PDF into a high-quality PNG image. All images are saved in a dedicated output folder, ready for the OCR model.

### 4. Loading and Preparing DeepSeek-OCR

It loads the DeepSeek-OCR model using Transformers, preparing it to run on GPU with optimal settings. The model is configured for efficient attention processing and smart tokenization.

### 5. Extracting Markdown from Images

Every PDF page image is passed through the DeepSeek-OCR model. The model reads each page and generates clean, concise Markdown text. This conversion supports tables, lists, and more, keeping the document’s structure intact.

### 6. Cleaning and Organizing the Output

Detection artifacts, tags, and duplicate lines are removed from the output to ensure clarity. Each page's Markdown is stored individually, and all content is also merged into a single combined Markdown file for easy viewing.

### 7. Runtime and Statistics

As each page is processed, the workflow logs runtime statistics and details for transparency. All timing data are saved for review.

### 8. Downloading Your Results

When processing is complete, you can download all results—including images, individual Markdown files, the combined Markdown file, and timing statistics—bundled in a convenient ZIP archive.

## Output Structure

- Each page as a PNG image.
- Individual Markdown files for every page.
- A combined Markdown file for the whole document.
- A CSV file with runtime statistics.
- All files zipped for easy access.


## Usage Tips

- For best OCR accuracy, ensure PDFs are clear and use the recommended DPI setting.
- Tables and data-rich content are formatted as Markdown tables.
- If any advanced GPU features are unavailable, the workflow automatically switches to fallback modes.


