using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using OptiStudio.Domain.Entity;
using OptiStudio.Domain.Enum;

namespace OptiStudio.Persistence.Configurations;

public class ArtifactConfiguration : IEntityTypeConfiguration<Artifact>
{
    public void Configure(EntityTypeBuilder<Artifact> builder)
    {
        builder.ToTable("Artifacts");
        builder.HasKey(a => a.Id);

        builder.Property(a => a.FileName)
            .HasMaxLength(500);

        builder.Property(a => a.FileType)
            .HasMaxLength(20);

        builder.Property(a => a.Category)
            .HasConversion<string>()
            .IsRequired()
            .HasMaxLength(30);

        builder.Property(a => a.BlobUrl)
            .HasMaxLength(2000);

        builder.Property(a => a.StoragePath)
            .HasMaxLength(1000);

        builder.Property(a => a.Version)
            .HasDefaultValue(1);

        builder.HasOne(a => a.ChatMessage)
            .WithMany(m => m.Artifacts)
            .HasForeignKey(a => a.ChatMessageId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(a => a.UploadedByUser)
            .WithMany(u => u.UploadedArtifacts)
            .HasForeignKey(a => a.UploadedByUserId)
            .OnDelete(DeleteBehavior.Restrict);
    }
}
