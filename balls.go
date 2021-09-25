package main

// TODO
// - do something useful with the default handler

// XXX connection/request limits/sec
// XXX penalize user for tossing when they don't have ball?

// Requirement: badge must wake up periodically and show the user's
// current score and their mac address (used to identify the badge)

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"os"
	"regexp"
	"time"

	"github.com/gorilla/mux"
)

type Ball struct {
	// time
	Owner    string
	Lastseen time.Time
}

type User struct {
	Id       string
	Score    int
	Lastseen time.Time
}

type GameMessage struct {
	user string
	name string
	ret  chan string
}

type ReturnMessage struct {
	User    string
	Score   int
	Err     string
	Hasball bool
}

type GameState struct {
	activityTimeout time.Duration
	ballTimeout     time.Duration
	balls           []Ball
	users           []User
}

// for marshaling/unmarshaling
type GameStateDisk struct {
	ActivityTimeout string
	BallTimeout     string
	Balls           []Ball
	Users           []User
}

var defaultActivityTimeout string = "3m"
var defaultBallTimeout string = "1m"
var gameState GameState

// All that multithreading to end up in a singlethreaded game state...
func messageWorker(c <-chan GameMessage) {
	for msg := range c {
		expireBalls()
		updateLastSeenUser(msg.user)

		if msg.name == "toss" {
			tossBall(msg.user)
		}

		fixBallCount()
		tossBalls()

		saveGame()
		returnMessage(msg.ret, msg.user)
		close(msg.ret)
	}
}

func returnMessage(c chan string, user string) {
	r := ReturnMessage{}
	r.User = user

	for _, ball := range gameState.balls {
		if ball.Owner == user {
			r.Hasball = true
			break
		}
	}

	for _, u := range gameState.users {
		if u.Id == user {
			r.Score = u.Score
			break
		}
	}

	res, err := json.Marshal(r)
	if err != nil {
		log.Fatal(err)
	}

	c <- string(res)
}

func tossBall(user string) {
	for i, ball := range gameState.balls {
		if ball.Owner == user {
			addScore(user, 1)
			gameState.balls[i].Owner = ""
			return
		}
	}
}

func addScore(user string, inc int) {
	for i, u := range gameState.users {
		if user == u.Id {
			gameState.users[i].Score += inc
			return
		}
	}
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
		if ball.Owner != "" {
			holders[ball.Owner] = true
		}
		ballsToToss = append(ballsToToss, i)
	}

	for _, u := range gameState.users {
		if time.Since(u.Lastseen) > gameState.activityTimeout {
			// not active, skip
			continue
		}

		_, hasball := holders[u.Id]
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
		gameState.balls[i].Lastseen = time.Now()
		gameState.balls[i].Owner = users[rand.Intn(len(users))].Id
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
			if ball.Owner == "" {
				removeBall(i)
				found = true
				delta++
				break
			}
		}
		if !found {
			// didn't find one to delete, oh well
			break
		}
	}
}

func expireBalls() {
	for i, ball := range gameState.balls {
		if ball.Owner == "" {
			// not currently in play
			continue
		}
		if time.Since(ball.Lastseen) <= gameState.ballTimeout {
			// not expired yet
			continue
		}

		// mark as un-owned
		gameState.balls[i].Owner = ""
	}
}

func updateLastSeenUser(id string) {
	for i, u := range gameState.users {
		if u.Id == id {
			gameState.users[i].Lastseen = time.Now()
			return
		}
	}
	user := User{id, 0, time.Now()}
	gameState.users = append(gameState.users, user)
}

func numActiveUsers() int {
	cnt := 0
	for _, u := range gameState.users {
		if time.Since(u.Lastseen) <= gameState.activityTimeout {
			cnt++
		}
	}
	return cnt
}

func saveGame() {
	var gsd GameStateDisk

	gsd.BallTimeout = gameState.ballTimeout.String()
	gsd.ActivityTimeout = gameState.activityTimeout.String()
	gsd.Users = gameState.users
	gsd.Balls = gameState.balls

	content, err := json.Marshal(gsd)
	if err != nil {
		log.Fatal("can't marshal gamestate: ", err)
	}

	ioutil.WriteFile("gamestate.json", content, 0644)
}

func initGameState() {

	var gsd GameStateDisk

	content, err := ioutil.ReadFile("gamestate.json")
	if os.IsNotExist(err) {
		fmt.Println("game state not found, initializing")
		gameState.activityTimeout, err = time.ParseDuration(defaultActivityTimeout)
		if err != nil {
			log.Fatal("invalid timeout: ", defaultActivityTimeout)
		}
		gameState.ballTimeout, err = time.ParseDuration(defaultBallTimeout)
		if err != nil {
			log.Fatal("invalid timeout: ", defaultBallTimeout)
		}
	} else if err != nil {
		log.Fatal("error opening gamestate: ", err)
	} else {
		err = json.Unmarshal(content, &gsd)
		if err != nil {
			log.Fatal("error loading state: ", err)
		}

		gameState.activityTimeout, err = time.ParseDuration(gsd.ActivityTimeout)
		if err != nil {
			log.Fatal("invalid timeout: ", gsd.ActivityTimeout)
		}

		gameState.ballTimeout, err = time.ParseDuration(gsd.BallTimeout)
		if err != nil {
			log.Fatal("invalid timeout: ", gsd.BallTimeout)
		}

		gameState.users = gsd.Users
		gameState.balls = gsd.Balls
	}

	saveGame()
}

var parseIdMatcher = regexp.MustCompile(`^[0-9a-fA-F]+$`)

func parseId(id string) bool {
	// match an ethernet mac address in hex w/out :'s
	if len(id) != 12 {
		// avoid having to parse stupid long re's
		return false
	}
	return parseIdMatcher.MatchString(id)
}

func main() {

	msgWorker := make(chan GameMessage)
	go messageWorker(msgWorker)

	initGameState()

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
	})

	r := mux.NewRouter()

	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/",
		http.FileServer(http.Dir("."))))

	r.HandleFunc("/poll/{id}", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)

		id, hasid := vars["id"]
		if !hasid {
			http.Error(w, "missing id", http.StatusNotAcceptable)
			return
		}

		if !parseId(id) {
			http.Error(w, "bad id", http.StatusNotAcceptable)
			return
		}

		msg := GameMessage{id, "poll", make(chan string)}
		msgWorker <- msg
		w.Header().Set("Content-Type",
			"application/json; charset=utf-8")
		fmt.Fprintf(w, "%s", <-msg.ret)
	})

	r.HandleFunc("/toss/{id}", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)

		id, hasid := vars["id"]
		if !hasid {
			http.Error(w, "missing id", http.StatusNotAcceptable)
			return
		}

		if !parseId(id) {
			http.Error(w, "bad id", http.StatusNotAcceptable)
			return
		}

		msg := GameMessage{id, "toss", make(chan string)}
		msgWorker <- msg
		w.Header().Set("Content-Type",
			"application/json; charset=utf-8")
		fmt.Fprintf(w, "%s", <-msg.ret)
	})

	log.Fatal(http.ListenAndServe(":8080", r))
}
