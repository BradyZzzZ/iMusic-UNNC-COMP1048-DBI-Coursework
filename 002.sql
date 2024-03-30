SELECT COUNT(*) as Tracks, COUNT(DISTINCT AlbumId) as Albums, COUNT(DISTINCT ArtistId) as Artists, SUM(Milliseconds) as Duration, SUM(UnitPrice) as TotalValue
FROM Track NATURAL JOIN Album