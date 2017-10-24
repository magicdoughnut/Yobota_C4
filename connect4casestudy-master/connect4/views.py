

from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Game, Coin
import models
from django.db.models import Q
import numpy as np

# Create your views here.
def loginview(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'],password=request.POST['password'])
        if user is not None:
            login(request,user)
            if 'next' in request.POST:
                return redirect(request.POST['next'])
            # return render(request, 'connect4/games.html',{'error':'Login successful'})
            return redirect('games')
        else:
            return render(request, 'connect4/login.html',{'error':'The Username and Password didn\'t match'})
    else:
        return render(request, 'connect4/login.html')

def logoutview(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                User.objects.get(username=request.POST['username'])
                return render(request, 'connect4/signup.html',{'error':'Username has already been taken'})
            except User.DoesNotExist:
                user = User.objects.create_user(request.POST['username'], password =request.POST['password1'])
                login(request,user)
                return render(request, 'connect4/signup.html')
        else:
            return render(request, 'connect4/signup.html',{'error':'Passwords didn\'t match'})
    else:
        return render(request, 'connect4/signup.html')


def games(request):
    """
    Write your view which controls the game set up and selection screen here
    :param request:
    :return:
    """
    yourGames = Game.objects
    # qs = Game.objects.filter(status="Finished")
    # print qs.query
    UserName = request.user.username

    if request.method == 'POST':
        if request.POST['newGame']:
            game = models.Game()
            game.player1 = request.user
            game.status = 'waiting for 2nd player'
            game.created_date = timezone.datetime.now()
            game.save()
            return redirect('games')
    else:
        pass

    return render(request,'connect4/games.html',{'yourGames':yourGames,'UserName':UserName})


def make_grid(coins,game_id):
    currentGame = Game.objects.filter(id=game_id)
    currentGame = currentGame[0]

    grid = np.zeros((6, 7),dtype=np.int)

    for coin in coins:
        if str(coin.player) == str(currentGame.player1):
            grid[int(coin.row),int(coin.column)] = 1
        if str(coin.player) == str(currentGame.player2):
            grid[int(coin.row),int(coin.column)] = 2

    for line in grid:
        print line

    return grid 

def check_if_won(grid):
    return False

def play(request, game_id):
    """
    write your view which controls the gameplay interaction w the web layer here
    :param request:
    :return:
    """
    game = get_object_or_404(Game, pk=game_id)
    coins = Coin.objects.filter(game = game_id)
    grid = make_grid(coins,game_id)

    if request.method == 'POST':
        if request.POST['column'] and request.POST['row']:

            rowVal = int(request.POST['row'])
            columnVal = int(request.POST['column'])

            print 'row value is :' +str(rowVal)
            print 'column value is :' +str(columnVal)
            print 'grid value is :' + str(grid[rowVal,columnVal])

            for row in grid:
                print row

            if rowVal not in range(0,6) or columnVal not in range(0,7): # Make sure coin is in grid range
                print '___COIN NOT IN GRID RANGE___'
                return render(request, 'connect4/play.html', {'game':game,'grid':grid,'error':'outside of grid'})
            elif rowVal != 5 and grid[rowVal+1,columnVal] == 0:  # Make sure coin is not floating
                print '___COIN IS FLOATING___'
                return render(request, 'connect4/play.html', {'game':game,'grid':grid,'error':'coins cant float!'})
            elif grid[rowVal,columnVal] != 0: # Make sure coin space is vacant
                print '___SPACE IS NOT VACANT___'
                return render(request, 'connect4/play.html', {'game':game,'grid':grid,'error':'already a coin here!'})
            elif check_if_won(grid) == True: # Check for winner
                print '___SOMEONE HAS WON___'
                # Change game status to 'Finished'
                return render(request, 'connect4/play.html', {'game':game,'grid':grid,'error':'YOU WIN!'})
            else: # Update grid
                print '___GRID HAS BEEN UPDATED___'
                coin = models.Coin()
                coin.column = request.POST['column']
                coin.row = request.POST['row']
                coin.player = request.user
                coin.game = get_object_or_404(Game, pk=game_id)
                coin.created_date = timezone.datetime.now()
                coin.save()
                grid = make_grid(coins,game_id)
                return render(request, 'connect4/play.html', {'game':game,'grid':grid})

    return render(request, 'connect4/play.html', {'game':game,'grid':grid})



