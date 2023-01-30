from .models import Backlogged  
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils import timezone
from re import findall

import datetime
import requests

endpoint = 'https://api.igdb.com/v4'
HEADERS = {
    'Client-ID': 'eclpixd8yx6t9lfnn52s84xkcpgyq0',
    'Authorization': 'Bearer 27xap8tn68bt62u6vd6ttfzr4hwt7w'
}

# Create your views here.
def index(request):
    return render(request, 'games/index.html')

def search(request):
    # Retrieve search term and store in context data.
    query = request.GET.get('q')
    context_data = {'search_term' : query}
    
    # Check if there is a search term present.
    if query:
        # Retrieve a list of similar games from IGDB.
        games = requests.post(f'{endpoint}/games', headers=HEADERS, data=f'fields id,name,first_release_date,category; search "{query}"; where total_rating_count > 0 & category = (0,8); limit 500;').json()
        
        # Compile a list of game IDs and request cover images for them from IGDB.
        ids = []
        for game in games:
            ids.append(game['id'])
            if 'first_release_date' in game:
                game['first_release_date'] = datetime.datetime.fromtimestamp(game['first_release_date']).strftime('%Y-%m-%d')
            else:
                game['first_release_date'] = 'Unknown'
        ids = ','.join(str(x) for x in ids)
        images = requests.post(f'{endpoint}/covers', headers=HEADERS, data=f'fields url,game; where game = ({ids}); limit 500;').json()

        # Add image filename as a new key into the games object.
        for image in images:
            for game in games:
                if game['id'] == image['game']:
                    game['img'] = findall('(?:\/.+\/)(.*\.jpg)',image['url'])[0]

        # Add games object into context data object.
        context_data['search_results'] = games

    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        games = user.backlog.values('game')
        backlog = []
        for game in games:
            backlog.append(game['game'])

        if request.method == 'POST':
            
            game = int(request.POST['game'])
            
            if not game in backlog:
                log = Backlogged(game=game, date_added=timezone.now(), user_id=user)
                log.save()
                backlog.append(game)
            else:
                log = Backlogged.objects.get(user_id=user, game=game)
                log.delete()
                backlog.remove(game)
    
        context_data['backlog'] = backlog
    else:
        if request.method == 'POST':
            messages.info(request, 'You must be logged in to add games to your backlog.')
            return redirect('login')


    
    # print(context_data)
    return render(request, 'games/search.html', context_data)