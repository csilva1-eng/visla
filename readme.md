### Name to be changed but currently Visla v1

### Features
    - Instagram bot @shax.xl2
    - Google auth
    - Connected to google calendar
    - Send bot posts or messages of events and it will auto add to your google calendar
    - Small frontend for connecting google account

### Architecture
    - AWS RDS postgresql db
    - llm calls to navigator using model gpt-oss-120b
    - fastapi + python backend
    - react + vite frontend
    - instagram bot created using facebook.developers

    dm bot on instagram 
            |
            V
    bot replies with on boarding link
            |
            V
    using the onboarding link access frontend
            |
            V
    Connect google account
            |
            V
    Now send bot posts whenever you want
            |
            V
    Post are auto added to calendar

### Future Features?
    - Bot can find when events are interfering on same dates. Improve this to check times and ask user if they would like to remove either event or keep both
    - Make frontend have more features such as light/dark mode, maybe a log of all the events ever created by user(?), a disconnect/delete account option, if possible give user choice of different calendars
    - Have onboard link be sent when a user follows the account rather than send a first message
    - Have a introduction message for visla
    - Change the name from visla to something that makes more sense
    - custom favicon