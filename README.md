# Electricity notification :electric_plug:

Checks a local site for electricity shutdown notification and if a street
 in alert settings exists it will send an alert to a discord channel via discord
webhook.

# Usage

Make an **env.json** file with following:

```json
  "discord_webhook": "discord webhook",
  "search_page_url": "search page of the local website",
  "checks": [
    {
      "street": "Street Name",
      "user": "<@UserDiscordId>"
    },
    {
      "street": "Street Name 2",
      "user": "<@UserDiscordId2>"
    }
  ]
```

After that just run the script with python3.