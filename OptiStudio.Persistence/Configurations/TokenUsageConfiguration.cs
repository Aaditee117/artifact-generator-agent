using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using OptiStudio.Domain.Entity;

namespace OptiStudio.Persistence.Configurations;

public class TokenUsageConfiguration : IEntityTypeConfiguration<TokenUsage>
{
    public void Configure(EntityTypeBuilder<TokenUsage> builder)
    {
        builder.HasKey(t => t.Id);

        builder.Property(t => t.Feature)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(t => t.Action)
            .HasMaxLength(100);

        builder.Property(t => t.ModelUsed)
            .HasMaxLength(100);

        builder.Property(t => t.EstimatedCost)
            .HasPrecision(18, 6);

        builder.Property(t => t.ErrorMessage)
            .HasMaxLength(2000);

        builder.HasOne(t => t.User)
            .WithMany(u => u.TokenUsages)
            .HasForeignKey(t => t.UserId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasOne(t => t.ChatSession)
            .WithMany()
            .HasForeignKey(t => t.ChatSessionId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(t => t.Feature);
        builder.HasIndex(t => t.CreatedAt);
        builder.HasIndex(t => t.UserId);
    }
}
