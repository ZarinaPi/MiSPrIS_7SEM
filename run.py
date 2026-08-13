"""
Точка входа в приложение.
Запуск Flask-приложения с фабрикой create_app.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print('Сервер запущен на http://127.0.0.1:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
