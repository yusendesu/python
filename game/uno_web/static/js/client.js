class UNOClient {
    constructor() {
        this.socket = io();
        this.gameState = null;
        this.playerName = '';
        this.gameCode = '';
        this.isMyTurn = false;

        this.initializeEventListeners();
        this.setupSocketEvents();
    }

    initializeEventListeners() {
        // 大厅事件
        document.getElementById('create-game-btn').addEventListener('click', () => this.createGame());
        document.getElementById('join-game-btn').addEventListener('click', () => this.joinGame());

        // 游戏事件
        document.getElementById('draw-card-btn').addEventListener('click', () => this.drawCard());
        document.getElementById('say-uno-btn').addEventListener('click', () => this.sayUno());

        // 颜色选择器事件
        document.querySelectorAll('.color-picker button').forEach(btn => {
            btn.addEventListener('click', (e) => this.chooseColor(e.target.dataset.color));
        });
    }

    setupSocketEvents() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('player_joined', (data) => {
            this.updatePlayersList(data.players);
            this.showMessage(`${data.player_name} 加入了游戏`);
        });

        this.socket.on('game_started', (data) => {
            this.showMessage('游戏开始！');
            this.updateGameState(data);
        });

        this.socket.on('card_played', (data) => {
            this.showMessage(data.message);
            this.updateGameState(data.game_state);
        });

        this.socket.on('card_drawn', (data) => {
            this.addCardToHand(data.card);
            this.updateHandCount();
        });

        this.socket.on('player_drew_card', (data) => {
            this.showMessage(`${data.player_name} 抽了一张牌`);
            this.updatePlayerHandCount(data.player_name, data.hand_count);
        });

        this.socket.on('uno_said', (data) => {
            this.showMessage(`${data.player_name} 喊了 UNO!`);
        });

        this.socket.on('round_ended', (data) => {
            this.showMessage(`${data.winner} 赢得了这一回合！`);
            this.updateScores(data.scores);
        });

        this.socket.on('new_round_started', (data) => {
            this.showMessage('新回合开始！');
            this.updateGameState(data.game_state);
        });

        this.socket.on('player_left', (data) => {
            this.showMessage(`${data.player_name} 离开了游戏`);
            this.removePlayer(data.player_name);
        });

        this.socket.on('error', (data) => {
            this.showMessage(data.message, true);
        });

        this.socket.on('game_state', (data) => {
            this.updateGameState(data);
        });
    }

    createGame() {
        this.playerName = document.getElementById('player-name').value.trim();
        if (!this.playerName) {
            this.showMessage('请输入你的名字', true);
            return;
        }

        fetch('/create_game')
            .then(response => response.json())
            .then(data => {
                this.gameCode = data.game_id;
                this.joinGameAfterCreate();
            });
    }

    joinGameAfterCreate() {
        this.socket.emit('join_game', {
            game_id: this.gameCode,
            player_name: this.playerName
        });

        this.showLobby(false);
        document.getElementById('current-game-code').textContent = this.gameCode;
    }

    joinGame() {
        this.playerName = document.getElementById('join-player-name').value.trim();
        this.gameCode = document.getElementById('game-code').value.trim();

        if (!this.playerName || !this.gameCode) {
            this.showMessage('请输入名字和游戏代码', true);
            return;
        }

        fetch(`/join_game/${this.gameCode}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    this.showMessage(data.error, true);
                    return;
                }

                this.socket.emit('join_game', {
                    game_id: this.gameCode,
                    player_name: this.playerName
                });

                this.showLobby(false);
                document.getElementById('current-game-code').textContent = this.gameCode;
            });
    }

    playCard(cardIndex) {
        if (!this.isMyTurn) {
            this.showMessage('不是你的回合！', true);
            return;
        }

        const card = this.gameState.your_hand[cardIndex];

        // 如果是万能牌，显示颜色选择器
        if (card.color === 'wild') {
            this.showColorPicker(cardIndex);
            return;
        }

        this.socket.emit('play_card', {
            card_index: cardIndex
        });
    }

    chooseColor(color) {
        const cardIndex = this.colorPickerCardIndex;
        this.hideColorPicker();

        this.socket.emit('play_card', {
            card_index: cardIndex,
            chosen_color: color
        });
    }

    drawCard() {
        if (!this.isMyTurn) {
            this.showMessage('不是你的回合！', true);
            return;
        }

        this.socket.emit('draw_card');
    }

    sayUno() {
        this.socket.emit('say_uno');
    }

    updateGameState(state) {
        this.gameState = state;
        this.isMyTurn = state.your_turn;

        // 更新玩家列表
        this.updatePlayersList(state.players);

        // 更新出牌堆
        if (state.play_pile_top) {
            document.getElementById('top-card').src = state.play_pile_top.image_src;
        }

        // 更新当前颜色显示
        this.updateCurrentColor(state.current_color);

        // 更新玩家手牌
        if (state.your_hand) {
            this.updatePlayerHand(state.your_hand);
        }

        // 更新回合状态
        this.updateTurnIndicator();

        // 更新分数
        this.updateScores(this.getScoresFromState(state.players));
    }

    updatePlayerHand(hand) {
        const handContainer = document.getElementById('player-hand');
        handContainer.innerHTML = '';

        hand.forEach((card, index) => {
            const cardElement = document.createElement('img');
            cardElement.src = card.image_src;
            cardElement.alt = `${card.color} ${card.value}`;
            cardElement.classList.add('player-card');

            if (this.isMyTurn) {
                cardElement.style.cursor = 'pointer';
                cardElement.addEventListener('click', () => this.playCard(index));
            }

            handContainer.appendChild(cardElement);
        });
    }

    updatePlayersList(players) {
        const container = document.getElementById('players-container');
        container.innerHTML = '';

        players.forEach(player => {
            const playerElement = document.createElement('div');
            playerElement.className = 'player-item';
            playerElement.innerHTML = `
                <span class="player-name">${player.name}</span>
                <span class="hand-count">${player.hand_count}张牌</span>
                <span class="score">${player.score}分</span>
                ${player.said_uno ? '<span class="uno-badge">UNO!</span>' : ''}
            `;
            container.appendChild(playerElement);
        });
    }

    updateScores(scores) {
        const container = document.getElementById('scores-container');
        container.innerHTML = '<h3>分数</h3>';

        Object.entries(scores).forEach(([name, score]) => {
            const scoreElement = document.createElement('div');
            scoreElement.className = 'score-item';
            scoreElement.innerHTML = `${name}: ${score}分`;
            container.appendChild(scoreElement);
        });
    }

    updateTurnIndicator() {
        document.querySelectorAll('.player-item').forEach(item => {
            item.classList.remove('current-turn');
        });

        if (this.gameState && this.gameState.current_player) {
            const currentPlayerElement = [...document.querySelectorAll('.player-item')]
                .find(item => item.querySelector('.player-name').textContent === this.gameState.current_player);

            if (currentPlayerElement) {
                currentPlayerElement.classList.add('current-turn');
            }
        }

        // 更新抽牌按钮状态
        const drawButton = document.getElementById('draw-card-btn');
        drawButton.disabled = !this.isMyTurn;
        drawButton.style.opacity = this.isMyTurn ? '1' : '0.5';
    }

    updateCurrentColor(color) {
        const topCard = document.getElementById('top-card');
        if (color && topCard) {
            topCard.style.border = `3px solid ${this.getColorHex(color)}`;
        }
    }

    getColorHex(color) {
        const colorMap = {
            'red': '#FF0000',
            'green': '#00AA45',
            'blue': '#0096E0',
            'yellow': '#FFDE00'
        };
        return colorMap[color] || '#FFFFFF';
    }

    showColorPicker(cardIndex) {
        this.colorPickerCardIndex = cardIndex;
        document.querySelector('.color-picker').classList.remove('hidden');
    }

    hideColorPicker() {
        document.querySelector('.color-picker').classList.add('hidden');
    }

    showLobby(show) {
        document.getElementById('lobby').classList.toggle('hidden', !show);
        document.getElementById('game').classList.toggle('hidden', show);
    }

    showMessage(message, isError = false) {
        const messageElement = document.getElementById('game-message');
        const textElement = document.getElementById('message-text');

        textElement.textContent = message;
        messageElement.className = `game-message ${isError ? 'error' : 'info'}`;
        messageElement.classList.remove('hidden');

        setTimeout(() => {
            messageElement.classList.add('hidden');
        }, 3000);
    }

    getScoresFromState(players) {
        const scores = {};
        players.forEach(player => {
            scores[player.name] = player.score;
        });
        return scores;
    }

    addCardToHand(card) {
        if (!this.gameState.your_hand) this.gameState.your_hand = [];
        this.gameState.your_hand.push(card);
        this.updatePlayerHand(this.gameState.your_hand);
    }

    updateHandCount() {
        // 更新玩家手牌数量显示
        this.updatePlayersList(this.gameState.players);
    }

    updatePlayerHandCount(playerName, handCount) {
        // 更新特定玩家的手牌数量
        const playerElement = [...document.querySelectorAll('.player-item')]
            .find(item => item.querySelector('.player-name').textContent === playerName);

        if (playerElement) {
            playerElement.querySelector('.hand-count').textContent = `${handCount}张牌`;
        }
    }

    removePlayer(playerName) {
        // 从玩家列表中移除玩家
        this.updatePlayersList(this.gameState.players.filter(p => p.name !== playerName));
    }
}

// 初始化客户端
document.addEventListener('DOMContentLoaded', () => {
    new UNOClient();
});
