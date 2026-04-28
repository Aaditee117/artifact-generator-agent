using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using OptiStudio.Domain.Entity;

namespace OptiStudio.Persistence.Configurations;

public class ApiRequestLogConfiguration : IEntityTypeConfiguration<ApiRequestLog>
{
    public void Configure(EntityTypeBuilder<ApiRequestLog> builder)
    {
        builder.HasKey(a => a.Id);
        
        builder.Property(a => a.Endpoint)
            .IsRequired()
            .HasMaxLength(500);
            
        builder.Property(a => a.HttpMethod)
            .IsRequired()
            .HasMaxLength(10);
            
        builder.Property(a => a.UserAgent)
            .HasMaxLength(500);
            
        builder.Property(a => a.IpAddress)
            .HasMaxLength(50);
            
        builder.Property(a => a.ErrorMessage)
            .HasMaxLength(2000);

        builder.HasOne(a => a.User)
            .WithMany()
            .HasForeignKey(a => a.UserId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(a => a.Endpoint);
        builder.HasIndex(a => a.CreatedAt);
        builder.HasIndex(a => a.StatusCode);
        builder.HasIndex(a => a.UserId);
    }
}
