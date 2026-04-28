namespace OptiStudio.Application.Interface;

public interface IPasswordHasher
{
    string Hash(string password);
    bool Verify(string password, string hash);
}
