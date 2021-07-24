
This is a server for a MMORPG. The players get to be characters in the
audience of their favorite music artistic while a concert is happening.
Suddenly, some number of beach balls are tossed into the audience. The
players might catch them, they might throw them back... who knows!

Much excitement abounds!

Ok, for the RESTful API... an `id` is a 12 character hexidecimal ascii
string, e.g. `feedbeefcafe`, `babb1ebabb1e`, or `f001de7ec7ed`.

`/poll/[id]`: poll the server to determine whether you currently have a ball

`/toss/[id]`: toss the ball (if you have it)

Each of these endpoints returns a json object like this:

```
{
	"User":"001122334455",
	"Score":0,
	"Err":"",
	"Hasball":true
}
```

`User` is the `id` passed to the API, `Score` is the user's current score
(more later), `Err` is any error message (usually empty), and `Hasball` is
an indicator of whether this user currently has a ball.

To score, a user must toss the ball after having realized they have it, but
they must do so before the ball expires (currently 2 minutes). Users are
expected to poll once per minute. The number of balls in circulation is
kept to approximately 1 per 5 active users. A user is active if they have
interacted with the API in the past 3 minutes.

