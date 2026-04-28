using OptiStudio.Domain.Enum;

namespace OptiStudio.Application.Models;

public class FileUploadData
{
    public string FileName { get; set; } = string.Empty;
    public string ContentType { get; set; } = string.Empty;
    public long Length { get; set; }
    public Stream Stream { get; set; } = null!;
    public ArtifactCategory Category { get; set; }
}
