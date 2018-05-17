from flask import render_template, redirect, url_for, jsonify, request
from lidarts.game import bp
from lidarts.game.forms import CreateX01GameForm, ScoreForm
from lidarts.models import Game
from lidarts import db
from lidarts.game.utils import get_name_by_id


@bp.route('/create', methods=['GET', 'POST'])
@bp.route('/create/<mode>', methods=['GET', 'POST'])
def create(mode='x01'):
    if mode == 'x01':
        form = CreateX01GameForm()
    else:
        pass
    if form.validate_on_submit():
        game = Game(player1=None, player2=None, type=form.type.data,
                    bo_sets=form.bo_sets.data, bo_legs=form.bo_legs.data,
                    p1_sets=0, p2_sets=0, p1_legs=0, p2_legs=0,
                    p1_score=int(form.type.data), p2_score=int(form.type.data))
        game.p1_next_turn = form.starter.data == 'me'
        db.session.add(game)
        db.session.commit()
        game.set_hashid()
        db.session.commit()
        return redirect(url_for('game.start', hashid=game.hashid))
    return render_template('game/create_X01.html', form=form)


@bp.route('/game')
def game():
    return render_template('game/game.html')


@bp.route('/<hashid>')
def start(hashid):
    form = ScoreForm()
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    game_dict = game.as_dict()
    if game.player1:
        game_dict['player1_name'] = get_name_by_id(game.player1)
    else:
        game_dict['player1_name'] = 'Guest'
    if game.player2:
        game_dict['player2_name'] = get_name_by_id(game.player2)
    else:
        game_dict['player2_name'] = 'Guest'
    return render_template('game/X01.html', game=game_dict, form=form)


@bp.route('/validate_score', methods=['POST'])
def validate_score():
    form = ScoreForm(request.form)
    result = form.validate()
    print(form.errors)
    return jsonify(form.errors)
