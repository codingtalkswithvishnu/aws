using System.Text;
using System.Text.Json;
using Amazon;
using Amazon.BedrockRuntime;
using Amazon.BedrockRuntime.Model;
using Microsoft.Extensions.Configuration;

var config = new ConfigurationBuilder()
 .SetBasePath(Directory.GetCurrentDirectory())
 .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
 .AddEnvironmentVariables()
 .Build();

string regionName = config["AWS:Region"] ?? "us-east-1";
string modelId = config["Bedrock:SentimentModelId"] ?? "anthropic.claude-v2";
string text = config["Bedrock:Text"] ?? "I love using AWS Bedrock!";

var region = RegionEndpoint.GetBySystemName(regionName);
using var bedrockClient = new AmazonBedrockRuntimeClient(region);

Console.WriteLine("AWS Bedrock Sentiment Analysis Demo\n");

try
{
 Console.WriteLine($"Text: {text}\n");
 var requestBody = JsonSerializer.Serialize(new
 {
 prompt = $"Classify the sentiment of this text as Positive, Negative, or Neutral: {text}",
 max_tokens_to_sample =20
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
 Console.WriteLine($"Sentiment Result: {result}\n");
}
catch (Exception ex)
{
 Console.WriteLine($"Error: {ex.Message}");
 Console.WriteLine(ex);
}

Console.WriteLine("Demo complete.\n");
