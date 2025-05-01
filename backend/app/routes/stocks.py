from flask import Blueprint, jsonify
from ..models.stock import Stock
from ..utils.auth import token_required

stocks_bp = Blueprint('stocks', __name__)

@stocks_bp.route('/stocks', methods=['GET'])
@token_required
def get_stocks(current_user):
    stocks = Stock.query.all()
    return jsonify([stock.to_dict() for stock in stocks]), 200

@stocks_bp.route('/stocks/<symbol>', methods=['GET'])
@token_required
def get_stock_by_symbol(current_user, symbol):
    stock = Stock.query.filter_by(symbol=symbol).first()
    if not stock:
        return jsonify({'message': 'Stock not found'}), 404
    return jsonify(stock.to_dict()), 200 