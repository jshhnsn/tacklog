from .models import Goty, Library

from datetime import datetime, date
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
    if request.user.is_authenticated:
        return redirect('backlog')
    else:
        return redirect('about')

def about(request):
    return render(request, 'games/about.html')

def search(request):
    # Retrieve search term and store in context data.
    query = request.GET.get('q')
    context_data = {'search_term' : query}
    
    results = False

    # Check if there is a search term present.
    if query:

        # Get games from IGDB.
        results = igdb_data('search', query)
        if results == 401:
            print(f'Error code: {results}')
            messages.error(request, f'IGDB API error: 401 Unauthorized')
            return render(request, 'games/search.html')

    # If the user is logged in.
    if request.user.is_authenticated:
        # Get games in the user's backlog.
        user = User.objects.get(username=request.user)
        games = Library.objects.filter(user=user).values()

        # Transform to list of game IDs.
        backlog = []
        for game in games:
            backlog.append(game['game_id'])

        if results:
            for result in results:
                for game in games:
                    if result['id'] == game['game_id']:
                        result['status'] = game['status']
                        result['date_started'] = game['date_started']
                        result['date_completed'] = game['date_completed']

        # If user added or removed game.
        if request.method == 'POST':
            # Get game ID.            
            game_id = int(request.POST['game_id'])
            game_name = request.POST['game_name']
            date_released = request.POST['game_release']

            # Add to backlog if not already there.
            if not game_id in backlog:
                if date_released:
                    log_lib = Library(
                        game_id=game_id, 
                        game_name=game_name, 
                        date_released=date_released,
                        date_backlogged=datetime.now(), 
                        user=user
                        )
                else:
                    log_lib = Library(
                        game_id=game_id, 
                        game_name=game_name,
                        date_backlogged=datetime.now(), 
                        user=user
                        )
                log_lib.save()
            
            # Delete from backlog if already there.
            else:
                log_lib = Library.objects.get(user=user, game_id=game_id)
                log_lib.delete()
            
            return redirect(f'/search?q={query}')

        # Pass list of backlog game IDs to the context data.
        context_data['backlog'] = backlog
        context_data['search_results'] = results
        

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
    
    year = date.today().year
    context_data = {
        'year' : year
        }

    # If user is logged in.
    if request.user.is_authenticated:

        # Get user details and game playing.
        user = User.objects.get(username=request.user)
        playing = Library.objects.filter(user=user,status='playing').values()
        completed = Library.objects.filter(user=user,status='completed',date_completed__gte=date(year,1,1)).order_by('-date_completed').values()
        library = Library.objects.filter(user=user
            ).exclude(date_completed__lt=date(year,1,1)
            ).exclude(date_retired__lt=date(year,1,1)
            ).exclude(date_completed=None, status='completed'
            ).order_by('-date_released').values()


        # If user is editing a game in their backlog.
        if request.method == 'POST':
            
            # Get game ID and action.
            game_id = request.POST.get('game_id')
            action = request.POST.get('action')

            # Update database.
            if action == 'playing':
                Library.objects.filter(user=user, game_id=game_id).update(
                    status=action,date_started=date.today())
            elif action == 'retired':
                Library.objects.filter(user=user, game_id=game_id).update(
                    status=action,date_retired=date.today())
            elif action == 'completed':
                Library.objects.filter(user=user, game_id=game_id).update(
                    status=action,date_completed=date.today())
            elif action == 'backlog':
                Library.objects.filter(user=user, game_id=game_id).update(
                    status=action,date_started=None,date_retired=None)
            elif action == 'remove':
                log = Library.objects.get(user=user, game_id=game_id)
                log.delete()
            elif action == 'edit_dates':
                date_backlogged = request.POST.get('date_backlogged')
                date_backlogged = None if date_backlogged == '' else date_backlogged
                date_started = request.POST.get('date_started')
                date_started = None if date_started == '' else date_started
                date_completed = request.POST.get('date_completed')
                date_completed = None if date_completed == '' else date_completed
                status = request.POST.get('status')
                Library.objects.filter(user=user, game_id=game_id).update(
                    date_backlogged=date_backlogged,
                    date_started=date_started,
                    date_completed=date_completed,
                    status=status,
                    )

            return redirect('backlog')
        

        # Gather game IDs for playing games.
        playing_ids = []
        for game in playing:
            playing_ids.append(game['game_id'])
        playing_ids = ','.join(str(x) for x in playing_ids)


        # Add cover art image name and days played to playing games.
        if playing_ids:
            games = igdb_data('display', playing_ids)

            if games == 401:
                print(f'Error code: {games}')
                messages.error(request, f'IGDB API error: 401 Unauthorized')
                return render(request, 'games/backlog.html')

            for game in games:
                for p in playing:
                    if game['id'] == p['game_id']:
                        p['img'] = game['img']
                        if p['date_started'] is not None:
                            dp = (date.today() - p['date_started']).days
                            p['days_playing'] = f"{dp:,d}"
                        else:
                            p['days_playing'] = '--'
                            p['date_started'] = date(1,1,1)

            context_data['playing'] = sorted(
                playing, key=itemgetter('date_started'), reverse=True)
            
        # Gather game IDs for playing games.
        complete_ids = []
        for game in completed:
            complete_ids.append(game['game_id'])
        complete_ids = ','.join(str(x) for x in complete_ids)
        
        # Add cover art image name and days played to completed games.
        if complete_ids:
            games = igdb_data('display', complete_ids)

            if games == 401:
                print(f'Error code: {games}')
                messages.error(request, f'IGDB API error: 401 Unauthorized')
                return render(request, 'games/backlog.html')

            for game in games:
                for c in completed:
                    if game['id'] == c['game_id']:
                        c['img'] = game['img']

            context_data['completed'] = completed

        context_data['backlog'] = library
    #import pdb; pdb.set_trace()
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
        'Authorization': 'Bearer 93nj18cq31dwtd9ad7c3pxdf7d43no'
    }

    if query_type == 'search':
        data = f'''
                fields id,name,first_release_date,summary; 
                where name ~ *"{input}"* & first_release_date != null &
                category = (0,4,8,10); limit 500; sort category asc;
                '''
        #total_rating > 0
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
                
    # Truncate name for title.
    for game in games:
        if len(game['name']) > 30:
            game['title'] = game['name'][:27].rstrip() + '...'
        else:
            game['title'] = game['name']
    
    return games