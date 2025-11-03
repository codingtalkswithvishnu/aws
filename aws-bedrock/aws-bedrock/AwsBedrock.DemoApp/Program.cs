using System.Text;
using Amazon;
using Amazon.BedrockRuntime;
using Amazon.BedrockRuntime.Model;
using Microsoft.Extensions.Configuration;

// Build configuration
var config = new ConfigurationBuilder()
 .SetBasePath(Directory.GetCurrentDirectory())
 .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
 .AddEnvironmentVariables()
 .Build();

// Read settings from configuration
string regionName = config["AWS:Region"] ?? "us-east-1";
string textModelId = config["Bedrock:TextModelId"] ?? "anthropic.claude-v2";
string imageModelId = config["Bedrock:ImageModelId"] ?? "stability.stable-diffusion-xl-v0";

var region = RegionEndpoint.GetBySystemName(regionName);
using var bedrockClient = new AmazonBedrockRuntimeClient(region);

Console.WriteLine("AWS Bedrock Demo: Text Summarization and Image Generation\n");

try
{
 // --- TEXT SUMMARIZATION DEMO ---
 string textToSummarize = "Amazon Bedrock is a fully managed service that makes foundation models from leading AI companies accessible via an API, so you can build and scale generative AI applications easily.";
 Console.WriteLine($"Original Text: {textToSummarize}\n");

 var summarizeRequest = new InvokeModelRequest
 {
 ModelId = textModelId,
 ContentType = "application/json",
 Accept = "application/json",
 Body = new MemoryStream(Encoding.UTF8.GetBytes($"{{\"prompt\":\"Summarize this: {textToSummarize}\",\"max_tokens_to_sample\":100}}"))
 };
 var summarizeResponse = await bedrockClient.InvokeModelAsync(summarizeRequest);
 using var reader = new StreamReader(summarizeResponse.Body);
 string summaryResult = await reader.ReadToEndAsync();
 Console.WriteLine($"Summary Result: {summaryResult}\n");

 // --- IMAGE GENERATION DEMO ---
 string imagePrompt = "A futuristic city skyline at sunset, digital art.";
 Console.WriteLine($"Image Generation Prompt: {imagePrompt}\n");

 var imageRequest = new InvokeModelRequest
 {
 ModelId = imageModelId,
 ContentType = "application/json",
 Accept = "application/json",
 Body = new MemoryStream(Encoding.UTF8.GetBytes($"{{\"prompt\":\"{imagePrompt}\"}}"))
 };
 var imageResponse = await bedrockClient.InvokeModelAsync(imageRequest);
 using var imageReader = new StreamReader(imageResponse.Body);
 string imageResult = await imageReader.ReadToEndAsync();
 Console.WriteLine($"Image Generation Result: {imageResult}\n");
}
catch (Exception ex)
{
 Console.WriteLine($"Error: {ex.Message}");
 Console.WriteLine(ex);
}

Console.WriteLine("Demo complete.\n");
