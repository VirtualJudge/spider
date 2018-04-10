from flask import Flask, render_template
import json
from VirtualJudgeSpider.Config import Account
from VirtualJudgeSpider.Control import Controller
from VirtualJudgeSpider.Config import Problem

app = Flask(__name__, template_folder='.')


@app.route("/raw/<string:remote_oj>/<string:remote_id>")
def get_raw(remote_oj, remote_id):
    problem = Controller(remote_oj).get_problem(remote_id, account=Account('robot4test', 'robot4test'))
    if problem and problem.status:
        problem.status = problem.status.value
        return '<xmp>' + str(
            json.dumps(problem.__dict__, sort_keys=True, indent=4)) + '</xmp>'
    return 'No Such OJ'


@app.route("/<string:remote_oj>/<string:remote_id>")
def problem(remote_oj, remote_id):
    problem = Controller(remote_oj).get_problem(remote_id, account=Account('robot4test', 'robot4test'))
    if problem.status == Problem.Status.STATUS_CRAWLING_SUCCESS:
        return problem.html
    return problem.status.name


@app.route("/supports")
def supports():
    return json.dumps({
        'supports': Controller.get_supports()
    })


@app.route("/")
def index():
    return render_template('server.html')


if __name__ == '__main__':
    app.run(debug=True, port=7777, host='0.0.0.0')
