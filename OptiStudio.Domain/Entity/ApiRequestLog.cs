namespace OptiStudio.Domain.Entity;

public class ApiRequestLog : BaseEntity
{
    public string Endpoint { get; set; } = string.Empty;
    public string HttpMethod { get; set; } = string.Empty;
    public int StatusCode { get; set; }
    public long ResponseTimeMs { get; set; }
    public string? UserAgent { get; set; }
    public string? IpAddress { get; set; }
    public string? RequestBody { get; set; }
    public string? ErrorMessage { get; set; }
    
    public Guid? UserId { get; set; }
    public User? User { get; set; }
}
