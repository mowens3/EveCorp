# EVE Commissar

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/AnaxRho/EVECommissar/blob/main/README.md)
[![ru](https://img.shields.io/badge/lang-ru-yellow.svg)](https://github.com/AnaxRho/EVECommissar/blob/main/README.ru.md)

EVE Commissar is open source Discord bot and web app for managing Discord server roles based on corporation membership in EVE Online.

[Bot invite link](https://discord.com/api/oauth2/authorize?client_id=1157665492564197437&permissions=268437504&scope=bot)

## Contents
* [Administrator Guide](#administrator-guide)
* [User Guide](#user-guide)

## Administrator Guide
    
### Prerequisites

* Create and set up roles which EVE Commissar is supposed to grant members.
* EVE Commissar should have his role on server higher than roles that it will grant \ revoking.
* Create and setup text channel that can be used for granting \ revoking roles notifications.
* You will need to know in-game corporation ID, which can be easily obtained from zkillboard or dotlan.

### Setting up notifications

Set up notifications using `/setup` command.

Command takes 2 arguments:
* `channel` — text channel for notifications. Hit `#` in field to see list of channels; 
* `locale` — locale (language) for bot notifications. As of today, `ru`, `en` (default) options available. 

### Creating rules

Add rules using `/rules add` command.

Command takes 2 arguments:
* `corporation_id` — EVE Online corporation ID;
* `role` — role, which bot should be granting. Hit `@` in field to see list of roles.
    
After creating rule EVE Commissar can perform automated tasks for granting \ revoking roles.\
Use command `/rules show` to see list of rules.\
Use command `/rules remove` to remove rule.
  
### Managing users

* `/member info` — check user registered characters. Hit `@` to see a list of users.
* `/member register` — register user character yourself, provided you know character ID.
* `/member who` — search for character by name of partial name (minimum 4 letters) in registered characters.

### Reports

* `/reports stats` — shows registration statistics.
* `/reports unregistered` — show users which didn't register at least one character.
* `/reports registered` — show registered users and characters list.

### Automated tasks

* EVE Commissar updated registered characters info every 4 hours.
* EVE Commissar check if some members is missing role or has role, which he should not have every 5 minutes.
  * For granting role user should have at least one registered character in specified corporation.
  * For revoking role user should not have registered character in specified corporation.

### Security concerns

* EVECommissar is open-source application.
* In character authorization process EVECommissar requests OAuth 2.0 authorization info from `login.eveonline.com` using only 'publicData' scope.
* EVECommissar doesn't save user authorization info (access_token, refresh_token).
* Access token is used once for verifying character ID.

Refer to [sso_authorization_flow](`https://docs.esi.evetech.net/docs/sso/sso_authorization_flow.html`) for additional information about OAuth 2.0.

## User Guide
        
* Start by running `/character register` command to register your first EVE Online character with bot. After that follow instructions from direct message.
* Command `/character info` could be used to show list of your registered character.
* Command `/character remove` — for removal of registered character.    