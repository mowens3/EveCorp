# EVE Commissar

EVE Commissar is open source Discord bot and web app for managing Discord server roles based on corporation membership in EVE Online.

[Bot invite link](https://discord.com/api/oauth2/authorize?client_id=1157665492564197437&permissions=268437504&scope=bot)

## Contents
* [Administrator Guide](#administrator-guide)
* [User Guide](#user-guide)

## Administrator Guide
    
### Prerequisites

* Create and set up roles which EVE Commissar is supposed to grant members.
* EVE Commissar should have his role on server higher than roles that it will grant \ revoking.
* Server should have text channel that can be used for granting \ revoking roles notifications.
* You will need to know in-game corporation ID, which can be easily obtained from zkillboard or dotlan.

### Creating rules

After that you can add rules using `/rules add` command.

Command takes 4 arguments:
* corporation_id — EVE Online corporation ID;
* role — role, which bot should be granting;
* channel — text channel for notifications; 
* locale — locale (language) for bot notifications.
    
After creating rule EVE Commissar can perform automated tasks for granting \ revoking roles.\
Use command `/rules show` to see list of rules.\
Use command `/rules remove` to remove rule.

### Automated tasks

* EVE Commissar updated registered characters info every 4 hours.
* EVE Commissar check if some members is missing role or has role, which he should not have every 5 minutes.
  * For granting role user should have at least one registered character in specified corporation.
  * For revoking role user should not have registered character in specified corporation.
  
### Managing users

You can use command `/member info` to check user registered characters.
You can use `/member register` to register user character yourself, provided you know character ID.

### Reports

* `/reports stats` — shows registration statistics.
* `/reports unregistered` — show users which didn't register at least one character.
* `/reports registered` — show registered users and characters list.

### Security concerns

* EVECommissar is open-source application.
* In character authorization process EVECommissar requests OAuth 2.0 authorization info from `login.eveonline.com` using only 'publicData' scope.
* EVECommissar doesn't save user authorization info (access_token, refresh_token).
* Access token is used once for verifying character ID.

Refer to [sso_authorization_flow](`https://docs.esi.evetech.net/docs/sso/sso_authorization_flow.html`) for additional information about OAuth 2.0.

## User Guide
        
* Start by running `/character register` command to register your first EVE Online character with bot.
* Command `/character info` could be used to show list of your registered character.
* Command `/character remove` — for removal of registered character.    