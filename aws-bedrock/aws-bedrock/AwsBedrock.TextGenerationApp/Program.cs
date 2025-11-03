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

// Read settings from configuration
string regionName = config["AWS:Region"] ?? "us-east-1";
string modelId = config["Bedrock:TextModelId"] ?? "anthropic.claude-v2";
string prompt = config["Bedrock:Prompt"] ?? "Write a short story about a robot learning to paint.";

var region = RegionEndpoint.GetBySystemName(regionName);
using var bedrockClient = new AmazonBedrockRuntimeClient(region);

Console.WriteLine("AWS Bedrock Text Generation Demo\n");

try
{
 Console.WriteLine($"Prompt: {prompt}\n");
 var requestBody = JsonSerializer.Serialize(new
 {
 prompt = prompt,
 max_tokens_to_sample =200
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
 Console.WriteLine($"Text Generation Result: {result}\n");
}
catch (Exception ex)
{
 Console.WriteLine($"Error: {ex.Message}");
 Console.WriteLine(ex);
}

Console.WriteLine("Demo complete.\n");
