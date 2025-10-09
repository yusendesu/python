from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from game_logic import UNOGame
import uuid
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uno_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 存储游戏实例
games = {}
player_sessions = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_game')
def create_game():
    game_id = str(uuid.uuid4())[:8]
    games[game_id] = UNOGame(game_id)
    return {'game_id': game_id, 'status': 'created'}


@app.route('/join_game/<game_id>')
def join_game(game_id):
    if game_id not in games:
        return {'error': 'Game not found'}, 404

    game = games[game_id]
    if len(game.players) >= 4:
        return {'error': 'Game is full'}, 400

    return {'game_id': game_id, 'status': 'can_join'}


@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')


@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    if session_id in player_sessions:
        game_id = player_sessions[session_id]['game_id']
        player_name = player_sessions[session_id]['player_name']

        if game_id in games:
            game = games[game_id]
            game.remove_player(player_name)

            # 通知其他玩家
            emit('player_left', {'player_name': player_name}, room=game_id)

            # 如果游戏为空，清理游戏
            if len(game.players) == 0:
                del games[game_id]

        del player_sessions[session_id]


@socketio.on('join_game')
def handle_join_game(data):
    game_id = data['game_id']
    player_name = data['player_name']

    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return

    game = games[game_id]

    if len(game.players) >= 4:
        emit('error', {'message': 'Game is full'})
        return

    # 加入房间
    join_room(game_id)

    # 存储玩家会话信息
    player_sessions[request.sid] = {
        'game_id': game_id,
        'player_name': player_name
    }

    # 添加玩家到游戏
    success, player_id = game.add_player(player_name, request.sid)

    if success:
        # 通知所有玩家
        emit('player_joined', {
            'player_name': player_name,
            'players': game.get_players_info()
        }, room=game_id)

        # 发送游戏状态给新玩家
        emit('game_state', game.get_game_state(player_id), room=request.sid)

        # 如果游戏可以开始，自动开始
        if len(game.players) >= 2 and not game.started:
            game.start_game()
            emit('game_started', {
                'current_player': game.current_player,
                'play_pile': game.play_pile[-1].to_dict() if game.play_pile else None
            }, room=game_id)


@socketio.on('play_card')
def handle_play_card(data):
    session_info = player_sessions.get(request.sid)
    if not session_info:
        return

    game_id = session_info['game_id']
    player_name = session_info['player_name']

    if game_id not in games:
        return

    game = games[game_id]
    card_index = data['card_index']
    chosen_color = data.get('chosen_color')

    success, message = game.play_card(player_name, card_index, chosen_color)

    if success:
        # 广播游戏状态更新
        game_state = game.get_game_state()
        emit('card_played', {
            'player_name': player_name,
            'card_index': card_index,
            'game_state': game_state,
            'message': message
        }, room=game_id)

        # 检查游戏是否结束
        if game.check_round_winner():
            winner = game.get_round_winner()
            emit('round_ended', {
                'winner': winner,
                'scores': game.get_scores()
            }, room=game_id)

            # 开始新回合
            game.start_new_round()
            emit('new_round_started', {
                'game_state': game.get_game_state()
            }, room=game_id)


@socketio.on('draw_card')
def handle_draw_card():
    session_info = player_sessions.get(request.sid)
    if not session_info:
        return

    game_id = session_info['game_id']
    player_name = session_info['player_name']

    if game_id not in games:
        return

    game = games[game_id]
    card = game.draw_card(player_name)

    if card:
        # 只通知当前玩家抽到的牌
        emit('card_drawn', {
            'card': card.to_dict(),
            'hand_count': len([p for p in game.players if p.name == player_name][0].hand)
        }, room=request.sid)

        # 通知其他玩家有人抽牌
        emit('player_drew_card', {
            'player_name': player_name,
            'hand_count': len([p for p in game.players if p.name == player_name][0].hand)
        }, room=game_id)


@socketio.on('say_uno')
def handle_say_uno():
    session_info = player_sessions.get(request.sid)
    if not session_info:
        return

    game_id = session_info['game_id']
    player_name = session_info['player_name']

    if game_id not in games:
        return

    game = games[game_id]
    game.say_uno(player_name)

    emit('uno_said', {
        'player_name': player_name
    }, room=game_id)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80)