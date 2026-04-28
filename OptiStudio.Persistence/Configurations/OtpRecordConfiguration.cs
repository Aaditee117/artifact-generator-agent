using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using OptiStudio.Domain.Entity;

namespace OptiStudio.Persistence.Configurations;

public class OtpRecordConfiguration : IEntityTypeConfiguration<OtpRecord>
{
    public void Configure(EntityTypeBuilder<OtpRecord> builder)
    {
        builder.ToTable("OtpRecords");
        builder.HasKey(o => o.Id);

        builder.Property(o => o.Code)
            .IsRequired()
            .HasMaxLength(4);

        builder.Property(o => o.ExpiresAt)
            .IsRequired();

        builder.Property(o => o.IsUsed)
            .HasDefaultValue(false);
    }
}
