package main

// XXX connection/request limits/sec

// Requirement: badge must wake up periodically and show the user's
// current score and their mac address (used to identify the badge)

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"time"

	"github.com/gorilla/mux"
)

type Ball struct {
	// time
	owner    string
	lastseen time.Time
}

type User struct {
	id       string
	score    int
	lastseen time.Time
}

type GameMessage struct {
	user string
	name string
	ret  chan string
}

type GameState struct {
	// next id for a ball
	ballCounter     int
	activityTimeout time.Duration
	ballTimeout     time.Duration
	balls           []Ball
	users           []User
}

var gameState GameState

// All that multithreading to end up in a singlethreaded game state...
func messageWorker(c <-chan GameMessage) {
	msg := <-c

	expireBalls()
	updateLastSeenUser(msg.user)

	if msg.name == "toss" {
		// user tosses ball
		// if they don't have it: error
		// else: record score
		//       mark ball as unowned
	}

	fixBallCount()
	tossBalls()
}

func removeBall(i int) {
	gameState.balls[i] = gameState.balls[len(gameState.balls)-1]
	gameState.balls = gameState.balls[:len(gameState.balls)-1]
}

// Toss all of the unowned balls, make sure a user only has at most 1.
func tossBalls() {
	holders := make(map[string]bool)
	var users []User
	var ballsToToss []int

	for i, ball := range gameState.balls {
		if ball.owner != "" {
			holders[ball.owner] = true
		}
		ballsToToss = append(ballsToToss, i)
	}

	for _, u := range gameState.users {
		if time.Since(u.lastseen) > gameState.activityTimeout {
			// not active, skip
			continue
		}

		_, hasball := holders[u.id]
		if hasball {
			// already has one, skip
			continue
		}

		users = append(users, u)
	}

	if len(users) == 0 {
		return
	}

	for _, i := range ballsToToss {
		gameState.balls[i].lastseen = time.Now()
		gameState.balls[i].owner = users[rand.Intn(len(users))].id
	}
}

func fixBallCount() {
	target := (numActiveUsers() / 5) + 1
	delta := target - len(gameState.balls)

	for delta > 0 {
		// too few
		var ball = Ball{"", time.Now()}
		gameState.balls = append(gameState.balls, ball)
		delta--
	}

	for delta < 0 {
		// too many
		found := false
		for i, ball := range gameState.balls {
			if ball.owner == "" {
				removeBall(i)
				found = true
				delta++
			}
		}
		if !found {
			// didn't find one to delete, oh well
			break
		}
	}
}

func expireBalls() {
	for _, ball := range gameState.balls {
		if ball.owner == "" {
			// not currently in play
			continue
		}
		if time.Since(ball.lastseen) <= gameState.ballTimeout {
			// not expired yet
			continue
		}

		// mark as un-owned
		ball.owner = ""
	}
}

func updateLastSeenUser(id string) {
	for _, u := range gameState.users {
		if u.id == id {
			u.lastseen = time.Now()
			return
		}
	}
	user := User{id, 0, time.Now()}
	gameState.users = append(gameState.users, user)
}

func numActiveUsers() int {
	cnt := 0
	for _, u := range gameState.users {
		if time.Since(u.lastseen) <= gameState.activityTimeout {
			cnt++
		}
	}
	return cnt
}

func main() {

	msgWorker := make(chan GameMessage)
	go messageWorker(msgWorker)

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Hello, you've requested: %s\n", r.URL.Path)
	})

	r := mux.NewRouter()

	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/",
		http.FileServer(http.Dir("."))))

	r.HandleFunc("/poll", func(w http.ResponseWriter, r *http.Request) {
		var msg GameMessage

		msg.user = "user"
		msg.name = "poll"
		msg.ret = make(chan string)
		msgWorker <- msg
		fmt.Fprintf(w, "%s", <-msg.ret)
	})

	r.HandleFunc("/toss", func(w http.ResponseWriter, r *http.Request) {
		var msg GameMessage

		msg.user = "user"
		msg.name = "toss"
		msg.ret = make(chan string)
		msgWorker <- msg
		fmt.Fprintf(w, "%s", <-msg.ret)
	})

	log.Fatal(http.ListenAndServe(":8080", r))
}
