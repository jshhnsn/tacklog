from .models import Backlogged  
from django.contrib import messages
from django.shortcuts import render, redirect
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
    query = request.GET.get('q')
    data = {'search_term' : query}
    
    if query:
        games = requests.post(f'{endpoint}/games', headers=HEADERS, data=f'fields id,name,first_release_date,category; search "{query}"; where total_rating_count > 0 & category = (0,8); limit 500;').json()
        # print(games)
        ids = []

        for game in games:
            ids.append(game['id'])
            if 'first_release_date' in game:
                game['first_release_date'] = datetime.datetime.fromtimestamp(game['first_release_date']).strftime('%Y-%m-%d')
            else:
                game['first_release_date'] = 'Unknown'


        ids = ','.join(str(x) for x in ids)
        images = requests.post(f'{endpoint}/covers', headers=HEADERS, data=f'fields url,game; where game = ({ids}); limit 500;').json()

        for image in images:
            for game in games:
                if game['id'] == image['game']:
                    game['img'] = findall('(?:\/.+\/)(.*\.jpg)',image['url'])[0]

        data['search_results'] = games
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, 'You must be logged in to add games to your backlog.')
            return redirect('login')
        game = int(request.POST['game'])
        user = request.user
        log = Backlogged(game=game, date_added=datetime.datetime.now(), user_id=user)
        log.save()
    
    return render(request, 'games/search.html', data)