from .models import Backlogged, Recommend, Playing

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
                log = Backlogged(game=game, user=user)
                log.save()
                backlog.append(game)
            # Delete from backlog if already there.
            else:
                log = Backlogged.objects.get(user=user, game=game)
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
            log = Backlogged.objects.get(user=user, game=game)
            log.delete()
        
        # Get games in user's backlog.
        backlog = Backlogged.objects.filter(user=user).order_by(
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
    context_data = {
        'status' : 'recommended'
    }

    # If user is logged in.
    if request.user.is_authenticated:
        # Get user details.
        user = User.objects.get(username=request.user)

        to_play = request.POST.get('playing')
        to_pass = request.POST.get('pass')
        to_finish = request.POST.get('finish')
        to_abandon = request.POST.get('abandon')

        if request.method == 'POST':
            
            # Update playing model with current game.
            if to_play:
                playing_log = Playing(backlog=Backlogged.objects.get(
                        user=user, game=to_play), user=user)
                playing_log.save()
                return redirect('what-to-play')
            
            # Remove game from playing table.
            if to_finish or to_abandon:
                remove = Playing.objects.get(user=user)
                if to_finish:
                    # Remove from backlog if complete.
                    Backlogged.objects.get(id=remove.backlog_id).delete()
                remove.delete()


        # Get currently playing game and most recently recommended game.
        playing = Playing.objects.filter(user=user).values().first()
        recommended = Recommend.objects.filter(user=user).order_by(
            '-date_recommended').values().first()
        
        # Get the ID of the game to display.
        if playing:
            backlog = Backlogged.objects.filter(user=user, id=playing['backlog_id']).values().first()
            context_data['status'] = 'playing'
        elif recommended and not to_pass:
            backlog = Backlogged.objects.filter(user=user,id=recommended['backlog_id']).values().first()
        elif Backlogged.objects.filter(user=user):
            backlog = recommend_game(user, to_pass)
        else:
            context_data['game'] = False
            return render(request, 'games/what_to_play.html', context_data)


        # Get game data from IGDB
        game = requests.post(f'{endpoint}/games', headers=HEADERS, 
                    data=f'''
                    fields id,name,first_release_date,summary; 
                    where id = {backlog['game']}; limit 500;
                    '''
                    ).json()[0]
        
        # Convert the release date format.
        if game['first_release_date']:
            game['first_release_date'] = datetime.fromtimestamp(
                        game['first_release_date']).strftime('%b. %d, %Y')
        
        # Calculate days since game was added to backlog.
        current_date = datetime.strptime(
            datetime.now().strftime('%Y/%m/%d'),"%Y/%m/%d")
        added_date = datetime.strptime(
            backlog['date_added'].strftime('%Y/%m/%d'),"%Y/%m/%d")
        game['days_elapsed'] = (current_date - added_date).days
        
        # Get the game's cover art.
        image = requests.post(f'{endpoint}/covers', headers=HEADERS, 
                            data=f'''
                            fields url,game; where game = {backlog['game']};
                            '''
                            ).json()[0]
        game['img'] = findall('(?:\/.+\/)(.*\.jpg)',image['url'])[0]
        context_data['game'] = game
        print(context_data)
    
    return render(request, 'games/what_to_play.html', context_data)



def recommend_game(user, skip):
    games = Backlogged.objects.filter(user=user).exclude(game=skip).values()
    selection = choice(games)
    recommended_log = Recommend(backlog=Backlogged.objects.get(
        user=user,game=selection['game']))
    recommended_log.save()
    recommended_log.user.add(user)
    return selection