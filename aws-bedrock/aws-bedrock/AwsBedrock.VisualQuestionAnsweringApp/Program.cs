using System.Text;
using System.Text.Json;
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

string regionName = config["AWS:Region"] ?? "us-east-1";
string modelId = config["Bedrock:VQAModelId"] ?? "anthropic.claude-v2";
string imagePath = config["Bedrock:ImagePath"] ?? "input.jpg";
string question = config["Bedrock:Question"] ?? "What is in the image?";

var region = RegionEndpoint.GetBySystemName(regionName);
using var bedrockClient = new AmazonBedrockRuntimeClient(region);

Console.WriteLine("AWS Bedrock Visual Question Answering Demo\n");

try
{
 if (!File.Exists(imagePath))
 {
 Console.WriteLine($"Image file not found: {imagePath}");
 return;
 }
 var imageBytes = await File.ReadAllBytesAsync(imagePath);
 var base64Image = Convert.ToBase64String(imageBytes);

 var requestBody = JsonSerializer.Serialize(new
 {
 image = base64Image,
 question = question
 });

 var request = new InvokeModelRequest
 {
 ModelId = modelId,
 ContentType = "application/json",
 Accept = "application/json",
 Body = new MemoryStream(Encoding.UTF8.GetBytes(requestBody))
 };
 var response = await bedrockClient.InvokeModelAsync(request);
 using var reader = new StreamReader(response.Body);
 string result = await reader.ReadToEndAsync();
 Console.WriteLine($"VQA Result: {result}\n");
 }
catch (Exception ex)
{
 Console.WriteLine($"Error: {ex.Message}");
 Console.WriteLine(ex);
 }

Console.WriteLine("Demo complete.\n");
