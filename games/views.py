from .models import Backlogged, Recommend, Playing, Goty

from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils import timezone
from howlongtobeatpy import HowLongToBeat
from operator import itemgetter
from random import choice
from re import findall

import random
import requests


def index(request):
    return render(request, 'games/index.html')


def search(request):
    # Retrieve search term and store in context data.
    query = request.GET.get('q')
    context_data = {'search_term' : query}
    
    # Check if there is a search term present.
    if query:

        # Get games from IGDB.
        games = igdb_data('search', query)
        if games == 401:
            print(f'Error code: {games}')
            messages.error(request, f'IGDB API error: 401 Unauthorized')
            return render(request, 'games/search.html')

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

        # Get user details and game playing.
        user = User.objects.get(username=request.user)
        playing = Playing.objects.filter(user=user).first()

        # If user is removing a game from backlog.
        if request.method == 'POST':
            
            # Get game ID.
            to_play = request.POST.get('play')
            to_remove = request.POST.get('remove')
            to_shelve = request.POST.get('shelve')

            if to_play:
                # Add game to playing table.
                playing_log = Playing(backlog=Backlogged.objects.get(
                        user=user, game=to_play), user=user)
                playing_log.save()
                return redirect('backlog')
            
            if to_remove:
                remove_log = Backlogged.objects.get(user=user, game=to_remove)
                remove_log.delete()
                return redirect('backlog')
            
            if to_shelve:
                playing.delete()
                return redirect('backlog')


        
        # Get games in user's backlog.
        backlog = Backlogged.objects.filter(user=user).order_by(
            '-date_added').values()
        
        # Transform to list of game IDs.
        ids = []
        for record in backlog:
            ids.append(record['game'])
        ids = ','.join(str(x) for x in ids)

        # Get games from IGDB.
        if ids:
            games = igdb_data('display', ids)

            if games == 401:
                print(f'Error code: {games}')
                messages.error(request, f'IGDB API error: 401 Unauthorized')
                return render(request, 'games/backlog.html')

            # Add date added to backlog to the games object.
            for game in games:
                for log in backlog:
                    if game['id'] == log['game']:
                        game['date_added'] = log['date_added']
                        
                        # Play game as playing.
                        if playing:
                            if log['id'] == playing.backlog_id:
                                game['playing'] = True
                                
                                # Calculate days since game was added to backlog.
                                current_date = datetime.strptime(
                                    datetime.now().strftime('%Y/%m/%d'),"%Y/%m/%d")
                                added_date = datetime.strptime(
                                    game['date_added'].strftime('%Y/%m/%d'),"%Y/%m/%d")
                                started_date = datetime.strptime(
                                    playing.date_started.strftime('%Y/%m/%d'),"%Y/%m/%d")

                                game['days_elapsed'] = (current_date - added_date).days
                                game['days_playing'] = (current_date - started_date).days

                                if game['first_release_date'] == 'Unknown':
                                    game['days_release'] = False
                                else:
                                    release_date = datetime.strptime(
                                        game['first_release_date'],"%Y-%m-%d")
                                    game['days_release'] = (current_date - release_date).days

                                context_data['playing'] = game
                            else: 
                                game['playing'] = False

            games = sorted(
                games, key=itemgetter('first_release_date'), reverse=True)

            # Render backlog page with list of games.
            context_data['backlog'] = games

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
        to_shelve = request.POST.get('shelve')

        if request.method == 'POST':
            
            # Update playing model with current game.
            if to_play:
                playing_log = Playing(backlog=Backlogged.objects.get(
                        user=user, game=to_play), user=user)
                playing_log.save()
                return redirect('what-to-play')
            
            # Remove game from playing table.
            if to_finish or to_shelve:
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
            backlog = Backlogged.objects.filter(
                user=user, id=playing['backlog_id']).values().first()
            context_data['status'] = 'playing'
        elif recommended and not to_pass and not to_shelve:
            backlog = Backlogged.objects.filter(
                user=user,id=recommended['backlog_id']).values().first()
        elif Backlogged.objects.filter(user=user):
            backlog = recommend_game(user, to_pass)
        else:
            context_data['game'] = False
            return render(request, 'games/what_to_play.html', context_data)


        # Get game data from IGDB
        game = igdb_data('display', backlog['game'])
        if game == 401:
            print(f'Error code: {game}')
            messages.error(request, f'IGDB API error: 401 Unauthorized')
            return render(request, 'games/what_to_play.html')
        
        game = game[0]
        
        # Calculate days since game was added to backlog.
        current_date = datetime.strptime(
            datetime.now().strftime('%Y/%m/%d'),"%Y/%m/%d")
        added_date = datetime.strptime(
            backlog['date_added'].strftime('%Y/%m/%d'),"%Y/%m/%d")
        game['days_elapsed'] = (current_date - added_date).days

        gotys = Goty.objects.filter(game=game['id']).values()
        if gotys:
            game['gotys'] = gotys

        hltb_list = HowLongToBeat().search(game['name'])

        if hltb_list is not None and len(hltb_list) > 0:
            hltb_result = max(
                hltb_list, key=lambda element: element.similarity)
            hltb = hltb_result.all_styles

            if hltb % 1 >= 0.25 and hltb % 1 <= 0.75:
                time = str(int(hltb)) + '½'
            else:
                time = str(int(round(hltb)))
            
            game['time_to_beat'] = time
        
        context_data['game'] = game
    
    return render(request, 'games/what_to_play.html', context_data)


def recommend_game(user, skip):
    games = Backlogged.objects.filter(user=user).exclude(game=skip).values()
    selection = choice(games)
    recommended_log = Recommend(backlog=Backlogged.objects.get(
        user=user,game=selection['game']))
    recommended_log.save()
    recommended_log.user.add(user)
    return selection


def igdb_data(query_type, input):

    endpoint = 'https://api.igdb.com/v4'
    HEADERS = {
        'Client-ID': 'eclpixd8yx6t9lfnn52s84xkcpgyq0',
        'Authorization': 'Bearer 2o02ulh84j10on71el9qcptyvpi4b0'
    }

    if query_type == 'search':
        data = f'''
                fields id,name,first_release_date,summary; 
                search "{input}"; where total_rating > 0 
                & category = (0,4,8); limit 500;
                '''
    elif query_type == 'display':
        data = f'''
                fields id,name,first_release_date,summary; 
                where id = ({input}); limit 500;
                '''
    else:
        return -1
    
    # Get list of games from IGDB.
    response = requests.post(f'{endpoint}/games',
                          headers=HEADERS,
                          data=data
                          )

    # Check that the API call was sucessful
    if response.status_code == 200:
        games = response.json()
    else:
        return response.status_code

    # Compile a list of game IDs and format timestamps.
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
    
    return games