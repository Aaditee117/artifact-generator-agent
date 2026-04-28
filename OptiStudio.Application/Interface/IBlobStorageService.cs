namespace OptiStudio.Application.Interface;

public interface IBlobStorageService
{
    Task<(string BlobUrl, string StoragePath)> UploadAsync(Stream fileStream, string fileName, string contentType, string containerName, string? sessionFolder = null);
    Task DeleteAsync(string storagePath, string containerName);
    Task<bool> CheckMalwareScanResultAsync(string storagePath, string containerName);
    Task<string> GenerateSasUrlAsync(string storagePath, string containerName, int expiryMinutes = 60);
    Task CopyToApprovedAsync(string storagePath, string sourceContainer, string destContainer);
}
