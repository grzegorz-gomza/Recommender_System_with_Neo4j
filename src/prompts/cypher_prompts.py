CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about movies and provide recommendations.
Convert the user's question based on the schema.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Do not return entire nodes or embedding properties.

Fine Tuning:

1. The actor names, director names, genres, country names and movie type are lowercase.
2. When you are asked about more than one parameter or node type, don't try to create a query which directly answers the question.
Instead of that take one node/parameter as the start point and yield the the other node parameteres, to avoid returning no results.
Example:
Instead of:
MATCH (a:Actor {actorName: "actor_name"})-[:ACTED_IN]->(m:Movie)-[:IN_GENRE]->(g:Genre {genre: "genre_name"})
RETURN m.title
Do:
MATCH (a:Actor {actorName: "actor_name"})-[:ACTED_IN]->(m:Movie)-[:IN_GENRE]->(g:Genre)
RETURN m.title, g.genre


Example Cypher Statements:

1. To find who acted in a movie:
```
MATCH (a:Actor)-[r:ACTED_IN]->(m:Movie {{title: "Movie Title"}})
RETURN a.actorName
```

2. To find who directed a movie:
```
MATCH (d:Director)-[r:DIRECTED]->(m:Movie {{title: "Movie Title"}})
RETURN d.directorName
```

3. How to find how many degrees of separation there are between two Actors:
```
MATCH path = shortestPath(
  (p1:Actor {{actorName: "Actor 1"}})-[:ACTED_IN*]-(p2:Actor {{actorName: "Actor 2"}})
)
WITH path, p1, p2, relationships(path) AS rels
RETURN
  p1 {{ .actorName }} AS start,
  p2 {{ .actorName }} AS end,
  reduce(output = '', i in range(0, length(path)-1) |
    output + CASE
      WHEN i = 0 THEN
       startNode(rels[i]).actorName + CASE WHEN type(rels[i]) = 'ACTED_IN' THEN ' played '+ rels[i].role +' in 'ELSE ' directed ' END + endNode(rels[i]).title
       ELSE
         ' with '+ startNode(rels[i]).actorName + ', who '+ CASE WHEN type(rels[i]) = 'ACTED_IN' THEN 'played '+ rels[i].role +' in '
    ELSE 'directed '
      END + endNode(rels[i]).title
      END
  ) AS pathBetweenPeople
```

Schema:
{schema}

Question:
{question}
"""


CYPHER_MOVIE_SIMILARITY_SEARCH_TEMPLATE = """
MATCH (target:Movie {title: $movie_title})-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(m:Movie)
OPTIONAL MATCH (target)<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(m)
WHERE NOT m.title IN $user_watched_movies + $user_movies
WITH m, g, 
    CASE WHEN a IS NOT NULL THEN a ELSE "No Actor" END AS validActor
WITH m, 
    COUNT(DISTINCT g) AS sharedGenres, 
    COUNT(DISTINCT validActor) AS sharedActors
WITH m, 
    sharedGenres, 
    sharedActors, 
    (sharedGenres * 2 + sharedActors) AS score
RETURN m.title AS RecommendedMovie, score
ORDER BY score DESC, m.title 
LIMIT 5
    """


CYPHER_GENRE_SIMILARITY_SEARCH_TEMPLATE = """
MATCH (rec:Movie)-[:IN_GENRE]-(g:Genre)
WHERE g.genre IN $user_genres
AND NOT rec.title IN $user_watched_movies
WITH rec, COLLECT(DISTINCT g.genre) AS genres
WITH rec, SIZE([gen IN $user_genres WHERE gen IN genres]) AS genreMatchCount
ORDER BY genreMatchCount DESC
RETURN DISTINCT rec.title LIMIT 5
    """


CYPHER_ACTOR_SIMILARITY_SEARCH_TEMPLATE = """
MATCH (rec:Movie)<-[:ACTED_IN]-(a:Actor)
WHERE a.actorName in $user_actors
AND NOT rec.title IN $user_watched_movies
WITH rec, COLLECT(DISTINCT a.actorName) as Actors
WITH rec, SIZE([actor IN $user_actors WHERE actor in Actors]) AS actorsMatchCount
ORDER BY actorsMatchCount DESC
RETURN DISTINCT rec.title LIMIT 5
"""
