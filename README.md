# AWS Bedrock .NET9 Sample Apps

**AWS Bedrock** is a fully managed service from Amazon Web Services that provides access to a wide range of foundation models (FMs) for generative AI tasks such as text generation, image creation, code generation, and more. Bedrock enables developers to easily integrate state-of-the-art AI capabilities into their applications using a unified API, with built-in security, scalability, and cost controls.

This repository contains multiple .NET9 console applications demonstrating how to use AWS Bedrock Runtime for various AI and ML tasks. Each project is self-contained and showcases a specific Bedrock capability.

## Author

**Vishnu VG** 
- [LinkedIn](https://www.linkedin.com/in/vishnuvgtvm/) 
- [Spotify Podcast](https://open.spotify.com/show/1OxmL5CmtnvfAhu7GJfq4O)
- [YouTube Channel](https://www.youtube.com/@codingtalkswithvishnu)

## Projects Overview

| Project Name | Description |
|--------------|-------------|
| **AwsBedrock.ImageGenerationApp** | Generates images from text prompts using Bedrock image models. |
| **AwsBedrock.TextGenerationApp** | Generates text completions or creative writing from prompts. |
| **AwsBedrock.ChatbotApp** | Demonstrates conversational AI/chatbot using Bedrock. |
| **AwsBedrock.SentimentAnalysisApp** | Analyzes sentiment of input text. |
| **AwsBedrock.TextTranslationApp** | Translates text between languages. |
| **AwsBedrock.TextClassificationApp** | Classifies text into categories. |
| **AwsBedrock.QuestionAnsweringApp** | Answers questions based on provided context. |
| **AwsBedrock.NamedEntityRecognitionApp** | Extracts named entities (people, places, etc.) from text. |
| **AwsBedrock.ImageCaptioningApp** | Generates captions for images. |
| **AwsBedrock.VisualQuestionAnsweringApp** | Answers questions about the content of images. |
| **AwsBedrock.DocumentUnderstandingApp** | Extracts structured information from documents. |
| **AwsBedrock.CodeGenerationApp** | Generates code from natural language prompts. |
| **AwsBedrock.TextSummarizationApp** | Summarizes long text into concise summaries. |

## Getting Started

1. **Clone the repository**
2. **Restore NuGet packages**: `dotnet restore`
3. **Configure AWS credentials** and update `appsettings.json` in each project as needed.
4. **Build and run** any project:
 ```sh
 dotnet run --project AwsBedrock.ImageGenerationApp
 ```

## Prerequisites
- .NET9 SDK
- AWS credentials with Bedrock access

## Notes
- Each project has its own `appsettings.json` for configuration.
- All dependencies are managed via NuGet and will auto-restore on build.

---

For more details, see the source code in each project folder.
