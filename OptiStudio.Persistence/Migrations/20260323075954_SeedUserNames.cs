using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace OptiStudio.Persistence.Migrations
{
    /// <inheritdoc />
    public partial class SeedUserNames : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("UPDATE Users SET Name = 'Aditee Agrawal' WHERE Email = 'aadiagrawal69@gmail.com'");
            migrationBuilder.Sql("UPDATE Users SET Name = 'admin' WHERE Email = 'admin@optistudio.com'");
            migrationBuilder.Sql("UPDATE Users SET Name = 'Aaditee Agrawal' WHERE Email = 'aaditee.agrawal@optimusinfo.com'");
            migrationBuilder.Sql("UPDATE Users SET Name = 'Rishi Jha' WHERE Email = 'rishi.jha@optimusinfo.com'");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("UPDATE Users SET Name = '' WHERE Email IN ('aadiagrawal69@gmail.com', 'admin@optistudio.com', 'aaditee.agrawal@optimusinfo.com', 'rishi.jha@optimusinfo.com')");
        }
    }
}
