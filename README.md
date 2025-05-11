# 🚨 PFP Alerter Discord Bot 🚨

A _discord bot_ that sends alert messages (with funny message) whenever a user changes their **profile picture** or there **display name** on _discord_.

# Features

 - [x] Sends message on profile change
 - [x] Members Opt-in and out
 - [ ] Funny messages **_(quips)_**
 - [x] Image of changes sent when alerting
 - [ ] Leaderboards and Rank
 - [ ] Adding your own quips

# Contributing

Please read the [Contributing Guide](CONTRIBUTING.md) before even thinking about creating a fork 👀

You can also get an high-level overview of the code in the [Technical Specification](TECHNICAL_SPEC.md) document!

### Project TODOs
Here are a list of thing that we need help with!

**Before 1.0 Releases:**

 - [ ] More funny messages
 - [x] Logo
 - [x] An member before and after image render
 - [ ] Leaderboard and Rank commands
 - [ ] Editing quips commands

**Possible features**
 - [ ] Logo as SVG
 - [ ] More diff arrows / user defined custom arrows
 - [ ] Better logging *
 - [ ] AI Generated quips **_(???)_**
 - [ ] Sharing Quips between guilds


<details>
    <summary><h5><small><em>*: More info about the logging<em></small></h5></summary>
    <p>This is for sending logs/log ids to users when an error occurs. This system should be robust so it can work for other bots <small><em>(maybe a separate module, idk).</em></small></p>
    <p>It would be nice if we where able to send the full log to the user, so they can send it as an issue and get well versed contributes to help, however, logs most likely will have context that contain sensitive data and also most people using the bot, are most-likely... <em>dumb</em> so it wouldn't be of use to most people</p>
</details>