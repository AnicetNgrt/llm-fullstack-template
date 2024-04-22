# YOUR APP

A template with a complete backend in Python and frontend in SvelteKit to make real-time LLM apps.

## Features

- Main blank page with a go to demo button
- Easily invite users and manage data using the Supabase dashboard
- Authentication
- Onboarding page for new users
- Compartimented and persisted user sessions
- Real-time chat with a state-based agent

## Screenshots

![alt text](docs/loginscreen.png)

![alt text](docs/screen.png)

## How it works roughly

The backend and the frontend communicate partially via http calls and mainly via websocket communication within persistant sessions.

Sessions are handled on the frontend with the `useSessions` and `usePayloads` hooks which allow sending/receiving payloads from the backend.

Sessions are handled on the backend via states, which are persisted for later recovery. See `backend/yourapp/example_logic/example.py`. This is where you should put your prompting/agents code.

The backend features utilities to prompt models hosted by Anthropic, Perplexity, Groq and Mistral. 

The backend delegates authentication partially and storage entirely to Supabase. You probably don't need to bother about it.


## Setup

### Supabase and Database

1. Create a free tier project on [supabase](https://supabase.com/).

2. Enable login via email/password

![alt text](docs/emaillogin.png)

3. Create a user, or many (without requiring email verification), assign them a password (they'll choose a new one and a username during onboarding):

![alt](docs/adduser.png)

4. Create a `users infos` table with these columns:

![alt text](docs/userinfos.png)

5. Create a `sessions` table with these columns:

![alt text](docs/sessions1.png)

![alt text](docs/sessions2.png)

6. Create a `sessions messages` table with these columns:

![alt text](docs/sessionsmessages.png)

### Backend

1. Add and edit `backend/.env` with the help of `backend/.env.sample`

2. Create the environment and install the dependencies with the help of `backend/README.md`

### Frontend

1. Install the dependencies with the help of `frontend/README.md`

Note that due to dependencies optimization, the first use of the webapp after launching the dev frontend server may be super slow/irresponsive for a minute. After that hot-reloading got you covered anyway.