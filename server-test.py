from flask import Flask, render_template
import json
from VirtualJudgeSpider.Config import Account
from VirtualJudgeSpider.Control import Controller

app = Flask(__name__, template_folder='.')


@app.route("/<string:remote_oj>/<string:remote_id>")
def problem(remote_oj, remote_id):
    problem = Controller(remote_oj).get_problem(remote_id, account=Account('robot4test', 'robot4test'))
    if problem:
        return problem.html
    return None


@app.route("/supports")
def supports():
    return json.dumps({
        'supports': Controller.get_supports()
    })


@app.route("/")
def index():
    return render_template('server.html')


if __name__ == '__main__':
    app.run(debug=False, port=7777, host='0.0.0.0')
