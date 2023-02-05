from .models import Backlogged  

from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils import timezone
from random import choice
from re import findall

import random
import requests

endpoint = 'https://api.igdb.com/v4'
HEADERS = {
    'Client-ID': 'eclpixd8yx6t9lfnn52s84xkcpgyq0',
    'Authorization': 'Bearer 27xap8tn68bt62u6vd6ttfzr4hwt7w'
}



def index(request):
    return render(request, 'games/index.html')


def search(request):
    # Retrieve search term and store in context data.
    query = request.GET.get('q')
    context_data = {'search_term' : query}
    
    # Check if there is a search term present.
    if query:
        # Retrieve a list of similar games from IGDB.
        games = requests.post(f'{endpoint}/games', headers=HEADERS, 
                              data=f'''
                              fields id,name,first_release_date,category; 
                              search "{query}"; where total_rating_count > 0 
                              & category = (0,8); limit 500;
                              '''
                              ).json()
        
        # Compile a list of game IDs.
        ids = []
        for game in games:
            ids.append(game['id'])
            if 'first_release_date' in game:
                game['first_release_date'] = datetime.fromtimestamp(
                    game['first_release_date']).strftime('%Y-%m-%d')
            else:
                game['first_release_date'] = 'Unknown'
        ids = ','.join(str(x) for x in ids)

        # Request cover artwork for games from IGDB.
        images = requests.post(f'{endpoint}/covers', headers=HEADERS, 
                               data=f'''
                               fields url,game; where game = ({ids}); 
                               limit 500;
                               '''
                               ).json()

        # Add image filename as a new key into the games object.
        for image in images:
            for game in games:
                if game['id'] == image['game']:
                    game['img'] = findall(
                        '(?:\/.+\/)(.*\.jpg)',image['url'])[0]

        # Add games object into context data.
        context_data['search_results'] = games

    # If the user is logged in.
    if request.user.is_authenticated:
        # Get games in the user's backlog.
        user = User.objects.get(username=request.user)
        games = user.backlog.values('game')
        # Transform to list of game IDs.
        backlog = []
        for game in games:
            backlog.append(game['game'])

        # If user added or removed game.
        if request.method == 'POST':
            # Get game ID.            
            game = int(request.POST['game'])
            # Add to backlog if not already there.
            if not game in backlog:
                log = Backlogged(game=game, date_added=timezone.now(), 
                                 user_id=user)
                log.save()
                backlog.append(game)
            # Delete from backlog if already there.
            else:
                log = Backlogged.objects.get(user_id=user, game=game)
                log.delete()
                backlog.remove(game)

        # Pass list of backlog game IDs to the context data.
        context_data['backlog'] = backlog

    # If user is not logged in, and trying to add game to backlog.
    else:
        if request.method == 'POST':
            # Generate error message and redirect to login page.
            messages.info(request, 
                          'You must be logged in to add games to your backlog.'
                          )
            return redirect('login')

    # Render search page with list of games IDs in user's backlog.
    return render(request, 'games/search.html', context_data)


@login_required
def backlog(request):
    context_data = {}

    # If user is logged in.
    if request.user.is_authenticated:

        # Get user details.
        user = User.objects.get(username=request.user)

        # If user is removing a game from backlog.
        if request.method == 'POST':
            # Get game ID.
            game = int(request.POST['game'])
            # Remove game from backlog.
            log = Backlogged.objects.get(user_id=user, game=game)
            log.delete()
        
        # Get games in user's backlog.
        backlog = Backlogged.objects.filter(user_id=user).order_by(
            '-date_added').values()
        
        # Transform to list of game IDs.
        ids = []
        for record in backlog:
            ids.append(record['game'])
        ids = ','.join(str(x) for x in ids)

        # Request ID, name, and release data for games.
        games = requests.post(f'{endpoint}/games', headers=HEADERS, 
                              data=f'''
                              fields id,name,first_release_date; 
                              where id = ({ids}); limit 500;
                              '''
                              ).json()

        # Add data added as a new key into the games object.
        for entry in backlog:
            for game in games:
                if entry['game'] == game['id']:
                    entry['name'] = game['name']
                    if 'first_release_date' in game:
                        entry['release_date'] = datetime.fromtimestamp(
                            game['first_release_date']).strftime('%b. %d, %Y')
                    else:
                        entry['release_date'] = 'Unknown'

    # Render backlog page with list of games.
        context_data['backlog'] = backlog
    return render(request, 'games/backlog.html', context_data)

@login_required
def play_next(request):
    context_data = {}

    # If user is logged in.
    if request.user.is_authenticated:
        # Get user details.
        user = User.objects.get(username=request.user)
        # Get games in user's backlog.
        backlog = Backlogged.objects.filter(user_id=user).order_by(
            '-date_added').values()

        # If there are no games in backlog, return context data with no game.
        if not backlog:
            context_data['game'] = False

        # If the user has games in their backlog.
        else:
            # Choose a game at random.
            winner = choice(backlog)
            id = winner['game']
            # Get game info from IGDB
            game = requests.post(f'{endpoint}/games', headers=HEADERS, 
                        data=f'''
                        fields id,name,first_release_date,summary; 
                        where id = {id}; limit 500;
                        '''
                        ).json()[0]
            
            # Calculate days since game was added to backlog.
            current_date = datetime.strptime(datetime.now().strftime('%Y/%m/%d'),"%Y/%m/%d")
            added_date = datetime.strptime(winner['date_added'].strftime('%Y/%m/%d'),"%Y/%m/%d")
            game['days_elapsed'] = (current_date - added_date).days
            
            # Convert the release date format.
            if game['first_release_date']:
                game['first_release_date'] = datetime.fromtimestamp(
                            game['first_release_date']).strftime('%b. %d, %Y')
            
            # Get the game's cover art.
            image = requests.post(f'{endpoint}/covers', headers=HEADERS, 
                               data=f'''
                               fields url,game; where game = {id};
                               '''
                               ).json()[0]
            game['img'] = findall('(?:\/.+\/)(.*\.jpg)',image['url'])[0]
            context_data['game'] = game
    
    return render(request, 'games/what_to_play.html', context_data)
