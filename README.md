# Tacklog
#### Video Demo:  <URL HERE>
#### Description:
The idea for my  final project started small––and quickly ballooned. If I have learned one non-technical thing from this project, it's the importance of defining the scope of a project and sticking to those guidelines.

Originally my idea was to create a script that would help people get through their backlog of unplayed video games by selecting the next game they should play for them. The recommendation would be based off the games the person had played recently. For example, if they previously played a long game, this algorithm would recommend a short game from their backlog; if they recently played a horror game, maybe it would recommend a puzzle game.

What I failed consider at the outset was that this would require a system to track and manage users' backlogs for the algorithm to use. Once I started building the backlog management system, I realised that this was a big enough task in itself.

So the project that I'm presenting for this submission is a video game backlog management tool, which will be the basis for the recommendation engine that I hope to build in the future.

The project is built on the Django framework and sources most if its data from IGDB.com, a database site that stores information about video games, via an API. 

I used Django's native [user authentication system](https://docs.djangoproject.com/en/5.0/topics/auth/) and built one Django app (called "games") that handles searching for games from IGDB, adding games to users' backlogs, and marking a status ("backlog","playing", or "completed") along with the associated dates of each.

When a user adds a game to their backlog, I record the IGDB game ID in a Django model, associated with the user ID. When the user then visits their "My Games" page, I ping the IGDB API to retrieve the metadata associated with each game (ie. name, release date, cover art, etc.).

For the front end I used Bootstrap (v5.3.0) for the with some minor customisations, such as the overlay that appears when you hover your mouse over a currently-playing game.

And for hosting I used AWS——EC2 for my database and Elastic Beanstalk for the site. I purchased an SSL certificate from my domain registrar, Namecheap, and once approved, uploaded that to AWS's Certificate Manager.