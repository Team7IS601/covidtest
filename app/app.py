




@app.route('/')
def index():
    return render_template('symptoms.html')

@app.route('/symptoms', methods=['POST'])
def user_rec():
    user_name = request.form.get('user_input')
    min_time = request.form.get('min_time')
    max_time = request.form.get('max_time')
    players = request.form.getlist('check')
    print(user_name, min_time, max_time, players)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)