using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using Azure.Storage.Sas;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using OptiStudio.Application.Interface;
using OptiStudio.Infrastructure.Settings;

namespace OptiStudio.Infrastructure.Services;

public class BlobStorageService : IBlobStorageService
{
    private readonly BlobServiceClient _blobServiceClient;
    private readonly ILogger<BlobStorageService> _logger;

    public BlobStorageService(IOptions<AzureBlobSettings> options, ILogger<BlobStorageService> logger)
    {
        _blobServiceClient = new BlobServiceClient(options.Value.ConnectionString);
        _logger = logger;
    }

    public async Task<(string BlobUrl, string StoragePath)> UploadAsync(
        Stream fileStream, string fileName, string contentType, string containerName, string? sessionFolder = null)
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
        await containerClient.CreateIfNotExistsAsync(PublicAccessType.None);

        string storagePath;
        if (!string.IsNullOrEmpty(sessionFolder))
        {
            storagePath = $"{sessionFolder}/uploaded/{fileName}";
        }
        else
        {
            storagePath = $"{Guid.NewGuid()}/{fileName}";
        }

        var blobClient = containerClient.GetBlobClient(storagePath);

        var headers = new BlobHttpHeaders { ContentType = contentType };
        await blobClient.UploadAsync(fileStream, new BlobUploadOptions { HttpHeaders = headers });

        _logger.LogInformation("Uploaded blob {StoragePath} to container {Container}.", storagePath, containerName);
        return (blobClient.Uri.ToString(), storagePath);
    }

    public async Task DeleteAsync(string storagePath, string containerName)
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
        var blobClient = containerClient.GetBlobClient(storagePath);
        await blobClient.DeleteIfExistsAsync();
        _logger.LogInformation("Deleted blob {StoragePath} from container {Container}.", storagePath, containerName);
    }

    public async Task<bool> CheckMalwareScanResultAsync(string storagePath, string containerName)
    {
        // Azure Defender for Storage performs automatic malware scanning.
        // When enabled on the storage account, scan results are stored as blob index tags.
        // Tag key: "Malware Scanning scan result"
        // Tag values: "No threats found" or "Malicious"
        try
        {
            var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
            var blobClient = containerClient.GetBlobClient(storagePath);

            // Poll for scan result with retries (scan may take a few seconds)
            const int maxRetries = 3;
            const int delayMs = 2000;

            for (var i = 0; i < maxRetries; i++)
            {
                await Task.Delay(delayMs);

                try
                {
                    var tagsResponse = await blobClient.GetTagsAsync();
                    var tags = tagsResponse.Value.Tags;

                    if (tags.TryGetValue("Malware Scanning scan result", out var scanResult))
                    {
                        if (scanResult == "Malicious")
                        {
                            _logger.LogWarning("Malware detected in blob {StoragePath}.", storagePath);
                            return false;
                        }
                        return true;
                    }
                }
                catch (Azure.RequestFailedException ex) when (ex.Status == 404)
                {
                    // Tags not yet available, continue polling
                }
            }

            // If Azure Defender is not configured or scan result is unavailable,
            // allow the file (fail-open). Enable Azure Defender for Storage for full protection.
            _logger.LogInformation(
                "Malware scan result not available for {StoragePath}. Ensure Azure Defender for Storage is enabled.",
                storagePath);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error checking malware scan result for {StoragePath}. Allowing upload.", storagePath);
            return true;
        }
    }

    public Task<string> GenerateSasUrlAsync(string storagePath, string containerName, int expiryMinutes = 60)
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
        var blobClient = containerClient.GetBlobClient(storagePath);

        var sasBuilder = new BlobSasBuilder
        {
            BlobContainerName = containerName,
            BlobName = storagePath,
            Resource = "b",
            ExpiresOn = DateTimeOffset.UtcNow.AddMinutes(expiryMinutes)
        };
        sasBuilder.SetPermissions(BlobSasPermissions.Read);

        var sasUri = blobClient.GenerateSasUri(sasBuilder);
        _logger.LogInformation("Generated SAS URL for {StoragePath} valid for {Minutes} minutes.", storagePath, expiryMinutes);
        return Task.FromResult(sasUri.ToString());
    }

    public async Task CopyToApprovedAsync(string storagePath, string sourceContainer, string destContainer)
    {
        var srcContainerClient = _blobServiceClient.GetBlobContainerClient(sourceContainer);
        var dstContainerClient = _blobServiceClient.GetBlobContainerClient(destContainer);
        await dstContainerClient.CreateIfNotExistsAsync(PublicAccessType.None);

        var srcBlob = srcContainerClient.GetBlobClient(storagePath);
        var dstBlob = dstContainerClient.GetBlobClient(storagePath);

        var copyOp = await dstBlob.StartCopyFromUriAsync(srcBlob.Uri);
        await copyOp.WaitForCompletionAsync();

        _logger.LogInformation("Copied blob {StoragePath} from {Source} to {Dest}.", storagePath, sourceContainer, destContainer);
    }

    public static string BuildSessionFolder(string sessionTitle, Guid sessionId)
    {
        var slug = System.Text.RegularExpressions.Regex.Replace(
            (sessionTitle ?? "untitled").ToLowerInvariant().Trim(), @"[^\w\s-]", "");
        slug = System.Text.RegularExpressions.Regex.Replace(slug, @"[\s_]+", "-");
        slug = System.Text.RegularExpressions.Regex.Replace(slug, @"-+", "-").Trim('-');
        if (slug.Length > 80) slug = slug[..80];
        if (string.IsNullOrEmpty(slug)) slug = "untitled";
        return $"{slug}_{sessionId.ToString()[..8]}";
    }
}
