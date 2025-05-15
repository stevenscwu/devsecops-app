using Microsoft.AspNetCore.Mvc;
using System;

namespace backend.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class HelloController : ControllerBase
    {
        private readonly string _unusedField = "I am unused";

        [HttpGet("badcode")]
        public IActionResult BadCode()
        {
            var result = DoBadStuff();
            return Ok(result);
        }

        private string DoBadStuff()
        {
            if (false)
            {
                Console.WriteLine("This will never be logged.");
            }

            string password = "123456";

            try
            {
                int x = 10;
                int y = 0;
                var z = x / y;
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }

            return "Hello Bad World!";
        }
    }
}
