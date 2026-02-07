# API Documentation

## Base URL

```
http://localhost:7777/api
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### Register
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword",
  "password_confirm": "securepassword"
}

Response: 201 Created
{
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    ...
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user",
  "password": "password"
}

Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Logout
```http
POST /api/auth/logout/
Authorization: Bearer <token>
Content-Type: application/json

{
  "refresh": "refresh_token_here"
}

Response: 200 OK
{
  "message": "Logout successful"
}
```

#### Refresh Token
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "refresh_token_here"
}

Response: 200 OK
{
  "access": "new_access_token"
}
```

### Profile

#### Get Profile
```http
GET /api/auth/profile/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "username": "user",
  "email": "user@example.com",
  "bio": "",
  "avatar": null,
  "total_songs_created": 5,
  "total_songs_published": 2,
  "created_at": "2026-01-15T10:30:00Z"
}
```

#### Update Profile
```http
PATCH /api/auth/profile/
Authorization: Bearer <token>
Content-Type: application/json

{
  "bio": "Music lover and AI enthusiast"
}

Response: 200 OK
```

#### Set API Key
```http
PATCH /api/auth/api-key/
Authorization: Bearer <token>
Content-Type: application/json

{
  "openai_api_key": "sk-...",
  "use_own_api_key": true
}

Response: 200 OK
{
  "message": "API key updated successfully",
  "use_own_api_key": true
}
```

### Songs

#### List Songs
```http
GET /api/songs/?my_songs=true&genre=pop&ordering=-created_at
Authorization: Bearer <token>

Query Parameters:
- my_songs: boolean (show user's songs)
- genre: string (filter by genre)
- mood: string (filter by mood)
- search: string (search in title/lyrics)
- ordering: string (sort field, prefix with - for descending)

Response: 200 OK
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {...},
      "title": "Summer Vibes",
      "lyrics": "...",
      "genre": "pop",
      "mood": "happy",
      "duration": 30,
      "audio_file": "/media/songs/...",
      "status": "completed",
      "is_public": true,
      "upvotes": 15,
      "downvotes": 2,
      "score": 13,
      "play_count": 42,
      "user_vote": "up",
      "created_at": "2026-02-01T12:00:00Z"
    }
  ]
}
```

#### Get Song
```http
GET /api/songs/1/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "title": "Summer Vibes",
  ...
}
```

#### Create Song
```http
POST /api/songs/create/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My New Song",
  "lyrics": "Verse 1...",
  "description": "A happy summer song",
  "genre": "pop",
  "mood": "happy",
  "duration": 30,
  "temperature": 1.0
}

Response: 201 Created
{
  "id": 2,
  "status": "generating",
  ...
}
```

#### Update Song
```http
PATCH /api/songs/1/
Authorization: Bearer <token>
Content-Type: application/json

{
  "description": "Updated description"
}

Response: 200 OK
```

#### Delete Song
```http
DELETE /api/songs/1/
Authorization: Bearer <token>

Response: 204 No Content
```

#### Publish/Unpublish Song
```http
POST /api/songs/1/publish/
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "publish"  // or "unpublish"
}

Response: 200 OK
{
  "message": "Song published successfully",
  "song": {...}
}
```

#### Record Play
```http
POST /api/songs/1/play/

Response: 200 OK
{
  "play_count": 43
}
```

#### Vote on Song
```http
POST /api/songs/1/vote/
Authorization: Bearer <token>
Content-Type: application/json

{
  "vote_type": "up"  // or "down"
}

Response: 200 OK
{
  "message": "Vote recorded",
  "upvotes": 16,
  "downvotes": 2,
  "score": 14
}
```

#### Remove Vote
```http
DELETE /api/songs/1/vote/
Authorization: Bearer <token>

Response: 200 OK
{
  "message": "Vote removed",
  "upvotes": 15,
  "downvotes": 2,
  "score": 13
}
```

### Generation

#### Generate Lyrics
```http
POST /api/generation/lyrics/
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt": "Write lyrics for a happy pop song about summer",
  "temperature": 0.8
}

Response: 200 OK
{
  "status": "success",
  "lyrics": "Verse 1:\nSunshine on my face..."
}
```

#### Get Task Status
```http
GET /api/generation/task/<task_id>/
Authorization: Bearer <token>

Response: 200 OK
{
  "task_id": "abc-123",
  "status": "SUCCESS",
  "result": {...}
}
```

### Library

#### Get Library Stats
```http
GET /api/library/stats/
Authorization: Bearer <token>

Response: 200 OK
{
  "total_songs": 10,
  "completed_songs": 8,
  "generating_songs": 1,
  "failed_songs": 1,
  "published_songs": 5,
  "total_plays": 250,
  "total_upvotes": 48,
  "genres": [
    {"genre": "pop", "count": 5},
    {"genre": "rock", "count": 3},
    {"genre": "jazz", "count": 2}
  ]
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "error": "Error message here"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

Song generation is rate-limited to prevent abuse:
- Default: 10 songs per hour per user
- Configurable in settings

## WebSocket Support

Real-time updates for song generation status (future enhancement).
