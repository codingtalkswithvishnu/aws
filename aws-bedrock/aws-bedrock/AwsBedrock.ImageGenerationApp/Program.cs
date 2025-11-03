using System.Text;
using System.Text.Json;
using Amazon;
using Amazon.BedrockRuntime;
using Amazon.BedrockRuntime.Model;
using Microsoft.Extensions.Configuration;
using System.Diagnostics;

// Build configuration
var config = new ConfigurationBuilder()
 .SetBasePath(Directory.GetCurrentDirectory())
 .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
 .AddEnvironmentVariables()
 .Build();

string regionName = config["AWS:Region"] ?? "us-east-1";
string imageModelId = config["Bedrock:ImageModelId"] ?? "stability.stable-diffusion-xl-v0";
string imagePrompt = config["Bedrock:Prompt"] ?? "A futuristic city skyline at sunset, digital art.";

var region = RegionEndpoint.GetBySystemName(regionName);
using var bedrockClient = new AmazonBedrockRuntimeClient(region);

Console.WriteLine("AWS Bedrock Image Generation Demo\n");

try
{
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
 Console.WriteLine($"Raw Image Generation Result: {imageResult}\n");

 // Try to extract base64 image from JSON response
 string? base64Image = null;
 try
 {
 using var doc = JsonDocument.Parse(imageResult);
 if (doc.RootElement.TryGetProperty("artifacts", out var artifacts) &&
 artifacts.ValueKind == JsonValueKind.Array &&
 artifacts.GetArrayLength() >0)
 {
 var artifact = artifacts[0];
 if (artifact.TryGetProperty("base64", out var base64Prop))
 {
 base64Image = base64Prop.GetString();
 }
 }
 // Some models may return "image" or other keys
 if (string.IsNullOrEmpty(base64Image) && doc.RootElement.TryGetProperty("image", out var imageProp))
 {
 base64Image = imageProp.GetString();
 }
 }
 catch (Exception jsonEx)
 {
 Console.WriteLine($"Could not parse image JSON: {jsonEx.Message}");
 }

 if (!string.IsNullOrEmpty(base64Image))
 {
 var imageBytes = Convert.FromBase64String(base64Image);
 var fileName = $"generated-image-{DateTime.Now:yyyyMMddHHmmss}.png";
 await File.WriteAllBytesAsync(fileName, imageBytes);
 Console.WriteLine($"Image saved to: {fileName}");

 // Try to open the image in the default viewer
 try
 {
 var psi = new ProcessStartInfo
 {
 FileName = fileName,
 UseShellExecute = true
 };
 Process.Start(psi);
 }
 catch (Exception openEx)
 {
 Console.WriteLine($"Could not open image automatically: {openEx.Message}");
 }
 }
 else
 {
 Console.WriteLine("No base64 image found in response.");
 }
}
catch (Exception ex)
{
 Console.WriteLine($"Error: {ex.Message}");
 Console.WriteLine(ex);
}

Console.WriteLine("Demo complete.\n");
