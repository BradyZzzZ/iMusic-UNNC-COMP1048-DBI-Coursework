SELECT UnitPrice, COUNT(*), COUNT(DISTINCT AlbumId), COUNT(DISTINCT ArtistId), SUM(Milliseconds), UnitPrice * COUNT(*)
FROM Track NATURAL JOIN Album
GROUP BY UnitPrice
