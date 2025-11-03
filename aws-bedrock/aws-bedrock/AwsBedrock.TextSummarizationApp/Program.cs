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
string modelId = config["Bedrock:TextModelId"] ?? "anthropic.claude-v2";
string textToSummarize = config["Bedrock:TextToSummarize"] ?? "Amazon Bedrock is a fully managed service that makes foundation models from leading AI companies accessible via an API, so you can build and scale generative AI applications easily.";

var region = RegionEndpoint.GetBySystemName(regionName);
using var bedrockClient = new AmazonBedrockRuntimeClient(region);

Console.WriteLine("AWS Bedrock Text Summarization Demo\n");

try
{
 Console.WriteLine($"Original Text: {textToSummarize}\n");
 var requestBody = JsonSerializer.Serialize(new
 {
 prompt = $"Summarize this: {textToSummarize}",
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
 Console.WriteLine($"Summary Result: {result}\n");
}
catch (Exception ex)
{
 Console.WriteLine($"Error: {ex.Message}");
 Console.WriteLine(ex);
}

Console.WriteLine("Demo complete.\n");
