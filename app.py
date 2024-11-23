from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import joblib
import psycopg2
from psycopg2.extras import execute_values
from sklearn.model_selection import train_test_split

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Загрузка модели
model = joblib.load('random_forest_model.pkl')

# Параметры подключения к базе данных
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "123"

def db_x_test():
    try:
        # используем библиотеки и подключаемся
        connect = psycopg2.connect(host="localhost", user="postgres", password="123", dbname="postgres")
        cursor = connect.cursor()
        # отправляем запрос к базе
        cursor.execute("select * from matchhistory;")
        # сохраняем результаты запроса
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        # сохраняем в пандаский датафрейм
        df = pd.DataFrame(rows, columns=column_names)
    except psycopg2.OperationalError as e:
        # ловим ошибки, а они вполне могут быть
        print(f"Connect error: {e}")
    finally:
        # в любом случае дропаем подклдчения
        if cursor:
            cursor.close()
        if connect:
            connect.close()
    return df

data = db_x_test()
data = data.drop('id', axis=1)
X = data.drop('matchresult', axis=1)
y = data['matchresult']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.27)


def get_db_connection():
    """Подключение к базе данных"""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn


@app.route('/')
def home():
    """Главная страница"""
    return render_template('index.html')


@app.route('/new_data', methods=['GET', 'POST'])
def new_data():
    """Страница добавления новых данных"""
    if request.method == 'POST':
        # Проверяем, загружен ли файл
        if 'file' not in request.files:
            flash('Файл не найден')
            return redirect(url_for('new_data'))

        file = request.files['file']

        if file.filename == '':
            flash('Файл не выбран')
            return redirect(url_for('new_data'))

        if file and file.filename.endswith('.csv'):
            try:
                # Чтение файла CSV
                df = pd.read_csv(file)

                # Проверка наличия необходимых столбцов
                if 'specific' not in df.columns or 'matchresult' not in df.columns:
                    flash('CSV-файл должен содержать столбцы "specific" и "matchresult"')
                    return redirect(url_for('new_data'))

                # Подключение к базе данных
                conn = get_db_connection()
                cur = conn.cursor()

                # Подготовка данных для вставки
                data_to_insert = [(row['specific'], row['matchresult']) for _, row in df.iterrows()]

                # Вставка данных в базу данных
                execute_values(
                    cur,
                    "INSERT INTO matchhistory (specific, matchresult) VALUES %s",
                    data_to_insert
                )

                conn.commit()
                cur.close()
                conn.close()

                flash('Файл успешно загружен, данные добавлены в базу.')
                return redirect(url_for('new_data'))

            except Exception as e:
                flash(f'Ошибка при обработке файла: {e}')
                return redirect(url_for('new_data'))
            flash('Загрузите файл в формате CSV.')
            return redirect(url_for('new_data'))
    else:
        return render_template('new_data.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Страница прогнозирования"""
    if request.method == 'POST':
        try:
            # Perform prediction
            pred = model.predict_proba(X_test)[:, 1]  # Вероятности для Y = 1

            # Generate results
            result_df = pd.DataFrame({
                'X': X_test.values.flatten(),
                'Y_prob': pred
            })
            max_prob_row = result_df.loc[result_df['Y_prob'].idxmax()]

            # Prepare the message with only the X value
            x_value = max_prob_row['X']
            if (x_value == 0):
                message = f"Лучший период для команды: Обычный рабочий"
                return render_template('predict.html', prediction=message)
            elif (x_value == 1):
                message = f"Лучший период для команды: Сессионный"
                return render_template('predict.html', prediction=message)
            elif (x_value == 2):
                message = f"Лучший период для команды: Каникулярный"
                return render_template('predict.html', prediction=message)

        except Exception as e:
            # Обработка ошибок, чтобы избежать "нет возвращаемого значения"
            error_message = f"Ошибка при выполнении предсказания: {e}"
            return render_template('predict.html', prediction=error_message)

    # Обработка метода 'GET' или других
    return render_template('predict.html', prediction=None)

if __name__ == '__main__':
    app.run(debug=True)