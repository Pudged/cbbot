
# Casa Bonita Bot

This application will check for availability of reservations at Casa Bonita. The prerequisite being you have a unique access_code from the email recieved after being selected from the waitlist. This application will check for any new dates that have been added and send a notification to the user through a Discord bot.



## Documentation

[Getting Started with Discord.py](https://discordpy.readthedocs.io/en/stable)

[Deploying to Heroku](https://www.youtube.com/watch?v=TxYGJyuEXPk)

## Run Locally

Clone the project

```bash
  git clone git@github.com:Pudged/cbbot.git
```

Install dependencies

```bash
  pip3 install -r requirements.txt
```

Setup environment variables
```bash
  cp copy.env .env
```

Run the python

```bash
  python3 main.py
```


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file if running the app locally. If running on Heroku, these will need to be added to the Config Vars for your application.

`BOOKING_CODE`: Obtain from your unique email link \
`PARTY_SIZE`: Size of party (1-8)\
`SERVICE`: lunch or dinner\
`SEATING`: 'default' for traditional dining or 'counter' for Cliffside Dining\
`DISCORD_TOKEN`:  Token for Discord developer application\
`GUILD`: Discord Server ID\
`CHANNEL`: Discord Channel ID\
`USER_ID`: User ID to be pinged on notification


## Deployment
I personally used Heroku to deploy this project. The video I used as a guideline is in the Documentation section

