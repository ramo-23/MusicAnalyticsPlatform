using api.DTOs;
using Dapper;
using DuckDB.NET.Data;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace api.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class AnalyticsController : ControllerBase
    {
        private readonly string _connectionString;

        public AnalyticsController(IConfiguration configuration)
        {
            _connectionString = configuration.GetConnectionString("DuckDbConnection") 
                                ?? throw new InvalidOperationException("DuckDB connection string is missing.");
        }

        [HttpGet("top-tracks")]
        public async Task<ActionResult<IEnumerable<TrackMetricDto>>> GetTopTracks()
        {
            using var connection = new DuckDBConnection(_connectionString);
            connection.Open();

            var sql = @"
                SELECT 
                    f.Chart_Rank AS ChartRank, 
                    t.Title, 
                    a.Name AS ArtistName, 
                    f.Platform 
                FROM Fact_Metrics f
                JOIN Dim_Track t ON f.Track_ID = t.Track_ID
                JOIN Dim_Artist a ON t.Artist_ID = a.Artist_ID
                ORDER BY f.Chart_Rank ASC
                LIMIT 200;
            ";

            // Map SQL aliases to DTO properties
            var tracks = await connection.QueryAsync<TrackMetricDto>(sql);
            return Ok(tracks);
        }
    }
}
