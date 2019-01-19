import json
import time

from flask import Flask, render_template, request

from spider.config import Account
from spider.config import Problem, Result
from spider.core import Core

app = Flask(__name__, template_folder='.')


@app.route("/submit", methods=['POST'])
def submit():
    source_code = request.files['source_code']
    if request.form.get('remote_oj') and request.form.get('language') and request.form.get('remote_id') and source_code:
        remote_oj = request.form['remote_oj']
        remote_id = request.form['remote_id']
        language = request.form['language']

        ans = False
        tries = 3
        account = Account('robot4test', 'robot4test')
        while ans is False and tries > 0:
            tries -= 1
            core = Core(str(remote_oj))
            ans = core.submit_code(pid=remote_id, account=account, code=source_code.read(), language=language)
            print(ans.__dict__)
            account.set_cookies(core.get_cookies())
        if ans.status in [Result.Status.STATUS_SUBMIT_ERROR, Result.Status.STATUS_SPIDER_ERROR,
                          Result.Status.STATUS_SYSTEM_ERROR]:
            return "SUBMIT FAILED"
        core = Core(remote_oj)
        result = core.get_result(account=account, pid=remote_id)
        print(result.__dict__)
        account.set_cookies(core.get_cookies())
        tries = 5
        while result.verdict == Result.Verdict.VERDICT_RUNNING and tries > 0:
            time.sleep(2)
            result = Core(remote_oj).get_result_by_rid_and_pid(rid=result.unique_key, pid=remote_id)
            tries -= 1

        if result.status == Result.Status.STATUS_RESULT_SUCCESS:
            return str(result.__dict__)
        return result.status.name
    return "Error"


@app.route("/raw/<string:remote_oj>/<string:remote_id>")
def get_raw(remote_oj, remote_id):
    problem = Core(remote_oj).get_problem(remote_id, account=Account('robot4test', 'robot4test'))
    if problem and problem.status:
        problem.status = problem.status.value
        return '<xmp>' + str(
            json.dumps(problem.__dict__, sort_keys=True, indent=4)) + '</xmp>'
    return 'No Such OJ'


@app.route("/languages/<string:remote_oj>")
def language(remote_oj):
    return json.dumps({
        'languages': Core(remote_oj).find_language(account=Account('robot4test', 'robot4test'))
    })


@app.route("/<string:remote_oj>/<string:remote_id>")
def problem(remote_oj, remote_id):
    problem_json = Core(remote_oj).get_problem(remote_id, account=Account('robot4test', 'robot4test'))
    if problem_json.status == Problem.Status.STATUS_SUCCESS:
        return problem_json.html
    return problem_json.status.name


@app.route("/supports")
def supports():
    return json.dumps({
        'supports': Core.get_supports()
    })


@app.route("/")
def index():
    return render_template('server.html')


if __name__ == '__main__':
    app.run(debug=True, port=7777, host='127.0.0.1')
