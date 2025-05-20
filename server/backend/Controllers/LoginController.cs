using Microsoft.AspNetCore.Mvc;
using System.Data.SqlClient;
using MyApp.Models; // ✅ import your model

namespace MyApp.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class LoginController : ControllerBase
    {
        [HttpPost]
        public IActionResult Login([FromBody] LoginModel model)
        {
            string username = model.Username;
            string password = model.Password;

            string query = $"SELECT * FROM Users WHERE Username = '{username}' AND Password = '{password}'";

            using (SqlConnection conn = new SqlConnection("YourConnectionString"))
            {
                conn.Open();
                SqlCommand cmd = new SqlCommand(query, conn);
                var reader = cmd.ExecuteReader();
                if (reader.HasRows)
                {
                    return Ok("Login successful");
                }
            }
            return Unauthorized();
        }
    }
}
