using System.Text;
using System.Text.Json;
using Amazon;
using Amazon.BedrockRuntime;
using Amazon.BedrockRuntime.Model;
using Microsoft.Extensions.Configuration;

// See https://aka.ms/new-console-template for more information
Console.WriteLine("Hello, World!");

var config = new ConfigurationBuilder()
 .SetBasePath(Directory.GetCurrentDirectory())
 .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
 .AddEnvironmentVariables()
 .Build();

string regionName = config["AWS:Region"] ?? "us-east-1";
string modelId = config["Bedrock:NERModelId"] ?? "anthropic.claude-v2";
string text = config["Bedrock:Text"] ?? "Jeff Bezos founded Amazon in Seattle.";

var region = RegionEndpoint.GetBySystemName(regionName);
using var bedrockClient = new AmazonBedrockRuntimeClient(region);

Console.WriteLine("AWS Bedrock Named Entity Recognition Demo\n");

try
{
 Console.WriteLine($"Text: {text}\n");
 var requestBody = JsonSerializer.Serialize(new
 {
 prompt = $"Extract all named entities (people, organizations, locations) from this text: {text}",
 max_tokens_to_sample =100
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
 Console.WriteLine($"NER Result: {result}\n");
}
catch (Exception ex)
{
 Console.WriteLine($"Error: {ex.Message}");
 Console.WriteLine(ex);
}

Console.WriteLine("Demo complete.\n");
