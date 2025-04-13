import os
from flask import Flask

def create_app(test_config=None):
    # アプリケーションを作成し、設定します
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # デフォルトの秘密鍵を設定
        SECRET_KEY='dev',
        # データベースのパスを設定
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # インスタンス設定が存在する場合は、それを読み込みます
        app.config.from_pyfile('config.py', silent=True)
    else:
        # テスト設定が渡された場合は、それを読み込みます
        app.config.update(test_config)

    # インスタンスフォルダが存在することを確認
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # データベースを初期化
    from . import db
    db.init_app(app)
    
    # 認証用のブループリントを登録
    from . import auth
    app.register_blueprint(auth.bp)

    # 作者管理用のブループリントを登録
    from . import author
    app.register_blueprint(author.bp)

    # ジャンル管理用のブループリントを登録
    from . import genre
    app.register_blueprint(genre.bp)

    # 分析用のブループリントを登録
    from . import analytics
    app.register_blueprint(analytics.bp)

    # ブログ用のブループリントを登録
    from . import books
    app.register_blueprint(books.bp)
    app.add_url_rule('/', endpoint='index')

    return app 